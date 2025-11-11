import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.exceptions import OutputParserException
from openai import OpenAIError

# 加载环境变量
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = 'https://api.gptsapi.net/v1'

# 1. 定义 Pydantic 模型（与示例 1 一致）
class FlowerAdCopy(BaseModel):
    description: str = Field(description="15-30字鲜花营销文案")
    reason: str = Field(description="15-30字文案理由")

# 2. 创建基础解析器
base_parser = PydanticOutputParser(pydantic_object=FlowerAdCopy)
format_instructions = base_parser.get_format_instructions()

# 3. 定义「原始任务 Prompt」和「修复 Prompt」
# 原始任务 Prompt
task_prompt = ChatPromptTemplate.from_messages([
    ("system", f"严格按格式输出：{format_instructions}，仅返回结构化结果，无额外内容"),
    ("user", "鲜花类型：{flower_type}，适用场合：{occasion}")
])

# 修复 Prompt（接收原始需求、错误信息，让模型修正）
fix_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你之前的输出不符合要求，解析错误如下：
    {error}
    请严格按照以下格式重新输出（仅返回结构化结果，不要添加任何解释）：
    {format_instructions}
    原始需求：鲜花类型={flower_type}，适用场合={occasion}
    """)
])

# 4. 初始化模型
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

# 5. 自动修复逻辑（核心）
def auto_fix_parser(flower_type: str, occasion: str) -> FlowerAdCopy:
    # 第一步：调用模型获取原始输出
    raw_prompt = task_prompt.format(flower_type=flower_type, occasion=occasion)
    messages = [("user", raw_prompt)]
    print(f"📝 TEST")
    raw_output = model.invoke(messages).content.strip()
    print(f"📝 模型原始输出：{raw_output}")

    try:
        # 尝试解析原始输出
        return base_parser.parse(raw_output)
    except OutputParserException as e:
        # 解析失败，生成修复 Prompt
        print(f"❌ 解析失败：{str(e)}，正在自动修复...")
        fix_messages = fix_prompt.format_messages(
            error=str(e),
            format_instructions=format_instructions,
            flower_type=flower_type,
            occasion=occasion
        )
        # 调用模型修复输出
        fixed_output = model.invoke(fix_messages).content.strip()
        print(f"📝 模型修复后输出：{fixed_output}")
        # 再次解析修复后的输出
        return base_parser.parse(fixed_output)

# 6. 执行自动修复流程
try:
    print(f"📝 TESTv2")
    result = auto_fix_parser(flower_type="野玫瑰", occasion="爱情")
    print("\n✅ 修复后结构化结果：")
    print(f"文案：{result.description}")
    print(f"理由：{result.reason}")
except OpenAIError as e:
    print(f"❌ API 调用失败：{str(e)}")
except Exception as e:
    print(f"❌ 自动修复失败：{str(e)}")