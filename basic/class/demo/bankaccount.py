class BankAccount:
    def __init__(self, name, balance):
        self.name = name  # 公开属性（外部可访问）
        self.__balance = balance  # 私有属性（外部无法直接访问）

    # 公开方法：对外提供“查询余额”的接口
    def check_balance(self):
        return f"{self.name}的账户余额：{self.__balance}元"

    # 公开方法：对外提供“存款”的接口（带逻辑校验）
    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return f"存款成功！当前余额：{self.__balance}元"
        else:
            return "存款金额必须大于0！"


# 创建账户实例
account = BankAccount(name="张三", balance=1000)

# 正确：通过公开方法访问/修改数据
print(account.check_balance())  # 输出：张三的账户余额：1000元
print(account.deposit(500))  # 输出：存款成功！当前余额：1500元

# 错误：外部直接访问私有属性（会报错）
# print(account.__balance)  # AttributeError: 'BankAccount' object has no attribute '__balance'