#!/usr/bin/env python3
"""Passo dopo build.py e mkfiltri: aggiunge le foto (Wikimedia Commons) alla guida.
Usa /home/claude/foto/foto-finale.json (prodotto da controllo.py): solo foto con autore e licenza.
Scrive foto.<hash>.json, copia le immagini in img/ e aggiunge la chiave 'foto' al manifest."""
import json, hashlib, os, shutil, glob, subprocess
G = '/home/claude/achs-places-guide/'; F = '/home/claude/foto/'
subprocess.run(['python3', F + 'unisci_ramo.py'], check=True)
subprocess.run(['python3', F + 'controllo.py'], check=True)
fin = json.load(open(F + 'foto-finale.json'))
import base64
def chiave(pid):
    return pid.split('--')[0].rsplit('-', 1)[-1] if '--' in pid else 'bo'
out = {}; alb = {}
for k, v in sorted(fin.items()):
    if v.get('img') and v.get('l') and os.path.exists(F + 'img/' + v['img']):
        ch = chiave(k)
        out[k] = [ch, v.get('a', ''), v['l'], v.get('u', ''), v.get('c', '')]
        alb[k] = F + 'img/' + v['img']
# 10/11/2026 ripiego: foto libera del comune (Wikidata P18) per i luoghi senza foto propria; una sola immagine per comune
# nell'album (chiave "@<istat>"), la riga del luogo ha in sesta posizione la chiave e in settima il nome del comune.
R = '/home/claude/foto-ramo/'
if os.environ.get('FOTO_COMUNE', '1') != '0' and os.path.exists(R + 'metacom.json'):   # 10/11 13:58: pubblicata su richiesta di Stefano (FOTO_COMUNE=0 per spegnerla)
    import sys as _s; _s.path.insert(0, G); from leggi_dati import righe as _rr
    import unicodedata as _ud, re as _re
    def _sl(s):
        s = ''.join(c for c in _ud.normalize('NFD', s) if not _ud.combining(c)).lower(); return _re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
    MC = json.load(open(R + 'metacom.json')); _m = json.load(open(G + 'manifest.json')); _D = _rr(json.load(open(G + _m['dati']))); nc = 0
    for cc in _D['c']:
        ist = str(cc.get('istat', '')).zfill(6); v = MC.get(ist)
        if not v or not os.path.exists(R + 'img/' + v[0]): continue
        for a in cc['places']:
            k = cc['slug'] + '--' + (a[0] if a[0] else _sl(a[1]))
            if k in out: continue
            ch = chiave(k); ak = '@' + ist
            out[k] = [ch, v[1], v[2], v[3], v[4], ak, cc['name']]; nc += 1
            alb.setdefault(ak, R + 'img/' + v[0])
    print('luoghi con foto del comune:', nc)
# 10/11/2026 sera: niente più album fa.<prov>.json (85 MB, la pagina non li usa): ogni miniatura va direttamente in
# f/<chiave>.webp, chiave = id del luogo o "@<istat>" per la foto del comune (come fotoSrc() nella pagina).
for f in glob.glob(G + 'foto.*.json') + glob.glob(G + 'fa.*.json'): os.remove(f)
if os.path.isdir(G + 'img'): shutil.rmtree(G + 'img')
FD = G + 'f/'; os.makedirs(FD, exist_ok=True); nuove = uguali = 0
for k, src in alb.items():
    dst = FD + k + '.webp'; dati = open(src, 'rb').read()
    if os.path.exists(dst) and os.path.getsize(dst) == len(dati) and open(dst, 'rb').read() == dati: uguali += 1; continue
    open(dst, 'wb').write(dati); nuove += 1
via = 0
for f in os.listdir(FD):
    if f.endswith('.webp') and f[:-5] not in alb: os.remove(FD + f); via += 1
b = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode()
name = 'foto.%s.json' % hashlib.sha256(b).hexdigest()[:10]
open(G + name, 'wb').write(b)
m = json.load(open(G + 'manifest.json')); m['foto'] = name; m.pop('fa', None)
json.dump(m, open(G + 'manifest.json', 'w'), ensure_ascii=False)
print('foto in guida:', len(out), name, 'miniature in f/:', len(alb), '(nuove %d, uguali %d, tolte %d)' % (nuove, uguali, via),
      'peso f/ MB:', round(sum(os.path.getsize(FD + x) for x in os.listdir(FD)) / 1048576, 1))
