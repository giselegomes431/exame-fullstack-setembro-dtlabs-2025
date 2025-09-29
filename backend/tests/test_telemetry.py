import pytest
from httpx import Client
from unittest.mock import patch
import uuid

# Mock de dados de telemetria. O UUID deve ser válido no formato
VALID_TELEMETRY_DATA = {
    "cpu_usage": 55.0,
    "ram_usage": 30.5,
    "temperature": 45.2,
    "latency": 10.0,
    "connectivity": 1,
    "boot_date": "2025-09-26T10:00:00Z",
    "device_uuid": str(uuid.uuid4())
}

@patch('backend.app.api.endpoints.telemetry.publish_telemetry_message')
def test_receive_telemetry_success(mock_publish, client: Client):
    # Testa se o endpoint recebe dados e chama o publicador de mensagens corretamente
    
    response = client.post("/telemetry", json=VALID_TELEMETRY_DATA)
    
    # Verifica o status HTTP da API
    assert response.status_code == 200
    
    # Verifica a resposta JSON da API
    assert response.json()["status"] == "success"
    assert "recebidos e enviados para a fila" in response.json()["message"]
    
    mock_publish.assert_called_once_with(VALID_TELEMETRY_DATA)

@patch('backend.app.api.endpoints.telemetry.publish_telemetry_message')
def test_receive_telemetry_error_handling(mock_publish, client: Client):
    # Testa se o endpoint lida corretamente com exceções no serviço de mensageria.

    # Configura o mock para levantar uma exceção simulando uma falha de conexão/publicação
    mock_publish.side_effect = Exception("Falha de conexão com RabbitMQ simulada")
    
    response = client.post("/telemetry", json=VALID_TELEMETRY_DATA)
    
    # Verifica o status HTTP
    assert response.status_code == 200
    
    # Verifica se a resposta JSON reflete o erro interno
    assert response.json()["status"] == "error"
    assert "Erro interno ao processar os dados." in response.json()["message"]
    
    # Confirma que o publicador foi chamado, mesmo que tenha falhado
    mock_publish.assert_called_once()
