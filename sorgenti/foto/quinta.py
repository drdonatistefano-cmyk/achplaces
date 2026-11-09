"""9/11/2026 quinta ricerca, in locale (query.wikidata.org funziona da qui).
Per ogni comune con luoghi ancora senza foto: tutti gli elementi Wikidata collocati nel comune (P131 = comune, anche
di secondo livello) che hanno una foto (P18). Il luogo prende la foto dell'elemento con lo stesso nome:
- parole distintive dell'etichetta tutte presenti nel nome del luogo, tipo compatibile (castello con castello);
- etichetta del tipo «castello di <Comune>» (nessuna parola distintiva): valida se il nome del luogo ha lo stesso tipo,
  il nome del comune e al massimo parole deboli in più (reale, antico, ducale...), ed è l'unica candidata del suo tipo.
Scrive le voci "r5" (con il file già scelto) in coda.json: GitHub Actions scarica foto, autore e licenza."""
import json, os, re, sys, time
src = open('/home/claude/foto/foto.py').read()
exec(src.split("m=json.load(open(G+'manifest.json'))")[0])
m = json.load(open(G + 'manifest.json')); D = json.load(open(G + m['dati']))
sys.path.insert(0, '/home/claude/achs-places-guide'); from leggi_dati import righe; D = righe(D)
c = json.load(open(F + 'foto2.json'))
FIN = set(json.load(open(F + 'foto-finale.json')))
SC = json.load(open(F + 'controllo.json'))['scarti']
pid_of = lambda cc, a: (cc['slug'] + '--' + (a[0] if a[0] else slug40(a[1]))) if cc['slug'] else a[0]
WEAK = set('reale ducale antico antica vecchio vecchia nuovo nuova storico storica medievale monumentale principale grande maggiore comunale sabaudo estense visconteo sforzesco marchionale vescovile baronale feudale normanno svevo aragonese'.split())
BRUTTI = re.compile(r'stemma|coat[ _]of[ _]arms|wappen|blason|logo|mappa|map[ _.]|locator|flag|bandiera|cartina|pianta[ _]|planimetria|schema|diagram|signpost|cartello|targa|lapide|banner|painting|dipinto|engraving|incisione|postcard|cartolina', re.I)
CACHE = F + 'quinta-cache.json'
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
def elementi(ist):
    if ist in cache: return cache[ist]
    q = '''SELECT DISTINCT ?it ?l ?img WHERE { ?com wdt:P635 "%s" . { ?it wdt:P131 ?com } UNION { ?it wdt:P131 ?x . ?x wdt:P131 ?com }
 ?it wdt:P18 ?img . ?it rdfs:label ?l . FILTER(lang(?l)="it") } LIMIT 3000''' % ist
    b = sparql(q)
    out = [[x['l']['value'], urllib.parse.unquote(x['img']['value'].split('Special:FilePath/')[-1])] for x in b]
    cache[ist] = out
    return out
def sim(w, ws): return any(w == x or (len(w) > 5 and len(x) > 5 and w[:6] == x[:6]) for x in ws)
def varianti(n):
    v = [re.sub(r'\s*\([^)]*\)', '', n).strip()] + re.findall(r'\(([^)]+)\)', n)
    v += [x.strip() for x in re.split(r'\s+[–-]\s+|:', v[0])]
    return [x for i, x in enumerate(v) if x and x not in v[:i]]
def scegli(nome, com, els, no):
    C = set(norm(com)); best = []
    for v in varianti(nome):
        A = [w for w in norm(v) if w not in C]; DA = [w for w in A if w not in GEN]; TA = tipi(A)
        ha_com = all(w in norm(v) for w in C)
        for lab, f in els:
            if BRUTTI.search(f) or f.replace('_', ' ') == (no or '').replace('_', ' '): continue
            L = norm(lab); B = [w for w in L if w not in C]; DB = [w for w in B if w not in GEN]; TB = tipi(B)
            if TA and TB and not (TA & TB): continue
            if DB:
                if not all(sim(w, DA) for w in DB): continue
                s = len(DB) / max(len(DA), 1) + (0.2 if TA & TB else 0)
                if s < 0.6: continue
            else:
                if not (TA and TB and TA & TB) or not all(w in L for w in C) or not ha_com: continue
                if any(w not in WEAK for w in DA): continue
                s = 0.5
            best.append((s, lab, f))
    if not best: return None
    best.sort(key=lambda x: -x[0])
    top = [b for b in best if b[0] == best[0][0]]
    if len({b[2] for b in top}) > 1: return None   # ambiguo: due foto diverse con lo stesso punteggio
    return best[0]
coda_p = '/home/claude/achplaces/sorgenti/foto/coda.json'
coda = json.load(open(coda_p))
gia = {x['p'] for x in coda if x.get('r5')}
nuove = []; per = {}
for cc in D['c']:
    for a in cc['places']:
        p = pid_of(cc, a)
        if os.environ.get('SOLO') and os.environ['SOLO'] not in p: continue
        if p in FIN or p in gia or str(SC.get(p, '')).startswith('foto generica'): continue
        per.setdefault(cc.get('istat', ''), []).append((p, cc['name'], a[1]))
print('comuni', len(per), 'luoghi', sum(len(v) for v in per.values()), flush=True)
for i, (ist, ls) in enumerate(per.items()):
    if not ist: continue
    els = elementi(ist)
    for p, com, n in ls:
        r = scegli(n, com, els, (c.get(p) or {}).get('file'))
        if r: nuove.append({'p': p, 'com': com, 'n': n, 'file': r[2], 'via': 'wikidata-comune', 'lab': r[1], 'r5': 1})
    if i % 50 == 0:
        json.dump(cache, open(CACHE, 'w')); print(i, 'trovate', len(nuove), flush=True)
    time.sleep(0.3)
json.dump(cache, open(CACHE, 'w'))
json.dump(nuove, open(F + 'quinta-trovate.json', 'w'), ensure_ascii=False, indent=0)
print('FINE trovate', len(nuove))
