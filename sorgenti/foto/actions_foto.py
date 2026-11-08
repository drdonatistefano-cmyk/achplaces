"""Eseguito da GitHub Actions (indirizzi non limitati da Wikimedia).
Legge sorgenti/foto/coda.json  [{"p": id_luogo, "file": "Nome file Commons.jpg"}, ...]
e completa la cartella out/ (ramo «foto»): out/img/<nome>.webp (168x168) e out/meta.json
{id_luogo: [img, autore, licenza, url_pagina, colore]}. Solo foto con licenza dichiarata."""
import json, os, re, sys, time, html, hashlib, unicodedata, urllib.parse
import requests
from PIL import Image
from io import BytesIO
UA = {'User-Agent': "AchsPlacesGuide/0.2 (https://achplaces.com; guida turistica non commerciale) python-requests"}
OUT = 'out/'; os.makedirs(OUT + 'img', exist_ok=True)
meta = json.load(open(OUT + 'meta.json')) if os.path.exists(OUT + 'meta.json') else {}
coda = [x for x in json.load(open('sorgenti/foto/coda.json')) if x['p'] not in meta]
LIM = time.time() + 60 * float(os.environ.get('MINUTI', '300'))
S = requests.Session(); S.headers.update(UA)
def get(url, **kw):
    for k in range(6):
        r = S.get(url, timeout=60, **kw)
        if r.status_code == 200: return r
        if r.status_code == 404: return None
        time.sleep(int(r.headers.get('retry-after', 0) or 0) + 2 * (k + 1))
    return None
def pulisci(s):
    s = re.sub(r'<[^>]+>', '', s or ''); s = html.unescape(s); return re.sub(r'\s+', ' ', s).strip()[:120]
def slug40(s):
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40]
print('in coda', len(coda), flush=True)
fatti = 0
for i in range(0, len(coda), 50):
    if time.time() > LIM: break
    lotto = coda[i:i + 50]
    titoli = '|'.join('File:' + x['file'].replace('_', ' ') for x in lotto)
    r = get('https://commons.wikimedia.org/w/api.php', params={'action': 'query', 'format': 'json', 'formatversion': 2,
            'prop': 'imageinfo', 'iiprop': 'extmetadata|url', 'iiurlwidth': 330,
            'iiextmetadatafilter': 'Artist|LicenseShortName', 'titles': titoli, 'maxlag': 5})
    if not r: continue
    q = r.json().get('query', {})
    norm = {x['to']: x['from'] for x in q.get('normalized', [])}
    info = {}
    for pg in q.get('pages', []):
        ii = (pg.get('imageinfo') or [None])[0]
        if ii: info[norm.get(pg['title'], pg['title'])[5:].replace('_', ' ')] = ii
    for x in lotto:
        ii = info.get(x['file'].replace('_', ' '))
        if not ii: continue
        em = ii.get('extmetadata', {})
        lic = pulisci(em.get('LicenseShortName', {}).get('value'))
        if not lic: continue
        aut = pulisci(em.get('Artist', {}).get('value')) or 'vedi pagina del file'
        t = get(ii.get('thumburl') or ii['url'])
        if not t: continue
        try:
            im = Image.open(BytesIO(t.content)).convert('RGB'); w, h = im.size; s = min(w, h)
            im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((168, 168), Image.LANCZOS)
            fn = slug40(x['p'].replace('--', '-'))[:40] + '-' + hashlib.md5(x['p'].encode()).hexdigest()[:6] + '.webp'
            im.save(OUT + 'img/' + fn, 'WEBP', quality=72, method=6)
            col = '#%02x%02x%02x' % im.resize((1, 1)).getpixel((0, 0))
        except Exception:
            continue
        meta[x['p']] = [fn, aut, lic, ii.get('descriptionurl', ''), col]; fatti += 1
        time.sleep(0.2)
    json.dump(meta, open(OUT + 'meta.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('lotto', i // 50 + 1, 'foto', fatti, flush=True)
    time.sleep(1)
json.dump(meta, open(OUT + 'meta.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('FINE nuove', fatti, 'totale', len(meta))
