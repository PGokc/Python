import os
from langchain_openai import ChatOpenAI

# -------------------------- 基础配置（必填）--------------------------
# 1. 读取 API Key（你的代理密钥，环境变量名：GPTSAPI_API_KEY）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

# 2. 代理配置（第三方代理地址）
base_url = "https://api.gptsapi.net/v1"

# -------------------------- 初始化大模型客户端 --------------------------
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,  # 统一代理地址不变
    model="claude-3-sonnet-20240229",  # Claude 模型名称（支持 claude-3-haiku、claude-3-opus 等）
    temperature=0.7
)

# -------------------------- 简单调用 --------------------------
result = llm.invoke("用一句话推荐适合送妈妈的鲜花")
print("Claude 响应：", result.content)