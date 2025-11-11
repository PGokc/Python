import os
# 核心导入（LangChain 0.2.x+ 规范路径）
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI  # 最新版嵌入模型导入路径

# 1. 基础配置（代理 API Key + 代理地址，与之前的鲜花店代码保持一致）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

base_url = "https://api.gptsapi.net/v1"

# 2. 定义示例数据（samples，需提前准备，示例如下）
samples = [
    {"flower_type": "白玫瑰", "occasion": "表白", "suggestion": "白玫瑰象征纯洁，适合含蓄表白，搭配满天星更显温柔"},
    {"flower_type": "香槟玫瑰", "occasion": "纪念日", "suggestion": "香槟玫瑰自带高级感，寓意长久陪伴，适合周年纪念"},
    {"flower_type": "康乃馨", "occasion": "感恩", "suggestion": "康乃馨是感恩之花，花色淡雅，送给长辈表达敬意"},
    {"flower_type": "向日葵", "occasion": "鼓励", "suggestion": "向日葵象征阳光希望，适合送给朋友传递正能量"}
]

# 3. 定义示例提示模板（example_prompt）
prompt_sample = PromptTemplate(
    input_variables=["flower_type", "occasion", "suggestion"],
    template="鲜花类型: {flower_type}\n场合: {occasion}\n推荐语: {suggestion}\n"
)

# 4. 初始化语义相似性示例选择器（关键适配最新版）
example_selector = SemanticSimilarityExampleSelector.from_examples(
    examples=samples,  # 最新版参数名统一为 examples（旧版为 samples）
    embeddings=OpenAIEmbeddings(
        api_key=api_key,
        base_url=base_url  # 嵌入模型也需要配置代理（避免直接调用 OpenAI 官方接口）
    ),
    vectorstore_cls=Chroma,  # 最新版参数名统一为 vectorstore_cls（旧版为 Chroma）
    k=1,  # 选择最相似的 1 个示例
    # vectorstore_kwargs={
    #     "persist_directory": None,  # 不持久化向量库（临时使用，避免生成多余文件）
    #     "collection_name": "flower_examples"  # 向量库集合名（可选，增强可读性）
    # }
)

# 5. 创建 FewShotPromptTemplate（最新版参数兼容）
prompt = FewShotPromptTemplate(
    example_selector=example_selector,
    example_prompt=prompt_sample,
    suffix="鲜花类型: {flower_type}\n场合: {occasion}\n推荐语:",  # 补充结尾提示，让模型聚焦生成推荐语
    input_variables=["flower_type", "occasion"],
    example_separator="\n---\n"  # 示例之间的分隔符，优化模型读取体验
)

# 6. 测试：根据输入动态选择相似示例并生成提示词
formatted_prompt = prompt.format(flower_type="红玫瑰", occasion="爱情")
print("=== 生成的完整提示词 ===")
print(formatted_prompt)

# 7. 把提示传递给大模型
# 检查环境变量是否配置
import os
# 初始化聊天模型（适配 GPTSAPI 代理）
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

# 8. 规范调用模型（核心优化：聊天模型需传消息列表）
try:
    # 构造消息列表（system 指令 + user 提示，符合聊天模型要求）
    messages = [
        {
            "role": "system",
            "content": "你是专业的鲜花文案撰写员，严格按照用户提供的示例风格和要求生成文案，不添加额外内容。"
        },
        {
            "role": "user",
            "content": formatted_prompt  # 传入少样本 Prompt
        }
    ]

    # 新版 LangChain 推荐用 invoke() 调用（替代直接 chat_model(prompt)）
    response = chat_model.invoke(messages)

    # 提取核心结果（聊天模型返回的是结构化对象，content 字段是文案）
    result = response.content.strip()

    # 输出结果
    print("✅ 生成的营销文案：")
    print(result)

# 9. 捕获各类异常（提升稳定性）
except OpenAIError as e:
    raise RuntimeError(f"❌ API 调用失败（代理/密钥问题）：{str(e)}") from e
except TimeoutError:
    raise RuntimeError("❌ 调用超时，请检查网络或代理是否可用") from None
except Exception as e:
    raise RuntimeError(f"❌ 未知错误：{str(e)}") from e
