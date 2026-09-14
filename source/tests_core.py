# -*- coding: utf-8 -*-
"""Teste pentru logica din pdf_tool.py (fara interfata grafica)."""
import os
import sys
import pymupdf

sys.path.insert(0, r"C:\Users\kappa\Documents\PDF-Tool\source")
import pdf_tool as T

import tempfile
OUT = tempfile.mkdtemp(prefix="pdft_core_")
ok = lambda m: print("  OK  " + m)
fail = []


def check(cond, msg):
    if cond:
        ok(msg)
    else:
        fail.append(msg)
        print("  FAIL " + msg)


# ---------------------------------------------------------------- fonturi
print("\n[1] Fonturi si diacritice")
f, path, name = T.sys_font("sans")
check(path is not None, "font sistem gasit: %s" % path)
w = T.text_width("Șoseaua Ștefan cel Mare, Târgoviște", 12)
check(w > 100, "latime text cu diacritice = %.1f" % w)
for ch in "ăâîșțĂÂÎȘȚ":
    check(f.has_glyph(ord(ch)), "fontul contine '%s'" % ch)

# ------------------------------------------------------------ PDF de test
print("\n[2] Creez PDF de test (3 pagini)")
doc = pymupdf.open()
for i in range(3):
    p = doc.new_page(width=595, height=842)
    p.draw_rect(pymupdf.Rect(0, 0, 595, 120), color=None, fill=(0.90, 0.94, 1.0))
    T.textbox(p, pymupdf.Rect(50, 40, 545, 90), "FACTURĂ Nr. 1234", 22, (0.1, 0.1, 0.3))
    T.textbox(p, pymupdf.Rect(50, 160, 545, 220),
              "Client: Ștefan Ionescu  ·  Data: 13.09.2026  ·  Total: 1.250,00 lei",
              12, (0, 0, 0))
    T.textbox(p, pymupdf.Rect(50, 240, 545, 400),
              "Pagina de test %d. Text cu diacritice: îmbrăcăminte, țară, șosea." % (i + 1),
              11, (0.2, 0.2, 0.2))
src = os.path.join(OUT, "test.pdf")
doc.save(src)
doc.close()
check(os.path.getsize(src) > 1000, "PDF creat, %d bytes" % os.path.getsize(src))

doc = pymupdf.open(src)
txt = doc.load_page(0).get_text("text")
check("FACTURĂ" in txt, "diacriticele se extrag corect din PDF")
check("Ștefan" in txt, "'Ștefan' extras corect")

# ---------------------------------------------------------------- intervale
print("\n[3] Parsare intervale de pagini")
check(T.parse_ranges("1-3", 10) == {0, 1, 2}, "'1-3'")
check(T.parse_ranges("1, 5, 9", 10) == {0, 4, 8}, "'1, 5, 9'")
check(T.parse_ranges("8-", 10) == {7, 8, 9}, "'8-' (pana la final)")
check(T.parse_ranges("-3", 10) == {0, 1, 2}, "'-3' (de la inceput)")
check(T.parse_ranges("2-4, 9, 99", 10) == {1, 2, 3, 8}, "mixt + ignora paginile inexistente")

# ---------------------------------------------------------------- culoare fundal
print("\n[4] Detectare culoare fundal")
bg = T.bg_color_at(doc.load_page(0), pymupdf.Rect(50, 40, 300, 70))
check(bg[2] > bg[0], "fundal albastrui detectat in antet: %s"
      % (tuple(round(c, 2) for c in bg),))
bg2 = T.bg_color_at(doc.load_page(0), pymupdf.Rect(50, 250, 300, 270))
check(all(c > 0.9 for c in bg2), "fundal alb detectat in corp: %s"
      % (tuple(round(c, 2) for c in bg2),))

# ---------------------------------------------------------------- filigran
print("\n[5] Filigran cu rotatie si transparenta")
page = doc.load_page(0)
before = len(page.get_text("text"))
T.write_line(page, pymupdf.Point(150, 450), "CONFIDENȚIAL", 52, (1, 0, 0),
             angle=45, opacity=0.22, pivot=pymupdf.Point(297, 421))
after = page.get_text("text")
check("CONFIDENȚIAL" in after, "filigranul cu diacritice e in pagina")
check(len(after) > before, "textul paginii a crescut")

