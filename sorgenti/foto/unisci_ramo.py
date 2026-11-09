"""Porta in foto2.json le foto scaricate da GitHub Actions (ramo «foto» del repository achplaces)."""
import json, os, shutil, subprocess
F = '/home/claude/foto/'; R = '/home/claude/foto-ramo/'
if os.path.isdir(R + '.git'): subprocess.run(['git', '-C', R, 'fetch', '-q', '--depth', '1', 'origin', 'foto'], check=True); subprocess.run(['git', '-C', R, 'reset', '-q', '--hard', 'FETCH_HEAD'], check=True)
else: subprocess.run(['git', 'clone', '-q', '--depth', '1', '-b', 'foto', 'https://github.com/drdonatistefano-cmyk/achplaces', R], check=True)
meta = json.load(open(R + 'meta.json')); c = json.load(open(F + 'foto2.json')); n = 0
# 9/11: i luoghi trovati solo con la ricerca su Commons non erano in foto2.json e venivano saltati: nome e comune dai dati della Guida
import sys as _s9; _s9.path.insert(0, '/home/claude/achs-places-guide'); from leggi_dati import righe as _r9
_G = '/home/claude/achs-places-guide/'; _m = json.load(open(_G + 'manifest.json')); _D = _r9(json.load(open(_G + _m['dati'])))
_src = open(F + 'foto.py').read(); exec(_src.split("m=json.load(open(G+'manifest.json'))")[0].split('import')[0] if False else '')
import unicodedata as _ud, re as _re
def _s40(s):
    s = ''.join(ch for ch in _ud.normalize('NFD', s) if not _ud.combining(ch)).lower(); return _re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
NOMI = {cc['slug'] + '--' + (a[0] if a[0] else _s40(a[1])): (a[1], cc['name']) for cc in _D['c'] for a in cc['places']}
for p, v in meta.items():
    img, a, l, u, col = v[:5]
    r = c.get(p)
    if r is None and p in NOMI: r = c[p] = {'n': NOMI[p][0], 'com': NOMI[p][1], 'arch': 3}
    if r is None or not os.path.exists(R + 'img/' + img): continue
    shutil.copy2(R + 'img/' + img, F + 'img/' + img)
    r.update({'img': img, 'a': a, 'l': l, 'u': u, 'c': col})
    if len(v) > 5: r['file'] = v[5]; r['via'] = v[6]
    if len(v) > 7 and v[7]: r['catf'] = v[7]   # categoria Commons da cui viene la foto
    elif len(v) > 7: r.pop('catf', None)
    if len(v) > 8: r['lab'] = v[8]; r['s'] = 1   # 9/11: terza ricerca Wikidata per nome (aree vaste)
    n += 1
json.dump(c, open(F + 'foto2.json.tmp', 'w'), ensure_ascii=False); os.replace(F + 'foto2.json.tmp', F + 'foto2.json')
print('dal ramo foto:', n)
