import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.runnables.history import BaseChatMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_classic.memory import ConversationSummaryBufferMemory

# -------------------------- 1. 基础配置（必填）--------------------------
# 1. 读取 API Key（你的代理密钥，环境变量名：GPTSAPI_API_KEY）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

# 2. 代理配置（第三方代理地址）
base_url = "https://api.gptsapi.net/v1"

llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo"  # 可替换为 claude-3-sonnet-20240229、gemini-pro 等
)

# -------------------------- 多会话存储（通用工具）--------------------------
def get_session_history(session_id: str = "default") -> BaseChatMessageHistory:
    """多会话隔离存储（临时用字典，实际可替换为 Redis/MongoDB）"""
    if not hasattr(get_session_history, "session_store"):
        get_session_history.session_store = {}
    if session_id not in get_session_history.session_store:
        get_session_history.session_store[session_id] = InMemoryChatMessageHistory()
    return get_session_history.session_store[session_id]


# -------------------------- ConversationSummaryBufferMemory 实例 --------------------------
def run_summary_buffer_memory_demo(session_id: str = "summary_buffer_demo"):
    print("=" * 60)
    print("ConversationSummaryBufferMemory 实例（中长对话场景）")
    print("核心特性：超 Token 阈值后，早期对话摘要化，近期对话完整保留")
    print("=" * 60)

    # 1. 初始化 SummaryBuffer 记忆（关键参数配置）
    memory = ConversationSummaryBufferMemory(
        chat_memory=get_session_history(session_id),  # 绑定会话历史
        llm=llm,  # 用于生成摘要的 LLM
        max_token_limit=50,  # 核心阈值：缓冲区最大 Token 数（超阈值触发摘要）
        return_messages=True,  # 返回 ChatMessage 格式（易读+适配 Prompt）
        moving_summary_buffer="100",  # 可选：摘要缓冲区大小（控制摘要长度）
        human_prefix="用户",  # 可选：自定义用户角色前缀
        ai_prefix="助手"  # 可选：自定义助手角色前缀
    )

    # 2. 构建带记忆的 Prompt（注入历史对话/摘要）
    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        你是专业的电商客服助手，负责鲜花订单咨询，需：
        1. 记住用户的核心需求（花材、数量、包装、配送时间/地址）；
        2. 近期对话的细节（如刚确认的价格、优惠）需精准回应；
        3. 早期对话的关键信息（如预算、偏好）从摘要中提取，无需遗漏。
        """),
        MessagesPlaceholder(variable_name="chat_history"),  # 自动注入「近期对话原文+早期对话摘要」
        ("user", "{input}")
    ])

    # 3. 构建带记忆的链（基于 RunnableWithMessageHistory 新版架构）
    chain = RunnableWithMessageHistory(
        runnable=prompt | llm,
        get_session_history=lambda: get_session_history(session_id),
        input_messages_key="input",
        history_messages_key="chat_history"
    )

    # 4. 中长对话测试（模拟用户逐步确认订单，触发 Token 阈值后自动摘要）
    test_inputs = [
        "我想订鲜花送朋友，预算 800 元以内，要高端一点的花材",
        "花材选粉色郁金香+白色满天星，数量 16 束，包装要黑色哑光纸+银色丝带",
        "贺卡写 '祝黄总事业蒸蒸日上'，字体选商务黑体",
        "我在上海浦东新区，下周三下午 2-4 点送到，能保证新鲜度吗？",
        "对了，加一个小礼盒，里面放 2 块巧克力，额外费用多少？",
        "刚才说的花材单价是多少？16 束的总价包含礼盒和配送费吗？",
        "如果下周三上午 10 点前送到，需要加钱吗？",
        "最后确认一下：所有需求（花材、包装、贺卡、礼盒、配送时间）都对吗？总价多少？"
    ]

    # 执行多轮对话
    for idx, user_input in enumerate(test_inputs, 1):
        print(f"\n【对话 {idx}】")
        print(f"用户：{user_input}")
        # 调用链（传入会话 ID 隔离记忆）
        result = chain.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"助手：{result.content}")

    # 5. 查看最终记忆结构（关键！验证「摘要+近期原文」的混合存储）
    print("\n" + "=" * 60)
    print("最终记忆结构（早期摘要 + 近期原文）")
    print("=" * 60)
    memory_content = memory.load_memory_variables({})["history"]
    print(memory_content)

    # 区分摘要和原文（摘要存储在 AIMessage 中，原文是 HumanMessage/AIMessage 对）
    for msg in memory_content:
        if msg.type == "ai" and "摘要：" in msg.content:
            print(f"【早期对话摘要】：{msg.content}")
        else:
            role = "用户" if msg.type == "human" else "助手"
            print(f"【{role}】：{msg.content}")


# -------------------------- 执行演示 --------------------------
if __name__ == "__main__":
    run_summary_buffer_memory_demo()