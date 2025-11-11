import os

from langchain_core.chat_history import InMemoryChatMessageHistory, BaseChatMessageHistory
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

# -------------------------- 1. 基础配置（必填）--------------------------
# 1. 读取 API Key（你的代理密钥，环境变量名：GPTSAPI_API_KEY）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

# 2. 代理配置（第三方代理地址）
base_url = "https://api.gptsapi.net/v1"

llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo"  # 可替换为 claude-3-sonnet-20240229、gemini-2.5-pro 等
)

# -------------------------- 2. 构建基础链（无记忆的核心逻辑）--------------------------
from langchain_classic.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_core.chat_history import InMemoryChatMessageHistory  # 对话存储核心
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# 提示词模板：必须包含 MessagesPlaceholder（变量名默认是 "history"）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的鲜花推荐助手，根据用户需求和对话历史提供建议，语气友好自然"),
    MessagesPlaceholder(variable_name="history"),  # 注入对话历史（关键）
    ("human", "{input}")  # 接收当前用户输入
])

# 基础链：提示词 → 模型 → 解析器（无记忆）
# 输出解析器（简化为字符串输出）
output_parser = StrOutputParser()
base_chain = prompt | llm | output_parser

# -------------------------- 3. 配置记忆组件 --------------------------
def get_session_history(session_id: str = "default") -> BaseChatMessageHistory:
    """多会话隔离存储（临时用字典，实际可替换为 Redis/MongoDB）"""
    if not hasattr(get_session_history, "session_store"):
        get_session_history.session_store = {}
    if session_id not in get_session_history.session_store:
        get_session_history.session_store[session_id] = InMemoryChatMessageHistory()
    return get_session_history.session_store[session_id]

# ------------------------- 4. 绑定记忆到链（核心：RunnableWithMessageHistory）-------------------------
# 用 RunnableWithMessageHistory 包装基础链，实现「自动记忆管理」：
# 绑定记忆的最终链
chain_with_history = RunnableWithMessageHistory(
    runnable=base_chain,  # 传入基础链
    get_session_history=lambda :get_session_history(),  # 传入「记忆获取函数」（按 session_id 分配记忆）
    input_messages_key="input",  # 指定用户输入的变量名（对应 prompt 中的 {input}）
    history_messages_key="history",  # 指定对话历史的变量名（对应 prompt 中的 MessagesPlaceholder）
)


def chat_with_history():
    print("🚀 鲜花推荐助手（输入 'quit' 退出，输入 'switch' 切换用户）")
    current_session_id = "user_001"  # 默认会话 ID（第一个用户）

    while True:
        user_input = input(f"\n用户[{current_session_id}]：")

        # 退出逻辑
        if user_input.lower() == "quit":
            print("👋 再见！")
            break

        # 切换用户（测试多会话隔离）
        if user_input.lower() == "switch":
            new_session_id = input("请输入新的会话 ID（如 user_002）：")
            current_session_id = new_session_id
            print(f"✅ 已切换到用户[{current_session_id}]，对话历史独立")
            continue

        # 执行链：传入用户输入 + 会话 ID（自动加载/更新记忆）
        result = chain_with_history.invoke(
            input={"input": user_input},  # 匹配 input_messages_key
            config={"configurable": {"session_id": current_session_id}}  # 传入会话 ID（关键）
        )

        print(f"助手：{result}")

if __name__ == "__main__":
    chat_with_history()