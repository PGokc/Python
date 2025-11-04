# 一、基础输出：print() 函数（最常用）
# print() 是 Python 内置函数，用于将内容输出到控制台（终端），支持单个 / 多个参数、自动换行，语法简单灵活。

# ------------------------------------------- 1. 基本用法（直接输出文本 / 变量）-------------------------------------------
# 1. 输出文本（字符串）
print("Hello, Python!")  # 输出：Hello, Python!

# 2. 输出变量（支持任意数据类型：int、str、list、dict 等）
user_id = 1001
follow_count = 5000
print(user_id)  # 输出：1001
print(follow_count)  # 输出：5000
print("用户ID：", user_id, "关注数：", follow_count)  # 多变量输出，默认用空格分隔
# 输出：用户ID： 1001 关注数： 5000

# ------------------------------------------- 2. 关键参数（后端开发常用）-------------------------------------------
# print() 有 3 个实用参数，解决「分隔符、换行、输出目标」问题：
# sep：指定多个参数的分隔符（默认是空格）；
# end：指定输出结尾的字符（默认是 \n 换行符，可改为空字符串或其他字符）；
# file：指定输出目标（默认是控制台，可改为文件对象）。

# 1. 用逗号分隔多变量（替代默认空格）
print(user_id, follow_count, sep=",")  # 输出：1001,5000

# 2. 不自动换行（适合连续输出同一行内容，如进度条）
print("正在加载...", end="")
print("完成！")  # 输出：正在加载...完成！（同一行）

# 3. 输出到文件（替代单独的文件写入，适合临时日志）
# with open("debug.log", "w", encoding="utf-8") as f:
#     print("用户ID：", user_id, "操作时间：", "2025-11-05", file=f)
# 结果：debug.log 文件中写入「用户ID： 1001 操作时间： 2025-11-05」


# -------------------------------------------- 3. 输出特殊类型（list、dict、对象）--------------------------------------------
# print() 可直接输出复杂类型（如列表、字典），无需手动转换，适合快速调试：
# 输出列表
follow_shop_ids = [101, 102, 103]
print(follow_shop_ids)  # 输出：[101, 102, 103]

# 输出字典（后端接口参数/返回结果常用）
user_info = {"user_id": 1001, "name": "张三", "is_vip": True}
print(user_info)  # 输出：{'user_id': 1001, 'name': '张三', 'is_vip': True}

# 输出自定义对象（需定义 __str__ 方法，否则输出内存地址）
class User:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
    # 自定义输出格式（后端调试时清晰显示对象属性）
    def __str__(self):
        return f"User(user_id={self.user_id}, name={self.name})"

user = User(1001, "张三")
print(user)  # 输出：User(user_id=1001, name=张三)


# 二、格式化输出（后端核心技能，必掌握）
# 直接用 print() 拼接字符串（如 print("用户ID：" + str(user_id))）效率低、易出错，后端开发优先用「格式化输出」，推荐 3 种方式（按优先级排序）：
# -------------------------------------------- 1. f-string（Python 3.6+，首选）--------------------------------------------
# 语法：f"文本{变量/表达式}"，简洁高效、可读性强，支持直接嵌入变量和计算表达式，是后端格式化的首选。
# 示例（接口返回、日志打印、大模型 Prompt 构造常用）：
# 1. 嵌入变量
user_id = 1001
name = "张三"
print(f"用户ID：{user_id}，姓名：{name}")  # 输出：用户ID：1001，姓名：张三

# 2. 嵌入计算表达式
price = 5999
discount = 0.8
final_price = price * discount
print(f"原价：{price}元，折后：{final_price:.0f}元（折扣{discount*100:.0f}%）")
# 输出：原价：5999元，折后：4799元（折扣80%）

# 3. 格式化日期时间（后端日志常用）
from datetime import datetime
now = datetime.now()
print(f"操作时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")
# 输出：操作时间：2025-11-05 14:30:00

# 4. 格式化字典（接口参数打印）
user_info = {"user_id": 1001, "is_vip": True}
print(f"用户信息：{user_info['user_id']}，VIP状态：{user_info['is_vip']}")
# 输出：用户信息：1001，VIP状态：True

# -------------------------------------------- 2. str.format() 方法（兼容旧版本）--------------------------------------------
# 语法："文本{}".format(变量)，不依赖 Python 版本，适合需要兼容 Python 3.6 以下的场景（后端开发极少用，了解即可）。
print("用户ID：{}，姓名：{}".format(user_id, name))  # 输出：用户ID：1001，姓名：张三
print("折后价：{:.0f}元".format(final_price))  # 输出：折后价：4799元