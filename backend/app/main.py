from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import init_db, get_db
from app.storage import init_bucket, upload_file
from app.worker import analyze_model_task
from app.models import AnalysisResult, Project, User
import uuid
from typing import List
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import joblib
import numpy as np
from app.storage import download_file
from pydantic import BaseModel
from typing import Dict, Any
import os
from fastapi.responses import Response
from xhtml2pdf import pisa
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import io

app = FastAPI(title="XAI-SaaS API (User Entegre)")

# Simülasyon için veri modeli
class SimulationRequest(BaseModel):
    task_id: str
    input_data: Dict[str, Any]
# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    init_bucket()
    init_db()
    print("✅ Sistem Hazır (DB + MinIO + User Support)")

# --- YENİ YARDIMCI: KULLANICIYI BUL VEYA OLUŞTUR ---
def get_or_create_user_context(db: Session, user_id: str):
    """
    Frontend'den gelen user_id ile veritabanında kullanıcıyı bulur.
    Yoksa oluşturur. (SaaS mantığı)
    """
    # 1. Kullanıcıyı Ara
    user = db.query(User).filter(User.id == user_id).first()
    
    # 2. Yoksa Oluştur
    if not user:
        # Clerk'ten sadece ID geliyor, email/isim şimdilik opsiyonel kalsın
        user = User(id=user_id, email=f"{user_id}@clerk.user", full_name="Yeni Kullanıcı")
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"👤 Yeni kullanıcı oluşturuldu: {user_id}")
    
    # 3. Varsayılan Projesini Bul veya Oluştur
    # (İleride kullanıcı proje seçebilecek, şimdilik 'Default Project' atıyoruz)
    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        project = Project(id=str(uuid.uuid4()), name="Varsayılan Projem", owner_id=user.id)
        db.add(project)
        db.commit()
        db.refresh(project)
        
    return project

@app.get("/")
def read_root():
    return {"message": "XAI-SaaS API Ready 🚀"}

@app.post("/upload")
async def upload_model(
    model_file: UploadFile = File(...),
    data_file: UploadFile = File(...),
    user_id: str = Form(...), # <-- YENİ: Frontend'den ID bekliyoruz
    db: Session = Depends(get_db)
):
    print(f"📥 Upload İsteği Geldi - User ID: {user_id}")

    # 1. Kullanıcı ve Proje Bağlamını Getir
    project = get_or_create_user_context(db, user_id)
    
    # 2. ID ve Dosya Yolları
    task_id = str(uuid.uuid4())
    model_path = f"{task_id}/model.pkl"
    data_path = f"{task_id}/data.csv"

    # 3. MinIO'ya Yükle
    if not upload_file(model_file.file, model_path):
        raise HTTPException(500, "Model yüklenemedi")
    if not upload_file(data_file.file, data_path):
        raise HTTPException(500, "Veri yüklenemedi")

    # 4. VERİTABANINA KAYIT (Gerçek Proje ID ile)
    new_analysis = AnalysisResult(
        id=task_id,
        filename_model=model_file.filename,
        filename_data=data_file.filename,
        project_id=project.id, # <-- Artık Demo değil, gerçek proje!
        status="pending"
    )
    db.add(new_analysis)
    db.commit()

    # 5. Celery'yi Tetikle
    analyze_model_task.apply_async(args=[task_id, model_path, data_path], task_id=task_id)

    return {
        "task_id": task_id,
        "celery_task_id": task_id,
        "status": "pending",
        "message": "Analiz gerçek kullanıcı hesabına eklendi."
    }

@app.get("/result/{task_id}")
async def get_result(task_id: str, db: Session = Depends(get_db)):
    record = db.query(AnalysisResult).filter(AnalysisResult.id == task_id).first()

    if not record:
        raise HTTPException(404, "Analiz bulunamadı")
    
    if record.status == "pending" or record.status == "processing":
        return {"status": "processing", "message": "Analiz devam ediyor..."}
    
    if record.status == "failed":
        return {"status": "failed", "error": record.error_message}
    
    return {
        "status": "completed",
        "data": {
            "feature_importance": record.feature_importance,
            "ai_explanation": record.ai_explanation,
            "sample_data": record.sample_data
        }
    }

    # --- YENİ: Response Modeli (Veriyi düzenli göndermek için) ---
class AnalysisSummary(BaseModel):
    id: str
    filename_model: str
    filename_data: str
    status: str
    created_at: datetime
    
    class Config:
        orm_mode = True

@app.get("/my-analyses", response_model=List[AnalysisSummary])
async def get_my_analyses(
    user_id: str,  # Frontend'den user_id'yi query param olarak alacağız (?user_id=...)
    db: Session = Depends(get_db)
):
    """
    Kullanıcının geçmiş analizlerini listeler.
    """
    # 1. Kullanıcıyı bul
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return [] # Henüz kullanıcının kaydı yoksa boş liste dön
    
    # 2. Kullanıcının projesini bul (Şimdilik tek proje var)
    project = db.query(Project).filter(Project.owner_id == user.id).first()
    if not project:
        return []
    
    # 3. O projeye ait analizleri (en yeniden eskiye) getir
    analyses = db.query(AnalysisResult)\
        .filter(AnalysisResult.project_id == project.id)\
        .order_by(AnalysisResult.created_at.desc())\
        .all()
        
    return analyses

