"""Langkah 2: bangun sheet Harian + Dashboard (rumus, KPI, grafik) dari data rapi.
Pemakaian: python dashboard.py data_rapi.xlsx dashboard.xlsx"""
import sys, datetime as dt
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.formatting.rule import ColorScaleRule
from openpyxl.utils import get_column_letter as L

SRC, OUT = sys.argv[1], sys.argv[2]
wb = openpyxl.load_workbook(SRC)
for n in ("Harian","Dashboard"):
    if n in wb.sheetnames: del wb[n]

NAVY="1F4E78"; LIGHT="DDEBF7"; GREY="F2F2F2"; INPUT="FFF2CC"
H = Font(bold=True, color="FFFFFF"); HF = PatternFill("solid", fgColor=NAVY)
thin = Side(style="thin", color="BFBFBF"); box = Border(top=thin,bottom=thin,left=thin,right=thin)
NUM = "#,##0"; PCT = "0.0%"
SEL, PORSI, OWNER = "Dashboard!$C$3", "Dashboard!$G$3", "Dashboard!$C$4"
T1, T2 = "'Tempat 1'", "'Tempat 2'"
def both(f1, f2):   # gabungkan Tempat 1 & 2 sesuai pilihan C3
    return f'IF({SEL}="Tempat 2",0,{f1})+IF({SEL}="Tempat 1",0,{f2})'

# ================= Harian =================
h = wb.create_sheet("Harian")
h.append(["Tanggal","Bulan","Tempat 1 (kotor)","Tempat 2 (kotor)","Kotor (pilihan)",
          "Pemilik (pilihan)","Gaji Karyawan","Pendapatan Bisnis"])
for c in h[1]: c.font, c.fill, c.alignment = H, HF, Alignment(wrap_text=True, horizontal="center")
d = dt.date(2026,6,1); r = 2
while d <= dt.date(2026,10,31):
    h.cell(r,1,d).number_format = "dd/mm/yyyy"
    h.cell(r,2,f"=MONTH(A{r})")
    h.cell(r,3,f"=SUMIFS({T1}!$C:$C,{T1}!$A:$A,$A{r})")
    h.cell(r,4,f"=SUMIFS({T2}!$C:$C,{T2}!$A:$A,$A{r})")
    h.cell(r,5,f"={both(f'C{r}', f'D{r}')}")
    h.cell(r,6,"="+both(f"SUMIFS({T1}!$C:$C,{T1}!$A:$A,$A{r},{T1}!$B:$B,{OWNER})",
                        f"SUMIFS({T2}!$C:$C,{T2}!$A:$A,$A{r},{T2}!$B:$B,{OWNER})"))
    h.cell(r,7,f"=(E{r}-F{r})*{PORSI}")
    h.cell(r,8,f"=E{r}-G{r}")
    for j in range(3,9): h.cell(r,j).number_format = NUM
    d += dt.timedelta(days=1); r += 1
HL = r-1
for j,w in enumerate((12,7,12,12,12,12,12,13),1): h.column_dimensions[L(j)].width = w
h.freeze_panes = "A2"
rng = lambda col: f"Harian!${col}$2:${col}${HL}"

# ================= Dashboard =================
ws = wb.create_sheet("Dashboard", 0)
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 2
for j,w in enumerate((36,14,14,14,14,14,14,13,13),2): ws.column_dimensions[L(j)].width = w

ws["B1"] = "Dashboard Pendapatan Bisnis — Jun s/d Okt 2026"; ws["B1"].font = Font(bold=True, size=16, color=NAVY)
ws["B2"] = "Semua angka dalam RIBUAN Rupiah (120 = Rp120.000). Kuning = sel yang boleh diubah."
ws["B2"].font = Font(italic=True, color="7F7F7F")
def inp(cell, val, nf=None):
    c = ws[cell]; c.value = val; c.fill = PatternFill("solid", fgColor=INPUT); c.border = box; c.font = Font(bold=True)
    if nf: c.number_format = nf
ws["B3"] = "Pilih Tempat:"; inp("C3","Semua")
ws["E3"] = "Porsi gaji karyawan:"; inp("G3",0.5,"0%")
ws["B4"] = "Pemilik (pendapatan utuh):"; inp("C4","Pemilik")
for c in ("B3","E3","B4"): ws[c].font = Font(bold=True)
ws["E4"] = "Pekerja selain pemilik: pendapatan × porsi = gaji, sisanya masuk bisnis."
ws["E4"].font = Font(italic=True, size=9, color="7F7F7F")
dv = DataValidation(type="list", formula1='"Semua,Tempat 1,Tempat 2"'); ws.add_data_validation(dv); dv.add("C3")

def header(row, labels, col0=2):
    for j,t in enumerate(labels):
        c = ws.cell(row,col0+j,t); c.font, c.fill = H, HF
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[row].height = 30

