# exame-fullstack-setembro-dtlabs-2025  
### Plataforma de Monitoramento de IoT  

Este projeto é uma avaliação prática para a vaga de **Desenvolvedor(a) Full Stack** na **dtLabs**.  
A aplicação consiste em uma plataforma de monitoramento para dispositivos IoT, com arquitetura baseada em **microsserviços**, **comunicação assíncrona** e **frontend em React**.  

---

## 🚀 Funcionalidades Chave  

- **Simulador de Telemetria** → Script Python que gera dados aleatórios e os envia continuamente para a API de Telemetria, facilitando testes e demonstrações em tempo real.  
- **API de Telemetria** → Recebe dados de heartbeat dos dispositivos.  
- **Comunicação Assíncrona** → Integração com RabbitMQ para envio de dados de telemetria a filas de processamento.  
- **Processamento de Regras** → Serviço worker que consome mensagens, persiste no PostgreSQL e verifica regras de notificação.  
- **Alertas em Tempo Real** → Notificações instantâneas via **Socket.IO (WebSockets)** para o frontend.  
- **Frontend Moderno** → Interface React para visualização de dados, criação de regras e gerenciamento de dispositivos.  

---

## 🏗 Arquitetura  

A arquitetura utiliza **Docker** e é orquestrada pelo `docker-compose.yaml`.  

| Serviço     | Imagem Base / Tipo           | Função Principal                                                    | Portas Mapeadas (Host:Container) |
|-------------|------------------------------|---------------------------------------------------------------------|----------------------------------|
| **backend** | exame-fullstack-set (FastAPI) | API principal: rotas, autenticação e emissão de mensagens           | 8000:8000 |
| **frontend**| exame-fullstack-set (React/Vite) | Interface de usuário (visualização e gerenciamento)                 | 3000:5173 |
| **worker**  | exame-fullstack-set (Python) | Processamento de regras, persistência e alertas via Socket.IO       | Nenhuma (interno) |
| **simulador**| exame-fullstack-set (Python) | Gera dados de telemetria e envia ao backend                         | Nenhuma (interno) |
| **db**      | postgres:13                  | Banco de dados principal (usuários, dispositivos e telemetria)      | 5432:5432 |
| **redis**   | redis:6-alpine               | Cache para otimização de consultas                                  | 6379:6379 |
| **rabbitmq**| rabbitmq:3-management        | Broker de mensagens (RabbitMQ)                                      | 15672:15672 (Interface Web) |
| **pgadmin** | dpage/pgadmin4               | Interface gráfica para PostgreSQL                                   | 5050:80 (padrão) |

---

## 🛠 Tecnologias Utilizadas  

- **Linguagens**: Python 3.10, TypeScript/JavaScript  
- **Frameworks**: FastAPI, React/Vite, Styled Components  
- **Mensageria**: RabbitMQ (via pika)  
- **WebSockets**: Python Socket.IO (integrado ao FastAPI)  
- **Banco de Dados**: PostgreSQL (SQLAlchemy + psycopg2-binary)  
- **Cache**: Redis  
- **Orquestração**: Docker + Docker Compose  

---

## ⚙️ Configuração do Frontend  

Para o frontend se conectar corretamente aos serviços, crie um arquivo **`.env`** na pasta `frontend/` com o conteúdo:  

```env
# frontend/.env
VITE_API_URL=http://localhost:8000
VITE_WEBSOCKET_URL=http://localhost:8000
```

---

## 📘 Documentação da API  

Após iniciar a aplicação, a API oferece documentação interativa:  

| Tipo | Caminho Local |
|------|---------------|
| **Swagger UI (Interativo)** | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Redoc (Estático)**        | [http://localhost:8000/redoc](http://localhost:8000/redoc) |

---

## ▶️ Como Rodar a Aplicação  

### 1. Pré-requisitos  
- Docker instalado  
- Docker Compose instalado  
- Docker Desktop em execução  

### 2. Clonar o Repositório  

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 3. Subir e Acessar (Recomendado)

```bash
# subir containers
docker compose up --build
```

### Acessos e Simulador

- **Frontend:** [http://localhost:5173/](http://localhost:5173/)  
- **Backend:** [http://localhost:8000/](http://localhost:8000/)  

**Credenciais de Teste:**  
- Usuário: `user1_sim`  
- Senha: `pass123`  

⚡ **Simulador:** Após login, inicie manualmente o contêiner `iot_simulator` via Docker Desktop ou CLI.  

📌 **Dica:** Se novos dispositivos ou regras não funcionarem, rode:  
```bash
docker compose up -d --build
```

---
### 4. Verificar e Acessar
- Frontend: [http://localhost:5173/](http://localhost:5173/)   
- Backend API: [http://localhost:8000/](http://localhost:8000/)  
- RabbitMQ Dashboard: [http://localhost:15672/](http://localhost:15672/)  
- pgAdmin: [http://localhost:5050/](http://localhost:5050/)  

Para confirmar os serviços ativos:
```bash
docker compose up -d --build
```

### ⚠️ Troubleshooting
- Problemas com regras ou dispositivos?
Reinicie os contêineres:
```bash
docker compose down && docker compose up -d --build
```
- Simulador não envia dados?
Certifique-se de que o login foi feito e o contêiner iot_simulator está rodando.

- Banco não acessível?
Verifique se a porta 5432 não está em uso localmente.