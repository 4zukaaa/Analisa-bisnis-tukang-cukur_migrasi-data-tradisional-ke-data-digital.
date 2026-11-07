---
title: "Appendix: Metodologi Perhitungan Dashboard Pendapatan Bisnis"
---

# Appendix: Metodologi Perhitungan

Dokumen ini menjelaskan cara setiap angka di dashboard dihitung. Semua perhitungan ditulis sebagai notasi variabel sehingga bisa diterapkan ulang di alat apa pun, misalnya Google Sheets, Excel, SQL, atau Python/Pandas.

> Satuan: semua nilai uang dalam **ribuan Rupiah** (120 = Rp120.000).

---

## A. Notasi

| Simbol | Arti |
|---|---|
| $t$ | Tanggal (1 Jun – 31 Okt 2026, total 153 hari) |
| $m$ | Bulan (Jun, Jul, Agu, Sep, Okt) |
| $k$ | Tempat usaha ($k \in \{1, 2\}$) |
| $i$ | Pekerja |
| $o$ | Pemilik usaha (pendapatannya tidak dibagi) |
| $K$ | Himpunan tempat yang dipilih di filter: $\{1\}$, $\{2\}$, atau $\{1, 2\}$ |
| $R_{i,t,k}$ | Pendapatan kotor pekerja $i$ pada tanggal $t$ di tempat $k$ |
| $s$ | Porsi bagi hasil untuk karyawan (default $s = 0{,}5$) |
| $\mathbb{1}[\cdot]$ | Fungsi indikator: bernilai 1 jika kondisi benar, 0 jika salah |

---

## B. Persiapan Data

1. **Reshape (wide → long).** Data asli berbentuk matriks *tanggal × pekerja* per bulan. Data diubah menjadi satu baris per kombinasi $(t, i)$ dengan kolom `Tanggal | Pekerja | Pendapatan | Status`.
2. **Status.** Setiap baris diberi status:
   $$\text{Status}_{i,t,k} = \begin{cases} \text{Tercatat} & \text{jika } R_{i,t,k} \text{ berisi angka} \\ \text{Kosong} & \text{jika sel kosong} \end{cases}$$
   Sel kosong **tidak** diisi 0, karena kosong bisa berarti tidak masuk atau tidak dicatat.
3. **Standardisasi.** Nama pekerja diseragamkan (alias digabung). Baris tanpa nomor tanggal dipetakan ke tanggal 31.

---

## C. Perhitungan Harian

Untuk setiap tanggal $t$ dan pilihan tempat $K$:

**Pendapatan kotor harian**
$$R_t = \sum_{k \in K} \sum_{i} R_{i,t,k}$$

**Pendapatan pemilik harian**
$$O_t = \sum_{k \in K} R_{o,t,k}$$

**Gaji karyawan harian** (bagi hasil hanya berlaku untuk non-pemilik)
$$W_t = s \cdot (R_t - O_t)$$

**Pendapatan bisnis harian** (yang diterima pemilik usaha)
$$B_t = R_t - W_t = O_t + (1 - s)(R_t - O_t)$$

---

## D. Tren Bulanan

Untuk setiap bulan $m$, jumlahkan semua tanggal $t \in m$:

| Metrik | Definisi |
|---|---|
| Pendapatan kotor per tempat | $R_{m,k} = \sum_{t \in m} \sum_i R_{i,t,k}$ |
| Pendapatan kotor | $R_m = \sum_{t \in m} R_t$ |
| Gaji karyawan | $W_m = \sum_{t \in m} W_t$ |
| Pendapatan bisnis | $B_m = \sum_{t \in m} B_t$ |
| Hari operasional | $D_m = \sum_{t \in m} \mathbb{1}[R_t > 0]$ |
| Bisnis per hari | $\bar{B}_m = \dfrac{B_m}{D_m}$ |
| Perubahan vs bulan lalu | $\Delta_m = \dfrac{B_m}{B_{m-1}} - 1$ |

**Contoh: Agustus**

- $R_m = 30.020$, $W_m = 13.072{,}5$, $B_m = 16.947{,}5$, $D_m = 31$
- $\bar{B}_m = 16.947{,}5 / 31 = 546{,}7$
- $\Delta_m = 16.947{,}5 / 12.115{,}5 - 1 = +39{,}9\%$

---

## E. Kartu KPI (Ringkasan Periode)

Dengan $R = \sum_m R_m$, $W = \sum_m W_m$, $B = \sum_m B_m$, dan $D = \sum_m D_m$:

| KPI | Definisi | Hasil |
|---|---|---|
| Pendapatan kotor | $R$ | 135.911 |
| Gaji karyawan | $W$ | 60.115 |
| Pendapatan bisnis | $B$ | 75.795 |
| Margin bisnis | $\dfrac{B}{R}$ | 55,8% |
| Bisnis per hari operasional | $\dfrac{B}{D}$ | 502 |
| Bisnis bulan terakhir vs sebelumnya | $\Delta_{\text{Okt}} = \dfrac{B_{\text{Okt}}}{B_{\text{Sep}}} - 1$ | −6,1% |