# ---- Tren Bulanan: header 11, data 12-16, total 17 ----
MON = [("Juni",6),("Juli",7),("Agustus",8),("September",9),("Oktober",10)]
ws["B10"] = "Tren Bulanan"; ws["B10"].font = Font(bold=True, size=12, color=NAVY)
header(11, ["Bulan","Tempat 1 (kotor)","Tempat 2 (kotor)","Pendapatan Kotor","Gaji Karyawan",
            "Pendapatan Bisnis","Hari Operasional","Bisnis / Hari","Δ Bisnis vs Bln Lalu"])
for i,(b,m) in enumerate(MON):
    r = 12+i; ws.cell(r,2,b)
    for j,col in zip(range(3,8),"CDEGH"):
        ws.cell(r,j,f"=SUMIFS({rng(col)},{rng('B')},{m})")
    ws.cell(r,8,f'=COUNTIFS({rng("B")},{m},{rng("E")},">0")')
    ws.cell(r,9,f"=IFERROR(G{r}/H{r},0)")
    ws.cell(r,10,"-" if i==0 else f"=IFERROR(G{r}/G{r-1}-1,0)")
    for j in range(2,11):
        c = ws.cell(r,j); c.border = box; c.number_format = PCT if j==10 else NUM
    ws.cell(r,10).alignment = Alignment(horizontal="right")
ws.cell(17,2,"Total")
for j in range(3,9): ws.cell(17,j,f"=SUM({L(j)}12:{L(j)}16)")
ws.cell(17,9,"=IFERROR(G17/H17,0)")
for j in range(2,11):
    c = ws.cell(17,j); c.font = Font(bold=True); c.number_format = NUM; c.border = box
    c.fill = PatternFill("solid", fgColor=LIGHT)
ws.conditional_formatting.add("G12:G16", ColorScaleRule(start_type="min", start_color="F8CBAD", end_type="max", end_color="A9D08E"))

# ---- Kinerja Pekerja: header 20, data 21-25, total 26 ----
P = ["Pemilik","Karyawan A","Karyawan B","Karyawan C","Karyawan D"]
ws["B19"] = "Kinerja Pekerja (sesuai pilihan tempat)"; ws["B19"].font = Font(bold=True, size=12, color=NAVY)
header(20, ["Pekerja","Pendapatan Kotor","Hari Masuk","Rata-rata / Hari Masuk","Kontribusi %",
            "Peringkat Produktivitas","Gaji Diterima","Masuk ke Bisnis"])
for i,p in enumerate(P):
    r = 21+i; ws.cell(r,2,p)
    ws.cell(r,3,"="+both(f"SUMIFS({T1}!$C:$C,{T1}!$B:$B,$B{r})", f"SUMIFS({T2}!$C:$C,{T2}!$B:$B,$B{r})"))
    ws.cell(r,4,"="+both(f'COUNTIFS({T1}!$B:$B,$B{r},{T1}!$D:$D,"Tercatat")', f'COUNTIFS({T2}!$B:$B,$B{r},{T2}!$D:$D,"Tercatat")'))
    ws.cell(r,5,f"=IFERROR(C{r}/D{r},0)")
    ws.cell(r,6,f"=IFERROR(C{r}/$C$26,0)")
    ws.cell(r,7,f'=IF(D{r}=0,"-",COUNTIF($E$21:$E$25,">"&E{r})+1)')
    ws.cell(r,8,f"=IF($B{r}={OWNER},0,C{r}*{PORSI})")
    ws.cell(r,9,f"=C{r}-H{r}")
    for j in range(2,10):
        c = ws.cell(r,j); c.border = box; c.number_format = PCT if j==6 else NUM
    ws.cell(r,7).alignment = Alignment(horizontal="center")
ws.cell(26,2,"Total")
for j in (3,4,8,9): ws.cell(26,j,f"=SUM({L(j)}21:{L(j)}25)")
ws.cell(26,5,"=IFERROR(C26/D26,0)"); ws.cell(26,6,"=SUM(F21:F25)")
for j in range(2,10):
    c = ws.cell(26,j); c.font = Font(bold=True); c.border = box; c.fill = PatternFill("solid", fgColor=LIGHT)
    c.number_format = PCT if j==6 else NUM
ws.conditional_formatting.add("E21:E25", ColorScaleRule(start_type="min", start_color="F8CBAD", end_type="max", end_color="A9D08E"))

# ---- KPI cards: label 6, value 7 ----
kpis = [("Pendapatan Kotor","=E17",NUM), ("Gaji Karyawan","=F17",NUM), ("Pendapatan Bisnis","=G17",NUM),
        ("Margin Bisnis (Bisnis ÷ Kotor)","=IFERROR(G17/E17,0)",PCT), ("Bisnis / Hari Operasional","=I17",NUM),
        ("Bisnis Okt vs Sep","=J16","+0.0%;-0.0%;0.0%")]
