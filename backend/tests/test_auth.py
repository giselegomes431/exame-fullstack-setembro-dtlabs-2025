from httpx import Client

# Dados comuns para teste
TEST_USER = {
    "username": "test_auth_user",
    "password": "test_password123",
    "confirm_password": "test_password123"
}

def test_register_user_success(client: Client):
    # Testa se um novo usuário pode ser registrado com sucesso
    response = client.post("/api/v1/register", json=TEST_USER)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["username"] == TEST_USER["username"]

def test_register_duplicate_user(client: Client):
    # Testa a falha ao registrar um usuário com username duplicado
    
    # Primeiro registro
    client.post("/api/v1/register", json=TEST_USER)
    
    # Segundo registro
    response = client.post("/api/v1/register", json=TEST_USER)
    assert response.status_code == 400
    assert "Username already registered" in response.json()["detail"]

def test_login_success(client: Client):
    # Testa o login com credenciais válidas e a obtenção do token
    
    # Garante que o usuário existe
    client.post("/api/v1/register", json=TEST_USER)

    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_failure_invalid_password(client: Client):
    # Testa a falha no login com senha incorreta
    
    # Garante que o usuário existe
    client.post("/api/v1/register", json=TEST_USER)

    login_data = {
        "username": TEST_USER["username"],
        "password": "wrongpassword"
    }
    response = client.post("/api/v1/login", data=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"
