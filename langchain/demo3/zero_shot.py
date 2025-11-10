from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os

# 1. 初始化模型
model = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="gpt-3.5-turbo"
)

# 2. 零样本提示模板（仅描述任务，无示例）
zero_shot_prompt = PromptTemplate(
    template="任务：为售价{price}元的{flower}写一句电商文案（15-20字），突出花的寓意和性价比。",
    input_variables=["flower", "price"]
)

# 3. 执行零样本生成
chain = zero_shot_prompt | model
result = chain.invoke({"flower": "勿忘我", "price": 32})
print("ZeroShot 文案：", result.content)
# 输出示例：32元勿忘我象征永恒思念，性价比高，送礼自留皆可～


from langchain_core.prompts import ChatPromptTemplate

# 零样本分类提示（明确分类选项）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是订单咨询意图分类器，将用户输入分为3类：订单查询、售后投诉、价格咨询。仅输出分类结果，不要多余文字。"),
    # ("user", "我的花什么时候发货？")
    ("user", "红玫瑰多少钱一束？")
])

chain = prompt | model
result = chain.invoke({})
print("ZeroShot 分类结果：", result.content)  # 输出：订单查询