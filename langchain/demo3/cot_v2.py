from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

llm = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="gpt-3.5-turbo",
    temperature=0.3  # 低温度保证推理逻辑稳定
)

# CoT 提示模板（明确分步推理要求+FewShot示例）
cot_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是花店AI助手，按以下步骤推理并回复：
    1. 先明确用户的核心需求（如预算、颜色、场合、花语偏好）；
    2. 分析需求对应的鲜花特性（颜色、花语、价格、适配场景）；
    3. 筛选符合条件的鲜花，给出2-3个推荐；
    4. 解释每个推荐的匹配逻辑（对应需求的哪一点）。

    示例：
    人类：预算50元，想送女朋友，喜欢粉色。
    AI：1. 核心需求：预算50元+粉色+爱情场景+送女朋友；
        2. 需求分析：粉色象征浪漫，爱情场景需花语贴合“爱”，价格≤50元；
        3. 推荐：粉色玫瑰（45元/束）、粉色芍药（50元/束）；
        4. 理由：粉色玫瑰花语“热烈的爱”，价格符合预算，适配爱情场景；粉色芍药花语“情有独钟”，花瓣饱满，适合送女朋友表达珍视。
    """),
    ("user", "{human_input}")
])

# 构建链并执行
chain = cot_prompt | llm
response = chain.invoke({
    "human_input": "预算30元，想送妈妈，喜欢紫色，希望花语是感恩。"
})

print(response.content)