from sqlalchemy import Column, Integer, String, DateTime, Float
from base import Base

# Modelo de Telemetria
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