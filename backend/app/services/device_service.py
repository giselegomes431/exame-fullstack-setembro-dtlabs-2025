# backend/app/services/device_service.py

from sqlalchemy.orm import Session
from ..database.models import Device
from ..api.endpoints.devices import DeviceCreate, DeviceUpdate # Importa os modelos Pydantic
from fastapi import HTTPException
import uuid

def create_new_device(db: Session, device: DeviceCreate):
    """Cria um novo dispositivo no banco de dados."""
    # Garante que o SN é único
    existing_device = db.query(Device).filter(Device.sn == device.sn).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Serial Number already registered")

    # Garante que o user_id é um UUID válido
    try:
        user_uuid = uuid.UUID(device.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    new_device = Device(
        name=device.name,
        location=device.location,
        sn=device.sn,
        description=device.description,
        user_id=user_uuid
    )
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

def get_all_devices(db: Session):
    """Retorna todos os dispositivos do banco de dados."""
    return db.query(Device).all()

def get_device_by_uuid(db: Session, device_uuid: str):
    """Busca um dispositivo por UUID."""
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

def update_existing_device(db: Session, device_uuid: str, device: DeviceUpdate):
    """Atualiza um dispositivo existente."""
    existing_device = get_device_by_uuid(db, device_uuid) # Reutiliza a função de busca
    
    for key, value in device.dict(exclude_unset=True).items():
        setattr(existing_device, key, value)

    db.commit()
    db.refresh(existing_device)
    return existing_device

def delete_existing_device(db: Session, device_uuid: str):
    """Deleta um dispositivo por UUID."""
    device = get_device_by_uuid(db, device_uuid) # Reutiliza a função de busca
    db.delete(device)
    db.commit()
    return