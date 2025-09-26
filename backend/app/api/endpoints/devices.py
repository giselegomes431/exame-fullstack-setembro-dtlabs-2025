from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Security
from sqlalchemy.orm import Session
from ...database.base import get_db
from ...database.models import Device, User
from pydantic import BaseModel, field_validator
from typing import List, Optional
import uuid
from .auth import get_current_user  # Importa a função de segurançafrom ...database.models import Telemetry
from ...database.models import Telemetry
from typing import Dict

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
    latest_telemetry = {}
    user_devices = db.query(Device).filter(Device.user_id == user.id).all()

    for device in user_devices:
        latest = db.query(Telemetry).filter(Telemetry.device_uuid == device.uuid).order_by(Telemetry.boot_date.desc()).first()
        if latest:
            latest_telemetry[str(device.uuid)] = latest

    return latest_telemetry

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, tags=["Devices"])
def create_device(
    device_data: DeviceCreate,
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user)  # Obtém o usuário do token
):
    existing_device = db.query(Device).filter(Device.sn == device_data.sn).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Serial Number already registered")

    new_device = Device(
        name=device_data.name,
        location=device_data.location,
        sn=device_data.sn,
        description=device_data.description,
        user_id=current_user.id  # Usa o UUID do usuário autenticado
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.get("/devices", response_model=List[DeviceResponse], tags=["Devices"])
def get_all_devices(
    db: Session = Depends(get_db),
    current_user: User = Security(get_current_user)
):
    devices = db.query(Device).filter(Device.user_id == current_user.id).all()
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
    return

@router.get("/devices/{device_uuid}/historical", response_model=HistoricalDataResponse, tags=["Devices"])
def get_historical_data(
    device_uuid: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    period: str = "last_24h"
):
    # Verifique se o dispositivo existe e pertence ao usuário
    device = db.query(Device).filter(Device.uuid == device_uuid, Device.user_id == current_user.id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found or not owned by user.")

    # Calcule o período de tempo para o filtro
    if period == "last_24h":
        time_limit = datetime.utcnow() - timedelta(hours=24)
    elif period == "last_7d":
        time_limit = datetime.utcnow() - timedelta(days=7)
    elif period == "last_30d":
        time_limit = datetime.utcnow() - timedelta(days=30)
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Use 'last_24h', 'last_7d', or 'last_30d'.")

    # Busque os dados históricos do banco de dados
    historical_telemetry = db.query(Telemetry).filter(
        Telemetry.device_uuid == device_uuid,
        Telemetry.boot_date >= time_limit
    ).order_by(Telemetry.boot_date).all()

    # Formate os dados para o frontend
    timestamps = [t.boot_date for t in historical_telemetry]
    cpu_usage = [t.cpu_usage for t in historical_telemetry]
    ram_usage = [t.ram_usage for t in historical_telemetry]
    temperature = [t.temperature for t in historical_telemetry]

    return {
        "timestamps": timestamps,
        "cpu_usage": cpu_usage,
        "ram_usage": ram_usage,
        "temperature": temperature
    }

