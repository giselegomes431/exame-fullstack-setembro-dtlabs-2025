from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ...database.base import get_db
from ...database.models import User
from ...dependencies import get_current_user
from ...core.security import hash_password, verify_password, create_access_token
from pydantic import BaseModel
from datetime import timedelta
import uuid

router = APIRouter()

# --- Modelos Pydantic para validação ---
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    user_id: uuid.UUID
    username: str
    access_token: str
    token_type: str = "bearer"

# --- Endpoints de Autenticação ---
@router.post("/register", tags=["Authentication"])
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = hash_password(user.password)
    
    # Cria o novo usuário
    new_user = User(username=user.username, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

@router.post("/login", response_model=TokenResponse, tags=["Authentication"])
def login(user: UserLogin, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if not existing_user or not verify_password(user.password, existing_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(existing_user.id)},
        expires_delta=access_token_expires
    )
    
    # Retorna o ID, o username e o token na resposta
    return {
        "user_id": existing_user.id,
        "username": existing_user.username,
        "access_token": access_token,
        "token_type": "bearer"
    }