# python动态性的直观体现

# 1. 无需声明变量类型，赋值即定义
a = 10          # a 是 int 类型
print(type(a))  # <class 'int'>

a = "hello"     # 同一变量可改为 str 类型
print(type(a))  # <class 'str'>

a = [1, 2, 3]   # 再改为 list 类型
print(type(a))  # <class 'list'>

# 2. 函数参数无类型限制，可接收任意类型
def add(x, y):
    return x + y

print(add(10, 20))        # 30（int+int）
print(add("hello", "world"))  # "helloworld"（str+str）
print(add([1,2], [3,4]))  # [1,2,3,4]（list+list）
