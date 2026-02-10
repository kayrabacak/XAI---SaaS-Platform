import os
import pandas as pd
import shap
import joblib
import numpy as np
import traceback
import google.generativeai as genai
from celery import Celery
from datetime import datetime
from sqlalchemy.orm import Session
from app.storage import download_file
from app.database import SessionLocal
from app.models import AnalysisResult

# Ayarlar
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

celery = Celery(__name__)
celery.conf.broker_url = CELERY_BROKER_URL
celery.conf.result_backend = CELERY_RESULT_BACKEND

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def generate_llm_explanation(importance_dict):
    if not GEMINI_API_KEY:
        return "API Key eksik olduğu için AI yorumu yapılamadı."
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt = f"""
        Sen uzman bir Veri Bilimci ve İş Analistisin.
        Aşağıda bir makine öğrenmesi modelinin "Feature Importance" değerleri var.
        
        Veriler: {importance_dict}
        
        GÖREVİN:
        1. Bu verileri teknik olmayan bir iş yöneticisine özetle.
        2. En önemli 3 etkeni vurgula.
        3. Modelin neye odaklandığını basit, akıcı bir Türkçe ile anlat.
        4. Markdown kullanma, düz paragraf yaz.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"LLM Hatası: {e}")
        return "AI servisine ulaşılamadı."

def update_db_result(task_id: str, data: dict, status: str):
    """Veritabanındaki kaydı günceller"""
    db: Session = SessionLocal()
    try:
        record = db.query(AnalysisResult).filter(AnalysisResult.id == task_id).first()
        if record:
            record.status = status
            if status == "completed":
                record.feature_importance = data.get("feature_importance")
                record.ai_explanation = data.get("ai_explanation")
                record.sample_data = data.get("sample_data")
                record.completed_at = datetime.utcnow()
            elif status == "failed":
                record.error_message = data.get("error")
            
            db.commit()
            print(f"💾 Veritabanı güncellendi: {task_id} -> {status}")
    except Exception as e:
        print(f"DB Kayıt Hatası: {e}")
        db.rollback()
    finally:
        db.close()

@celery.task(name="analyze_model_task")
def analyze_model_task(task_id, model_path, data_path):
    print(f"🔥 Analiz Başlıyor (DB Modu): {task_id}")
    
    # Başlangıçta durumu 'processing' yap
    update_db_result(task_id, {}, "processing")

    local_model = f"/tmp/{task_id}_model.pkl"
    local_data = f"/tmp/{task_id}_data.csv"

    try:
        # 1. İndirme
        if not download_file(model_path, local_model):
            raise Exception("Model indirilemedi")
        if not download_file(data_path, local_data):
            raise Exception("Veri indirilemedi")

        # 2. Yükleme
        df = pd.read_csv(local_data)
        background_data_df = df.select_dtypes(include=[np.number]).iloc[:100]
        background_data = background_data_df.values
        feature_names = background_data_df.columns.tolist()
        model = joblib.load(local_model)

        # 3. SHAP
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(background_data, check_additivity=False)
        except:
            predict_fn = model.predict_proba if hasattr(model, "predict_proba") else model.predict
            explainer = shap.KernelExplainer(predict_fn, background_data)
            shap_values = explainer.shap_values(background_data)

        # 4. Importance Hesaplama
        if isinstance(shap_values, list):
            vals = np.abs(np.array(shap_values)).mean(axis=0).mean(axis=0)
        else:
            vals = np.abs(shap_values).mean(axis=0)

        importance_dict = dict(zip(feature_names, vals.tolist()))
        sorted_importance = dict(sorted(importance_dict.items(), key=lambda item: item[1], reverse=True))
        top_5 = dict(list(sorted_importance.items())[:5])

        # 5. Gemini
        ai_text = generate_llm_explanation(top_5)

        # 6. Başarılı Sonucu DB'ye Yaz
        result_data = {
            "feature_importance": sorted_importance,
            "ai_explanation": ai_text,
            "sample_data": df.head(5).to_dict(orient='records')
        }
        update_db_result(task_id, result_data, "completed")

        # Temizlik
        if os.path.exists(local_model): os.remove(local_model)
        if os.path.exists(local_data): os.remove(local_data)

        return {"status": "completed", "task_id": task_id}

    except Exception as e:
        print("❌ HATA:")
        traceback.print_exc()
        # Hatayı DB'ye Yaz
        update_db_result(task_id, {"error": str(e)}, "failed")
        return {"status": "failed", "error": str(e)}