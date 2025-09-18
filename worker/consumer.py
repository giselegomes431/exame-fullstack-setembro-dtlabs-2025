import json
import pika
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker

# Banco de Dados
DATABASE_URL = "postgresql://testeiotdb:iotdb2025@db:5432/iotdb"

# SQLAlchemy
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Modelos de Dados
class Telemetry(Base):
    __tablename__ = 'telemetry'

    id = Column(Integer, primary_key=True, index=True)
    cpu_usage = Column(Float)
    ram_usage = Column(Float)
    disk_free = Column(Float)
    temperature = Column(Float)
    latency = Column(Float)
    connectivity = Column(Integer)
    boot_date = Column(DateTime)
    
# Cria a tabela no banco 
Base.metadata.create_all(bind=engine)

# Cria a sessão para interagir com o banco
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# RabbitMQ
rabbitmq_host = 'rabbitmq'
rabbitmq_queue = 'telemetry_queue'

# Salva os dados de telemetria
def save_telemetry_to_db(telemetry_data):
    db = SessionLocal()
    try:
        new_telemetry = Telemetry(
            cpu_usage=telemetry_data.get('cpu_usage'),
            ram_usage=telemetry_data.get('ram_usage'),
            disk_free=telemetry_data.get('disk_free'),
            temperature=telemetry_data.get('temperature'),
            latency=telemetry_data.get('latency'),
            connectivity=telemetry_data.get('connectivity'),
            boot_date=telemetry_data.get('boot_date')
        )
 
        db.add(new_telemetry)
        db.commit()
        print(f"Dados de telemetria salvos: {telemetry_data}")
    except Exception as e:
        db.rollback()
        print(f"Erro ao salvar no banco de dados: {e}")
    finally:
        db.close()

# Quando uma mensagem chega na fila
def callback(ch, method, properties, body):
    print(f" [x] Recebido: {body.decode()}")
    telemetry_data = json.loads(body)
    save_telemetry_to_db(telemetry_data)
    ch.basic_ack(delivery_tag=method.delivery_tag)

# Inicia o consumidor
def start_consuming():
    connection = None
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue=rabbitmq_queue, durable=True)
        print(' [*] Aguardando mensagens. Para sair, pressione CTRL+C')
        
        # Consume as mensagens da fila
        channel.basic_consume(
            queue=rabbitmq_queue,
            on_message_callback=callback
        )
        channel.start_consuming()
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Erro ao conectar com o RabbitMQ: {e}. O Worker irá tentar novamente em alguns segundos.")
        # Lógica de retentativa - futuro
    except KeyboardInterrupt:
        print('Encerrando...')
    finally:
        if connection and connection.is_open:
            connection.close()

if __name__ == '__main__':
    start_consuming()