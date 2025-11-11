import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from openai import OpenAIError

# 加载环境变量
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")

# 初始化统一模型（也可给不同角色配置不同 temperature，如植物学家 0.3 更严谨）
try:
    model = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo",
        timeout=20,
    )
except Exception as e:
    raise RuntimeError(f"模型初始化失败：{str(e)}") from e

# ---------------------- 第一步：植物学家 → 输出鲜花专业知识 ----------------------
botanist_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是资深植物学家，专注于花卉研究。请针对"{flower_type}"输出以下专业知识（分点列出，语言简洁准确）：
    1. 植物分类（科属、学名）；
    2. 形态特征（花型、花色、花期）；
    3. 生长习性（适宜环境、分布区域）；
    4. 花语起源与文化寓意（历史背景、核心象征）。
    仅输出知识，不添加额外评论或情感表达。
    """),
    ("user", "请提供 {flower_type} 的专业植物学知识。")
])

# 构建植物学家 Chain
botanist_chain = botanist_prompt | model

# ---------------------- 第二步：鲜花评论者 → 基于植物学知识写评论 ----------------------
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是资深鲜花评论者，擅长从专业+大众视角点评鲜花。请参考以下植物学知识：
    {botanist_knowledge}
    输出一篇 150-200 字的评论，要求：
    1. 结合植物学特征（如花型、花期），突出鲜花的独特观赏价值；
    2. 关联花语文化，挖掘情感共鸣点；
    3. 语言生动有感染力，符合普通消费者的审美视角；
    4. 不堆砌专业术语，兼顾专业性和易懂性。
    """),
    ("user", "请基于上述植物学知识，点评 {flower_type}。")
])

# 构建评论者 Chain（依赖第一步的植物学知识）
critic_chain = (
        RunnablePassthrough.assign(
            botanist_knowledge=botanist_chain  # 先执行植物学家 Chain，获取知识
        )
        | critic_prompt
        | model
)

# ---------------------- 第三步：运营经理 → 基于前两步写社交媒体文案 ----------------------
marketer_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是易速鲜花的社交媒体运营经理，负责小红书/朋友圈风格的运营文案。请参考以下信息：
    1. 植物学知识：{botanist_knowledge}
    2. 鲜花评论：{critic_comment}
    输出一篇 200-250 字的运营文案，要求：
    1. 开头吸引眼球（用emoji+场景化表达）；
    2. 突出核心卖点（结合花型、花语、情感价值）；
    3. 语言活泼有互动性（使用口语化表达、设问/感叹）；
    4. 结尾加行动号召（如“戳链接带走”“送TA一份惊喜”）；
    5. 带2-3个相关话题标签（如 #洋桔梗花语 #鲜花送礼指南）。
    """),
    ("user", "请基于植物学知识和专业评论，写一篇 {flower_type} 的社交媒体运营文案。")
])

# 构建运营经理 Chain（依赖第一步和第二步的结果）
full_chain = (
        RunnablePassthrough.assign(
            # 先执行前两步，获取依赖数据
            botanist_knowledge=botanist_chain,
            critic_comment=critic_chain
        )
        | marketer_prompt
        | model
)


# ---------------------- 执行完整流程 ----------------------
def generate_flower_full_flow(flower_type: str) -> dict:
    """
    执行三步流程：植物学知识 → 专业评论 → 运营文案
    :param flower_type: 鲜花类型（如"洋桔梗"）
    :return: 包含三步结果的字典
    """
    try:
        # 执行完整 Chain，传入鲜花类型
        result = full_chain.invoke({"flower_type": flower_type})

        # 单独获取前两步的结果（用于展示）
        botanist_result = botanist_chain.invoke({"flower_type": flower_type}).content.strip()
        critic_result = critic_chain.invoke({"flower_type": flower_type}).content.strip()
        marketer_result = result.content.strip()

        return {
            "植物学家知识": botanist_result,
            "鲜花评论者点评": critic_result,
            "社交媒体运营文案": marketer_result
        }
    except OpenAIError as e:
        raise RuntimeError(f"API 调用失败：{str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"流程执行失败：{str(e)}") from e


# 测试调用（以「洋桔梗」为例）
if __name__ == "__main__":
    flower_type = "洋桔梗"
    try:
        full_result = generate_flower_full_flow(flower_type)

        # 打印三步结果
        print("=" * 80)
        print(f"🌹 三步流程结果（{flower_type}）")
        print("=" * 80)

        for role, content in full_result.items():
            print(f"\n【{role}】")
            print("-" * 50)
            print(content)

    except Exception as e:
        print(f"❌ 错误：{str(e)}")