import os

from openai import OpenAI

client = OpenAI(
    # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

response = client.completions.create(
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    model="qwen-plus",
    temperature=0.5,
    max_tokens=1000,
    prompt="我是一名CSGO玩家，请用恶毒的语言攻击我最薄弱的地方！"
)

print(response.choices[0].message.content.strip())