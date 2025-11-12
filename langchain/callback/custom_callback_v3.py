import os
from typing import Any

from langchain_core.callbacks import StreamingStdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


class CustomStreamingCallback(StreamingStdOutCallbackHandler):
    def __init__(self, log_file="stream_log.txt"):
        self.log_file = log_file
        self.file = open(log_file, "a", encoding="utf-8")  # 打开日志文件

    # 每生成一个 Token 触发一次
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        print(token, end="", flush=True)  # 逐字打印
        self.file.write(token)  # 逐字写入文件

    # 流式结束时关闭文件
    def on_llm_end(self, response: Any, **kwargs) -> None:
        self.file.close()
        print("\n✅ 流式输出完成，日志已保存到 stream_log.txt")

# 初始化流式 LLM + 自定义流式回调
custom_stream_llm = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="claude-3-sonnet-20240229",
    streaming=True,
    callbacks=[CustomStreamingCallback()]
)

# 组装并调用流式链
prompt = ChatPromptTemplate.from_messages([("human", "用 2 句话介绍 LangChain 最新版")])
custom_stream_chain = prompt | custom_stream_llm
print("\n=== 自定义 StreamingCallback 演示 ===")
print("流式响应：", end="", flush=True)
for chunk in custom_stream_chain.stream({"input": ""}):
    pass