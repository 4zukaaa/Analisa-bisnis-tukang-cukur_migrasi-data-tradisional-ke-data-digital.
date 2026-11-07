# Barbershop Data Structuring & Revenue Dashboard

**Studi kasus UMKM:** memindahkan catatan pendapatan harian dari **buku tulis** ke **spreadsheet**, merapikannya menjadi data terstruktur, lalu membangun dashboard agar pemilik usaha bisa melihat kondisi riil bisnisnya.

> *English summary: a case study on digitizing a small barbershop's handwritten daily revenue log, restructuring it into analysis-ready data, and building a Google Sheets dashboard that shows the owner's real (post profit-sharing) income. Includes Python scripts, calculation methodology, and validation checks.*

---

## ⚠️ Catatan tentang Data

Proyek ini dibuat dari **data riil** keluarga saya. Untuk melindungi privasi saya dan karyawan, data yang dipublikasikan di repo ini **sudah dianonimkan**:

- **Nama** pemilik dan karyawan diganti kode (`Pemilik`, `Karyawan A–D`), dan nama usaha tidak dicantumkan.
- **Angka pendapatan** dikalikan faktor skala acak yang dirahasiakan, ditambah *noise* acak ±15% per sel, lalu dibulatkan ke kelipatan 5. Proses ini dibantu AI dan dijalankan dengan [`scripts/anonymize.py`](scripts/anonymize.py).
- **Struktur, tanggal, pola kehadiran, dan pola tren tetap dipertahankan**, jadi metode dan alur analisisnya tetap sama dengan aslinya.

**Karena itu, jangan memakai angka di repo ini sebagai gambaran bisnis yang sebenarnya.** Fokuslah pada **metodenya**: cara merapikan data, cara menghitung metrik, dan cara memvalidasi hasil.

---

## Masalah

Banyak UMKM masih mencatat pendapatan di buku tulis. Data seperti itu sulit dijumlah, tidak bisa difilter, dan tidak bisa menjawab pertanyaan sederhana seperti:

- Apakah bisnis bulan ini naik atau turun?
- Berapa pendapatan yang **benar-benar** masuk ke pemilik setelah bagi hasil dengan karyawan?
- Tempat mana yang lebih menghasilkan?
- Karyawan mana yang paling rajin dan paling produktif?

Usaha dalam studi kasus ini adalah barbershop dengan **2 tempat** dan **5 orang** (pemilik + 4 karyawan) yang memakai **sistem bagi hasil 50:50**: pendapatan pemilik masuk utuh ke bisnis, sedangkan pendapatan setiap karyawan dibagi dua (50% gaji karyawan, 50% untuk bisnis).

---

## Linimasa Pengerjaan

### Jumat, 6 November 2026 — Digitalisasi
Saya memindahkan data secara manual, langsung dari buku catatan harian ayah saya ke Google Sheets, agar bisa dianalisis. Periodenya Juni–Oktober 2026 untuk 2 tempat.

