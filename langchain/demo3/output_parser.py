import os
import pandas as pd
# 核心导入（LangChain v0.3+ 最新规范，替换废弃的 ResponseSchema）
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers.json import JsonOutputParser
from pydantic import BaseModel, Field  # 用于定义 JSON 输出结构（替代 ResponseSchema）

# -------------------------- 1. 环境配置与依赖检查 --------------------------
# 检查环境变量是否配置
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("❌ 请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

# 代理配置（确保代理支持 gpt-3.5-turbo 模型）
base_url = "https://api.gptsapi.net/v1"

# -------------------------- 2. 定义结构化输出格式（替代 ResponseSchema） --------------------------
# 用 Pydantic 模型严格约束输出结构（类型安全，自动校验）
class FlowerCopywriting(BaseModel):
    description: str = Field(
        description="鲜花的描述文案，15-30字，突出场景感和吸引力，语言优美",
        min_length=15,
        max_length=30
    )
    reason: str = Field(
        description="文案设计理由，结合鲜花价格和寓意，15-25字，逻辑清晰",
        min_length=15,
        max_length=25
    )


# -------------------------- 3. 创建输出解析器（最新规范） --------------------------
# 替代旧的 JsonOutputParser.from_response_schemas
output_parser = JsonOutputParser(pydantic_object=FlowerCopywriting)
print(output_parser)
# 获取自动生成的格式指令（无需手动写 JSON 格式要求）
format_instructions = output_parser.get_format_instructions()

# -------------------------- 4. 优化提示模板 --------------------------
prompt_template = """您是一位专业的鲜花店文案撰写员，擅长结合价格和花材寓意创作吸引人的短文案。
请为售价 {price} 元的 {flower_name} 完成以下要求：
1. 描述文案：15-30字，突出场景感（如送礼、装饰）和花材特点，语言简洁优美；
2. 设计理由：15-25字，说明文案如何结合价格定位和花的寓意。

{format_instructions}
⚠️  注意：仅输出 JSON 格式结果，不要添加任何多余文字（如解释、问候）！
"""

# 创建提示词模板（注入格式指令）
prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["price", "flower_name"],
    partial_variables={"format_instructions": format_instructions}
)
print(format_instructions)

# -------------------------- 5. 初始化聊天模型（兼容代理） --------------------------
model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",  # 代理支持的聊天模型
    temperature=0.7,  # 保留创意性
    timeout=15,  # 超时保护
    max_retries=2  # 失败自动重试（增强稳定性）
)

# -------------------------- 6. 数据准备（可扩展） --------------------------
# 扩展更多花材和价格（支持批量生成）
flowers_data = [
    ("玫瑰", "50"),  # 爱情主题
    ("百合", "30"),  # 纯洁主题
    ("康乃馨", "20"),  # 感恩主题
    ("向日葵", "45"),  # 阳光主题
    ("郁金香", "35")  # 优雅主题
]

# -------------------------- 7. 初始化结果存储 --------------------------
df = pd.DataFrame(columns=["flower", "price", "description", "reason"])

# -------------------------- 8. 批量生成（优化异常处理） --------------------------
print("🚀 开始批量生成鲜花文案...")
for flower, price in flowers_data:
    try:
        # 1. 填充提示词（含花名、价格、格式要求）
        filled_prompt = prompt.format(flower_name=flower, price=price)

        # 2. 调用模型（聊天模型需用 HumanMessage 包装）
        messages = [HumanMessage(content=filled_prompt)]
        response = model.invoke(messages)

        # 3. 解析输出（自动校验格式，不符合会抛出异常）
        parsed_output = output_parser.parse(response.content)

        # 4. 补充字段并添加到 DataFrame
        result_row = {
            "flower": flower,
            "price": price,
            "description": parsed_output["description"],
            "reason": parsed_output["reason"]
        }
        df.loc[len(df)] = result_row

        # 打印成功信息（带预览）
        print(f"\n✅ {flower}（{price}元）生成成功：")
        print(f"   文案：{parsed_output['description']}")
        print(f"   理由：{parsed_output['reason']}")

    except ValueError as ve:
        # 格式校验失败（如文案长度不符合）
        print(f"\n❌ {flower}（{price}元）生成失败：格式错误 - {str(ve)}")
    except Exception as e:
        # 其他异常（API 错误、网络问题等）
        print(f"\n❌ {flower}（{price}元）生成失败：{str(e)[:100]}")  # 截取错误信息

# -------------------------- 9. 结果输出与保存 --------------------------
print("\n" + "=" * 50)
print("📊 批量生成完成！")
print("=" * 50)

# 打印 DataFrame 结果
print("\n生成结果汇总：")
print(df.to_string(index=False))

# 保存到 CSV（支持中文编码，Windows/Mac 兼容）
output_file = "flowers_with_descriptions.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"\n📁 结果已保存到：{os.path.abspath(output_file)}")