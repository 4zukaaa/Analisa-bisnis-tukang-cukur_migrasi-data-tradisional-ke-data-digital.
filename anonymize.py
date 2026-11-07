"""Anonimisasi data mentah sebelum dipublikasikan.
Pemakaian: python anonymize.py data_asli.xlsx data_anonim.xlsx nama_map.json"""
# Anonimisasi: nama -> kode, angka -> dikali faktor rahasia + noise acak, dibulatkan ke 5
import sys, json, random, openpyxl
SRC, OUT = sys.argv[1], sys.argv[2]
random.seed()                       # seed acak -> tidak bisa direproduksi = tidak bisa dibalik
K = random.uniform(0.75, 1.25)      # faktor skala global (rahasia, tidak disimpan)
# Peta nama asli -> kode disimpan di file PRIVAT (jangan di-commit, sudah ada di .gitignore).
# Contoh isi nama_map.json: {"nama asli pemilik": "Pemilik", "nama karyawan 1": "Karyawan A"}
MAP = {k.lower(): v for k, v in json.load(open(sys.argv[3] if len(sys.argv) > 3 else "nama_map.json")).items()}
wb = openpyxl.load_workbook(SRC)
for ws in wb.worksheets:
    for c in ws[2]:
        if isinstance(c.value,str) and c.value.strip().lower() in MAP: c.value = MAP[c.value.strip().lower()]
    for row in ws.iter_rows(min_row=3, max_row=33, min_col=2):
        for c in row:
            if isinstance(c.value,(int,float)):
                c.value = max(5, round(c.value*K*random.uniform(0.85,1.15)/5)*5)
    ws.delete_rows(34, ws.max_row)   # buang ringkasan manual lama (berisi rumus nama asli)
if "Copy of Tempat 1" in wb.sheetnames: wb["Copy of Tempat 1"].title = "Tempat 2"
wb.save(OUT)
