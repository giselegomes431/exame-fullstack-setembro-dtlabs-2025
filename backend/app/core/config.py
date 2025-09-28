import os

class Settings:
    # Configurações do Banco de Dados
    DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://testeiotdb:iotdb2025@db:5432/iotdb")

    # Configurações do RabbitMQ
    RABBITMQ_HOST: str = os.environ.get("RABBITMQ_HOST", "rabbitmq")
    RABBITMQ_QUEUE: str = os.environ.get("RABBITMQ_QUEUE", "telemetry_queue")

    # Chave para o JWT
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "gisele1409")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Configurações do Redis
    REDIS_HOST: str = os.environ.get("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.environ.get("REDIS_PORT", 6379))

settings = Settings()