@app.post("/simulate")
async def simulate_prediction(request: SimulationRequest):
    """
    Kullanıcının değiştirdiği değerlere göre anlık tahmin yapar (What-If).
    """
    task_id = request.task_id
    
    # Geçici dosya yolları
    local_model_path = f"/tmp/{task_id}_model_sim.pkl"
    # MinIO'daki yolu (task_id klasörünün altında model.pkl var)
    minio_model_path = f"{task_id}/model.pkl" 

    try:
        # 1. Modeli İndir (Eğer tmp'de yoksa)
        # Performans Notu: Prod ortamında bu modelleri RAM'de cachelemek gerekir.
        if not os.path.exists(local_model_path):
            if not download_file(minio_model_path, local_model_path):
                raise HTTPException(status_code=404, detail="Model dosyası bulunamadı.")

        # 2. Modeli Yükle
        model = joblib.load(local_model_path)

        # 3. Veriyi Hazırla (DataFrame'e çevir)
        # Gelen JSON verisini, modelin beklediği formata (DataFrame) çeviriyoruz.
        # Dikkat: Tek bir satır tahmin edeceğiz.
        input_df = pd.DataFrame([request.input_data])
        
        # 4. Tahmin Yap
        # Modelin predict_proba'sı varsa olasılık, yoksa direkt sınıfı dönelim
        if hasattr(model, "predict_proba"):
            prediction = model.predict_proba(input_df)
            # Genelde [0.1, 0.9] gibi döner, biz 1. sınıfın olasılığını alalım veya en yüksek olanı
            result = prediction[0].tolist() # Liste olarak dön
        else:
            prediction = model.predict(input_df)
            result = prediction[0].tolist()

        # Temizlik (İsteğe bağlı, her seferinde indirmemek için silmeyebiliriz ama yer kaplar)
        # os.remove(local_model_path) 

        return {
            "status": "success",
            "prediction": result
        }

    except Exception as e:
        print(f"Simülasyon Hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/report/{task_id}/download")
async def download_report(task_id: str, db: Session = Depends(get_db)):
    """
    Analiz sonucunu PDF formatında indirir.
    """
    # 1. Veriyi Çek
    record = db.query(AnalysisResult).filter(AnalysisResult.id == task_id).first()
    if not record:
        raise HTTPException(404, "Analiz bulunamadı")

    if record.status != "completed":
        raise HTTPException(400, "Analiz henüz tamamlanmamış.")

    # 2. Şablonu Hazırla (Jinja2)
    # backend/templates klasörünü mutlak yol ile bulalım
    import os
    # app/main.py -> backend/app/main.py -> backend/
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(BASE_DIR, "templates")
    
    if not os.path.exists(templates_dir):
        print(f"❌ Şablon klasörü bulunamadı: {templates_dir}")
    
    def normalize_turkish_chars(text: str) -> str:
        if not isinstance(text, str):
            return str(text)
        replacements = {
            "ş": "s", "Ş": "S",
            "ı": "i", "İ": "I",
            "ğ": "g", "Ğ": "G",
            "ü": "u", "Ü": "U",
            "ö": "o", "Ö": "O",
            "ç": "c", "Ç": "C"
        }
        for search, replace in replacements.items():
            text = text.replace(search, replace)
        return text

    try:
        env = Environment(loader=FileSystemLoader(templates_dir))
        template = env.get_template("report.html")

        # 3. Veriyi Hazırla ve Temizle
        feature_importance = record.feature_importance or {}
        sanitized_importance = {}
        
        print("DEBUG: Raw feature_importance:", feature_importance)

        for k, v in feature_importance.items():
            try:
                # Numpy tiplerini temizle ve Türkçe karakterleri düzelt
                key_str = normalize_turkish_chars(str(k))
                if isinstance(v, list):
                    # Liste ise ortalamasını al
                    val = sum(v) / len(v) if len(v) > 0 else 0
                    sanitized_importance[key_str] = float(val)
                else:
                    # Değilse direkt sayıya çevir
                    sanitized_importance[key_str] = float(v)
            except Exception as e:
                print(f"⚠️ Veri temizleme hatası ({k}): {e}")
                sanitized_importance[str(k)] = 0.0

        print("DEBUG: Sanitized importance:", sanitized_importance)

        # 4. Verileri Şablona Göm (Normalize Edilmiş)
        html_content = template.render(
            task_id=record.id,
            date=datetime.now().strftime("%d.%m.%Y %H:%M"),
            filename_model=normalize_turkish_chars(record.filename_model),
            filename_data=normalize_turkish_chars(record.filename_data),
            ai_explanation=normalize_turkish_chars(record.ai_explanation or "AI yorumu bulunamadı."),
            feature_importance=sanitized_importance,
            # font_path parametresini kaldırdık, standart font kullanıyoruz
        )
        print("DEBUG: HTML Render OK")
    except Exception as e:
            print(f"❌ HTML Render Hatası: {e}")
            raise e

    # 5. HTML -> PDF Çevrimi
    pdf_file = io.BytesIO()
    try:
        # pisa.CreatePDF bazen garip hatalar verebilir, loglayalım
        pisa_status = pisa.CreatePDF(io.BytesIO(html_content.encode("utf-8")), dest=pdf_file)
    except Exception as e:
        print(f"❌ pisa.CreatePDF İÇ HATA: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"PDF Motoru Hatası: {str(e)}")

    if pisa_status.err:
        print(f"❌ PDF Oluşturma Hatası (pisa status): {pisa_status.err}")
        raise HTTPException(500, "PDF oluşturulurken hata oluştu.")

    # 5. Dosyayı Gönder
    pdf_file.seek(0)
    headers = {
        'Content-Disposition': f'attachment; filename="Analiz_Raporu_{task_id[:8]}.pdf"'
    }
    return Response(content=pdf_file.read(), media_type="application/pdf", headers=headers)