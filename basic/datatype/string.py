# ------------------------------------- 1. 字符串定义的4种常用方式 ----------------------------------
# 1. 单引号（适合包含双引号的文本）
s1 = 'He said "Python is easy"'
print(s1)

# 2. 双引号（适合包含单引号的文本）
s2 = "It's a good day"
print(s2)

# 3. 三引号（支持多行文本，后端常用於配置、文档注释）
s3 = """用户协议：
1. 本服务仅供个人使用；
2. 禁止商业转载。"""
print(s3)

# 4. 转义字符（处理特殊字符：\n换行、\t制表符、\\反斜杠等）
s4 = "第一行\n第二行\t缩进"  # \n换行，\t制表符
print(s4)
# 输出：
# 第一行
# 第二行    缩进

# 5. 原始字符串（前缀 r，忽略转义，适合文件路径、正则表达式）
s5 = r"C:\Users\Desktop\file.txt"  # 无需写 \\，直接写 \
print(s5)  # 输出：C:\Users\Desktop\file.txt

# ------------------------------------- 2. 索引与切片 ----------------------------------
# 接口返回的用户信息文本
response_text = '{"user_id":"1001","name":"张三","age":25}'
# 提取 user_id 的值（索引 11-15）
user_id = response_text[11:15]
print(user_id)  # 输出：1001

# ------------------------------------- 3. 字符串常用方法  ----------------------------------
# 1. + 拼接（简单场景）
shop_name = "华为旗舰店"
product = "Mate 60"
notice = "您关注的【" + shop_name + "】上新了「" + product + "」"

# 2. join() 拼接（批量数据，如列表转字符串）
user_ids = ["1001", "1002", "1003"]
id_str = ",".join(user_ids)  # 用逗号连接，结果："1001,1002,1003"（接口参数常用格式）

# 1. f-string（Python 3.6+，后端首选）
price = 5999.0
discount = 0.8
final_price = price * discount
info = f"商品：{product}，原价：{price:.0f}元，折后：{final_price:.0f}元"
print(info)  # 输出：商品：Mate 60，原价：5999元，折后：4799元

# 2. format() 方法（兼容场景）
info2 = "商品：{}，折后价：{}元".format(product, final_price)

# 场景：清洗接口返回的多余空格
raw_text = "  商品名称：  手机  ，价格：  3999  "
# 1. 替换所有空格
clean_text = raw_text.replace(" ", "")
print(clean_text)  # 输出：商品名称：手机，价格：3999

# 2. 查找"价格"的位置
price_index = clean_text.find("价格")
print(price_index)  # 输出：8（"价格"从索引8开始）

# 3. 统计"："出现次数
colon_count = clean_text.count("：")
print(colon_count)  # 输出：2

# 场景：用户输入参数校验
user_input = "  Python  "
# 去除两端空白 + 转小写
standard_input = user_input.strip().lower()
print(standard_input)  # 输出：python

# 场景：接口参数标准化（如品牌名称统一大写）
brand = "huawei"
brand_upper = brand.upper()
print(brand_upper)  # 输出：HUAWEI

# 1. split() 分割（解析逗号分隔的参数）
order_ids = "202501,202502,202503"
order_list = order_ids.split(",")
print(order_list)  # 输出：['202501', '202502', '202503']

# 2. 判断文件后缀（如筛选PDF文件）
file_name = "产品手册.pdf"
if file_name.endswith(".pdf"):
    print("是PDF文件")  # 输出：是PDF文件

# 3. 校验用户ID是否为纯数字
user_id = "1001"
if user_id.isdigit():
    print("用户ID格式正确")  # 输出：用户ID格式正确


# 场景：大模型长Prompt构造
long_prompt = """你是一个电商客服助手，需遵循以下规则：
1. 回复友好，使用中文；
2. 仅回答商品相关问题；
3. 未知问题请回复"请咨询人工客服"。

用户问题：{}"""

user_question = "这个手机支持5G吗？"
final_prompt = long_prompt.format(user_question)