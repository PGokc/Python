import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
# 修正导入路径：直接从 tool_calling 模块导入
from langchain.chains import create_tool_calling_chain
from langchain_core.output_parsers import StrOutputParser
from openai import OpenAIError

# 加载环境变量
load_dotenv()
api_key = os.getenv("GPTSAPI_API_KEY")
base_url = os.getenv("GPTSAPI_BASE_URL")

# ---------------------- 工具定义（和之前一致） ----------------------
@tool
def check_flower_order(order_id: str) -> str:
    """查询鲜花订单的基本状态（已支付/已发货/已完成），需传入订单号（YS+8位数字）。"""
    order_db = {"YS20240520": "已发货", "YS20240521": "已支付（待发货）", "YS20240522": "已完成"}
    status = order_db.get(order_id, "订单号不存在")
    return f"订单{order_id}状态：{status}"

@tool
def track_flower_logistics(order_id: str) -> str:
    """跟踪已发货订单的物流进度，需传入订单号。"""
    logistics_db = {"YS20240520": "上海→杭州，预计明日送达", "YS20240522": "已签收"}
    return logistics_db.get(order_id, "订单未发货或不存在")

@tool
def get_flower_care_guide(flower_type: str) -> str:
    """获取指定鲜花的养护建议，需传入鲜花类型（如玫瑰、洋桔梗）。"""
    care_guide_db = {"玫瑰": "每2-3天换水，斜剪花茎", "洋桔梗": "水位3-5cm，避免空调直吹"}
    return care_guide_db.get(flower_type, "暂无该鲜花养护建议")

tools = [check_flower_order, track_flower_logistics, get_flower_care_guide]

# ---------------------- 初始化 LLM ----------------------
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",
    temperature=0.5,
    model_kwargs={"max_tokens": 800}
)

# ---------------------- 构建工具调用 Chain ----------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是易速鲜花智能助手，需调用工具解答订单、物流、养护问题，参数不全时追问用户。"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])

tool_chain = create_tool_calling_chain(
    tools=tools,
    llm=llm,
    prompt=prompt,
    output_parser=StrOutputParser()
)

# ---------------------- 交互式测试 ----------------------
def flower_ai_assistant(user_input: str) -> str:
    try:
        result = tool_chain.invoke({"input": user_input})
        return result.strip()
    except OpenAIError as e:
        return f"API 错误：{str(e)}"
    except Exception as e:
        return f"系统错误：{str(e)}"

if __name__ == "__main__":
    print("🌸 易速鲜花智能助手（输入 q 退出）")
    while True:
        user_input = input("\n请输入问题：").strip()
        if user_input.lower() == "q":
            print("👋 再见！")
            break
        if not user_input:
            print("❌ 请输入有效问题！")
            continue
        print("💬 回复：", flower_ai_assistant(user_input))