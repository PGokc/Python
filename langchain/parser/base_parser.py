# 基础文本解析器（简单结构化）
# 适用于将输出拆分为列表、键值对等基础结构，无需复杂格式约束。

# 1. CommaSeparatedListOutputParser：解析为逗号分隔的列表
from langchain_core.output_parsers import CommaSeparatedListOutputParser

parser = CommaSeparatedListOutputParser()
# 生成格式指令（可直接嵌入 Prompt）
format_inst = parser.get_format_instructions()  # "输出用逗号分隔的列表，如：a,b,c"

# 解析模型输出
model_output = "野玫瑰，爱情，热烈，浪漫"
result = parser.parse(model_output)  # 输出：["野玫瑰", "爱情", "热烈", "浪漫"]
print(result)