📄 Data yang masih mentah (format ayah saya): [https://docs.google.com/spreadsheets/d/1ZD19EmWjw8CtG6jBSUqS-JochMYLlkLTpEBcNL1a0Ng/edit?usp=sharing]
📄 Data yang sudah dirapihkan ; [https://docs.google.com/spreadsheets/d/1TytDP3_KQFijjiTkhRn9CE-tC4I438Mjhblr4Xt7pzc/edit?usp=sharing]

### Minggu, 8 November 2026 — Analisis & Dashboard
Saya menganalisis data dan membangun dashboard untuk melihat kondisi bisnis ayah saya.

```
1. Merapikan & membersihkan data kotor
        ⇓
2. Menyusun ulang format tabel sesuai variabel yang dibutuhkan
        ⇓
3. Menganalisis variabel:
   • pendapatan harian per orang di masing-masing tempat
   • kehadiran karyawan (jumlah hari masuk)
   • produktivitas karyawan (pendapatan rata-rata per hari masuk)
        ⇓
4. Membangun dashboard agar pengambil keputusan mudah melihat kondisi riil bisnis
```

📊 Dashboard: [https://docs.google.com/spreadsheets/d/1ewKfXSMV89W-08_aGXPeiljWrYLO2g33fdlowHV5xFI/edit?usp=sharing]
---

## Langkah Detail

### 1. Pembersihan data (*data cleaning*)
Masalah yang ditemukan di data mentah dan cara menanganinya:

| Masalah | Penanganan |
|---|---|
| Format "buku": satu blok kolom per bulan, tanggal di baris, pekerja di kolom | Diubah menjadi format panjang (*wide → long*) |
| Tanggal dan bulan terpisah di sel yang berbeda | Digabung menjadi satu kolom tanggal asli (`dd/mm/yyyy`) |
| Nama ditulis berbeda-beda untuk orang yang sama | Diseragamkan |
| Baris tanpa nomor tanggal di bawah tanggal 30 | Dipetakan ke tanggal 31 (hanya muncul di bulan yang punya 31 hari) |
| Blok kolom "Oktober" ganda yang kosong | Dibuang |
| Total & persentase manual tercampur dengan data harian | Dipisahkan; semua total dihitung ulang dengan rumus |
| Sel kosong | **Tidak** diisi 0. Diberi status `Kosong` (bisa berarti tidak masuk atau tidak dicatat) |

### 2. Format tabel baru
Satu baris = satu orang pada satu hari di satu tempat:

| Tanggal | Pekerja | Pendapatan (Rp ribu) | Status |
|---|---|---|---|
| 01/06/2026 | Karyawan B | 345 | Tercatat |
| 01/06/2026 | Karyawan C | | Kosong |

### 3. Variabel yang dianalisis
- **Pendapatan kotor** per hari, per bulan, per tempat, per orang
- **Gaji karyawan** = pendapatan karyawan × porsi bagi hasil (50%)
- **Pendapatan bisnis** = pendapatan kotor − gaji karyawan (yang benar-benar diterima pemilik)
- **Kehadiran** = jumlah hari dengan pendapatan tercatat
- **Produktivitas** = pendapatan rata-rata per hari masuk

> Catatan: produktivitas di sini diukur dari **pendapatan per hari kerja**. Metrik ini **tidak mengukur kualitas layanan** (kepuasan pelanggan, kerapian potongan, dsb.), karena data tersebut tidak dicatat.

Rumus lengkap ada di **[APPENDIX.md](APPENDIX.md)**.

### 4. Dashboard
- **Filter tempat** (Semua / Tempat 1 / Tempat 2) dan **parameter porsi bagi hasil** yang bisa diubah untuk simulasi
- **6 KPI:** pendapatan kotor, gaji karyawan, pendapatan bisnis, margin, pendapatan bisnis per hari, dan perubahan bulan terakhir
- **Tabel tren bulanan** dan **tabel kinerja pekerja** dengan peringkat produktivitas
- **Insight otomatis** dan **grafik**

---

## Insight Utama (dari data anonim)

1. **Pendapatan kotor bisa menyesatkan.** September punya pendapatan kotor tertinggi, tetapi pendapatan **bisnis** tertinggi justru di Agustus. Kenaikan di September datang dari karyawan, yang hanya menyumbang 50% ke bisnis.
2. **Pendapatan bisnis turun 2 bulan berturut-turut** (Agustus → September → Oktober, sekitar −6% per bulan). Ini sinyal utama untuk ditindaklanjuti.
3. **Margin bisnis ±56% sangat bergantung pada kehadiran pemilik.** Pendapatan pemilik masuk 100% ke bisnis, sedangkan pendapatan karyawan hanya 50%.
4. **Total ≠ produktivitas.** Karyawan dengan total terbesar bukan yang paling produktif per hari. Peringkat produktivitas sudah diuji ulang pada periode yang sama (Sep–Okt) untuk menghindari bias periode, dan urutannya tetap.
5. **Tempat 1 menyumbang ±57%** pendapatan kotor, Tempat 2 ±43%.

---

## Struktur Repo

```
├── README.md
├── APPENDIX.md                  ← metodologi & rumus (notasi variabel)
├── LICENSE
├── data/
│   ├── data_mentah_anonim.xlsx  ← format buku (setelah digitalisasi)
│   ├── data_rapi_anonim.xlsx    ← format panjang (setelah cleaning)
│   └── dashboard_anonim.xlsx    ← dashboard lengkap
└── scripts/
    ├── anonymize.py             ← anonimisasi data
    ├── rapikan.py               ← cleaning + reshape wide → long
    └── dashboard.py             ← membangun sheet Harian + Dashboard
```

## Cara Menjalankan Ulang

```bash
pip install openpyxl
python scripts/rapikan.py data/data_mentah_anonim.xlsx data/data_rapi_anonim.xlsx
python scripts/dashboard.py data/data_rapi_anonim.xlsx data/dashboard_anonim.xlsx
```

Buka `dashboard_anonim.xlsx` di Google Sheets (**File → Impor → Upload**) atau Excel. Semua angka adalah rumus, jadi akan dihitung ulang otomatis.

---

## Untuk UMKM: Panduan Singkat Mulai Mencatat dengan Rapi

Kalau Anda pemilik usaha yang masih memakai buku catatan, lima aturan ini akan sangat memudahkan analisis:

1. **Satu baris = satu kejadian** (satu orang, satu hari, satu tempat). Jangan membuat blok terpisah per bulan.
2. **Tanggal dalam satu kolom** dengan format tanggal yang benar, bukan teks seperti "1 juni".
3. **Tulis nama dengan cara yang sama** setiap kali, atau pakai daftar pilihan (*dropdown*).
4. **Bedakan 0 dan kosong.** Tulis `0` jika masuk tetapi tidak ada pendapatan, dan biarkan kosong (atau tulis "libur") jika tidak masuk.
5. **Jangan mengetik total secara manual.** Biarkan rumus yang menghitung, supaya tidak ada salah hitung.

---

## Keterbatasan
- Data hanya mencakup 5 bulan, jadi pola musiman belum bisa disimpulkan.
- Rata-rata produktivitas untuk orang dengan sedikit hari masuk (< 10 hari) tidak stabil.
- Belum ada data biaya operasional (sewa, listrik, alat), sehingga "pendapatan bisnis" belum sama dengan laba bersih.

## Tentang Penulis
Saya berlatar belakang fisika dan matematika dan sedang beralih ke bidang data analytics. Proyek ini adalah penerapan nyata pertama saya: dari data keluarga yang berantakan menjadi alat bantu keputusan.

## Lisensi
Kode dilisensikan di bawah [MIT](LICENSE). Dokumentasi (README, APPENDIX) di bawah CC BY 4.0. Data contoh sudah dianonimkan dan disediakan hanya untuk tujuan belajar.
