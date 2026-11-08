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
