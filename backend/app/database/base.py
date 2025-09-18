# backend/app/database/base.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from ..core.config import settings
from typing import Generator

# Define o URL do banco de dados a partir das configurações
DATABASE_URL = settings.DATABASE_URL

# Cria a engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Cria a classe base para os modelos do SQLAlchemy
Base = declarative_base()

# Cria uma sessão para interagir com o banco de dados
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Função para obter a sessão do banco de dados (reutilizável)
def get_db() -> Generator:
    """Retorna uma sessão do banco de dados e a fecha após o uso."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para criar todas as tabelas
def create_tables():
    """Cria todas as tabelas definidas nos modelos no banco de dados."""
    Base.metadata.create_all(bind=engine)