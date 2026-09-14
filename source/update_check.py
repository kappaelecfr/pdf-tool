# -*- coding: utf-8 -*-
"""A aparut o versiune mai noua?

Singurul loc din program care atinge internetul. Cere de la GitHub
eticheta ultimei versiuni publicate si atat: o cerere GET, fara nimic
despre tine si fara nimic despre fisierele pe care le deschizi. Nu
descarca nimic si nu instaleaza nimic — daca apare ceva nou, programul
o spune si te lasa pe tine sa hotarasti.

Se poate opri din fereastra „Despre si actualizari”, iar atunci nu mai
pleaca nicio cerere.

Orice se poate intampla in drum — nu ai retea, GitHub nu raspunde,
raspunsul e stricat — se termina in tacere. Verificarea e un lux, nu o
conditie ca programul sa mearga.
"""

import io
import json
import os
import re
import subprocess
import tempfile
import threading
import urllib.request

API = "https://api.github.com/repos/kappaelecfr/pdf-tool/releases/latest"
# Pagina pe care o vede omul: a noastra, in limba lui. Fisierul vine tot
# din API-ul de mai sus, dar asta nu are de ce sa i se arate.
PAGINA = "https://kappaproject.com/apps/pdf-tool"


def numere(v):
    """„1.2.10” -> (1, 2, 10). Ce nu e numar se ignora."""
    parti = re.findall(r"\d+", v or "")
    return tuple(int(p) for p in parti[:4]) or (0,)


def mai_noua(actuala, gasita):
    """Versiunea gasita e mai noua decat cea care ruleaza?

    Comparam numar cu numar, nu ca text: altfel „1.2.10” ar parea mai
    veche decat „1.2.9”.
    """
    a, g = numere(actuala), numere(gasita)
    n = max(len(a), len(g))
    a = a + (0,) * (n - len(a))
    g = g + (0,) * (n - len(g))
    return g > a


def intreaba(actuala, timeout=6):
    """Cere eticheta ultimei versiuni. (versiune, adresa) sau None."""
    cerere = urllib.request.Request(API, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "PDF-Tool/%s" % actuala,
    })
    with urllib.request.urlopen(cerere, timeout=timeout) as r:
        d = json.load(r)
    eticheta = (d.get("tag_name") or "").lstrip("vV").strip()
    if not eticheta:
        return None
    return eticheta, PAGINA


def cauta(actuala, gata, si_daca_e_la_zi=False, timeout=6):
    """Verifica pe un fir separat, ca sa nu tina fereastra pe loc.

    `gata` se cheama cu (versiune, adresa) cand e ceva mai nou, cu
    (None, None) cand esti la zi si ai cerut-o singur, si nu se cheama
    deloc daca verificarea nu a reusit — afara de cazul cand ai cerut-o
    singur, cand primesti (False, None) ca sa poti spune de ce.
    """
    def lucreaza():
        try:
            r = intreaba(actuala, timeout)
        except Exception:
            if si_daca_e_la_zi:
                gata(False, None)
            return
        if r and mai_noua(actuala, r[0]):
            gata(r[0], r[1])
        elif si_daca_e_la_zi:
            gata(None, None)

    threading.Thread(target=lucreaza, daemon=True).start()


# --------------------------------------------------- descarcarea versiunii

def fisierul_nou(actuala, timeout=6):
    """(versiune, adresa_exe, marime) pentru ultima versiune, sau None."""
    cerere = urllib.request.Request(API, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "PDF-Tool/%s" % actuala,
    })
    with urllib.request.urlopen(cerere, timeout=timeout) as r:
        d = json.load(r)
    eticheta = (d.get("tag_name") or "").lstrip("vV").strip()
    for a in d.get("assets") or []:
        if (a.get("name") or "").lower().endswith(".exe"):
            return eticheta, a.get("browser_download_url"), a.get("size") or 0
    return None


def descarca(adresa, catre, marime=0, progres=None, timeout=30):
    """Ia fisierul bucata cu bucata, anuntand cat a venit.

    `progres` primeste o valoare intre 0 si 1. Daca intoarce False,
    descarcarea se opreste si fisierul pe jumatate se sterge.
    """
    cerere = urllib.request.Request(adresa, headers={"User-Agent": "PDF-Tool"})
    luat = 0
    try:
        with urllib.request.urlopen(cerere, timeout=timeout) as r:
            total = marime or int(r.headers.get("Content-Length") or 0)
            with io.open(catre, "wb") as fh:
                while True:
                    bucata = r.read(262144)
                    if not bucata:
                        break
                    fh.write(bucata)
                    luat += len(bucata)
                    if progres and progres(luat / total if total else 0.0) is False:
                        raise RuntimeError("oprit")
    except Exception:
        try:
            os.remove(catre)
        except Exception:
            pass
        raise
    return luat


def pare_program(cale, marime_asteptata=0):
    """Fisierul descarcat chiar e un program Windows intreg?"""
    try:
        if marime_asteptata and os.path.getsize(cale) != marime_asteptata:
            return False
        with io.open(cale, "rb") as fh:
            return fh.read(2) == b"MZ"
    except Exception:
        return False


AJUTOR = """@echo off
setlocal
set "TINTA=%~1"
set "NOU=%~2"
set "VECHI=%~3"
set /a N=0
:incearca
set /a N+=1
move /Y "%TINTA%" "%VECHI%" >nul 2>&1
if not errorlevel 1 goto eliberat
if %N% GEQ 90 exit /b 1
ping -n 2 127.0.0.1 >nul
goto incearca
:eliberat
move /Y "%NOU%" "%TINTA%" >nul 2>&1
if errorlevel 1 (
  move /Y "%VECHI%" "%TINTA%" >nul 2>&1
  exit /b 1
)
start "" "%TINTA%"
ping -n 3 127.0.0.1 >nul
del "%VECHI%" >nul 2>&1
(goto) 2>nul & del "%~f0"
"""


def inlocuieste_si_reporneste(tinta, nou):
    """Lasa in urma un ajutor care schimba programul dupa ce se inchide.

    Se cheama chiar inainte de inchiderea ferestrei. Nu se intoarce cu
    nimic util: ori a pornit ajutorul, ori a crapat si spune de ce.
    """
    dosar = os.path.dirname(os.path.abspath(tinta)) or "."
    vechi = os.path.join(dosar, os.path.basename(tinta) + ".precedent")
    ajutor = os.path.join(tempfile.gettempdir(), "pdftool-update.cmd")
    with io.open(ajutor, "w", encoding="ascii", newline="\r\n") as fh:
        fh.write(AJUTOR)
    # Programul dezarhivat cu PyInstaller isi lasa dosarul temporar intr-o
    # variabila de mediu. Daca ajutorul o mosteneste, programul nou pornit de
    # el crede ca e deja dezarhivat si isi cauta python3xx.dll in dosarul
    # vechi — care intre timp a fost sters. De aici "Failed to load Python
    # DLL". Pornim ajutorul cu mediul curatat de aceste urme.
    mediu = dict(os.environ)
    for cheie in list(mediu):
        if cheie.startswith("_MEI") or cheie.startswith("_PYI"):
            mediu.pop(cheie, None)
    subprocess.Popen(["cmd", "/c", ajutor, tinta, nou, vechi],
                     env=mediu,
                     creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)
                     | getattr(subprocess, "DETACHED_PROCESS", 0),
                     close_fds=True)
