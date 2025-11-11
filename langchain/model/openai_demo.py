import os
from langchain_openai import OpenAI  # 文本模型专用类
from langchain_openai import ChatOpenAI  # 聊天模型专用类
from langchain_core.messages import HumanMessage  # 构造聊天模型输入

# -------------------------- 基础配置（必填）--------------------------
# 1. 读取 API Key（你的代理密钥，环境变量名：GPTSAPI_API_KEY）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

# 2. 代理配置（第三方代理地址）
base_url = "https://api.gptsapi.net/v1"

# -------------------------- 1. 调用 OpenAI 文本模型 --------------------------
# 适用场景：文本续写、简单生成、代码补全（纯文本输入输出）
# 推荐模型：gpt-3.5-turbo-instruct（官方主推）、text-davinci-003（兼容旧场景）
def call_text_model(prompt: str):
    # 初始化文本模型
    text_llm = OpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo-instruct",  # 文本模型名称（代理需支持）
        temperature=0.7,  # 随机性：0=确定，1=灵活
        max_tokens=200,  # 输出最大 Token 数
        timeout=15  # 超时时间
    )

    # 调用模型（直接传入纯文本 prompt）
    try:
        result = text_llm.invoke(prompt)  # 文本模型直接传字符串
        return {"模型类型": "文本模型（gpt-3.5-turbo-instruct）", "结果": result.strip()}
    except Exception as e:
        return {"模型类型": "文本模型（gpt-3.5-turbo-instruct）", "错误": f"{type(e).__name__}: {str(e)}"}


# -------------------------- 2. 调用 OpenAI 聊天模型 --------------------------
# 适用场景：多轮对话、智能助手、Agent 工具调用（结构化输入）
# 推荐模型：gpt-3.5-turbo（代理支持率最高）、gpt-4-turbo（需代理支持）
def call_chat_model(user_query: str):
    # 初始化聊天模型
    chat_llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo",  # 聊天模型名称（代理大概率支持）
        temperature=0.7,
        max_tokens=200,
        timeout=15
    )

    # 构造输入（聊天模型必须用 messages 列表，HumanMessage 表示用户输入）
    messages = [HumanMessage(content=user_query)]

    # 调用模型
    try:
        result = chat_llm.invoke(messages)  # 传入 messages 列表
        return {"模型类型": "聊天模型（gpt-3.5-turbo）", "结果": result.content.strip()}
    except Exception as e:
        return {"模型类型": "聊天模型（gpt-3.5-turbo）", "错误": f"{type(e).__name__}: {str(e)}"}


# -------------------------- 测试调用 --------------------------
if __name__ == "__main__":
    # 测试 prompt（给花店起名）
    prompt = "请给我的花店起5个温馨、有诗意的名字，每个名字配1句简短解释"

    # 1. 调用文本模型
    text_result = call_text_model(prompt)
    print("=" * 50)
    for k, v in text_result.items():
        print(f"{k}：{v}")

    # 2. 调用聊天模型
    chat_result = call_chat_model(prompt)
    print("\n" + "=" * 50)
    for k, v in chat_result.items():
        print(f"{k}：{v}")