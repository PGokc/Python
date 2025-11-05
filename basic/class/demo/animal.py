# -------------------------------------- 1. 单继承 --------------------------------------
# 父类：Animal（动物）
class Animal:
    def __init__(self, name):
        self.name = name  # 父类的实例属性

    # 父类的方法
    def eat(self):
        return f"{self.name}正在吃东西"


# 子类：Dog（狗）继承 Animal
class Dog(Animal):
    # 新增子类的实例属性（通过 super() 调用父类构造方法）
    def __init__(self, name, breed):
        # super() 指代父类，调用父类的 __init__ 初始化 name 属性
        super().__init__(name)
        self.breed = breed  # 子类新增属性：品种

    # 重写父类的 eat 方法（自定义狗的进食行为）
    def eat(self):
        return f"{self.name}（{self.breed}）正在吃骨头"

    # 新增子类的方法
    def bark(self):
        return f"{self.name}在汪汪叫"


# 创建子类实例
dog = Dog(name="旺财", breed="金毛")

# 调用子类重写的方法（覆盖父类）
print(dog.eat())  # 输出：旺财（金毛）正在吃骨头

# 调用子类新增的方法
print(dog.bark())  # 输出：旺财在汪汪叫

# 调用继承自父类的属性
print(dog.name)  # 输出：旺财

# -------------------------------------- 2. 多继承 --------------------------------------
class Flyable:
    def fly(self):
        return "会飞"

class Swimmable:
    def swim(self):
        return "会游泳"

# 子类 Duck 继承两个父类：Animal（之前定义的）、Flyable、Swimmable
class Duck(Animal, Flyable, Swimmable):
    def __init__(self, name):
        super().__init__(name)

duck = Duck(name="小黄鸭")
print(duck.eat())  # 继承 Animal 的方法：小黄鸭正在吃东西
print(duck.fly())  # 继承 Flyable 的方法：会飞
print(duck.swim()) # 继承 Swimmable 的方法：会游泳

# -------------------------------------- 3. 多态 --------------------------------------
# 父类：Animal（动物）
class Animal:
    def __init__(self, name):
        self.name = name  # 父类的实例属性

    # 父类的方法
    def eat(self):
        return f"{self.name}正在吃东西"

# 父类：Animal（已定义）
class Cat(Animal):  # 子类 Cat 继承 Animal
    def eat(self):  # 重写 eat 方法
        return f"{self.name}正在吃小鱼干"

class Bird(Animal): # 子类 Bird 继承 Animal
    def eat(self):  # 重写 eat 方法
        return f"{self.name}正在吃虫子"

# 定义一个通用函数（接收 Animal 类型的参数）
def feed_animal(animal: Animal):
    # 调用 eat 方法：不同子类实例，表现出不同行为
    print(animal.eat())

# 父类引用指向不同子类对象（多态的核心）
feed_animal(Dog(name="旺财", breed="金毛"))  # 输出：旺财（金毛）正在吃骨头
feed_animal(Cat(name="咪宝"))                # 输出：咪宝正在吃小鱼干
feed_animal(Bird(name="啾啾"))               # 输出：啾啾正在吃虫子