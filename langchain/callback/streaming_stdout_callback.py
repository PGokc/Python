import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# 1. 初始化流式 LLM（必须设置 streaming=True）
streaming_llm = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="claude-3-sonnet-20240229",
    streaming=True,  # 开启流式
    callbacks=[StreamingStdOutCallbackHandler()]  # 流式回调
)

# 2. 组装流式链
prompt = ChatPromptTemplate.from_messages([("human", "用 2 句话介绍 LangChain 最新版")])
stream_chain = prompt | streaming_llm

# 3. 最新版流式调用：用 stream() 替代 invoke()
print("\n=== 内置 StreamingStdOutCallback 演示 ===")
print("流式响应：", end="", flush=True)
# stream() 返回生成器，需迭代消费（自动触发逐字输出）
for chunk in stream_chain.stream({"input": ""}):
    pass  # 回调已实时打印，无需额外处理