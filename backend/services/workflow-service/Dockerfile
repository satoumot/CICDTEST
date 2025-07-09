FROM python:3.13.5

WORKDIR /app

COPY backend/services/workflow-service/app ./

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 環境変数でバッファリング無効化
ENV PYTHONUNBUFFERED=1

COPY backend/shared /shared
RUN pip install -e /shared

RUN python -m grpc_tools.protoc \
    -I /shared/proto \
    --python_out=/app \
    --grpc_python_out=/app \
    /shared/proto/order.proto \
    /shared/proto/payment.proto

CMD ["sh", "-c", "python consumer.py & python main.py"]