# Data Dictionary - SnapBudget Datasets
**Versi:** 2.0 | **Proyek:** SnapBudget · CC26-PSU098

Dokumen ini memuat kamus data (Data Dictionary) lengkap untuk ketiga
dataset yang digunakan dalam ekosistem aplikasi **SnapBudget**.

---

## 1. Data Dictionary — Dataset 1 (Klasifikasi Item Transaksi)

**Deskripsi Dataset:**
Dataset ini memuat teks nama item transaksi keuangan beserta label
kategorinya. Digunakan untuk melatih model AI *Natural Language
Processing* (NLP) agar dapat mengklasifikasikan teks item struk secara
otomatis ke dalam 8 kategori pengeluaran.

**Sumber Data:**
- **CORD-v1** (Hugging Face) → foto struk restoran Indonesia nyata
- **Synthetic Dataset** → data sintetis buatan tim AI

**Statistik Dataset:**

| Keterangan | Nilai |
|---|---|
| Jumlah baris (gabungan) | ~10.000+ baris |
| Jumlah kolom | 3 kolom |
| Jumlah kelas | 8 kategori |
| Format | CSV |

**Skema Kolom:**

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Fungsi |
|:---|:---|:---|:---|
| `text` | `String` | `"Nasi Campur Bali"`, `"Cappuccino"` | Teks asli nama item dari struk transaksi. Ini adalah fitur **Input (X)** utama untuk model NLP. |
| `label_id` | `Integer` | `0`, `1`, `7` | Kode angka yang mewakili kategori transaksi. Ini adalah **Target Output (Y)** dalam bentuk numerik. |
| `category` | `String` | `"makanan"`, `"minuman"` | Nama kategori dalam bentuk teks (representasi dari `label_id`). |

**Mapping Label:**

| `label_id` | `category` | Contoh Item |
|:---:|:---|:---|
| 0 | makanan | Nasi Goreng, Ayam Bakar, Burger |
| 1 | minuman | Kopi, Boba, Jus Mangga |
| 2 | transportasi | Grab, Bensin, Parkir |
| 3 | belanja | Sabun, Deterjen, Kaos |
| 4 | tagihan | Listrik, BPJS, Internet |
| 5 | hiburan | Bioskop, Karaoke, Gym |
| 6 | kesehatan | Obat, Vitamin, Konsultasi Dokter |
| 7 | lain_lain | Parkir, Sumbangan, Lainnya |

**Panduan untuk Training Model:**
- **Input (X):** Kolom `text` → diubah menjadi TF-IDF atau word embeddings
- **Target Output (Y):** Kolom `label_id` → klasifikasi multikelas (8 kelas)
- **Catatan:** Kolom `category` dihapus saat training karena merupakan
  representasi string dari `label_id`

---

## 2. Data Dictionary — Dataset 2 (Prediksi Arus Kas 7 Hari)

**Deskripsi Dataset:**
Dataset ini berisi simulasi pengeluaran harian mahasiswa selama 90 hari
untuk 150 user sintetis. Menggunakan teknik *sliding window* (30 hari
input → 7 hari target) untuk menghasilkan sampel training model
*Time-Series Forecasting* berbasis GRU.

**Sumber Data:** Sintetis (generated oleh tim AI)

**Statistik Dataset:**

| Keterangan | Nilai |
|---|---|
| Jumlah user | 150 user |
| Periode per user | 90 hari |
| Jumlah sampel (sliding window) | ~7.950 sampel |
| Window input | 30 hari |
| Window target | 7 hari |
| Jumlah kategori | 8 kategori |
| Satuan nilai | Ribuan Rupiah (Rp) |
| Format | Array 3D NumPy |

**Skema Data (Format Flat CSV untuk Referensi):**

