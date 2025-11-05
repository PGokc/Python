import os

from openai import OpenAI
print(os.getenv("OPENAI_API_KEY"))

client = OpenAI()

# 调用Text模型
response = client.responses.create(
    model="gpt-5",
    input="Write a one-sentence bedtime story about a unicorn."
)

print(response.output_text)

# 调用Chat模型
response = client.chat.completions.create(
  model="gpt-4",
  messages=[
        {"role": "system", "content": "You are a creative AI."},
        {"role": "user", "content": "请给我的花店起个名"},
    ],
  temperature=0.8,
  max_tokens=60
)

