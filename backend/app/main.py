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
fastapi_app = FastAPI(on_startup=[create_tables])

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

# Inicia o processador de notificações em uma thread separada.
def start_processor_thread(sio_instance):
    # Define o loop de eventos para a nova thread (Correção do erro "no current event loop")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    time.sleep(10) 
    notification_processor.start_notification_listener(sio_instance)


thread = threading.Thread(target=start_processor_thread, args=(sio,), daemon=True)
thread.start()

@fastapi_app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Backend de Monitoramento de IoT!"}

# 🚨 CORREÇÃO: Função async e await em enter_room
@sio.on('connect')
async def connect(sid, environ, auth):
    user_id = auth.get('userId')
    if user_id:
        # Usar await para a coroutine enter_room
        await sio.enter_room(sid, str(user_id)) 
        print(f"[SOCKET.IO DEBUG] Conexão recebida. SID: {sid}, Auth Payload: {auth}")
        print(f"[SOCKET.IO] Cliente {sid} ENTROU na sala {user_id}")
    else:
        print(f"[SOCKET.IO] Cliente {sid} conectado sem autenticação.")

# Exponha a instância do FastAPI para o Uvicorn
app = fastapi_app
