import os
# 核心导入（最新版本规范）
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI  # 聊天模型用 ChatOpenAI（替代文本模型的 OpenAI）

# 1. 读取代理 API Key（优先从环境变量获取）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

# 2. 代理配置（第三方代理地址）
base_url = "https://api.gptsapi.net/v1"

# 3. 创建提示模板（修复变量传入逻辑，优化格式）
template = """您是一位专业的鲜花店文案撰写员。
对于售价为 {price} 元的 {flower_name} ，请提供一个吸引人的简短描述（15-30字，突出美感和场景感）。
"""
prompt = PromptTemplate(
    template=template,
    input_variables=["price", "flower_name"],
    template_format="f-string"
)

# 4. 初始化 gpt-3.5-turbo 聊天模型（最新版本参数规范）
model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",  # 改用聊天模型
    temperature=0.7,  # 文案推荐 0.6-0.8，保证创意性
    timeout=15
)

# 5. 生成填充后的提示词（修复：flower_name 不能传列表，转为字符串）
filled_prompt = prompt.format(
    flower_name="玫瑰",  # 单花名传字符串；多花名用 "玫瑰、香槟玫瑰"
    price="50"
)

# 6. 调用模型（聊天模型需包装为 messages 格式）
# 关键修改：用 ChatPromptTemplate 包装，或直接构造 messages 列表
from langchain_core.messages import HumanMessage

# 方式1：直接构造 messages（简单直观）
messages = [HumanMessage(content=filled_prompt)]
output = model.invoke(messages)

# 方式2：用 ChatPromptTemplate 包装（更规范，支持多轮对话扩展）
# from langchain_core.prompts import ChatPromptTemplate
# chat_prompt = ChatPromptTemplate.from_messages([("user", "{input}")])
# chain = chat_prompt | model
# output = chain.invoke({"input": filled_prompt})

# 7. 提取并打印结果（聊天模型从 content 属性获取输出）
print("文案生成结果：")
print(output.content.strip())

# 4. 定义多组花名和价格（可根据需要扩展）
flower_price_list = [
    {"flower_name": "玫瑰", "price": 50},
    {"flower_name": "香槟玫瑰", "price": 68},
    {"flower_name": "向日葵", "price": 45},
    {"flower_name": "满天星", "price": 25},
    {"flower_name": "勿忘我", "price": 32},
    {"flower_name": "郁金香", "price": 48}
]

# 5. for 循环批量生成文案
print("=== 鲜花文案批量生成结果 ===\n")
for i, item in enumerate(flower_price_list, 1):  # 枚举，添加序号
    flower_name = item["flower_name"]
    price = item["price"]

    # 填充提示词
    filled_prompt = prompt.format(flower_name=flower_name, price=price)

    # 构造 messages 并调用模型
    messages = [HumanMessage(content=filled_prompt)]
    output = model.invoke(messages)

    # 打印结果（带序号，清晰区分）
    print(f"{i}. {flower_name}（{price}元）：")
    print(f"   {output.content.strip()}\n")


# 6. 扩展：用 LangChain 链（Chain）批量生成（更高效）
# 如果需要处理大量数据（几十 / 上百组），用 LangChain 的 Runnable 链更高效（内部优化了调用逻辑），代码如下：
# 用 ChatPromptTemplate 直接定义（更简洁）
from langchain_core.prompts import ChatPromptTemplate
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "您是专业的鲜花店文案撰写员，描述简洁吸引人（15-30字）。"),
    ("user", "为售价 {price} 元的 {flower_name} 写一句文案。")
])
chain = chat_prompt | model  # 提示模板 → 模型，构成链
print("=== 鲜花文案批量生成结果（Chain 版） ===\n")
for i, item in enumerate(flower_price_list, 1):
    output = chain.invoke(item)
    print(f"{i}. {item['flower_name']}（{item['price']}元）：")
    print(f"   {output.content.strip()}\n")