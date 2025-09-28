import requests
import json
import time
import os
import random
from datetime import datetime, timedelta
import uuid

# --- CONFIGURAÇÕES DE AMBIENTE ---
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend_app:8000")
LOGIN_URL = f"{BACKEND_URL}/api/v1/login"
DEVICES_URL = f"{BACKEND_URL}/api/v1/devices"
TELEMETRY_ENDPOINT = f"{BACKEND_URL}/telemetry"

# Credenciais de Teste para o Simulador
SIM_USERNAME = os.environ.get("SIM_USERNAME", "simulador_user")
SIM_PASSWORD = os.environ.get("SIM_PASSWORD", "simulador_pass")

# --- Variáveis Globais de Estado ---
ALL_SIMULATED_DEVICES = []

# --- CONFIGURAÇÃO DE MÚLTIPLOS USUÁRIOS  ---
SIMULATOR_USERS = [
    {"username": SIM_USERNAME, "password": SIM_PASSWORD},
]

def generate_heartbeat(device_uuid: str):
    return {
        # Adicionado random.uniform para gerar valores float para simulação
        "cpu_usage": round(random.uniform(10.0, 95.0), 2), 
        "ram_usage": round(random.uniform(20.0, 85.0), 2),
        "disk_free": round(random.uniform(10.0, 90.0), 2),
        "temperature": round(random.uniform(30.0, 80.0), 2),
        "latency": round(random.uniform(10.0, 150.0), 2),
        "connectivity": random.choice([0, 1]),
        "boot_date": (datetime.utcnow() - timedelta(seconds=random.randint(1, 3600))).isoformat() + "Z", # Simula diferentes tempos de boot
        "device_uuid": device_uuid,
    }

def send_heartbeat(device_uuid: str, token: str):
    # Envia os dados de telemetria para a API
    heartbeat_data = generate_heartbeat(device_uuid)
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(TELEMETRY_ENDPOINT, json=heartbeat_data, headers=headers)
        
        if response.status_code == 200:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] OK: Heartbeat enviado para {device_uuid}")
        elif response.status_code == 401:
             print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRO 401: Token expirado. Tentando refazer login.")
             return False # Sinaliza que o token expirou
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRO: Falha no envio para {device_uuid}. Status: {response.status_code}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ERRO: Falha de conexão com o backend: {e}")
        return False

def login_and_fetch_devices():
    # Faz login para todos os usuários e coleta seus dispositivos e tokens
    global ALL_SIMULATED_DEVICES
    ALL_SIMULATED_DEVICES = []
    
    for sim_user in SIMULATOR_USERS:
        try:
            login_response = requests.post(LOGIN_URL, json={"username": sim_user["username"], "password": sim_user["password"]})
            login_response.raise_for_status()
            
            token = login_response.json().get("access_token")
            
            if not token: continue
                
            headers = {"Authorization": f"Bearer {token}"}
            
            # Buscar Dispositivos
            devices_response = requests.get(DEVICES_URL, headers=headers)
            devices_response.raise_for_status()
            
            # Armazena o UUID do dispositivo e o Token do usuário
            for device in devices_response.json():
                ALL_SIMULATED_DEVICES.append({
                    "uuid": device['uuid'],
                    "token": token
                })
            
            print(f"[INFO] {len(devices_response.json())} dispositivos carregados para {sim_user['username']}.")
            
        except requests.exceptions.RequestException as e:
            print(f"[ERRO] Falha ao processar usuário {sim_user['username']}: {e}")
            
    return len(ALL_SIMULATED_DEVICES) > 0


if __name__ == "__main__":
    if not login_and_fetch_devices():
        print("[CRÍTICO] Nenhuma sessão ativa ou dispositivo encontrado. O Simulador não pode iniciar. Verifique as credenciais.")
        exit(1)

    print(f"[INÍCIO] Simulação rodando para {len(ALL_SIMULATED_DEVICES)} dispositivos. Intervalo: 60s.")
    while True:
        start_time = time.time()
        
        # Envia um heartbeat único para CADA dispositivo
        for device_data in ALL_SIMULATED_DEVICES:
            # Se o envio falhar tenta refazer o login
            if not send_heartbeat(device_data['uuid'], device_data['token']):
                login_and_fetch_devices() # Tenta refazer login e atualizar todos os tokens
                
        elapsed_time = time.time() - start_time
        sleep_duration = 60 - elapsed_time
        
        if sleep_duration > 0:
            time.sleep(sleep_duration)