import os

from langchain_core.chat_history import InMemoryChatMessageHistory  # 正确导入对话历史存储类
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from serpapi import GoogleSearch

# -------------------------- 1. 基础配置（模型+API）--------------------------
# 初始化 LLM（兼容 ReAct 框架，需支持函数调用）
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",  # 推荐 gpt-3.5-turbo/gpt-4（支持工具调用）
    temperature=0.1,  # ReAct 需低温度，确保思考逻辑连贯
    timeout=30
)

# -------------------------- 2. 定义工具（Agent 可调用的行动）--------------------------
# 工具1：查询鲜花价格
def query_flower_price(flower_name: str) -> str:
    """查询指定鲜花的单价，仅支持常见鲜花（红玫瑰、白玫瑰、满天星、郁金香）"""
    price_map = {
        "红玫瑰": "39元/束（含包装）",
        "白玫瑰": "42元/束（含包装）",
        "满天星": "25元/束（含包装）",
        "郁金香": "45元/束（含包装）"
    }
    return price_map.get(flower_name, f"暂无{flower_name}的价格信息，支持查询：红玫瑰、白玫瑰、满天星、郁金香")

# 工具2：查询鲜花库存
def query_flower_stock(flower_name: str) -> str:
    """查询指定鲜花的当前库存数量，仅支持常见鲜花（红玫瑰、白玫瑰、满天星、郁金香）"""
    stock_map = {
        "红玫瑰": "120束",
        "白玫瑰": "85束",
        "满天星": "200束",
        "郁金香": "60束"
    }
    return stock_map.get(flower_name, f"暂无{flower_name}的库存信息，支持查询：红玫瑰、白玫瑰、满天星、郁金香")

