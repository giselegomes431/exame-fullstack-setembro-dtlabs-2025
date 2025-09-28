import redis
import json
import uuid
from datetime import datetime
from fastapi import HTTPException
from ..core.config import settings

# --- Função de Serialização Personalizada ---
def custom_json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        # Usar o formato ISO 8601
        return obj.isoformat()

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

# --- Configuração do Redis ---
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def set_cache(key: str, value: any, ttl_seconds: int = 3600):
    try:
        value_json = json.dumps(value, default=custom_json_serializer)
        # Salva no Redis com um tempo de expiração
        redis_client.setex(key, ttl_seconds, value_json)
    except Exception as e:
        print(f"Erro ao salvar no cache: {e}")
        
def get_cache(key: str) -> any:
    try:
        cached_value = redis_client.get(key)
        if cached_value:
            return json.loads(cached_value)
        return None
    except Exception as e:
        print(f"Erro ao buscar no cache: {e}")
        return None

def clear_cache(key: str):
    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"Erro ao limpar o cache: {e}")
