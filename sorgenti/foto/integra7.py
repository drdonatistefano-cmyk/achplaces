#!/usr/bin/env python3
"""20/11/2026: porta nella guida le foto della settima ricerca (sorgenti/foto/r7/), al posto della foto del comune.
Scarta: un file assegnato a più luoghi; esemplari da museo e cartelli; dalle categorie, i file il cui nome non ha
nessuna parola in comune né con la categoria né col comune (foto generiche della cartella).
Scrive foto.<impronta>.json e f/<luogo>.webp, aggiorna il manifest; poi va lanciato sorgenti/foto_split.py.
Uso: python3 sorgenti/foto/integra7.py [--secco]"""
import json, glob, os, re, sys, shutil, hashlib, collections, unicodedata
SECCO = '--secco' in sys.argv
R = 'sorgenti/foto/r7/'
def norm(s):
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if not unicodedata.combining(c)).lower()
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
VUOTE = set('della delle dello degli del dei di da la le il lo gli and the with from chiesa church file jpeg jpg png webp category'.split())
def parole(s):
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)          # «FossatoDiVicoSanBenedetto1»
    return {w for w in norm(s).split() if len(w) > 3 and w not in VUOTE}
NO = re.compile(r'MHNT|specimen|dorsal|ventral|herbari|bacheca|cartello|\bsign(board)?\b|consolle|segnaletica', re.I)
M = {}
for f in sorted(glob.glob(R + 'meta-*.json')): M.update(json.load(open(f)))
C = {x['p']: x for x in json.load(open('sorgenti/foto/coda7.json'))}
uso = collections.Counter(v[5] for v in M.values())
tolti = collections.Counter(); buoni = {}
for p, v in sorted(M.items()):
    fil = v[5]
    if uso[fil] > 1: tolti['stesso file su più luoghi'] += 1; continue
    if NO.search(fil): tolti['esemplari o cartelli'] += 1; continue
    if v[6] == 'categoria':
        cat = v[7][9:] if len(v) > 7 else ''
        if not (parole(fil) & (parole(cat) | parole(C[p]['com']) | parole(C[p]['n']))): tolti['foto generica della categoria'] += 1; continue
    if not os.path.exists(R + 'img/' + v[0]): tolti['immagine mancante'] += 1; continue
    buoni[p] = v
print('trovate', len(M), 'tenute', len(buoni), dict(tolti))
if SECCO: sys.exit()
m = json.load(open('manifest.json')); F = json.load(open(m['foto']))
nuove = 0
for p, v in buoni.items():
    if p in F and len(F[p]) != 7: continue          # ha già una foto propria
    ch = p.split('--')[0].rsplit('-', 1)[-1]
    F[p] = [ch, v[1], v[2], v[3], v[4]]
    shutil.copyfile(R + 'img/' + v[0], 'f/' + p + '.webp'); nuove += 1
usate = {v[5] for v in F.values() if len(v) == 7}
via = 0
for f in glob.glob('f/@*.webp'):
    if os.path.basename(f)[:-5] not in usate: os.remove(f); via += 1
b = json.dumps(dict(sorted(F.items())), ensure_ascii=False, separators=(',', ':')).encode()
nome = 'foto.%s.json' % hashlib.sha256(b).hexdigest()[:10]
if nome != m['foto']:
    os.remove(m['foto']); open(nome, 'wb').write(b); m['foto'] = nome
    json.dump(m, open('manifest.json', 'w'), ensure_ascii=False)
print('foto proprie nuove', nuove, 'foto del comune non più usate tolte', via, nome)
