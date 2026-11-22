"""10/11/2026 foto di ripiego: un'immagine libera del comune (proprietà P18 «immagine» dell'elemento Wikidata del comune,
trovato col codice ISTAT P635), per i luoghi rimasti senza foto propria. In guida compare con la didascalia
«Foto del comune di X, non del luogo». Solo licenze libere (si scartano non-free e fair use). Salva sul ramo «foto»
metacom.json {istat: [file webp, autore, licenza, pagina, colore, file Commons]} e img/com-<istat>.webp."""
import json, os, re, time, html, subprocess
import requests
from PIL import Image
from io import BytesIO
UA = {'User-Agent': "AchsPlacesGuide/0.3 (https://achplaces.com; guida turistica non commerciale) python-requests"}
OUT = 'out/'; os.makedirs(OUT + 'img', exist_ok=True); FM = OUT + 'metacom.json'
meta = json.load(open(FM)) if os.path.exists(FM) else {}
ist = sorted({str(x['istat']).zfill(6) for x in json.load(open('sorgenti/foto/coda6.json')) if x.get('istat')} - set(meta))
print('comuni da cercare', len(ist), flush=True)
S = requests.Session(); S.headers.update(UA)
def get(url, **kw):
    for k in range(6):
        try: r = S.get(url, timeout=90, **kw)
        except Exception: time.sleep(3 * (k + 1)); continue
        if r.status_code == 200: return r
        if r.status_code == 404: return None
        time.sleep(int(r.headers.get('retry-after', 0) or 0) + 3 * (k + 1))
    return None
def pulisci(s):
    s = re.sub(r'<[^>]+>', '', s or ''); s = html.unescape(s); return re.sub(r'\s+', ' ', s).strip()[:120]
img = {}
for i in range(0, len(ist), 300):
    v = ' '.join('"%s"' % c for c in ist[i:i + 300])
    q = 'SELECT ?c ?f WHERE { VALUES ?c { %s } ?x wdt:P635 ?c; wdt:P18 ?f. }' % v
    r = get('https://query.wikidata.org/sparql', params={'query': q, 'format': 'json'})
    for b in (r.json()['results']['bindings'] if r else []):
        img.setdefault(b['c']['value'], requests.utils.unquote(b['f']['value'].rsplit('/', 1)[-1]).replace('_', ' '))
    time.sleep(1)
print('comuni con immagine su Wikidata', len(img), flush=True)
cs = list(img.items())
for i in range(0, len(cs), 50):
    pz = cs[i:i + 50]
    r = get('https://commons.wikimedia.org/w/api.php', params={'action': 'query', 'format': 'json', 'formatversion': 2, 'prop': 'imageinfo',
            'iiprop': 'extmetadata|url', 'iiurlwidth': 330, 'iiextmetadatafilter': 'Artist|LicenseShortName', 'titles': '|'.join('File:' + f for _, f in pz), 'maxlag': 5})
    if not r: continue
    q = r.json().get('query', {}); nm = {e['to']: e['from'] for e in q.get('normalized', [])}; info = {}
    for pg in q.get('pages', []):
        ii = (pg.get('imageinfo') or [None])[0]
        if ii: info[nm.get(pg['title'], pg['title'])[5:].replace('_', ' ')] = ii
    for c, f in pz:
        ii = info.get(f)
        if not ii: continue
        em = ii.get('extmetadata', {}); lic = pulisci(em.get('LicenseShortName', {}).get('value'))
        if not lic or re.search(r'non.?free|fair.?use', lic, re.I): continue
        t = get(ii.get('thumburl') or ii['url'])
        if not t: continue
        try:
            im = Image.open(BytesIO(t.content)).convert('RGB'); w, h = im.size; s = min(w, h)
            im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((168, 168), Image.LANCZOS)
            fn = 'com-%s.webp' % c; im.save(OUT + 'img/' + fn, 'WEBP', quality=72, method=6)
            col = '#%02x%02x%02x' % im.resize((1, 1)).getpixel((0, 0))
        except Exception: continue
        meta[c] = [fn, pulisci(em.get('Artist', {}).get('value')) or 'vedi pagina del file', lic, ii.get('descriptionurl', ''), col, f]
        time.sleep(0.15)
    time.sleep(0.5)
json.dump(meta, open(FM, 'w'), ensure_ascii=False, separators=(',', ':'))
sh = lambda *a: subprocess.run(['git', '-C', OUT] + list(a), capture_output=True, text=True)
sh('add', '--sparse', '-A'); sh('commit', '-q', '-m', 'Foto dei comuni (ripiego): %d' % len(meta))
for k in range(6):
    sh('pull', '--rebase', '-q', 'origin', 'foto')
    if sh('push', '-q', 'origin', 'HEAD:foto').returncode == 0: print('salvato', len(meta)); break
    time.sleep(5 + 5 * k)
