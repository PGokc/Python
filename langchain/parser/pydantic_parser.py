from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

# 1. 定义 Pydantic 模型（约束结构和字段）
class FlowerAd(BaseModel):
    description: str = Field(description="15-30字营销文案", min_length=15, max_length=30)
    reason: str = Field(description="15-30字理由", min_length=15, max_length=30)

# 2. 创建解析器
parser = PydanticOutputParser(pydantic_object=FlowerAd)

# 3. 生成格式指令（自动从 Pydantic 模型提取）
format_inst = parser.get_format_instructions()
print(format_inst)
# 输出：要求输出 JSON 对象，包含 description（15-30字）和 reason（15-30字）

# 4. 解析模型输出
model_output = '''{
    "description": "野玫瑰热烈纯粹，是爱情里独特的心意表达",
    "reason": "情侣追求专属浪漫，野玫瑰的野性契合爱情"
}'''
result = parser.parse(model_output)  # 输出：FlowerAd 实例对象
print(result.description)  # 访问字段：野玫瑰热烈纯粹，是爱情里独特的心意表达