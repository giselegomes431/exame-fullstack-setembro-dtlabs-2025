# backend/app/services/notification_processor.py

import pika
import json
from sqlalchemy import and_
from sqlalchemy.orm import Session
from ..database.base import get_db, SessionLocal
from ..database.models import Notification, Device
from ..core.config import settings

def check_notification_rules(db: Session, telemetry_data: dict):
    """Verifica se alguma regra de notificação é acionada."""
    device_uuid = telemetry_data.get('device_uuid')
    
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not device:
        print(f"Dispositivo não encontrado: {device_uuid}")
        return

    rules = db.query(Notification).filter(
        and_(
            Notification.user_id == device.user_id,
            Notification.device_uuid.in_([device_uuid, None])
        )
    ).all()
    
    for rule in rules:
        telemetry_value = telemetry_data.get(rule.parameter)
        if telemetry_value is not None:
            if eval(f"{telemetry_value} {rule.operator} {rule.threshold}"):
                print(f"ALERTA ACIONADO: {rule.message} para o dispositivo {device_uuid}")
                # Aqui você integraria o WebSocket para enviar a notificação.

def rabbitmq_callback(ch, method, properties, body):
    """Função de callback do RabbitMQ."""
    telemetry_data = json.loads(body)
    
    db: Session = SessionLocal()
    try:
        check_notification_rules(db, telemetry_data)
    finally:
        db.close()
    
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_notification_listener():
    """Inicia o consumidor de notificações do backend."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
        
        channel.basic_consume(
            queue=settings.RABBITMQ_QUEUE,
            on_message_callback=rabbitmq_callback
        )
        print("Backend está ouvindo a fila de telemetria para notificações.")
        channel.start_consuming()
    except Exception as e:
        print(f"Erro no processador de notificações: {e}")