# ---------------------- 定义接口（普通类）----------------------
class DeliveryInterface:
    """配送接口：文档化规范，无强制约束"""
    def deliver(self, address: str) -> str:
        """配送方法：子类需实现"""
        raise NotImplementedError("子类必须实现 deliver 方法")

    def cancel_delivery(self, delivery_id: str) -> str:
        """取消配送：子类需实现"""
        raise NotImplementedError("子类必须实现 cancel_delivery 方法")

# ---------------------- 实现接口（子类）----------------------
class ExpressDelivery(DeliveryInterface):
    """快递配送：实现配送接口"""
    def deliver(self, address: str) -> str:
        return f"快递配送已出发！收货地址：{address}"

    def cancel_delivery(self, delivery_id: str) -> str:
        return f"已取消配送！配送ID：{delivery_id}"

# ---------------------- 使用接口 ----------------------
if __name__ == "__main__":
    express = ExpressDelivery()
    print(express.deliver("北京市朝阳区XX街道"))  # 输出：快递配送已出发！收货地址：北京市朝阳区XX街道

    # 警告：未实现接口方法的子类可实例化，但调用时报错
    class SelfDelivery(DeliveryInterface):
        pass  # 未实现接口方法

    self_delivery = SelfDelivery()
    # print(self_delivery.deliver("上海市黄浦区"))  # 报错：NotImplementedError: 子类必须实现 deliver 方法