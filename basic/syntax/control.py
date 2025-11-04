# --------------------------------------- 1.if ---------------------------------------
# 模拟接口请求参数
user_id = 1001
token = "valid_token_123"  # 有效token
# token = None  # 无效token（测试else分支）

# 条件判断：校验用户是否登录
if user_id is None:
    print("错误：用户ID不能为空")
elif token is None or token == "":
    print("错误：请先登录（token缺失）")
else:
    print(f"用户{user_id}登录成功，允许访问接口")

# 模拟订单状态（后端数据库查询结果）
order_status = 2  # 0-待支付，1-已支付，2-已发货，3-已完成
order_id = "OD20251105001"

if order_status == 0:
    print(f"订单{order_id}：待支付，请在24小时内完成付款")
elif order_status == 1:
    print(f"订单{order_id}：已支付，正在备货中")
elif order_status == 2:
    print(f"订单{order_id}：已发货，快递单号：SF123456789")
elif order_status == 3:
    print(f"订单{order_id}：已完成，感谢您的购买")
else:
    print(f"订单{order_id}：状态异常，请联系客服")

# --------------------------------------- 2.for ---------------------------------------
# 模拟关注某店铺的用户ID列表（后端从Redis/数据库查询）
follow_user_ids = ["user_1001", "user_1002", "user_1003", "user_1004"]
shop_name = "华为旗舰店"
product_name = "Mate 60 Pro"

# 遍历用户ID，批量生成推送通知
for user_id in follow_user_ids:
    notification = f"用户{user_id}：您关注的【{shop_name}】上新了「{product_name}」，点击查看详情～"
    print(notification)  # 实际场景：调用推送API发送通知

# 模拟接口返回的用户信息字典（后端常用）
user_info = {
    "user_id": "user_1001",
    "name": "张三",
    "age": 25,
    "is_vip": True,
    "follow_shops": ["shop_101", "shop_102"]
}

# 遍历字典的key-value对（items()方法）
print("用户信息详情：")
for key, value in user_info.items():
    print(f"{key}：{value}")

# 生成10个连续订单号（前缀OD+日期+序号）
date_str = "20251105"
for i in range(1, 11):  # 从1到10（结束值11不包含）
    order_id = f"OD{date_str}{i:03d}"  # 序号补03位（001-010）
    print(f"生成订单号：{order_id}")

# --------------------------------------- 3.while ---------------------------------------
import time

# 模拟调用大模型API的函数（失败概率高）
def call_llm_api(prompt):
    import random
    if random.random() < 0.7:  # 70%概率失败
        raise Exception("API调用超时")
    return f"成功生成回答：{prompt} 的相关内容"

# 重试逻辑：最多重试3次，每次失败间隔2秒
prompt = "写一篇Mate 60 Pro的测评"
retry_count = 0  # 重试次数
max_retry = 3    # 最大重试次数
success = False  # 是否成功

while retry_count < max_retry and not success:
    try:
        result = call_llm_api(prompt)
        print(result)
        success = True  # 成功后退出循环
    except Exception as e:
        retry_count += 1
        print(f"API调用失败（第{retry_count}次重试）：{e}，2秒后重试...")
        time.sleep(2)  # 等待2秒

if not success:
    print(f"重试{max_retry}次后仍失败，请稍后再试")

# 输出（可能的结果）：
# API调用失败（第1次重试）：API调用超时，2秒后重试...
# API调用失败（第2次重试）：API调用超时，2秒后重试...
# 成功生成回答：写一篇Mate 60 Pro的测评 的相关内容

# 模拟用户交互：直到输入"退出"才停止
print("欢迎使用店铺上新通知工具（输入'退出'结束）")
while True:  # 无限循环（条件永远为True）
    user_input = input("请输入您的操作（查询/推送/退出）：")
    if user_input == "退出":
        print("感谢使用，再见！")
        break  # 退出循环
    elif user_input == "查询":
        print("查询结果：您关注了3家店铺，近期2家有上新")
    elif user_input == "推送":
        print("推送成功：已向所有关注用户发送通知")
    else:
        print("无效操作，请重新输入")

# --------------------------------------- 4.continue/break ---------------------------------------
# 模拟包含无效数据的用户ID列表
user_ids = ["user_1001", "", "user_1002", None, "user_1003", "invalid_id"]

# 遍历并筛选有效用户ID（非空、非None、包含"user_"前缀）
valid_users = []
for uid in user_ids:
    if uid is None or uid == "":
        continue  # 跳过空值，进入下一次循环
    if not uid.startswith("user_"):
        print(f"跳过无效用户ID：{uid}")
        continue  # 跳过非用户前缀的ID
    valid_users.append(uid)
    if len(valid_users) >= 2:
        break  # 最多筛选2个有效ID，退出循环

print("有效用户ID：", valid_users)