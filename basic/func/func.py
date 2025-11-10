# 1. 无参数无返回值
def say_hello():
    print("hello world!")

say_hello()

# 2. 有参数无返回值
def greet_by_name(name: str):
    print(f"你好，{name}")

greet_by_name("PGokc")

# 3. 有参数有返回值
def add(a, b):
    result = a + b
    return result

sum1 = add(1, 13)
print(sum1)

# 4. 带默认参数：参数可传可不传
def calculate_discount(price, discount=0.9):
    return price * discount

price1 = calculate_discount(100)
print(price1)
price2 = calculate_discount(100, 0.8)
print(price2)

# 5. 关键字参数：明确参数含义（避免参数混乱）
def print_info(name, age, city):
    print(f"姓名:{name}, 年龄:{age}, 城市:{city}")

print_info("PG", 33, "LA")
print_info(name="PG", age=33, city="OKC")