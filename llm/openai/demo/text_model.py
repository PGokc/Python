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
response = client.completions.create(
    model="gpt-3.5-turbo-instruct",
    temperature=0.5,
    max_tokens=100,
    prompt="请给我的花店起个名"
)
print(response.choices[0].text.strip())