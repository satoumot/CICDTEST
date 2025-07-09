# gRPCの型定義とサービス定義をインポート
import cart_pb2
import cart_pb2_grpc
import grpc  # contextの型ヒントのためにインポート

# データベース操作用の関数をインポート
from model import create_cart, get_cart_by_id


# CartService（gRPCサービスの実装クラス）
class CartService(cart_pb2_grpc.CartServiceServicer):
    # カート情報を取得する処理（GetCart RPC）
    def GetCart(
        self, request: cart_pb2.GetCartRequest, context: grpc.ServicerContext
    ) -> cart_pb2.CartResponse:
        """指定されたIDのカート情報を取得します。"""
        # データベースからカート情報を取得
        cart_data = get_cart_by_id(request.id)

        # リクエストのログ出力
        print(f"gRPC Request: id={request.id}, fields={request.fields}", flush=True)

        # Cart型のレスポンスオブジェクトを作成
        cart = cart_pb2.Cart()

        # クライアントから要求されたフィールドだけをセット
        for field in request.fields:
            if field in cart_data:
                setattr(cart, field, cart_data[field])

        # 返す内容のログを出力
        print(f"Returning Product: {cart}", flush=True)

        # レスポンスとしてCartResponseを返す
        return cart_pb2.CartResponse(cart=cart)

    # カートを新規作成する処理（CreateCart RPC）
    def CreateCart(
        self, request: cart_pb2.CreateCartRequest, context: grpc.ServicerContext
    ) -> cart_pb2.CreateCartResponse:
        """新しいカートを作成します。"""
        # リクエストのログを表示
        print(f"[CartService] create_cart: {request}")

        # モデル層の関数を使って、カートをデータベースに追加
        create_cart(
            id=request.id, product_id=request.product_id, quantity=request.quantity
        )

        # 成功メッセージを返す
        return cart_pb2.CreateCartResponse(
            message=f"Cart {request.id} created successfully."
        )