# 工具3：查询配送范围及时效
def query_delivery(city: str) -> str:
    """查询指定城市的配送范围和送达时效，仅支持国内省会及直辖市"""
    supported_cities = ["北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "重庆"]
    if city in supported_cities:
        return f"{city}主城区支持当日达（14:00前下单），郊区支持次日达，配送费免费"
    return f"暂不支持{city}的配送，目前支持配送的城市：{','.join(supported_cities)}"


# 工具4：SerpAPI 搜索工具（外部实时查询）
def search_external_info(query: str) -> str:
    """
    调用谷歌搜索（SerpAPI）查询外部实时信息，适用于以下场景：
    1. 内部工具无法回答的问题（如小众鲜花价格、新城市配送政策、节日活动）；
    2. 需要实时数据的问题（如当日鲜花市场价、近期配送延迟通知、新品上市信息）；
    3. 需要外部知识的问题（如鲜花保鲜技巧、节日送花习俗、热门花束推荐）。

    搜索结果会提取前3条核心信息，整理后返回。
    """
    try:
        # 配置 SerpAPI 搜索参数（谷歌搜索）
        search_params = {
            "q": query,  # 搜索关键词
            "api_key": os.getenv("SERPAPI_API_KEY"),  # 从环境变量获取 SerpAPI Key
            "engine": "google",  # 搜索引擎（默认谷歌，也可改为 bing 等）
            "gl": "cn",  # 地区：中国
            "hl": "zh-CN"  # 语言：中文
        }

        # 执行搜索
        search = GoogleSearch(search_params)
        results = search.get_dict()  # 获取搜索结果（字典格式）

        # 提取核心信息（优先提取 organic_results，无结果则返回相关信息）
        organic_results = results.get("organic_results", [])
        if not organic_results:
            return f"搜索结果为空，未找到与「{query}」相关的有效信息"

        # 整理前3条结果（标题+链接+摘要）
        search_summary = []
        for idx, result in enumerate(organic_results[:3], 1):
            title = result.get("title", "无标题")
            link = result.get("link", "无链接")
            snippet = result.get("snippet", "无摘要")
            search_summary.append(f"{idx}. 标题：{title}\n   链接：{link}\n   摘要：{snippet}")

        return f"搜索到与「{query}」相关的3条核心信息：\n{chr(10).join(search_summary)}\n\n注：信息来自公开网络，仅供参考\n"

    except Exception as e:
        return f"搜索工具调用失败：{str(e)}（请检查 SerpAPI Key 是否有效，或网络是否正常）"

# 封装工具（Agent 会自动识别工具描述，判断何时调用）
tools = [
    Tool(
        name="QueryFlowerPrice",
        func=query_flower_price,
        description="当用户询问某类鲜花的价格时调用，必须传入鲜花名称（如红玫瑰、白玫瑰）"
    ),
    Tool(
        name="QueryFlowerStock",
        func=query_flower_stock,
        description="当用户询问某类鲜花的库存数量时调用，必须传入鲜花名称（如红玫瑰、白玫瑰）"
    ),
    Tool(
        name="QueryDelivery",
        func=query_delivery,
        description="当用户询问配送范围、送达时效时调用，必须传入城市名称（如北京、上海）"
    ),
    # SerpAPI 搜索工具（核心新增）
    Tool(
        name="SearchExternalInfo",
        func=search_external_info,
        description="""
        用于查询内部工具无法回答的问题，必须联网，支持实时信息查询，适用场景包括：
        1. 小众鲜花（如洋桔梗、绣球花）的价格、库存、配送；
        2. 内部工具未覆盖的城市（如南京、西安）的配送政策；
        3. 实时数据（如当日鲜花市场价、节日促销活动、配送延迟通知）；
        4. 外部知识（如鲜花保鲜技巧、节日送花习俗、热门花束推荐）；
        5. 内部工具返回「暂无信息」时，自动调用该工具补充查询。
        调用时需传入明确的搜索关键词（如「南京 洋桔梗 配送政策」「2025年母亲节 鲜花促销活动」）。
        """
    )
]

# -------------------------- 3. 构建 ReAct 专属 Prompt（核心引导逻辑）--------------------------
react_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是专业的鲜花店智能助手，严格遵循 ReAct 框架解决用户问题，核心规则如下：
    1. 思考（Reason）：
       - 先判断用户问题是否在内部工具的覆盖范围内（常见鲜花价格/库存、8个支持城市配送）；
       - 若内部工具能回答，直接调用对应内部工具（无需搜索，快速响应）；
       - 若内部工具无法回答（如小众鲜花、未覆盖城市、实时信息、外部知识），立即调用 SearchExternalInfo 工具搜索；
       - 若内部工具返回「暂无信息」，自动切换为搜索工具补充查询。
       - 如果用户问题与鲜花无关，则统一回复：我是一名鲜花店智能助手，只能解答鲜花相关问题哦~

    2. 行动（Act）：
       - 调用内部工具时，确保参数正确（鲜花名称/城市名称必须明确）；
       - 调用搜索工具时，需将用户问题转化为精准的搜索关键词（如用户问「南京能送洋桔梗吗？」→ 搜索关键词「南京 洋桔梗 配送政策」）；
       - 一次仅调用一个工具，不允许同时调用多个。

    3. 观察（Observe）：
       - 内部工具返回结果后，直接整理回答，无需进一步操作；
       - 搜索工具返回结果后，提炼核心信息（忽略无关内容），用自然语言转述给用户，并注明「信息来自公开网络」。

    4. 禁止规则：
       - 禁止在内部工具能回答的情况下调用搜索工具（避免冗余）；
       - 禁止猜测内部工具未覆盖的数据，必须通过搜索工具获取；
       - 禁止直接返回搜索链接，需提炼摘要后回答。
    """),
    # 记忆注入：保留多轮对话上下文（如之前的搜索结果、内部工具查询结果）
    MessagesPlaceholder(variable_name="chat_history"),
    # 用户输入
    ("user", "{input}"),
    # Agent 思考和工具调用的临时存储区
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

# -------------------------- 4. 修复：会话历史存储（支持多会话隔离）--------------------------
# 存储结构：{session_id: InMemoryChatMessageHistory实例}
session_store = {}

def get_chat_history(session_id: str = "default") -> InMemoryChatMessageHistory:
    """返回指定会话的对话历史（正确类型：InMemoryChatMessageHistory）"""
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

# -------------------------- 5. 修复：为当前会话创建独立的记忆实例--------------------------
# 这里以 "react_agent_demo" 为默认会话ID，如需多会话可动态创建 memory
current_session_id = "react_agent_demo"
memory = ConversationBufferMemory(
    chat_memory=get_chat_history(current_session_id),  # 绑定当前会话的历史
    memory_key="chat_history",  # 与 Prompt 中 variable_name 对应
    return_messages=True  # 返回 ChatMessage 格式，适配模型
)

# -------------------------- 6. 修复：create_openai_tools_agent 无效参数--------------------------
agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=react_prompt,
    # 移除 agent_type 和 memory 参数（旧版函数不支持）
)

# -------------------------- 7. 修复：AgentExecutor 无需传入 session_id 配置--------------------------
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 查看 ReAct 循环细节(开启后可查看完整 ReAct 循环（思考→工具调用→观察→回答）)
    handle_parsing_errors="抱歉，我暂时无法处理你的请求，请检查问题描述是否清晰~",
    memory=memory,  # 注入当前会话的记忆
    max_iterations=5  # 防止无限循环（如搜索失败时, 可选，推荐添加）
)

# -------------------------- 8. 测试 Agent（支持内部查询 + 外部搜索）--------------------------
print("=== ReAct 框架 Agent 测试（集成 SerpAPI 搜索工具）===")
print("提示：")
print("1. 支持查询内部常见鲜花价格/库存/配送（红玫瑰、白玫瑰、满天星、郁金香；8个城市）；")
print("2. 支持搜索外部信息（小众鲜花、其他城市、实时活动、保鲜技巧等）；")
print("3. 输入 '退出' 结束对话~")
print("="*60)

while True:
    user_input = input("\n用户：")
    if user_input.strip() == "退出":
        print("助手：再见！有任何鲜花相关需求随时回来~")
        break

    # 执行 Agent（自动选择内部工具或搜索工具）
    result = agent_executor.invoke({"input": user_input})

    # 输出结果
    print(f"助手：{result['output']}")