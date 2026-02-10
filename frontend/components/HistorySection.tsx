"use client";

import { useEffect, useState } from "react";
import axios from "axios";
import { Clock, FileText, ArrowRightCircle } from "lucide-react";
import styles from "./HistorySection.module.css";
import { useAuth } from "@clerk/nextjs";

interface AnalysisSummary {
    id: string;
    filename_model: string;
    filename_data: string;
    status: string;
    created_at: string;
}

interface HistorySectionProps {
    onSelectAnalysis: (id: string) => void;
}

export default function HistorySection({ onSelectAnalysis }: HistorySectionProps) {
    const { userId } = useAuth();
    const [history, setHistory] = useState<AnalysisSummary[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (!userId) return;

        const fetchHistory = async () => {
            try {
                const res = await axios.get(`http://localhost:8000/my-analyses?user_id=${userId}`);
                setHistory(res.data);
            } catch (err) {
                console.error("Geçmiş yüklenirken hata:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [userId]);

    if (!userId) return null;

    return (
        <div className={styles.wrapper}>
            <h3 className={styles.title}>
                <Clock className="text-gray-400" size={24} />
                Geçmiş Analizler
            </h3>

            {loading ? (
                <div className={styles.empty}>Yükleniyor...</div>
            ) : history.length === 0 ? (
                <div className={styles.empty}>Henüz hiç analiz yapmadınız.</div>
            ) : (
                <div className={styles.list}>
                    {history.map((item) => (
                        <div
                            key={item.id}
                            className={styles.item}
                            onClick={() => onSelectAnalysis(item.id)}
                            style={{ cursor: "pointer" }}
                            title="Sonuçları görüntülemek için tıklayın"
                        >
                            <div className={styles.itemLeft}>
                                <div className={styles.iconBox}>
                                    <FileText size={20} />
                                </div>
                                <div className={styles.itemDetail}>
                                    <h4>{item.filename_data}</h4>
                                    <p>{new Date(item.created_at).toLocaleDateString("tr-TR")} • {item.filename_model}</p>
                                </div>
                            </div>

                            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                                {item.status === "completed" && (
                                    <span className={`${styles.badge} ${styles.completed}`}>Tamamlandı</span>
                                )}
                                {item.status === "processing" && (
                                    <span className={`${styles.badge} ${styles.processing}`}>İşleniyor</span>
                                )}
                                {item.status === "failed" && (
                                    <span className={`${styles.badge} ${styles.failed}`}>Hata</span>
                                )}

                                <ArrowRightCircle size={20} color="#6b7280" />
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
