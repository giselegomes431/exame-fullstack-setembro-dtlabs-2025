# backend/app/services/messaging_service.py

import pika
import json
import os
from ..core.config import settings
from fastapi import HTTPException

def get_rabbitmq_connection():
    """Conecta ao RabbitMQ e retorna a conexão e o canal."""
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBITMQ_HOST))
        channel = connection.channel()
        channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Erro ao conectar com o RabbitMQ: {e}")
        return None, None

def publish_telemetry_message(telemetry_data: dict):
    """Publica uma mensagem na fila do RabbitMQ."""
    connection, channel = get_rabbitmq_connection()
    if not connection or not channel:
        raise HTTPException(status_code=500, detail="Could not connect to RabbitMQ.")
    
    try:
        message_body = json.dumps(telemetry_data)
        
        channel.basic_publish(
            exchange='', 
            routing_key=settings.RABBITMQ_QUEUE,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Mensagem persistente
            )
        )
        print(f"Mensagem enviada para a fila: {message_body}")
    except Exception as e:
        print(f"Erro ao publicar a mensagem no RabbitMQ: {e}")
        raise HTTPException(status_code=500, detail="Failed to publish message.")
    finally:
        if connection:
            connection.close()