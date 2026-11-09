"""Scrive la coda per GitHub Actions: luoghi senza foto, non già provati."""
import json, os
src = open('/home/claude/foto/foto.py').read()
exec(src.split("m=json.load(open(G+'manifest.json'))")[0])
m = json.load(open(G + 'manifest.json')); D = json.load(open(G + m['dati']))
R = '/home/claude/foto-ramo/'
meta = json.load(open(R + 'meta.json')); prov = set(json.load(open(R + 'provati.json')) if os.path.exists(R+'provati.json') else [])
c = json.load(open(F + 'foto2.json'))
pid_of = lambda cc, a: (cc['slug'] + '--' + (a[0] if a[0] else slug40(a[1]))) if cc['slug'] else a[0]
coda = []
for cc in D['c']:
    for a in cc['places']:
        p = pid_of(cc, a)
        r = c.get(p, {})
        if p in meta and r.get('img'): continue
        if p in prov and not (r.get('file') and r.get('file') != (meta.get(p) or [None]*6)[5]): continue   # già provato, salvo foto nuova da Wikidata
        if r.get('img') and r.get('l'): continue
        e = {'p': p, 'com': cc['name']}
        if r.get('file'): e['file'] = r['file']
        else:
            if r.get('cat'): e['cat'] = r['cat']
            e['q'] = a[1] + ' ' + cc['name']
        coda.append(e)
json.dump(coda, open('/home/claude/achplaces/sorgenti/foto/coda.json', 'w'), ensure_ascii=False, indent=0)
print('coda', len(coda))
