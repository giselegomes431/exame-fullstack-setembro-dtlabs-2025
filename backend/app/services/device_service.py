from sqlalchemy.orm import Session
from ..database.models import Device
from ..api.endpoints.devices import DeviceCreate, DeviceUpdate
from fastapi import HTTPException
import uuid

def create_new_device(db: Session, device: DeviceCreate):
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
    return db.query(Device).all()

def get_device_by_uuid(db: Session, device_uuid: str):
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

def update_existing_device(db: Session, device_uuid: str, device: DeviceUpdate):
    existing_device = get_device_by_uuid(db, device_uuid) # Reutiliza a função de busca
    
    for key, value in device.dict(exclude_unset=True).items():
        setattr(existing_device, key, value)

    db.commit()
    db.refresh(existing_device)
    return existing_device

def delete_existing_device(db: Session, device_uuid: str):
    device = get_device_by_uuid(db, device_uuid) # Reutiliza a função de busca
    db.delete(device)
    db.commit()
    return