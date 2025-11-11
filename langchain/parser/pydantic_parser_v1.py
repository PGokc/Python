import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from openai import OpenAIError

# 加载环境变量
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = 'https://api.gptsapi.net/v1'

# 1. 定义 Pydantic 模型（约束输出结构）
class FlowerAdCopy(BaseModel):
    """鲜花营销文案和理由的结构化输出"""
    description: str = Field(
        description="15-30字营销文案，突出鲜花象征意义和场合适配性，语言简洁有感染力"
    )
    reason: str = Field(
        description="15-30字理由，解释文案的合理性，贴合目标场景的用户心理"
    )

# 2. 创建 Pydantic 输出解析器
parser = PydanticOutputParser(pydantic_object=FlowerAdCopy)

# 3. 定义 Prompt 模板（必须包含格式指令）
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是专业的鲜花文案撰写员，严格按照以下格式要求输出：
    {format_instructions}
    内容需符合：
    1. description：15-30字，突出鲜花类型和适用场合；
    2. reason：15-30字，理性分析文案的吸引力逻辑；
    仅输出结构化结果，不要添加任何额外内容。
    """),
    ("user", "鲜花类型：{flower_type}，适用场合：{occasion}")
])

# 注入格式指令（解析器自动生成的 Pydantic 格式要求）
formatted_prompt = prompt.partial(format_instructions=parser.get_format_instructions())

# 4. 初始化 OpenAI 模型（适配 GPTSAPI 代理）
try:
    model = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model="gpt-3.5-turbo",
        temperature=0.7,
        timeout=15
    )
except Exception as e:
    raise RuntimeError(f"模型初始化失败：{str(e)}") from e

# 5. 链式调用（Prompt → 模型 → 解析器）
chain = formatted_prompt | model | parser

# 6. 执行并输出结果
try:
    result = chain.invoke({
        "flower_type": "野玫瑰",
        "occasion": "爱情"
    })
    print("✅ 结构化输出结果：")
    print(f"文案：{result.description}")
    print(f"理由：{result.reason}")
    print(f"\n原始 Pydantic 对象：{result}")
except OpenAIError as e:
    print(f"❌ API 调用失败：{str(e)}")
except Exception as e:
    print(f"❌ 解析失败（格式不符合 Pydantic 要求）：{str(e)}")