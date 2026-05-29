# 💰 Dashboard SnapBudget

Dashboard interaktif hasil analisis data sintetis SnapBudget.

## Cara Menjalankan

### 1. Siapkan File
Pastikan semua file berikut berada dalam **satu folder yang sama**:
```
📁 snapbudget-dashboard/
├── app.py
├── requirements.txt
├── ssynthetic_dataset_head1c.csv
├── head2_synthetic_dataset.csv
└── dataset_head3_dirty.csv
```

### 2. Install Dependensi
```bash
pip install -r requirements.txt
```

### 3. Jalankan Dashboard
```bash
streamlit run app.py
```

Browser akan otomatis terbuka di `http://localhost:8501`

---

## Fitur Dashboard

| Halaman | Konten |
|---------|--------|
| 🏠 Ringkasan Eksekutif | KPI cards, chart ringkasan 2 pertanyaan bisnis |
| 📊 PB1 · Pengeluaran Kategori | Bar chart interaktif, pie chart, tabel statistik |
| 🔥 PB2 · Profil & Status | Stacked bar, heatmap, radar chart |
| 📈 Analisis Lanjutan | Tren harian, distribusi profil, klasifikasi teks |
| 🗃️ Eksplorasi Dataset | Preview & statistik deskriptif tiap dataset |

## Dashboard Streamlit Deploy
https://snapbudgetdashboard-app.streamlit.app/

