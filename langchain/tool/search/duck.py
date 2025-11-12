import os

from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_community.tools.ddg_search.tool import (
    DuckDuckGoSearchResults,
    DuckDuckGoSearchRun,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

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

# 1. 初始化搜索工具
search_tool = DuckDuckGoSearchRun()
tools = [search_tool]

prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是智能助手, 请按照以下规则解答用户提问：
    - 禁止猜测，必须通过工具查询；
    - 工具返回结果后，若信息足够，立即用自然语言回答用户，无需额外思考；
    - 多轮对话中，记住之前的工具查询结果，无需重复调用；
    - 仅支持调用提供的 3 个工具，不允许调用其他工具。
    """),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")  
])

# 2. 创建 Self-Ask Agent
agent = create_openai_tools_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# 调用（需要多轮搜索的问题）
agent_executor.invoke({"input": "北京明天的天气是否适合去颐和园野餐？"})