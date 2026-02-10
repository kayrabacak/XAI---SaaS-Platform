"use client";

import { CheckCircle, BarChart3, Download } from "lucide-react";
import styles from "./ResultSection.module.css";
import { useEffect, useState } from "react";
import SimulationPanel from "./SimulationPanel";

interface ResultSectionProps {
    result: any;
}

export default function ResultSection({ result }: ResultSectionProps) {
    // Simple animation trigger for bars
    const [mounted, setMounted] = useState(false);
    useEffect(() => setMounted(true), []);

    return (
        <div className={styles.wrapper}>
            <div className={styles.card}>

                <div className={styles.header}>
                    <div className={styles.headerLeft}>
                        <CheckCircle className="text-green-500" color="#22c55e" size={32} />
                        <div>
                            <h2 className={styles.headerTitle}>Analiz Raporu</h2>
                            <p style={{ color: '#9ca3af' }}>Model ve veri setiniz başarıyla incelendi.</p>
                        </div>
                    </div>

                    <button
                        onClick={() => window.open(`http://localhost:8000/report/${result.id || result.task_id}/download`, '_blank')}
                        className={styles.downloadBtn}
                    >
                        <Download size={18} />
                        <span>Raporu İndir</span>
                    </button>
                </div>

                <div className={styles.grid}>
                    {/* AI Insight Column */}
                    <div>
                        <div className={styles.aiBox}>
                            <h3 className={styles.aiTitle}>
                                <span style={{ width: '24px', height: '4px', background: '#6366f1', display: 'inline-block', borderRadius: '4px' }}></span>
                                Gemini AI Görüşü
                            </h3>
                            <p className={styles.aiText}>
                                {result.ai_explanation || "AI yorumu üretilemedi."}
                            </p>
                        </div>
                    </div>

                    {/* Feature Importance Column */}
                    <div>
                        <div className={styles.chartBox}>
                            <h3 className={styles.chartTitle}>
                                <BarChart3 color="#60a5fa" size={20} />
                                Önemli Faktörler
                            </h3>

                            <div>
                                {Object.entries(result.feature_importance || {}).slice(0, 5).map(([key, value]: any, index) => {
                                    let displayValue = 0;
                                    if (Array.isArray(value)) {
                                        const sum = value.reduce((a: number, b: number) => a + b, 0);
                                        displayValue = sum / value.length;
                                    } else {
                                        displayValue = Number(value);
                                    }

                                    return (
                                        <div key={key} className={styles.barRow}>
                                            <div className={styles.barLabel}>
                                                <span className={styles.barKey}>{key}</span>
                                                <span className={styles.barValue}>{displayValue.toFixed(3)}</span>
                                            </div>
                                            <div className={styles.barTrack}>
                                                <div
                                                    className={styles.barFill}
                                                    style={{ width: mounted ? `${Math.min(displayValue * 100, 100)}%` : '0%' }}
                                                ></div>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>

                {/* What-If Modülü */}
                {result.sample_data && result.sample_data.length > 0 && (
                    <SimulationPanel
                        taskId={result.id || result.task_id}
                        initialData={result.sample_data[0]}
                    />
                )}
            </div>
        </div>
    );
}
