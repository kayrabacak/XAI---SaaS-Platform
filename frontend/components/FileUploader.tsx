"use client";

import { LucideIcon, CheckCircle2 } from "lucide-react";
import { ChangeEvent } from "react";
import styles from "./FileUploader.module.css";

interface FileUploaderProps {
    label: string;
    subLabel?: string;
    accept: string;
    icon: LucideIcon;
    onChange: (e: ChangeEvent<HTMLInputElement>) => void;
    file: File | null;
    color: "blue" | "purple";
}

export default function FileUploader({
    label,
    subLabel,
    accept,
    icon: Icon,
    onChange,
    file,
    color
}: FileUploaderProps) {

    const isSelected = !!file;

    // Dynamically construct class names based on state
    let containerClass = styles.container;
    if (isSelected) {
        containerClass += ` ${color === 'blue' ? styles.activeBlue : styles.activePurple}`;
    } else {
        containerClass += ` ${color === 'blue' ? styles.blueBorder : styles.purpleBorder}`;
    }

    const btnClass = color === 'blue' ? styles.btnBlue : styles.btnPurple;
    const iconColor = color === 'blue' ? "#60a5fa" : "#c084fc";

    return (
        <div className={containerClass}>
            <div className={styles.content}>
                <div className={styles.flexRow}>
                    <div className={styles.iconWrapper}>
                        {isSelected ? (
                            <CheckCircle2 color={iconColor} size={32} />
                        ) : (
                            <Icon color={iconColor} size={32} />
                        )}
                    </div>

                    <div className={styles.textGroup}>
                        <h3 className={styles.label}>{label}</h3>
                        <p className={styles.subLabel}>{file ? file.name : subLabel || "Dosya seçilmedi"}</p>

                        <label>
                            <input
                                type="file"
                                accept={accept}
                                onChange={onChange}
                                className={styles.input}
                            />
                            <span className={`${styles.button} ${btnClass}`}>
                                {file ? "Değiştir" : "Dosya Seç"}
                            </span>
                        </label>
                    </div>
                </div>
            </div>
        </div>
    );
}
