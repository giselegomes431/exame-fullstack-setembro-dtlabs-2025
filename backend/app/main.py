from fastapi import FastAPI
import pika
import json

app = FastAPI()


rabbitmq_host = 'rabbitmq'
rabbitmq_queue = 'telemetry_queue'

def connect_to_rabbitmq():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))
        channel = connection.channel()
        channel.queue_declare(queue=rabbitmq_queue, durable=True)
        return connection, channel
    except pika.exceptions.AMQPConnectionError as e:
        print(f"Erro ao conectar com o RabbitMQ: {e}")
        return None, None

# Rota de teste
@app.get("/")
def read_root():
    return {"message": "Bem-vindo ao Backend de Monitoramento de IoT!"}

# Rota dados de telemetria
@app.post("/telemetry")
def receive_telemetry_data(data: dict):
    connection, channel = connect_to_rabbitmq()

    if not connection or not channel:
        return {"status": "error", "message": "Não foi possível conectar ao RabbitMQ."}

    try:
        message_body = json.dumps(data)
        
        # Publica a mensagem na fila
        channel.basic_publish(
            exchange='',  
            routing_key=rabbitmq_queue,
            body=message_body,
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        print(f"Mensagem enviada para a fila: {message_body}")
        return {"status": "success", "message": "Dados de telemetria recebidos e enviados para a fila."}
    
    except Exception as e:
        print(f"Erro ao enviar mensagem para o RabbitMQ: {e}")
        return {"status": "error", "message": "Erro ao processar os dados."}
    finally:
        if connection:
            connection.close()