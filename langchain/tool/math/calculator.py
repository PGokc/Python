from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 1. 初始化模型和工具
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",  # 推荐 gpt-3.5-turbo/gpt-4（支持工具调用）
    temperature=0.1,  # ReAct 需低温度，确保思考逻辑连贯
    timeout=30
)
calculator = CalculatorTool()  # 内置数学计算工具

# 2. 直接调用工具（测试）
result = calculator.invoke("(25 + 30) * 0.8 - 10")
print("数学计算结果：", result)  # 输出：34.0

# 3. 结合链使用（让 LLM 决定何时调用工具）
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor

# 提示词模板（告诉 LLM 可以调用计算器）
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是数学助手，遇到计算问题必须调用计算器工具，不要自己估算"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")  # 存储工具调用记录
])

# 创建智能体（绑定模型+工具+提示词）
agent = create_openai_tools_agent(llm, [calculator], prompt)
agent_executor = AgentExecutor(agent=agent, verbose=True)  # verbose 显示思考过程

# 运行测试
agent_executor.invoke({
    "input": "情人节买 2 束玫瑰，每束 50 元，店铺打 8 折，最终需要花多少钱？"
})