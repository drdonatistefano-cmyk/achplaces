"""20/11/2026 coda per l'ottava ricerca foto (sorgenti/foto/actions_foto8.py): i luoghi della guida che hanno solo la foto
del comune (ripiego, 7 campi in foto.<impronta>.json) o nessuna foto, con nome, comune, regione e coordinate.
Uso, dalla radice del sito: python3 sorgenti/foto/gen_coda8.py"""
import json, sys, re, unicodedata, collections
sys.path.insert(0, 'sorgenti')
from leggi_dati import righe
def sl(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
m = json.load(open('manifest.json')); d = json.load(open(m['dati'])); r = righe(d); Z = d['dz']
foto = json.load(open(m['foto']))
CK = ['storia', 'musei', 'sacro', 'natura', 'locale']
out = []
for c in r['c']:
    reg = Z['regione'][c['regione']] if isinstance(c['regione'], int) else c['regione']
    for a in c['places']:
        pid = c['slug'] + '--' + (a[0] if a[0] else sl(a[1]))
        if pid in foto and len(foto[pid]) != 7: continue          # ha già una foto propria
        x = {'p': pid, 'n': a[1], 'com': c['name'], 'istat': c.get('istat', ''), 'reg': reg, 'cat': CK[a[2]],
             'clat': c.get('lat'), 'clng': c.get('lng')}
        ex = a[9] if len(a) > 9 and isinstance(a[9], dict) else {}
        if ex.get('lat') is not None: x['lat'] = ex['lat']; x['lng'] = ex['lng']
        out.append(x)
json.dump(out, open('sorgenti/foto/coda8.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(out), 'luoghi in coda;', collections.Counter(x['reg'] for x in out).most_common(6))
