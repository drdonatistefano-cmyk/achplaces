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
        alb.setdefault(ch, {})[k] = base64.b64encode(open(F + 'img/' + v['img'], 'rb').read()).decode()
# 10/11/2026 ripiego: foto libera del comune (Wikidata P18) per i luoghi senza foto propria; una sola immagine per comune
# nell'album (chiave "@<istat>"), la riga del luogo ha in sesta posizione la chiave e in settima il nome del comune.
R = '/home/claude/foto-ramo/'
if os.environ.get('FOTO_COMUNE') and os.path.exists(R + 'metacom.json'):   # 10/11: disattivato, Stefano vuole solo foto del luogo
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
            if ak not in alb.setdefault(ch, {}): alb[ch][ak] = base64.b64encode(open(R + 'img/' + v[0], 'rb').read()).decode()
    print('luoghi con foto del comune:', nc)
for f in glob.glob(G + 'foto.*.json') + glob.glob(G + 'fa.*.json'): os.remove(f)
if os.path.isdir(G + 'img'): shutil.rmtree(G + 'img')
fa = {}
for ch, d in sorted(alb.items()):
    b = json.dumps(d, separators=(',', ':')).encode()
    n = 'fa.%s.%s.json' % (ch, hashlib.sha256(b).hexdigest()[:10]); open(G + n, 'wb').write(b); fa[ch] = n
b = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode()
name = 'foto.%s.json' % hashlib.sha256(b).hexdigest()[:10]
open(G + name, 'wb').write(b)
m = json.load(open(G + 'manifest.json')); m['foto'] = name; m['fa'] = fa
json.dump(m, open(G + 'manifest.json', 'w'), ensure_ascii=False)
print('foto in guida:', len(out), name, 'album:', len(fa), 'peso album KB:', sum(os.path.getsize(G + x) for x in fa.values()) // 1024)
