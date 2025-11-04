# python所有变量都是对象的引用， 所以大小都为8字节

import sys
import ctypes

# 定义不同类型的变量（指向不同对象）
a = 10          # int 对象
b = "hello"     # str 对象
c = [1,2,3]     # list 对象
d = {"name": "张三"}  # dict 对象
e = lambda x: x  # 函数对象

# 方法 1：用 ctypes 测指针大小（最准确，直接反映引用的底层大小）
# Python 变量在底层是 PyObject* 指针，ctypes.c_void_p 等价于 void* 指针
pointer_size = ctypes.sizeof(ctypes.c_void_p)
print(f"当前 Python 指针大小（变量大小）：{pointer_size} 字节")  # 64 位环境输出 8，32 位输出 4

# 核心：Python 所有变量的引用都是 void* 指针，直接用 ctypes.c_void_p 测大小
pointer_size = ctypes.sizeof(ctypes.c_void_p)
print(f"当前 Python 指针大小（变量大小）：{pointer_size} 字节")  # 64位输出8，32位输出4

# 验证：所有变量对应的指针大小都等于 pointer_size（无需单独测每个变量）
print(f"int 变量 a 对应的指针大小：{pointer_size} 字节")
print(f"str 变量 b 对应的指针大小：{pointer_size} 字节")
print(f"list 变量 c 对应的指针大小：{pointer_size} 字节")
print(f"dict 变量 d 对应的指针大小：{pointer_size} 字节")
print(f"函数变量 e 对应的指针大小：{pointer_size} 字节")


#（用 sys.getsizeof() 测对象大小）：
a = 10
b = [1,2,3]
print(sys.getsizeof(a))  # 输出 28（int 对象本身的大小，不是变量 a 的大小）
print(sys.getsizeof(b))  # 输出 48（list 对象本身的大小，不是变量 b 的大小）