# exame-fullstack-setembro-dtlabs-2025

# Plataforma de Monitoramento de IoT  

Este projeto é uma avaliação prática para a vaga de **Desenvolvedor(a) Full Stack** na **dtLabs**.  
A aplicação consiste em uma plataforma de monitoramento para dispositivos de IoT, com **backend em Python** e uma arquitetura baseada em **microsserviços** e **comunicação assíncrona**.  

---

## 🚀 Funcionalidades  

- **API de Telemetria** → Recebe os dados de *heartbeat* dos dispositivos.  
- **Comunicação Assíncrona** → Envia os dados de telemetria para uma fila no **RabbitMQ**.  
- **Processamento de Dados** → Um serviço *worker* consome mensagens da fila e salva no **PostgreSQL**.  

---

## 🏗 Arquitetura  

A arquitetura é baseada em contêineres **Docker**, orquestrados pelo `docker-compose.yaml`.  

- `backend/` → Código da API em Python (**FastAPI**) responsável por receber dados e publicar mensagens.  
- `worker/` → Serviço em Python que consome mensagens do **RabbitMQ** e persiste no **PostgreSQL**.  
- `db/` → Banco de dados **PostgreSQL**.  
- `rabbitmq/` → Mensageria para entrega assíncrona.  
- `redis/` → Cache (planejado para uso futuro).  

---

## 🛠 Tecnologias Utilizadas  

- **Linguagem**: Python 3.10  
- **Framework**: FastAPI  
- **Mensageria**: RabbitMQ (via `pika`)  
- **Banco de Dados**: PostgreSQL (via `SQLAlchemy` e `psycopg2-binary`)  
- **Cache**: Redis  
- **Orquestração**: Docker + Docker Compose  

---

## ▶️ Como Rodar a Aplicação  

### 1. Pré-requisitos  
- [Docker](https://docs.docker.com/get-docker/) instalado  
- [Docker Compose](https://docs.docker.com/compose/install/) instalado  
- Docker Desktop em execução  

---

### 2. Clonar o Repositório  
```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 3. Subir os Contêineres

Na raiz do projeto (onde está o docker-compose.yaml):
```bash
docker compose up --build
```

### 4. Verificar os Contêineres

Confirme se todos os serviços estão rodando:
```bash
docker ps
```
