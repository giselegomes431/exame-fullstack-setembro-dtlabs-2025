from sqlalchemy import Column, Float, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from base import Base

class Device(Base):
    __tablename__ = "devices"
    uuid = Column(UUID(as_uuid=True), primary_key=True)

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, autoincrement=True)
    cpu_usage = Column(Float)
    ram_usage = Column(Float)
    disk_free = Column(Float)
    temperature = Column(Float)
    latency = Column(Integer)
    connectivity = Column(Integer)
    boot_date = Column(DateTime)
    device_uuid = Column(UUID(as_uuid=True), ForeignKey("devices.uuid"))
