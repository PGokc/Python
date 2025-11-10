# 1. 并行遍历两个列表（长度一致）

names = ["Alice", "Bob", "Charlie"]
ages = [25, 30, 35]

# 并行遍历，打包 (name, age)
for name, age in zip(names, ages):
    print(f"{name} 的年龄是 {age}")

# 2. 转换为列表（查看打包结果）
result = list(zip(names, ages))
print(result)  # 输出：[('Alice', 25), ('Bob', 30), ('Charlie', 35)]

# 3. 多个可迭代对象（长度不一致）
# 默认 strict=False 时，zip 会以「最短的可迭代对象」为准，超出部分被忽略：
names = ["Alice", "Bob", "Charlie"]  # 长度 3
ages = [25, 30]  # 长度 2
cities = ["Beijing", "Shanghai"]  # 长度 2

result = list(zip(names, ages, cities))
print(result)  # 输出：[('Alice', 25, 'Beijing'), ('Bob', 30, 'Shanghai')]（Charlie 被忽略）

# 4. strict=True（强制长度一致）
try:
    result = list(zip(names, ages, strict=True))
except ValueError as e:
    print(e)  # 输出：zip() arguments have different lengths: 3, 2

# 5. 解压 zip 结果（用 * 运算符）
packed = zip(names, ages)
unpacked_names, unpacked_ages = zip(*packed)
print(unpacked_names)  # 输出：('Alice', 'Bob', 'Charlie')
print(unpacked_ages)   # 输出：(25, 30, 35)
