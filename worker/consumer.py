import json
import pika
from sqlalchemy.orm import Session
from base import SessionLocal
from models import Telemetry
import os
from datetime import datetime
import uuid
import time

# Configurações do RabbitMQ
RABBITMQ_HOST = os.environ.get('RABBITMQ_HOST', 'rabbitmq')
RABBITMQ_QUEUE = os.environ.get('RABBITMQ_QUEUE', 'telemetry_queue')

def save_telemetry_to_db(data: dict):
    # Salva dados de telemetria no PostgreSQL
    db: Session = SessionLocal()
    try:
        print(f"[INFO] Recebido para salvar no DB: {data}")
        boot_date_str = data.get('boot_date')
        boot_date = None
        if boot_date_str:
            try:
                # Adiciona o tratamento para o formato com Z no final
                boot_date = datetime.fromisoformat(boot_date_str.replace('Z', '+00:00'))
            except ValueError:
                # Tenta formatar sem substituição caso o formato seja apenas ISO
                try:
                    boot_date = datetime.fromisoformat(boot_date_str)
                except Exception as date_e:
                    print(f"[ERRO CONVERSÃO] Falha ao converter boot_date '{boot_date_str}': {date_e}")

        device_uuid_str = data.get('device_uuid')
        device_uuid = None
        if device_uuid_str:
            try:
                device_uuid = uuid.UUID(device_uuid_str)
            except Exception as uuid_e:
                print(f"[ERRO CONVERSÃO] Falha ao converter device_uuid '{device_uuid_str}': {uuid_e}")
            
        if not device_uuid:
            raise ValueError(f"UUID do dispositivo inválido ou ausente: {device_uuid_str}")


        telemetry = Telemetry(
            cpu_usage=data.get('cpu_usage'),
            ram_usage=data.get('ram_usage'),
            disk_free=data.get('disk_free'),
            temperature=data.get('temperature'),
            latency=data.get('latency'),
            connectivity=data.get('connectivity'),
            boot_date=boot_date,
            device_uuid=device_uuid
        )

        db.add(telemetry)
        db.commit()
        db.refresh(telemetry)
        print(f"[INFO] Telemetria salva no DB: id={telemetry.id}, device={telemetry.device_uuid}")
        
    except Exception as e:
        db.rollback()
        print(f"[ERRO FATAL SALVAMENTO] Falha ao salvar telemetria para {device_uuid_str}: {e}")
    finally:
        db.close()

def callback(ch, method, properties, body):
    # Função chamada para cada mensagem da fila
    try:
        message = json.loads(body)
        print(f"[INFO] Mensagem recebida do RabbitMQ: {message}")
        save_telemetry_to_db(message)
    except Exception as e:
        print(f"[ERRO] Falha no callback: {e}")
    finally:
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"[INFO] Mensagem confirmada no RabbitMQ (ACK).")

def start_consumer():
    # Inicia o consumidor com reconexão automática
    while True:
        try:
            print(f"[INFO] Conectando ao RabbitMQ em {RABBITMQ_HOST}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    heartbeat=60,
                    blocked_connection_timeout=300
                )
            )

            channel = connection.channel()
            channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
            channel.basic_qos(prefetch_count=1)
            print(f"[INFO] Conectado ao RabbitMQ. Aguardando mensagens na fila '{RABBITMQ_QUEUE}'...")
            channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
            channel.start_consuming()


        except pika.exceptions.AMQPConnectionError as e:
            print(f"[ERRO] Conexão ao RabbitMQ falhou: {e}. Tentando reconectar em 5s...")
            time.sleep(5)
        except KeyboardInterrupt:
            print("[INFO] Worker encerrado manualmente.")
            try:
                if connection and connection.is_open:
                    connection.close()
            except:
                pass
            break

if __name__ == "__main__":
    start_consumer()
