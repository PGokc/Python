from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


# ---------------------- 数据接口（Pydantic模型：强制数据结构）----------------------
class OrderData(BaseModel):
    """订单数据接口：定义订单的必填字段和格式"""
    order_id: str = Field(description="订单ID，必填")
    flower_name: str = Field(description="花束名称，必填")
    amount: float = Field(ge=0, description="订单金额，≥0元")
    address: str = Field(description="收货地址，必填")


# ---------------------- 方法接口（ABC抽象类：强制方法实现）----------------------
class OrderInterface(ABC):
    """订单接口：定义订单处理的方法规范"""

    @abstractmethod
    def create_order(self, order_data: OrderData) -> str:
        """创建订单"""
        pass

    @abstractmethod
    def cancel_order(self, order_id: str) -> str:
        """取消订单"""
        pass


# ---------------------- 实现接口（子类）----------------------
class FlowerShopOrder(OrderInterface):
    """花店订单服务：实现订单接口"""

    def create_order(self, order_data: OrderData) -> str:
        # Pydantic 自动校验 order_data 的结构和字段合法性
        return f"订单创建成功！订单信息：{order_data.model_dump()}"

    def cancel_order(self, order_id: str) -> str:
        return f"订单取消成功！订单ID：{order_id}"


# ---------------------- 使用接口 ----------------------
if __name__ == "__main__":
    # 构造符合数据接口的订单数据
    valid_order = OrderData(
        order_id="ORDER_789",
        flower_name="浪漫粉芍",
        amount=59.9,
        address="广州市天河区XX路"
    )

    # 调用订单服务
    order_service = FlowerShopOrder()
    print(order_service.create_order(valid_order))
    # 输出：订单创建成功！订单信息：{'order_id': 'ORDER_789', 'flower_name': '浪漫粉芍', 'amount': 59.9, 'address': '广州市天河区XX路'}

    # 错误示例：数据不符合接口规范（自动校验报错）
    invalid_order = OrderData(
        order_id="ORDER_000",
        flower_name="",  # 字段为空（无默认值，必填）
        amount=10,  # 金额为负（违反 ge=0 约束）
        address="深圳市南山区"
    )
    print(order_service.create_order(invalid_order))  # 报错：ValidationError: 2 validation errors for OrderData