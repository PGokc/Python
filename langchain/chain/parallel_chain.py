import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAIError

# 加载环境变量（GPTSAPI 代理配置）
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")

# 初始化大模型（所有并行任务共用一个模型，也可单独配置）
try:
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo",
        temperature=0.6,
        timeout=15,
    )
except Exception as e:
    raise RuntimeError(f"模型初始化失败：{str(e)}") from e

# ---------------------- 1. 定义 4 个并行任务（每个任务都是独立的 Runnable 流程） ----------------------
# 任务1：生成核心花语（1句话概括）
task_flower_language = (
        ChatPromptTemplate.from_messages([
            ("user", "生成{flower_type}的核心花语，1句话概括（≤30字），符合大众认知。")
        ])
        | llm
        | StrOutputParser()
)

# 任务2：提炼营销卖点（3个核心卖点，分点）
task_selling_points = (
        ChatPromptTemplate.from_messages([
            ("user", "提炼{flower_type}的3个营销卖点，分点列出（每点≤15字），突出差异化优势。")
        ])
        | llm
        | StrOutputParser()
)

# 任务3：推荐适用场景（3个场景，分点）
task_applicable_scenes = (
        ChatPromptTemplate.from_messages([
            ("user", "推荐{flower_type}的3个适用场景，分点列出（每点≤10字），覆盖送礼/自用/装饰。")
        ])
        | llm
        | StrOutputParser()
)

# 任务4：生成话题标签（3-5个，适配小红书/抖音）
task_hashtags = (
        ChatPromptTemplate.from_messages([
            ("user", "生成{flower_type}的3-5个话题标签，格式为#XXX，贴合鲜花营销和年轻用户喜好。")
        ])
        | llm
        | StrOutputParser()
)

# ---------------------- 2. 包装并行流程（核心：RunnableParallel） ----------------------
# 用字典形式定义并行任务，key 为任务名，value 为任务流程
parallel_chain = RunnableParallel(
    核心花语=task_flower_language,
    营销卖点=task_selling_points,
    适用场景=task_applicable_scenes,
    话题标签=task_hashtags
)


# ---------------------- 3. 执行并行流程 + 结果合并 ----------------------
def generate_flower_marketing_materials(flower_type: str) -> dict:
    """
    并行生成鲜花营销素材：花语+卖点+场景+标签
    :param flower_type: 鲜花类型（如"绣球花"）
    :return: 合并后的营销素材字典
    """
    try:
        # 执行并行流程（一次 invoke，同时完成 4 个任务）
        print(f"🔍 正在并行生成{flower_type}的营销素材...")
        results = parallel_chain.invoke({"flower_type": flower_type})

        # （可选）将并行结果拼接成完整营销文案
        full_copy = f"""
🌸 {flower_type} 营销文案
【核心花语】：{results['核心花语']}
【营销卖点】：
{results['营销卖点']}
【适用场景】：
{results['适用场景']}
【话题标签】：{results['话题标签']}
        """

        # 返回原始并行结果 + 拼接后的完整文案
        return {
            "原始并行结果": results,
            "完整营销文案": full_copy.strip()
        }
    except OpenAIError as e:
        raise RuntimeError(f"API 调用失败：{str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"并行流程执行失败：{str(e)}") from e


# ---------------------- 测试调用 ----------------------
if __name__ == "__main__":
    flower_type = "绣球花"
    try:
        marketing_materials = generate_flower_marketing_materials(flower_type)

        # 打印结果
        print("=" * 80)
        print(f"🌹 {flower_type} 营销素材（并行流程生成）")
        print("=" * 80)

        # 1. 打印原始并行结果（分任务展示）
        print("\n【原始并行结果】")
        print("-" * 50)
        for task_name, result in marketing_materials["原始并行结果"].items():
            print(f"\n{task_name}：")
            print(result)

        # 2. 打印拼接后的完整营销文案
        print("\n\n【完整营销文案】")
        print("-" * 50)
        print(marketing_materials["完整营销文案"])

    except Exception as e:
        print(f"❌ 错误：{str(e)}")