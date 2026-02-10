from sqlalchemy import Column, String, Integer, JSON, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

# 1. KULLANICI TABLOSU
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Clerk'ten gelen ID'yi kullanacağız
    email = Column(String, unique=True, index=True)
    full_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişki: Bir kullanıcının birden fazla projesi olabilir
    projects = relationship("Project", back_populates="owner")


# 2. PROJE TABLOSU
class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, index=True) # Örn: "Kredi Risk Analizi"
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # İlişki: Bu proje kime ait?
    owner_id = Column(String, ForeignKey("users.id"))
    owner = relationship("User", back_populates="projects")
    
    # İlişki: Bir projenin içinde birden fazla analiz olabilir
    analyses = relationship("AnalysisResult", back_populates="project")


# 3. ANALİZ SONUÇLARI TABLOSU (Gelişmiş Versiyon)
class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(String, primary_key=True, index=True) # Task ID
    
    # Dosya yolları
    filename_model = Column(String)
    filename_data = Column(String)
    
    # Durum
    status = Column(String, default="pending") # pending, processing, completed, failed
    
    # Zamanlar
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Sonuç Verileri (Gelecekte buraya yeni metrikler eklenebilir, JSON esnektir)
    feature_importance = Column(JSON, nullable=True)
    ai_explanation = Column(Text, nullable=True)
    sample_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # İlişki: Bu analiz hangi projeye ait?
    project_id = Column(String, ForeignKey("projects.id"))
    project = relationship("Project", back_populates="analyses")