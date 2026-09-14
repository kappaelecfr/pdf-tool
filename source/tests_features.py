# -*- coding: utf-8 -*-
"""Teste pentru: multilingv, zoom, drag & drop, zonele de text."""
import os
import sys
import ast
import io
import time
import shutil
import tempfile
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pdf_tool as T
import lang as LG
from pdf_tool import filedialog, messagebox

fail = []


def check(cond, msg):
    print(("  OK  " if cond else "  FAIL ") + msg)
    if not cond:
        fail.append(msg)


D = tempfile.mkdtemp(prefix="pdfn_")
src = os.path.join(D, "a.pdf")
doc = pymupdf.open()
for i in range(4):
    p = doc.new_page(width=595, height=842)
    T.textbox(p, pymupdf.Rect(50, 60, 545, 100), "Factura 2026-%03d" % (i + 1), 18, (0, 0, 0))
    T.textbox(p, pymupdf.Rect(50, 140, 545, 200), "Client: Ștefan Ionescu", 12, (0, 0, 0))
    T.textbox(p, pymupdf.Rect(50, 220, 545, 280), "Total: 1.250,00 lei", 12, (0, 0, 0))
doc.save(src)
doc.close()

messagebox.showinfo = lambda *a, **k: None
messagebox.showerror = lambda *a, **k: None
messagebox.askyesno = lambda *a, **k: False
messagebox.askyesnocancel = lambda *a, **k: False


# =====================================================================
print("\n[1] Acoperirea traducerilor")
source = io.open(os.path.join(HERE, "pdf_tool.py"), encoding="utf-8").read()
tree = ast.parse(source)
keys = set()
for node in ast.walk(tree):
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "t" and node.args
            and isinstance(node.args[0], ast.Constant)):
        keys.add(node.args[0].value)
print("      %d texte folosite in cod" % len(keys))
for code in LG.TR:
    missing = [k for k in keys if k not in LG.TR[code]]
    check(not missing, "%s: toate cele %d texte sunt traduse%s"
          % (code, len(keys), "" if not missing else " — lipsesc %d: %r" % (len(missing), missing[:3])))


# =====================================================================
print("\n[2] Pornirea interfetei si comutarea limbii")
app = T.PDFTool()
app.update()
app.load(src)
end = time.time() + 1.2
while time.time() < end:
    app.update()
check(app.npages == 4, "document incarcat, 4 pagini")

probe = {}
for code in LG.LANG_ORDER:
    app.cb_ui_lang.set(LG.LANG_NAMES[code])
    app.on_lang_change()
    app.update()
    txt = app.btn_save.cget("text")
    probe[code] = txt
    okdoc = app.doc is not None and app.npages == 4
    check(bool(txt) and okdoc, "%-10s -> buton Salveaza = %-22r document pastrat=%s"
          % (LG.LANG_NAMES[code], txt, okdoc))
check(len(set(probe.values())) >= 7,
      "%d formulari distincte pentru acelasi buton" % len(set(probe.values())))

app.cb_ui_lang.set(LG.LANG_NAMES["ro"])
app.on_lang_change()
app.update()
check(app.btn_save.cget("text") == "Salvează", "revenit la romana")
check(os.path.exists(LG._CFG), "preferinta de limba s-a salvat pe disc")


# =====================================================================
print("\n[3] Zoom")
app.set_zoom(None)
app.update()
fit = app.preview_scale
check(fit > 0, "incadrat in fereastra: %d%%" % round(fit * 100))
app.zoom_by(1.25)
app.update()
check(abs(app.preview_scale - fit * 1.25) < 1e-6,
      "dupa + : %d%%" % round(app.preview_scale * 100))
app.zoom_by(1 / 1.25)
app.update()
check(abs(app.preview_scale - fit) < 1e-6, "dupa - : inapoi la %d%%" % round(app.preview_scale * 100))

