import redis
import json
import uuid
from datetime import datetime
from fastapi import HTTPException
from ..core.config import settings

# --- Função de Serialização Personalizada ---
def custom_json_serializer(obj):
    """
    Converte tipos não serializáveis (como UUID e datetime) para string
    antes de salvar no Redis. Isso resolve os erros de 'Object of type X is not JSON serializable'.
    """
    if isinstance(obj, uuid.UUID):
        return str(obj)
    if isinstance(obj, datetime):
        # Usar o formato ISO 8601 (padrão) para preservar a informação de tempo
        return obj.isoformat()
    # Levanta um erro para outros tipos não suportados
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

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
        # Converte o valor para JSON, usando o serializador personalizado
        # O parâmetro 'default' garante que UUID e datetime sejam tratados.
        value_json = json.dumps(value, default=custom_json_serializer)
        # Salva no Redis com um tempo de expiração
        redis_client.setex(key, ttl_seconds, value_json)
    except Exception as e:
        print(f"Erro ao salvar no cache: {e}")
        # Em um ambiente de produção, é melhor logar o erro e falhar silenciosamente 
        # (continuar a execução sem cache, mas sem travar a aplicação).

def get_cache(key: str) -> any:
    """Busca um valor no cache."""
    try:
        cached_value = redis_client.get(key)
        if cached_value:
            # Converte de volta de JSON. UUIDs e datetimes virão como strings,
            # o que é o formato esperado para serem validados pelo Pydantic nos endpoints.
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
