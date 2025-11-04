# 基础类型

# 1. 整数/浮点数：运算与类型转换
user_id = 1001  # int
price = 99.9    # float
total = int(price * 2)  # 类型转换：float→int（舍弃小数），结果 199
print(f"订单总价：{total} 元")

# 2. 字符串：拼接、格式化（后端接口返回/日志打印常用）
shop_name = "华为旗舰店"
product_name = "Mate 60"
# f-string 格式化（最推荐，简洁高效）
notice = f"您关注的【{shop_name}】上新了「{product_name}」"
print(notice)  # 输出：您关注的【华为旗舰店】上新了「Mate 60」

# 3. 布尔值：判断条件（接口逻辑/数据过滤常用）
is_follow = True
if is_follow and user_id > 1000:
    print("发送上新通知")

# 4. None：参数默认值（接口函数常用）
def get_user_info(user_id=None):
    if user_id is None:
        return "请传入用户ID"
    return f"用户ID：{user_id}"

if __name__ == '__main__':
    get_user_info(None)