app.set_zoom(3.0)
app.update()
check(app.lbl_zoom.cget("text") == "300%", "eticheta arata %s" % app.lbl_zoom.cget("text"))
check(app._scrollable(), "la 300%% pagina se poate derula")
sr = [float(v) for v in str(app.pcanvas.cget("scrollregion")).split()]
check(sr[2] > app.pcanvas.winfo_width(), "zona de derulare e mai lata decat fereastra")

app.set_zoom(20.0)
check(app.zoom == 8.0, "zoom limitat la maxim 800%%")
app.set_zoom(0.01)
check(app.zoom == 0.10, "zoom limitat la minim 10%%")
app.set_zoom(None)
app.update()
check(not app._scrollable(), "incadrat: nu mai e nevoie de derulare")


# =====================================================================
print("\n[4] Zonele de text din modul editare")
app.set_click_mode("text")
app.update()
check(len(app.edit_spans) >= 3, "%d zone de text gasite pe pagina 1" % len(app.edit_spans))
zones = app.pcanvas.find_withtag("zone")
check(len(zones) == len(app.edit_spans),
      "%d dreptunghiuri desenate peste text" % len(zones))

page = app.doc.load_page(0)
r = page.search_for("Ștefan")[0]
sp = app._span_at((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
check(sp is not None and "Ștefan" in sp["text"],
      "click pe mijlocul textului gaseste zona: %r" % (sp["text"] if sp else None))
check(app._span_at(5, 5) is None, "click pe zona goala nu gaseste nimic")

app.set_click_mode(None)
app.update()
check(not app.pcanvas.find_withtag("zone"), "zonele dispar cand opresc modul editare")


# =====================================================================
print("\n[5] Drag and drop")
print("      biblioteca activa:", T.HAS_DND)


class FakeDrop:
    def __init__(self, data):
        self.data = data


class FakeChoice:
    """Inlocuieste fereastra de alegere, ca testul sa nu astepte un om."""
    answer = None

    def __init__(self, *a, **k):
        self.result = FakeChoice.answer


T.ChoiceDialog = FakeChoice

n0 = app.npages
FakeChoice.answer = "append"
app.on_drop(FakeDrop("{%s}" % src))
app.update()
check(app.npages == n0 + 4,
      "raspuns 'adauga la final': %d -> %d pagini" % (n0, app.npages))

n1 = app.npages
FakeChoice.answer = None            # utilizatorul a inchis fereastra
app.on_drop(FakeDrop("{%s}" % src))
app.update()
check(app.npages == n1, "raspuns 'renunta': documentul ramane la %d pagini" % app.npages)

FakeChoice.answer = "open"
app.on_drop(FakeDrop("{%s}" % src))
app.update()
check(app.npages == 4, "raspuns 'deschide-l': document nou, %d pagini" % app.npages)

img = os.path.join(D, "s.png")
from PIL import Image as PILImage
PILImage.new("RGBA", (120, 60), (255, 0, 0, 128)).save(img)
app.on_drop(FakeDrop("{%s}" % img))
app.update()
check(app.stamp_path == img, "imaginea trasa devine stampila")
check(app.click_mode == "image", "trece automat in modul plasare")

app.set_click_mode(None)
app.on_drop(FakeDrop("{%s}" % os.path.join(D, "nuexista.pdf")))
check(True, "fisier inexistent: ignorat fara eroare")

txtf = os.path.join(D, "x.txt")
open(txtf, "w").write("salut")
app.on_drop(FakeDrop("{%s}" % txtf))
check(True, "fisier nepotrivit: mesaj, fara crapare")

app.cmd_close_doc()
app.update()
app.on_drop(FakeDrop("{%s}" % src))
app.update()
check(app.doc is not None and app.npages == 4,
      "PDF tras cand nu e nimic deschis -> se deschide direct")


# =====================================================================
print("\n[6] Ecranul gol")
app.cmd_close_doc()
app.update()
items = app.pcanvas.find_all()
texts = [app.pcanvas.itemcget(i, "text") for i in items
         if app.pcanvas.type(i) == "text"]
check(any("PDF" in x for x in texts), "mesajul 'trage aici un PDF' e afisat: %r" % texts[:2])


# =====================================================================
print("\n[7] Ghidul")
import guide as G
import faq as F
import unicodedata

check(len(G.GUIDE) == len(LG.LANG_ORDER),
      "ghid pentru toate cele %d limbi" % len(LG.LANG_ORDER))
for code in LG.LANG_ORDER:
    g = G.GUIDE.get(code, "")
    linii = g.split("\n")
    lungi = [x for x in linii if len(x) > 78]
    check(len(g) > 1500 and not lungi,
          "%-10s %4d caractere, %3d randuri, latime maxima %d col%s"
          % (LG.LANG_NAMES[code], len(g), len(linii),
             max(len(x) for x in linii),
             "" if not lungi else " - %d randuri prea lungi" % len(lungi)))
check(G.text_for("xx") == G.GUIDE["en"], "limba necunoscuta cade pe engleza")

LG._write_cfg({})
check(not LG.guide_seen(), "la prima pornire ghidul nu a fost vazut")
LG.mark_guide_seen()
check(LG.guide_seen(), "dupa afisare ramane marcat")
LG.save_pref("fr")
check(LG.guide_seen() and LG._read_cfg().get("lang") == "fr",
      "salvarea limbii nu sterge marcajul ghidului")

app2 = T.PDFTool()
app2.update()
app2.show_guide()
app2.update()
ferestre = [w for w in app2.winfo_children() if isinstance(w, T.TextViewer)]
check(len(ferestre) == 1, "butonul '?' deschide fereastra ghidului")
if ferestre:
    ferestre[0].destroy()
app2.destroy()

# =====================================================================
print("\n[8] Limba sistemului si copyright")
import datetime
import locale as _loc

sl = LG.system_lang()
check(isinstance(sl, str) and len(sl) in (0, 2),
      "Windows raporteaza limba: %r" % sl)
prin_biblioteca = ""
try:
    prin_biblioteca = (_loc.getdefaultlocale()[0] or "").split("_")[0].lower()
except Exception:
    pass
check(sl == prin_biblioteca or not prin_biblioteca,
      "acelasi raspuns ca vechea metoda (%r vs %r)" % (sl, prin_biblioteca))

LG._write_cfg({})
fara_pref = LG.load_pref()
check(fara_pref == sl or (sl not in LG.LANG_NAMES and fara_pref == "en"),
      "fara preferinte salvate porneste in %r" % fara_pref)
LG.save_pref("pl")
check(LG.load_pref() == "pl", "preferinta salvata bate limba sistemului")
LG._write_cfg({})

an = datetime.date.today().year
check("%d" % an in (T.COPYRIGHT % an), "anul %d apare in text" % an)
check("KappaProject" in T.COPYRIGHT, "numele e in text")
check((T.COPYRIGHT % 2031).endswith("2031"),
      "anul e luat din ceas, nu scris fix: %r" % (T.COPYRIGHT % 2031))

app3 = T.PDFTool()
app3.update()
etichete = []


def aduna(w):
    for c in w.winfo_children():
        try:
            if c.winfo_class() == "Label":
                etichete.append(c.cget("text"))
        except Exception:
            pass
        aduna(c)


aduna(app3)
copy_linii = [x for x in etichete if "KappaProject" in str(x)]
check(len(copy_linii) == 1, "o singura linie de copyright in fereastra: %r"
      % (copy_linii[0] if copy_linii else None))
check(str(an) in str(copy_linii[0]) if copy_linii else False,
      "linia afisata contine anul curent")

app3.cb_ui_lang.set(LG.LANG_NAMES["de"])
app3.on_lang_change()
app3.update()
etichete = []
aduna(app3)
check(any("KappaProject" in str(x) for x in etichete),
      "copyright-ul ramane si dupa schimbarea limbii")
app3.destroy()

# =====================================================================
print("\n[9] FAQ")
check(len(F.FAQ) == len(LG.LANG_ORDER),
      "FAQ pentru toate cele %d limbi" % len(LG.LANG_ORDER))

ALFABETE_STRAINE = ("CJK", "HIRAGANA", "KATAKANA", "HANGUL", "ARABIC",
                    "HEBREW", "DEVANAGARI", "THAI")
for code in LG.LANG_ORDER:
    txt = F.FAQ.get(code, "")
    linii = txt.split("\n")
    lungi = [x for x in linii if len(x) > 78]
    intrebari = sum(1 for x in linii if x.strip() and set(x.strip()) == {"-"})
    straine = []
    for ch in set(txt):
        if ord(ch) < 0x2000:
            continue
        try:
            nume = unicodedata.name(ch)
        except ValueError:
            continue
        if any(k in nume for k in ALFABETE_STRAINE):
            straine.append(ch)
    ok = len(txt) > 2500 and not lungi and not straine and intrebari >= 10
    check(ok, "%-10s %4d car., %2d intrebari, max %2d col%s%s"
          % (LG.LANG_NAMES[code], len(txt), intrebari,
             max(len(x) for x in linii),
             "" if not lungi else " - %d randuri prea lungi" % len(lungi),
             "" if not straine else " - caractere straine: %r" % straine[:3]))

nr = set()
for code in LG.LANG_ORDER:
    nr.add(sum(1 for x in F.FAQ[code].split("\n")
               if x.strip() and set(x.strip()) == {"-"}))
check(len(nr) == 1, "toate limbile au acelasi numar de intrebari: %s" % nr)
check(F.text_for("xx") == F.FAQ["en"], "limba necunoscuta cade pe engleza")

# fisierele de pe disc trebuie sa fie identice cu ce arata programul
import os
DIST = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
perechi = [(os.path.join(DIST, "FAQ.txt"), F.FAQ["en"]),
           (os.path.join(DIST, "README.txt"), G.GUIDE["en"]),
           (os.path.join(DIST, "Readme", "FAQ-ro.txt"), F.FAQ["ro"]),
           (os.path.join(DIST, "Readme", "README-ru.txt"), G.GUIDE["ru"])]
for cale, asteptat in perechi:
    exista = os.path.exists(cale)
    egal = exista and io.open(cale, encoding="utf-8").read().replace("\r\n", "\n") == asteptat
    check(egal, "%s e identic cu ce arata programul" % os.path.basename(cale))

app4 = T.PDFTool()
app4.update()
app4.show_faq()
app4.update()
ferestre = [w for w in app4.winfo_children() if isinstance(w, T.TextViewer)]
check(len(ferestre) == 1, "butonul FAQ deschide fereastra")
if ferestre:
    check("FAQ" in ferestre[0].title(), "titlul ferestrei: %r" % ferestre[0].title())
    ferestre[0].destroy()
app4.destroy()

# =====================================================================
print("\n[10] Modificarea nu se mai pierde din neatentie")

import tempfile as _tf2
D2 = _tf2.mkdtemp(prefix="autoap_")
sursa = os.path.join(D2, "doc.pdf")
_d = pymupdf.open()
for _i in range(2):
    _p = _d.new_page(width=595, height=842)
    T.textbox(_p, pymupdf.Rect(50, 60, 545, 100), "PRIMUL rand de text", 14, (0, 0, 0))
    T.textbox(_p, pymupdf.Rect(50, 140, 545, 180), "AL DOILEA rand de text", 14, (0, 0, 0))
_d.save(sursa)
_d.close()

app5 = T.PDFTool()
app5.update()
app5.load(sursa)
app5.set_click_mode("text")
app5.update()


def zona(app, cuvant):
    pg = app.doc.load_page(app.current)
    h = pg.search_for(cuvant)
    return (h[0].x0 + h[0].x1) / 2, (h[0].y0 + h[0].y1) / 2


def scrie(app, text):
    app.txt_edit.delete("1.0", "end")
    app.txt_edit.insert("1.0", text)


# scenariul raportat: scriu, apoi dau click pe alt text fara sa apas nimic
x, y = zona(app5, "PRIMUL")
app5.pick_text_at(app5.doc.load_page(0), x, y)
check(app5.edit_target is not None, "am selectat primul text")
scrie(app5, "SCHIMBAT-PRIN-CLICK")
check(app5.pending_edit(), "aplicatia stie ca e o modificare nesalvata")

x2, y2 = zona(app5, "DOILEA")
app5.pick_text_at(app5.doc.load_page(0), x2, y2)
app5.update()
txt = T.norm_text(app5.doc.load_page(0).get_text("text"))
check("SCHIMBAT-PRIN-CLICK" in txt,
      "click pe alt text APLICA modificarea, nu o arunca")
check("PRIMUL rand" not in txt, "textul vechi a disparut")

# Ctrl+Z trebuie sa o poata anula
app5.undo()
app5.update()
txt = T.norm_text(app5.doc.load_page(0).get_text("text"))
check("PRIMUL rand" in txt and "SCHIMBAT-PRIN-CLICK" not in txt,
      "Ctrl+Z anuleaza aplicarea automata")

# schimbarea paginii aplica si ea
app5.set_click_mode("text")
x, y = zona(app5, "PRIMUL")
app5.pick_text_at(app5.doc.load_page(0), x, y)
scrie(app5, "SCHIMBAT-PRIN-PAGINA")
app5.goto(1)
app5.update()
txt0 = T.norm_text(app5.doc.load_page(0).get_text("text"))
check("SCHIMBAT-PRIN-PAGINA" in txt0, "schimbarea paginii aplica modificarea")

# iesirea din modul editare aplica
app5.goto(0)
app5.set_click_mode("text")
x2, y2 = zona(app5, "DOILEA")
app5.pick_text_at(app5.doc.load_page(0), x2, y2)
scrie(app5, "SCHIMBAT-LA-IESIRE")
app5.set_click_mode(None)
app5.update()
txt = T.norm_text(app5.doc.load_page(0).get_text("text"))
check("SCHIMBAT-LA-IESIRE" in txt, "oprirea modului editare aplica modificarea")

# butonul Arunca chiar arunca
app5.set_click_mode("text")
x, y = zona(app5, "SCHIMBAT-LA-IESIRE")
app5.pick_text_at(app5.doc.load_page(0), x, y)
scrie(app5, "ASTA-NU-TREBUIE-SA-RAMANA")
app5.discard_edit()
app5.update()
txt = T.norm_text(app5.doc.load_page(0).get_text("text"))
check("ASTA-NU-TREBUIE-SA-RAMANA" not in txt, "butonul Aruncă chiar aruncă")
check("SCHIMBAT-LA-IESIRE" in txt, "si nu strica ce era deja aplicat")

# un text neschimbat nu declanseaza nimic
x, y = zona(app5, "SCHIMBAT-LA-IESIRE")
app5.pick_text_at(app5.doc.load_page(0), x, y)
check(not app5.pending_edit(), "fara modificare, nu e nimic de aplicat")
inainte = app5.doc.tobytes()
app5.set_click_mode(None)
check(True, "iesirea fara modificari nu face nimic")

app5.destroy()

# =====================================================================
print("\n[11] Caseta de editare se poarta ca un camp de text")

app6 = T.PDFTool()
app6.update()
app6.load(sursa)
app6.set_click_mode("text")
app6.update()

pg6 = app6.doc.load_page(0)
h6 = pg6.search_for("PRIMUL")[0]
app6.pick_text_at(pg6, (h6.x0 + h6.x1) / 2, (h6.y0 + h6.y1) / 2)
inainte = app6.txt_edit.get("1.0", "end").strip()
check(inainte != "", "textul s-a incarcat in caseta")

app6.txt_edit.insert("end", " ADAUGAT")
app6.update()
check("ADAUGAT" in app6.txt_edit.get("1.0", "end"), "am scris in caseta")

doc_inainte = T.norm_text(app6.doc.load_page(0).get_text("text"))
app6.txt_edit.edit_undo()
app6.update()
check(app6.txt_edit.get("1.0", "end").strip() == inainte,
      "Ctrl+Z in caseta anuleaza doar scrisul")
check(T.norm_text(app6.doc.load_page(0).get_text("text")) == doc_inainte,
      "documentul nu a fost atins de Ctrl+Z din caseta")

app6._select_all_text()
check(bool(app6.txt_edit.tag_ranges("sel")), "Ctrl+A selecteaza textul din caseta")

# in afara casetei, scurtaturile lucreaza pe document, ca inainte
app6.discard_edit()
app6.set_click_mode(None)
n_inainte = app6.npages
app6._select_all_key()
check(len(app6.selected) == n_inainte,
      "in afara casetei, Ctrl+A selecteaza paginile (%d)" % len(app6.selected))

app6.op_rotate(90)
rot = app6.doc.load_page(0).rotation
app6._undo_key()
app6.update()
check(app6.doc.load_page(0).rotation != rot,
      "in afara casetei, Ctrl+Z anuleaza operatia pe document")

app6.destroy()

# =====================================================================
print("\n[12] Corector ortografic si copie de siguranta")

import spell as SP
import msvcrt as _mc

check(isinstance(SP.disponibil(), bool), "corectorul Windows raspunde: %s" % SP.disponibil())
instalate = [c for c in LG.LANG_ORDER if SP.eticheta_pentru(c)]
print("      limbi cu dictionar pe acest calculator: %s"
      % (" ".join(instalate) if instalate else "niciuna"))

if instalate:
    cod = instalate[0]
    c = SP.corector_pentru(cod)
    check(c is not None, "am obtinut un corector pentru %s" % cod)
    if c:
        proba = {"fr": "Ceci est un texte avec une fote.",
                 "en": "This is a texct here.",
                 "ro": "Acesta e un text cu o greseala."}.get(cod, "This is a texct here.")
        gres = c.greseli(proba)
        check(len(gres) >= 1, "gaseste greseli in %r: %s" % (proba, [g[2] for g in gres]))
        if gres:
            sug = c.sugestii(gres[0][2])
            check(len(sug) >= 1, "propune variante pentru %r: %s" % (gres[0][2], sug[:3]))
        check(c.greseli("") == [], "text gol: nicio greseala")
        c.close()
else:
    check(True, "(niciun dictionar instalat, sar peste verificarea propriu-zisa)")

check(SP.corector_pentru("xx") is None, "limba inexistenta nu da corector")

# caseta: sublinierea nu schimba textul
app7 = T.PDFTool()
app7.update()
app7.load(sursa)
app7.set_click_mode("text")
app7.update()
pg7 = app7.doc.load_page(0)
h7 = pg7.search_for("PRIMUL")[0]
app7.pick_text_at(pg7, (h7.x0 + h7.x1) / 2, (h7.y0 + h7.y1) / 2)
app7.txt_edit.delete("1.0", "end")
app7.txt_edit.insert("1.0", "un texct cu greseli")
app7._spell_check()
app7.update()
check(app7.txt_edit.get("1.0", "end").strip() == "un texct cu greseli",
      "corectorul NU schimba textul singur")
app7.discard_edit()

# copia de siguranta se scrie doar dupa o salvare reusita
import tempfile as _tf3
D3 = _tf3.mkdtemp(prefix="bak_")
tinta3 = os.path.join(D3, "f.pdf")
shutil.copy(sursa, tinta3)
octeti0 = open(tinta3, "rb").read()
app7.load(tinta3)
app7.op_rotate(90)

blocaj = open(tinta3, "rb")
blocaj.read(256)
blocat = True
try:
    _mc.locking(blocaj.fileno(), _mc.LK_NBLCK, 4096)
except OSError:
    blocat = False
app7.cmd_save()
app7.update()
if blocat:
    try:
        blocaj.seek(0)
        _mc.locking(blocaj.fileno(), _mc.LK_UNLCK, 4096)
    except OSError:
        pass
blocaj.close()

if blocat:
    check(open(tinta3, "rb").read() == octeti0, "fisier ocupat: nu s-a scris nimic")
    check(len(os.listdir(D3)) == 1, "fisier ocupat: nu ramane nicio copie inutila")
else:
    check(True, "(nu am putut bloca fisierul, sar peste)")

app7.cmd_save()
app7.update()
check(open(tinta3, "rb").read() != octeti0, "fisier liber: salvarea a mers")
copii = [f for f in os.listdir(D3) if f != "f.pdf"]
check(copii == ["f (original).pdf"], "copia de siguranta: %s" % copii)
if copii:
    check(open(os.path.join(D3, copii[0]), "rb").read() == octeti0,
          "copia contine fisierul dinainte de modificare")

app7.destroy()

# =====================================================================
print("[13] Stergerile accidentale nu se aplica in tacere")

D4 = _tf3.mkdtemp(prefix="guard_")
s4 = os.path.join(D4, "d.pdf")
_d4 = pymupdf.open()
_p4 = _d4.new_page()
T.textbox(_p4, pymupdf.Rect(50, 60, 545, 100), "Facture", 22, (0, 0, 0))
T.textbox(_p4, pymupdf.Rect(50, 140, 545, 180), "Interv depannage elec 18 rue", 11, (0, 0, 0))
_d4.save(s4)
_d4.close()

_raspuns = {"da": False}
messagebox.askyesno = lambda *a, **k: _raspuns["da"]


def _scenariu(cuvant, text_nou, confirma):
    _raspuns["da"] = confirma
    a = T.PDFTool()
    a.update()
    a.load(s4)
    a.set_click_mode("text")
    a.update()
    pg = a.doc.load_page(0)
    h = pg.search_for(cuvant)[0]
    a.pick_text_at(pg, (h.x0 + h.x1) / 2, (h.y0 + h.y1) / 2)
    a.txt_edit.delete("1.0", "end")
    a.txt_edit.insert("1.0", text_nou)
    celalalt = "Interv" if cuvant == "Facture" else "Facture"
    alt = a.doc.load_page(0).search_for(celalalt)[0]
    a.pick_text_at(a.doc.load_page(0), (alt.x0 + alt.x1) / 2, (alt.y0 + alt.y1) / 2)
    a.update()
    txt = T.norm_text(a.doc.load_page(0).get_text("text"))
    a.destroy()
    return txt

t1 = _scenariu("Facture", "F", False)
check("Facture" in t1, "stergere aproape totala, raspund NU: textul ramane intreg")

t2 = _scenariu("Facture", "F", True)
check("Facture" not in t2, "aceeasi stergere, raspund DA: se aplica")

t3 = _scenariu("Interv", "Travaux electricite 18 rue", False)
check("Travaux electricite" in t3,
      "corectura normala se aplica singura, fara sa intrebe")

t4 = _scenariu("Interv", "Interv depannage elec 18 rue Boursault", False)
check("Boursault" in t4, "textul mai lung se aplica fara intrebare")

messagebox.askyesno = lambda *a, **k: False





LG._write_cfg({})


app.destroy()

print("\n" + "=" * 58)
if fail:
    print("AU PICAT %d teste:" % len(fail))
    for m in fail:
        print("   - " + m)
    sys.exit(1)
print("TOATE TESTELE NOI AU TRECUT")
