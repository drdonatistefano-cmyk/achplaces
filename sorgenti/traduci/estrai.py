#!/usr/bin/env python3
"""13/11/2026 – versione inglese. Raccoglie i testi italiani da tradurre (schede dei luoghi e dei comuni)
e scrive sorgenti/traduci/testi_it.jsonl: una riga {"k": impronta, "t": testo} per ogni testo diverso.

L'impronta e' la stessa che calcola la pagina (en_k in template.html e mappa_tpl.html):
FNV-1a a 32 bit sulle unita' UTF-16 del testo, in base 36, piu' "." e la lunghezza.
La traduzione la fa GitHub Actions (traduci.yml) con un modello aperto (Opus-MT, Helsinki-NLP, CC BY 4.0):
nessun servizio di terzi, nessun dato Google.
"""
import json, os, subprocess, glob, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAMPI = ('desc', 'why', 'access', 'price', 'duration', 'tip', 'statusNote', 'hours', 'booking')
CAMPI_C = ('lede', 'notice')

def b36(n):
    s = ''
    while True:
        n, r = divmod(n, 36); s = '0123456789abcdefghijklmnopqrstuvwxyz'[r] + s
        if not n: return s

def en_k(t):
    h = 0x811c9dc5
    u = t.encode('utf-16-le')
    for i in range(0, len(u), 2):
        h ^= u[i] | (u[i + 1] << 8)
        h = (h * 0x01000193) & 0xffffffff
    return b36(h) + '.' + str(len(t.encode('utf-16-le')) // 2)

def da_tradurre(t):
    return isinstance(t, str) and len(t.strip()) > 1 and not t.startswith('http') and any(c.isalpha() for c in t)

def raccogli():
    """{provincia: {impronta: testo}}"""
    M = json.load(open(os.path.join(HERE, 'manifest.json')))
    out = {}
    for pr, n in M['det'].items():
        d = out.setdefault(pr, {})
        for sl, ps in json.load(open(os.path.join(HERE, n))).items():
            for pid, x in ps.items():
                for c in (CAMPI_C if pid == '_c' else CAMPI):
                    t = x.get(c)
                    if da_tradurre(t): d[en_k(t)] = t
    BO = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs');eval(fs.readFileSync('" + os.path.join(HERE, 'data', 'places-bologna.js') + "','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES))"]))
    d = out.setdefault('BO', {})
    for p in BO:
        for c in CAMPI:
            t = p.get(c)
            if da_tradurre(t): d[en_k(t)] = t
    return out

if __name__ == '__main__':
    R = raccogli()
    tutti = {}
    for d in R.values(): tutti.update(d)
    dest = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'traduci', 'testi_it.jsonl')
    with open(dest, 'w') as f:
        for k in sorted(tutti): f.write(json.dumps({'k': k, 't': tutti[k]}, ensure_ascii=False) + '\n')
    print('testi da tradurre:', len(tutti), 'caratteri:', sum(map(len, tutti.values())))