| Nama Kolom | Tipe Data | Contoh Nilai | Keterangan / Logika Pembentukan Data |
|:---|:---|:---|:---|
| `sample_id` | `Integer` | `0`, `1`, `2` | ID unik satu rangkaian waktu (satu sliding window). |
| `day_relative` | `Integer` | `1` s.d. `37` | Urutan hari (1-30 = input historis, 31-37 = target prediksi). |
| `is_prediction_target` | `Boolean` | `False`, `True` | `False` = data historis (input), `True` = 7 hari ke depan (target). |
| `makanan` | `Float` | `45.84`, `32.08` | Pengeluaran makanan (Rp ribu). Harian, stabil 70%-140% budget dasar. |
| `minuman` | `Float` | `12.75`, `0.00` | Pengeluaran minuman (Rp ribu). Peluang muncul 80%/hari, fluktuasi 50%-150%. |
| `transportasi` | `Float` | `13.96`, `22.03` | Pengeluaran transportasi (Rp ribu). Weekday 85%, weekend 40%. |
| `belanja` | `Float` | `0.00`, `69.13` | Pengeluaran belanja (Rp ribu). Peluang 35%/hari, nilai 2-8× lipat saat muncul. |
| `tagihan` | `Float` | `0.00`, `219.25` | Pembayaran tagihan (Rp ribu). Spike besar di awal bulan (tgl 1-7), 0 di sisa bulan. |
| `hiburan` | `Float` | `0.00`, `48.50` | Pengeluaran hiburan (Rp ribu). Weekend 55%, weekday 10%, nilai 2-6× budget. |
| `kesehatan` | `Float` | `157.65`, `0.00` | Pengeluaran kesehatan (Rp ribu). Sporadis (~8%/hari), nilai besar saat muncul. |
| `lain_lain` | `Float` | `0.00`, `9.81` | Pengeluaran lain-lain (Rp ribu). Acak ~25%/hari, nilai kecil. |

**Profil User Sintetis:**

| Profil | Proporsi | Multiplier Pengeluaran |
|:---|:---:|:---|
| Hemat | 25% | 40% – 70% dari budget dasar |
| Normal | 50% | 70% – 110% dari budget dasar |
| Boros | 25% | 110% – 160% dari budget dasar |

**Panduan untuk Training Model:**
- **Input (X):** Baris dengan `is_prediction_target == False` → shape `(n_sampel, 30, 8)`
- **Target (Y):** Baris dengan `is_prediction_target == True` → shape `(n_sampel, 7, 8)`
- **Pra-pemrosesan:** Normalisasi MinMaxScaler per kategori (fit dari X saja, hindari data leakage)
- **Model:** GRU (Gated Recurrent Unit) dengan arsitektur MLP Encoder + Stacked GRU + Multi-Step Decoder

---

## 3. Data Dictionary — Dataset 3 (Klasifikasi Status Keuangan)

**Deskripsi Dataset:**
Dataset numerik terstruktur berisi kalkulasi analitik kondisi keuangan
mahasiswa. Digunakan untuk melatih model klasifikasi MLP multi-head
yang mendiagnosis status keuangan per kategori maupun secara keseluruhan.

**Sumber Data:** Sintetis (generated oleh tim AI)

**Statistik Dataset:**

| Keterangan | Nilai |
|---|---|
| Jumlah sampel | 8.000 baris |
| Jumlah fitur input | 42 fitur |
| Jumlah kolom total | 53 kolom |
| Jumlah kelas output | 5 kelas |
| Format | CSV |

**Mapping Label Status:**

| `label_id` | `label_name` | Rasio Proyeksi/Budget | Arti |
|:---:|:---|:---:|:---|
| 0 | HEMAT | < 50% | Pengeluaran sangat terkontrol |
| 1 | AMAN | 50% – 85% | Pengeluaran dalam batas wajar |
| 2 | WASPADA | 85% – 105% | Mendekati batas budget |
| 3 | BOROS | 105% – 130% | Melebihi budget |
| 4 | DARURAT | > 130% | Krisis keuangan |

**Skema Kolom — Fitur per Kategori (×8 kategori):**

*Pola: `[kategori]` = makanan / minuman / transportasi / belanja /
tagihan / hiburan / kesehatan / lain_lain*

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Fungsi |
|:---|:---|:---|:---|
| `[kategori]_pct_used` | `Float` | `0.412`, `0.250` | **Persentase Terpakai.** Rasio pengeluaran aktual terhadap budget kategori hingga hari ini. Nilai 1.0 = 100% budget sudah habis. |
| `[kategori]_pred_vs_sisa` | `Float` | `0.264`, `0.453` | **Prediksi vs Sisa Budget.** Perbandingan prediksi pengeluaran 7 hari ke depan dengan sisa budget. Nilai > 1.0 = prediksi melebihi sisa. |
| `[kategori]_proj_pct` | `Float` | `0.727`, `1.501` | **Proyeksi Akhir Bulan.** Estimasi total pemakaian budget di akhir bulan. Nilai > 1.0 = akan melebihi budget. |
| `[kategori]_daily_avg` | `Float` | `0.850`, `1.200` | **Rata-rata Harian (Normalized).** Rasio pengeluaran harian rata-rata terhadap target harian ideal. Khusus tagihan nilainya selalu 0.0 (lump sum). |

