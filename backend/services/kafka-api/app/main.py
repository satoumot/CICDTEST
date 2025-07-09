import json
import logging
import os

import uvicorn
from aiokafka import AIOKafkaProducer
from fastapi import FastAPI, HTTPException

# -----------------------------
# 設定
# -----------------------------
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "product-updates")
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka-service:9092")

# ロガー設定
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)

# FastAPI アプリ初期化
app = FastAPI()

# グローバルProducer（起動時に作成・再利用）
producer: AIOKafkaProducer | None = None

# -----------------------------
# ライフサイクルイベント
# -----------------------------


@app.on_event("startup")
async def startup_event() -> None:
    global producer
    log.info("🚀 Kafka Producer starting...")
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
    await producer.start()
    log.info("Kafka Producer started.")


@app.on_event("shutdown")
async def shutdown_event() -> None:
    global producer
    log.info("🛑 Kafka Producer shutting down...")
    if producer:
        await producer.stop()
    log.info("Kafka Producer stopped.")


# -----------------------------
# エンドポイント（複数対応）
# -----------------------------


@app.post("/update_product/")
async def update_products(products: list[dict]) -> dict:
    """
    Kafkaに複数の商品情報を送信するエンドポイント
    """
    # Mypyエラーを解消するため、producerがNoneでないことをチェック
    if not producer:
        raise HTTPException(status_code=503, detail="Kafka producer is not available.")

    results = []
    for product in products:
        log.info(f"📤 Sending message to Kafka: {product}")
        message = {"type": "update_product", "payload": product}
        value_json = json.dumps(message).encode("utf-8")
        try:
            # この時点でproducerはNoneではないことが保証されている
            await producer.send_and_wait(KAFKA_TOPIC, value_json)
            log.info(f"✅ Sent product {product.get('id')} to Kafka")
            results.append({"status": "success", "id": product.get("id")})
        except Exception as e:
            log.error(f"❌ Failed to send product {product.get('id')}: {e}")
            results.append(
                {"status": "error", "id": product.get("id"), "error": str(e)}
            )

    return {"message": f"{len(results)} products processed.", "results": results}


# -----------------------------
# ヘルスチェック用エンドポイント
# -----------------------------
@app.get("/health/")  # ヘルスチェック用エンドポイントを追加
async def health_check() -> dict:
    """
    ヘルスチェック用エンドポイント
    ルートへのGETリクエストに対し、ステータスコード200と{"status": "ok"}を返す
    """
    return {"status": "ok"}


# -----------------------------
# ローカル実行用
# -----------------------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
