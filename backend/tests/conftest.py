import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
# Importações necessárias para o isolamento
from backend.app.main import fastapi_app
from backend.app.database.base import Base, get_db
from backend.app.core.config import settings

# --- Configuração de Testes de Banco de Dados ---
# Usa SQLite em memória para garantir o isolamento e velocidade dos testes
# 🚨 Esta URL deve ser usada APENAS nos testes
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# Ajustamos o engine para o SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 1. Fixture para isolar o ambiente de Teste/DB (Escopo de função para cada teste)
@pytest.fixture(scope="function", autouse=True)
def setup_test_environment(monkeypatch):
    """
    Usa monkeypatch para forçar o settings.DATABASE_URL a ser o SQLite
    durante o ciclo de vida do TestClient, evitando conexões com o PostgreSQL real.
    """
    # 🚨 Sobrescreve a URL original para forçar o SQLite na inicialização do FastAPI
    monkeypatch.setattr(settings, "DATABASE_URL", SQLALCHEMY_DATABASE_URL)
    
    # 2. Setup e Teardown das tabelas
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

# 3. Função de sobrescrita de dependência
def override_get_db() -> Generator[Session, None, None]:
    """Sobrescreve a dependência get_db para usar a sessão de teste (SQLite)."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Aplica a sobrescrita à aplicação FastAPI (necessário para rodar as rotas)
fastapi_app.dependency_overrides[get_db] = override_get_db

# --- Fixtures de Cliente ---

@pytest.fixture(scope="module")
def client():
    """Fixture que fornece o TestClient do FastAPI."""
    # TestClient chama o lifespan do FastAPI, que usa a URL sobrescrita para o SQLite
    with TestClient(fastapi_app) as c:
        yield c

@pytest.fixture(scope="module")
def authenticated_client(client: TestClient):
    """
    Fixture que registra um usuário de teste e retorna um cliente
    com o header de autenticação JWT configurado.
    """
    # Dados de autenticação únicos
    test_username = "test_auth_user"
    test_password = "test_password123"
    
    # 1. Registra um usuário de teste
    register_data = {
        "username": test_username,
        "password": test_password,
    }
    # Tenta registrar (a falha por duplicidade na segunda execução é esperada)
    client.post("/api/v1/register", json=register_data)

    # 2. Faz o login
    login_data = {
        "username": test_username,
        "password": test_password,
    }
    response = client.post("/api/v1/login", data=login_data)
    
    if response.status_code != 200:
        # Se o login falhar, mostramos a resposta para debug
        raise Exception(f"Falha na autenticação do usuário de teste: {response.json()}")

    token = response.json().get("access_token")

    # 3. Configura o cliente com o header de autenticação
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}",
    }
    return client
