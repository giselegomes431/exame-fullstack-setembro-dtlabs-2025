import asyncio
import threading
import time
import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.endpoints import telemetry, auth, devices, notifications
from .database.base import create_tables
from .services import notification_processor

# 1. Crie o servidor Socket.IO como um objeto global
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")

# 2. Crie a instância do FastAPI
# A função get_main_loop será executada como parte da inicialização
fastapi_app = FastAPI() 

# NOVO: Variável global para armazenar o event loop principal
main_event_loop = None

# Adiciona o middleware CORS
origins = ["http://localhost", "http://localhost:3000", "http://localhost:5173", "*"]
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

# Função que a thread do RabbitMQ irá rodar
def start_processor_thread(sio_instance, loop_instance):
    # Dê um pequeno tempo de espera para garantir que o RabbitMQ está pronto
    time.sleep(5) 
    notification_processor.start_notification_listener(sio_instance, loop_instance)

# 🚨 AJUSTE CRÍTICO: Use o hook de 'startup' para garantir que o loop exista
@fastapi_app.on_event("startup")
def get_main_loop_and_start_processor():
    global main_event_loop
    # Captura o loop de eventos que o Uvicorn está usando
    main_event_loop = asyncio.get_event_loop()
    create_tables()

    # Inicia a thread DO PROCESSADOR AQUI, APÓS o loop ser capturado.
    thread = threading.Thread(
        target=start_processor_thread, 
        args=(sio, main_event_loop), 
        daemon=True
    )
    thread.start()
    print("[INIT] Processador de Notificações iniciado em thread separada.")


@sio.on('connect')
async def connect(sid, environ, auth):
    user_id = auth.get('userId')
    if user_id:
        await sio.enter_room(sid, str(user_id)) 
        print(f"[SOCKET.IO DEBUG] Conexão recebida. SID: {sid}, Auth Payload: {auth}")
        print(f"[SOCKET.IO] Cliente {sid} ENTROU na sala {user_id}")
    else:
        print(f"[SOCKET.IO] Cliente {sid} conectado sem autenticação.")

# Exponha a instância do FastAPI para o Uvicorn
app = fastapi_app
