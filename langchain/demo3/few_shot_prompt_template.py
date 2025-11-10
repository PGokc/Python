from langchain_openai import ChatOpenAI  # 导入聊天模型类（新版必需）
from openai import OpenAIError  # 捕获 API 相关异常

# 1. 创建一些示例
samples = [
  {
    "flower_type": "玫瑰",
    "occasion": "爱情",
    "ad_copy": "玫瑰，浪漫的象征，是你向心爱的人表达爱意的最佳选择。"
  },
  {
    "flower_type": "康乃馨",
    "occasion": "母亲节",
    "ad_copy": "康乃馨代表着母爱的纯洁与伟大，是母亲节赠送给母亲的完美礼物。"
  },
  {
    "flower_type": "百合",
    "occasion": "庆祝",
    "ad_copy": "百合象征着纯洁与高雅，是你庆祝特殊时刻的理想选择。"
  },
  {
    "flower_type": "向日葵",
    "occasion": "鼓励",
    "ad_copy": "向日葵象征着坚韧和乐观，是你鼓励亲朋好友的最好方式。"
  }
]

# 2. 创建一个提示模板
from langchain_core.prompts import PromptTemplate
template="鲜花类型: {flower_type}\n场合: {occasion}\n文案: {ad_copy}"
prompt_sample = PromptTemplate(
    input_variables=["flower_type", "occasion", "ad_copy"],
    template=template
)
print(prompt_sample.format(**samples[0]))

# 3. 创建一个FewShotPromptTemplate对象
from langchain_core.prompts import FewShotPromptTemplate
few_shot_prompt = FewShotPromptTemplate(
    examples=samples,  # 示例数据
    example_prompt=prompt_sample,  # 单个示例的格式
    # 关键优化：prefix 增加「任务指令」，告诉模型要做什么、模仿什么风格
    prefix="请模仿以下示例的风格（格式：突出鲜花象征意义+场合适配性），为指定鲜花和场合生成一句营销文案（15-30字，简洁有感染力）：",
    suffix="鲜花类型: {flower_type}\n场合: {occasion}",  # 待填充的输入
    input_variables=["flower_type", "occasion"],  # 动态传入的参数
    example_separator="\n\n"  # 多个示例之间的分隔符，避免拥挤
)
# 测试少样本 Prompt 格式（可选，验证 Prompt 是否符合预期）
test_prompt = few_shot_prompt.format(flower_type="野玫瑰", occasion="爱情")
print("📝 生成的完整 Prompt：")
print(test_prompt)
print("-" * 50)

# 4. 把提示传递给大模型
# 检查环境变量是否配置
import os
# 4. 初始化聊天模型（适配 GPTSAPI 代理）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("❌ 请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

try:
    chat_model = ChatOpenAI(
        api_key=api_key,
        base_url="https://api.gptsapi.net/v1",  # GPTSAPI 代理地址
        model="gpt-3.5-turbo",  # 聊天模型（适配代理）
        temperature=0.8,  # 创意度（0-1，越高越灵活）
        timeout=15,  # 超时保护
    )
except Exception as e:
    raise RuntimeError(f"❌ 模型初始化失败：{str(e)}") from e

# 5. 规范调用模型（核心优化：聊天模型需传消息列表）
try:
    # 构造消息列表（system 指令 + user 提示，符合聊天模型要求）
    messages = [
        {
            "role": "system",
            "content": "你是专业的鲜花文案撰写员，严格按照用户提供的示例风格和要求生成文案，不添加额外内容。"
        },
        {
            "role": "user",
            "content": test_prompt  # 传入少样本 Prompt
        }
    ]

    # 新版 LangChain 推荐用 invoke() 调用（替代直接 chat_model(prompt)）
    response = chat_model.invoke(messages)

    # 提取核心结果（聊天模型返回的是结构化对象，content 字段是文案）
    result = response.content.strip()

    # 输出结果
    print("✅ 生成的营销文案：")
    print(result)

# 6. 捕获各类异常（提升稳定性）
except OpenAIError as e:
    raise RuntimeError(f"❌ API 调用失败（代理/密钥问题）：{str(e)}") from e
except TimeoutError:
    raise RuntimeError("❌ 调用超时，请检查网络或代理是否可用") from None
except Exception as e:
    raise RuntimeError(f"❌ 未知错误：{str(e)}") from e