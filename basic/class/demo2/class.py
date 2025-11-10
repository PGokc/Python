# --------------------------------------------- 1. 简单类：属性 + 基础方法 ---------------------------------------------
# 定义类：Person（人）
class Person:
    # 初始化方法：创建实例时自动执行，给属性赋值
    def __init__(self, name, age):
        self.name = name  # 实例属性：姓名
        self.age = age    # 实例属性：年龄

    # 实例方法：类内的函数，必须带 self 参数（指代当前实例）
    def introduce(self):
        # 通过 self 访问实例属性
        print(f"大家好！我叫{self.name}，今年{self.age}岁～")

    def grow_up(self):
        # 修改实例属性
        self.age += 1
        print(f"{self.name}长大了1岁，现在{self.age}岁啦！")

# 1. 创建实例（对象）：类是“模板”，实例是“具体事物”
person1 = Person("小明", 25)
person2 = Person("小红", 30)

# 2. 访问实例属性
print(person1.name)  # 输出：小明
print(person2.age)   # 输出：30

# 3. 调用实例方法
person1.introduce()  # 输出：大家好！我叫小明，今年25岁～
person2.grow_up()    # 输出：小红长大了1岁，现在31岁啦！


# --------------------------------------------- 2. 类属性：所有实例共享的特征 ---------------------------------------------
# 定义类：Student（学生）
class Student:
    # 类属性：所有学生共享的学校名称（不用 self，直接写在类内）
    school = "阳光小学"

    def __init__(self, name, grade):
        self.name = name  # 实例属性：姓名（每个学生不同）
        self.grade = grade  # 实例属性：年级（每个学生不同）

    def show_info(self):
        # 同时访问类属性和实例属性
        print(f"学校：{Student.school}，姓名：{self.name}，年级：{self.grade}")

# 创建实例
stu1 = Student("小刚", 3)
stu2 = Student("小丽", 4)

# 访问类属性（所有实例共享）
print(stu1.school)  # 输出：阳光小学
print(stu2.school)  # 输出：阳光小学

# 调用方法
stu1.show_info()  # 输出：学校：阳光小学，姓名：小刚，年级：3
stu2.show_info()  # 输出：学校：阳光小学，姓名：小丽，年级：4

# 修改类属性（所有实例都会受影响）
Student.school = "星光小学"
stu1.show_info()  # 输出：学校：星光小学，姓名：小刚，年级：3


# --------------------------------------------- 3. 类方法与静态方法：不依赖实例的方法 ---------------------------------------------
class Calculator:
    # 类方法：用 @classmethod 装饰，参数是 cls（指代类本身）
    @classmethod
    def add(cls, a, b):
        print(f"类方法计算：{a}+{b}")
        return a + b

    # 静态方法：用 @staticmethod 装饰，无默认参数（和普通函数类似）
    @staticmethod
    def multiply(a, b):
        print(f"静态方法计算：{a}×{b}")
        return a * b

# 调用类方法（不用创建实例，直接用类名调用）
sum_result = Calculator.add(3, 5)
print(f"结果：{sum_result}")  # 输出：结果：8

# 调用静态方法（不用创建实例）
mul_result = Calculator.multiply(4, 6)
print(f"结果：{mul_result}")  # 输出：结果：24

# --------------------------------------------- 4. 模拟 ---------------------------------------------
# 模拟 LangChain 的 ChatModel 类（简化版）
class SimpleChatModel:
    def __init__(self, model_name, temperature=0.7):
        self.model_name = model_name  # 模型名称
        self.temperature = temperature  # 创意度

    def invoke(self, input_msg):
        # 模拟模型调用逻辑
        response = f"[{self.model_name}] 收到消息：{input_msg}，生成回复（温度：{self.temperature}）"
        return response

# 创建实例（类似 ChatOpenAI() 初始化）
model = SimpleChatModel(model_name="gpt-3.5-turbo", temperature=0.8)

# 调用方法（类似 model.invoke()）
result = model.invoke("给鲜花公司起名")
print(result)  # 输出：[gpt-3.5-turbo] 收到消息：给鲜花公司起名，生成回复（温度：0.8）


# --------------------------------------------- 5. 模拟 ---------------------------------------------
# 先定义工具函数（独立功能）
def calculate_price(flower_type, quantity):
    """计算鲜花总价：玫瑰50元/枝，百合30元/枝"""
    price_map = {"玫瑰": 50, "百合": 30}
    return price_map[flower_type] * quantity

# 再定义类（封装属性和方法）
class FlowerShop:
    def __init__(self, shop_name):
        self.shop_name = shop_name  # 店铺名称
        self.sales_record = []  # 销售记录（属性）

    def sell_flowers(self, customer_name, flower_type, quantity):
        """卖花（方法）：调用工具函数计算价格"""
        total_price = calculate_price(flower_type, quantity)  # 调用外部函数
        # 记录销售
        record = {
            "客户": customer_name,
            "花卉": flower_type,
            "数量": quantity,
            "总价": total_price
        }
        self.sales_record.append(record)
        print(f"✅ {self.shop_name} 售出 {quantity} 枝 {flower_type} 给 {customer_name}，总价：{total_price}元")

    def show_sales(self):
        """查看销售记录（方法）"""
        print(f"\n📊 {self.shop_name} 销售记录：")
        for idx, record in enumerate(self.sales_record, 1):
            print(f"{idx}. {record}")

# 实战使用
shop = FlowerShop("花漾空间")
shop.sell_flowers("小明", "玫瑰", 2)    # 输出：✅ 花漾空间 售出 2 枝 玫瑰 给 小明，总价：100元
shop.sell_flowers("小红", "百合", 3)    # 输出：✅ 花漾空间 售出 3 枝 百合 给 小红，总价：90元
shop.show_sales()  # 查看所有记录