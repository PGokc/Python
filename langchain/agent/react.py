import os

from langchain_core.chat_history import InMemoryChatMessageHistory  # 正确导入对话历史存储类
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.memory import ConversationBufferMemory
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor

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
    )
]

# -------------------------- 3. 构建 ReAct 专属 Prompt（核心引导逻辑）--------------------------
react_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是专业的鲜花店智能助手，严格遵循 ReAct 框架解决用户问题：
    1. 思考（Reason）：先分析用户需求，判断是否需要调用工具（价格/库存/配送问题必须调用对应工具，已知答案可直接回答）；
    2. 行动（Act）：需调用工具时，选择唯一合适的工具，传入完整、正确的参数（参数缺失会导致查询失败）；
    3. 观察（Observe）：获取工具返回结果后，判断是否需要进一步调用工具（如用户问总价需先查单价），或直接整理结果回答。

    规则：
    - 禁止猜测价格、库存、配送信息，必须通过工具查询；
    - 工具返回结果后，若信息足够，立即用自然语言回答用户，无需额外思考；
    - 多轮对话中，记住之前的工具查询结果，无需重复调用；
    - 仅支持调用提供的 3 个工具，不允许调用其他工具。
    """),
    MessagesPlaceholder(variable_name="chat_history"),  # 记忆注入
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")  # ReAct 临时存储区
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

# -------------------------- 6. 修复：create_openai_tools_agent 无无效参数--------------------------
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
    verbose=True,  # 查看 ReAct 循环细节
    handle_parsing_errors="抱歉，我暂时无法处理你的请求，请检查问题描述是否清晰~",
    memory=memory,  # 注入当前会话的记忆
    max_iterations=5  # 防止无限循环（可选，推荐添加）
)

# -------------------------- 8. 测试 ReAct Agent（多轮对话）--------------------------
print("=== ReAct 框架 Agent 测试（基于 langchain_classic）===")
print("提示：支持查询鲜花价格、库存、配送，输入 '退出' 结束对话~")

while True:
    user_input = input("\n用户：")
    if user_input.strip() == "退出":
        print("助手：再见！有任何需求随时回来~")
        break

    # 修复：无需传入 config={"configurable": ...}，直接调用
    result = agent_executor.invoke({"input": user_input})

    # 输出结果
    print(f"助手：{result['output']}")