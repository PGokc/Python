import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from openai import OpenAIError

# 加载环境变量
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")

# 1. 定义 Pydantic 模型（结构化约束）
class FlowerLanguage(BaseModel):
    core_meaning: str = Field(description="核心花语（≤30字）")
    detailed_meanings: list[str] = Field(description="1-3点详细花语（每点≤20字）")
    applicable_scene: str = Field(description="适用场景（≤20字）")

def get_flower_language_no_chain(flower_type: str) -> FlowerLanguage:
    """不使用 Chain：手动构造 Prompt → 调用模型 → 解析输出"""
    # 步骤1：手动构造 Prompt（含格式指令）
    prompt = f"""
    提供"{flower_type}"的花语，严格按以下 JSON 格式输出（无额外内容）：
    {{
        "core_meaning": "核心花语（≤30字）",
        "detailed_meanings": ["详细花语1", "详细花语2"],
        "applicable_scene": "适用场景"
    }}
    要求：JSON 语法正确，内容符合大众认知。
    """

    # 步骤2：手动初始化模型
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

    # 步骤3：手动调用模型（构造消息列表）
    try:
        messages = [{"role": "user", "content": prompt.strip()}]
        response = model.invoke(messages)
        raw_output = response.content.strip()
        print(f"📝 模型原始输出：{raw_output}")  # 手动加日志（中间步骤自定义）
    except OpenAIError as e:
        raise RuntimeError(f"API 调用失败：{str(e)}") from e

    # 步骤4：手动解析 JSON + Pydantic 校验
    try:
        json_data = json.loads(raw_output)
        result = FlowerLanguage(**json_data)
        return result
    except json.JSONDecodeError as e:
        raise RuntimeError(f"JSON 解析失败：{str(e)}") from e
    except ValidationError as e:
        raise RuntimeError(f"字段校验失败：{str(e)}") from e

# 测试
if __name__ == "__main__":
    flower_type = "铃兰"
    try:
        result = get_flower_language_no_chain(flower_type)
        print(f"\n🌹 {flower_type} 花语（无 Chain）：")
        print(f"核心：{result.core_meaning}")
        print(f"详细：{result.detailed_meanings}")
        print(f"场景：{result.applicable_scene}")
    except Exception as e:
        print(f"❌ 错误：{str(e)}")