for j,(lab,f,nf) in enumerate(kpis):
    col = 2+j
    a = ws.cell(6,col,lab); a.font = Font(bold=True, color="FFFFFF", size=9); a.fill = HF
    a.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    v = ws.cell(7,col,f); v.font = Font(bold=True, size=16, color=NAVY); v.number_format = nf
    v.alignment = Alignment(horizontal="center", vertical="center"); v.fill = PatternFill("solid", fgColor=LIGHT)
    for rr in (6,7): ws.cell(rr,col).border = box
ws.row_dimensions[6].height = 30; ws.row_dimensions[7].height = 34
ws["G8"] = "+ naik / − turun"; ws["G8"].font = Font(italic=True, size=8, color="7F7F7F")

# ---- Insight ----
ws["B29"] = "Insight Otomatis"; ws["B29"].font = Font(bold=True, size=12, color=NAVY)
ins = [
 ("Bulan pendapatan bisnis tertinggi", '=INDEX(B12:B16,MATCH(MAX(G12:G16),G12:G16,0))&" ("&TEXT(MAX(G12:G16),"#,##0")&")"'),
 ("Bulan pendapatan bisnis terendah", '=INDEX(B12:B16,MATCH(MIN(G12:G16),G12:G16,0))&" ("&TEXT(MIN(G12:G16),"#,##0")&")"'),
 ("Penyumbang terbesar ke bisnis", '=INDEX(B21:B25,MATCH(MAX(I21:I25),I21:I25,0))&" — "&TEXT(MAX(I21:I25),"#,##0")&" ("&TEXT(MAX(I21:I25)/I26,"0%")&" dari pendapatan bisnis)"'),
 ("Paling produktif (kotor / hari masuk)", '=INDEX(B21:B25,MATCH(MAX(E21:E25),E21:E25,0))&" — "&TEXT(MAX(E21:E25),"#,##0")&" / hari"'),
 ("Porsi pendapatan kotor Tempat 1 : 2", '=TEXT(C17/(C17+D17),"0%")&" : "&TEXT(D17/(C17+D17),"0%")'),
 ("Hari tanpa pendapatan", f'=COUNTIF({rng("E")},0)&" dari "&ROWS({rng("E")})&" hari"'),
]
for i,(lab,f) in enumerate(ins):
    r = 30+i; ws.cell(r,2,lab).font = Font(bold=True)
    ws.merge_cells(start_row=r,start_column=3,end_row=r,end_column=8)
    ws.cell(r,3,f).fill = PatternFill("solid", fgColor=GREY)

# ---- Charts (kanan, mulai kolom L) ----
def nogrid(c): c.y_axis.majorGridlines = None
cats = Reference(ws, min_col=2, min_row=12, max_row=16)
c1 = LineChart(); c1.title = "Pendapatan Kotor per Bulan per Tempat (ribu)"; c1.height, c1.width = 7.5, 16
c1.add_data(Reference(ws, min_col=3, max_col=4, min_row=11, max_row=16), titles_from_data=True); c1.set_categories(cats)
for s in c1.series: s.smooth = False
ws.add_chart(c1, "L3")

c2 = BarChart(); c2.type = "col"; c2.grouping = "stacked"; c2.overlap = 100
c2.title = "Pembagian Pendapatan per Bulan (ribu)"; c2.height, c2.width = 7.5, 16
c2.add_data(Reference(ws, min_col=6, max_col=7, min_row=11, max_row=16), titles_from_data=True); c2.set_categories(cats)
ws.add_chart(c2, "L19")

c3 = BarChart(); c3.type = "bar"; c3.grouping = "stacked"; c3.overlap = 100
c3.title = "Per Pekerja: Gaji vs Masuk ke Bisnis (ribu)"; c3.height, c3.width = 7.5, 16
c3.add_data(Reference(ws, min_col=8, max_col=9, min_row=20, max_row=25), titles_from_data=True)
c3.set_categories(Reference(ws, min_col=2, min_row=21, max_row=25))
ws.add_chart(c3, "L35")

c4 = BarChart(); c4.type = "bar"; c4.title = "Rata-rata Pendapatan per Hari Masuk (ribu)"; c4.height, c4.width = 7.5, 16
c4.add_data(Reference(ws, min_col=5, min_row=20, max_row=25), titles_from_data=True)
c4.set_categories(Reference(ws, min_col=2, min_row=21, max_row=25)); c4.legend = None
ws.add_chart(c4, "L51")

c5 = LineChart(); c5.title = "Pendapatan Bisnis Harian (ribu, sesuai pilihan)"; c5.height, c5.width = 7.5, 30
c5.add_data(Reference(h, min_col=8, min_row=1, max_row=HL), titles_from_data=True)
c5.set_categories(Reference(h, min_col=1, min_row=2, max_row=HL)); c5.legend = None
c5.x_axis.number_format = "dd/mm"
for s in c5.series: s.smooth = False
ws.add_chart(c5, "B38")
for c in (c1,c2,c3,c4,c5): nogrid(c)

wb.active = 0
wb.save(OUT); print("ok", HL)
