import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# 1. 基础配置（同上）
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = "https://api.gptsapi.net/v1"

# 2. 用 ChatPromptTemplate 直接定义（更简洁）
chat_prompt = ChatPromptTemplate.from_messages([
    # System 消息：明确合规要求 + 角色定位 + 格式约束
    ("system", """
    你是合规的文案撰写助手，严格遵守 Azure OpenAI 内容管理政策。
    任务：为鲜花生成「文案 + 理由」，要求如下：
    1. description：15-30字，客观突出产品价格、适用场景（如情侣日常赠礼），语言自然，无夸张/情感化表述；
    2. reason：15-30字，理性分析文案适配的用户需求，不涉及敏感情感引导；
    3. 必须按以下格式输出（仅 JSON，无额外内容）
    """),
    # User 消息：保留原有的动态参数（price + flower_name）
    ("user", "为售价 {price} 元的 {flower_name} 生成内容，适用场景为情侣日常赠礼。")
])

# 3. 初始化模型 + 构建链
model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",
    temperature=0.7,
)
chain = chat_prompt | model  # 提示模板 → 模型，构成链

# 4. 批量数据（同上）
flower_price_list = [
    {"flower_name": "玫瑰", "price": 50},
    {"flower_name": "香槟玫瑰", "price": 68},
    # ... 其他花名和价格
]

# 5. for 循环调用链（更规范，支持扩展多轮对话）
print("=== 鲜花文案批量生成结果（Chain 版） ===\n")
for i, item in enumerate(flower_price_list, 1):
    output = chain.invoke(item)
    print(f"{i}. {item['flower_name']}（{item['price']}元）：")
    print(f"   {output.content.strip()}\n")