from abc import ABC, abstractmethod

# 接口1：支付接口
class PaymentInterface(ABC):
    @abstractmethod
    def pay(self, amount: float) -> str:
        pass

# 接口2：日志接口
class LogInterface(ABC):
    @abstractmethod
    def log(self, message: str) -> None:
        pass

# 子类同时实现两个接口
class WeChatPaymentWithLog(PaymentInterface, LogInterface):
    def pay(self, amount: float) -> str:
        result = f"微信支付成功！金额：{amount}元"
        self.log(result)  # 调用日志接口
        return result

    def log(self, message: str) -> None:
        print(f"【日志】{message}")

# 使用
wechat_log_pay = WeChatPaymentWithLog()
print(wechat_log_pay.pay(35.0))
# 输出：
# 【日志】微信支付成功！金额：35.0元
# 微信支付成功！金额：35.0元