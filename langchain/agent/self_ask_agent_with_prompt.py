import os

from langchain_community.utilities import SerpAPIWrapper
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
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

# -------------------------- 2. 初始化 PlayWright 浏览器工具集 --------------------------
search = SerpAPIWrapper(
    params={
        "engine": "google",  # 搜索引擎（默认谷歌，可改为 bing 等）
        "gl": "cn",  # 地区：中国
        "hl": "zh-CN"  # 语言：中文
    }
)
tools = [
    Tool(
        name="SerpApi",
        func=search.run,
        description="""
        当你需要通过搜索获取信息才能回答用户问题时，必须调用此工具。
        适用场景：
        1. 未知事实性问题（如国家的国花、首都、数据统计等）；
        2. 时效性强的信息（如最新政策、实时数据等）；
        3. 你不确定的任何客观信息。
        调用时需传入明确的搜索关键词（如「以玫瑰为国花的国家」）。
        """
    )
]

# -------------------------- 3. 配置对话记忆（支持多轮交互连贯性）--------------------------
# 会话存储（多会话隔离）
session_store = {}
def get_chat_history(session_id: str = "playwright_demo") -> InMemoryChatMessageHistory:
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

# 记忆初始化
memory = ConversationBufferMemory(
    chat_memory=get_chat_history(),
    memory_key="chat_history",
    return_messages=True  # 返回 ChatMessage 格式，适配 Prompt
)

# -------------------------- 4. 构建 Structured Tool Chat Prompt（核心引导逻辑）--------------------------
# 原 AgentType.SELF_ASK_WITH_SEARCH 的核心逻辑通过 Prompt 实现
self_ask_prompt = ChatPromptTemplate.from_messages([
    ("system", """
        你是一个会通过逐步提问解决问题的智能助手，严格遵循以下规则：
        1. 面对用户问题，先判断是否需要搜索：
           - 如果不需要搜索（你确定答案），直接返回结果；
           - 如果需要搜索，生成一个「中间问题」，调用「SerpApi」工具获取答案；
        2. 拿到搜索结果后，判断是否已足够回答用户问题：
           - 若足够，整理搜索结果形成最终答案；
           - 若不足，生成新的「中间问题」继续搜索，直到获取足够信息；
        3. 禁止在未搜索的情况下猜测答案，所有事实性信息必须来自搜索工具；
        4. 搜索关键词需精准，中间问题要明确（如用户问「以玫瑰为国花的国家的首都是哪里？」，第一步搜索关键词为「以玫瑰为国花的国家」）。
        """),
    MessagesPlaceholder(variable_name="chat_history"),  # 支持多轮对话（可选）
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")  # 工具调用临时存储区
])

# -------------------------- 5. 创建 Self Ask With Search Chat Agent --------------------------
agent = create_openai_tools_agent(
    llm=llm,
    tools=tools,
    prompt=self_ask_prompt,
    strict=False,
)

# -------------------------- 6. 创建 Agent 执行器（调度工具和处理错误）--------------------------
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 开启调试，查看工具调用细节
    handle_parsing_errors="搜索失败或问题解析错误，请检查关键词或网络连接~",
    memory=memory,
    max_iterations=10,  # 防止无限循环
    early_stopping_method="generate"  # 操作完成后自动生成结果
)

# -------------------------- 7. 测试 SelfAsk Tool Chat（Follow-up Question（追问）+ Intermediate Answer（中间答案））--------------------------
print("=== SerpApi SelfAskWithSearch Tool Chat Demo ===")
print("示例需求：")
print("1. 使用玫瑰作为国花的国家的首都是哪里?")
print("2. 保罗乔治效力过的队伍中，哪些是有总冠军的？")
print("输入 '退出' 结束对话~")
print("="*60)

while True:
    user_input = input("\n用户：")
    if user_input.strip() == "退出":
        print("助手：再见！随时回来~")
        break

    # 执行 Agent，自然语言驱动浏览器操作
    result = agent_executor.invoke({"input": user_input})
    print(f"助手：{result['output']}")