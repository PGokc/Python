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

# 初始化统一模型（也可给分类器/不同ChatBot配置不同temperature）
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

# ---------------------- 1. 问题分类器：判断问题类型（养护/装饰） ----------------------
# 分类 Prompt：让模型输出"养护"或"装饰"，无其他内容
classifier_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是问题分类专家，仅需判断用户问题属于以下哪一类，输出结果只能是"养护"或"装饰"，不添加任何额外文字：
    - 养护类：涉及鲜花存活、健康、浇水、施肥、保鲜、病虫害防治等问题；
    - 装饰类：涉及鲜花搭配、颜色组合、场地装饰、插花技巧、场景布置等问题。
    若无法明确分类，默认输出"养护"。
    """),
    ("user", "用户问题：{user_query}")
])

# 分类 Chain：输出"养护"或"装饰"字符串
classifier_chain = classifier_prompt | model | StrOutputParser()

# ---------------------- 2. ChatBot A：鲜花养护专家（对应养护类问题） ----------------------
chatbot_a_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是资深鲜花养护专家 ChatBot A，负责解答鲜花养护相关问题，按以下要求回复：
    1. 针对性：聚焦用户问题（如浇水、保鲜、施肥），不偏离主题；
    2. 实操性：给出具体步骤（如"每2天换一次水"），避免空泛建议；
    3. 简洁性：分点列出核心操作，语言通俗易懂，适合普通用户；
    4. 补充提示：可添加1条关键注意事项（如"避免阳光直射"）。
    仅输出养护指示，不添加额外闲聊内容。
    """),
    ("user", "用户问题：{user_query}")
])

chatbot_a_chain = chatbot_a_prompt | model | StrOutputParser()

# ---------------------- 3. ChatBot B：鲜花装饰专家（对应装饰类问题） ----------------------
chatbot_b_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是资深鲜花装饰专家 ChatBot B，负责解答鲜花装饰/搭配相关问题，按以下要求回复：
    1. 场景化：结合用户提到的场景（如客厅、婚礼、生日）给出方案；
    2. 搭配逻辑：说明花材组合、颜色搭配、容器选择的理由；
    3. 实操性：给出具体装饰步骤或插花技巧，普通人可直接上手；
    4. 氛围营造：补充1条提升装饰效果的小建议（如"搭配绿植增加层次感"）。
    仅输出装饰指示，不添加额外闲聊内容。
    """),
    ("user", "用户问题：{user_query}")
])

chatbot_b_chain = chatbot_b_prompt | model | StrOutputParser()

# ---------------------- 4. 条件分支 Chain：根据分类路由到对应ChatBot ----------------------
# 核心：RunnableBranch 实现条件判断，按分类结果执行不同Chain
full_chatbot_chain = (
        RunnablePassthrough.assign(
            # 第一步：先执行分类，将结果存入"query_type"字段
            query_type=classifier_chain
        )
        | RunnableBranch(
    # 分支1：如果是"养护"，执行ChatBot A
    (lambda x: x["query_type"] == "养护", chatbot_a_chain),
    # 分支2：如果是"装饰"，执行ChatBot B
    (lambda x: x["query_type"] == "装饰", chatbot_b_chain),
    # 默认分支：兜底执行ChatBot A（防止分类失败）
    chatbot_a_chain
)
)


# ---------------------- 封装客服调用函数 ----------------------
def flower_chatbot(user_query: str) -> dict:
    """
    鲜花运营智能客服入口函数
    :param user_query: 用户问题（如"玫瑰怎么保鲜更久？"）
    :return: 包含问题分类、对应ChatBot、回复内容的字典
    """
    try:
        # 执行完整Chain
        response = full_chatbot_chain.invoke({"user_query": user_query})

        # 单独获取分类结果（用于展示）
        query_type = classifier_chain.invoke({"user_query": user_query}).strip()
        chatbot_name = "ChatBot A（养护专家）" if query_type == "养护" else "ChatBot B（装饰专家）"

        return {
            "用户问题": user_query,
            "问题分类": query_type,
            "执行ChatBot": chatbot_name,
            "回复内容": response.strip()
        }
    except OpenAIError as e:
        raise RuntimeError(f"API 调用失败：{str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"客服执行失败：{str(e)}") from e


# ---------------------- 测试调用 ----------------------
if __name__ == "__main__":
    # 测试两个类型的问题
    test_queries = [
        # 养护类问题
        "洋桔梗买回家后怎么浇水才能活更久？",
        # 装饰类问题
        "婚礼现场用郁金香和满天星怎么搭配装饰主舞台？"
    ]

    for query in test_queries:
        print("=" * 80)
        result = flower_chatbot(query)
        for key, value in result.items():
            print(f"\n【{key}】")
            print("-" * 50)
            print(value)
        print("\n" + "=" * 80)