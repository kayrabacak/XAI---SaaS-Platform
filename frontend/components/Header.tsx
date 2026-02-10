"use client";

import styles from "./Header.module.css";

export default function Header() {
  return (
    <div className={styles.headerContainer}>
      <div className={styles.titleWrapper}>
        <h1 className={styles.title}>
          XAI SaaS Platform
        </h1>
      </div>
      <p className={styles.subtitle}>
        ML Modellerinizi Sürükleyin, <span className={styles.highlight}>Yapay Zeka</span> Yorumlasın.
      </p>
    </div>
  );
}

