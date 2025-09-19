# backend/app/api/endpoints/notifications.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ...database.base import get_db
from ...database.models import Notification, User
from pydantic import BaseModel, field_validator
from typing import List, Optional
import uuid
from datetime import datetime
from .devices import get_current_user

router = APIRouter()

# Modelos Pydantic para validação
class NotificationCreate(BaseModel):
    device_uuid: Optional[str] = None
    parameter: str
    operator: str = ">"
    threshold: float
    message: str
    
    @field_validator('operator')
    @classmethod
    def validate_operator(cls, v):
        valid_operators = ['>', '<', '==', '!=', '>=', '<=']
        if v not in valid_operators:
            raise ValueError(f'Invalid operator: {v}. Must be one of {valid_operators}')
        return v

class NotificationResponse(BaseModel):
    id: int
    user_id: uuid.UUID
    device_uuid: Optional[uuid.UUID] = None
    parameter: str
    operator: str
    threshold: float
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Rota para criar uma notificação
@router.post("/notifications", response_model=NotificationResponse, tags=["Notifications"])
def create_notification(
    notification: NotificationCreate,
    user: User = Depends(get_current_user), # Rota protegida
    db: Session = Depends(get_db)
):
    new_notification = Notification(
        user_id=user.id,
        device_uuid=notification.device_uuid,
        parameter=notification.parameter,
        operator=notification.operator,
        threshold=notification.threshold,
        message=notification.message
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification

# Rota para listar as notificações de um usuário
@router.get("/notifications", response_model=List[NotificationResponse], tags=["Notifications"])
def get_user_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = db.query(Notification).filter(Notification.user_id == user.id).all()
    return notifications