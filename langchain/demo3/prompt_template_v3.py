# 1. PromptTemplate
from langchain_core.prompts import PromptTemplate

template = """\
你是业务咨询顾问。
你给一个销售{product}的电商公司，起一个好的名字？
"""
prompt = PromptTemplate.from_template(template)

print(prompt.format(product="鲜花"))

prompt = PromptTemplate(
    input_variables=["product", "market"],
    template="你是业务咨询顾问。对于一个面向{market}市场的，专注于销售{product}的公司，你会推荐哪个名字？"
)
print(prompt.format(product="鲜花", market="高端"))

# 2. ChatPromptTemplate
# -------------------------- 1. 核心导入（1.x 最新路径）--------------------------
# 提示词模板（1.x 统一从 langchain_core 导入）
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
# 聊天模型（1.x 从 langchain_openai 导入，替代旧的 langchain.chat_models）
from langchain_openai import ChatOpenAI
# 环境变量和系统模块
import os
from dotenv import load_dotenv  # 推荐用 dotenv 管理密钥（更安全）

# -------------------------- 2. 加载 API 密钥（最佳实践）--------------------------
# 检查环境变量是否配置
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    raise ValueError("❌ 请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

# 代理配置（确保代理支持 gpt-3.5-turbo 模型）
base_url = "https://api.gptsapi.net/v1"

# -------------------------- 3. 构建聊天提示模板（逻辑不变，路径已更新）--------------------------
# 系统消息模板（定义角色）
system_template = "你是一位专业顾问，负责为专注于{product}的公司起名。"
system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)

# 人类消息模板（提供具体信息）
human_template = "公司主打产品是{product_detail}。"
human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

# 组合聊天模板（按 [系统消息, 人类消息] 顺序）
prompt_template = ChatPromptTemplate.from_messages([
    system_message_prompt,
    human_message_prompt
])

# -------------------------- 4. 格式化提示词（1.x 用法不变，输出更规范）--------------------------
# 填充变量，生成可直接传给模型的消息列表
prompt = prompt_template.format_prompt(
    product="鲜花装饰",
    product_detail="创新的鲜花设计（含家居装饰、婚礼布置、商业空间花艺）"
).to_messages()

# 可选：打印格式化后的提示词（调试用）
print("📝 格式化后的提示词：")
for msg in prompt:
    print(f"[{msg.type.upper()}] {msg.content}")
print("-" * 50)

# -------------------------- 5. 初始化模型（1.x 统一用 invoke 方法调用）--------------------------
chat_model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo",  # 推荐用此模型（性价比高）
    temperature=0.8,  # 控制创意度（0-1，越高越有创意）
    timeout=15  # 超时保护
)

# -------------------------- 6. 调用模型（1.x 推荐用 invoke 替代直接调用）--------------------------
try:
    print("🚀 正在生成公司名称...")
    # 1.x 用 invoke 方法（更规范，支持链式调用）
    result = chat_model.invoke(prompt)

    # -------------------------- 7. 输出结果（优化格式）--------------------------
    print("\n🎉 生成结果：")
    print(f"公司名称推荐：\n{result.content}")

    # 可选：保存结果到文件
    with open("company_names.txt", "w", encoding="utf-8") as f:
        f.write(f"产品领域：鲜花装饰\n核心产品：创新的鲜花设计\n\n生成的公司名称：\n{result.content}")
    print("\n📁 结果已保存到 company_names.txt")

except Exception as e:
    print(f"\n❌ 调用失败：{str(e)[:150]}")  # 截取错误信息，避免输出过长
