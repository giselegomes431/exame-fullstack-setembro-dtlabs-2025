from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from sqlalchemy import func
from ...database.base import get_db
from ...database.models import Device, User
from pydantic import BaseModel, field_validator
from typing import List, Optional
import uuid
from .auth import get_current_user  # Importa a função de segurançafrom ...database.models import Telemetry
from ...database.models import Telemetry
from typing import Dict
from ...services.cache_service import get_cache, set_cache, clear_cache

# Cria um APIRouter para as rotas de dispositivos
router = APIRouter()

# --- Modelos Pydantic para validação ---
class DeviceCreate(BaseModel):
    name: str
    location: str
    sn: str
    description: str
    # O user_id não é necessário aqui, pois será obtido do token.

    @field_validator('sn')
    @classmethod
    def sn_must_have_12_digits(cls, v: str):
        if len(v) != 12 or not v.isdigit():
            raise ValueError('sn must be a 12-digit number')
        return v

class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None

class DeviceResponse(BaseModel):
    uuid: uuid.UUID
    name: str
    location: str
    sn: str
    description: str
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class HistoricalDataResponse(BaseModel):
    timestamps: List[datetime]
    cpu_usage: List[float]
    ram_usage: List[float]
    temperature: List[float]
    
class TelemetryResponse(BaseModel):
    id: int
    cpu_usage: float
    ram_usage: float
    temperature: float
    latency: float
    connectivity: int
    boot_date: datetime
    device_uuid: uuid.UUID

    class Config:
        from_attributes = True

# --- Endpoints de Dispositivo (CRUD) ---
@router.get("/devices/latest-telemetry", response_model=Dict[str, TelemetryResponse], tags=["Devices"])
def get_latest_telemetry(
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    user_id_str = str(user.id)
    cache_key = f"latest_telemetry:{user_id_str}" 
 # 1. Tenta buscar do cache (TTL de 30s)
    cached_data = get_cache(cache_key)
    if cached_data:
        print(f"[CACHE HIT] Última Telemetria para o usuário {user_id_str}")
        return cached_data

# 2. Consulta ao DB
    print(f"[CACHE MISS] Consultando DB por Última Telemetria para o usuário {user_id_str}")
    latest_telemetry = {}
    user_devices = db.query(Device).filter(Device.user_id == user.id).all()


    for device in user_devices:
        latest = db.query(Telemetry).filter(Telemetry.device_uuid == device.uuid).order_by(Telemetry.boot_date.desc()).first()
        if latest:
# Serializa para dicionário antes de salvar no cache
            latest_telemetry[str(device.uuid)] = TelemetryResponse.model_validate(latest).model_dump()

# 3. Cachear o resultado (TTL de 30 segundos)
    set_cache(cache_key, latest_telemetry, ttl_seconds=30)

    return latest_telemetry

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, tags=["Devices"])
def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user) 
):
    existing_device = db.query(Device).filter(Device.sn == device_data.sn).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Serial Number already registered")

    new_device = Device(
        name=device_data.name,
        location=device_data.location,
        sn=device_data.sn,
        description=device_data.description,
        user_id=current_user.id
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)

# INVALIDAÇÃO DE CACHE: A lista de dispositivos mudou.
    clear_cache(f"user_devices:{str(current_user.id)}")

    return new_device

@router.get("/devices", response_model=List[DeviceResponse], tags=["Devices"])
def get_all_devices(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user)
):
    user_id_str = str(current_user.id)
    cache_key = f"user_devices:{user_id_str}"

# 1. Tenta buscar do cache (TTL de 60s)
    cached_devices = get_cache(cache_key)
    if cached_devices:
        print(f"[CACHE HIT] Lista de Dispositivos para o usuário {user_id_str}")
        return cached_devices

# 2. Consulta ao DB
    print(f"[CACHE MISS] Consultando DB por lista de dispositivos para o usuário {user_id_str}")
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()

# 3. Cachear o resultado
    try:
# Converte a lista de objetos Device para lista de dicionários serializáveis
        device_data = [DeviceResponse.model_validate(d).model_dump() for d in devices]
        set_cache(cache_key, device_data, ttl_seconds=60)
    except Exception as e:
        print(f"[ERRO CACHE] Falha ao serializar lista de dispositivos: {e}")

    return devices

