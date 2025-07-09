FROM python:3.13.5

WORKDIR /app

COPY backend/services/graphql-service/app ./

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/shared /shared
RUN pip install -e /shared

# RUN python -m grpc_tools.protoc \
#     -I /shared/proto \
#     --python_out=/app \
#     --grpc_python_out=/app \
#     /shared/proto/cart.proto \
#     /shared/proto/product.proto \
#     /shared/proto/order.proto \
#     /shared/proto/payment.proto

CMD python -m grpc_tools.protoc -I /shared/proto --python_out=/app --grpc_python_out=/app /shared/proto/*.proto && \
    python -m debugpy --listen 0.0.0.0:5678 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload