FROM python:3.13.5

WORKDIR /app

COPY backend/services/kafka-api/app ./

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/shared /shared
RUN pip install -e /shared

CMD ["python", "main.py"]
