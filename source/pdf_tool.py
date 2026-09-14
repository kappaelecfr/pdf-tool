#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PDF Tool - aplicatie locala pentru modificat PDF-uri.

Copyright (C) KappaProject

Acest program este software liber: il puteti redistribui si/sau modifica
in termenii Licentei Publice Generale Affero GNU, versiunea 3 sau, la
alegerea dumneavoastra, orice versiune ulterioara, asa cum e publicata
de Free Software Foundation.

Programul e distribuit in speranta ca va fi util, dar FARA NICIO
GARANTIE. Vedeti fisierul LICENSE pentru textul complet, sau
https://www.gnu.org/licenses/

Ruleaza complet offline. Niciun fisier nu pleaca de pe calculator.

Necesita: python -m pip install pymupdf pillow
Optional (doar pentru OCR pe documente scanate): Tesseract OCR
"""

import os
import re
import sys
import datetime
import tempfile
import csv
import traceback
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

from lang import (t, set_lang, save_pref, load_pref, current,
                  guide_seen, mark_guide_seen, check_updates, set_check_updates,
                  LANG_NAMES, LANG_ORDER)
from guide import text_for as guide_text
import spell
import update_check
from faq import text_for as faq_text

APP_NAME = "PDF Tool"
APP_VER = "1.3.1"
# anul vine din ceasul calculatorului, deci se schimba singur
COPYRIGHT = "Copyright \u00a9 KappaProject %d"


def _fatal(msg):
    try:
        r = tk.Tk()
        r.withdraw()
        messagebox.showerror(APP_NAME, msg)
        r.destroy()
    except Exception:
        print(msg)
    sys.exit(1)


try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        _fatal(t("Lipseste biblioteca PyMuPDF.\n\n"
               "Deschide Command Prompt si ruleaza:\n\n"
               "    python -m pip install pymupdf pillow"))

try:
    from tkinterdnd2 import TkinterDnD, DND_FILES
    _ROOT_BASE = TkinterDnD.Tk
    HAS_DND = True
except Exception:                      # fara drag & drop, restul merge la fel
    _ROOT_BASE = tk.Tk
    DND_FILES = None
    HAS_DND = False

try:
    from PIL import Image, ImageDraw, ImageTk
except ImportError:
    _fatal(t("Lipseste biblioteca Pillow.\n\n"
           "Deschide Command Prompt si ruleaza:\n\n"
           "    python -m pip install pymupdf pillow"))


# --------------------------------------------------------------------------
# Aspect
# --------------------------------------------------------------------------

BG = "#eef1f5"
PANEL = "#ffffff"
BORDER = "#d4d9e2"
INK = "#1b2130"
MUTED = "#697586"
ACCENT = "#2563eb"
ACCENT_DK = "#1d4ed8"
DANGER = "#dc2626"
CANVAS_BG = "#8b93a1"

THUMB_W = 116
UNDO_MAX = 12


# --------------------------------------------------------------------------
# Fonturi (diacritice romanesti: ăâîșț)
# --------------------------------------------------------------------------

FONT_DIR = os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts")
FONT_FILES = {
    "sans":        ["arial.ttf", "segoeui.ttf", "calibri.ttf", "tahoma.ttf", "verdana.ttf"],
    "sans-bold":   ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf", "tahomabd.ttf"],
    "sans-italic": ["ariali.ttf", "segoeui.ttf", "calibrii.ttf"],
    "serif":       ["times.ttf", "georgia.ttf", "constan.ttf"],
    "serif-bold":  ["timesbd.ttf", "georgiab.ttf"],
    "mono":        ["consola.ttf", "cour.ttf", "lucon.ttf"],
}
_font_cache = {}

# Fonturile standard PDF: nu se incorporeaza in fisier (fisier mic) si dau
# spatii normale la copiere, dar nu au diacritice romanesti.
BASE14 = {
    "sans": "helv", "sans-bold": "hebo", "sans-italic": "heit",
    "serif": "tiro", "serif-bold": "tibo", "mono": "cour",
}


def pick_font(text, kind="sans"):
    """Alege fontul potrivit pentru un text.

    Text simplu (fara diacritice) -> font standard PDF: fisier mic si
    spatii curate la copy-paste. Text cu ăâîșț -> font de sistem.
    """
    if text is not None and text.isascii():
        name = BASE14.get(kind, "helv")
        key = "@" + name
        if key not in _font_cache:
            _font_cache[key] = (pymupdf.Font(name), None, name)
        return _font_cache[key]
    return sys_font(kind)


def sys_font(kind="sans"):
    """Returneaza (obiect Font, cale fisier sau None, nume intern)."""
    if kind in _font_cache:
        return _font_cache[kind]
    for fn in FONT_FILES.get(kind, []):
        p = os.path.join(FONT_DIR, fn)
        if os.path.exists(p):
            try:
                f = pymupdf.Font(fontfile=p)
                _font_cache[kind] = (f, p, "F" + os.path.splitext(fn)[0])
                return _font_cache[kind]
            except Exception:
                continue
    f = pymupdf.Font("helv")
    _font_cache[kind] = (f, None, "helv")
    return _font_cache[kind]


def font_kind_for(pdf_font_name):
    """Ghiceste familia potrivita pornind de la numele fontului din PDF."""
    n = (pdf_font_name or "").lower()
    bold = "bold" in n or n.endswith("bd") or "black" in n or "heavy" in n
    if "mono" in n or "courier" in n or "consol" in n:
        return "mono"
    if "times" in n or "serif" in n or "georgia" in n or "roman" in n or "garamond" in n:
        return "serif-bold" if bold else "serif"
    if bold:
        return "sans-bold"
    if "italic" in n or "oblique" in n:
        return "sans-italic"
    return "sans"


def page_fontname(page, doc, base, text):
    """Un nume de resursa de font sub care textul dat chiar se poate scrie.

    Daca pagina are deja un font cu numele cerut, PyMuPDF il refoloseste
    si ignora fisierul pe care il dam. Bun cand fontul acela contine tot
    ce ne trebuie; dezastruos cand a fost subsetat si nu contine.
    """
    try:
        existente = {}
        for f in page.get_fonts(full=True):
            existente[f[4]] = f[0]          # nume resursa -> xref
    except Exception:
        return base

    if base not in existente:
        return base

    # numele e luat: fontul de acolo acopera literele noastre?
    nevoie = {ord(c) for c in text if not c.isspace()}
    try:
        buf = doc.extract_font(existente[base])
        if buf and buf[3]:
            f = pymupdf.Font(fontbuffer=buf[3])
            if all(f.has_glyph(c) for c in nevoie):
                return base                 # se potriveste, il refolosim
    except Exception:
        pass

    # nu acopera: luam un nume liber, ca fontul sa fie incorporat din nou
    i = 2
    while "%s%d" % (base, i) in existente:
        i += 1
    return "%s%d" % (base, i)


def textbox(page, rect, text, fontsize, color=(0, 0, 0), kind="sans", align=0):
    """Scrie text intr-un dreptunghi. Micsoreaza fontul daca nu incape."""
    font, path, name = pick_font(text, kind)
    if path:                                # fonturile standard nu se incorporeaza
        name = page_fontname(page, page.parent, name, text)
    size = fontsize
    for _ in range(24):
        kw = {"fontsize": size, "color": color, "align": align, "fontname": name}
        if path:
            kw["fontfile"] = path
        rc = page.insert_textbox(rect, text, **kw)
        if rc >= 0:
            return size
        size *= 0.92
        if size < 3:
            break
    return None


def write_baseline(page, point, text, fontsize, color=(0, 0, 0), kind="sans",
                   maxw=None):
    """Scrie textul cu picioarele literelor exact pe linia data.

    textbox() aseaza randul dupa inaltimea fontului nou, deci iese cu un
    fir mai sus sau mai jos decat textul de langa el. Aici pornim de la
    punctul de baza al textului vechi, asa cum il da PDF-ul, si randul
    cade la fix. Daca nu incape in latimea ramasa, micsoram fontul.
    """
    font, path, name = pick_font(text, kind)
    if path:
        name = page_fontname(page, page.parent, name, text)
    size = float(fontsize)
    if maxw and maxw > 0:
        while size > 3 and font.text_length(text, size) > maxw:
            size *= 0.96
    kw = {"fontsize": size, "color": color, "fontname": name}
    if path:
        kw["fontfile"] = path
    page.insert_text(pymupdf.Point(point[0], point[1]), text, **kw)
    return size


def write_line(page, point, text, fontsize, color=(0, 0, 0), kind="sans",
               angle=0, opacity=1.0, pivot=None):
    """Scrie o linie de text, cu rotatie si transparenta optionale."""
    font, path, _ = pick_font(text, kind)
    tw = pymupdf.TextWriter(page.rect)
    tw.append(point, text, font=font, fontsize=fontsize)
    kw = {"color": color, "opacity": opacity, "overlay": True}
    if angle:
        kw["morph"] = (pivot or point, pymupdf.Matrix(angle))
    tw.write_text(page, **kw)


def text_width(text, fontsize, kind="sans"):
    font, _, _ = pick_font(text, kind)
    return font.text_length(text, fontsize)


def norm_text(s):
    """Spatiile speciale devin spatii normale, la export."""
    return ((s or "").replace(chr(0xa0), " ").replace(chr(0x2009), " ")
            .replace(chr(0x202f), " ").replace(chr(0xad), "-"))


# --------------------------------------------------------------------------
# Utilitare PDF
# --------------------------------------------------------------------------

def bg_color_at(page, rect):
    """Culoarea fundalului din jurul unui dreptunghi (pentru acoperit text)."""
    try:
        pad = 3
        clip = pymupdf.Rect(rect.x0 - pad, rect.y0 - pad,
                            rect.x1 + pad, rect.y1 + pad) & page.rect
        if clip.is_empty or clip.width < 2 or clip.height < 2:
            return (1, 1, 1)
        pix = page.get_pixmap(clip=clip, colorspace=pymupdf.csRGB, alpha=False)
        w, h = pix.width, pix.height
        pts = []
        for x in range(0, w, max(1, w // 12)):
            pts.append((x, 0))
            pts.append((x, h - 1))
        for y in range(0, h, max(1, h // 12)):
            pts.append((0, y))
            pts.append((w - 1, y))
        counts = {}
        for x, y in pts:
            try:
                c = pix.pixel(x, y)
            except Exception:
                continue
            counts[c] = counts.get(c, 0) + 1
        if not counts:
            return (1, 1, 1)
        c = max(counts.items(), key=lambda kv: kv[1])[0]
        return (c[0] / 255.0, c[1] / 255.0, c[2] / 255.0)
    except Exception:
        return (1, 1, 1)


def int_color(rgb_int):
    return ((rgb_int >> 16 & 255) / 255.0,
            (rgb_int >> 8 & 255) / 255.0,
            (rgb_int & 255) / 255.0)


def hex_to_rgb(h):
    h = h.lstrip("#")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0, int(h[4:6], 16) / 255.0)


def rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(int(round(c * 255)) for c in rgb)


def backup_path(path):
    """Numele copiei de siguranta: ramane PDF, se poate deschide normal."""
    baza, ext = os.path.splitext(path)
    return "%s (original)%s" % (baza, ext or ".pdf")


def write_atomic(path, data):
    """Scrie tot, sau nimic. Nu lasa niciodata fisierul pe jumatate scris."""
    folder = os.path.dirname(os.path.abspath(path)) or "."
    fd, tmp = tempfile.mkstemp(prefix=".pdftool-", suffix=".tmp", dir=folder)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except Exception:
            pass
        raise


def check_pdf(data):
    """Verifica un PDF proaspat scris. Returneaza None daca e bun,
    altfel o descriere scurta a problemei."""
    try:
        doc = pymupdf.open("pdf", data)
    except Exception as e:
        return "fisierul nu se mai poate deschide (%s)" % e
    try:
        if doc.page_count < 1:
            return "fisierul a ramas fara pagini"
        for pno in range(doc.page_count):
            page = doc.load_page(pno)
            page.get_text("text")
            for info in doc.get_page_images(pno, full=True):
                xref = info[0]
                try:
                    filt = str(doc.xref_get_key(xref, "Filter")[1])
                    raw = doc.xref_stream_raw(xref)
                except Exception:
                    return "o imagine de pe pagina %d nu se mai poate citi" % (pno + 1)
                if "DCTDecode" in filt and not raw.startswith(b"\xff\xd8"):
                    return "o imagine JPEG de pe pagina %d e coruptă" % (pno + 1)
                if "FlateDecode" in filt and raw[:1] != b"\x78":
                    return "o imagine comprimată de pe pagina %d e coruptă" % (pno + 1)
    except Exception as e:
        return "verificarea a eșuat (%s)" % e
    finally:
        try:
            doc.close()
        except Exception:
            pass
    return None


def shrink_fonts(doc):
    """Pastreaza in fisier doar literele chiar folosite. Reduce mult marimea."""
    try:
        doc.subset_fonts(verbose=False)
    except Exception:
        pass


def apply_redactions(page):
    """Sterge textul marcat, fara sa distruga imaginile si liniile de sub el."""
    try:
        page.apply_redactions(images=0, graphics=0)
    except TypeError:
        try:
            page.apply_redactions(images=0)
        except TypeError:
            page.apply_redactions()


def erase_area(page, rect):
    """Scoate din fisier tot ce se afla in dreptunghi.

    Spre deosebire de apply_redactions, aici dispar si imaginile, si
    desenele vectoriale — pentru coduri QR, sigle, stampile. Desenele
    care doar ating marginea raman intregi, ca sa nu taiem chenarul
    paginii sau liniile tabelului de alaturi.
    """
    page.add_redact_annot(rect, fill=False)
    try:
        page.apply_redactions(images=pymupdf.PDF_REDACT_IMAGE_REMOVE,
                              graphics=pymupdf.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
                              text=pymupdf.PDF_REDACT_TEXT_REMOVE)
    except (TypeError, AttributeError):
        page.apply_redactions()


def parse_ranges(s, total):
    """'1-3, 7, 10-' -> set de indici 0-based."""
    out = set()
    for part in re.split(r"[,;]", s):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d*)", part)
        if m:
            a = int(m.group(1))
            b = int(m.group(2)) if m.group(2) else total
            for i in range(min(a, b), max(a, b) + 1):
                if 1 <= i <= total:
                    out.add(i - 1)
            continue
        m = re.fullmatch(r"-\s*(\d+)", part)
        if m:
            for i in range(1, int(m.group(1)) + 1):
                if 1 <= i <= total:
                    out.add(i - 1)
            continue
        if part.isdigit():
            i = int(part)
            if 1 <= i <= total:
                out.add(i - 1)
    return out


def find_tesseract():
    """Returneaza (cale exe, cale tessdata) sau (None, None)."""
    cands = []
    for d in (os.environ.get("PATH") or "").split(os.pathsep):
        if d.strip():
            cands.append(os.path.join(d.strip(), "tesseract.exe"))
    cands += [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Tesseract-OCR\tesseract.exe"),
    ]
    for p in cands:
        if p and os.path.isfile(p):
            td = os.environ.get("TESSDATA_PREFIX")
            if not td or not os.path.isdir(td):
                td = os.path.join(os.path.dirname(p), "tessdata")
            return p, (td if os.path.isdir(td) else None)
    return None, None


def arrow_icon(master, spre_dreapta, culoare=(52, 62, 80), marime=17):
    """O sageata curbata: anulare (spre stanga) sau refacere (spre dreapta).

    Simbolurile Unicode de undo/redo lipsesc din Segoe UI si Windows le
    inlocuieste cu doua arcuri care arata identic. Desenate aici, arata
    la fel pe orice calculator.
    """
    S = marime * 4
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # gros si cu varf mare: la 17 px o linie subtire dispare
    gros = max(3, int(S * 0.16))
    d.arc([S * 0.14, S * 0.22, S * 0.86, S * 0.94], start=185, end=355,
          fill=culoare + (255,), width=gros)
    x = S * 0.86 if spre_dreapta else S * 0.14
    y, h = S * 0.58, S * 0.30
    if spre_dreapta:
        varf = [(x + h * 0.45, y - h * 0.75), (x + h * 0.45, y + h * 0.55), (x - h * 0.85, y - h * 0.1)]
    else:
        varf = [(x - h * 0.45, y - h * 0.75), (x - h * 0.45, y + h * 0.55), (x + h * 0.85, y - h * 0.1)]
    d.polygon(varf, fill=culoare + (255,))
    return ImageTk.PhotoImage(im.resize((marime, marime), Image.LANCZOS), master=master)


def human_size(n):
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return ("%.0f %s" % (n, u)) if u == "B" else ("%.1f %s" % (n, u))
        n /= 1024.0


def open_in_explorer(path):
    try:
        if os.path.isdir(path):
            os.startfile(path)
        else:
            subprocess.Popen(["explorer", "/select,", os.path.normpath(path)])
    except Exception:
        pass


# --------------------------------------------------------------------------
# Dialog de progres
# --------------------------------------------------------------------------

class Progress:
    def __init__(self, parent, title, total):
        self.cancelled = False
        self.total = max(1, total)
        self.top = tk.Toplevel(parent)
        self.top.title(title)
        self.top.configure(bg=PANEL)
        self.top.resizable(False, False)
        self.top.transient(parent)
        self.top.grab_set()
        self.top.protocol("WM_DELETE_WINDOW", self.cancel)
        f = tk.Frame(self.top, bg=PANEL, padx=24, pady=20)
        f.pack()
        self.lbl = tk.Label(f, text=title, bg=PANEL, fg=INK,
                            font=("Segoe UI", 10), anchor="w", width=44)
        self.lbl.pack(anchor="w")
        self.bar = ttk.Progressbar(f, length=360, maximum=self.total, mode="determinate")
        self.bar.pack(pady=(10, 12))
        ttk.Button(f, text=t("Anulează"), command=self.cancel).pack()
        parent.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() - 420) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - 140) // 2
        self.top.geometry("+%d+%d" % (max(0, x), max(0, y)))
        self.top.update()

    def step(self, i, text=None):
        if text:
            self.lbl.config(text=text)
        self.bar["value"] = i
        self.top.update()
        return not self.cancelled

    def cancel(self):
        self.cancelled = True

    def close(self):
        try:
            self.top.grab_release()
            self.top.destroy()
        except Exception:
            pass


# --------------------------------------------------------------------------
# Aplicatia
# --------------------------------------------------------------------------

class PDFTool(_ROOT_BASE):

    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.configure(bg=BG)
        # porneste incadrat in ecran, chiar si pe laptopuri mici
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1360, sw - 60), min(880, sh - 80)
        self.geometry("%dx%d+%d+%d" % (w, h, max(0, (sw - w) // 2),
                                       max(0, (sh - h) // 3)))
        self.minsize(min(980, sw - 20), min(620, sh - 40))

        self.doc = None
        self.path = None
        self.dirty = False
        self.selected = set()
        self.current = 0
        self.undo_stack = []
        self.redo_stack = []
        self.thumb_imgs = {}
        self.thumb_labels = {}
        self.preview_img = None
        self.preview_scale = 1.0
        self.preview_off = (0, 0)
        self.click_mode = None          # None | "text" | "image" | "erase"
        self.zoom = None                # None = incadrat in fereastra
        self.edit_spans = []            # zonele de text de pe pagina curenta
        self.pan_from = None
        self.erase_from = None          # coltul de unde trag dreptunghiul de sters
        self.align_drag = None          # tragerea textului scris, ca sa-l aliniez
        self.src_broken = None          # fisierul era deja stricat la deschidere?
        self.speller = None             # corectorul Windows, daca exista dictionar
        self._spell_job = None
        self.stamp_path = None
        self._thumb_job = None
        self._preview_job = None

        set_lang(load_pref())

        self._setup_style()
        self._build_ui()
        self._bind_keys()
        self._enable_dnd()
        self._update_state()
        self.after(60, self.render_preview)

        if not guide_seen():
            self.after(500, self.first_run_guide)
        # intrebam abia dupa ce fereastra e pe ecran, si pe un fir separat
        self.after(1500, self._start_update_check)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # fisier dat ca argument in linia de comanda
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            self.after(120, lambda: self.load(sys.argv[1]))

    # ---------------------------------------------------------------- stil

    def _setup_style(self):
        s = ttk.Style(self)
        try:
            s.theme_use("clam")
        except Exception:
            pass
        s.configure(".", background=BG, foreground=INK, font=("Segoe UI", 9))
        s.configure("TFrame", background=BG)
        s.configure("Card.TFrame", background=PANEL)
        s.configure("TLabel", background=BG, foreground=INK)
        s.configure("Card.TLabel", background=PANEL, foreground=INK)
        s.configure("Muted.TLabel", background=PANEL, foreground=MUTED, font=("Segoe UI", 8))
        s.configure("Head.TLabel", background=PANEL, foreground=INK,
                    font=("Segoe UI Semibold", 9))
        s.configure("TButton", padding=(8, 5), relief="flat",
                    background="#e3e7ee", foreground=INK, borderwidth=0)
        s.map("TButton",
              background=[("active", "#d3d9e3"), ("disabled", "#eceef2")],
              foreground=[("disabled", "#a6adb9")])
        s.configure("Accent.TButton", background=ACCENT, foreground="white")
        s.map("Accent.TButton",
              background=[("active", ACCENT_DK), ("disabled", "#a9bff0")],
              foreground=[("disabled", "#eaf0fd")])
        s.configure("Danger.TButton", background="#fee2e2", foreground=DANGER)
        s.map("Danger.TButton", background=[("active", "#fecaca")])
        s.configure("TNotebook", background=BG, borderwidth=0)
        s.configure("TNotebook.Tab", padding=(9, 7), background="#dfe4ec",
                    foreground=MUTED, borderwidth=0)
        s.map("TNotebook.Tab",
              background=[("selected", PANEL)],
              foreground=[("selected", ACCENT)])
        s.configure("TCheckbutton", background=PANEL, foreground=INK)
        s.configure("TRadiobutton", background=PANEL, foreground=INK)
        s.configure("TEntry", fieldbackground="white", borderwidth=1)
        s.configure("TCombobox", fieldbackground="white")
        s.configure("Horizontal.TProgressbar", background=ACCENT,
                    troughcolor="#e3e7ee", borderwidth=0, thickness=8)
        s.configure("TScale", background=PANEL)
        s.configure("TSeparator", background=BORDER)
        s.configure("Vertical.TScrollbar", background="#c2c9d6",
                    troughcolor="#eef0f4", bordercolor="#eef0f4",
                    arrowcolor="#5b6473", borderwidth=0, relief="flat", width=13)
        s.map("Vertical.TScrollbar",
              background=[("active", "#a5aebe"), ("pressed", "#8d97a8")])

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        self._build_toolbar()
        self._build_status()

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=8, pady=(0, 0))

        self._build_thumbs(body)
        self._build_preview(body)
        self._build_tabs(body)

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG, height=52)
        bar.pack(fill="x", side="top", padx=8, pady=(8, 6))

        ttk.Button(bar, text=t("Deschide PDF"), style="Accent.TButton",
                   command=self.cmd_open).pack(side="left")
        self.btn_save = ttk.Button(bar, text=t("Salvează"), command=self.cmd_save)
        self.btn_save.pack(side="left", padx=(6, 0))
        self.btn_saveas = ttk.Button(bar, text=t("Salvează ca…"), command=self.cmd_save_as)
        self.btn_saveas.pack(side="left", padx=(6, 0))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)

        self.ico_undo = arrow_icon(self, False)
        self.ico_redo = arrow_icon(self, True)
        self.btn_undo = ttk.Button(bar, text=t("Anulează"), image=self.ico_undo,
                                   compound="left", command=self.undo)
        self.btn_undo.pack(side="left")
        self.btn_redo = ttk.Button(bar, text=t("Refă"), image=self.ico_redo,
                                   compound="left", command=self.redo)
        self.btn_redo.pack(side="left", padx=(6, 0))

        ttk.Separator(bar, orient="vertical").pack(side="left", fill="y", padx=10, pady=4)

        ttk.Button(bar, text=t("Închide fișierul"), command=self.cmd_close_doc).pack(side="left")

        self.lbl_file = tk.Label(bar, text=t("Niciun fișier deschis"), bg=BG, fg=MUTED,
                                 font=("Segoe UI", 9))
        self.lbl_file.pack(side="right", padx=(0, 4))

        self.cb_ui_lang = ttk.Combobox(bar, width=11, state="readonly",
                                       values=[LANG_NAMES[c] for c in LANG_ORDER])
        self.cb_ui_lang.set(LANG_NAMES.get(current(), "Rom\u00e2n\u0103"))
        self.cb_ui_lang.bind("<<ComboboxSelected>>", self.on_lang_change)
        self.cb_ui_lang.pack(side="right", padx=(10, 12))
        ttk.Button(bar, text="?", width=3,
                   command=self.show_guide).pack(side="right")
        ttk.Button(bar, text="FAQ", width=5,
                   command=self.show_faq).pack(side="right", padx=(0, 4))

    def _build_thumbs(self, parent):
        wrap = tk.Frame(parent, bg=BORDER, bd=0)
        wrap.pack(side="left", fill="y", padx=(0, 8))
        inner = tk.Frame(wrap, bg=PANEL)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        hdr = tk.Frame(inner, bg=PANEL)
        hdr.pack(fill="x", padx=8, pady=(8, 4))
        tk.Label(hdr, text=t("Pagini"), bg=PANEL, fg=INK,
                 font=("Segoe UI Semibold", 9)).pack(side="left")
        self.lbl_selcount = tk.Label(hdr, text="", bg=PANEL, fg=ACCENT,
                                     font=("Segoe UI", 8))
        self.lbl_selcount.pack(side="right")

        cwrap = tk.Frame(inner, bg=PANEL)
        cwrap.pack(fill="both", expand=True)
        self.tcanvas = tk.Canvas(cwrap, bg=PANEL, width=THUMB_W + 46,
                                 highlightthickness=0, bd=0)
        tsb = ttk.Scrollbar(cwrap, orient="vertical", command=self.tcanvas.yview)
        self.tcanvas.configure(yscrollcommand=lambda *a: (tsb.set(*a), self._queue_thumbs()))
        tsb.pack(side="right", fill="y")
        self.tcanvas.pack(side="left", fill="both", expand=True)
        self.tframe = tk.Frame(self.tcanvas, bg=PANEL)
        self.tcanvas.create_window((0, 0), window=self.tframe, anchor="nw")
        self.tframe.bind("<Configure>",
                         lambda e: self.tcanvas.configure(scrollregion=self.tcanvas.bbox("all")))
        self.tcanvas.bind("<MouseWheel>", self._thumb_wheel)
        self.tframe.bind("<MouseWheel>", self._thumb_wheel)

        btns = tk.Frame(inner, bg=PANEL)
        btns.pack(fill="x", padx=6, pady=6)
        ttk.Button(btns, text=t("Toate"),
                   command=lambda: self.select_set(set(range(self.npages)))
                   ).pack(side="left", fill="x", expand=True)
        ttk.Button(btns, text=t("Niciuna"),
                   command=lambda: self.select_set(set())
                   ).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btns, text=t("Invers"),
                   command=lambda: self.select_set(
                       set(range(self.npages)) - self.selected)
                   ).pack(side="left", fill="x", expand=True)

    def _build_preview(self, parent):
        wrap = tk.Frame(parent, bg=BORDER)
        wrap.pack(side="left", fill="both", expand=True, padx=(0, 8))
        inner = tk.Frame(wrap, bg=CANVAS_BG)
        inner.pack(fill="both", expand=True, padx=1, pady=1)

        nav = tk.Frame(inner, bg=PANEL, height=34)
        nav.pack(fill="x", side="bottom")
        ttk.Button(nav, text="◀", width=3,
                   command=lambda: self.goto(self.current - 1)).pack(side="left", padx=(8, 2), pady=4)
        ttk.Button(nav, text="▶", width=3,
                   command=lambda: self.goto(self.current + 1)).pack(side="left", padx=2, pady=4)
        self.lbl_page = tk.Label(nav, text="—", bg=PANEL, fg=INK, font=("Segoe UI", 9))
        self.lbl_page.pack(side="left", padx=10)

        ttk.Separator(nav, orient="vertical").pack(side="left", fill="y", padx=8, pady=7)
        ttk.Button(nav, text="−", width=3,
                   command=lambda: self.zoom_by(1 / 1.25)).pack(side="left", pady=4)
        self.lbl_zoom = tk.Label(nav, text="—", bg=PANEL, fg=MUTED,
                                 font=("Segoe UI", 8), width=6)
        self.lbl_zoom.pack(side="left")
        ttk.Button(nav, text="+", width=3,
                   command=lambda: self.zoom_by(1.25)).pack(side="left", pady=4)
        ttk.Button(nav, text=t("Încadrează"),
                   command=lambda: self.set_zoom(None)).pack(side="left", padx=6, pady=4)

        self.lbl_hint = tk.Label(nav, text="", bg=PANEL, fg=ACCENT, font=("Segoe UI", 8))
        self.lbl_hint.pack(side="right", padx=10)

        holder = tk.Frame(inner, bg=CANVAS_BG)
        holder.pack(fill="both", expand=True)
        self.pvsb = ttk.Scrollbar(holder, orient="vertical")
        self.phsb = ttk.Scrollbar(holder, orient="horizontal")
        self.pcanvas = tk.Canvas(holder, bg=CANVAS_BG, highlightthickness=0, bd=0,
                                 xscrollcommand=self.phsb.set,
                                 yscrollcommand=self.pvsb.set)
        self.pvsb.config(command=self.pcanvas.yview)
        self.phsb.config(command=self.pcanvas.xview)
        self.phsb.pack(side="bottom", fill="x")
        self.pvsb.pack(side="right", fill="y")
        self.pcanvas.pack(side="left", fill="both", expand=True)

        self.pcanvas.bind("<Configure>", lambda e: self._queue_preview())
        self.pcanvas.bind("<Button-1>", self.on_preview_press)
        self.pcanvas.bind("<B1-Motion>", self.on_preview_drag)
        self.pcanvas.bind("<ButtonRelease-1>", self.on_preview_release)
        self.pcanvas.bind("<Motion>", self.on_preview_motion)
        self.pcanvas.bind("<MouseWheel>", self.on_preview_wheel)
        self.pcanvas.bind("<Shift-MouseWheel>", lambda e:
                          self.pcanvas.xview_scroll(int(-e.delta / 120), "units"))

    def _build_tabs(self, parent):
        wrap = tk.Frame(parent, bg=BG, width=386)
        wrap.pack(side="left", fill="y")
        wrap.pack_propagate(False)

        self.nb = ttk.Notebook(wrap)
        self.nb.pack(fill="both", expand=True)
        self.nb.bind("<<NotebookTabChanged>>", lambda e: self._tab_changed())

        self.tab_pages = self._scroll_tab(t("Pagini"))
        self.tab_add = self._scroll_tab(t("Adaugă"))
        self.tab_text = self._scroll_tab(t("Editare"))
        self.tab_extract = self._scroll_tab(t("Extrage"))

        self._build_tab_pages(self.tab_pages)
        self._build_tab_add(self.tab_add)
        self._build_tab_text(self.tab_text)
        self._build_tab_extract(self.tab_extract)

        for tb in (self.tab_pages, self.tab_add, self.tab_text, self.tab_extract):
            self._bind_wheel(tb, tb._wheel)

    def _bind_wheel(self, widget, fn):
        """Rotita mouse-ului sa functioneze peste tot in panoul lateral."""
        for w in widget.winfo_children():
            if isinstance(w, (tk.Text, tk.Scale, ttk.Combobox, ttk.Spinbox)):
                continue
            w.bind("<MouseWheel>", fn)
            self._bind_wheel(w, fn)

    def _scroll_tab(self, title):
        outer = tk.Frame(self.nb, bg=PANEL)
        self.nb.add(outer, text=title)
        holder = tk.Frame(outer, bg=PANEL)
        holder.pack(fill="both", expand=True)
        cv = tk.Canvas(holder, bg=PANEL, highlightthickness=0, bd=0)
        sb = ttk.Scrollbar(holder, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        f = tk.Frame(cv, bg=PANEL)
        win = cv.create_window((0, 0), window=f, anchor="nw")
        f.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.bind("<Configure>", lambda e: cv.itemconfig(win, width=e.width))

        def wheel(e):
            cv.yview_scroll(int(-e.delta / 120), "units")
        for w in (cv, f):
            w.bind("<MouseWheel>", wheel)
        f._wheel = wheel
        return f

    def _autowrap(self, lbl, parent, margin=30):
        """Textul se reincadreaza singur cand panoul isi schimba latimea."""
        parent.bind("<Configure>",
                    lambda e, w=lbl, m=margin: w.config(
                        wraplength=max(120, e.width - m)),
                    add="+")
        return lbl

    def _section(self, parent, title, sub=None):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", pady=(12, 0))
        tk.Label(parent, text=title.upper(), bg=PANEL, fg=MUTED,
                 font=("Segoe UI Semibold", 8)).pack(anchor="w", padx=12, pady=(10, 2))
        if sub:
            lb = tk.Label(parent, text=sub, bg=PANEL, fg=MUTED, font=("Segoe UI", 8),
                          justify="left", anchor="w")
            lb.pack(anchor="w", fill="x", padx=12, pady=(0, 4))
            self._autowrap(lb, parent)
        box = tk.Frame(parent, bg=PANEL)
        box.pack(fill="x", padx=12, pady=(2, 6))
        return box

    def _build_status(self):
        st = tk.Frame(self, bg=BG, height=26)
        st.pack(fill="x", side="bottom", padx=10, pady=(2, 6))
        self.lbl_status = tk.Label(st, text=t("Gata."), bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.lbl_status.pack(side="left")
        tk.Label(st, text=COPYRIGHT % datetime.date.today().year,
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="right")
        # ca sa se stie dintr-o privire ce versiune ruleaza; click = detalii
        self.lbl_ver = tk.Label(st, text="%s %s" % (APP_NAME, APP_VER),
                                bg=BG, fg=MUTED, font=("Segoe UI", 8), cursor="hand2")
        self.lbl_ver.pack(side="right", padx=(0, 14))
        self.lbl_ver.bind("<Button-1>", lambda e: self.show_about())
        # anuntul unei versiuni noi, cand exista; altfel nu se vede
        self.lbl_nou = tk.Label(st, text="", bg=BG, fg=ACCENT,
                                font=("Segoe UI", 8, "bold"), cursor="hand2")
        self.lbl_nou.pack(side="right", padx=(0, 14))
        self.lbl_nou.bind("<Button-1>", lambda e: self._deschide_versiunea())

    # ---------------------------------------------- corector ortografic

    def _spell_setup(self):
        """Ia corectorul pentru limba interfetei, daca Windows il are."""
        vechi = getattr(self, "speller", None)
        if vechi:
            try:
                vechi.close()
            except Exception:
                pass
        self.speller = None
        try:
            self.speller = spell.corector_pentru(current())
        except Exception:
            self.speller = None

    def _spell_later(self, _e=None):
        """Verifica dupa ce te opresti din scris, nu la fiecare tasta."""
        if not self.speller:
            return
        if self._spell_job:
            try:
                self.after_cancel(self._spell_job)
            except Exception:
                pass
        self._spell_job = self.after(350, self._spell_check)

    def _spell_check(self):
        self._spell_job = None
        if not self.speller:
            return
        try:
            text = self.txt_edit.get("1.0", "end-1c")
            self.txt_edit.tag_remove("gresit", "1.0", "end")
            for start, lung, _cuv in self.speller.greseli(text):
                self.txt_edit.tag_add("gresit",
                                      "1.0 + %d chars" % start,
                                      "1.0 + %d chars" % (start + lung))
        except Exception:
            pass

    def _spell_menu(self, event):
        """Click dreapta pe un cuvant subliniat: variantele propuse."""
        if not self.speller:
            return
        try:
            poz = self.txt_edit.index("@%d,%d" % (event.x, event.y))
            if "gresit" not in self.txt_edit.tag_names(poz):
                return
            a = self.txt_edit.tag_prevrange("gresit", poz + " +1c")
            if not a:
                return
            cuvant = self.txt_edit.get(a[0], a[1])
            variante = self.speller.sugestii(cuvant)
        except Exception:
            return

        meniu = tk.Menu(self, tearoff=0)
        if variante:
            for v in variante:
                meniu.add_command(
                    label=v,
                    command=lambda x=v, i=a: self._spell_replace(i, x))
        else:
            meniu.add_command(label=t("Nicio sugestie"), state="disabled")
        try:
            meniu.tk_popup(event.x_root, event.y_root)
        finally:
            meniu.grab_release()
        return "break"

    def _spell_replace(self, interval, cuvant):
        try:
            self.txt_edit.delete(interval[0], interval[1])
            self.txt_edit.insert(interval[0], cuvant)
            self._spell_check()
        except Exception:
            pass

    def _in_textbox(self):
        """Cursorul e in caseta de editare?"""
        try:
            return self.focus_get() is self.txt_edit
        except Exception:
            return False

    def _undo_key(self, _e=None):
        if self._in_textbox():
            return                      # caseta isi face singura undo
        self.undo()
        return "break"

    def _redo_key(self, _e=None):
        if self._in_textbox():
            return
        self.redo()
        return "break"

    def _select_all_key(self, _e=None):
        if self._in_textbox():
            return
        self.select_set(set(range(self.npages)))
        return "break"

    def _select_all_text(self, _e=None):
        self.txt_edit.tag_add("sel", "1.0", "end-1c")
        self.txt_edit.mark_set("insert", "1.0")
        return "break"

    def _bind_keys(self):
        self.bind("<Control-o>", lambda e: self.cmd_open())
        self.bind("<Control-s>", lambda e: self.cmd_save())
        self.bind("<Control-S>", lambda e: self.cmd_save_as())
        self.bind("<Control-z>", self._undo_key)
        self.bind("<Control-y>", self._redo_key)
        self.bind("<Control-a>", self._select_all_key)
        self.bind("<Delete>", lambda e: self.op_delete())
        self.bind("<Prior>", lambda e: self.goto(self.current - 1))
        self.bind("<Next>", lambda e: self.goto(self.current + 1))
        self.bind("<Escape>", lambda e: self.set_click_mode(None))

    # -------------------------------------------------------------- TAB 1

    def _build_tab_pages(self, f):
        b = self._section(f, t("Selecție"),
                          t("Click pe miniaturi pentru a selecta. Sau scrie un interval, ex: 1-3, 7, 10-"))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        self.e_range = ttk.Entry(row)
        self.e_range.pack(side="left", fill="x", expand=True)
        self.e_range.bind("<Return>", lambda e: self.apply_range())
        ttk.Button(row, text=t("Aplică"), command=self.apply_range).pack(side="left", padx=(6, 0))
        r2 = tk.Frame(b, bg=PANEL)
        r2.pack(fill="x", pady=(6, 0))
        ttk.Button(r2, text=t("Pagini pare"), command=lambda: self.select_set(
            {i for i in range(self.npages) if i % 2 == 1})).pack(side="left")
        ttk.Button(r2, text=t("Pagini impare"), command=lambda: self.select_set(
            {i for i in range(self.npages) if i % 2 == 0})).pack(side="left", padx=6)

        b = self._section(f, t("Rotire"))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        ttk.Button(row, text=t("90° stânga"), command=lambda: self.op_rotate(-90)).pack(side="left")
        ttk.Button(row, text=t("90° dreapta"), command=lambda: self.op_rotate(90)).pack(side="left", padx=6)
        ttk.Button(row, text=t("180°"), command=lambda: self.op_rotate(180)).pack(side="left")

        b = self._section(f, t("Ordine și ștergere"))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        ttk.Button(row, text=t("▲ Mută sus"), command=lambda: self.op_move(-1)).pack(side="left")
        ttk.Button(row, text=t("▼ Mută jos"), command=lambda: self.op_move(1)).pack(side="left", padx=6)
        ttk.Button(row, text=t("Șterge"), style="Danger.TButton",
                   command=self.op_delete).pack(side="left")

        b = self._section(f, t("Unire"), t("Adaugă paginile altui PDF în documentul curent."))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        ttk.Button(row, text=t("Adaugă PDF la final…"),
                   command=lambda: self.op_merge("end")).pack(side="left")
        ttk.Button(row, text=t("Inserează aici…"),
                   command=lambda: self.op_merge("here")).pack(side="left", padx=6)

        b = self._section(f, t("Împărțire"))
        ttk.Button(b, text=t("Salvează paginile selectate ca PDF nou…"),
                   style="Accent.TButton", command=self.op_extract_sel).pack(fill="x")
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        tk.Label(row, text=t("Împarte la fiecare"), bg=PANEL, fg=INK).pack(side="left")
        self.sp_split = ttk.Spinbox(row, from_=1, to=9999, width=5)
        self.sp_split.set(1)
        self.sp_split.pack(side="left", padx=6)
        tk.Label(row, text=t("pagini"), bg=PANEL, fg=INK).pack(side="left")
        ttk.Button(b, text=t("Împarte în fișiere separate…"),
                   command=self.op_split).pack(fill="x", pady=(6, 0))

    # -------------------------------------------------------------- TAB 2

    def _build_tab_add(self, f):
        # --- filigran
        b = self._section(f, t("Filigran (watermark)"))
        self.e_wm = ttk.Entry(b)
        self.e_wm.insert(0, "CONFIDENȚIAL")
        self.e_wm.pack(fill="x")

        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(8, 0))
        tk.Label(row, text=t("Mărime"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.sc_wm_size = tk.Scale(row, from_=8, to=140, orient="horizontal", bg=PANEL,
                                   highlightthickness=0, bd=0, troughcolor="#e3e7ee",
                                   showvalue=True, length=150)
        self.sc_wm_size.set(52)
        self.sc_wm_size.pack(side="left", fill="x", expand=True)

        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        tk.Label(row, text=t("Transparență"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.sc_wm_op = tk.Scale(row, from_=5, to=100, orient="horizontal", bg=PANEL,
                                 highlightthickness=0, bd=0, troughcolor="#e3e7ee", length=150)
        self.sc_wm_op.set(22)
        self.sc_wm_op.pack(side="left", fill="x", expand=True)

        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        tk.Label(row, text=t("Unghi"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.sc_wm_rot = tk.Scale(row, from_=-90, to=90, orient="horizontal", bg=PANEL,
                                  highlightthickness=0, bd=0, troughcolor="#e3e7ee", length=150)
        self.sc_wm_rot.set(45)
        self.sc_wm_rot.pack(side="left", fill="x", expand=True)

        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        tk.Label(row, text=t("Culoare"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.wm_color = "#ff0000"
        self.btn_wm_color = tk.Button(row, bg=self.wm_color, width=4, relief="flat",
                                      bd=0, command=self.pick_wm_color, cursor="hand2")
        self.btn_wm_color.pack(side="left")
        self.v_wm_tile = tk.BooleanVar(value=False)
        ttk.Checkbutton(row, text=t("Repetat pe toată pagina"),
                        variable=self.v_wm_tile).pack(side="left", padx=10)

        self.v_wm_scope = tk.StringVar(value="all")
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        ttk.Radiobutton(row, text=t("Toate paginile"), value="all",
                        variable=self.v_wm_scope).pack(side="left")
        ttk.Radiobutton(row, text=t("Doar selecția"), value="sel",
                        variable=self.v_wm_scope).pack(side="left", padx=10)
        ttk.Button(b, text=t("Aplică filigranul"), style="Accent.TButton",
                   command=self.op_watermark).pack(fill="x", pady=(8, 0))

        # --- numerotare
        b = self._section(f, t("Numerotare pagini"),
                          t("Folosește {n} pentru numărul paginii și {total} pentru total."))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        tk.Label(row, text=t("Format"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.e_num_fmt = ttk.Entry(row)
        self.e_num_fmt.insert(0, "{n} / {total}")
        self.e_num_fmt.pack(side="left", fill="x", expand=True)

        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        tk.Label(row, text=t("Începe de la"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.sp_num_start = ttk.Spinbox(row, from_=0, to=99999, width=6)
        self.sp_num_start.set(1)
        self.sp_num_start.pack(side="left")
        tk.Label(row, text=t("Sari peste primele"), bg=PANEL, fg=INK).pack(side="left", padx=(10, 4))
        self.sp_num_skip = ttk.Spinbox(row, from_=0, to=9999, width=4)
        self.sp_num_skip.set(0)
        self.sp_num_skip.pack(side="left")

        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        tk.Label(row, text=t("Mărime"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.sp_num_size = ttk.Spinbox(row, from_=5, to=48, width=5)
        self.sp_num_size.set(10)
        self.sp_num_size.pack(side="left")
        tk.Label(row, text=t("Culoare"), bg=PANEL, fg=INK).pack(side="left", padx=(10, 4))
        self.num_color = "#333333"
        self.btn_num_color = tk.Button(row, bg=self.num_color, width=4, relief="flat", bd=0,
                                       command=self.pick_num_color, cursor="hand2")
        self.btn_num_color.pack(side="left")

        tk.Label(b, text=t("Poziție"), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8)).pack(anchor="w", pady=(8, 2))
        self.v_num_pos = tk.StringVar(value="bc")
        self._pos_grid(b, self.v_num_pos)
        ttk.Button(b, text=t("Numerotează paginile"), style="Accent.TButton",
                   command=self.op_numbering).pack(fill="x", pady=(8, 0))

        # --- imagine / semnatura
        b = self._section(f, t("Imagine / semnătură / ștampilă"),
                          t("Alege o imagine (PNG cu fundal transparent arată cel mai bine), "
                          "apoi dă click pe pagină unde vrei s-o pui."))
        self.lbl_stamp = tk.Label(b, text=t("Nicio imagine aleasă"), bg=PANEL, fg=MUTED,
                                  font=("Segoe UI", 8), anchor="w", justify="left")
        self.lbl_stamp.pack(fill="x")
        self._autowrap(self.lbl_stamp, b, 6)
        ttk.Button(b, text=t("Alege imagine…"), command=self.pick_stamp).pack(fill="x", pady=(6, 0))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(8, 0))
        tk.Label(row, text=t("Lățime"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.sc_stamp_w = tk.Scale(row, from_=20, to=500, orient="horizontal", bg=PANEL,
                                   highlightthickness=0, bd=0, troughcolor="#e3e7ee", length=150)
        self.sc_stamp_w.set(140)
        self.sc_stamp_w.pack(side="left", fill="x", expand=True)
        self.btn_place = ttk.Button(b, text=t("Plasează prin click pe pagină"),
                                    style="Accent.TButton", command=self.toggle_place)
        self.btn_place.pack(fill="x", pady=(6, 0))
        ttk.Button(b, text=t("Pune pe toate paginile selectate (colț dreapta-jos)"),
                   command=self.op_stamp_all).pack(fill="x", pady=(6, 0))

    def _pos_grid(self, parent, var):
        g = tk.Frame(parent, bg=PANEL)
        g.pack(anchor="w")
        labels = [("ts", "sus stg"), ("tc", "sus"), ("td", "sus dr"),
                  ("ms", "mij stg"), ("mc", "mijloc"), ("md", "mij dr"),
                  ("bs", "jos stg"), ("bc", "jos"), ("bd", "jos dr")]
        for i, (val, txt) in enumerate(labels):
            ttk.Radiobutton(g, text=txt, value=val, variable=var).grid(
                row=i // 3, column=i % 3, sticky="w", padx=(0, 8))

    # -------------------------------------------------------------- TAB 3

    def _build_tab_text(self, f):
        b = self._section(
            f, t("Editare text direct în PDF"),
            t("Atenție: PDF-ul nu păstrează text editabil ca Word. Aplicația acoperă "
            "textul vechi și îl rescrie cu un font asemănător. Merge bine pentru "
            "corecturi scurte (date, nume, sume). Nu rearanjează restul paragrafului."))
        self.btn_edit_mode = ttk.Button(b, text=t("Pornește modul editare"),
                                        style="Accent.TButton", command=self.toggle_edit)
        self.btn_edit_mode.pack(fill="x")
        tk.Label(b, text=t("Apoi dă click pe textul din previzualizare."),
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

        b = self._section(f, t("Textul selectat"))
        self.txt_edit = tk.Text(b, height=5, wrap="word", font=("Segoe UI", 10),
                                relief="solid", bd=1, highlightthickness=0,
                                undo=True, autoseparators=True, maxundo=-1)
        self.txt_edit.pack(fill="x")
        # in casuta, scurtaturile lucreaza pe text, nu pe document
        self.txt_edit.bind("<Control-a>", self._select_all_text)
        self.txt_edit.bind("<Control-A>", self._select_all_text)
        self.txt_edit.tag_config("gresit", underline=True, underlinefg="#d92d20")
        self.txt_edit.bind("<KeyRelease>", self._spell_later)
        self.txt_edit.bind("<Button-3>", self._spell_menu)
        self._spell_setup()
        self.lbl_editinfo = tk.Label(b, text="—", bg=PANEL, fg=MUTED, font=("Segoe UI", 8),
                                     anchor="w", justify="left")
        self.lbl_editinfo.pack(fill="x", pady=(4, 0))
        self._autowrap(self.lbl_editinfo, b, 6)
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        self.btn_apply_text = ttk.Button(row, text=t("Aplică modificarea"),
                                         style="Accent.TButton", command=self.op_apply_text)
        self.btn_apply_text.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text=t("Aruncă"),
                   command=self.discard_edit).pack(side="left", padx=(6, 0))

        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        tk.Label(row, text=t("Aliniere fină"), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8)).pack(side="left", padx=(0, 6))
        for eticheta, dx, dy in (("\u2190", -0.25, 0), ("\u2192", 0.25, 0),
                                 ("\u2191", 0, -0.25), ("\u2193", 0, 0.25)):
            ttk.Button(row, text=eticheta, width=3,
                       command=lambda a=dx, b2=dy: self.nudge_text(a, b2)).pack(
                           side="left", padx=(0, 3))
        tk.Label(row, text=t("mută textul scris"), bg=PANEL, fg=MUTED,
                 font=("Segoe UI", 8)).pack(side="left", padx=(6, 0))

        b = self._section(f, t("Caută și înlocuiește"),
                          t("Înlocuiește un text în tot documentul sau doar în paginile selectate."))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        tk.Label(row, text=t("Caută"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.e_find = ttk.Entry(row)
        self.e_find.pack(side="left", fill="x", expand=True)
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(5, 0))
        tk.Label(row, text=t("Înlocuiește"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.e_repl = ttk.Entry(row)
        self.e_repl.pack(side="left", fill="x", expand=True)
        self.v_repl_scope = tk.StringVar(value="all")
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        ttk.Radiobutton(row, text=t("Tot documentul"), value="all",
                        variable=self.v_repl_scope).pack(side="left")
        ttk.Radiobutton(row, text=t("Doar selecția"), value="sel",
                        variable=self.v_repl_scope).pack(side="left", padx=10)
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        ttk.Button(row, text=t("Numără aparițiile"), command=self.op_count).pack(side="left")
        ttk.Button(row, text=t("Înlocuiește tot"), style="Accent.TButton",
                   command=self.op_replace).pack(side="left", padx=(6, 0))

        b = self._section(f, t("Ascunde definitiv (redactare)"),
                          t("Șterge complet textul din fișier și pune o bandă neagră peste. "
                          "Textul nu mai poate fi recuperat."))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        self.e_redact = ttk.Entry(row)
        self.e_redact.pack(side="left", fill="x", expand=True)
        ttk.Button(row, text=t("Ascunde"), style="Danger.TButton",
                   command=self.op_redact).pack(side="left", padx=(6, 0))

        b = self._section(
            f, t("Șterge o zonă din pagină"),
            t("Pentru ce nu e text: cod QR, siglă, ștampilă. Trage un dreptunghi "
            "peste zonă în previzualizare și dispare din fișier cu totul — nu e "
            "doar acoperit."))
        self.btn_erase = ttk.Button(b, text=t("Alege o zonă de șters"),
                                    style="Danger.TButton", command=self.toggle_erase)
        self.btn_erase.pack(fill="x")
        tk.Label(b, text=t("Ce doar atinge marginea zonei rămâne întreg."),
                 bg=PANEL, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(4, 0))

    # -------------------------------------------------------------- TAB 4

    def _build_tab_extract(self, f):
        self.v_ex_scope = tk.StringVar(value="all")

        b = self._section(f, t("Ce pagini"))
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        ttk.Radiobutton(row, text=t("Tot documentul"), value="all",
                        variable=self.v_ex_scope).pack(side="left")
        ttk.Radiobutton(row, text=t("Doar selecția"), value="sel",
                        variable=self.v_ex_scope).pack(side="left", padx=10)

        b = self._section(f, t("Text"))
        ttk.Button(b, text=t("Salvează textul ca .txt…"), style="Accent.TButton",
                   command=self.op_export_text).pack(fill="x")
        ttk.Button(b, text=t("Arată textul paginii curente"),
                   command=self.op_show_text).pack(fill="x", pady=(6, 0))

        b = self._section(f, t("Tabele"),
                          t("Detectează tabelele și le salvează ca .csv (se deschid în Excel)."))
        ttk.Button(b, text=t("Caută și salvează tabelele…"),
                   command=self.op_export_tables).pack(fill="x")

        b = self._section(f, t("Imagini"))
        ttk.Button(b, text=t("Extrage imaginile din PDF…"),
                   command=self.op_export_images).pack(fill="x")
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x", pady=(6, 0))
        tk.Label(row, text=t("Calitate (DPI)"), bg=PANEL, fg=INK).pack(side="left")
        self.sp_dpi = ttk.Spinbox(row, from_=72, to=600, increment=24, width=6)
        self.sp_dpi.set(200)
        self.sp_dpi.pack(side="left", padx=6)
        ttk.Button(b, text=t("Salvează paginile ca imagini PNG…"),
                   command=self.op_pages_to_png).pack(fill="x", pady=(6, 0))

        b = self._section(f, t("OCR — documente scanate"),
                          t("Citește textul din pagini scanate (poze). Necesită Tesseract OCR "
                          "instalat separat pe calculator."))
        self.lbl_ocr = tk.Label(b, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 8),
                                anchor="w", justify="left")
        self.lbl_ocr.pack(fill="x", pady=(0, 6))
        self._autowrap(self.lbl_ocr, b, 6)
        row = tk.Frame(b, bg=PANEL)
        row.pack(fill="x")
        tk.Label(row, text=t("Limba"), bg=PANEL, fg=INK, width=12, anchor="w").pack(side="left")
        self.cb_lang = ttk.Combobox(row, values=["ron", "ron+eng", "eng", "fra", "deu", "ita"],
                                    width=10, state="readonly")
        self.cb_lang.set("ron+eng")
        self.cb_lang.pack(side="left")
        self.btn_ocr_text = ttk.Button(b, text=t("Extrage textul prin OCR…"),
                                       style="Accent.TButton", command=self.op_ocr_text)
        self.btn_ocr_text.pack(fill="x", pady=(6, 0))
        self.btn_ocr_pdf = ttk.Button(b, text=t("Fă PDF-ul căutabil (OCR)…"),
                                      command=self.op_ocr_pdf)
        self.btn_ocr_pdf.pack(fill="x", pady=(6, 0))
        self.btn_ocr_help = ttk.Button(b, text=t("Cum instalez Tesseract?"),
                                       command=self.show_ocr_help)
        self.btn_ocr_help.pack(fill="x", pady=(6, 0))
        self.refresh_ocr_state()

        b = self._section(f, t("Optimizare"))
        ttk.Button(b, text=t("Comprimă PDF-ul (salvează ca…)"),
                   command=self.op_compress).pack(fill="x")
        ttk.Button(b, text=t("Informații despre document"),
                   command=self.op_info).pack(fill="x", pady=(6, 0))

    # ------------------------------------------------------------ helpers

    @property
    def npages(self):
        return self.doc.page_count if self.doc else 0

    def status(self, msg):
        self.lbl_status.config(text=msg)
        self.update_idletasks()

    def need_doc(self):
        if not self.doc:
            messagebox.showinfo(APP_NAME, t("Deschide întâi un fișier PDF."))
            return False
        return True

    def target_pages(self, scope_var=None, default_all=True):
        """Paginile pe care se aplica operatia."""
        if scope_var is not None and scope_var.get() == "sel":
            if not self.selected:
                messagebox.showinfo(APP_NAME, t("Nu ai selectat nicio pagină.\n"
                                              "Dă click pe miniaturi în stânga."))
                return None
            return sorted(self.selected)
        if scope_var is None and self.selected:
            return sorted(self.selected)
        return list(range(self.npages)) if default_all else sorted(self.selected)

    # ------------------------------------------------------- deschide/salv

    def cmd_open(self):
        p = filedialog.askopenfilename(
            title=t("Deschide PDF"),
            filetypes=[("Fișiere PDF", "*.pdf"), ("Toate fișierele", "*.*")])
        if p:
            self.load(p)

    def load(self, path):
        if not self.confirm_discard():
            return
        try:
            # citim tot in memorie: documentul nu ramane legat de fisierul
            # de pe disc, deci salvarea peste el nu-l poate desincroniza
            with open(path, "rb") as fh:
                raw = fh.read()
            doc = pymupdf.open("pdf", raw)
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot deschide fișierul:\n\n%s") % e)
            return
        if doc.needs_pass:
            pw = SimpleAsk(self, t("Fișier protejat"),
                           t("PDF-ul are parolă. Scrie parola:"), show="*").result
            if not pw or not doc.authenticate(pw):
                messagebox.showerror(APP_NAME, t("Parolă greșită. Fișierul nu a fost deschis."))
                doc.close()
                return
        if self.doc:
            try:
                self.doc.close()
            except Exception:
                pass
        self.src_broken = check_pdf(raw)
        self.doc = doc
        self.path = path
        self.dirty = False
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.selected.clear()
        self.current = 0
        self.clear_edit()
        self.set_click_mode(None)
        self.rebuild_thumbs()
        self.render_preview()
        self._update_state()
        self.status(t("Deschis: %s — %d pagini") % (os.path.basename(path), self.npages))
        if self.src_broken:
            messagebox.showwarning(
                APP_NAME,
                t("Fișierul are o problemă încă dinainte de a-l deschide:\n\n%s\n\n"
                  "Poți lucra pe el, dar unele programe îl pot refuza. "
                  "Salvează-l sub alt nume, ca să păstrezi originalul.")
                % self.src_broken)

    def cmd_close_doc(self):
        if not self.doc:
            return
        if not self.confirm_discard():
            return
        try:
            self.doc.close()
        except Exception:
            pass
        self.doc = None
        self.path = None
        self.dirty = False
        self.selected.clear()
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.rebuild_thumbs()
        self.render_preview()
        self._update_state()
        self.status(t("Gata."))

    def cmd_save(self):
        if not self.need_doc():
            return
        self.commit_pending_edit()
        if not self.path:
            return self.cmd_save_as()
        try:
            shrink_fonts(self.doc)
            data = self.doc.tobytes(garbage=3, deflate=True)
            rau = check_pdf(data)
            if rau and not self.src_broken:
                # era bun cand l-am deschis: nu scriem ce am stricat noi
                messagebox.showerror(APP_NAME, t("Nu pot salva:\n\n%s") % rau)
                return

            # continutul dinainte, pentru copie — citit acum, cat e intact
            vechi = None
            bak = backup_path(self.path)
            if not os.path.exists(bak):
                try:
                    with open(self.path, "rb") as fh:
                        vechi = fh.read()
                except Exception:
                    vechi = None

            # intai salvam; abia daca a mers, facem copia
            write_atomic(self.path, data)
            if vechi:
                try:
                    write_atomic(bak, vechi)
                except Exception:
                    pass                      # copia e un plus, nu o conditie
        except PermissionError:
            if messagebox.askyesno(
                    APP_NAME,
                    t("Fișierul e deschis în alt program (de exemplu Acrobat), "
                      "așa că NU a fost salvat.\n\nÎl salvez sub alt nume?")):
                self.cmd_save_as()
            return
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot salva:\n\n%s") % e)
            return
        self.dirty = False
        self._update_state()
        self.status(t("Salvat în %s  (copie de siguranță: %s)")
                    % (self.path, os.path.basename(backup_path(self.path))))

    def cmd_save_as(self):
        if not self.need_doc():
            return
        self.commit_pending_edit()
        base = os.path.splitext(os.path.basename(self.path or "document.pdf"))[0]
        p = filedialog.asksaveasfilename(
            title=t("Salvează ca"), defaultextension=".pdf",
            initialfile=base + "-modificat.pdf",
            filetypes=[("Fișiere PDF", "*.pdf")])
        if not p:
            return
        try:
            shrink_fonts(self.doc)
            data = self.doc.tobytes(garbage=3, deflate=True)
            rau = check_pdf(data)
            if rau and not self.src_broken:
                messagebox.showerror(APP_NAME, t("Nu pot salva:\n\n%s") % rau)
                return
            write_atomic(p, data)
        except PermissionError:
            messagebox.showerror(
                APP_NAME,
                t("Fișierul e deschis în alt program (de exemplu Acrobat), "
                  "așa că NU a fost salvat.\n\nÎnchide-l acolo, sau alege alt nume."))
            return
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot salva:\n\n%s") % e)
            return
        self.path = p
        self.dirty = False
        self._update_state()
        self.status(t("Salvat: %s") % p)
        if messagebox.askyesno(APP_NAME, t("Salvat.\n\nDeschid folderul?")):
            open_in_explorer(p)

    def confirm_discard(self):
        if not self.dirty:
            return True
        a = messagebox.askyesnocancel(
            APP_NAME, t("Ai modificări nesalvate.\n\nVrei să le salvezi?"))
        if a is None:
            return False
        if a:
            self.cmd_save()
            return not self.dirty
        return True

    def _cancel_jobs(self):
        """Opreste sarcinile programate, ca sa nu se execute dupa inchidere."""
        for nume in ("_spell_job", "_thumb_job", "_preview_job"):
            job = getattr(self, nume, None)
            if job:
                try:
                    self.after_cancel(job)
                except Exception:
                    pass
                setattr(self, nume, None)

    def destroy(self):
        self._cancel_jobs()
        try:
            if getattr(self, "speller", None):
                self.speller.close()
        except Exception:
            pass
        super().destroy()

    def on_close(self):
        if self.confirm_discard():
            self.destroy()

    # ---------------------------------------------------------- undo/redo

    def snapshot(self):
        if not self.doc:
            return
        try:
            self.undo_stack.append((self.doc.tobytes(), set(self.selected), self.current))
        except Exception:
            return
        if len(self.undo_stack) > UNDO_MAX:
            self.undo_stack.pop(0)
        self.redo_stack.clear()

    def _restore(self, snap):
        data, sel, cur = snap
        try:
            self.doc.close()
        except Exception:
            pass
        self.doc = pymupdf.open("pdf", data)
        self.selected = set(i for i in sel if i < self.npages)
        self.current = min(cur, max(0, self.npages - 1))
        self.clear_edit()
        self.rebuild_thumbs()
        self.render_preview()
        self._update_state()

    def undo(self):
        if not self.undo_stack:
            return
        try:
            self.redo_stack.append((self.doc.tobytes(), set(self.selected), self.current))
        except Exception:
            pass
        self._restore(self.undo_stack.pop())
        self.dirty = True
        self.status(t("Am anulat ultima modificare."))

    def redo(self):
        if not self.redo_stack:
            return
        self.undo_stack.append((self.doc.tobytes(), set(self.selected), self.current))
        self._restore(self.redo_stack.pop())
        self.dirty = True
        self.status(t("Am refăcut modificarea."))

    def changed(self, msg=""):
        self.dirty = True
        self.rebuild_thumbs()
        self.render_preview()
        self._update_state()
        if msg:
            self.status(msg)

    def _update_state(self):
        has = self.doc is not None
        for w in (self.btn_save, self.btn_saveas):
            w.state(["!disabled"] if has else ["disabled"])
        self.btn_undo.state(["!disabled"] if self.undo_stack else ["disabled"])
        self.btn_redo.state(["!disabled"] if self.redo_stack else ["disabled"])
        if has:
            name = os.path.basename(self.path) if self.path else "(nesalvat)"
            if len(name) > 32:
                name = name[:15] + "…" + name[-15:]
            mark = " •" if self.dirty else ""
            self.lbl_file.config(text=t("%s%s   —   %d pagini") % (name, mark, self.npages))
            self.lbl_page.config(text=t("Pagina %d din %d") % (self.current + 1, self.npages))
        else:
            self.lbl_file.config(text=t("Niciun fișier deschis"))
            self.lbl_page.config(text="—")
        n = len(self.selected)
        self.lbl_selcount.config(text=(t("%d selectate") % n) if n else "")
        self.title("%s%s — %s" % (
            os.path.basename(self.path) if self.path else APP_NAME,
            " •" if self.dirty else "",
            APP_NAME) if has else APP_NAME)

    # ------------------------------------------------------------ thumbs

    def rebuild_thumbs(self):
        for w in self.tframe.winfo_children():
            w.destroy()
        self.thumb_imgs.clear()
        self.thumb_labels.clear()
        if not self.doc:
            return
        for i in range(self.npages):
            try:
                r = self.doc.load_page(i).rect
                ratio = (r.height / r.width) if r.width else 1.4
            except Exception:
                ratio = 1.4
            h = max(40, int(THUMB_W * ratio))
            holder = tk.Frame(self.tframe, bg=PANEL, padx=6, pady=4)
            holder.pack()
            card = tk.Frame(holder, bg=BORDER, bd=0,
                            highlightthickness=2, highlightbackground=PANEL)
            card.pack()
            blank = tk.PhotoImage(width=THUMB_W, height=h, master=self)
            lbl = tk.Label(card, image=blank, bg="#f4f5f7", width=THUMB_W, height=h,
                           cursor="hand2", bd=0)
            lbl._blank = blank
            lbl.pack(padx=1, pady=1)
            num = tk.Label(holder, text=str(i + 1), bg=PANEL, fg=MUTED,
                           font=("Segoe UI", 8))
            num.pack()
            for w in (lbl, num, holder, card):
                w.bind("<Button-1>", lambda e, i=i: self.on_thumb_click(i, e))
                w.bind("<MouseWheel>", self._thumb_wheel)
            self.thumb_labels[i] = (lbl, card, num, holder)
        self.tframe.update_idletasks()
        self.tcanvas.configure(scrollregion=self.tcanvas.bbox("all"))
        self.paint_selection()
        self._queue_thumbs()

    def _thumb_wheel(self, e):
        self.tcanvas.yview_scroll(int(-e.delta / 120), "units")
        self._queue_thumbs()

    def _queue_thumbs(self):
        if self._thumb_job:
            try:
                self.after_cancel(self._thumb_job)
            except Exception:
                pass
        self._thumb_job = self.after(70, self._render_visible_thumbs)

    def _render_visible_thumbs(self):
        self._thumb_job = None
        if not self.doc:
            return
        top = self.tcanvas.canvasy(0)
        bot = top + self.tcanvas.winfo_height()
        for i, (lbl, card, num, holder) in list(self.thumb_labels.items()):
            if i in self.thumb_imgs:
                continue
            try:
                y0 = holder.winfo_y()
                y1 = y0 + holder.winfo_height()
            except Exception:
                continue
            if y1 < top - 300 or y0 > bot + 300:
                continue
            try:
                page = self.doc.load_page(i)
                z = THUMB_W / max(1.0, page.rect.width)
                pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
                img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
                ph = ImageTk.PhotoImage(img, master=self.tcanvas)
                self.thumb_imgs[i] = ph
                lbl.config(image=ph, width=pix.width, height=pix.height)
            except Exception:
                continue

    def paint_selection(self):
        for i, (lbl, card, num, holder) in self.thumb_labels.items():
            sel = i in self.selected
            cur = i == self.current
            if sel:
                card.config(highlightbackground=ACCENT, highlightthickness=2)
                num.config(fg=ACCENT, font=("Segoe UI Semibold", 8))
            elif cur:
                card.config(highlightbackground="#9aa4b4", highlightthickness=2)
                num.config(fg=INK, font=("Segoe UI", 8))
            else:
                card.config(highlightbackground=PANEL, highlightthickness=2)
                num.config(fg=MUTED, font=("Segoe UI", 8))
        self._update_state()

    def on_thumb_click(self, i, event=None):
        shift = bool(event and (event.state & 0x0001))
        if shift and self.selected:
            a, b = min(self.current, i), max(self.current, i)
            self.selected |= set(range(a, b + 1))
        else:
            if i in self.selected:
                self.selected.discard(i)
            else:
                self.selected.add(i)
        self.current = i
        self.paint_selection()
        self.render_preview()
        self.scroll_to_thumb(i)

    def select_set(self, s):
        if not self.doc:
            return
        self.selected = set(s)
        self.paint_selection()

    def apply_range(self):
        if not self.need_doc():
            return
        s = self.e_range.get().strip()
        if not s:
            return
        sel = parse_ranges(s, self.npages)
        if not sel:
            messagebox.showinfo(APP_NAME, t("Nu am înțeles intervalul.\nExemple: 1-3, 7, 10-"))
            return
        self.select_set(sel)
        self.status(t("Selectate %d pagini.") % len(sel))

    def scroll_to_thumb(self, i):
        item = self.thumb_labels.get(i)
        if not item:
            return
        holder = item[3]
        try:
            total = self.tframe.winfo_height()
            y = holder.winfo_y()
            h = self.tcanvas.winfo_height()
            top = self.tcanvas.canvasy(0)
            if y < top or y + holder.winfo_height() > top + h:
                self.tcanvas.yview_moveto(max(0, (y - h / 3) / max(1, total)))
                self._queue_thumbs()
        except Exception:
            pass

    # ----------------------------------------------------------- preview

    def goto(self, i):
        if not self.doc:
            return
        i = max(0, min(self.npages - 1, i))
        if i == self.current:
            return
        self.commit_pending_edit()
        self.current = i
        self.clear_edit()
        self.load_text_spans()
        self.paint_selection()
        self.render_preview()
        self.scroll_to_thumb(i)

    def _queue_preview(self):
        if self._preview_job:
            try:
                self.after_cancel(self._preview_job)
            except Exception:
                pass
        self._preview_job = self.after(120, self.render_preview)

    def fit_scale(self, page):
        cw = max(50, self.pcanvas.winfo_width())
        ch = max(50, self.pcanvas.winfo_height())
        r = page.rect
        z = min((cw - 28) / max(1.0, r.width), (ch - 28) / max(1.0, r.height))
        return max(0.05, min(z, 8.0))

    def set_zoom(self, z):
        self.zoom = None if z is None else max(0.10, min(8.0, z))
        self.render_preview()

    def zoom_by(self, k):
        if self.doc:
            self.set_zoom((self.preview_scale or 1.0) * k)

    def render_preview(self):
        self._preview_job = None
        self.pcanvas.delete("all")
        if not self.doc or self.npages == 0:
            self.preview_img = None
            self.pcanvas.configure(scrollregion=(0, 0, 0, 0))
            self.lbl_zoom.config(text="—")
            self._draw_empty_hint()
            return
        self.current = max(0, min(self.current, self.npages - 1))
        try:
            page = self.doc.load_page(self.current)
            z = self.zoom or self.fit_scale(page)
            pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
            img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            self.preview_img = ImageTk.PhotoImage(img, master=self.pcanvas)
        except Exception:
            return
        cw = max(50, self.pcanvas.winfo_width())
        ch = max(50, self.pcanvas.winfo_height())
        pad = 12
        w = max(cw, pix.width + 2 * pad)
        h = max(ch, pix.height + 2 * pad)
        ox, oy = (w - pix.width) // 2, (h - pix.height) // 2
        self.preview_scale = z
        self.preview_off = (ox, oy)
        self.pcanvas.configure(scrollregion=(0, 0, w, h))
        self.pcanvas.create_rectangle(ox + 4, oy + 4, ox + pix.width + 5, oy + pix.height + 5,
                                      fill="#6e7684", outline="")
        self.pcanvas.create_image(ox, oy, image=self.preview_img, anchor="nw")
        if self.click_mode == "text":
            self._draw_text_zones()
        self.lbl_zoom.config(text="%d%%" % round(z * 100))
        self._update_state()

    def _draw_empty_hint(self):
        cw = max(50, self.pcanvas.winfo_width())
        ch = max(50, self.pcanvas.winfo_height())
        self.pcanvas.create_text(cw // 2, ch // 2 - 12, text=t("Trage aici un fișier PDF"),
                                 fill="#eceff4", font=("Segoe UI", 15))
        self.pcanvas.create_text(cw // 2, ch // 2 + 15,
                                 text=t("sau apasă „Deschide PDF”"),
                                 fill="#ccd2dc", font=("Segoe UI", 10))

    def load_text_spans(self):
        """Zonele de text de pe pagina curenta, pentru modul editare."""
        self.edit_spans = []
        if not self.doc or self.click_mode != "text":
            return
        try:
            d = self.doc.load_page(self.current).get_text("dict")
        except Exception:
            return
        for blk in d.get("blocks", []):
            if blk.get("type") != 0:
                continue
            for line in blk.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("text", "").strip():
                        self.edit_spans.append(span)

    def _draw_text_zones(self):
        ox, oy = self.preview_off
        z = self.preview_scale
        for span in self.edit_spans:
            x0, y0, x1, y1 = span["bbox"]
            self.pcanvas.create_rectangle(ox + x0 * z - 1, oy + y0 * z - 1,
                                          ox + x1 * z + 1, oy + y1 * z + 1,
                                          fill=ACCENT, stipple="gray12",
                                          outline="#8fb0f5", width=1, tags="zone")

    def _span_at(self, x, y):
        pt = pymupdf.Point(x, y)
        for span in self.edit_spans:
            r = pymupdf.Rect(span["bbox"])
            if pymupdf.Rect(r.x0 - 2, r.y0 - 2, r.x1 + 2, r.y1 + 2).contains(pt):
                return span
        return None

    def canvas_to_pdf(self, cx, cy):
        ox, oy = self.preview_off
        return ((cx - ox) / self.preview_scale, (cy - oy) / self.preview_scale)

    def _scrollable(self):
        try:
            x0, y0, x1, y1 = [float(v) for v in str(
                self.pcanvas.cget("scrollregion")).split()]
        except Exception:
            return False
        return (x1 - x0 > self.pcanvas.winfo_width() + 2 or
                y1 - y0 > self.pcanvas.winfo_height() + 2)

    def on_preview_wheel(self, e):
        if e.state & 0x0004:                       # Ctrl apasat = zoom
            self.zoom_by(1.15 if e.delta > 0 else 1 / 1.15)
        else:
            self.pcanvas.yview_scroll(int(-e.delta / 120), "units")

    def on_preview_press(self, e):
        if self.click_mode == "erase":
            self.erase_from = (self.pcanvas.canvasx(e.x), self.pcanvas.canvasy(e.y))
            self.pcanvas.delete("erase")
            return
        if self.click_mode == "text" and self._peste_scrisul_meu(e):
            # poate fi tragere, poate fi doar click: decidem la miscare
            self.align_drag = {"de_la": (self.pcanvas.canvasx(e.x),
                                         self.pcanvas.canvasy(e.y)), "mutat": False}
            return
        if self.click_mode:
            self.on_preview_click(e)
            return
        if self._scrollable():
            self.pan_from = (e.x, e.y)
            self.pcanvas.scan_mark(e.x, e.y)

    def on_preview_drag(self, e):
        if self.align_drag:
            x0, y0 = self.align_drag["de_la"]
            x1, y1 = self.pcanvas.canvasx(e.x), self.pcanvas.canvasy(e.y)
            if abs(x1 - x0) > 3 or abs(y1 - y0) > 3:
                self.align_drag["mutat"] = True
            z = self._zona_scrisului()
            if z is not None:
                ox, oy = self.preview_off
                m = self.preview_scale
                self.pcanvas.delete("align")
                self.pcanvas.create_rectangle(
                    ox + z.x0 * m + (x1 - x0), oy + z.y0 * m + (y1 - y0),
                    ox + z.x1 * m + (x1 - x0), oy + z.y1 * m + (y1 - y0),
                    outline=ACCENT, width=2, dash=(3, 2), tags="align")
            return
        if self.erase_from:
            x0, y0 = self.erase_from
            self.pcanvas.delete("erase")
            self.pcanvas.create_rectangle(
                x0, y0, self.pcanvas.canvasx(e.x), self.pcanvas.canvasy(e.y),
                outline=DANGER, width=2, dash=(4, 3), tags="erase")
            return
        if self.pan_from:
            self.pcanvas.scan_dragto(e.x, e.y, gain=1)

    def on_preview_release(self, e):
        if self.align_drag:
            a = self.align_drag
            self.align_drag = None
            self.pcanvas.delete("align")
            if not a["mutat"]:
                self.on_preview_click(e)          # a fost doar un click
                return
            x0, y0 = a["de_la"]
            m = self.preview_scale or 1
            self.nudge_text((self.pcanvas.canvasx(e.x) - x0) / m,
                            (self.pcanvas.canvasy(e.y) - y0) / m)
            return
        if self.erase_from:
            x0, y0 = self.erase_from
            self.erase_from = None
            self.pcanvas.delete("erase")
            self.erase_between(x0, y0, self.pcanvas.canvasx(e.x),
                               self.pcanvas.canvasy(e.y))
            return
        self.pan_from = None

    def on_preview_motion(self, e):
        if self.click_mode:
            self.pcanvas.config(cursor="crosshair")
        elif self._scrollable():
            self.pcanvas.config(cursor="fleur")
        else:
            self.pcanvas.config(cursor="")
        if self.click_mode == "text" and self.edit_spans:
            self.pcanvas.delete("hover")
            x, y = self.canvas_to_pdf(self.pcanvas.canvasx(e.x),
                                      self.pcanvas.canvasy(e.y))
            sp = self._span_at(x, y)
            if sp:
                ox, oy = self.preview_off
                z = self.preview_scale
                x0, y0, x1, y1 = sp["bbox"]
                self.pcanvas.create_rectangle(ox + x0 * z - 2, oy + y0 * z - 2,
                                              ox + x1 * z + 2, oy + y1 * z + 2,
                                              outline=ACCENT, width=2, tags="hover")

    def toggle_erase(self):
        if not self.need_doc():
            return
        self.set_click_mode(None if self.click_mode == "erase" else "erase")

    def erase_between(self, cx0, cy0, cx1, cy1):
        """Sterge tot ce se afla in dreptunghiul tras pe previzualizare."""
        if not self.doc:
            return
        x0, y0 = self.canvas_to_pdf(min(cx0, cx1), min(cy0, cy1))
        x1, y1 = self.canvas_to_pdf(max(cx0, cx1), max(cy0, cy1))
        page = self.doc.load_page(self.current)
        r = pymupdf.Rect(x0, y0, x1, y1) & page.rect
        if r.is_empty or r.width < 3 or r.height < 3:
            self.status(t("Zona e prea mică. Trage un dreptunghi peste ce vrei să ștergi."))
            return
        if not messagebox.askyesno(
                APP_NAME, t("Ștergi tot ce se află în zona aleasă?\n\n"
                          "Dispar din fișier textul, imaginile și desenele dinăuntru — "
                          "de exemplu un cod QR. Poți reveni cu butonul de anulare.")):
            return
        self.snapshot()
        try:
            erase_area(page, r)
        except Exception as ex:
            self.undo()
            messagebox.showerror(APP_NAME, t("Eroare la ștergere:\n\n%s") % ex)
            return
        self.thumb_imgs.clear()
        self.set_click_mode(None)
        self.changed(t("Am șters zona aleasă de pe pagina %d.") % (self.current + 1))

    def set_click_mode(self, mode):
        if mode != "text" and self.click_mode == "text":
            self.commit_pending_edit()
        self.click_mode = mode
        if mode == "text":
            self.btn_edit_mode.config(text=t("Oprește modul editare"))
            self.lbl_hint.config(text=t("Click pe text ca să-l modifici"))
        elif mode == "image":
            self.btn_place.config(text=t("Anulează plasarea"))
            self.lbl_hint.config(text=t("Click unde vrei imaginea"))
        elif mode == "erase":
            self.btn_erase.config(text=t("Renunță la ștergere"))
            self.lbl_hint.config(text=t("Trage un dreptunghi peste ce vrei să ștergi"))
        else:
            self.btn_edit_mode.config(text=t("Pornește modul editare"))
            self.btn_place.config(text=t("Plasează prin click pe pagină"))
            self.btn_erase.config(text=t("Alege o zonă de șters"))
            self.lbl_hint.config(text="")
        self.pcanvas.config(cursor="crosshair" if mode else "")
        self.load_text_spans()
        self.render_preview()

    def on_preview_click(self, e):
        if not self.doc or not self.click_mode:
            return
        x, y = self.canvas_to_pdf(self.pcanvas.canvasx(e.x), self.pcanvas.canvasy(e.y))
        page = self.doc.load_page(self.current)
        if not (0 <= x <= page.rect.width and 0 <= y <= page.rect.height):
            return
        if self.click_mode == "text":
            self.pick_text_at(page, x, y)
        elif self.click_mode == "image":
            self.place_stamp_at(page, x, y)

    # ------------------------------------------------- versiune noua

    def _start_update_check(self):
        """La pornire, daca utilizatorul nu a oprit-o."""
        if not check_updates():
            return
        update_check.cauta(APP_VER, self._update_gasit)

    def _update_gasit(self, versiune, adresa):
        """Vine de pe firul de retea: trecem pe firul ferestrei."""
        try:
            self.after(0, lambda: self._arata_versiunea(versiune, adresa))
        except Exception:
            pass

    def _arata_versiunea(self, versiune, adresa):
        if not versiune:
            return
        self.nou_versiune = (versiune, adresa)
        try:
            self.lbl_nou.config(text=t("Versiune nouă: %s") % versiune)
        except Exception:
            pass

    def _deschide_versiunea(self):
        n = getattr(self, "nou_versiune", None)
        if not n:
            return
        try:
            webbrowser.open(n[1])
        except Exception:
            pass

    def show_about(self):
        """Ce versiune ruleaza, si ce pleaca de pe calculator."""
        w = tk.Toplevel(self)
        w.title(t("Despre și actualizări"))
        w.configure(bg=PANEL)
        w.transient(self)
        w.resizable(False, False)
        f = tk.Frame(w, bg=PANEL)
        f.pack(fill="both", expand=True, padx=18, pady=16)

        tk.Label(f, text="%s %s" % (APP_NAME, APP_VER), bg=PANEL, fg=INK,
                 font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(f, text=COPYRIGHT % datetime.date.today().year, bg=PANEL,
                 fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w", pady=(2, 12))

        tk.Label(f, text=t("Programul verifică dacă a apărut o versiune mai "
                         "nouă. Atât pleacă de pe calculator: o întrebare. "
                         "Nimic despre tine și nimic despre fișierele tale. Nu "
                         "descarcă și nu instalează nimic — hotărăști tu."),
                 bg=PANEL, fg=INK, font=("Segoe UI", 9), justify="left",
                 wraplength=380).pack(anchor="w")

        stare = tk.Label(f, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 9))
        stare.pack(anchor="w", pady=(12, 0))

        rand = tk.Frame(f, bg=PANEL)
        rand.pack(fill="x", pady=(10, 0))

        def raspuns(versiune, adresa):
            def pe_fereastra():
                if not stare.winfo_exists():
                    return
                if versiune is False:
                    stare.config(text=t("Nu am putut verifica. Ești offline sau "
                                      "serverul nu răspunde."), fg=MUTED)
                elif versiune is None:
                    stare.config(text=t("Ești la zi. %s e cea mai nouă.") % APP_VER,
                                 fg=MUTED)
                else:
                    self._arata_versiunea(versiune, adresa)
                    stare.config(text=t("Versiune nouă: %s") % versiune, fg=ACCENT)
                    b_desc.pack(side="left", padx=(8, 0))
            try:
                self.after(0, pe_fereastra)
            except Exception:
                pass

        def cauta_acum():
            stare.config(text=t("Verific…"), fg=MUTED)
            update_check.cauta(APP_VER, raspuns, si_daca_e_la_zi=True)

        ttk.Button(rand, text=t("Caută o versiune nouă acum"),
                   command=cauta_acum).pack(side="left")
        b_desc = ttk.Button(rand, text=t("Deschide pagina de descărcare"),
                            style="Accent.TButton", command=self._deschide_versiunea)

        v = tk.BooleanVar(value=check_updates())
        ttk.Checkbutton(f, text=t("Caută automat la pornire"), variable=v,
                        command=lambda: set_check_updates(v.get())).pack(
                            anchor="w", pady=(14, 0))

        n = getattr(self, "nou_versiune", None)
        if n:
            stare.config(text=t("Versiune nouă: %s") % n[0], fg=ACCENT)
            b_desc.pack(side="left", padx=(8, 0))

        ttk.Button(f, text=t("Închide"), command=w.destroy).pack(anchor="e", pady=(16, 0))
        w.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w.geometry("+%d+%d" % (max(0, (sw - w.winfo_width()) // 2),
                               max(0, (sh - w.winfo_height()) // 3)))

    # --------------------------------------------------------- ghidul

    def show_guide(self):
        TextViewer(self, APP_NAME, guide_text(current()), width=860, height=620)

    def show_faq(self):
        TextViewer(self, APP_NAME + " — FAQ", faq_text(current()),
                   width=880, height=640)

    def first_run_guide(self):
        """Se arata o singura data pe calculator, la prima pornire."""
        mark_guide_seen()
        self.show_guide()

    # ------------------------------------------------- limba interfetei

    def on_lang_change(self, _evt=None):
        name = self.cb_ui_lang.get()
        code = next((c for c in LANG_ORDER if LANG_NAMES[c] == name), None)
        if not code or code == current():
            return
        set_lang(code)
        save_pref(code)
        self.relayout()
        self._spell_setup()

    def relayout(self):
        """Reconstruieste toata interfata, pastrand documentul deschis."""
        doc, path, dirty = self.doc, self.path, self.dirty
        sel, cur, zoom = set(self.selected), self.current, self.zoom
        stamp = self.stamp_path
        for w in list(self.winfo_children()):
            w.destroy()
        self.thumb_imgs.clear()
        self.thumb_labels.clear()
        self.click_mode = None
        self.edit_spans = []
        self._thumb_job = None
        self._preview_job = None
        self._setup_style()
        self._build_ui()
        self.doc, self.path, self.dirty = doc, path, dirty
        self.selected, self.current, self.zoom = sel, cur, zoom
        self.stamp_path = stamp
        if stamp:
            self.lbl_stamp.config(text=os.path.basename(stamp), fg=INK)
        self.clear_edit()
        self.rebuild_thumbs()
        self.render_preview()
        self._update_state()

    # ----------------------------------------------------- drag and drop

    def _enable_dnd(self):
        if not HAS_DND:
            return
        try:
            self.drop_target_register(DND_FILES)
            self.dnd_bind("<<Drop>>", self.on_drop)
        except Exception:
            pass

    def on_drop(self, event):
        try:
            paths = list(self.tk.splitlist(event.data))
        except Exception:
            paths = [str(event.data)]
        files = [q.strip("{}").strip() for q in paths]
        files = [q for q in files if q and os.path.isfile(q)]
        if not files:
            return
        pdfs = [q for q in files if q.lower().endswith(".pdf")]
        imgs = [q for q in files if os.path.splitext(q)[1].lower() in
                (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff")]
        if pdfs:
            self.drop_pdfs(pdfs)
        elif imgs:
            self.stamp_path = imgs[0]
            self.lbl_stamp.config(text=os.path.basename(imgs[0]), fg=INK)
            self.nb.select(1)
            if self.doc:
                self.set_click_mode("image")
            self.status(t("Imaginea e pregătită — dă click pe pagină ca s-o pui."))
        else:
            messagebox.showinfo(APP_NAME, t("Pot folosi doar fișiere PDF și imagini."))

    def drop_pdfs(self, pdfs):
        if not self.doc:
            self.load(pdfs[0])
            for q in pdfs[1:]:
                self._append_pdf(q)
            return
        pick = ChoiceDialog(
            self, t("Fișier tras în aplicație"),
            t("Ce vrei să fac cu\n%s?") % os.path.basename(pdfs[0]),
            [(t("Deschide-l"), "open"),
             (t("Adaugă la finalul documentului"), "append")]).result
        if pick == "open":
            self.load(pdfs[0])
            for q in pdfs[1:]:
                self._append_pdf(q)
        elif pick == "append":
            for q in pdfs:
                self._append_pdf(q)

    def _append_pdf(self, path, at=None):
        try:
            src = pymupdf.open(path)
            if src.needs_pass:
                pw = SimpleAsk(self, t("Fișier protejat"),
                               t("Parola pentru %s:") % os.path.basename(path),
                               show="*").result
                if not pw or not src.authenticate(pw):
                    messagebox.showerror(APP_NAME, t("Parolă greșită."))
                    return
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot deschide fișierul:\n\n%s") % e)
            return
        self.snapshot()
        try:
            self.doc.insert_pdf(src, start_at=self.npages if at is None else at)
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot uni fișierele:\n\n%s") % e)
            return
        n = src.page_count
        src.close()
        self.thumb_imgs.clear()
        self.changed(t("Am adăugat %d pagini din %s.") % (n, os.path.basename(path)))

    # ------------------------------------------------------ op: pagini

    def op_rotate(self, deg):
        if not self.need_doc():
            return
        pages = self.target_pages()
        if pages is None:
            return
        self.snapshot()
        for i in pages:
            p = self.doc.load_page(i)
            p.set_rotation((p.rotation + deg) % 360)
        self.thumb_imgs.clear()
        self.changed(t("Am rotit %d pagini cu %d°.") % (len(pages), deg))

    def op_delete(self):
        if not self.doc or not self.selected:
            return
        if len(self.selected) >= self.npages:
            messagebox.showinfo(APP_NAME, t("Nu poți șterge toate paginile."))
            return
        if not messagebox.askyesno(APP_NAME, t("Ștergi %d pagini?") % len(self.selected)):
            return
        self.snapshot()
        for i in sorted(self.selected, reverse=True):
            self.doc.delete_page(i)
        n = len(self.selected)
        self.selected.clear()
        self.current = min(self.current, max(0, self.npages - 1))
        self.changed(t("Am șters %d pagini.") % n)

    def op_move(self, direction):
        if not self.doc or not self.selected:
            messagebox.showinfo(APP_NAME, t("Selectează întâi paginile de mutat."))
            return
        order = list(range(self.npages))
        sel = sorted(self.selected, reverse=(direction > 0))
        moved = False
        for pid in sel:
            pos = order.index(pid)
            npos = pos + direction
            if 0 <= npos < len(order) and order[npos] not in self.selected:
                order[pos], order[npos] = order[npos], order[pos]
                moved = True
        if not moved:
            return
        self.snapshot()
        self.doc.select(order)
        self.selected = {order.index(p) for p in sel}
        self.current = min(order.index(sel[0]), self.npages - 1)
        self.thumb_imgs.clear()
        self.changed(t("Am mutat paginile."))

    def op_merge(self, where):
        if not self.need_doc():
            return
        p = filedialog.askopenfilename(title=t("Alege PDF-ul de adăugat"),
                                       filetypes=[("Fișiere PDF", "*.pdf")])
        if not p:
            return
        try:
            src = pymupdf.open(p)
            if src.needs_pass:
                pw = SimpleAsk(self, t("Fișier protejat"), t("Parola pentru %s:")
                               % os.path.basename(p), show="*").result
                if not pw or not src.authenticate(pw):
                    messagebox.showerror(APP_NAME, t("Parolă greșită."))
                    return
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot deschide fișierul:\n\n%s") % e)
            return
        self.snapshot()
        at = self.npages if where == "end" else self.current + 1
        try:
            self.doc.insert_pdf(src, start_at=at)
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot uni fișierele:\n\n%s") % e)
            return
        added = src.page_count
        src.close()
        self.thumb_imgs.clear()
        self.changed(t("Am adăugat %d pagini din %s.") % (added, os.path.basename(p)))

    def op_extract_sel(self):
        if not self.doc or not self.selected:
            messagebox.showinfo(APP_NAME, t("Selectează întâi paginile."))
            return
        base = os.path.splitext(os.path.basename(self.path or "document.pdf"))[0]
        out = filedialog.asksaveasfilename(
            title=t("Salvează selecția"), defaultextension=".pdf",
            initialfile="%s-selectie.pdf" % base, filetypes=[("Fișiere PDF", "*.pdf")])
        if not out:
            return
        try:
            nd = pymupdf.open()
            nd.insert_pdf(self.doc)
            nd.select(sorted(self.selected))
            shrink_fonts(nd)
            nd.save(out, garbage=3, deflate=True)
            nd.close()
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Eroare:\n\n%s") % e)
            return
        self.status(t("Am salvat %d pagini în %s") % (len(self.selected), out))
        if messagebox.askyesno(APP_NAME, t("Gata. Deschid folderul?")):
            open_in_explorer(out)

    def op_split(self):
        if not self.need_doc():
            return
        try:
            step = max(1, int(self.sp_split.get()))
        except Exception:
            step = 1
        folder = filedialog.askdirectory(title=t("Unde salvez fișierele rezultate?"))
        if not folder:
            return
        base = os.path.splitext(os.path.basename(self.path or "document.pdf"))[0]
        chunks = [list(range(i, min(i + step, self.npages)))
                  for i in range(0, self.npages, step)]
        pr = Progress(self, t("Împart documentul…"), len(chunks))
        made = 0
        try:
            for k, pages in enumerate(chunks, 1):
                if not pr.step(k, "Fișierul %d din %d…" % (k, len(chunks))):
                    break
                nd = pymupdf.open()
                nd.insert_pdf(self.doc)
                nd.select(pages)
                suffix = ("%d" % (pages[0] + 1)) if step == 1 else \
                         ("%d-%d" % (pages[0] + 1, pages[-1] + 1))
                shrink_fonts(nd)
                nd.save(os.path.join(folder, "%s_%s.pdf" % (base, suffix)),
                        garbage=3, deflate=True)
                nd.close()
                made += 1
        except Exception as e:
            pr.close()
            messagebox.showerror(APP_NAME, t("Eroare:\n\n%s") % e)
            return
        pr.close()
        self.status(t("Am creat %d fișiere în %s") % (made, folder))
        if messagebox.askyesno(APP_NAME, t("Am creat %d fișiere.\n\nDeschid folderul?") % made):
            open_in_explorer(folder)

    # ------------------------------------------------------ op: adauga

    def pick_wm_color(self):
        c = colorchooser.askcolor(color=self.wm_color, title=t("Culoarea filigranului"))
        if c and c[1]:
            self.wm_color = c[1]
            self.btn_wm_color.config(bg=c[1])

    def pick_num_color(self):
        c = colorchooser.askcolor(color=self.num_color, title=t("Culoarea numerelor"))
        if c and c[1]:
            self.num_color = c[1]
            self.btn_num_color.config(bg=c[1])

    def op_watermark(self):
        if not self.need_doc():
            return
        text = self.e_wm.get().strip()
        if not text:
            messagebox.showinfo(APP_NAME, t("Scrie textul filigranului."))
            return
        pages = self.target_pages(self.v_wm_scope)
        if pages is None:
            return
        size = int(self.sc_wm_size.get())
        op = self.sc_wm_op.get() / 100.0
        ang = int(self.sc_wm_rot.get())
        col = hex_to_rgb(self.wm_color)
        tile = self.v_wm_tile.get()
        self.snapshot()
        try:
            for i in pages:
                page = self.doc.load_page(i)
                r = page.rect
                w = text_width(text, size)
                if tile:
                    stepx = max(w + 60, 120)
                    stepy = max(size * 3.2, 80)
                    y = stepy * 0.6
                    row = 0
                    while y < r.height + stepy:
                        x = -stepx * 0.5 + (stepx * 0.5 if row % 2 else 0)
                        while x < r.width + stepx:
                            pt = pymupdf.Point(x, y)
                            write_line(page, pt, text, size, col, angle=ang,
                                       opacity=op, pivot=pymupdf.Point(x + w / 2, y - size / 3))
                            x += stepx
                        y += stepy
                        row += 1
                else:
                    x = (r.width - w) / 2.0
                    y = r.height / 2.0 + size / 3.0
                    write_line(page, pymupdf.Point(x, y), text, size, col, angle=ang,
                               opacity=op, pivot=pymupdf.Point(r.width / 2, r.height / 2))
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Eroare la filigran:\n\n%s") % e)
            return
        self.thumb_imgs.clear()
        self.changed(t("Am pus filigranul pe %d pagini.") % len(pages))

    def op_numbering(self):
        if not self.need_doc():
            return
        fmt = self.e_num_fmt.get() or "{n}"
        try:
            start = int(self.sp_num_start.get())
            skip = int(self.sp_num_skip.get())
            size = int(self.sp_num_size.get())
        except Exception:
            messagebox.showinfo(APP_NAME, t("Verifică valorile numerice."))
            return
        col = hex_to_rgb(self.num_color)
        pos = self.v_num_pos.get()
        margin = 28
        self.snapshot()
        total = self.npages - skip
        try:
            for idx in range(skip, self.npages):
                page = self.doc.load_page(idx)
                r = page.rect
                n = start + (idx - skip)
                txt = fmt.replace("{n}", str(n)).replace("{total}", str(total)) \
                         .replace("{pagina}", str(n)).replace("{N}", str(n))
                w = text_width(txt, size)
                if pos[1] == "s":
                    x = margin
                elif pos[1] == "c":
                    x = (r.width - w) / 2.0
                else:
                    x = r.width - margin - w
                if pos[0] == "t":
                    y = margin
                elif pos[0] == "m":
                    y = r.height / 2.0
                else:
                    y = r.height - margin + size * 0.35
                write_line(page, pymupdf.Point(x, y), txt, size, col)
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Eroare la numerotare:\n\n%s") % e)
            return
        self.thumb_imgs.clear()
        self.changed(t("Am numerotat %d pagini.") % total)

    def pick_stamp(self):
        p = filedialog.askopenfilename(
            title=t("Alege imaginea"),
            filetypes=[("Imagini", "*.png *.jpg *.jpeg *.bmp *.gif *.tif *.tiff"),
                       ("Toate fișierele", "*.*")])
        if not p:
            return
        self.stamp_path = p
        self.lbl_stamp.config(text=os.path.basename(p), fg=INK)

    def toggle_place(self):
        if self.click_mode == "image":
            self.set_click_mode(None)
            return
        if not self.need_doc():
            return
        if not self.stamp_path:
            messagebox.showinfo(APP_NAME, t("Alege întâi o imagine."))
            return
        self.set_click_mode("image")

    def place_stamp_at(self, page, x, y):
        try:
            with Image.open(self.stamp_path) as im:
                iw, ih = im.size
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot citi imaginea:\n\n%s") % e)
            return
        w = float(self.sc_stamp_w.get())
        h = w * ih / max(1, iw)
        rect = pymupdf.Rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        self.snapshot()
        try:
            page.insert_image(rect, filename=self.stamp_path,
                              keep_proportion=True, overlay=True)
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot insera imaginea:\n\n%s") % e)
            return
        self.thumb_imgs.pop(self.current, None)
        self.set_click_mode(None)
        self.changed(t("Am pus imaginea pe pagina %d.") % (self.current + 1))

    def op_stamp_all(self):
        if not self.need_doc():
            return
        if not self.stamp_path:
            messagebox.showinfo(APP_NAME, t("Alege întâi o imagine."))
            return
        pages = self.target_pages()
        if pages is None:
            return
        try:
            with Image.open(self.stamp_path) as im:
                iw, ih = im.size
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Nu pot citi imaginea:\n\n%s") % e)
            return
        w = float(self.sc_stamp_w.get())
        h = w * ih / max(1, iw)
        m = 32
        self.snapshot()
        for i in pages:
            page = self.doc.load_page(i)
            r = page.rect
            rect = pymupdf.Rect(r.width - m - w, r.height - m - h, r.width - m, r.height - m)
            try:
                page.insert_image(rect, filename=self.stamp_path,
                                  keep_proportion=True, overlay=True)
            except Exception:
                continue
        self.thumb_imgs.clear()
        self.changed(t("Am pus imaginea pe %d pagini.") % len(pages))

    # -------------------------------------------------------- op: text

    def toggle_edit(self):
        if self.click_mode == "text":
            self.set_click_mode(None)
            return
        if not self.need_doc():
            return
        self.set_click_mode("text")
        self.status(t("Modul editare pornit — dă click pe textul din previzualizare."))

    def discard_edit(self):
        """Arunca ce e in caseta, fara sa aplice."""
        avea = self.pending_edit()
        self.clear_edit()
        self.render_preview()
        if avea:
            self.status(t("Am aruncat modificarea nesalvată."))

    def clear_edit(self):
        self.edit_target = None
        try:
            self.txt_edit.delete("1.0", "end")
            self.lbl_editinfo.config(text="—")
        except Exception:
            pass

    def pending_edit(self):
        """Textul din caseta difera de cel din pagina?"""
        tgt = getattr(self, "edit_target", None)
        if not tgt:
            return False
        try:
            acum = self.txt_edit.get("1.0", "end").rstrip("\n")
        except Exception:
            return False
        return acum != tgt["orig"]

    def _pare_stergere(self):
        """Modificarea arata ca o stergere din greseala?

        Adica textul nou e gol sau a pierdut cea mai mare parte din cel
        vechi. O corectura normala schimba cuvinte, nu sterge randul.
        """
        tgt = getattr(self, "edit_target", None)
        if not tgt:
            return False
        vechi = (tgt.get("orig") or "").strip()
        try:
            nou = self.txt_edit.get("1.0", "end").rstrip("\n").strip()
        except Exception:
            return False
        if len(vechi) < 5:
            return False                 # prea scurt ca sa judecam
        return len(nou) < len(vechi) * 0.4

    def commit_pending_edit(self):
        """Aplica modificarea lasata in caseta, daca exista.

        Se cheama cand utilizatorul pleaca de pe textul curent: alt text,
        alta pagina, iesire din modul editare. Asa nu se mai pierde ce ai
        scris. Daca modificarea arata insa ca o stergere accidentala,
        intrebam intai.
        """
        if not self.pending_edit():
            return
        if self._pare_stergere():
            tgt = self.edit_target
            nou = self.txt_edit.get("1.0", "end").rstrip("\n").strip()
            if not messagebox.askyesno(
                    APP_NAME,
                    t("Textul\n\n    %s\n\ndevine\n\n    %s\n\nAplic modificarea?")
                    % ((tgt.get("orig") or "").strip()[:70],
                       nou[:70] if nou else t("(nimic)"))):
                self.clear_edit()
                self.render_preview()
                return
        self.op_apply_text()

    def pick_text_at(self, page, x, y):
        # ce era in caseta se aplica, nu se arunca
        self.commit_pending_edit()
        self.load_text_spans()
        best = self._span_at(x, y)
        if not best:
            self.status(t("N-am găsit text acolo. Încearcă exact peste litere."))
            return
        self.edit_target = {
            "page": self.current,
            "rect": pymupdf.Rect(best["bbox"]),
            "size": best.get("size", 11),
            "font": best.get("font", ""),
            "color": int_color(best.get("color", 0)),
            "orig": norm_text(best.get("text", "")),
            "origin": tuple(best.get("origin") or ()) or None,
        }
        self.txt_edit.delete("1.0", "end")
        self.txt_edit.insert("1.0", norm_text(best.get("text", "")))
        self.txt_edit.edit_reset()      # nu duce istoricul textului anterior
        self._spell_later()
        self.lbl_editinfo.config(
            text=t("Pagina %d · font %s · mărime %.1f") %
                 (self.current + 1, best.get("font", "?"), best.get("size", 0)))
        self.nb.select(2)
        self.txt_edit.focus_set()
        self.status(t("Text selectat. Modifică-l și apasă „Aplică modificarea”."))

    def op_apply_text(self):
        tgt = getattr(self, "edit_target", None)
        if not tgt:
            messagebox.showinfo(APP_NAME, t("Selectează întâi un text: pornește modul "
                                          "editare și dă click pe el în previzualizare."))
            return
        new = self.txt_edit.get("1.0", "end").rstrip("\n")
        if new == tgt["orig"]:
            self.status(t("Textul e neschimbat."))
            return
        self.snapshot()
        page = self.doc.load_page(tgt["page"])
        rect = tgt["rect"]
        bg = bg_color_at(page, rect)
        try:
            page.add_redact_annot(rect, fill=bg)
            apply_redactions(page)
            if new.strip():
                org = tgt.get("origin")
                if org:
                    # exact pe linia de baza a textului vechi
                    write_baseline(page, org, new, tgt["size"], tgt["color"],
                                   kind=font_kind_for(tgt["font"]),
                                   maxw=page.rect.x1 - 2 - org[0])
                else:
                    grow = max(6.0, text_width(new, tgt["size"]) - rect.width + 6.0)
                    box = pymupdf.Rect(rect.x0 - 1, rect.y0 - 2,
                                       min(page.rect.x1 - 2, rect.x1 + grow), rect.y1 + 3)
                    used = textbox(page, box, new, tgt["size"], tgt["color"],
                                   kind=font_kind_for(tgt["font"]))
                    if used is None:
                        raise RuntimeError(t("Textul nou e prea lung pentru spațiul disponibil."))
        except Exception as e:
            self.undo()
            messagebox.showerror(APP_NAME, t("Nu am putut înlocui textul:\n\n%s") % e)
            return
        self.thumb_imgs.pop(tgt["page"], None)
        self.nudge_last = ({"page": tgt["page"], "rect": rect, "origin": tgt.get("origin"),
                            "text": new, "size": tgt["size"], "color": tgt["color"],
                            "font": tgt["font"], "dx": 0.0, "dy": 0.0}
                           if tgt.get("origin") and new.strip() else None)
        if self.nudge_last:
            self.lbl_hint.config(text=t("Poți trage textul scris ca să-l aliniezi"))
        vechi_scurt = (tgt.get("orig") or "").strip()[:32]
        nou_scurt = new.strip()[:32] or t("(nimic)")
        self.clear_edit()
        self.changed(t("Pagina %d: „%s” → „%s”") % (tgt["page"] + 1, vechi_scurt, nou_scurt))

    def _zona_scrisului(self):
        """Dreptunghiul in care sta acum textul scris ultima data.

        Textul nou poate fi mai lat decat cel vechi, deci nu ne luam doar
        dupa chenarul vechi: masuram si latimea lui adevarata.
        """
        n = getattr(self, "nudge_last", None)
        if not n or n["page"] != self.current:
            return None
        r = n["rect"]
        lat = max(r.width, text_width(n["text"], n["size"], font_kind_for(n["font"])))
        return pymupdf.Rect(r.x0 + n["dx"] - 2, r.y0 + n["dy"] - 2,
                            r.x0 + n["dx"] + lat + 2, r.y1 + n["dy"] + 2)

    def _peste_scrisul_meu(self, e):
        """Apasarea cade peste textul scris ultima data?"""
        z = self._zona_scrisului()
        if z is None:
            return False
        x, y = self.canvas_to_pdf(self.pcanvas.canvasx(e.x), self.pcanvas.canvasy(e.y))
        return z.contains(pymupdf.Point(x, y))

    def nudge_text(self, dx, dy):
        """Mut textul scris ultima data, ca sa cada exact pe rand."""
        n = getattr(self, "nudge_last", None)
        if not n or not self.doc:
            self.status(t("Modifică întâi un text, apoi îl poți alinia."))
            return
        if not self.undo_stack:
            return
        # inapoi la pagina dinainte de scriere, fara sa umplem stiva de refacere
        self._restore(self.undo_stack.pop())
        n["dx"] += dx
        n["dy"] += dy
        self.snapshot()
        page = self.doc.load_page(n["page"])
        try:
            page.add_redact_annot(n["rect"], fill=bg_color_at(page, n["rect"]))
            apply_redactions(page)
            org = (n["origin"][0] + n["dx"], n["origin"][1] + n["dy"])
            write_baseline(page, org, n["text"], n["size"], n["color"],
                           kind=font_kind_for(n["font"]),
                           maxw=page.rect.x1 - 2 - org[0])
        except Exception as e:
            self.undo()
            messagebox.showerror(APP_NAME, t("Nu am putut înlocui textul:\n\n%s") % e)
            return
        self.thumb_imgs.pop(n["page"], None)
        self.changed(t("Aliniere: %+.2f pe orizontală, %+.2f pe verticală.")
                     % (n["dx"], n["dy"]))

    def _replace_scope(self):
        return self.target_pages(self.v_repl_scope)

    def op_count(self):
        if not self.need_doc():
            return
        term = self.e_find.get()
        if not term:
            return
        pages = self._replace_scope()
        if pages is None:
            return
        total = 0
        hits = []
        for i in pages:
            n = len(self.doc.load_page(i).search_for(term))
            if n:
                hits.append("%d (×%d)" % (i + 1, n))
                total += n
        if not total:
            messagebox.showinfo(APP_NAME, t("Nu am găsit „%s”.") % term)
        else:
            messagebox.showinfo(APP_NAME, t("Am găsit %d apariții.\n\nPe paginile: %s")
                                % (total, ", ".join(hits[:40]) +
                                   (" …" if len(hits) > 40 else "")))

    def op_replace(self):
        if not self.need_doc():
            return
        term = self.e_find.get()
        new = self.e_repl.get()
        if not term:
            messagebox.showinfo(APP_NAME, t("Scrie textul de căutat."))
            return
        pages = self._replace_scope()
        if pages is None:
            return
        self.snapshot()
        pr = Progress(self, t("Înlocuiesc…"), len(pages))
        count = 0
        try:
            for k, i in enumerate(pages, 1):
                if not pr.step(k, "Pagina %d…" % (i + 1)):
                    break
                page = self.doc.load_page(i)
                rects = page.search_for(term)
                if not rects:
                    continue
                info = []
                d = page.get_text("dict")
                for r in rects:
                    size, color, font, baza = 11.0, (0, 0, 0), "", None
                    for blk in d.get("blocks", []):
                        if blk.get("type") != 0:
                            continue
                        for line in blk.get("lines", []):
                            for span in line.get("spans", []):
                                sr = pymupdf.Rect(span["bbox"])
                                if sr.intersects(r):
                                    size = span.get("size", 11)
                                    color = int_color(span.get("color", 0))
                                    font = span.get("font", "")
                                    org = span.get("origin")
                                    # acelasi rand, dar de unde incepe potrivirea
                                    if org:
                                        baza = (r.x0, org[1])
                                    break
                    info.append((r, size, color, font, bg_color_at(page, r), baza))
                for r, size, color, font, bg, baza in info:
                    page.add_redact_annot(r, fill=bg)
                apply_redactions(page)
                for r, size, color, font, bg, baza in info:
                    if new.strip():
                        if baza:
                            write_baseline(page, baza, new, size, color,
                                           kind=font_kind_for(font),
                                           maxw=page.rect.x1 - 2 - baza[0])
                        else:
                            grow = max(4.0, text_width(new, size) - r.width + 4.0)
                            box = pymupdf.Rect(r.x0 - 1, r.y0 - 2,
                                               min(page.rect.x1 - 2, r.x1 + grow), r.y1 + 3)
                            textbox(page, box, new, size, color, kind=font_kind_for(font))
                    count += 1
        except Exception as e:
            pr.close()
            self.undo()
            messagebox.showerror(APP_NAME, t("Eroare la înlocuire:\n\n%s") % e)
            return
        pr.close()
        if not count:
            self.undo_stack.pop()
            messagebox.showinfo(APP_NAME, t("Nu am găsit „%s”.") % term)
            self._update_state()
            return
        self.thumb_imgs.clear()
        self.changed(t("Am înlocuit %d apariții.") % count)

    def op_redact(self):
        if not self.need_doc():
            return
        term = self.e_redact.get()
        if not term:
            return
        if not messagebox.askyesno(
                APP_NAME, t("Ștergi definitiv toate aparițiile lui „%s”?\n\n"
                          "Textul va fi acoperit cu negru și scos din fișier.") % term):
            return
        self.snapshot()
        count = 0
        for i in range(self.npages):
            page = self.doc.load_page(i)
            rects = page.search_for(term)
            for r in rects:
                page.add_redact_annot(r, fill=(0, 0, 0))
                count += 1
            if rects:
                apply_redactions(page)
        if not count:
            self.undo_stack.pop()
            messagebox.showinfo(APP_NAME, t("Nu am găsit „%s”.") % term)
            self._update_state()
            return
        self.thumb_imgs.clear()
        self.changed(t("Am ascuns definitiv %d apariții.") % count)

    # ----------------------------------------------------- op: extrage

    def op_export_text(self):
        if not self.need_doc():
            return
        pages = self.target_pages(self.v_ex_scope)
        if pages is None:
            return
        base = os.path.splitext(os.path.basename(self.path or "document.pdf"))[0]
        out = filedialog.asksaveasfilename(
            title=t("Salvează textul"), defaultextension=".txt",
            initialfile=base + ".txt",
            filetypes=[("Fișier text", "*.txt")])
        if not out:
            return
        try:
            with open(out, "w", encoding="utf-8") as fh:
                for i in pages:
                    fh.write("\n===== Pagina %d =====\n\n" % (i + 1))
                    fh.write(norm_text(self.doc.load_page(i).get_text("text")))
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Eroare:\n\n%s") % e)
            return
        self.status(t("Text salvat: %s") % out)
        if messagebox.askyesno(APP_NAME, t("Gata. Deschid folderul?")):
            open_in_explorer(out)

    def op_show_text(self):
        if not self.need_doc():
            return
        txt = norm_text(self.doc.load_page(self.current).get_text("text"))
        if not txt.strip():
            messagebox.showinfo(APP_NAME,
                                t("Pagina nu conține text — probabil e o imagine scanată.\n\n"
                                "Folosește secțiunea OCR de mai jos."))
            return
        TextViewer(self, t("Text — pagina %d") % (self.current + 1), txt)

    def op_export_tables(self):
        if not self.need_doc():
            return
        pages = self.target_pages(self.v_ex_scope)
        if pages is None:
            return
        folder = filedialog.askdirectory(title=t("Unde salvez tabelele (.csv)?"))
        if not folder:
            return
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]
        pr = Progress(self, t("Caut tabele…"), len(pages))
        made = 0
        try:
            for k, i in enumerate(pages, 1):
                if not pr.step(k, "Pagina %d…" % (i + 1)):
                    break
                page = self.doc.load_page(i)
                try:
                    finder = page.find_tables()
                    tables = list(finder.tables)
                except Exception:
                    continue
                for ti, tab in enumerate(tables, 1):
                    try:
                        rows = tab.extract()
                    except Exception:
                        continue
                    if not rows:
                        continue
                    fn = os.path.join(folder, "%s_p%d_tabel%d.csv" % (base, i + 1, ti))
                    with open(fn, "w", newline="", encoding="utf-8-sig") as fh:
                        wcsv = csv.writer(fh, delimiter=";")
                        for row in rows:
                            wcsv.writerow(["" if c is None else
                                           norm_text(str(c)).replace("\n", " ")
                                           for c in row])
                    made += 1
        except Exception as e:
            pr.close()
            messagebox.showerror(APP_NAME, t("Eroare:\n\n%s") % e)
            return
        pr.close()
        if not made:
            messagebox.showinfo(APP_NAME, t("Nu am găsit tabele în paginile alese."))
            return
        self.status(t("Am salvat %d tabele în %s") % (made, folder))
        if messagebox.askyesno(APP_NAME, t("Am salvat %d tabele.\n\nDeschid folderul?") % made):
            open_in_explorer(folder)

    def op_export_images(self):
        if not self.need_doc():
            return
        pages = self.target_pages(self.v_ex_scope)
        if pages is None:
            return
        folder = filedialog.askdirectory(title=t("Unde salvez imaginile?"))
        if not folder:
            return
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]
        pr = Progress(self, t("Extrag imaginile…"), len(pages))
        seen, made = set(), 0
        try:
            for k, i in enumerate(pages, 1):
                if not pr.step(k, "Pagina %d…" % (i + 1)):
                    break
                for info in self.doc.get_page_images(i, full=True):
                    xref = info[0]
                    if xref in seen:
                        continue
                    seen.add(xref)
                    try:
                        d = self.doc.extract_image(xref)
                    except Exception:
                        continue
                    if not d or not d.get("image"):
                        continue
                    fn = os.path.join(folder, "%s_p%d_%d.%s"
                                      % (base, i + 1, xref, d.get("ext", "png")))
                    with open(fn, "wb") as fh:
                        fh.write(d["image"])
                    made += 1
        except Exception as e:
            pr.close()
            messagebox.showerror(APP_NAME, t("Eroare:\n\n%s") % e)
            return
        pr.close()
        if not made:
            messagebox.showinfo(APP_NAME, t("Nu am găsit imagini încorporate.\n\n"
                                          "Dacă pagina e o scanare întreagă, folosește "
                                          "„Salvează paginile ca imagini PNG”."))
            return
        self.status(t("Am extras %d imagini în %s") % (made, folder))
        if messagebox.askyesno(APP_NAME, t("Am extras %d imagini.\n\nDeschid folderul?") % made):
            open_in_explorer(folder)

    def op_pages_to_png(self):
        if not self.need_doc():
            return
        pages = self.target_pages(self.v_ex_scope)
        if pages is None:
            return
        try:
            dpi = int(self.sp_dpi.get())
        except Exception:
            dpi = 200
        folder = filedialog.askdirectory(title=t("Unde salvez imaginile PNG?"))
        if not folder:
            return
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]
        z = dpi / 72.0
        pr = Progress(self, t("Salvez paginile ca PNG…"), len(pages))
        made = 0
        try:
            for k, i in enumerate(pages, 1):
                if not pr.step(k, "Pagina %d…" % (i + 1)):
                    break
                pix = self.doc.load_page(i).get_pixmap(matrix=pymupdf.Matrix(z, z), alpha=False)
                pix.save(os.path.join(folder, "%s_p%03d.png" % (base, i + 1)))
                made += 1
        except Exception as e:
            pr.close()
            messagebox.showerror(APP_NAME, t("Eroare:\n\n%s") % e)
            return
        pr.close()
        self.status(t("Am salvat %d imagini în %s") % (made, folder))
        if messagebox.askyesno(APP_NAME, t("Am salvat %d imagini.\n\nDeschid folderul?") % made):
            open_in_explorer(folder)

    # ------------------------------------------------------------- OCR

    def refresh_ocr_state(self):
        exe, td = find_tesseract()
        self.tess_exe, self.tess_data = exe, td
        ok = bool(exe)
        for b in (self.btn_ocr_text, self.btn_ocr_pdf):
            b.state(["!disabled"] if ok else ["disabled"])
        if ok:
            self.lbl_ocr.config(text=t("Tesseract găsit: %s") % exe, fg="#15803d")
            self.btn_ocr_help.pack_forget()
        else:
            self.lbl_ocr.config(text=t("Tesseract nu este instalat — OCR-ul e dezactivat."),
                                fg=DANGER)

    def show_ocr_help(self):
        TextViewer(self, t("Cum instalez Tesseract OCR"),
                   t("OCR = citirea textului din pagini scanate (poze).\n"
                   "Pentru asta ai nevoie de programul Tesseract, gratuit.\n\n"
                   "PAȘI\n"
                   "1. Descarcă instalerul pentru Windows de la:\n"
                   "   https://github.com/UB-Mannheim/tesseract/wiki\n"
                   "   (fișierul se numește ceva de genul tesseract-ocr-w64-setup-....exe)\n\n"
                   "2. Rulează instalerul. IMPORTANT: la pasul cu limbile\n"
                   "   (\"Additional language data\") bifează Romanian, ca să citească\n"
                   "   corect diacriticele.\n\n"
                   "3. Lasă folderul implicit:\n"
                   "   C:\\Program Files\\Tesseract-OCR\n\n"
                   "4. Închide și redeschide PDF Tool. Butoanele de OCR se activează singure.\n\n"
                   "Dacă l-ai instalat în alt folder, adaugă folderul acela în variabila\n"
                   "de mediu PATH, sau reinstalează în locul implicit."))

    def _ocr_pages(self, pages, lang):
        """Genereaza (index, text) pentru fiecare pagina, prin OCR."""
        kw = {"language": lang, "dpi": 300, "full": True}
        if self.tess_data:
            kw["tessdata"] = self.tess_data
        for i in pages:
            page = self.doc.load_page(i)
            tp = page.get_textpage_ocr(**kw)
            yield i, page.get_text("text", textpage=tp)

    def op_ocr_text(self):
        if not self.need_doc() or not self.tess_exe:
            return
        pages = self.target_pages(self.v_ex_scope)
        if pages is None:
            return
        lang = self.cb_lang.get() or "ron"
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]
        out = filedialog.asksaveasfilename(
            title=t("Salvează textul OCR"), defaultextension=".txt",
            initialfile=base + "-ocr.txt", filetypes=[("Fișier text", "*.txt")])
        if not out:
            return
        pr = Progress(self, t("OCR în curs… (durează)"), len(pages))
        try:
            with open(out, "w", encoding="utf-8") as fh:
                for k, (i, txt) in enumerate(self._ocr_pages(pages, lang), 1):
                    if not pr.step(k, "OCR pagina %d din %d…" % (k, len(pages))):
                        break
                    fh.write("\n===== Pagina %d =====\n\n" % (i + 1))
                    fh.write(norm_text(txt))
        except Exception as e:
            pr.close()
            messagebox.showerror(APP_NAME, t("OCR a eșuat:\n\n%s\n\n"
                                           "Verifică dacă limba aleasă e instalată "
                                           "în Tesseract.") % e)
            return
        pr.close()
        self.status(t("OCR gata: %s") % out)
        if messagebox.askyesno(APP_NAME, t("Gata. Deschid folderul?")):
            open_in_explorer(out)

    def op_ocr_pdf(self):
        if not self.need_doc() or not self.tess_exe:
            return
        lang = self.cb_lang.get() or "ron"
        base = os.path.splitext(os.path.basename(self.path or "document"))[0]
        out = filedialog.asksaveasfilename(
            title=t("Salvează PDF-ul căutabil"), defaultextension=".pdf",
            initialfile=base + "-cautabil.pdf", filetypes=[("Fișiere PDF", "*.pdf")])
        if not out:
            return
        pr = Progress(self, t("OCR în curs… (durează)"), self.npages)
        nd = pymupdf.open()
        try:
            for i in range(self.npages):
                if not pr.step(i + 1, "OCR pagina %d din %d…" % (i + 1, self.npages)):
                    break
                pix = self.doc.load_page(i).get_pixmap(matrix=pymupdf.Matrix(2.4, 2.4),
                                                       alpha=False)
                kw = {"language": lang, "compress": True}
                if self.tess_data:
                    kw["tessdata"] = self.tess_data
                data = pix.pdfocr_tobytes(**kw)
                src = pymupdf.open("pdf", data)
                nd.insert_pdf(src)
                src.close()
            nd.save(out, garbage=3, deflate=True)
        except Exception as e:
            pr.close()
            nd.close()
            messagebox.showerror(APP_NAME, t("OCR a eșuat:\n\n%s") % e)
            return
        pr.close()
        nd.close()
        self.status(t("PDF căutabil salvat: %s") % out)
        if messagebox.askyesno(APP_NAME, t("Gata.\n\nDeschid folderul?")):
            open_in_explorer(out)

    # ------------------------------------------------------------ altele

    def op_compress(self):
        if not self.need_doc():
            return
        base = os.path.splitext(os.path.basename(self.path or "document.pdf"))[0]
        out = filedialog.asksaveasfilename(
            title=t("Salvează versiunea comprimată"), defaultextension=".pdf",
            initialfile=base + "-mic.pdf", filetypes=[("Fișiere PDF", "*.pdf")])
        if not out:
            return
        try:
            shrink_fonts(self.doc)
            self.doc.save(out, garbage=4, deflate=True, deflate_images=True,
                          deflate_fonts=True, clean=True)
        except Exception as e:
            messagebox.showerror(APP_NAME, t("Eroare:\n\n%s") % e)
            return
        old = os.path.getsize(self.path) if self.path and os.path.exists(self.path) else 0
        new = os.path.getsize(out)
        msg = "Salvat: %s" % human_size(new)
        if old:
            msg += "   (înainte: %s, −%.0f%%)" % (human_size(old),
                                                  max(0, (1 - new / old) * 100))
        self.status(msg)
        messagebox.showinfo(APP_NAME, msg)

    def op_info(self):
        if not self.need_doc():
            return
        m = self.doc.metadata or {}
        sizes = {}
        for i in range(min(self.npages, 60)):
            r = self.doc.load_page(i).rect
            key = "%.0f × %.0f mm" % (r.width * 25.4 / 72, r.height * 25.4 / 72)
            sizes[key] = sizes.get(key, 0) + 1
        txt_pages = sum(1 for i in range(min(self.npages, 40))
                        if self.doc.load_page(i).get_text("text").strip())
        lines = [
            "Fișier:      %s" % (self.path or "(nesalvat)"),
            "Mărime:      %s" % (human_size(os.path.getsize(self.path))
                                 if self.path and os.path.exists(self.path) else "—"),
            "Pagini:      %d" % self.npages,
            "Titlu:       %s" % (m.get("title") or "—"),
            "Autor:       %s" % (m.get("author") or "—"),
            "Creat cu:    %s" % (m.get("producer") or m.get("creator") or "—"),
            "Criptat:     %s" % ("da" if self.doc.is_encrypted else "nu"),
            "",
            "Dimensiuni pagini:",
        ]
        for k, v in sizes.items():
            lines.append("   %s  (%d pagini)" % (k, v))
        lines += ["",
                  "Text: %d din primele %d pagini conțin text selectabil."
                  % (txt_pages, min(self.npages, 40))]
        if txt_pages == 0:
            lines.append("→ Documentul pare scanat. Pentru text folosește OCR.")
        TextViewer(self, t("Informații document"), "\n".join(lines))

    def _tab_changed(self):
        try:
            idx = self.nb.index(self.nb.select())
        except Exception:
            return
        if idx != 2 and self.click_mode == "text":
            self.set_click_mode(None)
        if idx != 1 and self.click_mode == "image":
            self.set_click_mode(None)


# --------------------------------------------------------------------------
# Ferestre mici
# --------------------------------------------------------------------------

class ChoiceDialog:
    """Intrebare cu mai multe butoane. Rezultatul e in .result."""

    def __init__(self, parent, title, prompt, options):
        self.result = None
        win = tk.Toplevel(parent)
        win.title(title)
        win.configure(bg=PANEL)
        win.resizable(False, False)
        win.transient(parent)
        win.grab_set()
        f = tk.Frame(win, bg=PANEL, padx=24, pady=20)
        f.pack(fill="both", expand=True)
        tk.Label(f, text=prompt, bg=PANEL, fg=INK, font=("Segoe UI", 10),
                 justify="left", wraplength=400).pack(anchor="w", pady=(0, 14))
        for label, value in options:
            def pick(v=value):
                self.result = v
                win.destroy()
            ttk.Button(f, text=label, style="Accent.TButton",
                       command=pick).pack(fill="x", pady=3)
        ttk.Button(f, text=t("Renunță"), command=win.destroy).pack(fill="x", pady=(12, 0))
        win.bind("<Escape>", lambda e: win.destroy())
        parent.update_idletasks()
        win.geometry("+%d+%d" % (parent.winfo_rootx() + 180, parent.winfo_rooty() + 160))
        parent.wait_window(win)


class SimpleAsk:
    def __init__(self, parent, title, prompt, show=None):
        self.result = None
        win = tk.Toplevel(parent)
        win.title(title)
        win.configure(bg=PANEL)
        win.resizable(False, False)
        win.transient(parent)
        win.grab_set()
        f = tk.Frame(win, bg=PANEL, padx=22, pady=18)
        f.pack()
        tk.Label(f, text=prompt, bg=PANEL, fg=INK, font=("Segoe UI", 10)).pack(anchor="w")
        e = ttk.Entry(f, width=34, show=show)
        e.pack(pady=(8, 12), fill="x")
        e.focus_set()

        def ok(*a):
            self.result = e.get()
            win.destroy()
        row = tk.Frame(f, bg=PANEL)
        row.pack(fill="x")
        ttk.Button(row, text=t("OK"), style="Accent.TButton", command=ok).pack(side="right")
        ttk.Button(row, text=t("Renunță"), command=win.destroy).pack(side="right", padx=(0, 6))
        e.bind("<Return>", ok)
        win.bind("<Escape>", lambda e: win.destroy())
        parent.wait_window(win)


class TextViewer(tk.Toplevel):
    def __init__(self, parent, title, text, width=760, height=560):
        super().__init__(parent)
        self.title(title)
        self.configure(bg=PANEL)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        width, height = min(width, sw - 60), min(height, sh - 80)
        self.geometry("%dx%d+%d+%d" % (width, height, max(0, (sw - width) // 2),
                                       max(0, (sh - height) // 3)))
        self.transient(parent)
        f = tk.Frame(self, bg=PANEL)
        f.pack(fill="both", expand=True, padx=12, pady=12)
        sb = ttk.Scrollbar(f, orient="vertical")
        sb.pack(side="right", fill="y")
        txt = tk.Text(f, wrap="word", font=("Consolas", 10), relief="solid", bd=1,
                    yscrollcommand=sb.set, padx=10, pady=10)
        txt.pack(fill="both", expand=True)
        sb.config(command=txt.yview)
        txt.insert("1.0", text)
        txt.config(state="disabled")
        row = tk.Frame(self, bg=PANEL)
        row.pack(fill="x", padx=12, pady=(0, 12))

        def copy():
            self.clipboard_clear()
            self.clipboard_append(text)
            self.status_lbl.config(text=t("Copiat în clipboard."))
        self.status_lbl = tk.Label(row, text="", bg=PANEL, fg=MUTED, font=("Segoe UI", 8))
        self.status_lbl.pack(side="left")
        ttk.Button(row, text=t("Închide"), command=self.destroy).pack(side="right")
        ttk.Button(row, text=t("Copiază tot"), command=copy).pack(side="right", padx=(0, 6))


# --------------------------------------------------------------------------

def main():
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass
    app = PDFTool()

    def on_error(exc, val, tb):
        traceback.print_exception(exc, val, tb)
        try:
            messagebox.showerror(APP_NAME, t("A apărut o eroare neașteptată:\n\n%s: %s") % (exc.__name__, val))
        except Exception:
            pass
    app.report_callback_exception = on_error
    app.mainloop()


if __name__ == "__main__":
    main()
