# backend/app/main.py

from fastapi import FastAPI
from .api.endpoints import telemetry, auth, devices, notifications
from .database.base import create_tables
from .services import notification_processor
import threading
import time

app = FastAPI(on_startup=[create_tables])

app.include_router(telemetry.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")

# Inicia o processador de notificações em uma thread separada
def start_processor_thread():
    # Espera para garantir que o RabbitMQ está rodando
    time.sleep(10) 
    notification_processor.start_notification_listener()

thread = threading.Thread(target=start_processor_thread, daemon=True)
thread.start()

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Backend de Monitoramento de IoT!"}