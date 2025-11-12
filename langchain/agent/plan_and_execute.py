import os

from langchain_classic.chains.llm_math.base import LLMMathChain
from langchain_community.utilities import SerpAPIWrapper
from langchain_core.tools import Tool
from langchain_openai import ChatOpenAI
from langchain_experimental.plan_and_execute import PlanAndExecute, load_agent_executor, load_chat_planner

search = SerpAPIWrapper()
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

llm_math_chain = LLMMathChain.from_llm(llm=llm, verbose=True)
tools = [
    Tool(
        name = "Search",
        func=search.run,
        description="useful for when you need to answer questions about current events"
    ),
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math"
    ),
]
planner = load_chat_planner(llm)
executor = load_agent_executor(llm, tools, verbose=True)
agent = PlanAndExecute(planner=planner, executor=executor, verbose=True)

agent.run("在纽约，100美元能买几束玫瑰?")