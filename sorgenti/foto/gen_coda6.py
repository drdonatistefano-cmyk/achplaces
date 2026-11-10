"""10/11/2026 coda per la sesta ricerca foto (GitHub Actions, sorgenti/foto/actions_foto6.py): tutti i luoghi della guida senza foto,
con nome, comune, ISTAT, regione e coordinate del comune (e del luogo, quando ci saranno)."""
import json, glob, sys, re, unicodedata
G = '/home/claude/achs-places-guide/'; sys.path.insert(0, G)
from leggi_dati import righe
def sl(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
m = json.load(open(G + 'manifest.json')); d = json.load(open(G + m['dati'])); r = righe(d); Z = d['dz']
foto = json.load(open(G + m['foto']))
CK = ['storia', 'musei', 'sacro', 'natura', 'locale']
out = []
for c in r['c']:
    reg = Z['regione'][c['regione']] if isinstance(c['regione'], int) else c['regione']
    for a in c['places']:
        pid = c['slug'] + '--' + (a[0] if a[0] else sl(a[1]))
        if pid in foto: continue
        x = {'p': pid, 'n': a[1], 'com': c['name'], 'istat': c.get('istat', ''), 'reg': reg, 'cat': CK[a[2]],
             'clat': c.get('lat'), 'clng': c.get('lng')}
        ex = a[9] if len(a) > 9 and isinstance(a[9], dict) else {}
        if ex.get('lat') is not None: x['lat'] = ex['lat']; x['lng'] = ex['lng']
        out.append(x)
json.dump(out, open('/home/claude/achplaces/sorgenti/foto/coda6.json', 'w'), ensure_ascii=False, separators=(',', ':'))
import collections; print(len(out), collections.Counter(x['reg'] for x in out).most_common())
