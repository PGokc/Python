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
    model="gpc-3.5-turbo"  # 可替换为 claude-3-sonnet-20240229、gemini-2.5-pro 等
)

# -------------------------- 2. 初始化 Memory（你的指定路径）--------------------------
from langchain_classic import ConversationChain
from langchain_classic.memory import ConversationBufferMemory
from langchain_core.runnables.history import RunnableWithMessageHistory  # 官方推荐替代组件
# ConversationBufferMemory：完整存储所有对话，不截断，不压缩
memory = ConversationBufferMemory(
    return_messages=True,  # 返回 ChatMessage 格式（HumanMessage/AIMessage），更易读
    memory_key="history" # 与 ConversationChain 的记忆键对应（默认就是 chat_history，可省略）
)

# -------------------------- 3. 创建带记忆的对话链 --------------------------
conversation_chain = ConversationChain(
    llm=llm,
    memory=memory,
    verbose=False,  # 需调试时设为 True，查看 Prompt 拼接和记忆加载过程
    input_key="input",  # 接收用户输入的键名（默认 input，可省略）
    output_key="response"  # 输出响应的键名（默认 response，可省略）
)

# -------------------------- 4. 多轮对话测试 --------------------------
print("=== 带记忆的多轮对话（输入 '退出' 结束）===")
print("提示：对话会记住你的历史需求（如价格、数量、偏好），无需重复说明~")

while True:
    user_input = input("\n你：")
    if user_input.strip() == "退出":
        print("助手：再见！有任何需求随时回来~")
        break

    # 调用对话链，自动加载历史记忆
    result = conversation_chain.invoke({"input": user_input})

    # 输出助手响应
    print(f"助手：{result['response']}")

# -------------------------- 5. 查看最终记忆内容（可选）--------------------------
print("\n=== 本次对话的完整记忆 ===")
# 加载记忆中的所有对话（return_messages=True 时返回 ChatMessage 列表）
chat_history = memory.load_memory_variables({})["history"]
for msg in chat_history:
    print(f"{msg.type}: {msg.content}")
