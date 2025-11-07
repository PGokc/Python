import os
from openai import OpenAI

# 1. 根据apiKey创建client
api_key = os.getenv("GPTSAPI_API_KEY")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.gptsapi.net/v1",
)

# 2. 调用Chat模型
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "user",
            "content": "请写一句情人节花店的宣传语！"
        }
    ]
)

# 打印返回结果
print(response.choices[0].message.content)