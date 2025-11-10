from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from pydantic import BaseModel, Field


# --------------------------
# 1. 定义 Pydantic 结构化模型（不变）
# --------------------------
class FlowerCopywriting(BaseModel):
    description: str = Field(
        description="鲜花的描述文案，15-30字，突出场景感和吸引力",
        min_length=15,
        max_length=30
    )
    reason: str = Field(
        description="文案设计理由，结合价格和寓意，15-25字",
        min_length=15,
        max_length=25
    )

# 1. 基础组件初始化（和 Pydantic 解析器一致）
output_parser = PydanticOutputParser(pydantic_object=FlowerCopywriting)
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = 'https://api.gptsapi.net/v1'
try:
    llm = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo",
        temperature=0.7,
        timeout=15
    )
except Exception as e:
    raise RuntimeError(f"模型初始化失败：{str(e)}") from e

# 2. 主生成提示词（和基础解析器一致）
main_prompt = PromptTemplate(
    template="""
    为 {price} 元的 {flower} 创作文案和理由，严格遵守：
    1. 仅返回 JSON，无额外文字/换行；
    2. 包含字段：description（15-30字）、reason（15-25字）；
    """,
    input_variables=["flower", "price"],
)

# 3. 修复提示词（核心：告诉 LLM 如何修复错误）
fix_prompt = PromptTemplate(
    template="""
    你需要修复以下错误的输出，使其符合要求：
    1. 输出格式：仅返回 JSON，包含 description（15-30字）、reason（15-25字）；
    2. 错误输出：{bad_output}
    3. 错误原因：{error_msg}
    注意：只返回修复后的 JSON，不要添加任何额外内容！
    """,
    input_variables=["bad_output", "error_msg"],
)


# 4. 自定义修复逻辑（RunnableLambda 嵌入函数）
def parse_or_fix(input_data):
    """解析失败则自动修复"""
    bad_output = input_data["model_output"]  # 模型原始输出
    try:
        # 第一次尝试解析
        return output_parser.parse(bad_output)
    except OutputParserException as e:
        error_msg = str(e)
        print(f"❌ 解析失败：{error_msg}，正在自动修复...")

        # 调用 LLM 修复错误输出
        fixed_output = (fix_prompt | llm).invoke({
            "bad_output": bad_output,
            "error_msg": error_msg
        }).content

        print(f"✅ 修复后输出：{fixed_output}")
        # 修复后重新解析
        return output_parser.parse(fixed_output)


# 5. 构建完整链（生成 → 修复 → 解析）
chain = (
        main_prompt
        | llm
        | RunnableLambda(lambda x: {"model_output": x.content})  # 提取模型输出
        | RunnableLambda(parse_or_fix)  # 解析+自动修复
)

# 6. 运行测试
if __name__ == "__main__":
    try:
        result = chain.invoke({"flower": "百合", "price": "30"})
        print("\n🎉 自动修复解析器成功：")
        print(f"文案：{result.description}")
        print(f"理由：{result.reason}")
    except Exception as e:
        print(f"\n❌ 修复失败：{str(e)[:200]}")