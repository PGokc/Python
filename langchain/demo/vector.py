from langchain_openai import OpenAIEmbeddings
import os

api_key = os.getenv("GPTSAPI_API_KEY")
embedding_model = OpenAIEmbeddings(
    api_key=api_key,
    base_url="https://api.gptsapi.net/v1",
)
# 生成文本向量
vector = embedding_model.embed_query("情人节红玫瑰")
print(len(vector))  # 输出 1536（向量维度）
print(vector[:5])  # 输出前5个数字：[0.0123, -0.0456, ...]