# worker/consumer.py (Código final)

import json
import pika
from sqlalchemy.orm import Session
from base import engine, Base, SessionLocal
from models import Telemetry
import os
import time

# Configurações do RabbitMQ
rabbitmq_host = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
rabbitmq_queue = os.environ.get('RABBITMQ_QUEUE', 'telemetry_queue')

def save_telemetry_to_db(telemetry_data):
    """Salva os dados de telemetria no banco de dados."""
    db: Session = SessionLocal()
    try:
        new_telemetry = Telemetry(
            cpu_usage=telemetry_data.get('cpu_usage'),
            ram_usage=telemetry_data.get('ram_usage'),
            disk_free=telemetry_data.get('disk_free'),
            temperature=telemetry_data.get('temperature'),
            latency=telemetry_data.get('latency'),
            connectivity=telemetry_data.get('connectivity'),
            boot_date=telemetry_data.get('boot_date'),
            device_uuid=telemetry_data.get('device_uuid')
        )
        db.add(new_telemetry)
        db.commit()
        db.refresh(new_telemetry)
        
        print(f"Dados de telemetria salvos: {telemetry_data}")
        
    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar no banco de dados: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    """Função chamada quando uma mensagem chega na fila."""
    print(f" [x] Recebido: {body.decode()}")
    telemetry_data = json.loads(body)
    save_telemetry_to_db(telemetry_data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

def start_consuming():
    """Inicia o consumo de mensagens do RabbitMQ com retentativas."""
    connection = None
    retries = 5
    while retries > 0:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
            channel = connection.channel()
            channel.queue_declare(queue=rabbitmq_queue, durable=True)
            print(' [*] Aguardando mensagens. Para sair, pressione CTRL+C')
            
            channel.basic_consume(
                queue=rabbitmq_queue,
                on_message_callback=callback
            )
            channel.start_consuming()
            break
        except pika.exceptions.AMQPConnectionError as e:
            retries -= 1
            print(f"Erro ao conectar com o RabbitMQ: {e}. Tentativas restantes: {retries}")
            if retries > 0:
                time.sleep(5)
        except KeyboardInterrupt:
            print('Encerrando...')
            break
        finally:
            if connection and connection.is_open:
                connection.close()

if __name__ == '__main__':
    start_consuming()