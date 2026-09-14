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

import json
import re
import threading
import urllib.request

API = "https://api.github.com/repos/kappaelecfr/pdf-tool/releases/latest"
PAGINA = "https://github.com/kappaelecfr/pdf-tool/releases/latest"


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
    return eticheta, (d.get("html_url") or PAGINA)


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
