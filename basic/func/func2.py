# 参数注解，返回值注解

# 1. 基础类型
def add(a: int, b: int) -> int:
    """两数相加，参数和返回值均为整数"""
    return a + b

def greet(name: str, is_formal: bool = False) -> str:
    """根据是否正式，返回问候语（默认参数也支持类型注解）"""
    if is_formal:
        return f"Hello, Mr. {name}!"
    return f"Hi, {name}!"

# 调用（类型注解不影响运行，传入错误类型也能执行，但不推荐）
print(add(3, 5))  # 输出：8
print(greet("Alice", is_formal=True))  # 输出：Hello, Mr. Alice!


# 2. 容器类型
# Python 3.9+ 写法（推荐）
def calculate_average(scores: list[int]) -> float:
    """计算整数列表的平均值，返回浮点数"""
    return sum(scores) / len(scores)

def get_user_info(user_id: int) -> dict[str, str | int]:
    """返回用户信息字典（key 为字符串，value 为字符串或整数）"""
    return {
        "user_id": user_id,
        "name": "Bob",
        "age": 25
    }

def get_coords() -> tuple[float, float]:
    """返回坐标元组（x, y），两个元素均为浮点数"""
    return (10.5, 20.3)

# 调用
print(calculate_average([90, 85, 95]))  # 输出：90.0
print(get_user_info(1001))  # 输出：{'user_id': 1001, 'name': 'Bob', 'age': 25}


# 3. 可选类型（Optional：允许参数为指定类型或 None）
# 用 Optional[类型] 表示参数可传指定类型或 None（Python 3.10+ 可简化为 类型 | None）：
# Python 3.10+ 写法（推荐）
def find_user(username: str | None) -> str:
    """查找用户，username 可为字符串或 None"""
    if username is None:
        return "匿名用户"
    return f"找到用户：{username}"

# Python 3.9 及以下写法（需导入 Optional）
from typing import Optional
def find_user_old(username: Optional[str]) -> str:
    if username is None:
        return "匿名用户"
    return f"找到用户：{username}"

# 调用
print(find_user("Charlie"))  # 输出：找到用户：Charlie
print(find_user(None))  # 输出：匿名用户


# 4. 无返回值（None）
# 函数无 return 或 return None 时，返回值类型注解为 None：
def print_log(message: str) -> None:
    """打印日志，无返回值"""
    print(f"[LOG] {message}")

# 调用
print_log("程序启动成功")  # 输出：[LOG] 程序启动成功


# 5. 多类型参数（Union：参数可接受多种类型）
# 用 Union[类型1, 类型2] 表示参数可接受多种类型（Python 3.10+ 简化为 类型1 | 类型2）：
# Python 3.10+ 写法
def format_number(num: int | float) -> str:
    """接受整数或浮点数，返回格式化字符串"""
    return f"数值：{num:.2f}"

# 调用
print(format_number(10))    # 输出：数值：10.00
print(format_number(3.1415))# 输出：数值：3.14


# 6. 自定义类作为类型
# 参数或返回值可以是自定义类的实例：
class Flower:
    def __init__(self, name: str, price: int):
        self.name: str = name  # 类的成员变量也支持类型注解
        self.price: int = price

def create_flower(name: str, price: int) -> Flower:
    """创建 Flower 实例并返回"""
    return Flower(name, price)

def get_flower_name(flower: Flower) -> str:
    """接收 Flower 实例，返回花名"""
    return flower.name

# 调用
rose = create_flower("玫瑰", 50)
print(get_flower_name(rose))  # 输出：玫瑰


# 7. 函数作为参数（Callable：回调函数类型）
# 用 Callable[[参数类型列表], 返回值类型] 表示函数类型参数：
from typing import Callable

def calculate(a: int, b: int, func: Callable[[int, int], int]) -> int:
    """接收两个整数和一个二元函数，返回计算结果"""
    return func(a, b)

# 定义回调函数（需符合 Callable 注解的类型）
def multiply(x: int, y: int) -> int:
    return x * y

# 调用
print(calculate(4, 5, multiply))  # 输出：20（4*5）


# 8. 泛型类型（List[T]：灵活适配多种类型）
# 用泛型（from typing import TypeVar, List）表示「任意类型的列表」，提升代码复用性：
from typing import TypeVar, List

# 定义泛型变量 T（代表任意类型）
T = TypeVar('T')

def reverse_list(items: List[T]) -> List[T]:
    """反转列表，保持元素类型不变（适用于任何类型的列表）"""
    return items[::-1]

# 调用（自动适配不同类型）
print(reverse_list([1, 2, 3]))          # 输出：[3, 2, 1]（int 列表）
print(reverse_list(["a", "b", "c"]))    # 输出：["c", "b", "a"]（str 列表）
print(reverse_list([True, False]))      # 输出：[False, True]（bool 列表）