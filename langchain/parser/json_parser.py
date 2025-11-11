# JSON 解析器（通用结构化）
# 专门处理 JSON 格式输出，支持 JSON 语法校验，是最常用的通用解析器。

# 1. JsonOutputParser：解析为 JSON 字典，自动处理 JSON 语法错误（如缺少引号、逗号）
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()
# 格式指令：要求大模型输出 JSON 对象
format_inst = parser.get_format_instructions()

model_output = '{"description": "野玫瑰热烈纯粹", "reason": "情侣追求独特浪漫"}'
result = parser.parse(model_output)  # 输出：字典对象
print(result)