**Skema Kolom — Fitur Global:**

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Fungsi |
|:---|:---|:---|:---|
| `days_remaining` | `Float` | `0.433`, `0.833` | **Sisa Hari (Normalized).** Rasio hari tersisa dalam bulan (nilai 1.0 = awal bulan, 0.0 = akhir bulan). |
| `saldo_pct` | `Float` | `0.502`, `0.669` | **Persentase Saldo.** Rasio saldo tersisa terhadap total budget bulanan. |
| `proj_overall_pct` | `Float` | `0.810`, `1.418` | **Proyeksi Keseluruhan.** Estimasi total pemakaian semua kategori di akhir bulan. |
| `total_pred7d_pct` | `Float` | `0.156`, `0.323` | **Prediksi 7 Hari (Normalized).** Rasio total prediksi pengeluaran 7 hari terhadap total budget. |
| `profile` | `Float` | `0.0`, `0.5`, `1.0` | **Profil Pengguna.** Estimasi profil finansial (0.0=Hemat, 0.5=Normal, 1.0=Boros). |

**Skema Kolom — Fitur Engineering Tambahan:**

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Fungsi |
|:---|:---|:---|:---|
| `n_kategori_over_budget` | `Float` | `0.125`, `0.500` | **Proporsi Kategori Melebihi Budget.** Rasio jumlah kategori yang sudah melampaui budget (nilai 0.5 = 4 dari 8 kategori over budget). |
| `max_rasio_kategori` | `Float` | `0.850`, `1.620` | **Rasio Tertinggi.** Nilai rasio aktual/budget tertinggi di antara semua kategori. |
| `mean_rasio_kategori` | `Float` | `0.412`, `0.980` | **Rata-rata Rasio.** Rata-rata rasio aktual/budget di semua kategori. |
| `saldo_cukup_7hari` | `Float` | `0.0`, `1.0` | **Kecukupan Saldo.** Indikator biner apakah saldo saat ini cukup menutup prediksi 7 hari (1.0=cukup, 0.0=tidak cukup). |
| `budget_per_hari_tersisa` | `Float` | `0.042`, `0.185` | **Budget Harian Tersisa.** Rasio sisa budget terhadap jumlah hari yang masih tersisa dalam bulan. |
| `proporsi_kebutuhan_pokok` | `Float` | `0.450`, `0.720` | **Proporsi Kebutuhan Pokok.** Rasio pengeluaran makanan + transportasi terhadap total pengeluaran (indikator prioritas kebutuhan dasar). |

**Skema Kolom — Label/Target:**

| Nama Kolom | Tipe Data | Contoh Nilai | Deskripsi & Fungsi |
|:---|:---|:---|:---|
| `[kategori]_label_id` | `Integer` | `0`, `2`, `4` | **Status per Kategori.** Label status keuangan untuk tiap kategori (0=HEMAT s.d. 4=DARURAT). Ada 8 kolom ini (satu per kategori). |
| `overall_label_id` | `Integer` | `1`, `3`, `0` | **Target Utama (Y).** Label status keuangan keseluruhan mahasiswa. |
| `overall_label_name` | `String` | `"AMAN"`, `"BOROS"` | Representasi teks dari `overall_label_id`. |

**Panduan untuk Training Model:**
- **Input (X):** Semua 42 kolom fitur float (pct_used, proj_pct, dll)
- **Target (Y) Overall:** `overall_label_id` → klasifikasi 5 kelas
- **Target (Y) Per Kategori:** `[kategori]_label_id` × 8 → multi-task learning
- **Pra-pemrosesan:**
  - Normalisasi menggunakan `StandardScaler` (bukan MinMaxScaler)
  - Hapus `overall_label_name` saat training (string dari target numerik)
  - One-hot encoding pada label sebelum masuk ke model
- **Model:** MLP Multi-Head dengan Focal Loss + Warmup Cosine Schedule

---

*Dokumen ini dibuat sebagai bagian dari proyek SnapBudget — CC26-PSU098*
*Coding Camp 2026 · DBS Foundation*
