# -*- coding: utf-8 -*-
"""Verificare ortografica prin corectorul din Windows.

Foloseste dictionarele pe care Windows le are deja instalate, prin
interfata COM ISpellChecker. Nu adauga nicio biblioteca si nu creste
marimea programului.

Daca limba ceruta nu are dictionar instalat, sau daca ceva nu merge,
totul se opreste in tacere: aplicatia functioneaza la fel, doar fara
subliniere.

Nu corecteaza nimic singura. Doar arata ce pare gresit si propune
variante cand ceri tu.
"""

import ctypes
from ctypes import wintypes, POINTER, byref, c_void_p, c_ulong, c_wchar_p

S_OK = 0
CLSCTX_INPROC_SERVER = 1
COINIT_APARTMENTTHREADED = 2

try:
    _ole32 = ctypes.windll.ole32
except Exception:                                  # pragma: no cover
    _ole32 = None


class _GUID(ctypes.Structure):
    _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD),
                ("Data3", wintypes.WORD), ("Data4", ctypes.c_ubyte * 8)]

    def __init__(self, text):
        super().__init__()
        _ole32.CLSIDFromString(ctypes.c_wchar_p(text), byref(self))


def _vtbl(ptr, index, *tipuri):
    """Metoda de la pozitia data din tabela virtuala a interfetei COM."""
    tabel = ctypes.cast(ptr, POINTER(POINTER(c_void_p))).contents
    return ctypes.WINFUNCTYPE(ctypes.HRESULT, c_void_p, *tipuri)(tabel[index])


def _elibereaza(ptr):
    if ptr:
        try:
            _vtbl(ptr, 2)(ptr)
        except Exception:
            pass


def _siruri(enum_ptr):
    """Citeste un IEnumString pana la capat."""
    out = []
    if not enum_ptr:
        return out
    try:
        urmatorul = _vtbl(enum_ptr, 3, c_ulong, POINTER(c_wchar_p), POINTER(c_ulong))
        while True:
            buf = c_wchar_p()
            luate = c_ulong()
            if urmatorul(enum_ptr, 1, byref(buf), byref(luate)) != S_OK or not luate.value:
                break
            if buf.value:
                out.append(buf.value)
                _ole32.CoTaskMemFree(buf)
    except Exception:
        pass
    return out


# Codul nostru de limba -> etichetele pe care le incearca Windows, in ordine.
_ETICHETE = {
    "ro": ("ro-RO", "ro"),
    "en": ("en-US", "en-GB", "en"),
    "fr": ("fr-FR", "fr-BE", "fr-CA", "fr"),
    "es": ("es-ES", "es-MX", "es"),
    "de": ("de-DE", "de-AT", "de-CH", "de"),
    "it": ("it-IT", "it"),
    "pt": ("pt-PT", "pt-BR", "pt"),
    "nl": ("nl-NL", "nl-BE", "nl"),
    "pl": ("pl-PL", "pl"),
    "ru": ("ru-RU", "ru"),
}

_stare = {"pornit": False, "factory": None}


def _factory():
    if _stare["pornit"]:
        return _stare["factory"]
    _stare["pornit"] = True
    if _ole32 is None:
        return None
    try:
        _ole32.CoInitializeEx(None, COINIT_APARTMENTTHREADED)
        f = c_void_p()
        hr = _ole32.CoCreateInstance(
            byref(_GUID("{7AB36653-1796-484B-BDFA-E74F1DB7C1DC}")), None,
            CLSCTX_INPROC_SERVER,
            byref(_GUID("{8E018A9D-2415-4677-BF08-794EA61F94BB}")), byref(f))
        _stare["factory"] = f if hr == S_OK else None
    except Exception:
        _stare["factory"] = None
    return _stare["factory"]


def disponibil():
    """Windows ofera un corector?"""
    return _factory() is not None


def limbi_instalate():
    """Etichetele pentru care exista dictionar pe acest calculator."""
    f = _factory()
    if not f:
        return []
    e = c_void_p()
    try:
        _vtbl(f, 3, POINTER(c_void_p))(f, byref(e))
    except Exception:
        return []
    out = _siruri(e)
    _elibereaza(e)
    return out


def eticheta_pentru(cod):
    """Prima eticheta instalata pentru limba noastra, sau None."""
    f = _factory()
    if not f:
        return None
    try:
        sustine = _vtbl(f, 4, c_wchar_p, POINTER(wintypes.BOOL))
    except Exception:
        return None
    for tag in _ETICHETE.get(cod, (cod,)):
        ok = wintypes.BOOL()
        try:
            if sustine(f, tag, byref(ok)) == S_OK and ok.value:
                return tag
        except Exception:
            continue
    return None


class Corector:
    """Verifica un text si propune variante. Nu schimba nimic singur."""

    def __init__(self, ptr, eticheta):
        self._ptr = ptr
        self.eticheta = eticheta

    def greseli(self, text):
        """[(pozitie, lungime, cuvant), ...] pentru ce pare gresit."""
        if not text or not self._ptr:
            return []
        out = []
        e = c_void_p()
        try:
            if _vtbl(self._ptr, 4, c_wchar_p, POINTER(c_void_p))(
                    self._ptr, text, byref(e)) != S_OK or not e:
                return []
            urmatorul = _vtbl(e, 3, POINTER(c_void_p))
            while len(out) < 200:
                err = c_void_p()
                if urmatorul(e, byref(err)) != S_OK or not err:
                    break
                start, lung = c_ulong(), c_ulong()
                _vtbl(err, 3, POINTER(c_ulong))(err, byref(start))
                _vtbl(err, 4, POINTER(c_ulong))(err, byref(lung))
                if lung.value:
                    out.append((start.value, lung.value,
                                text[start.value:start.value + lung.value]))
                _elibereaza(err)
        except Exception:
            pass
        finally:
            _elibereaza(e)
        return out

    def sugestii(self, cuvant, cate=6):
        if not cuvant or not self._ptr:
            return []
        e = c_void_p()
        try:
            if _vtbl(self._ptr, 5, c_wchar_p, POINTER(c_void_p))(
                    self._ptr, cuvant, byref(e)) != S_OK:
                return []
        except Exception:
            return []
        out = _siruri(e)
        _elibereaza(e)
        return out[:cate]

    def close(self):
        _elibereaza(self._ptr)
        self._ptr = None


def corector_pentru(cod):
    """Un corector pentru limba noastra, sau None daca nu exista dictionar."""
    tag = eticheta_pentru(cod)
    if not tag:
        return None
    f = _factory()
    ptr = c_void_p()
    try:
        if _vtbl(f, 5, c_wchar_p, POINTER(c_void_p))(f, tag, byref(ptr)) != S_OK or not ptr:
            return None
    except Exception:
        return None
    return Corector(ptr, tag)