# ---------------------------------------------------------------- numerotare
print("\n[6] Numerotare pagini")
for idx in range(doc.page_count):
    p = doc.load_page(idx)
    t = "{n} / {total}".replace("{n}", str(idx + 1)).replace("{total}", str(doc.page_count))
    wdt = T.text_width(t, 10)
    T.write_line(p, pymupdf.Point((p.rect.width - wdt) / 2, p.rect.height - 28), t, 10,
                 (0.2, 0.2, 0.2))
check("2 / 3" in doc.load_page(1).get_text("text"), "pagina 2 numerotata '2 / 3'")

# ------------------------------------------------------- cauta si inlocuieste
print("\n[7] Cauta si inlocuieste (cu pastrarea fundalului)")
page = doc.load_page(0)
hits = page.search_for("1.250,00")
check(len(hits) == 1, "gasit '1.250,00' o data")
r = hits[0]
d = page.get_text("dict")
size, color = 12, (0, 0, 0)
for blk in d["blocks"]:
    for line in blk.get("lines", []):
        for sp in line.get("spans", []):
            if pymupdf.Rect(sp["bbox"]).intersects(r):
                size = sp["size"]
                color = T.int_color(sp["color"])
bgc = T.bg_color_at(page, r)
page.add_redact_annot(r, fill=bgc)
T.apply_redactions(page)
grow = max(4.0, T.text_width("9.999,99", size) - r.width + 4.0)
T.textbox(page, pymupdf.Rect(r.x0 - 1, r.y0 - 2, r.x1 + grow, r.y1 + 3),
          "9.999,99", size, color)
t0 = page.get_text("text")
check("9.999,99" in t0, "suma noua e in pagina")
check("1.250,00" not in t0, "suma veche a disparut")
check("Ștefan" in t0, "restul textului a ramas intact")

# ---------------------------------------------------------------- pagini
print("\n[8] Operatii pe pagini")
doc.load_page(1).set_rotation(90)
check(doc.load_page(1).rotation == 90, "rotire 90 grade")
order = [2, 0, 1]
doc.select(order)
check(doc.page_count == 3, "reordonare: tot 3 pagini")
doc.delete_page(2)
check(doc.page_count == 2, "stergere pagina -> 2 ramase")

nd = pymupdf.open()
nd.insert_pdf(doc)
nd.insert_pdf(doc)
check(nd.page_count == 4, "unire: 2 + 2 = 4 pagini")
nd.close()

out = os.path.join(OUT, "rezultat.pdf")
doc.save(out, garbage=3, deflate=True)
check(os.path.exists(out), "salvare finala: %d bytes" % os.path.getsize(out))
doc.close()

# ---------------------------------------------------------------- tabele
print("\n[9] Detectare tabele")
d2 = pymupdf.open()
p = d2.new_page()
x0, y0, cw, ch = 60, 100, 120, 26
head = ["Produs", "Cant.", "Preț", "Total"]
rows = [["Șurub M8", "10", "2,50", "25,00"],
        ["Piuliță", "20", "1,10", "22,00"],
        ["Șaibă", "50", "0,40", "20,00"]]
for ri, row in enumerate([head] + rows):
    for ci, cell in enumerate(row):
        rect = pymupdf.Rect(x0 + ci * cw, y0 + ri * ch, x0 + (ci + 1) * cw, y0 + (ri + 1) * ch)
        p.draw_rect(rect, color=(0, 0, 0), width=0.7)
        T.textbox(p, pymupdf.Rect(rect.x0 + 4, rect.y0 + 6, rect.x1 - 2, rect.y1),
                  cell, 9, (0, 0, 0))
tabs = list(p.find_tables().tables)
check(len(tabs) >= 1, "am gasit %d tabel(e)" % len(tabs))
if tabs:
    ext = tabs[0].extract()
    check(len(ext) == 4, "tabelul are %d randuri" % len(ext))
    flat = " ".join(str(c) for row in ext for c in row)
    check("Șurub M8" in flat, "continut cu diacritice citit corect din tabel")
d2.close()

# ---------------------------------------------------------------- tesseract
print("\n[10] OCR")
exe, td = T.find_tesseract()
print("  --  tesseract: %s" % (exe or "neinstalat (OCR dezactivat, restul merge)"))

print("\n" + "=" * 56)
if fail:
    print("AU PICAT %d teste:" % len(fail))
    for m in fail:
        print("   - " + m)
    sys.exit(1)
print("TOATE TESTELE AU TRECUT")
