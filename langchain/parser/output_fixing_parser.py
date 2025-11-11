from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
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

# --------------------------
# 2. 初始化核心组件（不变）
# --------------------------
output_parser = PydanticOutputParser(pydantic_object=FlowerCopywriting)
format_instructions = output_parser.get_format_instructions()

import os
from langchain_openai import ChatOpenAI
# llm = ChatOllama(
#     model="llama3:8b",  # 或 qwen:7b（中文模型更推荐）
#     base_url="http://localhost:11434",
#     temperature=0.4,  # 降低温度，提升格式稳定性
#     max_tokens=200
# )
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

# --------------------------
# 3. 修正提示词模板
# --------------------------
prompt = PromptTemplate(
    template="""
     任务：为 {price} 元的 {flower} 创作 1 组文案和理由，严格按以下要求执行：

    输出要求（必须严格遵守，否则无效）：
    1. 仅返回 JSON 格式数据，不添加任何额外文字、注释、换行；
    2. JSON 必须包含 2 个字段，字段名不可修改：
       - description：15-30 字的鲜花文案，突出场景感和吸引力；
       - reason：15-25 字的设计理由，结合价格和寓意；
    3. 字段值必须符合长度要求，否则重新生成。

    错误提示：{error}
    """,
    input_variables=["flower", "price", "error"],
    partial_variables={"format_instructions": format_instructions}
)

# --------------------------
# 4. 构建链（不变）
# --------------------------
chain = (
        RunnablePassthrough.assign(error=lambda x: x.get("error", ""))
        | prompt
        | llm
        | output_parser
).with_retry(
    retry_if_exception_type=(OutputParserException,),
    wait_exponential_jitter=False,
    stop_after_attempt=2,
)

# --------------------------
# 5. 运行测试（不变）
# --------------------------
if __name__ == "__main__":
    try:
        print("🚀 开始生成鲜花文案...")
        # 调用时只传 input_variables 中定义的 3 个变量（正确）
        result = chain.invoke({
            "flower": "玫瑰",
            "price": "50",
            "error": ""
        })

        print("\n🎉 生成成功！")
        print(f"文案：{result.description}")
        print(f"理由：{result.reason}")
        print(f"结果类型：{type(result)}")

    except Exception as e:
        print(f"\n❌ 生成失败：{str(e)[:300]}")