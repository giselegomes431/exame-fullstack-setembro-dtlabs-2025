import pytest
from backend.app.api.endpoints import devices as devices_endpoint
from backend.app.services import cache_service

# Mock simples do serviço de cache
class MockCacheService:
    def __init__(self):
        self.cache = {}

    def get_cache(self, key):
        # Apenas retorna None para simular um miss e forçar a consulta ao DB
        return None 

    def set_cache(self, key, value, ttl_seconds):
        # Simula o armazenamento, mas não é usado nas asserções de teste
        self.cache[key] = value

    def clear_cache(self, key):
        if key in self.cache:
            del self.cache[key]
        return True

# Instância do mock
mock_cache = MockCacheService()

# Função que sobrescreve as chamadas reais
def override_get_cache(key: str):
    return mock_cache.get_cache(key)

def override_set_cache(key: str, value: dict, ttl_seconds: int):
    return mock_cache.set_cache(key, value, ttl_seconds)

def override_clear_cache(key: str):
    return mock_cache.clear_cache(key)

# 🚨 Aplica a sobrescrita aos endpoints ANTES de rodar os testes
devices_endpoint.get_cache = override_get_cache
devices_endpoint.set_cache = override_set_cache
devices_endpoint.clear_cache = override_clear_cache
