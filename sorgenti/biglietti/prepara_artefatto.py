#!/usr/bin/env python3
"""Prepara la pubblicazione sull'artefatto claude.ai, che ha ancora la struttura con gli album fa.*.json:
index_art.html = index.html con le 15 correzioni di velocizza.json rovesciate; manifest_art.json = manifest + fa del vecchio.
Stampa i file da caricare e quelli da togliere rispetto al manifest attuale dell'artefatto (/tmp/art/man_old.json)."""
import json, os, sys
G = '/home/claude/achs-places-guide/'
d = json.load(open('/home/claude/achplaces/sorgenti/velocizza.json'))['sostituzioni']
h = open(G + 'index.html').read()
for s in d:
    assert h.count(s['nuovo']) == 1, s['nuovo'][:60]; h = h.replace(s['nuovo'], s['vecchio'])
open(G + 'index_art.html', 'w').write(h)
old = json.load(open('/tmp/art/man_old.json')); new = json.load(open(G + 'manifest.json'))
m = dict(new); m['fa'] = old['fa']; m.pop('fotom', None); m.pop('cr', None)
json.dump(m, open(G + 'manifest_art.json', 'w'), ensure_ascii=False)
def nomi(x):
    out = set()
    def add(v):
        if isinstance(v, str) and (v.endswith('.json') or v.endswith('.js')): out.add(v)
        elif isinstance(v, dict): [add(y) for y in v.values()]
    for k, v in x.items():
        if k != 'fa': add(v)
    return out
need, have = nomi(m), nomi(old)
up = sorted(need - have); rm = sorted(have - need)
files = [{'as': x, 'path': G + x} for x in up] + [{'as': 'filtri.html', 'path': G + 'filtri.html'}, {'as': 'manifest.json', 'path': G + 'manifest_art.json'}, {'as': 'index.html', 'path': G + 'index_art.html'}]
json.dump({'files': files, 'remove': rm}, open('/tmp/art/piano.json', 'w'))
json.dump(m, open('/tmp/art/man_next.json', 'w'))
print(len(files), 'da caricare,', len(rm), 'da togliere')
