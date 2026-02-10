# XAI - SaaS Platform

**XAI (Explainable AI) tabanlı, veri analizi ve raporlama platformu.**

Bu proje, kullanıcıların CSV/Excel verilerini yükleyerek analiz etmelerini, görselleştirmelerini ve yapay zeka destekli içgörüler elde etmelerini sağlayan modern bir SaaS çözümüdür. Ayrıca analiz sonuçlarını profesyonel PDF raporları olarak indirebilirsiniz.


## 🚀 Özellikler

- **Veri Yükleme:** CSV ve Excel dosyalarını kolayca yükleyin.
- **Otomatik Analiz:** Veri setinizdeki eksik değerleri, istatistikleri ve korelasyonları otomatik olarak analiz eder.
- **Yapay Zeka İçgörüleri:** Seçilen AI modeli (Claude, GPT-4, Llama vb.) ile verileriniz hakkında derinlemesine yorumlar ve stratejik öneriler alın.
- **İnteraktif Grafikler:** Verilerinizi dinamik grafikler (Bar, Line, Scatter, Pie) ile görselleştirin.
- **Simülasyon Modu:** "What-if" senaryoları ile farklı parametrelerin sonuçları nasıl etkileyeceğini simüle edin.
- **PDF Raporlama:** Tüm analizleri, grafikleri ve AI yorumlarını içeren kapsamlı bir PDF raporu oluşturun ve indirin.
- **Kullanıcı Yönetimi:** Clerk ile güvenli kullanıcı girişi ve üyelik yönetimi.
- **Modern Arayüz:** Next.js ve Glassmorphism tasarımı ile şık ve kullanıcı dostu bir deneyim.

## 🛠️ Teknolojiler

### Frontend
- **Framework:** [Next.js 14](https://nextjs.org/) (App Directory)
- **Dil:** TypeScript / JavaScript
- **Stil:** CSS Modules (Modern ve modüler stil yapısı)
- **Grafikler:** Recharts
- **Kimlik Doğrulama:** Clerk
- **İkonlar:** Lucide React

### Backend
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Dil:** Python 3.10+
- **Veri Analizi:** Pandas, NumPy
- **PDF Oluşturma:** ReportLab / WeasyPrint
- **Veritabanı:** PostgreSQL (SQLAlchemy)
- **AI Entegrasyonu:** LangChain / OpenAI / Anthropic / Ollama

### Altyapı
- **Containerization:** Docker & Docker Compose

## 📦 Kurulum ve Çalıştırma

Projenin en kolay kurulum yöntemi Docker kullanmaktır.

### Yöntem 1: Docker ile Kurulum (Önerilen)

1. Repoyu klonlayın:
   ```bash
   git clone https://github.com/kayrabacak/XAI---SaaS-Platform.git
   cd XAI---SaaS-Platform
   ```

2. Gerekli `.env` dosyalarını oluşturun:
   - Ana dizinde `.env` (Veritabanı ve genel ayarlar için)
   - `frontend` klasöründe `.env.local` (Next.js ve Clerk ayarları için)

3. Docker Compose ile başlatın:
   ```bash
   docker-compose up --build
   ```
   
4. Tarayıcıda açın:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### Yöntem 2: Manuel Kurulum

**Backend:**
```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📝 Ortam Değişkenleri (.env)

Projenin çalışması için aşağıdaki değişkenlerin ayarlanması gerekir.

**Ana Dizin (`.env`):**
```ini
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=xai_db
DATABASE_URL=postgresql://user:password@db:5432/xai_db
SECRET_KEY=supersecretkey
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Frontend (`frontend/.env.local`):**
```ini
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
CLERK_SECRET_KEY=sk_test_...
NEXT_PUBLIC_API_URL=http://localhost:8000
```
