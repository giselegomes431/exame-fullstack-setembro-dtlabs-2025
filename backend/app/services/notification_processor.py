import pika
import json
import uuid
from sqlalchemy import and_
from sqlalchemy.orm import Session
from ..database.base import SessionLocal
from ..database.models import Notification, Device
from ..core.config import settings
import asyncio
import threading 

# Variável global para a instância do SocketIO
sio_instance = None 
main_loop_instance = None

def compare_values(telemetry_value: float, operator: str, threshold: float) -> bool:
    # Função segura para comparar valores
    val = float(telemetry_value)
    thresh = float(threshold)

    if operator == '>':
        return val > thresh
    elif operator == '<':
        return val < thresh
    elif operator == '==':
        return val == thresh
    elif operator == '>=':
        return val >= thresh
    elif operator == '<=':
        return val <= thresh
    elif operator == '!=':
        return val != thresh
    else:
        return False

async def emit_alert(sio, user_id, message, device_uuid):
    # Função assíncrona para emitir a notificação via SocketIO
    await sio.emit(
        'new_notification',
        {'message': message, 'device_uuid': device_uuid},
        to=str(user_id) # Envia para a ROOM do usuário
    )
    print(f"[SOCKET.IO EMITIDO] Evento 'new_notification' enviado para room: {user_id}")

def check_notification_rules(db: Session, telemetry_data: dict):
    # Verifica se alguma regra de notificação é acionada e dispara o WebSocket
    global sio_instance, main_loop_instance

    try:
        # Conversão segura do UUID
        device_uuid = uuid.UUID(telemetry_data.get('device_uuid'))
    except ValueError:
        print(f"[ALERTA] UUID inválido no payload: {telemetry_data.get('device_uuid')}")
        return
    
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not device:
        print(f"[ALERTA] Dispositivo não encontrado: {device_uuid}")
        return

    # Consulta as regras aplicáveis
    rules = db.query(Notification).filter(
        and_(
            Notification.user_id == device.user_id,
            Notification.device_uuid.in_([device_uuid, None])
        )
    ).all()
    
    for rule in rules:
        telemetry_value = telemetry_data.get(rule.parameter)
        
        if isinstance(telemetry_value, (int, float)):
            if compare_values(telemetry_value, rule.operator, rule.threshold):
                
                alert_message = f"ALERTA: {rule.message} | Device: {device.name} | {rule.parameter} é {telemetry_value}"
                print(f"[ALERTA EMITIDO] {alert_message}")

                # --- LÓGICA DE DISPARO DO WEBSOCKET ---
                if sio_instance and main_loop_instance:
                     future = asyncio.run_coroutine_threadsafe(
                        emit_alert(
                            sio_instance,
                            rule.user_id,
                            alert_message,
                            str(device_uuid)
                            ),
                            main_loop_instance # Usa o loop global
                    )

def rabbitmq_callback(ch, method, properties, body):
    # Função de callback do RabbitMQ
    telemetry_data = json.loads(body)
    
    db: Session = SessionLocal()
    try:
        check_notification_rules(db, telemetry_data)
    finally:
        db.close()
    
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_notification_listener(sio_app, loop_app):
    # Inicia o consumidor de notificações do backend
    global sio_instance, main_loop_instance
    main_loop_instance = loop_app
    sio_instance = sio_app
    
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
        
        print("Backend está ouvindo a fila de telemetria para notificações.")
        channel.basic_consume(
            queue=settings.RABBITMQ_QUEUE,
            on_message_callback=rabbitmq_callback
        )
        channel.start_consuming()
    except Exception as e:
        print(f"Erro no processador de notificações: {e}")