# backend/app/database/models.py

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .base import Base

# --- Modelo do Usuário ---
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- Modelo do Dispositivo ---
class Device(Base):
    __tablename__ = "devices"

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    location = Column(String)
    sn = Column(String(12), unique=True, index=True)
    description = Column(String)
    user_id = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- Modelo de Telemetria ---
class Telemetry(Base):
    __tablename__ = 'telemetry'

    id = Column(Integer, primary_key=True, index=True)
    cpu_usage = Column(Float)
    ram_usage = Column(Float)
    disk_free = Column(Float)
    temperature = Column(Float)
    latency = Column(Float)
    connectivity = Column(Integer)
    boot_date = Column(DateTime)