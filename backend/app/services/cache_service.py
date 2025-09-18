# backend/app/services/cache_service.py

import redis
import json
from fastapi import HTTPException
from ..core.config import settings

# --- Configuração do Redis ---
redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,
    decode_responses=True
)

def set_cache(key: str, value: any, ttl_seconds: int = 3600):
    """Salva um valor no cache com um tempo de vida (TTL)."""
    try:
        # Converte o valor para JSON
        value_json = json.dumps(value)
        # Salva no Redis com um tempo de expiração
        redis_client.setex(key, ttl_seconds, value_json)
    except Exception as e:
        print(f"Erro ao salvar no cache: {e}")
        # Lidar com o erro de forma mais robusta em produção

def get_cache(key: str) -> any:
    """Busca um valor no cache."""
    try:
        cached_value = redis_client.get(key)
        if cached_value:
            # Converte de volta para o formato original
            return json.loads(cached_value)
        return None
    except Exception as e:
        print(f"Erro ao buscar no cache: {e}")
        return None

def clear_cache(key: str):
    """Remove um valor do cache."""
    try:
        redis_client.delete(key)
    except Exception as e:
        print(f"Erro ao limpar o cache: {e}")