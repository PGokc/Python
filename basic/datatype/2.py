# 复合类型

# 1. 列表：批量数据处理（如关注的店铺ID列表）
follow_shop_ids = [101, 102, 103]
# 新增元素
follow_shop_ids.append(104)
# 遍历（接口返回数据组装常用）
for shop_id in follow_shop_ids:
    print(f"处理店铺ID：{shop_id}")

# 2. 字典：结构化数据（如用户信息、LLM调用参数）
# 场景：构造通义千问API调用参数
llm_config = {
    "model": "qwen-turbo",
    "temperature": 0.3,
    "max_tokens": 1024
}
# 取值（接口参数解析常用）
model_name = llm_config["model"]
print(f"使用模型：{model_name}")

# 3. 集合：数据去重（如过滤重复的用户ID）
user_ids = [1001, 1002, 1001, 1003]
unique_user_ids = set(user_ids)  # 去重：{1001, 1002, 1003}
# 交集运算（如两个店铺的共同关注用户）
shop1_followers = {1001, 1002, 1003}
shop2_followers = {1002, 1003, 1004}
common_followers = shop1_followers & shop2_followers  # 结果：{1002, 1003}

# 4. 元组：固定数据组合（如接口返回的键值对）
product_info = ("Mate 60", 5999, "黑色")  # 名称、价格、颜色
name, price, color = product_info  # 解包（便捷取值）
print(f"商品：{name}，价格：{price} 元")

if __name__ == '__main__':
    print("复合类型")
