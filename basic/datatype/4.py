# 所有变量存储的都是对象的引用

a = [1, 2, 3]
b = a  # b 复制的是 a 的“引用”，而非新列表
b.append(4)
print(a)  # 输出 [1,2,3,4]（a 和 b 指向同一个对象）

def modify_list(lst):
    lst.append(100)  # 直接修改引用指向的对象

my_list = [1, 2, 3]
modify_list(my_list)
print(my_list)  # 输出 [1,2,3,100]（函数内修改影响外部对象）

def reassign_list(lst):
    lst = [4, 5, 6]  # 重新赋值，lst 指向新对象，和外部无关

reassign_list(my_list)
print(my_list)  # 仍输出 [1,2,3,100]

a = 10
print(id(a))  # 输出类似 140703324567440（a 指向 10 的内存地址）
b = a
print(id(b))  # 输出和 id(a) 相同（b 和 a 指向同一个 10）
b = 20
print(id(b))  # 输出不同（b 改为指向 20 的内存地址）