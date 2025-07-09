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
    各Mutationが対応するgRPCクライアントを正しく