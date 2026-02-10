"use client";

import { Loader2, Sparkles } from "lucide-react";
import styles from "./AnalysisButton.module.css";

interface AnalysisButtonProps {
    onClick: () => void;
    loading: boolean;
    disabled: boolean;
}

export default function AnalysisButton({ onClick, loading, disabled }: AnalysisButtonProps) {
    return (
        <div className={styles.wrapper}>
            <button
                onClick={onClick}
                disabled={disabled}
                className={styles.button}
            >
                <span className={styles.content}>
                    {loading ? (
                        <>
                            <Loader2 className={styles.spin} size={24} />
                            <span>Analiz Yapılıyor...</span>
                        </>
                    ) : (
                        <>
                            <Sparkles className={!disabled ? styles.pulse : ""} size={24} />
                            <span>Analizi Başlat</span>
                        </>
                    )}
                </span>
            </button>
        </div>
    );
}
