import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAIError

# 加载环境变量
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")

# 初始化模型
try:
    model = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo",
        temperature=0.6,
        timeout=15,
    )
except Exception as e:
    raise RuntimeError(f"模型初始化失败：{str(e)}") from e

# ---------------------- 1. 问题分类器 ----------------------
classifier_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    仅判断用户问题属于"养护"或"装饰"，输出结果只能是这两个词之一，无其他内容：
    - 养护类：浇水、施肥、保鲜、存活、病虫害、换水等；
    - 装饰类：搭配、插花、场地布置、颜色组合、容器选择等；
    无法明确时默认输出"养护"。
    """),
    ("user", "用户问题：{user_query}")
])
classifier_chain = classifier_prompt | model | StrOutputParser()

# ---------------------- 2. ChatBot A（养护专家） ----------------------
chatbot_a_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是鲜花养护专家 ChatBot A，回复要求：
    1. 分点列出具体操作步骤（如"每2天换水"）；
    2. 语言通俗，避免专业术语；
    3. 补充1条关键注意事项；
    仅输出养护指示，不闲聊。
    """),
    ("user", "用户问题：{user_query}")
])
chatbot_a_chain = chatbot_a_prompt | model | StrOutputParser()

# ---------------------- 3. ChatBot B（装饰专家） ----------------------
chatbot_b_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是鲜花装饰专家 ChatBot B，回复要求：
    1. 结合场景给出花材搭配、步骤；
    2. 说明搭配逻辑，普通人可上手；
    3. 补充1条氛围提升建议；
    仅输出装饰指示，不闲聊。
    """),
    ("user", "用户问题：{user_query}")
])
chatbot_b_chain = chatbot_b_prompt | model | StrOutputParser()

# ---------------------- 4. 条件分支 Chain ----------------------
full_chatbot_chain = (
        RunnablePassthrough.assign(query_type=classifier_chain)
        | RunnableBranch(
    (lambda x: x["query_type"] == "养护", chatbot_a_chain),
    (lambda x: x["query_type"] == "装饰", chatbot_b_chain),
    chatbot_a_chain  # 兜底
)
)


# ---------------------- 5. 手动输入交互逻辑 ----------------------
def flower_chatbot_interactive():
    """交互式鲜花客服：支持用户手动输入，连续提问"""
    print("=" * 80)
    print("🌸 易速鲜花智能客服")
    print("💧 可咨询：鲜花养护（浇水、保鲜、施肥等）")
    print("🎨 可咨询：鲜花装饰（搭配、插花、场地布置等）")
    print("📌 输入 'q' 或 'Q' 退出程序")
    print("=" * 80)

    while True:
        # 接收用户手动输入
        user_query = input("\n请输入你的问题：").strip()

        # 退出逻辑
        if user_query.lower() == "q":
            print("👋 感谢使用，再见！")
            break

        # 空输入处理
        if not user_query:
            print("❌ 请输入有效问题，不能为空！")
            continue

        try:
            # 执行客服逻辑
            print("\n🔍 正在分析问题...")
            response = full_chatbot_chain.invoke({"user_query": user_query})
            query_type = classifier_chain.invoke({"user_query": user_query}).strip()
            chatbot_name = "ChatBot A（养护专家）" if query_type == "养护" else "ChatBot B（装饰专家）"

            # 格式化输出结果（带颜色和分隔符）
            print("\n" + "-" * 60)
            print(f"📋 问题分类：{query_type}")
            print(f"🤖 回复专家：{chatbot_name}")
            print("💬 回复内容：")
            print(response)
            print("-" * 60)

        except OpenAIError as e:
            print(f"\n❌ API 调用失败：{str(e)}")
        except Exception as e:
            print(f"\n❌ 系统错误：{str(e)}")


# 启动交互式客服
if __name__ == "__main__":
    try:
        flower_chatbot_interactive()
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出，感谢使用！")
    except Exception as e:
        print(f"\n❌ 程序启动失败：{str(e)}")