import os

from langchain_classic.chains.conversation.base import ConversationChain
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
from langchain_classic.chains.conversation.memory import ConversationSummaryMemory
from langchain_core.runnables.history import RunnableWithMessageHistory  # 官方推荐替代组件
# ConversationBufferMemory：完整存储所有对话，不截断，不压缩
memory = ConversationSummaryMemory(
    llm=llm,
    return_messages=True,  # 返回 ChatMessage 格式（HumanMessage/AIMessage），更易读
    memory_key="history" # 与 ConversationChain 的记忆键对应（默认就是 chat_history，可省略）
)

# -------------------------- 3. 创建带记忆的对话链 --------------------------
chain = ConversationChain(llm=llm, memory=memory, verbose=False)

# -------------------------- 3. 测试超长对话 --------------------------
print("=== ConversationSummaryMemory（摘要记忆）===")
chain.invoke({"input": "红玫瑰单价 39 元/束，含包装"})
chain.invoke({"input": "买 10 束打 9 折，总价 351 元"})
chain.invoke({"input": "北京主城区支持当日达，14:00 前下单"})
chain.invoke({"input": "需要粉色包装+白色满天星点缀"})

# 让助手总结订单信息（基于摘要记忆）
print(chain.invoke({"input": "总结一下我的订单所有信息？"})["response"])

# 查看生成的对话摘要
print("\n对话摘要：")
summary = memory.load_memory_variables({})["history"][0].content
print(summary)