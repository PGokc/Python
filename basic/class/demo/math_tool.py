class MathTool:
    # 类属性：π（所有实例共享）
    PI = 3.1415926

    # 类方法：计算圆的周长（依赖类属性 PI，用 cls 访问）
    @classmethod
    def circle_perimeter(cls, radius):
        return 2 * cls.PI * radius

    # 静态方法：计算两个数的和（不依赖任何类/实例属性）
    @staticmethod
    def add(a, b):
        return a + b


# 调用类方法（无需创建实例，直接用类名调用）
print(MathTool.circle_perimeter(5))  # 输出：31.415926

# 调用静态方法（无需创建实例）
print(MathTool.add(3, 5))  # 输出：8

# 实例也能调用类方法/静态方法（但不推荐，逻辑上属于类）
tool = MathTool()
print(tool.circle_perimeter(3))  # 输出：18.8495556