# worker/database/base.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
import os

# Define o URL do banco de dados a partir das variáveis de ambiente
DB_HOST = os.environ.get("DB_HOST", "db")
DB_USER = os.environ.get("DB_USER", "testeiotdb")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "iotdb2025")
DB_NAME = os.environ.get("DB_NAME", "iotdb")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}"

# Cria a engine do SQLAlchemy
engine = create_engine(DATABASE_URL)
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Retorna uma sessão do banco de dados e a fecha após o uso."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()