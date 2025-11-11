import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from langchain_core.prompts import MessagesPlaceholder

# 1. 初始化模型
llm = ChatOpenAI(
    api_key=os.getenv("GPTSAPI_API_KEY"),
    base_url="https://api.gptsapi.net/v1",
    model="gpt-3.5-turbo",
    temperature=0.5  # 适度温度，鼓励路径探索
)


# 2. 定义辅助工具（用于子问题评估，如价格校验、花语匹配）
def check_price(flower_combination: str, budget: float) -> str:
    """评估花材组合的价格是否符合预算（模拟价格数据库）"""
    price_map = {
        "康乃馨+百合": 35,
        "洋桔梗+满天星": 28,
        "芍药+勿忘我": 45
    }
    price = price_map.get(flower_combination, 30)
    return f"花材组合{flower_combination}价格：{price}元，{'符合' if price <= budget else '不符合'}预算{budget}元"


def check_flower_language(flower: str, theme: str) -> str:
    """评估花材是否匹配主题花语（模拟花语数据库）"""
    flower_language = {
        "康乃馨": "感恩、尊敬",
        "百合": "纯洁、陪伴",
        "洋桔梗": "真诚、感恩",
        "芍药": "珍视、温柔",
        "勿忘我": "思念、永恒"
    }
    fl = flower_language.get(flower, "无明确花语")
    return f"花材{flower}花语：{fl}，{'匹配' if theme in fl else '不匹配'}主题{theme}"


# 3. 注册工具
tools = [
    Tool.from_function(
        name="PriceChecker",
        func=check_price,
        description="评估花材组合的价格是否符合预算，需传入flower_combination（花材组合，如康乃馨+百合）和budget（预算金额）"
    ),
    Tool(
        name="FlowerLanguageChecker",
        func=check_flower_language,
        description="评估花材是否匹配主题花语，需传入flower（花材名称）和theme（主题，如感恩、爱情）"
    )
]

# 4. ToT 提示模板（引导 Agent 拆解子问题、探索路径、评估回溯）
tot_prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是花店营销方案规划师，需用树状思维（ToT）生成母亲节营销方案，步骤如下：
    1. 拆解主问题为子问题：目标人群（年轻/中年/老年子女）→ 花材组合 → 价格套餐 → 文案主题；
    2. 每个子问题生成2-3个可能选项（路径）；
    3. 用提供的工具评估每个路径的可行性（价格是否符合目标人群预算、花语是否匹配母亲节主题）；
    4. 淘汰不可行路径（如价格超标、花语不匹配），保留2个最优路径；
    5. 整合最优路径，形成完整营销方案。

    评估标准：① 价格适配目标人群（年轻子女预算20-30元，中年30-50元，老年20-40元）；② 花语贴合母亲节“感恩、陪伴”主题；③ 组合新颖性。
    """),
    ("user", "{human_input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")  # 用于 Agent 记录推理过程（路径探索+评估结果）
])

# 5. 初始化 ToT  Agent
agent = create_openai_tools_agent(llm, tools, tot_prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors="返回评估结果并继续推理")

# 6. 执行 ToT 推理（生成母亲节营销方案）
response = agent_executor.invoke({
    "human_input": "生成母亲节鲜花营销方案，覆盖不同预算的子女，突出感恩主题。"
})

print("\n=== 最终营销方案 ===")
print(response["output"])