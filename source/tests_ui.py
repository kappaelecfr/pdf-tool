# -*- coding: utf-8 -*-
"""Test de integrare: porneste interfata reala si apasa butoanele."""
import os
import sys
import tempfile
import pymupdf

sys.path.insert(0, r"C:\Users\kappa\Documents\PDF-Tool\source")
import pdf_tool as T
from pdf_tool import tk, ttk, filedialog, messagebox

D = tempfile.mkdtemp(prefix="pdft_")
fail = []


def check(cond, msg):
    print(("  OK  " if cond else "  FAIL ") + msg)
    if not cond:
        fail.append(msg)


# ---------------------------------------------------- PDF sursa de test
src = os.path.join(D, "in.pdf")
d = pymupdf.open()
for i in range(6):
    p = d.new_page(width=595, height=842)
    p.draw_rect(pymupdf.Rect(0, 0, 595, 110), fill=(0.92, 0.95, 1.0))
    T.textbox(p, pymupdf.Rect(50, 35, 545, 85), "Raport Ștefan – pagina %d" % (i + 1),
              20, (0.1, 0.1, 0.3))
    T.textbox(p, pymupdf.Rect(50, 150, 545, 260),
              "Total: 1.250,00 lei. Țara: România. Rând %d." % (i + 1), 12, (0, 0, 0))
d.save(src)
d.close()

# ------------------------------------------------- automatizare dialoguri
saved = {}
messagebox.showinfo = lambda *a, **k: None
messagebox.showerror = lambda *a, **k: saved.setdefault("errors", []).append(a)
messagebox.showwarning = lambda *a, **k: None
messagebox.askyesno = lambda *a, **k: False
messagebox.askyesnocancel = lambda *a, **k: False
filedialog.askdirectory = lambda *a, **k: D
filedialog.askopenfilename = lambda *a, **k: saved.get("open", "")
filedialog.asksaveasfilename = lambda *a, **k: saved.get("save", "")

print("\n[1] Pornire interfata")
app = T.PDFTool()
app.geometry("1300x850+40+40")
app.update()
check(app.winfo_exists() == 1, "fereastra creata")
check(app.nb.index("end") == 4, "are 4 taburi")
check(app.doc is None, "porneste fara document")

print("\n[2] Deschidere fisier")
app.load(src)
app.update()
check(app.npages == 6, "6 pagini incarcate")
check(len(app.thumb_labels) == 6, "6 miniaturi create")
check(app.preview_img is not None, "previzualizarea s-a randat")
app.after(60, app.quit); app.mainloop()
check(len(app.thumb_imgs) > 0, "%d miniaturi randate lenes (doar cele vizibile)" % len(app.thumb_imgs))

print("\n[3] Selectie")
app.e_range.delete(0, "end")
app.e_range.insert(0, "2-4")
app.apply_range()
check(app.selected == {1, 2, 3}, "interval '2-4' -> paginile 2,3,4")
app.on_thumb_click(0)
check(0 in app.selected, "click pe miniatura adauga pagina")
app.select_set({1, 2, 3})

print("\n[4] Rotire")
app.op_rotate(90)
app.update()
check(app.doc.load_page(1).rotation == 90, "pagina 2 rotita 90")
check(app.doc.load_page(0).rotation == 0, "pagina 1 neatinsa")
check(app.dirty is True, "documentul e marcat ca modificat")

print("\n[5] Anulare / refacere")
app.undo()
app.update()
check(app.doc.load_page(1).rotation == 0, "undo a anulat rotirea")
app.redo()
app.update()
check(app.doc.load_page(1).rotation == 90, "redo a refacut rotirea")
app.undo()

print("\n[6] Filigran")
app.e_wm.delete(0, "end")
app.e_wm.insert(0, "CONFIDENȚIAL")
app.v_wm_scope.set("all")
app.op_watermark()
app.update()
t0 = app.doc.load_page(0).get_text("text")
check("CONFIDENȚIAL" in t0, "filigranul e pe pagina 1")
check("CONFIDENȚIAL" in app.doc.load_page(5).get_text("text"), "si pe ultima pagina")

print("\n[7] Numerotare")
app.e_num_fmt.delete(0, "end")
app.e_num_fmt.insert(0, "{n} / {total}")
app.v_num_pos.set("bc")
app.op_numbering()
app.update()
check("3 / 6" in app.doc.load_page(2).get_text("text"), "pagina 3 numerotata '3 / 6'")

