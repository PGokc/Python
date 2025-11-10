# 定义一个接收关键字参数的函数
def create_flower(flower_name, price, description):
    return f"花名：{flower_name}，价格：{price}元，描述：{description}"

# 准备字典（键名必须与函数参数名一致）
flower_dict = {
    "flower_name": "玫瑰",
    "price": 50,
    "description": "热烈浪漫，情人节首选"
}

# 用 ** 解包字典传参（等价于：create_flower(flower_name="玫瑰", price=50, description="...")）
result = create_flower(** flower_dict)
print(result)
# 输出：花名：玫瑰，价格：50元，描述：热烈浪漫，情人节首选

# # 手动传入的 price=60 覆盖字典中的 price=50
# result = create_flower(** flower_dict, price=60)
# print(result)  # 输出：花名：玫瑰，价格：60元，描述：热烈浪漫，情人节首选


def create_order(flower_name, price, count, address):
    return f"订购 {count} 束 {flower_name}（{price}元/束），收货地址：{address}"

# 列表（位置参数）+ 字典（关键字参数）
flower_list = ["玫瑰", 50]  # 对应 flower_name、price（位置顺序必须匹配）
order_dict = {"count": 2, "address": "北京市朝阳区"}  # 对应 count、address（关键字参数）

# * 解包列表（位置参数） + ** 解包字典（关键字参数）
result = create_order(*flower_list, **order_dict)
print(result)
# 输出：订购 2 束 玫瑰（50元/束），收货地址：北京市朝阳区