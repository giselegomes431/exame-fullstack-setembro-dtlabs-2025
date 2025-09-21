# backend/app/api/endpoints/telemetry.py

from fastapi import APIRouter
import pika
import json
import os

router = APIRouter()

# --- Configurações do RabbitMQ ---
rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_queue = os.environ.get('RABBITMQ_QUEUE', 'telemetry_queue')

# Variáveis globais para conexão persistente
rabbitmq_connection = None
rabbitmq_channel = None

def get_rabbitmq_connection():
    global rabbitmq_connection, rabbitmq_channel
    if rabbitmq_connection and rabbitmq_connection.is_open:
        return rabbitmq_connection, rabbitmq_channel

    try:
        rabbitmq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=rabbitmq_host,
                heartbeat=60,  # heartbeat para manter a conexão viva
                blocked_connection_timeout=300
            )
        )
        rabbitmq_channel = rabbitmq_connection.channel()
        rabbitmq_channel.queue_declare(queue=rabbitmq_queue, durable=True)
        print(f"[INFO] Conectado ao RabbitMQ em {rabbitmq_host}")
        return rabbitmq_connection, rabbitmq_channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"[ERRO] Não foi possível conectar ao RabbitMQ: {e}")
        return None, None

@router.post("/telemetry")
def receive_telemetry_data(data: dict):
    connection, channel = get_rabbitmq_connection()
    if not connection or not channel:
        return {"status": "error", "message": "Não foi possível conectar ao RabbitMQ."}

    try:
        message_body = json.dumps(data)
        channel.basic_publish(
            exchange='',
            routing_key=rabbitmq_queue,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,  # mensagem persistente
            )
        )
        print(f"[INFO] Mensagem enviada para a fila: {message_body}")
        return {"status": "success", "message": "Dados de telemetria recebidos e enviados para a fila."}

    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem: {e}")
        return {"status": "error", "message": "Erro ao processar os dados."}
