# worker/Dockerfile
FROM python:3.10-slim

# Install build dependencies, including netcat-openbsd
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    netcat-openbsd \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# ... o restante do seu Dockerfile permanece o mesmo
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]

CMD ["python", "consumer.py"]