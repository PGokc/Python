import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableSequence  # Chain 核心类
from openai import OpenAIError

# 加载环境变量
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")

# 1. 定义 Pydantic 模型（与无 Chain 版本一致）
class FlowerLanguage(BaseModel):
    core_meaning: str = Field(description="核心花语（≤30字）")
    detailed_meanings: list[str] = Field(description="1-3点详细花语（每点≤20字）")
    applicable_scene: str = Field(description="适用场景（≤20字）")

# 2. 创建组件：Prompt 模板 + 模型 + 解析器
parser = PydanticOutputParser(pydantic_object=FlowerLanguage)

# Prompt 模板（嵌入格式指令，支持动态传入 flower_type）
prompt = ChatPromptTemplate.from_messages([
    ("user", """
    提供"{flower_type}"的花语，严格按以下格式输出（无额外内容）：
    {format_instructions}
    要求：内容符合大众认知，格式正确。
    """)
])

# 初始化模型
try:
    model = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo",
        temperature=0.5,
        timeout=15
    )
except Exception as e:
    raise RuntimeError(f"模型初始化失败：{str(e)}") from e

# 3. 构建 Chain：串联 Prompt → 模型 → 解析器（核心）
# 方式1：用 | 运算符（简洁，LangChain 1.0+ 推荐）
# chain = prompt.partial(format_instructions=parser.get_format_instructions()) | model | parser

# 方式2：用 RunnableSequence（显式定义，等价于 |）
chain = RunnableSequence(
    prompt.partial(format_instructions=parser.get_format_instructions()),
    model,
    parser
)

def get_flower_language_with_chain(flower_type: str) -> FlowerLanguage:
    """使用 Chain：自动串联流程，无需手动调用模型/解析"""
    try:
        # 只需调用 chain.invoke()，传入参数即可
        result = chain.invoke({"flower_type": flower_type})
        return result
    except OpenAIError as e:
        raise RuntimeError(f"API 调用失败：{str(e)}") from e
    except Exception as e:
        raise RuntimeError(f"Chain 执行失败：{str(e)}") from e

# 测试
if __name__ == "__main__":
    flower_type = "铃兰"
    try:
        result = get_flower_language_with_chain(flower_type)
        print(f"🌹 {flower_type} 花语（有 Chain）：")
        print(f"核心：{result.core_meaning}")
        print(f"详细：{result.detailed_meanings}")
        print(f"场景：{result.applicable_scene}")
    except Exception as e:
        print(f"❌ 错误：{str(e)}")