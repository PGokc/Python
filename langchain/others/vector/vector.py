import os
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

# 1. 配置 Claude API Key（从 Anthropic 官网获取：https://console.anthropic.com/）
os.environ["GPTSAPI_API_KEY"] = "你的 Claude API Key"  # 替换为真实 API Key

# 2. 初始化 Claude 模型（使用最新稳定版）
llm = ChatAnthropic(
    model_name="claude-3-sonnet-20240229",  # 主流选择：平衡性能和成本
    temperature=0.7,  # 控制随机性（0-1，0 更严谨，1 更多样）
    timeout=30
)

# 3. 定义提示模板（可选，简化直接调用也可）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个简洁的助手，用自然语言直接回答问题"),
    ("user", "{question}")
])

# 4. 构建链并调用（核心逻辑）
chain = prompt | llm
result = chain.invoke({"question": "介绍下 Claude 模型的核心优势，用3句话总结"})

# 5. 输出结果
print("Claude 响应：")
print(result.content)