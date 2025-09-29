import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from backend.app.main import fastapi_app
from backend.app.database.base import Base, get_db
from backend.app.core.config import settings

# --- Configuração de Testes de Banco de Dados ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 1. Fixture para isolar o ambiente de Teste/DB
@pytest.fixture(scope="function", autouse=True)
def setup_test_environment(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_URL", SQLALCHEMY_DATABASE_URL)
    
    # Setup e Teardown das tabelas
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# Função de sobrescrita de dependência
def override_get_db() -> Generator[Session, None, None]:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Aplica a sobrescrita à aplicação FastAPI
fastapi_app.dependency_overrides[get_db] = override_get_db

# --- Fixtures de Cliente ---
@pytest.fixture(scope="module")
def client():
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture(scope="module")
def authenticated_client(client: TestClient):
    
    # Dados de autenticação únicos
    test_username = "test_auth_user"
    test_password = "test_password123"
    
    # Registra um usuário de teste
    register_data = {
        "username": test_username,
        "password": test_password,
    }
    # Tenta registrar
    client.post("/api/v1/register", json=register_data)

    # Faz o login
    login_data = {
        "username": test_username,
        "password": test_password,
    }
    response = client.post("/api/v1/login", data=login_data)
    
    if response.status_code != 200:
        # Se o login falhar, mostramos a resposta para debug
        raise Exception(f"Falha na autenticação do usuário de teste: {response.json()}")

    token = response.json().get("access_token")

    # Configura o cliente com o header de autenticação
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}",
    }
    return client
