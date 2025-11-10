class FlowerShop:
    # 类属性：所有店铺共享的默认折扣（0.9 = 9折）
    default_discount = 0.9

    def __init__(self, shop_name, price):
        self.shop_name = shop_name  # 实例属性：店铺名
        self.price = price          # 实例属性：原价

    # 类方法：修改所有店铺的默认折扣（用 cls 操作类属性）
    @classmethod
    def set_default_discount(cls, new_discount):
        cls.default_discount = new_discount  # 通过 cls 修改类属性
        print(f"所有店铺默认折扣已改为：{new_discount}")

    # 类方法：创建“打折后”的实例（简化实例创建逻辑）
    @classmethod
    def create_discounted_shop(cls, shop_name, original_price):
        discounted_price = original_price * cls.default_discount  # 访问类属性
        return cls(shop_name, discounted_price)  # 通过 cls 创建实例（等价于 FlowerShop()）

    # 实例方法：查看当前店铺信息
    def show_info(self):
        print(f"店铺：{self.shop_name}，折后价：{self.price}元")

# 1. 用类方法修改类属性（所有实例共享）
FlowerShop.set_default_discount(0.8)  # 输出：所有店铺默认折扣已改为：0.8

# 2. 用类方法创建实例（无需手动计算折扣）
shop1 = FlowerShop.create_discounted_shop("花漾空间", 100)
shop2 = FlowerShop.create_discounted_shop("繁花艺境", 150)

# 3. 查看结果（所有实例都用了新的类属性折扣）
shop1.show_info()  # 输出：店铺：花漾空间，折后价：80.0元
shop2.show_info()  # 输出：店铺：繁花艺境，折后价：120.0元