from fastapi import FastAPI
from .api.endpoints import telemetry, auth, devices
from .database.base import create_tables

# Cria a instância da API
# A função `create_tables` será executada na inicialização
app = FastAPI(on_startup=[create_tables])

# Inclui os routers dos endpoints
app.include_router(telemetry.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")

# Rota de teste
@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Backend de Monitoramento de IoT!"}