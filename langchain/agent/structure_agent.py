import os
from typing import List

from langchain_community.tools import NavigateTool, ClickTool, ExtractTextTool, GetElementsTool
from langchain_community.tools.playwright.base import BaseBrowserTool
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor, create_structured_chat_agent
from langchain_community.tools.playwright.utils import create_async_playwright_browser
from langchain_community.agent_toolkits.playwright import PlayWrightBrowserToolkit
from playwright.sync_api import sync_playwright

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
def init_playwright_toolkit() -> PlayWrightBrowserToolkit:
    """初始化 PlayWright 结构化工具集，包含核心浏览器操作工具"""
    # 启动 Playwright 并创建浏览器上下文（最新版推荐显式管理上下文）
    playwright = sync_playwright().start()
    # 启动 Chromium 浏览器（headless=False 显示浏览器，便于调试；生产环境设为 True）
    browser = playwright.chromium.launch(
        headless=False,  # 调试时设为 False，直观查看 Agent 操作
        slow_mo=500,     # 慢动作执行（500ms/步），便于观察
        args=["--no-sandbox", "--disable-dev-shm-usage"]  # 容器兼容
    )

    # 初始化 PlayWright 工具集
    return PlayWrightBrowserToolkit.from_browser(browser)

# 初始化工具集
playwright_toolkit = init_playwright_toolkit()
tools = playwright_toolkit.get_tools()  # 提取结构化工具列表

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
# 原 AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION 的核心逻辑通过 Prompt 实现
structured_prompt = ChatPromptTemplate.from_messages([
    ("system", f"""
    你是一个精通浏览器操作的智能助手，通过 Playwright 结构化工具完成用户需求，严格遵循以下规则：

    ### 核心流程
    1. 分析需求：明确用户需要的浏览器操作（导航、点击、提取内容等）；
    2. 选择工具：从提供的结构化工具中选择唯一合适的工具（一个步骤一个工具）；
    3. 校验参数：确保工具参数完整（如导航需 URL、点击需 selector），参数缺失则询问用户；
    4. 执行操作：调用工具后，根据返回结果判断是否需要下一步操作（如点击后提取内容）；
    5. 整理结果：所有操作完成后，用自然语言汇总结果返回用户。

    ### 工具使用指南
    - 导航（NavigateTool）：用户要求访问网页时调用，参数必须是完整 URL（如 https://langchain.com/）；
    - 点击（ClickTool）：需要点击按钮/链接时调用，参数是 CSS 或 XPATH 选择器（如 ".nav-link"、"//button[text()='文档']"）；
    - 提取文本（ExtractTextTool）：需要获取页面某部分文本时调用，参数是选择器；
    - 获取标题（GetTitleTool）：用户询问页面标题时调用，无参数；
    - 等待元素（WaitForSelectorTool）：页面异步加载时，先调用该工具等待元素出现，再执行点击/提取；
    - 提取HTML（ExtractHtmlTool）：需要获取完整页面或部分HTML时调用，可选参数 selector。
    - 获取元素 (GetElementToll)：获取具体的HTML元素

    ### 关键规则
    - 必须使用提供的结构化工具，禁止手动编写浏览器代码；
    - 选择器优先使用 CSS 格式（如 "#id"、".class"），无法定位时再用 XPATH；
    - 操作前先确认页面是否已导航到目标URL，未导航则先调用 NavigateTool；
    - 遇到元素未找到时，先调用 WaitForSelectorTool 等待（超时10秒），仍未找到则告知用户；
    - 多轮操作时，记住之前的操作结果（如已点击的链接、已提取的文本），无需重复操作。
    """),
    MessagesPlaceholder(variable_name="chat_history"),  # 注入对话记忆
    ("user", "{input}"),                                # 用户输入
    MessagesPlaceholder(variable_name="agent_scratchpad")  # 工具调用临时存储区
])

# -------------------------- 5. 创建 Structured Tool Chat Agent --------------------------
# TODO 运行失败：不兼容
agent = create_structured_chat_agent(
    llm=llm,
    tools=tools,
    prompt=structured_prompt,
)

# -------------------------- 6. 创建 Agent 执行器（调度工具和处理错误）--------------------------
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # 开启调试，查看工具调用细节
    handle_parsing_errors="抱歉，工具调用格式错误，请检查需求描述是否清晰~",
    memory=memory,
    max_iterations=10,  # 防止无限循环
    early_stopping_method="generate"  # 操作完成后自动生成结果
)

# -------------------------- 7. 测试 Structured Tool Chat（自然语言驱动浏览器）--------------------------
print("=== PlayWright Structured Tool Chat Demo ===")
print("支持的操作：访问网页、点击元素、提取文本、获取标题等")
print("示例需求：")
print("1. 访问 LangChain 官网，获取页面标题")
print("2. 访问 https://langchain.com/docs，点击 'Guides' 链接，提取页面主要内容")
print("3. 访问百度，搜索 'LangChain 结构化工具'，提取前3条搜索结果")
print("输入 '退出' 结束对话~")
print("="*60)

while True:
    user_input = input("\n用户：")
    if user_input.strip() == "退出":
        print("助手：再见！如需自动化浏览器操作随时回来~")
        break

    # 执行 Agent，自然语言驱动浏览器操作
    result = agent_executor.invoke({"input": user_input})
    print(f"助手：{result['output']}")