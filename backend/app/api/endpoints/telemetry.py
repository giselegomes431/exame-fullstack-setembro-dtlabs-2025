# backend/app/api/endpoints/telemetry.py (código corrigido)

from fastapi import APIRouter, HTTPException
from ...services.messaging_service import publish_telemetry_message # <-- Importe o serviço

router = APIRouter()

@router.post("/telemetry")
def receive_telemetry_data(data: dict):
    try:
        publish_telemetry_message(data) # <-- Use a função do serviço
        return {"status": "success", "message": "Dados de telemetria recebidos e enviados para a fila."}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}
    except Exception as e:
        print(f"[ERRO] Falha ao enviar mensagem: {e}")
        return {"status": "error", "message": "Erro interno ao processar os dados."}