from pydantic import BaseModel, Field

# 定义结构化输出模型（所有解析器共用）
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

import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

# 1. 初始化 Pydantic 输出解析器
output_parser = PydanticOutputParser(pydantic_object=FlowerCopywriting)
# 获取格式说明（会传给模型，告诉它该怎么输出）
format_instructions = output_parser.get_format_instructions()

# 2. 构建提示词模板（必须包含格式说明）
prompt = PromptTemplate(
    template="为 {price} 元的 {flower} 写文案，严格遵循以下格式要求：\n{format_instructions}",
    input_variables=["flower", "price"],
    partial_variables={"format_instructions": format_instructions}
)

# 3. 初始化大模型
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

# 4. 构建链（提示词 → 模型 → 解析器）
chain = prompt | llm | output_parser

# 5. 调用测试（正常场景）
try:
    result = chain.invoke({"flower": "玫瑰", "price": "50"})
    print("✅ 正常输出结果：")
    print(f"文案：{result.description}")
    print(f"理由：{result.reason}")
    print(f"结果类型：{type(result)}")  # <class '__main__.FlowerCopywriting'>（Pydantic 实例）
except Exception as e:
    print(f"❌ 解析失败：{e}")

# 模拟错误场景（故意让模型输出非 JSON 文本）
# 若模型输出："文案：以爱之名，赠你浪漫；理由：情人节专属，传递心意"
# 会抛出错误：Could not parse output as JSON: ...