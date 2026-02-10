"use client";

import { useState } from "react";
import axios from "axios";
import { Play, RotateCcw } from "lucide-react";
import styles from "./SimulationPanel.module.css";

interface SimulationPanelProps {
    taskId: string;
    initialData: any; // Veritabanından gelen örnek veri (ilk satır)
}

export default function SimulationPanel({ taskId, initialData }: SimulationPanelProps) {
    // Başlangıç verisi (Sample data'nın ilk satırını state olarak tutuyoruz)
    const [formData, setFormData] = useState<any>(initialData);
    const [prediction, setPrediction] = useState<any>(null);
    const [loading, setLoading] = useState(false);

    // Input değişince state'i güncelle
    const handleChange = (key: string, value: string) => {
        setFormData((prev: any) => ({
            ...prev,
            [key]: parseFloat(value) || 0 // Sayısal model olduğu için float'a çeviriyoruz
        }));
    };

    // Simülasyon İsteği At
    const handleSimulate = async () => {
        setLoading(true);
        try {
            const res = await axios.post("http://localhost:8000/simulate", {
                task_id: taskId,
                input_data: formData
            });
            setPrediction(res.data.prediction);
        } catch (err) {
            console.error("Simülasyon hatası:", err);
            alert("Simülasyon yapılamadı. Backend loglarına bakın.");
        } finally {
            setLoading(false);
        }
    };

    // Verileri sıfırla
    const handleReset = () => {
        setFormData(initialData);
        setPrediction(null);
    };

    return (
        <div className={styles.panel}>
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <h3>
                        🎛️ What-If Simülasyonu
                    </h3>
                    <p className={styles.subtitle}>Değerleri değiştirin ve sonucun nasıl etkilendiğini görün.</p>
                </div>
                {prediction !== null && (
                    <div className={styles.predictionBox}>
                        <span className={styles.predictionLabel}>Yeni Tahmin:</span>
                        <span className={styles.predictionValue}>
                            {Array.isArray(prediction)
                                ? prediction.map(p => p.toFixed(2)).join(" / ") // Olasılık dönerse
                                : prediction}
                        </span>
                    </div>
                )}
            </div>

            {/* Input Alanları Grid */}
            <div className={styles.grid}>
                {Object.keys(formData).map((key) => (
                    <div key={key} className={styles.inputGroup}>
                        <label className={styles.inputLabel}>
                            {key}
                        </label>
                        <input
                            type="number"
                            value={formData[key]}
                            onChange={(e) => handleChange(key, e.target.value)}
                            className={styles.input}
                        />
                    </div>
                ))}
            </div>

            {/* Aksiyon Butonları */}
            <div className={styles.actions}>
                <button
                    onClick={handleReset}
                    className={styles.resetBtn}
                >
                    <RotateCcw size={16} /> Sıfırla
                </button>
                <button
                    onClick={handleSimulate}
                    disabled={loading}
                    className={styles.simulateBtn}
                >
                    {loading && (
                        <span className={styles.spin}>⏳</span>
                    )}
                    {!loading && <Play size={18} fill="currentColor" />}
                    {loading ? "Hesaplanıyor..." : "Simüle Et"}
                </button>
            </div>
        </div>
    );
}
