from abc import ABC, abstractmethod

# ---------------------- 定义接口（抽象基类）----------------------
class PaymentInterface(ABC):
    """支付接口：定义支付和退款的规范"""

    @abstractmethod
    def pay(self, amount: float) -> str:
        """支付方法（必须实现）
        :param amount: 支付金额
        :return: 支付结果（成功/失败信息）
        """
        pass  # 抽象方法仅定义接口，不实现逻辑

    @abstractmethod
    def refund(self, order_id: str) -> str:
        """退款方法（必须实现）
        :param order_id: 订单ID
        :return: 退款结果
        """
        pass


# ---------------------- 实现接口（子类）----------------------
class WeChatPayment(PaymentInterface):
    """微信支付：实现支付接口"""

    def pay(self, amount: float) -> str:
        # 具体实现微信支付逻辑（如调用微信支付API）
        return f"微信支付成功！金额：{amount}元"

    def refund(self, order_id: str) -> str:
        # 具体实现微信退款逻辑
        return f"微信退款成功！订单ID：{order_id}"


class AlipayPayment(PaymentInterface):
    """支付宝支付：实现支付接口"""

    def pay(self, amount: float) -> str:
        return f"支付宝支付成功！金额：{amount}元"

    def refund(self, order_id: str) -> str:
        return f"支付宝退款成功！订单ID：{order_id}"


# ---------------------- 使用接口 ----------------------
if __name__ == "__main__":
    # 微信支付实例
    wechat_pay = WeChatPayment()
    print(wechat_pay.pay(59.9))  # 输出：微信支付成功！金额：59.9元
    print(wechat_pay.refund("ORDER_123456"))  # 输出：微信退款成功！订单ID：ORDER_123456

    # 支付宝支付实例
    alipay = AlipayPayment()
    print(alipay.pay(35.0))  # 输出：支付宝支付成功！金额：35.0元


    # 错误示例：未实现接口的子类无法实例化
    class InvalidPayment(PaymentInterface):
        pass  # 未实现 pay 和 refund 方法

    # invalid_pay = InvalidPayment()  # 报错：TypeError: Can't instantiate abstract class InvalidPayment with abstract methods pay, refund