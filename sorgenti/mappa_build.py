#!/usr/bin/env python3
"""12/11/2026: pagina Luoghi con la mappa d'Italia (sostituisce la vecchia pagina Luoghi, filtri.html).

Legge i dati della Guida appena costruiti (manifest, dati, det per provincia, luoghi di Bologna) e scrive:
  mappa.<impronta>.json : confini (ISTAT via openpolis, CC BY), comuni con coordinate, luoghi con tipo e bollini,
                          link dei biglietti e i dettagli dei luoghi di Bologna (che non stanno nei file per provincia);
  filtri.html           : la pagina, da mappa_tpl.html.
La scheda di un luogo legge il file della sua provincia (det.<prov>.<impronta>.json), lo stesso della Guida.
"""
import hashlib, json, math, os, re, subprocess, sys, unicodedata, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from leggi_dati import righe
from fvtipi import T as tipo

M = json.load(open(os.path.join(HERE, 'manifest.json')))
d = righe(json.load(open(os.path.join(HERE, M['dati']))))
Z = d.get('dz')
def slug40(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
if Z:
    for c in d['c']:
        for k in ('regione', 'provName', 'provKind', 'verified'): c[k] = Z[k][c[k]]
        for a in c['places']:
            if a[0] == 0: a[0] = slug40(a[1])
            a[3] = Z['sub'][a[3]]; a[7] = Z['t'][a[7]]
DET = {}
for n in M['det'].values():
    for sl, ps in json.load(open(os.path.join(HERE, n))).items():
        for pid, x in ps.items():
            if pid != '_c': DET[pid] = x
CK = ["storia", "musei", "sacro", "natura", "locale"]
G6 = ['arch', 'mon', 'sacro', 'musei', 'nat', 'trad']
GEO = json.load(open(os.path.join(HERE, 'data', 'italia_geo.json')))
proj = lambda lat, lng: [round((lng - 6.5) * math.cos(math.radians(42)) * 100, 1), round((47.2 - lat) * 100, 1)]
BO = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs');eval(fs.readFileSync('" + os.path.join(HERE, 'data', 'places-bologna.js') + "','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES))"]))
LB = d.get('l', {}) or {}; TB = d.get('tb', {}) or {}; GB = d.get('gb', {}) or {}
geoB = d.get('g') or [44.4939, 11.3428]

C, P, TAGS, U, X, VER = [], [], [], [], {}, []
ti = lambda t: TAGS.index(t) if t in TAGS else (TAGS.append(t) or len(TAGS) - 1)
def ui(u):
    if not u: return -1
    if u not in U: U.append(u)
    return U.index(u)
def vi(v):
    if v not in VER: VER.append(v)
    return VER.index(v)
def tk(p):
    if p.get('tq'): return p['tq'], 1
    g = p.get('gy')
    if g and re.search(r'biglietto|ingresso|salta|ticket', g): return g, 1
    if p.get('ticketUrl'): return p['ticketUrl'], 0
    return None
def aggiungi(ci, p, pid_suffix, full):
    """p: dict con i campi della Guida; full: dettagli completi (solo Bologna)"""
    g, ts = tipo(dict(name=p['name'], desc=p.get('desc', '') or '', sub=p['sub'], cat=p['cat']))
    fl = ('g' if p.get('free') is True else 'P' if p.get('free') is False else '') + ('c' if p.get('card') else '') + ('u' if p.get('unesco') else '') + \
         ('i' if p.get('indoor') else '') + ('v' if p.get('view') else '') + ('w' if p.get('status') == 'warn' else 'x' if p.get('status') == 'closed' else '')
    i = len(P)
    t = tk(p)
    card = -2 if p.get('free') is True else (ui(t[0]) * 2 + t[1] if t else (ui(p['tf']) * 2 if p.get('tf') else -1))
    P.append([p['name'], ci, G6.index(g), [ti(x) for x in ts], fl, pid_suffix, card])
    x = {}
    for k_src, k in (('ticketUrl', 'tu'), ('tq', 'tq'), ('gy', 'gy'), ('tf', 'tf')):
        if p.get(k_src): x[k] = ui(p[k_src])
    if p.get('ps') is not None and p.get('free') is None: x['ps'] = p['ps']
    if p.get('lat') is not None and p.get('lng') is not None: x['ll'] = [p['lat'], p['lng']]
    if full: x['d'] = full
    elif p.get('desc'): x['ds'] = p['desc']
    if x: X[i] = x

