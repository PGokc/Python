import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI  # 用 OpenAI 兼容接口连接 Ollama
from langchain_community.chat_models import ChatOllama  # 也可直接用 Ollama 专属接口（二选一）

# -------------- 方式 1：用 ChatOpenAI 兼容接口（推荐，复用之前的代码逻辑）--------------
llm = ChatOpenAI(
    # Ollama 本地 API 地址（默认固定）
    base_url="http://localhost:11434/v1",
    # Ollama 无需 API Key，随便填一个字符串即可
    api_key="ollama-local",
    # 模型名称（必须与 Ollama 运行的模型一致，如 qwen:7b）
    model="qwen:7b",
    temperature=0.7,  # 控制生成随机性（0-1）
    timeout=30  # 超时时间
)

# -------------- 方式 2：用 Ollama 专属接口（更原生，功能更全）--------------
# from langchain_community.chat_models import ChatOllama
# llm = ChatOllama(
#     model="qwen:7b",  # 模型名称
#     temperature=0.7,
#     base_url="http://localhost:11434",  # Ollama 服务地址
#     # 可选：调整模型参数（如最大输出长度）
#     max_tokens=1024
# )

# ---------------------- 测试：鲜花文案生成（CoT 逻辑）----------------------
# 定义提示模板（鲜花店文案生成）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是花店AI助手，为鲜花写吸引人的电商文案（15-20字），突出花语和场景。"),
    ("user", "为售价35元的粉色芍药写一句文案。")
])

# 构建链并执行（复用之前的管道语法）
chain = prompt | llm
response = chain.invoke({})

# 输出结果
print("=== 开源模型（Qwen-7B）生成结果 ===")
print(response.content)
