"""Archivio foto: per ogni provincia (prefisso ISTAT) tutti gli elementi Wikidata con foto (P18) o categoria Commons (P373) nei suoi comuni."""
import json, os, sys, time
src = open('/home/claude/foto/foto.py').read()
exec(src.split("m=json.load(open(G+'manifest.json'))")[0])
A = F + 'archivio/'
m = json.load(open(G + 'manifest.json')); D = json.load(open(G + m['dati']))
import sys as _s9; _s9.path.insert(0,'/home/claude/achs-places-guide'); from leggi_dati import righe as _righe9; D = _righe9(D)   # 9/11: dati per colonne
pref = sorted({c['istat'][:3] for c in D['c'] if c.get('istat')} | {'037'})
if len(sys.argv) > 1: pref = sys.argv[1:]
for p in pref:
    out = A + 'prov-%s.json' % p
    if os.path.exists(out): continue
    q = '''SELECT ?istat ?it ?itLabel ?img ?cat WHERE { ?com wdt:P635 ?istat . FILTER(STRSTARTS(?istat,"%s")) ?it wdt:P131+ ?com . OPTIONAL{?it wdt:P18 ?img} OPTIONAL{?it wdt:P373 ?cat} FILTER(BOUND(?img)||BOUND(?cat)) SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". } }''' % p
    t = time.time()
    def prendi(px):
        qq = q.replace('"%s"' % p, '"%s"' % px)
        try:
            return sparql(qq)
        except Exception:
            if len(px) >= 5: print('  saltato', px, flush=True); return []
            out = []
            for d in '0123456789': out += prendi(px + d); time.sleep(1)
            return out
    r = prendi(p)
    rows = {}
    for b in r:
        k = (b['istat']['value'], b['it']['value'].rsplit('/', 1)[1])
        if k in rows: continue
        rows[k] = {'istat': k[0], 'wd': k[1], 'lab': b['itLabel']['value'],
                   'file': urllib.parse.unquote(b['img']['value'].split('FilePath/')[1]) if 'img' in b else None,
                   'cat': b['cat']['value'] if 'cat' in b else None}
    if r: json.dump(list(rows.values()), open(out, 'w'), ensure_ascii=False)
    print(p, len(rows), '%.0fs' % (time.time() - t), flush=True)
    time.sleep(1)
