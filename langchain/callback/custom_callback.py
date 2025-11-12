import os
import time
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.callbacks import BaseCallbackHandler, StdOutCallbackHandler


# 1. 自定义回调类（继承 BaseCallbackHandler）
class PerformanceMonitorCallback(BaseCallbackHandler):
    # LLM 开始调用时触发
    def __init__(self):
        self.start_time = None

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: list[str], **kwargs
    ) -> None:
        self.start_time = time.time()
        print(f"\n📊 LLM 开始调用，Prompt：{prompts[0]}")

    # LLM 调用成功结束时触发
    def on_llm_end(self, response: Any, **kwargs) -> None:
        elapsed_time = time.time() - self.start_time
        print(f"📊 LLM 调用完成，耗时：{elapsed_time:.2f} 秒")

    # LLM 调用出错时触发（可选）
    def on_llm_error(self, error: Exception, **kwargs) -> None:
        print(f"❌ LLM 调用失败：{str(error)}")

# 2. 注册自定义回调（可同时注册多个）
llm_with_monitor = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="claude-3-sonnet-20240229",
    callbacks=[
        StdOutCallbackHandler(),  # 内置日志回调
        PerformanceMonitorCallback()  # 自定义性能回调
    ]
)

# 3. 组装并调用链
prompt = ChatPromptTemplate.from_messages([("human", "用 2 句话介绍 LangChain 最新版")])
monitor_chain = prompt | llm_with_monitor
print("\n=== 自定义 PerformanceMonitorCallback 演示 ===")
monitor_chain.invoke({"input": ""})