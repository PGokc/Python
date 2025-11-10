class Test:
    class_attr = "我是类属性"

    def __init__(self):
        self.instance_attr = "我是实例属性"

    # 类方法：能访问类属性，不能直接访问实例属性
    @classmethod
    def class_method(cls):
        print(f"类方法访问类属性：{cls.class_attr}")
        # print(cls.instance_attr)  # 报错：类没有实例属性

    # 静态方法：不能访问类属性/实例属性
    @staticmethod
    def static_method():
        print("静态方法：我不能访问任何类/实例属性")
        # print(Test.class_attr)  # 不报错，但不推荐（硬编码类名，不灵活）

    # 实例方法：能访问类属性和实例属性
    def instance_method(self):
        print(f"实例方法访问类属性：{self.class_attr}")
        print(f"实例方法访问实例属性：{self.instance_attr}")

# 调用测试
Test.class_method()    # 正常运行（类名调用）
Test.static_method()   # 正常运行（类名调用）
# Test.instance_method()  # 报错：实例方法必须通过实例调用

obj = Test()
obj.class_method()     # 正常运行（实例也能调用类方法，但不推荐）
obj.static_method()    # 正常运行（实例也能调用静态方法，但不推荐）
obj.instance_method()  # 正常运行（实例调用实例方法）