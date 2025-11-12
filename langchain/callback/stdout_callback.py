import logging
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import StdOutCallbackHandler

# logging.getLogger("langchain").setLevel(logging.INFO)

# 1. 基础配置
load_dotenv()
llm = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="claude-3-sonnet-20240229",
    # 注册回调：LLM 层级（仅该 LLM 生效）
    callbacks=[StdOutCallbackHandler()]
)

# 2. 组装 Runnable 链（Prompt + LLM）
prompt = ChatPromptTemplate.from_messages([("human", "用 2 句话介绍 LangChain 最新版")])
chain = prompt | llm

# 3. 最新版调用：用 invoke() 替代 run()
print("\n=== 内置 StdOutCallback 演示 ===")
result = chain.invoke({"input": ""})  # Prompt 无变量时传入空字典
print(f"\n最终响应：{result.content}")