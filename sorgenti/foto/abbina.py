"""Abbina i luoghi della guida agli elementi dell'archivio (archivio/prov-XXX.json), senza richieste in rete.
Aggiorna foto2.json: per ogni luogo nuovo salva wd, lab, file (se c'è) o cat. Le miniature le scarica scarica.py."""
import json, os, glob, subprocess
src = open('/home/claude/foto/foto.py').read()
exec(src.split("m=json.load(open(G+'manifest.json'))")[0])
m = json.load(open(G + 'manifest.json')); D = json.load(open(G + m['dati']))
try:
    BO = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs');eval(fs.readFileSync('" + G + "data/places-bologna.js','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES.map(p=>[p.id,p.name])))"]))
    D['c'].append({'name': 'Bologna', 'istat': '037006', 'slug': '', 'places': [[i, n] for i, n in BO]})
except Exception as e:
    print('Bologna non letta', e)
ARCH = {}
for f in glob.glob(F + 'archivio/prov-*.json'):
    for r in json.load(open(f)):
        ARCH.setdefault(r['istat'], []).append(r)
CF = F + 'foto2.json'
cache = json.load(open(CF)) if os.path.exists(CF) else {}
pid_of = lambda c, a: (c['slug'] + '--' + (a[0] if a[0] else slug40(a[1]))) if c['slug'] else a[0]
nuovi = conf = 0
for c in D['c']:
    items = ARCH.get(c.get('istat'))
    if not items: continue
    for a in c['places']:
        pid = pid_of(c, a)
        old = cache.get(pid)
        if old and ('img' in old or old.get('file') or old.get('arch') == 3): continue
        best, bs = None, 0
        ct = set(norm(c['name'])); nt = [w for w in norm(a[1]) if w not in ct]
        simile = lambda w, ws: any(w == x or (len(w) > 5 and len(x) > 5 and w[:6] == x[:6]) for x in ws)
        for b in items:
            import re as _re
            var = [a[1]] + [v.strip() for v in _re.split(r'[()]', a[1]) if len(v.strip()) > 3 and v.strip() != a[1]]   # «Colosseo (Anfiteatro Flavio)» → anche «Colosseo» e «Anfiteatro Flavio»
            s = max(punteggio(v, b['lab'], c['name']) for v in var)
            if s <= 0: continue
            ld = [w for w in norm(b['lab']) if w not in ct and w not in GEN and len(w) > 2]
            if not all(simile(w, nt) for w in ld): s *= 0.85   # etichetta con parole estranee al nome del luogo
            if b['file']: s += 0.02                             # a parità, preferisci chi ha la foto
            tx = ((b['cat'] or '') + ' ' + (b['file'] or '')).lower()
            if _re.search(r'\b(station|stazione|metro|metropolitana|fermata|railway|ferrovia|tram|bus|airport|aeroporto)\b', tx) and not _re.search(r'stazion|ferrovi|metro', a[1].lower()):
                s *= 0.8                                        # omonimi: stazioni e fermate (es. «Colosseo» metro C)
            if s > bs or (s == bs and best and int(b['wd'][1:]) < int(best['wd'][1:])): bs, best = s, b   # a parità, l'elemento più noto (Q più basso)
        rec = dict(old or {}); rec.update({'n': a[1], 'com': c['name'], 's': round(bs, 2), 'arch': 3})
        if best and bs >= 0.76:
            rec['wd'] = best['wd']; rec['lab'] = best['lab']
            if best['file']: rec['file'] = best['file']; rec['via'] = 'wikidata'; conf += 1
            elif best['cat']: rec['cat'] = best['cat']
        cache[pid] = rec; nuovi += 1
json.dump(cache, open(CF + '.tmp', 'w'), ensure_ascii=False); os.replace(CF + '.tmp', CF)
print('comuni in archivio', sum(1 for c in D['c'] if c.get('istat') in ARCH), '| luoghi abbinati ora', nuovi, '| con foto da scaricare', conf,
      '| totale con img', sum('img' in v for v in cache.values()))
