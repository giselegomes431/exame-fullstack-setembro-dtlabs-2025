from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Security
from sqlalchemy.orm import Session
from ...database.base import get_db
from ...database.models import Device, User
from pydantic import BaseModel, field_validator
from typing import List
import uuid
from ...dependencies import get_current_user

# Cria um APIRouter para as rotas de dispositivos
router = APIRouter()

# --- Modelos Pydantic para validação ---
class DeviceCreate(BaseModel):
    name: str
    location: str
    sn: str
    description: str
    # Removido o user_id, pois ele será obtido do token.

    @field_validator('sn')
    def sn_must_have_12_digits(cls, v):
        if len(v) != 12 or not v.isdigit():
            raise ValueError('sn must be a 12-digit number')
        return v
    
class DeviceUpdate(BaseModel):
    name: str
    location: str
    description: str

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

# --- Endpoints de Dispositivo (CRUD) ---

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, tags=["Devices"])
def create_device(
    device_data: DeviceCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user) # Obtém o usuário do token
):
    # Verifica se o SN já existe
    existing_device = db.query(Device).filter(Device.sn == device_data.sn).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Serial Number already registered")

    # Cria o novo dispositivo com o user_id do usuário autenticado
    new_device = Device(
        name=device_data.name,
        location=device_data.location,
        sn=device_data.sn,
        description=device_data.description,
        user_id=current_user.id # Usa o UUID do usuário autenticado
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.get("/devices", response_model=List[DeviceResponse], tags=["Devices"])
def get_all_devices(
    user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Apenas os dispositivos do usuário autenticado são retornados
    devices = db.query(Device).filter(Device.user_id == user.id).all()
    return devices

@router.get("/devices/{device_uuid}", response_model=DeviceResponse, tags=["Devices"])
def get_device_by_uuid(
    device_uuid: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not device or device.user_id != current_user.uuid:
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
    if not existing_device or existing_device.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(existing_device)
    db.commit()
    return