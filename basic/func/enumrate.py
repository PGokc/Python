# 1. 默认索引（从 0 开始）
fruits = ["apple", "banana", "orange"]
for idx, fruit in enumerate(fruits):
    print(f"索引 {idx}：{fruit}")

# 2. 指定索引起始值（从 1 开始）
for idx, fruit in enumerate(fruits, start=1):
    print(f"第 {idx} 个水果：{fruit}")

# 3. 转换为列表（查看完整迭代结果）
result = list(enumerate(fruits))
print(result)  # 输出：[(0, 'apple'), (1, 'banana'), (2, 'orange')]

result2 = list(enumerate(fruits, start=10))
print(result2)  # 输出：[(10, 'apple'), (11, 'banana'), (12, 'orange')]