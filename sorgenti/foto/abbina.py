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
        if old and ('img' in old or old.get('arch')): continue
        best, bs = None, 0
        for b in items:
            s = punteggio(a[1], b['lab'], c['name'])
            if s > bs: bs, best = s, b
        rec = dict(old or {}); rec.update({'n': a[1], 'com': c['name'], 's': round(bs, 2), 'arch': 1})
        if best and bs >= 0.76:
            rec['wd'] = best['wd']; rec['lab'] = best['lab']
            if best['file']: rec['file'] = best['file']; rec['via'] = 'wikidata'; conf += 1
            elif best['cat']: rec['cat'] = best['cat']
        cache[pid] = rec; nuovi += 1
json.dump(cache, open(CF + '.tmp', 'w'), ensure_ascii=False); os.replace(CF + '.tmp', CF)
print('comuni in archivio', sum(1 for c in D['c'] if c.get('istat') in ARCH), '| luoghi abbinati ora', nuovi, '| con foto da scaricare', conf,
      '| totale con img', sum('img' in v for v in cache.values()))
