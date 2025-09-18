from ...core.security import decode_access_token
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi import Security
from sqlalchemy.orm import Session
from ...database.base import get_db
from ...database.models import Device, User
from pydantic import BaseModel, field_validator
from typing import List
import uuid

# Cria um APIRouter para as rotas de dispositivos
router = APIRouter()

# --- Modelos Pydantic para validação ---
class DeviceCreate(BaseModel):
    name: str
    location: str
    sn: str
    description: str
    user_id: str

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
        from_attributes = True # Nome atualizado do Pydantic V2

# --- Endpoints de Dispositivo (CRUD) ---
# **Nota:** Em um passo futuro, essas rotas serão protegidas por autenticação.
# Instancia a dependência que irá extrair o token do header da requisição
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/login")

# Funções de autenticação
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extrai o ID do usuário do payload do token
    user_id = payload.get("sub") 
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Busca o usuário pelo ID
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/devices", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED, tags=["Devices"])
def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    # Verifica se o SN já existe
    existing_device = db.query(Device).filter(Device.sn == device.sn).first()
    if existing_device:
        raise HTTPException(status_code=400, detail="Serial Number already registered")

    # Verifica se o user_id é um UUID válido
    try:
        user_uuid = uuid.UUID(device.user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user_id format")

    # Cria o novo dispositivo no banco
    new_device = Device(**device.dict())
    new_device.user_id = user_uuid
    db.add(new_device)
    db.commit()
    db.refresh(new_device)
    return new_device

@router.get("/devices", response_model=List[DeviceResponse], tags=["Devices"])
def get_all_devices(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Agora só retorna os dispositivos do usuário autenticado
    devices = db.query(Device).filter(Device.user_id == user.id).all()
    return devices

@router.get("/devices/{device_uuid}", response_model=DeviceResponse, tags=["Devices"])
def get_device_by_uuid(device_uuid: str, db: Session = Depends(get_db)):
    device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")
    return device

@router.put("/devices/{device_uuid}", response_model=DeviceResponse, tags=["Devices"])
def update_device(device_uuid: str, device: DeviceUpdate, db: Session = Depends(get_db)):
    existing_device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not existing_device:
        raise HTTPException(status_code=404, detail="Device not found")
        
    for key, value in device.dict(exclude_unset=True).items():
        setattr(existing_device, key, value)
        
    db.commit()
    db.refresh(existing_device)
    return existing_device

@router.delete("/devices/{device_uuid}", status_code=status.HTTP_204_NO_CONTENT, tags=["Devices"])
def delete_device(device_uuid: str, db: Session = Depends(get_db)):
    existing_device = db.query(Device).filter(Device.uuid == device_uuid).first()
    if not existing_device:
        raise HTTPException(status_code=404, detail="Device not found")
    
    db.delete(existing_device)
    db.commit()
    return