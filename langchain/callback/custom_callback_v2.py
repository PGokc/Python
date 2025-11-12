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

# 链级别回调
class ChainMonitorCallback(BaseCallbackHandler):
    # 链开始执行时触发
    def __init__(self):
        self.chain_start_time = None

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs
    ) -> None:
        self.chain_start_time = time.time()
        print(f"\n🔗 链开始执行，输入：{inputs}")

    # 链执行成功结束时触发
    def on_chain_end(self, outputs: Any, **kwargs) -> None:
        chain_elapsed = time.time() - self.chain_start_time
        print(f"🔗 链执行完成，耗时：{chain_elapsed:.2f} 秒，输出长度：{len(outputs.content)} 字")

# 组装链时注册回调（链层级，覆盖 LLM 层级回调）
prompt = ChatPromptTemplate.from_messages([("human", "用 2 句话介绍 LangChain 最新版")])
chain_with_chain_callback = prompt | llm_with_monitor
chain_with_chain_callback = chain_with_chain_callback.with_config(
    callbacks=[ChainMonitorCallback()]  # 链级回调
)

print("\n=== 自定义 ChainMonitorCallback 演示 ===")
chain_with_chain_callback.invoke({"input": ""})