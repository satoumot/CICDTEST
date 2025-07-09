FROM python:3.13.5

WORKDIR /app

COPY backend/services/grpc-payment-service/app ./

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/shared /shared
RUN pip install -e /shared

RUN python -m grpc_tools.protoc \
    -I /shared/proto \
    --python_out=/app \
    --grpc_python_out=/app \
    /shared/proto/payment.proto

CMD ["python", "main.py"]