print("\n[8] Cauta si inlocuieste")
app.e_find.delete(0, "end")
app.e_find.insert(0, "1.250,00")
app.e_repl.delete(0, "end")
app.e_repl.insert(0, "9.999,99")
app.v_repl_scope.set("all")
app.op_replace()
app.update()
t1 = T.norm_text(app.doc.load_page(0).get_text("text"))
check("9.999,99" in t1, "suma inlocuita pe pagina 1")
check("1.250,00" not in t1, "suma veche a disparut")
check("România" in t1, "restul textului intact")
check(len(app.doc.load_page(3).search_for("9.999,99")) == 1, "inlocuit si pe pagina 4")

print("\n[9] Editare text prin click")
page = app.doc.load_page(0)
r = page.search_for("Raport")[0]
app.set_click_mode("text")
app.pick_text_at(page, (r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2)
check(app.edit_target is not None, "textul a fost gasit la click")
check("Raport Ștefan" in app.edit_target["orig"], "textul corect: %r" % app.edit_target["orig"][:30])
app.txt_edit.delete("1.0", "end")
app.txt_edit.insert("1.0", "Situație lunară")
app.op_apply_text()
app.update()
t2 = T.norm_text(app.doc.load_page(0).get_text("text"))
check("Situație lunară" in t2, "textul nou e in pagina")
check("Raport Ștefan" not in t2, "textul vechi a disparut")

print("\n[10] Mutare si stergere pagini")
n0 = app.npages
app.select_set({5})
app.op_move(-1)
app.update()
check(app.npages == n0, "numarul de pagini neschimbat dupa mutare")
app.select_set({4, 5})
messagebox.askyesno = lambda *a, **k: True
app.op_delete()
app.update()
check(app.npages == n0 - 2, "2 pagini sterse -> %d ramase" % app.npages)
check(len(app.thumb_labels) == app.npages, "miniaturile s-au reconstruit")
messagebox.askyesno = lambda *a, **k: False

print("\n[11] Unire")
saved["open"] = src
n1 = app.npages
app.op_merge("end")
app.update()
check(app.npages == n1 + 6, "unire: %d + 6 = %d pagini" % (n1, app.npages))

print("\n[12] Salvare")
out = os.path.join(D, "out.pdf")
saved["save"] = out
app.cmd_save_as()
app.update()
check(os.path.exists(out), "fisier salvat")
check(app.dirty is False, "marcajul de nesalvat a disparut")
chk = pymupdf.open(out)
check(chk.page_count == app.npages, "fisierul salvat are %d pagini" % chk.page_count)
check("CONFIDENȚIAL" in chk.load_page(0).get_text("text"), "filigranul e in fisierul salvat")
print("      marime fisier: %s" % T.human_size(os.path.getsize(out)))
chk.close()

print("\n[13] Extragere text si pagini PNG")
txt_out = os.path.join(D, "t.txt")
saved["save"] = txt_out
app.v_ex_scope.set("all")
app.op_export_text()
check(os.path.exists(txt_out), "text exportat")
content = open(txt_out, encoding="utf-8").read()
check("\xa0" not in content, "spatiile din .txt sunt normale (fara nbsp)")
check("România" in content, "diacriticele in .txt sunt corecte")

app.select_set({0, 1})
app.v_ex_scope.set("sel")
app.sp_dpi.set(72)
app.op_pages_to_png()
pngs = [f for f in os.listdir(D) if f.endswith(".png")]
check(len(pngs) == 2, "%d imagini PNG salvate" % len(pngs))

print("\n[14] Impartire in fisiere")
app.sp_split.set(5)
app.op_split()
parts = [f for f in os.listdir(D) if f.startswith("out_") and f.endswith(".pdf")]
check(len(parts) >= 2, "%d fisiere rezultate din impartire" % len(parts))

print("\n[15] Selectie -> PDF nou")
sel_out = os.path.join(D, "sel.pdf")
saved["save"] = sel_out
app.select_set({0, 2})
app.op_extract_sel()
check(os.path.exists(sel_out), "PDF cu selectia salvat")
if os.path.exists(sel_out):
    s2 = pymupdf.open(sel_out)
    check(s2.page_count == 2, "contine exact 2 pagini")
    s2.close()

print("\n[16] Robustete")
app.cmd_close_doc()
app.update()
check(app.doc is None, "document inchis")
app.op_rotate(90)
app.op_watermark()
app.op_numbering()
app.op_replace()
app.op_apply_text()
app.undo()
check(True, "butoanele nu crapa fara document deschis")

errs = saved.get("errors", [])
check(not errs, "nicio eroare neasteptata%s" % ("" if not errs else ": %s" % (errs[:2],)))

app.destroy()

print("\n" + "=" * 56)
if fail:
    print("AU PICAT %d teste:" % len(fail))
    for m in fail:
        print("   - " + m)
    sys.exit(1)
print("TOATE TESTELE DE INTERFATA AU TRECUT")
print("(fisiere de test in %s)" % D)
