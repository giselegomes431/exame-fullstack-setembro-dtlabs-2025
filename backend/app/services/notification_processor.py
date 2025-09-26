# backend/app/services/notification_processor.py (CÓDIGO FINAL CORRIGIDO)

import pika
import json
import uuid
from sqlalchemy import and_
from sqlalchemy.orm import Session
from ..database.base import SessionLocal
from ..database.models import Notification, Device
from ..core.config import settings
import asyncio # <-- Importe esta biblioteca
import threading 

# Variável global para a instância do SocketIO
sio_instance = None 


def compare_values(telemetry_value: float, operator: str, threshold: float) -> bool:
    """Função segura para comparar valores."""
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


def check_notification_rules(db: Session, telemetry_data: dict):
    """Verifica se alguma regra de notificação é acionada e dispara o WebSocket."""
    global sio_instance

    try:
        # Conversão segura do UUID (necessária após a lógica de simulação)
        device_uuid = uuid.UUID(telemetry_data.get('device_uuid'))
    except ValueError:
        print(f"[ALERTA] UUID inválido no payload: {telemetry_data.get('device_uuid')}")
        return
    
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not device:
        print(f"[ALERTA] Dispositivo não encontrado: {device_uuid}")
        return

    # Consulta as regras aplicáveis (lógica que você criou)
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
                
                # --- LÓGICA DE DISPARO DO WEBSOCKET ---
                alert_message = f"ALERTA: {rule.message} | Device: {device.name} | {rule.parameter} é {telemetry_value}"
                print(f"[ALERTA EMITIDO] {alert_message}")

                # 1. Envia o evento via SocketIO
                if sio_instance:
                    # Obtenha o loop de eventos da thread principal
                    loop = asyncio.get_event_loop()
                    
                    # Execute a função assíncrona de forma thread-safe
                    asyncio.run_coroutine_threadsafe(
                        sio_instance.emit(
                            'new_notification',
                            {'message': alert_message, 'device_uuid': str(device_uuid)},
                            # room=str(device.user_id) 
                        ),
                        loop
                    )
# FIM da função check_notification_rules


def rabbitmq_callback(ch, method, properties, body):
    """Função de callback do RabbitMQ."""
    telemetry_data = json.loads(body)
    
    db: Session = SessionLocal()
    try:
        check_notification_rules(db, telemetry_data)
    finally:
        db.close()
    
    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_notification_listener(sio_app): # <-- Recebe a instância do SocketIO
    """Inicia o consumidor de notificações do backend."""
    global sio_instance
    sio_instance = sio_app # Armazena a instância globalmente
    
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