# Bologna (luoghi completi nella pagina della Guida)
C.append(['Bologna', 'Bologna', 'emilia-romagna', 'u', *proj(*geoB), 'bologna-bo', 'BO', vi('6 novembre 2026')])
for p in BO:
    q = dict(p); l = LB.get(p['id'])
    if l:
        if l.get('biglietti'): q['ticketUrl'] = l['biglietti']
        if l.get('orari'): q['hoursUrl'] = l['orari']
        if l.get('off'): q['official'] = l['off']
    if TB.get(p['id']): q['tq'] = TB[p['id']]
    if GB.get(p['id']): q['gy'] = GB[p['id']]
    full = {k: q.get(k) for k in ('desc', 'why', 'access', 'official', 'ownSite', 'sources', 'tip', 'statusNote', 'hoursUrl', 'wk', 'address', 'price', 'duration') if q.get(k) not in (None, '', [])}
    aggiungi(0, q, p['id'], full)
for c in d['c']:
    ci = len(C)
    aw = ''.join(x[0] for x in (c.get('aw') or []))
    C.append([c['name'], c.get('provName') or c['prov'], c['regione'], aw, *(proj(c['lat'], c['lng']) if c.get('lat') else [None, None]), c['slug'], c['prov'], vi(c.get('verified', ''))])
    for a in c['places']:
        p = dict(id=c['slug'] + '--' + a[0], name=a[1], cat=CK[a[2]], sub=a[3], desc=a[4] or DET.get(c['slug'] + '--' + a[0], {}).get('desc', ''))
        f = a[5]
        p.update(free=True if 'F' in f else False if 'P' in f else None, card='c' in f, unesco='u' in f, view='v' in f, indoor='i' in f, status=a[6] or 'ok')
        if len(a) > 9 and isinstance(a[9], dict): p.update(a[9])
        sfx = 0 if a[0] == slug40(a[1]) else a[0]
        q = dict(p); q['desc'] = a[4]   # nella mappa la descrizione va solo per i luoghi che la hanno nell'indice
        aggiungi(ci, dict(p, desc=p['desc']), sfx, None)
        if not a[4]: X.get(len(P) - 1, {}).pop('ds', None)
miss = [c for c in C if c[4] is None]
assert not miss, ('comuni senza coordinate', [c[0] for c in miss[:5]])
# 12/11 sera: dati in due file. Il primo (confini, comuni, numeri dei luoghi) basta per disegnare la mappa
# ed e' piccolo; il secondo (nomi, link, schede) arriva subito dopo, in parallelo.
for x in P: assert '\n' not in x[0]
core = dict(R=[r['d'] for r in GEO['reg']], V=[p['d'] for p in GEO['pro']], C=C, T=TAGS, VER=VER,
            pc=[x[1] for x in P], pg=''.join(str(x[2]) for x in P), pt=[x[3] for x in P], pf=[x[4] for x in P])
assert all('\n' not in u for u in U)
nomi = dict(N='\n'.join(x[0] for x in P), S={str(i): x[5] for i, x in enumerate(P) if x[5]}, K=[x[6] for x in P],
            U='\n'.join(U), X=json.dumps(X, ensure_ascii=False, separators=(',', ':')))
def scrivi(pref, obj):
    t = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    n = pref + '.' + hashlib.sha256(t.encode()).hexdigest()[:10] + '.json'
    for f in glob.glob(os.path.join(HERE, pref + '.*.json')):
        if not f.endswith(n): os.remove(f)
    open(os.path.join(HERE, n), 'w').write(t)
    return n, t
nome, t = scrivi('mappa', core)
nomen, tn = scrivi('mappan', nomi)
M['mappa'] = nome; M['mappan'] = nomen
json.dump(M, open(os.path.join(HERE, 'manifest.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
tpl = open(os.path.join(HERE, 'mappa_tpl.html')).read()
open(os.path.join(HERE, 'filtri.html'), 'w').write(tpl.replace('/*MAPPA*/', json.dumps(nome)).replace('/*MAPPAN*/', json.dumps(nomen)).replace('__MAPPA_NOME__', nome).replace('__MAPPAN_NOME__', nomen))
print('mappa:', nome, len(t) // 1024, 'KB +', nomen, len(tn) // 1024, 'KB,', len(C), 'comuni,', len(P), 'luoghi,', len(U), 'link')
