#!/usr/bin/env python3
"""Passo dopo build.py e mkfiltri: aggiunge le foto (Wikimedia Commons) alla guida.
Usa /home/claude/foto/foto-finale.json (prodotto da controllo.py): solo foto con autore e licenza.
Scrive foto.<hash>.json, copia le immagini in img/ e aggiunge la chiave 'foto' al manifest."""
import json, hashlib, os, shutil, glob, subprocess
G = '/home/claude/achs-places-guide/'; F = '/home/claude/foto/'
subprocess.run(['python3', F + 'controllo.py'], check=True)
fin = json.load(open(F + 'foto-finale.json'))
out = {}
for k, v in sorted(fin.items()):
    if v.get('img') and v.get('l') and os.path.exists(F + 'img/' + v['img']):
        out[k] = [v['img'], v.get('a', ''), v['l'], v.get('u', ''), v.get('c', '')]
for f in glob.glob(G + 'foto.*.json'): os.remove(f)
if os.path.isdir(G + 'img'): shutil.rmtree(G + 'img')
os.makedirs(G + 'img')
for v in out.values(): shutil.copy2(F + 'img/' + v[0], G + 'img/' + v[0])
b = json.dumps(out, ensure_ascii=False, separators=(',', ':')).encode()
name = 'foto.%s.json' % hashlib.sha256(b).hexdigest()[:10]
open(G + name, 'wb').write(b)
m = json.load(open(G + 'manifest.json')); m['foto'] = name
json.dump(m, open(G + 'manifest.json', 'w'), ensure_ascii=False)
print('foto in guida:', len(out), name)
