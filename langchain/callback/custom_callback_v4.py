import os
import time
from typing import Dict, Any

from langchain_core.callbacks import BaseCallbackHandler, StdOutCallbackHandler
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_openai import ChatOpenAI

# 1. 会话记忆存储（多用户隔离）
session_store = {}
def get_session_history(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = InMemoryChatMessageHistory()
    return session_store[session_id]

# 2. 带记忆的 Prompt 模板
memory_prompt = ChatPromptTemplate.from_messages([
    ("system", "你会记住用户的历史对话，无需重复说明。"),
    ("placeholder", "{chat_history}"),
    ("human", "{input}")
])

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
    model="gpt-3.5-turbo",
    callbacks=[
        StdOutCallbackHandler(),  # 内置日志回调
        PerformanceMonitorCallback()  # 自定义性能回调
    ]
)

# 3. 组装带记忆的链 + 回调
memory_chain = memory_prompt | llm_with_monitor  # 绑定性能监控回调
chain_with_history = RunnableWithMessageHistory(
    runnable=memory_chain,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history"
)

# 4. 多轮对话测试（带回调监控）
print("\n=== 带记忆+回调的多轮对话（输入 '退出' 结束）===")
SESSION_ID = "user_001"
while True:
    user_input = input("\n你：")
    if user_input == "退出":
        break
    # 调用带记忆的链，传入 session_id
    result = chain_with_history.invoke(
        {"input": user_input},
        config={"configurable": {"session_id": SESSION_ID}}
    )
    print(f"助手：{result.content}")