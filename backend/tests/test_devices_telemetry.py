import pytest
from httpx import Client
from datetime import datetime, timedelta
import uuid
from backend.app.database.models import Telemetry
from backend.app.database.base import get_db
from backend.app.main import fastapi_app

# Dados básicos para criar um dispositivo
DUMMY_DEVICE_DATA = {
    "name": "TestDeviceTele",
    "location": "Lab",
    "sn": "987654321098",
    "description": "Telemetria Teste"
}

# Fixture para configurar dados de telemetria no banco de dados de teste
@pytest.fixture(scope="module")
def setup_telemetry_data(authenticated_client: Client):
    # Cria um dispositivo e insere dados de telemetria mockados
    response = authenticated_client.post("/api/v1/devices", json=DUMMY_DEVICE_DATA)
    device_uuid = response.json()["uuid"]
    
    # Sobrescreve a dependência get_db para obter a sessão de teste
    db_generator = fastapi_app.dependency_overrides.get(get_db)
    db = next(db_generator())
    
    telemetry_list = []
    current_time = datetime.utcnow()

    # Cria 48 registros (para simular 2 dias de dados a cada hora)
    for i in range(48):
        # Gera dados com variação
        cpu = 50.0 + (i % 10)
        temp = 40.0 + (i % 5)
        
        telemetry_data = Telemetry(
            cpu_usage=cpu,
            ram_usage=30.0,
            temperature=temp,
            latency=10,
            connectivity=1,
            boot_date=current_time - timedelta(hours=i),
            device_uuid=uuid.UUID(device_uuid)
        )
        telemetry_list.append(telemetry_data)
    
    db.add_all(telemetry_list)
    db.commit()
    db.close()

    return device_uuid

def test_get_latest_telemetry_list(authenticated_client: Client, setup_telemetry_data: str):
    # Verifica se a lista de últimas telemetrias retorna dados corretamente
    device_uuid = setup_telemetry_data
    
    response = authenticated_client.get(f"/api/v1/devices/{device_uuid}/latest-telemetry-list", params={"limit": 5})
    assert response.status_code == 200
    telemetries = response.json()
    
    assert len(telemetries) == 5
    # Verifica se a ordenação está correta (o mais novo deve ser o primeiro)
    assert telemetries[0]["cpu_usage"] > telemetries[-1]["cpu_usage"]

def test_get_historical_data_24h(authenticated_client: Client, setup_telemetry_data: str):
    # Verifica se a rota de dados históricos (24h) retorna dados agregados por hora
    device_uuid = setup_telemetry_data
    
    response = authenticated_client.get(f"/api/v1/devices/{device_uuid}/historical", params={"period": "last_24h"})
    assert response.status_code == 200
    data = response.json()
    
    assert "timestamps" in data
    assert "cpu_usage" in data
    
    assert len(data["timestamps"]) <= 25 and len(data["timestamps"]) >= 23 
    
def test_get_latest_telemetry_dashboard(authenticated_client: Client, setup_telemetry_data: str):
    # Verifica se o endpoint do dashboard retorna a última telemetria por dispositivo
    
    # A rota deve retornar um dicionário onde a chave é o UUID
    response = authenticated_client.get("/api/v1/devices/latest-telemetry")
    assert response.status_code == 200
    latest_telemetry = response.json()
    
    # Confirma que o UUID do nosso dispositivo está no dicionário
    assert setup_telemetry_data in latest_telemetry
    
    # Verifica a estrutura do payload
    device_data = latest_telemetry[setup_telemetry_data]
    assert "cpu_usage" in device_data
    assert "device_uuid" == setup_telemetry_data
