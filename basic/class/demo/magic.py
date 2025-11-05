class Book:
    def __init__(self, title, pages):
        self.title = title
        self.pages = pages

    # 打印实例时，输出友好信息（替代默认的 <__main__.Book object at 0x...>）
    def __str__(self):
        return f"《{self.title}》（共{self.pages}页）"

    # 直接输入实例名时，输出可用于重建实例的字符串
    def __repr__(self):
        return f"Book(title='{self.title}', pages={self.pages})"

    # 调用 len(book) 时，返回页数
    def __len__(self):
        return self.pages

    # 把实例当作函数调用（如 book()）
    def __call__(self):
        return f"正在阅读《{self.title}》..."


book = Book(title="Python编程：从入门到实践", pages=450)

print(book)  # 触发 __str__：输出《Python编程：从入门到实践》（共450页）
print(repr(book))  # 触发 __repr__：输出 Book(title='Python编程：从入门到实践', pages=450)
print(len(book))  # 触发 __len__：输出 450
print(book())  # 触发 __call__：输出 正在阅读《Python编程：从入门到实践》...