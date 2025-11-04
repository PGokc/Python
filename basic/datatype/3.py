# 高级类型

# 1. 字节串：读取文件（如大模型应用中读取PDF/图片）
with open("product.png", "rb") as f:  # "rb" 表示二进制读取
    img_data = f.read()  # img_data 是 bytes 类型
print(f"图片大小：{len(img_data)} 字节")

# 2. datetime：日期时间处理（接口日志/订单时间常用）
from datetime import datetime, timedelta

# 获取当前时间
now = datetime.now()
print(f"当前时间：{now.strftime('%Y-%m-%d %H:%M:%S')}")  # 格式化输出

# 计算3天后的时间（如优惠券过期时间）
expire_time = now + timedelta(days=3)
print(f"优惠券过期时间：{expire_time.strftime('%Y-%m-%d')}")

