class FlowerShop:
    def __init__(self, shop_name, flower_type):
        self.shop_name = shop_name
        self.flower_type = flower_type

    # 静态方法：校验鲜花类型是否合法（不需要访问类/实例属性）
    @staticmethod
    def is_valid_flower(flower_type):
        valid_types = ["玫瑰", "百合", "康乃馨", "向日葵"]
        return flower_type in valid_types

    # 静态方法：格式化价格显示（独立工具函数）
    @staticmethod
    def format_price(price):
        return f"¥{price:.2f}"  # 格式化为：¥99.00

    def show_shop(self):
        # 实例方法中调用静态方法（需通过 类名.方法名()）
        if FlowerShop.is_valid_flower(self.flower_type):
            price_str = FlowerShop.format_price(100)
            print(f"店铺：{self.shop_name}，主营：{self.flower_type}，价格：{price_str}")
        else:
            print(f"店铺：{self.shop_name}，非法鲜花类型：{self.flower_type}")

# 1. 直接用类名调用静态方法（无需创建实例）
print(FlowerShop.is_valid_flower("玫瑰"))  # 输出：True
print(FlowerShop.format_price(150))        # 输出：¥150.00

# 2. 创建实例后调用
shop1 = FlowerShop("花漾空间", "玫瑰")
shop1.show_shop()  # 输出：店铺：花漾空间，主营：玫瑰，价格：¥100.00

shop2 = FlowerShop("错误店铺", "塑料花")
shop2.show_shop()  # 输出：店铺：错误店铺，非法鲜花类型：塑料花