# CoT + FewShot
import os
# 核心导入
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_openai import ChatOpenAI  # 最新版 ChatOpenAI 导入路径

# 1. 环境变量与 API 配置（优先从环境变量读取，更安全）
api_key = os.getenv("GPTSAPI_API_KEY")
if not api_key:
    # 若未设置环境变量，可直接赋值（不推荐硬编码，仅用于测试）
    # os.environ["GPTSAPI_API_KEY"] = "你的代理 API Key"
    raise ValueError("请先设置环境变量 GPTSAPI_API_KEY（存储代理 API Key）")

base_url = "https://api.gptsapi.net/v1"  # 代理地址（与之前鲜花店代码保持一致）

# 2. 创建最新版聊天模型
llm = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model="gpt-3.5-turbo", # 明确指定模型（推荐使用）
    temperature=0, # 保持零温度，确保推理逻辑稳定
    timeout=15 # 超时保护，避免网络堵塞
)

# 3. 设定 AI 角色和目标（System Prompt）
role_template = "你是一个为花店电商公司工作的AI助手，你的目标是帮助客户根据他们的喜好做出明智的决定"
system_prompt_role = SystemMessagePromptTemplate.from_template(role_template)

# 4. CoT(思维链) + FewShot提示模版
cot_template = """
作为一个为花店电商公司工作的AI助手，我的目标是帮助客户根据他们的喜好做出明智的决定。

我会按部就班地思考，先理解客户的需求，然后考虑各种鲜花的涵义、颜色适配性，最后根据需求给出推荐，并解释推荐原因。

示例 1:
  人类：我想找一种象征爱情的花。
  AI：首先，我理解你正在寻找一种可以象征爱情的花。在许多文化中，红玫瑰被视为爱情的象征，这是因为它们的红色通常与热情和浓烈的感情联系在一起。因此，考虑到这一点，我会推荐红玫瑰。红玫瑰不仅能够象征爱情，同时也可以传达出强烈的感情，这是你在寻找的。

示例 2:
  人类：我想要一些独特和奇特的花。
  AI：从你的需求中，我理解你想要的是独一无二和引人注目的花朵。兰花是一种非常独特并且颜色鲜艳的花，它们在世界上的许多地方都被视为奢侈品和美的象征。因此，我建议你考虑兰花。选择兰花可以满足你对独特和奇特的要求，而且，兰花的美丽和它们所代表的力量和奢侈也可能会吸引你。
"""
system_prompt_cot = SystemMessagePromptTemplate.from_template(cot_template)

# 5. 用户询问模版（Human Prompt）
human_template = "{human_input}"
human_prompt = HumanMessagePromptTemplate.from_template(human_template)

# 6. 组合链条提示
chat_prompt = ChatPromptTemplate.from_messages([
    system_prompt_role,
    system_prompt_cot,
    human_prompt,
])

# 7. 格式化提示词(生成模型可识别的 messages 结构)
# 最新版用 invoke() 替代 format_prompt()，更简洁
prompt_messages = chat_prompt.invoke({
    "human_input": "我想为我的女朋友购买一些花，她喜欢紫色。你有什么建议吗？"
}).to_messages()

# 8. 调用模型获取响应
response = llm.invoke(prompt_messages)

# 9. 输出结果(优化格式，仅打印 AI 回复内容)
print("=== AI 推荐回复 ===")
print(response.content)