import json
from typing import Any, Optional, TypeVar

import aio_pika
import strawberry
from grpc_clients import (
    grpc_cart,
    grpc_order,
    grpc_payment,
    grpc_product,
)
from strawberry.types import Info
from strawberry.types.nodes import SelectedField

# build_dynamic_objectで使うためのTypeVarを定義
T = TypeVar("T")


# ========================================================
# RabbitMQ
# ========================================================
async def publish_order_event(id: str, item_id: str) -> str:
    connection = await aio_pika.connect_robust("amqp://user:pass@rabbitmq/")
    channel = await connection.channel()

    message = aio_pika.Message(
        body=json.dumps(
            {
                "id": id,
                "item_id": item_id,
            }
        ).encode()
    )

    await channel.default_exchange.publish(message, routing_key="order.created")
    await connection.close()

    return f"Order event published for {id}"


# ========================================================
# 共通関数
# ========================================================
def build_dynamic_object(cls: type[T], source_obj: Any, fields: list[str]) -> T:
    """
    任意の Strawberry 型 `cls` に対して、
    指定された fields のみを初期化してインスタンスを返す
    """
    init_args = {
        field: getattr(source_obj, field, None) for field in cls.__annotations__.keys()
    }

    for key in init_args:
        if key not in fields:
            init_args[key] = None

    return cls(**init_args)


# ========================================================
# GraphQL
# ========================================================
@strawberry.type
class Product:
    id: Optional[str]
    name: Optional[str]
    price: Optional[float]
    description: Optional[str]


@strawberry.type
class Cart:
    id: Optional[str]
    product_id: Optional[str]
    quantity: Optional[int]


@strawberry.type
class Query:
    @strawberry.field
    def product(self, info: Info, id: str) -> Product:
        top = info.selected_fields[0]
        # isinstanceでチェックを追加
        requested_fields = [
            f.name for f in top.selections if isinstance(f, SelectedField)
        ]

        print(f"[GraphQL] リクエストフィールド: {requested_fields}", flush=True)
        product = grpc_product.get_product_by_id(id, fields=requested_fields)
        return build_dynamic_object(Product, product, requested_fields)

    @strawberry.field
    def cart(self, info: Info, id: str) -> Cart:
        top = info.selected_fields[0]
        # isinstanceでチェックを追加
        requested_fields = [
            f.name for f in top.selections if isinstance(f, SelectedField)
        ]

        print(f"[GraphQL] リクエストフィールド: {requested_fields}", flush=True)
        cart = grpc_cart.get_cart_by_id(id, fields=requested_fields)
        return build_dynamic_object(Cart, cart, requested_fields)


@strawberry.type
class Mutation:
    @strawberry.field
    def create_cart(self, id: str, product_id: str, quantity: int) -> str:
        return grpc_cart.create_cart(id=id, product_id=product_id, quantity=quantity)

    @strawberry.field
    def place_order(self, id: str, item_id: str, quantity: int) -> str:
        return grpc_order.place_order(id, item_id, quantity)

    @strawberry.field
    def refund_order(self, order_id: str) -> str:
        return grpc_order.refund_order(order_id)

    @strawberry.field
    def pay_order(self, order_id: str, amount: int) -> str:
        return grpc_payment.pay_order(order_id, amount)

    @strawberry.field
    async def workflow_order(self, order_id: str, item_id: str) -> str:
        return await publish_order_event(order_id, item_id)
