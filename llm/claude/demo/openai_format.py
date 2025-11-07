import os
from openai import OpenAI

# 创建客户端时指定自定义的 base URL
api_key = os.getenv("GPTSAPI_API_KEY")
print(api_key)

client = OpenAI(
    api_key=api_key,
    base_url="https://api.gptsapi.net/v1",
)

# 发送请求
response = client.chat.completions.create(
    model="claude-3-5-sonnet-20241022", #填写claude模型名称即可
    messages=[
        {
            "role": "user",
            "content": "Hello!"
        }
    ]
)

# 打印返回结果
print(response.choices[0].message.content)