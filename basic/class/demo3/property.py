class Flower:
    def __init__(self, name: str, price: float):
        self.name = name  # 普通属性
        self._price = price  # 私有变量（约定用 _ 表示，不建议外部直接访问）

    # 用 @property 装饰方法，伪装成属性
    @property
    def price(self):
        """获取价格（只读属性），返回保留 2 位小数的结果"""
        return round(self._price, 2)

    # 用 @属性名.setter 装饰，定义属性的赋值逻辑（可选）
    @price.setter
    def price(self, new_price: float):
        """设置价格时进行校验：必须是正数"""
        if new_price <= 0:
            raise ValueError("价格必须大于 0！")
        self._price = new_price

    # 用 @属性名.deleter 装饰，定义属性的删除逻辑（可选）
    @price.deleter
    def price(self):
        """删除价格时的逻辑（如禁止删除）"""
        raise PermissionError("价格属性不能删除！")

# 使用示例
rose = Flower("玫瑰", 50.123)
print(rose.price)  # 像访问属性一样调用，输出：50.12（触发 @property 装饰的方法）

rose.price = 60.456  # 像赋值属性一样操作，触发 @price.setter 装饰的方法
print(rose.price)  # 输出：60.46

rose.price = -10  # 触发校验，抛出 ValueError: 价格必须大于 0！

del rose.price  # 触发 @price.deleter，抛出 PermissionError: 价格属性不能删除！