---

## F. Kinerja Pekerja

Untuk setiap pekerja $i$ (sesuai pilihan tempat $K$):

**Pendapatan kotor**
$$R_i = \sum_{k \in K} \sum_t R_{i,t,k}$$

**Hari masuk** (jumlah hari dengan pendapatan tercatat)
$$H_i = \sum_{k \in K} \sum_t \mathbb{1}[\text{Status}_{i,t,k} = \text{Tercatat}]$$

**Rata-rata pendapatan per hari masuk** (dasar produktivitas)
$$\bar{R}_i = \frac{R_i}{H_i}$$

**Kontribusi**
$$C_i = \frac{R_i}{\sum_j R_j}$$

**Peringkat produktivitas.** Peringkat ditentukan oleh jumlah pekerja lain yang rata-ratanya lebih tinggi, ditambah 1:
$$\text{Rank}_i = 1 + \sum_{j} \mathbb{1}[\bar{R}_j > \bar{R}_i]$$
Pekerja dengan $H_i = 0$ tidak diberi peringkat. Nilai yang sama mendapat peringkat yang sama.

**Gaji diterima**
$$G_i = \begin{cases} 0 & \text{jika } i = o \\ s \cdot R_i & \text{jika } i \neq o \end{cases}$$

**Kontribusi ke bisnis**
$$B_i = R_i - G_i$$

**Baris total.** Untuk baris total, rata-rata per hari dihitung tertimbang: $\bar{R} = \dfrac{\sum_i R_i}{\sum_i H_i}$, bukan rata-rata dari $\bar{R}_i$.

**Contoh**

| Pekerja | $R_i$ | $H_i$ | $\bar{R}_i$ | Rank | $G_i$ | $B_i$ |
|---|---|---|---|---|---|---|
| Pemilik | 15.680 | 59 | 265,8 | 5 | 0 | 15.680 |
| Pekerja E | 18.954,5 | 43 | 440,8 | 1 | 9.477,3 | 9.477,3 |

Alasan memakai $\bar{R}_i$ dan bukan $R_i$: total selalu menguntungkan pekerja yang paling sering masuk. Membagi dengan $H_i$ menormalkan perbedaan jumlah hari kerja, sehingga yang dibandingkan adalah *pendapatan per hari kerja*.

---

## G. Insight Otomatis

| Insight | Definisi |
|---|---|
| Bulan bisnis tertinggi / terendah | $\arg\max_m B_m$, $\arg\min_m B_m$ |
| Penyumbang terbesar ke bisnis | $\arg\max_i B_i$, dengan porsi $\dfrac{B_i}{\sum_j B_j}$ |
| Paling produktif | $\arg\max_i \bar{R}_i$ |
| Porsi Tempat 1 : Tempat 2 | $\dfrac{R_{\cdot,1}}{R_{\cdot,1} + R_{\cdot,2}}$ : $\dfrac{R_{\cdot,2}}{R_{\cdot,1} + R_{\cdot,2}}$ |
| Hari tanpa pendapatan | $\sum_t \mathbb{1}[R_t = 0]$ |

---

## H. Validasi (Rekonsiliasi)

Pemeriksaan yang harus selalu terpenuhi:

1. $\sum_{t} \sum_{i} R_{i,t,k}$ setelah reshape $=$ jumlah semua sel angka di data asli. Hasil: Tempat 1 = 76.906, Tempat 2 = 59.004,5.
2. $W + B = R$
3. $\sum_m B_m = \sum_i B_i$ (agregasi per bulan dan agregasi per pekerja menghasilkan angka yang sama)
4. $\sum_i C_i = 100\%$

---

## I. Asumsi & Keterbatasan

- **Bias periode.** Pekerja yang hanya bekerja di bulan ramai bisa tampak lebih produktif. Sebagai uji, peringkat dibandingkan ulang hanya pada periode Sep–Okt, dan urutannya tetap sama.
- **Ukuran sampel.** $\bar{R}_i$ dengan $H_i$ kecil (misalnya kurang dari 10 hari) tidak stabil, sehingga tidak layak dipakai untuk menilai kinerja.
- **Status Kosong.** Status ini diperlakukan sebagai tidak masuk saat menghitung $H_i$. Jika sebenarnya hanya tidak dicatat, $H_i$ menjadi terlalu kecil dan $\bar{R}_i$ terlalu besar.
- **Rata-rata vs median.** Rata-rata sensitif terhadap hari dengan nilai ekstrem. Median bisa dipakai sebagai pembanding.
- **Parameter $s$ dan $o$** bisa diubah di dashboard (sel input) untuk simulasi skema bagi hasil.
