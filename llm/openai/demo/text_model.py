import os
from openai import OpenAI

# 1. 根据apiKey创建client
api_key = os.getenv("GPTSAPI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.gptsapi.net/v1",
)

# 2. 调用Text模型(调用报错404)
# 文本模型仅适用于纯文本续写，对话、Agent 等场景优先用聊天模型。
# GPTSAPI不支持纯文本模型，所以用聊天模型模拟文本模型：仅传 1 条 user 消息，实现文本生成
response = client.chat.completions.create(
    model="gpt-3.5-turbo",  # 列表中支持的聊天模型，任选一个
    messages=[{"role": "user", "content": "请给我的花店起个名"}],  # 文本续写 prompt
    temperature=0.7,
)

# 提取结果（和文本模型用法类似，仅结果路径不同）
print(response.choices[0].message.content.strip())