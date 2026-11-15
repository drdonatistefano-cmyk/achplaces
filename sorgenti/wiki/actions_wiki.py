"""10/11/2026 sera: titolo esatto della voce di it.wikipedia per i luoghi che Wikidata non ha abbinato (wiki-wd.json).
Gira su GitHub Actions (il container di lavoro non raggiunge it.wikipedia). Per ogni luogo:
  1) titoli candidati (nome, «nome (comune)», varianti) controllati 50 per richiesta, con redirect;
  2) se nessuno va, ricerca nel testo di it.wikipedia «nome comune», primi 3 risultati.
Una voce si accetta solo se non e' una disambigua, il titolo contiene tutte le parole distintive del nome e le coordinate
della voce stanno entro 25 km dal comune (o il titolo nomina il comune). Scrive out/wiki-<gruppo>.json {id: titolo}."""
import json, os, sys, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'foto'))
sys.argv = [sys.argv[0], sys.argv[1] if len(sys.argv) > 1 else '0']
import importlib.util
sp = importlib.util.spec_from_file_location('f6', os.path.join(os.path.dirname(__file__), '..', 'foto', 'actions_foto6.py'))
G = int(sys.argv[1])
# riuso delle funzioni di confronto della ricerca foto, senza eseguirne il ciclo principale
src = open(sp.origin).read(); src = src[:src.index('def via_coordinate')]
ns = {'__name__': 'f6'}; exec(compile(src, sp.origin, 'exec'), ns)
get, norm, distinte, ha, varianti, km, WAPI = (ns[k] for k in ('get', 'norm', 'distinte', 'ha', 'varianti', 'km', 'WAPI'))
coda = [x for x in json.load(open(os.path.join(os.path.dirname(__file__), 'coda-wiki.json'))) if x['g'] == G]
FO = f'out/wiki-{G}.json'; os.makedirs('out', exist_ok=True)
fatto = json.load(open(FO)) if os.path.exists(FO) else {}
def buona(p, x):
    if not p or p.get('missing') or 'disambiguation' in (p.get('pageprops') or {}): return False
    dv = distinte(x['n'], x['com']); tit = norm(p['title'])
    if dv and not ha(dv, tit): return False
    if not dv and norm(x['n']) not in tit: return False
    co = (p.get('coordinates') or [{}])[0]
    return km(co.get('lat'), co.get('lon'), x.get('clat'), x.get('clng')) <= 25 or norm(x['com']) in tit
def pagine(titoli):
    r = get(WAPI, params={'action': 'query', 'format': 'json', 'formatversion': 2, 'redirects': 1, 'titles': '|'.join(titoli),
                          'prop': 'coordinates|pageprops', 'ppprop': 'disambiguation'})
    if not r: return {}, {}
    q = r.json().get('query', {}); mp = {}
    for k in ('normalized', 'redirects'):
        for e in q.get(k, []): mp[e['from']] = e['to']
    return mp, {p['title']: p for p in q.get('pages', [])}
lav = [x for x in coda if x['p'] not in fatto]
print('gruppo', G, 'da fare', len(lav), flush=True)
for i in range(0, len(lav), 12):
    lotto = lav[i:i + 12]; cand = []
    for x in lotto:
        ts = []
        for v in varianti(x['n']): ts += [v, f"{v} ({x['com']})"]
        x['_t'] = list(dict.fromkeys(t[:1].upper() + t[1:] for t in ts))[:4]; cand += [(t, x) for t in x['_t']]
    for j in range(0, len(cand), 50):
        pz = cand[j:j + 50]; mp, pg = pagine([t for t, _ in pz])
        for t, x in pz:
            if x['p'] in fatto: continue
            tt = t
            for _ in range(3): tt = mp.get(tt, tt)
            if buona(pg.get(tt), x): fatto[x['p']] = pg[tt]['title']
        time.sleep(0.3)
    for x in lotto:
        if x['p'] in fatto: continue
        r = get(WAPI, params={'action': 'query', 'format': 'json', 'formatversion': 2, 'list': 'search', 'srsearch': f"{x['n']} {x['com']}", 'srlimit': 3, 'srnamespace': 0})
        hits = [h['title'] for h in (r.json().get('query', {}).get('search', []) if r else [])]
        if hits:
            mp, pg = pagine(hits)
            for t in hits:
                if buona(pg.get(mp.get(t, t)), x): fatto[x['p']] = pg[mp.get(t, t)]['title']; break
        time.sleep(0.2)
    if i % 600 == 0:
        json.dump(fatto, open(FO, 'w'), ensure_ascii=False); print(i, len(fatto), flush=True)
json.dump(fatto, open(FO, 'w'), ensure_ascii=False, sort_keys=True)
print('trovati', len(fatto), 'su', len(coda))
