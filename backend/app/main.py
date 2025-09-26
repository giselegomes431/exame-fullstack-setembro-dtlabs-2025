# backend/app/main.py (CÓDIGO CORRIGIDO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import telemetry, auth, devices, notifications
from .database.base import create_tables
from .services import notification_processor
import threading
import time
import socketio

# 1. Crie o servidor Socket.IO
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")

# 2. Crie a instância do FastAPI (APENAS UMA VEZ)
#    Adicione o create_tables ao startup
fastapi_app = FastAPI(on_startup=[create_tables])

# Adiciona o middleware CORS ao FastAPI
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclui os routers
fastapi_app.include_router(telemetry.router)
fastapi_app.include_router(auth.router, prefix="/api/v1")
fastapi_app.include_router(devices.router, prefix="/api/v1")
fastapi_app.include_router(notifications.router, prefix="/api/v1")

# 3. Monte o SocketIO na aplicação FastAPI
fastapi_app.mount("/socket.io", socketio.ASGIApp(sio))

# Inicia o processador de notificações em uma thread separada
def start_processor_thread():
    time.sleep(10)
    notification_processor.start_notification_listener()

thread = threading.Thread(target=start_processor_thread, daemon=True)
thread.start()

@fastapi_app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Backend de Monitoramento de IoT!"}

# Importante: Exponha a instância do FastAPI para o Uvicorn
app = fastapi_app