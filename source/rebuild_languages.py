# -*- coding: utf-8 -*-
"""Rebuilds everything that is generated:

    lang.py     interface strings
    guide.py    the quick guide, one text per language
    faq.py      the frequently asked questions, one text per language

and writes the matching README / FAQ files into the distribution folder,
so what the program shows and what sits on disk can never drift apart.

Sources:
    _src.json       interface strings in Romanian (the source language)
    _tr_<lg>.json   their translations, one entry per line, same order
    _extra.json     extra strings, every language in one place
    guides.json     the quick guide
    faqs.json       the questions and answers

Safe to run as often as you like.
"""
import io
import os
import json

LANGS = ['en', 'fr', 'es', 'de', 'it', 'pt', 'nl', 'pl', 'ru']
HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.dirname(HERE)
DOCS = os.path.join(DIST, 'Readme')


def here(name):
    return os.path.join(HERE, name)


# ------------------------------------------------------------- lang.py
src = json.load(io.open(here('_src.json'), encoding='utf-8'))
extra = json.load(io.open(here('_extra.json'), encoding='utf-8'))

cat = {}
for lg in LANGS:
    tr = json.load(io.open(here('_tr_%s.json' % lg), encoding='utf-8'))
    assert len(tr) == len(src), '%s: %d intrari, ar trebui %d' % (lg, len(tr), len(src))
    d = dict(zip(src, tr))
    for ro, per in extra.items():
        d[ro] = per.get(lg) or ro
    cat[lg] = d

head = io.open(here('lang.py'), encoding='utf-8').read().split('\nTR = {}')[0] + '\nTR = {}\n'
parts = [head]
for lg in LANGS:
    parts.append('\nTR["%s"] = %s\n' % (
        lg, json.dumps(cat[lg], ensure_ascii=False, indent=1, sort_keys=True)))
io.open(here('lang.py'), 'w', encoding='utf-8').write(''.join(parts))
print('lang.py    : %d limbi x %d texte, %.0f KB'
      % (len(LANGS), len(cat['en']), os.path.getsize(here('lang.py')) / 1024))

import lang as LG

# ------------------------------------------- guide.py, faq.py + fisiere
TEXTE = [
    ('guides.json', 'guide.py', 'GUIDE', 'README.txt', 'README'),
    ('faqs.json', 'faq.py', 'FAQ', 'FAQ.txt', 'FAQ'),
]

if not os.path.isdir(DOCS):
    os.makedirs(DOCS)

for sursa, modul, var, radacina, prefix in TEXTE:
    texte = json.load(io.open(here(sursa), encoding='utf-8'))
    for lg in ['ro'] + LANGS:
        assert lg in texte, '%s: lipseste limba %s' % (sursa, lg)
        lungi = [n for n, l in enumerate(texte[lg].split('\n'), 1) if len(l) > 78]
        assert not lungi, '%s / %s: randuri peste 78 coloane: %s' % (
            sursa, lg, lungi[:5])

    io.open(here(modul), 'w', encoding='utf-8').write(
        '# -*- coding: utf-8 -*-\n'
        '"""GENERAT de rebuild_languages.py din %s. Nu edita aici."""\n\n'
        '%s = %s\n\n\n'
        'def text_for(code):\n'
        '    return %s.get(code) or %s["en"]\n'
        % (sursa, var,
           json.dumps(texte, ensure_ascii=False, indent=1, sort_keys=True),
           var, var))
    print('%-11s: %d limbi, %.0f KB'
          % (modul, len(texte), os.path.getsize(here(modul)) / 1024))

    for code, text in sorted(texte.items()):
        if code == 'en':
            p = os.path.join(DIST, radacina)
        else:
            p = os.path.join(DOCS, '%s-%s.txt' % (prefix, code))
        io.open(p, 'w', encoding='utf-8', newline='').write(text.replace('\n', '\r\n'))
    print('             %d fisiere %s-*.txt scrise' % (len(texte), prefix))

print()
print('limbi: %s' % ' '.join(LG.LANG_NAMES[c] for c in LG.LANG_ORDER))