@router.get("/devices/{device_uuid}", response_model=DeviceResponse, tags=["Devices"])
def get_device_by_uuid(
    device_uuid: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    # A comparação do user_id deve ser com o id do usuário atual, não com o uuid
    if not device or device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/devices/{device_uuid}", response_model=DeviceResponse, tags=["Devices"])
def update_device(
    device_uuid: str, 
    device_data: DeviceUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_device = db.query(Device).filter(Device.uuid == device_uuid).first()
    # A comparação do user_id deve ser com o id do usuário atual
    if not existing_device or existing_device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")
        
    for key, value in device_data.dict(exclude_unset=True).items():
        setattr(existing_device, key, value)
        
    db.commit()
    db.refresh(existing_device)
    
    clear_cache(f"user_devices:{str(current_user.id)}")
    return existing_device

@router.delete("/devices/{device_uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["Devices"])
def delete_device(
    device_uuid: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    existing_device = db.query(Device).filter(Device.uuid == device_uuid).first()
    # A comparação do user_id deve ser com o id do usuário atual
    if not existing_device or existing_device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(existing_device)
    db.commit()
    
    clear_cache(f"user_devices:{str(current_user.id)}")
    return

@router.get("/devices/{device_uuid}/historical", response_model=HistoricalDataResponse, tags=["Devices"])
def get_historical_data(
    device_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "last_24h"
):
# Cria a chave de cache baseada no dispositivo e no período
    cache_key = f"historical:{device_uuid}:{period}"
    
# 1. Tenta buscar do cache (APENAS para 'last_24h')
    if period == "last_24h":
        cached_data = get_cache(cache_key)
        if cached_data:
            print(f"[CACHE HIT] Histórico 24h para {device_uuid}")
            return cached_data

# Verifique se o dispositivo existe e pertence ao usuário
    device = db.query(Device).filter(Device.uuid == device_uuid, Device.user_id == current_user.id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or not owned by user.")

# Calcule o período de tempo para o filtro
    if period == "last_24h":
        time_limit = datetime.utcnow() - timedelta(hours=24)
        interval_seconds = 60 * 60 # Agrupamento por hora
    elif period == "last_7d":
        time_limit = datetime.utcnow() - timedelta(days=7)
        interval_seconds = 60 * 60 * 12 # Agrupamento por 12 horas
    elif period == "last_30d":
        time_limit = datetime.utcnow() - timedelta(days=30)
        interval_seconds = 60 * 60 * 24 # Agrupamento por 24 horas
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Use 'last_24h', 'last_7d', or 'last_30d'.")

# 2. Busque os dados históricos do banco de dados (usando agregação para eficiência)
    historical_telemetry_raw = db.query(
        func.floor(func.extract("epoch", Telemetry.boot_date) / interval_seconds).label("time_bucket"),
        func.avg(Telemetry.cpu_usage).label("avg_cpu"),
        func.avg(Telemetry.ram_usage).label("avg_ram"),
        func.avg(Telemetry.temperature).label("avg_temp"),
        func.min(Telemetry.boot_date).label("min_date") # Obtém um timestamp representativo
    ).filter(
        Telemetry.device_uuid == uuid.UUID(device_uuid),
        Telemetry.boot_date >= time_limit
    ).group_by("time_bucket").order_by("time_bucket").all()

# Formate os dados para o frontend
    historical_data = {
        "timestamps": [t.min_date for t in historical_telemetry_raw],
        "cpu_usage": [t.avg_cpu for t in historical_telemetry_raw if t.avg_cpu is not None],
        "ram_usage": [t.avg_ram for t in historical_telemetry_raw if t.avg_ram is not None],
        "temperature": [t.avg_temp for t in historical_telemetry_raw if t.avg_temp is not None]
    }

# 3. Cachear o resultado (Apenas se for 'last_24h')
    if period == "last_24h":
        print(f"[CACHE MISS] Salvando Histórico 24h para {device_uuid}")
        set_cache(cache_key, historical_data, ttl_seconds=30)

    return historical_data


