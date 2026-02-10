# backend/app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
import os

# Docker-compose içindeki DB bilgileri
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@db:5432/xai_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Tabloları oluştur
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()