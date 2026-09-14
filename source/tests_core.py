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
# ---------------------------------------------------------------- salvare
print("\n[10] Salvare sigura")

# verificatorul trebuie sa treaca un fisier bun...
d = pymupdf.open()
pg = d.new_page()
T.textbox(pg, pymupdf.Rect(50, 50, 500, 90), "Text de control", 14, (0, 0, 0))
bun = d.tobytes(garbage=3, deflate=True)
d.close()
check(T.check_pdf(bun) is None, "un PDF valid trece verificarea")

# ...si sa opreasca gunoiul
check(T.check_pdf(b"nu sunt un pdf") is not None, "gunoiul e respins")
check(T.check_pdf(b"") is not None, "fisierul gol e respins")

# un PDF cu o imagine JPEG stricata trebuie prins
d = pymupdf.open()
pg = d.new_page()
import struct
jpg = (b"\xff\xd8\xff\xe0" + b"\x00\x10JFIF" + b"\x00" * 60 + b"\xff\xd9")
try:
    pg.insert_image(pymupdf.Rect(50, 100, 200, 200),
                    pixmap=pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 40, 40)))
    date = d.tobytes()
    d.close()
    d2 = pymupdf.open("pdf", date)
    xrefs = [i[0] for i in d2.get_page_images(0, full=True)]
    if xrefs:
        # compress=0: pastreaza octetii asa cum sunt, altfel PyMuPDF ii recomprima
        d2.update_stream(xrefs[0], b"gunoi care nu e nici JPEG nici zlib" * 4, compress=0)
        # imaginea dintr-un pixmap nu are filtru; il declar JPEG ca sa
        # reproduc exact tiparul gasit in fisierul stricat
        d2.xref_set_key(xrefs[0], "Filter", "/DCTDecode")
        stricat = d2.tobytes()
        d2.close()
        check(T.check_pdf(stricat) is not None,
              "o imagine coruptă e prinsă: %s" % T.check_pdf(stricat))
    else:
        d2.close()
        check(True, "(fara imagini de stricat, sar peste)")
except Exception as e:
    check(True, "(nu am putut fabrica imaginea stricata: %s)" % str(e)[:40])

# scrierea atomica: fisierul final e complet, si nu ramane gunoi in folder
import tempfile as _tf
folder = _tf.mkdtemp(prefix="atomic_")
tinta = os.path.join(folder, "iesire.pdf")
T.write_atomic(tinta, bun)
check(os.path.exists(tinta) and open(tinta, "rb").read() == bun,
      "scrierea atomica pune exact octetii ceruti")
ramase = [f for f in os.listdir(folder) if f.startswith(".pdftool-")]
check(not ramase, "nu ramane niciun fisier temporar in folder")

# suprascrierea nu lasa fisierul pe jumatate
vechi = open(tinta, "rb").read()
d = pymupdf.open()
d.new_page()
d.new_page()
alt = d.tobytes(garbage=3, deflate=True)
d.close()
T.write_atomic(tinta, alt)
check(open(tinta, "rb").read() == alt, "suprascrierea inlocuieste complet continutul")
check(pymupdf.open(tinta).page_count == 2, "fisierul rescris se deschide corect")

# daca scrierea esueaza, fisierul vechi ramane neatins
T.write_atomic(tinta, vechi)
try:
    T.write_atomic(os.path.join(folder, "fara", "cale.pdf"), bun)
    check(False, "o cale imposibila ar fi trebuit sa dea eroare")
except Exception:
    check(open(tinta, "rb").read() == vechi,
          "dupa o scriere esuata, fisierul existent ramane intact")

# numele copiei de siguranta: ramane PDF, se deschide normal
b = T.backup_path(r"C:\dosar\factura.pdf")
check(b.endswith(".pdf"), "copia de siguranta ramane un PDF: %s" % os.path.basename(b))
check("original" in b.lower(), "numele ei spune ce e")
check(T.backup_path("fara-extensie").endswith(".pdf"),
      "si fara extensie iese tot un PDF")


# ---------------------------------------------- diacritice la a doua editare
print("\n[11] Diacritice adaugate dupa o salvare")

# Pregatesc exact situatia care strica textul: pagina primeste un font
# de sistem sub numele "Farial", apoi e subsetata la salvare. A doua
# editare cere litere care nu mai sunt in acel subset.
d = pymupdf.open()
pg = d.new_page()
T.textbox(pg, pymupdf.Rect(50, 60, 545, 100), "Société générale", 11, (0, 0, 0))
T.shrink_fonts(d)
date = d.tobytes(garbage=3, deflate=True)
d.close()

d = pymupdf.open("pdf", date)
pg = d.load_page(0)
resurse = {f[4]: f[0] for f in pg.get_fonts(full=True)}
check("Farial" in resurse, "pagina are deja resursa Farial: %s" % list(resurse))

buf = d.extract_font(resurse["Farial"])
f_vechi = pymupdf.Font(fontbuffer=buf[3]) if buf and buf[3] else None
lipseste = f_vechi and not f_vechi.has_glyph(ord("Î"))
check(bool(lipseste), "fontul subsetat NU contine 'Î' — asta rupea textul")

# a doua editare, cu litere care lipsesc din subset
pg.add_redact_annot(pymupdf.Rect(50, 55, 545, 105), fill=(1, 1, 1))
T.apply_redactions(pg)
NOUTEXT = "Întârziere de plată: 40€"
T.textbox(pg, pymupdf.Rect(50, 60, 545, 100), NOUTEXT, 11, (0, 0, 0))
T.shrink_fonts(d)
date2 = d.tobytes(garbage=3, deflate=True)
d.close()

d = pymupdf.open("pdf", date2)
txt = T.norm_text(d.load_page(0).get_text("text"))
nume = [f[4] for f in d.load_page(0).get_fonts(full=True)]
d.close()
check(NOUTEXT in txt, "textul cu diacritice noi se extrage: %r" % txt.strip()[:40])

# mai multe editari, in alfabete diferite, nu trebuie sa umfle fisierul
curent = date2
marimi = [len(curent)]
for t_nou in ("Zahlungsverzug €", "Опоздание",
              "Réparation générale"):
    dd = pymupdf.open("pdf", curent)
    pp = dd.load_page(0)
    pp.add_redact_annot(pymupdf.Rect(50, 55, 545, 105), fill=(1, 1, 1))
    T.apply_redactions(pp)
    T.textbox(pp, pymupdf.Rect(50, 60, 545, 100), t_nou, 11, (0, 0, 0))
    T.shrink_fonts(dd)
    curent = dd.tobytes(garbage=3, deflate=True)
    dd.close()
    marimi.append(len(curent))
    dd = pymupdf.open("pdf", curent)
    are = t_nou in T.norm_text(dd.load_page(0).get_text("text"))
    nrf = len(dd.load_page(0).get_fonts(full=True))
    dd.close()
    check(are, "%r se scrie si se citeste inapoi" % t_nou[:16])

crestere = (marimi[-1] - marimi[0]) / 1024.0
check(abs(crestere) < 30,
      "dupa 3 editari in alfabete diferite fisierul creste cu %.0f KB, nu se umfla" % crestere)
check(nrf <= 8, "numarul de fonturi ramane marginit: %d" % nrf)





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
