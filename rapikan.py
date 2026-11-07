"""Langkah 1: ubah data mentah (format buku: tanggal x pekerja per bulan) menjadi tabel panjang.
Pemakaian: python rapikan.py data_mentah.xlsx data_rapi.xlsx"""
import sys, datetime as dt, calendar
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

SRC, OUT = sys.argv[1], sys.argv[2]
YEAR = 2026
BULAN = {"juni":6,"juli":7,"agustus":8,"september":9,"oktober":10}
NAMA = {n.lower(): n for n in ["Pemilik","Karyawan A","Karyawan B","Karyawan C","Karyawan D"]}
URUT = ["Pemilik","Karyawan A","Karyawan B","Karyawan C","Karyawan D"]
SHEETS = {"Tempat 1":"Tempat 1","Tempat 2":"Tempat 2"}

src = openpyxl.load_workbook(SRC)
out = openpyxl.Workbook(); out.remove(out.active)
hdr_font = Font(bold=True, color="FFFFFF"); hdr_fill = PatternFill("solid", fgColor="1F4E78")
log = []

for sname, tname in SHEETS.items():
    ws = src[sname]
    # blok bulan: header bulan di baris 1, nama pekerja di baris 2
    starts = [(c.column, c.value.strip().lower()) for c in ws[1] if c.value]
    seen = set(); rows = []
    for i,(col,mname) in enumerate(starts):
        if mname in seen:      # blok Oktober kedua (AH:AL) kosong -> abaikan
            log.append(f"{tname}: blok '{mname}' duplikat di kolom {get_column_letter(col)} diabaikan (tanpa data)")
            continue
        seen.add(mname)
        end = starts[i+1][0] if i+1 < len(starts) else ws.max_column+1
        m = BULAN[mname]; ndays = calendar.monthrange(YEAR, m)[1]
        for c in range(col, end):
            raw = ws.cell(2, c).value
            if not raw: continue
            nama = NAMA[raw.strip().lower()]
            for r in range(3, 34):          # baris 3..33 = tgl 1..31
                day = r - 2
                v = ws.cell(r, c).value
                if day > ndays:
                    if v not in (None, ""): log.append(f"{tname}: nilai {v} di {ws.cell(r,c).coordinate} melebihi jumlah hari {mname}")
                    continue
                ok = isinstance(v,(int,float))
                rows.append((dt.date(YEAR,m,day), nama, v if ok else None, "Tercatat" if ok else "Kosong"))
    rows.sort(key=lambda x:(x[0], URUT.index(x[1])))

    o = out.create_sheet(tname)
    o.append(["Tanggal","Pekerja","Pendapatan (Rp ribu)","Status"])
    for d,n,v,s in rows: o.append([d,n,v,s])
    for c in o[1]: c.font, c.fill, c.alignment = hdr_font, hdr_fill, Alignment(horizontal="center")
    for r in range(2, o.max_row+1):
        o.cell(r,1).number_format = "dd/mm/yyyy"; o.cell(r,3).number_format = "General"
    for col,w in zip("ABCD",(14,16,20,12)): o.column_dimensions[col].width = w
    o.freeze_panes = "A2"
    t = Table(displayName=tname.replace(" ","_"), ref=f"A1:D{o.max_row}")
    t.tableStyleInfo = TableStyleInfo(name="TableStyleMedium2", showRowStripes=True)
    o.add_table(t)
    n_ok = sum(1 for x in rows if x[3]=="Tercatat")
    log.append(f"{tname}: {len(rows)} baris ({n_ok} Tercatat, {len(rows)-n_ok} Kosong), total nilai {sum(x[2] or 0 for x in rows):,.0f}")

# Ringkasan dengan rumus (dihitung dari tabel harian, bukan diketik manual)
rs = out.create_sheet("Ringkasan")
bulan_list = [("Juni",6),("Juli",7),("Agustus",8),("September",9),("Oktober",10)]
r = 1
for tname in SHEETS.values():
    rs.cell(r,1,f"Total Pendapatan (Rp ribu) per Bulan — {tname}").font = Font(bold=True, size=12); r += 1
    head = ["Pekerja"]+[b for b,_ in bulan_list]+["Total","Hari Masuk"]
    for j,h in enumerate(head,1):
        c = rs.cell(r,j,h); c.font, c.fill = hdr_font, hdr_fill
    r += 1; first = r
    for p in URUT:
        rs.cell(r,1,p)
        for j,(b,m) in enumerate(bulan_list,2):
            a = dt.date(YEAR,m,1); z = dt.date(YEAR,m,calendar.monthrange(YEAR,m)[1])
            rs.cell(r,j,(f"=SUMIFS('{tname}'!$C:$C,'{tname}'!$B:$B,$A{r},"
                         f"'{tname}'!$A:$A,\">=\"&DATE({a.year},{a.month},{a.day}),"
                         f"'{tname}'!$A:$A,\"<=\"&DATE({z.year},{z.month},{z.day}))")).number_format="General"
        rs.cell(r,7,f"=SUM(B{r}:F{r})").number_format="General"
        rs.cell(r,8,f"=COUNTIFS('{tname}'!$B:$B,$A{r},'{tname}'!$D:$D,\"Tercatat\")")
        r += 1
    rs.cell(r,1,"Total").font = Font(bold=True)
    for j in range(2,9):
        L = get_column_letter(j)
        c = rs.cell(r,j,f"=SUM({L}{first}:{L}{r-1})"); c.font = Font(bold=True); c.number_format="General"
    r += 3
rs.column_dimensions["A"].width = 16
for j in range(2,9): rs.column_dimensions[get_column_letter(j)].width = 12

out.save(OUT)
print("\n".join(log))
