# backend/app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # Correct import
from .api.endpoints import telemetry, auth, devices, notifications
from .database.base import create_tables
from .services import notification_processor
import threading
import time

app = FastAPI(on_startup=[create_tables])

# Adiciona o middleware CORS
origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(telemetry.router)
app.include_router(auth.router, prefix="/api/v1")
app.include_router(devices.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")

# Inicia o processador de notificações em uma thread separada
def start_processor_thread():
    time.sleep(10)
    notification_processor.start_notification_listener()

thread = threading.Thread(target=start_processor_thread, daemon=True)
thread.start()

@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Backend de Monitoramento de IoT!"}