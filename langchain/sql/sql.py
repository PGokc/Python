from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import Tool
from langchain_classic.agents import create_openai_tools_agent, AgentExecutor
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# --------------------------
# 1. 加载环境变量（OpenAI API 密钥）
# --------------------------
load_dotenv()  # 读取 .env 文件中的 OPENAI_API_KEY
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("请在 .env 文件中配置 OPENAI_API_KEY")

# --------------------------
# 2. 连接 SQLite 数据库（复用你的 FlowerShop.db）
# --------------------------
# 连接数据库（自动识别表结构，无需手动定义）
db = SQLDatabase.from_uri("sqlite:///FlowerShop.db")
print("📊 数据库连接成功！已识别的表：", db.get_usable_table_names())

# --------------------------
# 3. 构建 SQL 工具箱（包含查询、表结构描述等工具）
# --------------------------
# 初始化 LLM（兼容 ReAct 框架，需支持函数调用）
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",  # 推荐 gpt-3.5-turbo/gpt-4（支持工具调用）
    temperature=0.1,  # ReAct 需低温度，确保思考逻辑连贯
    timeout=30
)

# 创建 SQL 工具箱（包含：查询表列表、描述表结构、执行 SQL、校验 SQL 等工具）
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = sql_toolkit.get_tools()
print("🔧 加载的 SQL 工具：", [tool.name for tool in tools])

# --------------------------
# 4. 配置智能体提示词（优化 SQL 查询逻辑）
# --------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", """
    你是专业的 SQL 数据库查询助手，负责回答 FlowerShop 鲜花店的业务问题，规则如下：
    1. 先调用 `sql_db_list_tables` 确认可用表名，再调用 `sql_db_describe_table` 查看表结构（字段名、类型）；
    2. 根据表结构生成合法的 SQLite SQL 语句，避免语法错误（如字符串用单引号、字段名不含空格）；
    3. 生成 SQL 后，先调用 `sql_db_query_checker` 校验语法，再执行查询；
    4. 查询结果仅基于数据库数据，不编造信息；若结果为空，直接回复“未查询到相关数据”；
    5. 回答用自然语言整理，分点清晰，无需展示原始 SQL。
    """),
    MessagesPlaceholder(variable_name="agent_scratchpad"),  # 存储工具调用记录
    ("human", "{input}")
])

# --------------------------
# 5. 创建 SQL 智能体（核心：自动推理+调用工具）
# --------------------------
# 构建智能体（绑定 LLM + 工具 + 提示词）
agent = create_openai_tools_agent(llm, tools, prompt)
# 智能体执行器（verbose=True 显示思考过程，便于调试）
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    # verbose=True,
    handle_parsing_errors="查询失败，请尝试重新表述问题"
)

# --------------------------
# 6. 执行查询（复用你的原始问题）
# --------------------------
def run_sql_queries():
    # 原始问题列表
    queries = [
        "有多少种不同的鲜花？",
        "哪种鲜花的存货数量最少？",
        "平均销售价格是多少？",
        "从法国进口的鲜花有多少种？",
        "哪种鲜花的销售量最高？"
    ]

    # 批量执行查询
    for i, query in enumerate(queries, 1):
        print(f"\n==================================================")
        print(f"❓ 问题 {i}：{query}")
        print(f"--------------------------------------------------")
        # 执行智能体查询
        result = agent_executor.invoke({"input": query})
        print(f"✅ 回答：{result['output']}")

if __name__ == "__main__":
    run_sql_queries()