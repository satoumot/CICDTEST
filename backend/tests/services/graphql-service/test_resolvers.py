import pytest
from unittest.mock import patch, MagicMock, AsyncMock

# ワークフローやTOMLを変更しないため、テストファイル側でインポートパスを修正します。
# 「backend.」で始まらないように、現在のワーキングディレクトリ（backend/）からの相対パスで記述します。
from services.graphql_service.app.resolvers import (
    Query,
    Mutation,
    Product,
    build_dynamic_object,
)

# ========================================================
# テスト対象: 共通関数
# ========================================================

def test_build_dynamic_object():
    """
    build_dynamic_objectが指定されたフィールドのみを持つオブジェクトを正しく生成するかテスト
    """
    # モックのソースオブジェクトを作成
    source_obj = MagicMock()
    source_obj.id = "prod-123"
    source_obj.name = "Test Product"
    source_obj.price = 99.99
    source_obj.description = "This is a test."

    # 'id'と'name'だけを要求
    fields_to_get = ["id", "name"]
    result_product = build_dynamic_object(Product, source_obj, fields_to_get)

    # 要求したフィールドは値が設定され、他はNoneになることを確認
    assert isinstance(result_product, Product)
    assert result_product.id == "prod-123"
    assert result_product.name == "Test Product"
    assert result_product.price is None
    assert result_product.description is None


# ========================================================
# テスト対象: Query
# ========================================================

# gRPCクライアントのモックを一元管理するためのパッチ
# `resolvers.py` 内で `grpc_product` としてインポートされているものをモックの対象にする
@patch("services.graphql_service.app.resolvers.grpc_product")
def test_query_product(mock_grpc_product):
    """
    Query.productがgRPCクライアントを正しい引数で呼び出し、結果を返すかテスト
    """
    # 準備：モックの設定
    # 1. gRPCクライアントの戻り値を設定
    mock_product_response = MagicMock()
    mock_product_response.id = "prod-001"
    mock_product_response.name = "Mocked Product"
    mock_grpc_product.get_product_by_id.return_value = mock_product_response

    # 2. StrawberryのInfoオブジェクトを模倣するモックを作成
    mock_info = MagicMock()
    mock_field = MagicMock()
    mock_field.name = "name"
    mock_info.selected_fields = [MagicMock(selections=[mock_field])]

    # 実行
    query_resolver = Query()
    result = query_resolver.product(info=mock_info, id="prod-001")

    # 検証
    # 1. gRPCクライアントが期待通りに呼び出されたか
    mock_grpc_product.get_product_by_id.assert_called_once_with("prod-001", fields=["name"])

    # 2. 返されたオブジェクトの中身が正しいか
    assert result.id is None # nameしか要求していないのでidはNone
    assert result.name == "Mocked Product"


# ========================================================
# テスト対象: Mutation
# ========================================================

# 複数のgRPCクライアントをまとめてモック
@patch("services.graphql_service.app.resolvers.grpc_payment")
@patch("services.graphql_service.app.resolvers.grpc_order")
@patch("services.graphql_service.app.resolvers.grpc_cart")
def test_mutations_call_grpc_clients(mock_grpc_cart, mock_grpc_order, mock_grpc_payment):
    """
    各Mutationが対応するgRPCクライアントを正しく呼び出すかテスト
    """
    mutation_resolver = Mutation()

    # --- create_cartのテスト ---
    mock_grpc_cart.create_cart.return_value = "cart-created-successfully"
    result = mutation_resolver.create_cart(id="cart-01", product_id="prod-01", quantity=2)
    mock_grpc_cart.create_cart.assert_called_once_with(id="cart-01", product_id="prod-01", quantity=2)
    assert result == "cart-created-successfully"

    # --- place_orderのテスト ---
    mock_grpc_order.place_order.return_value = "order-placed-successfully"
    result = mutation_resolver.place_order(id="order-01", item_id="item-01", quantity=1)
    mock_grpc_order.place_order.assert_called_once_with("order-01", "item-01", 1)
    assert result == "order-placed-successfully"


# `async`関数をテストするためのデコレーター
@pytest.mark.asyncio
# `publish_order_event`関数を非同期モック(AsyncMock)に置き換え
@patch("services.graphql_service.app.resolvers.publish_order_event", new_callable=AsyncMock)
async def test_workflow_order(mock_publish_order_event):
    """
    workflow_orderがRabbitMQのpublish関数を正しく呼び出すかテスト
    """
    # 準備：モックの戻り値を設定
    mock_publish_order_event.return_value = "event-published"

    # 実行
    mutation_resolver = Mutation()
    result = await mutation_resolver.workflow_order(order_id="workflow-123", item_id="item-456")

    # 検証
    # 1. モックにした関数が期待通りに呼び出されたか
    mock_publish_order_event.assert_awaited_once_with("workflow-123", "item-456")

    # 2. 返り値がモックの値と一致するか
    assert result == "event-published"