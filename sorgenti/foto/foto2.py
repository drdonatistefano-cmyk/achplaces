"""Fase A senza l'API di Commons (bloccata con 429 da questo indirizzo):
abbinamento con Wikidata (SPARQL) + miniatura da upload.wikimedia.org.
Autore e licenza si aggiungono dopo con meta.py. Cache: foto2.json"""
import json, os, sys, time, hashlib, urllib.parse, subprocess
src = open('/home/claude/foto/foto.py').read()
exec(src.split("m=json.load(open(G+'manifest.json'))")[0])  # funzioni e costanti
from PIL import Image
m = json.load(open(G + 'manifest.json')); D = json.load(open(G + m['dati']))
try:
    BO = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs');eval(fs.readFileSync('" + G + "data/places-bologna.js','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES.map(p=>[p.id,p.name])))"]))
    D['c'].append({'name': 'Bologna', 'istat': '037006', 'slug': '', 'places': [[i, n] for i, n in BO]})
except Exception as e:
    print('Bologna non letta', e)
CF = F + 'foto2.json'
cache = json.load(open(CF)) if os.path.exists(CF) else {}
# riusa i risultati già ottenuti (test Umbria e primi comuni)
for f in ['foto-umbria-test.json', 'foto-0.json', 'foto-1.json', 'foto-2.json']:
    if os.path.exists(F + f):
        for k, v in json.load(open(F + f)).items():
            if k not in cache or ('img' in v and 'img' not in cache[k]):
                cache[k] = v
def salva():
    json.dump(cache, open(CF + '.tmp', 'w'), ensure_ascii=False); os.replace(CF + '.tmp', CF)
def thumb(fn):
    n = fn.replace(' ', '_'); h = hashlib.md5(n.encode()).hexdigest(); q = urllib.parse.quote(n)
    t = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/250px-{q}'
    if n.lower().endswith(('.tif', '.tiff')): t += '.jpg'
    return t
def scarica(p, r):
    url = thumb(r['file'])
    for k in range(5):
        b = subprocess.run(['curl', '-sL', '--max-time', '40', '-A', UA, '-o', F + 'tmp2', '-w', '%{http_code}', url], capture_output=True, text=True).stdout
        if b in ('200', '404'): break
        time.sleep(2 + 3 * k)
    if b != '200': return False
    try:
        im = Image.open(F + 'tmp2').convert('RGB'); w, h = im.size; s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((168, 168), Image.LANCZOS)
        fn = slug40(p.replace('--', '-'))[:40] + '-' + hashlib.md5(p.encode()).hexdigest()[:6] + '.webp'
        im.save(F + 'img/' + fn, 'WEBP', quality=72, method=6)
        r['img'] = fn; r['c'] = '#%02x%02x%02x' % im.resize((1, 1)).getpixel((0, 0))
        r['u'] = 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(r['file'].replace(' ', '_'))
        return True
    except Exception:
        return False
pid_of = lambda c, a: (c['slug'] + '--' + (a[0] if a[0] else slug40(a[1]))) if c['slug'] else a[0]
t0 = time.time(); fatti = 0
for c in D['c']:
    if all(pid_of(c, a) in cache for a in c['places']): continue
    items = sparql('''SELECT ?it ?itLabel ?img ?cat WHERE { ?com wdt:P635 "%s". ?it wdt:P131+ ?com. OPTIONAL{?it wdt:P18 ?img} OPTIONAL{?it wdt:P373 ?cat} FILTER(BOUND(?img)||BOUND(?cat)) SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". } }''' % c['istat'])
    n = 0
    for a in c['places']:
        pid = pid_of(c, a)
        if pid in cache: continue
        best, bs = None, 0
        for b in items:
            s = punteggio(a[1], b['itLabel']['value'], c['name'])
            if s > bs: bs, best = s, b
        rec = {'n': a[1], 'com': c['name'], 's': round(bs, 2)}
        if best and bs >= 0.76:
            rec['wd'] = best['it']['value'].rsplit('/', 1)[1]; rec['lab'] = best['itLabel']['value']
            if 'img' in best:
                rec['file'] = urllib.parse.unquote(best['img']['value'].split('FilePath/')[1]); rec['via'] = 'wikidata'
                if scarica(pid, rec): n += 1
                else: rec.pop('file', None)
            elif 'cat' in best: rec['cat'] = best['cat']['value']
        cache[pid] = rec
    salva(); fatti += 1
    print(c['name'], n, '/', len(c['places']), '%.0fs' % (time.time() - t0), flush=True)
salva()
print('FINE', sum('img' in v for v in cache.values()), '/', len(cache))
