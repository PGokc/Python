class Car:
    # 类属性：所有汽车共享的属性（比如品牌统一为“新能源”）
    brand_type = "新能源"

    # 构造方法：创建汽车实例时，初始化“颜色”和“价格”（每个车不同）
    def __init__(self, color, price):
        # 实例属性：每个实例独有的数据
        self.color = color  # 颜色（如红色、蓝色）
        self.price = price  # 价格（如20万、30万）

    # 实例方法：汽车的行为（比如“行驶”）
    def drive(self):
        # 通过 self 访问实例属性和类属性
        return f"一辆{self.color}的{Car.brand_type}汽车（价格{self.price}万）正在行驶"

# 创建两个实例（对象）
car1 = Car(color="红色", price=25)  # 实例1：红色，25万
car2 = Car(color="蓝色", price=35)  # 实例2：蓝色，35万

# 访问类属性（所有实例共享）
print(Car.brand_type)  # 输出：新能源
print(car1.brand_type) # 输出：新能源（实例也能访问类属性）

# 访问实例属性（每个实例独立）
print(car1.color)      # 输出：红色
print(car2.color)      # 输出：蓝色

# 调用实例方法
print(car1.drive())    # 输出：一辆红色的新能源汽车（价格25万）正在行驶
print(car2.drive())    # 输出：一辆蓝色的新能源汽车（价格35万）