import os
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
    model="claude-3-sonnet-20240229"  # 可替换为 claude-3-sonnet-20240229、gemini-pro 等
)

# -------------------------- 2. 初始化 Memory（你的指定路径）--------------------------
from langchain_classic import ConversationChain
from langchain_classic.memory import ConversationBufferWindowMemory

# 只保留最近 2 轮对话（k=2）
memory = ConversationBufferWindowMemory(
    k=2,  # 窗口大小：保留最近 2 轮（每轮含用户+助手消息）
    return_messages=True
)

chain = ConversationChain(llm=llm, memory=memory, verbose=False)

# 测试多轮对话（超过 2 轮后，最早的对话会被丢弃）
print("=== ConversationBufferWindowMemory（k=2）===")
print(chain.invoke({"input": "红玫瑰单价多少？"})["response"])
print(chain.invoke({"input": "买10束能打折吗？"})["response"])
print(chain.invoke({"input": "北京能当天送吗？"})["response"])  # 此时会丢弃第一轮“红玫瑰价格”的记忆

# 查看当前记忆（仅保留后 2 轮）
print("\n当前记忆内容：")
for msg in memory.load_memory_variables({})["history"]:
    print(f"{msg.type}: {msg.content}")