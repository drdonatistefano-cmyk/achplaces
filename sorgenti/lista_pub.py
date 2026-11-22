"""Elenco dei file da pubblicare (dal manifest) e differenze rispetto all'ultima pubblicazione dell'anteprima.
Uso: python3 lista_pub.py <ultimo_elenco.json>  -> scrive /tmp/pub_new.json, /tmp/pub_add.json, /tmp/pub_gone.json"""
import json, os, sys, re
H = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(H, 'manifest.json')))
def walk(v):
    if isinstance(v, str): yield v
    elif isinstance(v, dict):
        for x in v.values(): yield from walk(x)
    elif isinstance(v, list):
        for x in v: yield from walk(x)
new = sorted({s for s in walk(m) if re.search(r'\.[0-9a-f]{10}\.(json|js)$', s)} | {'index.html', 'filtri.html', 'manifest.json'})
miss = [a for a in new if not os.path.exists(os.path.join(H, a))]
assert not miss, miss
old = [x['as'] for x in json.load(open(sys.argv[1]))] if len(sys.argv) > 1 and os.path.exists(sys.argv[1]) else []
add = [a for a in new if a not in old or a in ('index.html', 'filtri.html', 'manifest.json')]
gone = [a for a in old if a not in new]
J = lambda L: [{'as': a, 'path': os.path.join(H, a)} for a in L]
json.dump(J(new), open('/tmp/pub_new.json', 'w')); json.dump(J(add), open('/tmp/pub_add.json', 'w')); json.dump(gone, open('/tmp/pub_gone.json', 'w'))
print(len(new), 'file;', len(add), 'da inviare;', len(gone), 'da togliere')
