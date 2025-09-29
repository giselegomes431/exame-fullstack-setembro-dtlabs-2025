import pytest
from httpx import Client

# Dados de Dispositivo válidos
VALID_DEVICE_DATA = {
    "name": "Sensor de Temperatura Teste",
    "location": "Sala 101",
    "sn": "123456789012",
    "description": "Termômetro digital."
}

# Dados de Dispositivo inválidos
INVALID_SN_DATA = VALID_DEVICE_DATA.copy()
INVALID_SN_DATA["sn"] = "12345" # SN muito curto

def test_create_device_unauthenticated(client: Client):
    # Verifica se a criação de dispositivo é bloqueada sem autenticação
    response = client.post("/api/v1/devices", json=VALID_DEVICE_DATA)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_create_device_invalid_sn(authenticated_client: Client):
    # Verifica se a criação falha com um número de série inválido (menos de 12 dígitos)
    response = authenticated_client.post("/api/v1/devices", json=INVALID_SN_DATA)
    # O Pydantic deve retornar 422 para erros de validação
    assert response.status_code == 422 
    assert any("sn must be a 12-digit number" in err["msg"] for err in response.json()["detail"])

def test_create_and_read_device_success(authenticated_client: Client):
    # Verifica a criação bem-sucedida e a listagem do novo dispositivo
    
    # Criação
    response_create = authenticated_client.post("/api/v1/devices", json=VALID_DEVICE_DATA)
    assert response_create.status_code == 201
    created_device = response_create.json()
    assert created_device["name"] == VALID_DEVICE_DATA["name"]
    assert created_device["sn"] == VALID_DEVICE_DATA["sn"]
    
    device_uuid = created_device["uuid"]

    # Listagem
    response_list = authenticated_client.get("/api/v1/devices")
    assert response_list.status_code == 200
    devices = response_list.json()
    assert any(d["uuid"] == device_uuid for d in devices)

    # Leitura por UUID
    response_get = authenticated_client.get(f"/api/v1/devices/{device_uuid}")
    assert response_get.status_code == 200
    assert response_get.json()["uuid"] == device_uuid

def test_create_device_duplicate_sn(authenticated_client: Client):
    # Verifica se a criação de um dispositivo com SN duplicado falha
    
    # Primeiro POST (sucesso)
    authenticated_client.post("/api/v1/devices", json=VALID_DEVICE_DATA)
    
    # Segundo POST com o mesmo SN (deve falhar)
    response = authenticated_client.post("/api/v1/devices", json=VALID_DEVICE_DATA)
    assert response.status_code == 400
    assert response.json()["detail"] == "Serial Number already registered"

def test_update_device(authenticated_client: Client):
    # Verifica a atualização de um dispositivo existente
    
    # Cria o dispositivo
    response_create = authenticated_client.post("/api/v1/devices", json=VALID_DEVICE_DATA)
    device_uuid = response_create.json()["uuid"]
    
    update_data = {"name": "Novo Nome Atualizado", "description": "Descrição Nova"}
    
    # Atualiza
    response_update = authenticated_client.put(f"/api/v1/devices/{device_uuid}", json=update_data)
    assert response_update.status_code == 200
    updated_device = response_update.json()
    assert updated_device["name"] == update_data["name"]
    assert updated_device["description"] == update_data["description"]
    assert updated_device["location"] == VALID_DEVICE_DATA["location"] # Não deve mudar

def test_delete_device(authenticated_client: Client):
    # Verifica a exclusão de um dispositivo
    
    # Cria o dispositivo
    response_create = authenticated_client.post("/api/v1/devices", json=VALID_DEVICE_DATA)
    device_uuid = response_create.json()["uuid"]
    
    # Deleta
    response_delete = authenticated_client.delete(f"/api/v1/devices/{device_uuid}")
    assert response_delete.status_code == 204
    
    # Confirma que foi deletado
    response_check = authenticated_client.get(f"/api/v1/devices/{device_uuid}")
    assert response_check.status_code == 404
