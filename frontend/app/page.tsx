"use client";

import { useState } from "react";
import axios from "axios";
import { UploadCloud, FileText } from "lucide-react";
// Clerk Importları
import { SignedIn, SignedOut, SignInButton, UserButton, useAuth } from "@clerk/nextjs";

// Senin Componentlerin (Dosya yollarının doğru olduğundan emin ol)
import Header from "../components/Header";
import FileUploader from "../components/FileUploader";
import AnalysisButton from "../components/AnalysisButton";
import ResultSection from "../components/ResultSection";
import HistorySection from "../components/HistorySection";
import styles from "./Home.module.css";

export default function Home() {
  const { userId } = useAuth(); // <-- Kullanıcı ID'sini alıyoruz
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [dataFile, setDataFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<"idle" | "uploading" | "processing" | "completed">("idle");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, type: "model" | "data") => {
    if (e.target.files && e.target.files[0]) {
      type === "model" ? setModelFile(e.target.files[0]) : setDataFile(e.target.files[0]);
    }
  };

  const startAnalysis = async () => {
    if (!modelFile || !dataFile) {
      setError("Lütfen her iki dosyayı da yükleyin.");
      return;
    }
    setLoading(true);
    setError("");
    setStatus("uploading");
    setResult(null);

    const formData = new FormData();
    formData.append("model_file", modelFile);
    formData.append("data_file", dataFile);

    // Eğer kullanıcı giriş yapmışsa ID'sini Backend'e gönder
    if (userId) {
      formData.append("user_id", userId);
    }

    try {
      const uploadRes = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const taskId = uploadRes.data.celery_task_id;
      setStatus("processing");

      // Polling for results
      const interval = setInterval(async () => {
        try {
          const resultRes = await axios.get(`http://localhost:8000/result/${taskId}`);

          if (resultRes.data.status === "completed") {
            clearInterval(interval);
            setResult({ ...resultRes.data.data, id: taskId });
            setStatus("completed");
            setLoading(false);
          } else if (resultRes.data.status === "failed") {
            clearInterval(interval);
            setError("Analiz hatası: " + resultRes.data.error);
            setLoading(false);
            setStatus("idle");
          }
        } catch (err) {
          console.error(err);
        }
      }, 2000);

    } catch (err) {
      setError("Bağlantı hatası! Backend çalışıyor mu?");
      setLoading(false);
      setStatus("idle");
    }
  };

  return (
    <main className="min-h-screen p-6 bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white" style={{ minHeight: '100vh', padding: '1.5rem', background: 'linear-gradient(to bottom right, #111827, #1f2937, #000000)', color: 'white' }}>
      <div className="container mx-auto max-w-5xl" style={{ maxWidth: '64rem', margin: '0 auto' }}>

        {/* --- 1. ÜST BAR (Giriş/Profil Butonu) --- */}
        <div className={styles.topBar}>
          <div className={styles.authContainer}>
            <SignedOut>
              <SignInButton mode="modal">
                <button className={styles.loginLink}>
                  Giriş Yap / Kayıt Ol
                </button>
              </SignInButton>
            </SignedOut>
            <SignedIn>
              <div className="flex items-center gap-3" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span className={styles.accountLabel}>Hesabım</span>
                <UserButton afterSignOutUrl="/" />
              </div>
            </SignedIn>
          </div>
        </div>

        {/* --- 2. BAŞLIK --- */}
        <Header />

        {/* --- 3. GİRİŞ YAPMAMIŞSA GÖSTERİLECEK UYARI --- */}
        <SignedOut>
          <div className={styles.ctaBox}>
            <h3 className={styles.ctaTitle}>Devam Etmek İçin Giriş Yapın</h3>
            <p className={styles.ctaText}>
              Analizlerinizi kaydetmek ve AI raporlarına erişmek için ücretsiz hesabınızı oluşturun.
            </p>
            <SignInButton mode="modal">
              <button className={styles.ctaButton}>
                Hemen Başla 🚀
              </button>
            </SignInButton>
          </div>
        </SignedOut>

        {/* --- 4. GİRİŞ YAPMIŞSA GÖSTERİLECEK UYGULAMA --- */}
        <SignedIn>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '2rem', marginBottom: '3rem', marginTop: '2rem' }}>
            <FileUploader
              label="Model Dosyası (.pkl)"
              subLabel="Scikit-learn modeli"
              accept=".pkl"
              icon={UploadCloud}
              onChange={(e: any) => handleFileChange(e, "model")}
              file={modelFile}
              color="blue"
            />

            <FileUploader
              label="Veri Seti (.csv)"
              subLabel="Analiz edilecek veriler"
              accept=".csv"
              icon={FileText}
              onChange={(e: any) => handleFileChange(e, "data")}
              file={dataFile}
              color="purple"
            />
          </div>

          <AnalysisButton
            onClick={startAnalysis}
            loading={loading}
            disabled={loading || status === "processing"}
          />

          {error && (
            <div className={styles.errorBox}>
              {error}
            </div>
          )}

          {status === "processing" && (
            <div className={styles.processingBox}>
              <p className={styles.processingText}>
                🤖 Yapay zeka modeli inceliyor...
              </p>
              <p className={styles.processingSubtext}>Bu işlem veri boyutuna göre biraz zaman alabilir.</p>
            </div>
          )}

          {status === "completed" && result && (
            <div id="result-section">
              <ResultSection result={result} />
            </div>
          )}

          <HistorySection onSelectAnalysis={async (id) => {
            setLoading(true);
            try {
              const res = await axios.get(`http://localhost:8000/result/${id}`);
              if (res.data.status === "completed") {
                setResult({ ...res.data.data, id: id });
                setStatus("completed");
                // Scroll to result
                setTimeout(() => {
                  document.getElementById("result-section")?.scrollIntoView({ behavior: "smooth" });
                }, 100);
              } else {
                setError("Bu analiz henüz tamamlanmamış veya hatalı.");
              }
            } catch (err) {
              setError("Analiz detayları getirilemedi.");
            } finally {
              setLoading(false);
            }
          }} />
        </SignedIn>

      </div>
    </main>
  );
}