# backend/tests/services/graphql-service/app/test_resolve.py

import json
from types import SimpleNamespace
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from strawberry.types.nodes import SelectedField

# プロジェクト構造がこのインポートを許可していると仮定します。
# PYTHONPATHの調整が必要な場合があります。
from backend.services.graphql_service.app import resolvers
from backend.services.graphql_service.app.resolvers import (
    Product,
    Cart,
    Query,
    Mutation,
    build_dynamic_object,
    publish_order_event,
)

# このファイル内のすべてのテストをasyncioとしてマークする
pytestmark = pytest.mark.asyncio


# ========================================================
# モック & フィクスチャ
# ========================================================

def create_mock_info(*fields: str) -> MagicMock:
    """指定されたフィールドを持つInfoオブジェクトのモックを作成します。"""
    mock_info = MagicMock()
    selections = [MagicMock(spec=SelectedField, name=field) for field in fields]
    mock_info.selected_fields = [MagicMock(selections=selections)]
    return mock_info


# ========================================================
# テストスイート
# ========================================================

class TestCommonFunctions:
    """共通ユーティリティ関数のテスト。"""

    def test_build_dynamic_object(self):
        """
        指定されたフィールドのみが設定されたProductインスタンスを作成するべき。
        """
        # gRPCコールから返されるような、モックのソースオブジェクト
        source_obj = SimpleNamespace(
            id="prod-123", name="Test Product", price=99.99, description="A great product"
        )
        
        # 'id'と'price'のみをリクエストする
        requested_fields = ["id", "price"]

        # 関数を呼び出す
        result_product = build_dynamic_object(Product, source_obj, requested_fields)

        # アサーション
        assert isinstance(result_product, Product)
        assert result_product.id == "prod-123"
        assert result_product.price == 99.99
        # リクエストされなかったフィールドはNoneになるべき
        assert result_product.name is None
        assert result_product.description is None


class TestRabbitMQ:
    """RabbitMQとの連携に関するテスト。"""

    @patch("resolve.aio_pika.connect_robust")
    async def test_publish_order_event(self, mock_connect_robust):
        """
        RabbitMQに正しく接続し、フォーマットされたメッセージをpublishするべき。
        """
        # connection/channelチェーンのための非同期モックを設定
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_exchange = AsyncMock()

        mock_connect_robust.return_value = mock_connection
        mock_connection.channel.return_value = mock_channel
        mock_channel.default_exchange = mock_exchange

        # 関数を呼び出す
        order_id = "order-456"
        item_id = "item-789"
        result = await publish_order_event(order_id, item_id)

        # アサーション
        mock_connect_robust.assert_awaited_once_with("amqp://user:pass@rabbitmq/")
        mock_connection.channel.assert_awaited_once()

        # publishされたメッセージをチェック
        mock_exchange.publish.assert_awaited_once()
        args, kwargs = mock_exchange.publish.call_args
        message = args[0]
        
        # メッセージボディを検証
        expected_body = {"id": order_id, "item_id": item_id}
        assert json.loads(message.body.decode()) == expected_body
        
        # ルーティングキーを検証
        assert kwargs["routing_key"] == "order.created"

        mock_connection.close.assert_awaited_once()
        assert result == f"Order event published for {order_id}"


class TestGraphQLQuery:
    """GraphQL Queryリゾルバのテスト。"""

    @patch("resolve.grpc_product.get_product_by_id")
    def test_product_resolver(self, mock_get_product):
        """
        gRPCサービスに指定されたフィールドを要求し、Productを返すべき。
        """
        # gRPCのレスポンスをモック化
        mock_product_response = SimpleNamespace(id="prod-123", name="Test Product")
        mock_get_product.return_value = mock_product_response
        
        # GraphQLのInfoオブジェクトをモック化
        mock_info = create_mock_info("id", "name")
        
        # リゾルバクラスをインスタンス化し、メソッドを呼び出す
        query_resolver = Query()
        result = query_resolver.product(info=mock_info, id="prod-123")
        
        # アサーション
        mock_get_product.assert_called_once_with("prod-123", fields=["id", "name"])
        assert isinstance(result, Product)
        assert result.id == "prod-123"
        assert result.name == "Test Product"
        assert result.price is None # リクエストされていない

    @patch("resolve.grpc_cart.get_cart_by_id")
    def test_cart_resolver(self, mock_get_cart):
        """
        gRPCサービスに指定されたフィールドを要求し、Cartを返すべき。
        """
        mock_cart_response = SimpleNamespace(id="cart-abc", quantity=5)
        mock_get_cart.return_value = mock_cart_response
        
        mock_info = create_mock_info("id", "quantity")
        
        query_resolver = Query()
        result = query_resolver.cart(info=mock_info, id="cart-abc")
        
        mock_get_cart.assert_called_once_with("cart-abc", fields=["id", "quantity"])
        assert isinstance(result, Cart)
        assert result.id == "cart-abc"
        assert result.quantity == 5
        assert result.product_id is None # リクエストされていない


class TestGraphQLMutation:
    """GraphQL Mutationリゾルバのテスト。"""

    @patch("resolve.grpc_cart.create_cart")
    def test_create_cart(self, mock_create_cart):
        """create_cart gRPCメソッドを正しい引数で呼び出すべき。"""
        mock_create_cart.return_value = "Cart created successfully"
        mutation_resolver = Mutation()
        
        result = mutation_resolver.create_cart(id="cart-1", product_id="prod-1", quantity=2)
        
        mock_create_cart.assert_called_once_with(id="cart-1", product_id="prod-1", quantity=2)
        assert result == "Cart created successfully"

    @patch("resolve.grpc_order.place_order")
    def test_place_order(self, mock_place_order):
        """place_order gRPCメソッドを正しい引数で呼び出すべき。"""
        mock_place_order.return_value = "Order placed"
        mutation_resolver = Mutation()

        result = mutation_resolver.place_order(id="order-1", item_id="item-1", quantity=1)

        mock_place_order.assert_called_once_with("order-1", "item-1", 1)
        assert result == "Order placed"

    @patch("resolve.grpc_payment.pay_order")
    def test_pay_order(self, mock_pay_order):
        """pay_order gRPCメソッドを正しい引数で呼び出すべき。"""
        mock_pay_order.return_value = "Payment successful"
        mutation_resolver = Mutation()

        result = mutation_resolver.pay_order(order_id="order-1", amount=500)

        mock_pay_order.assert_called_once_with("order-1", 500)
        assert result == "Payment successful"

    @patch("resolve.publish_order_event", new_callable=AsyncMock)
    async def test_workflow_order(self, mock_publish_event):
        """非同期関数 publish_order_event を呼び出すべき。"""
        mock_publish_event.return_value = "Event published"
        mutation_resolver = Mutation()

        result = await mutation_resolver.workflow_order(order_id="order-flow-1", item_id="item-abc")

        mock_publish_event.assert_awaited_once_with("order-flow-1", "item-abc")
        assert result == "Event published"