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
coda = [x for x in json.load(open('sorgenti/foto/coda.json')) if x['p'] not in meta or x.get('r3') or x.get('r2b') or x.get('r4')]   # r3: rifà anche i luoghi con foto scartata dal controllo
PROVATI = OUT + 'provati.json'
provati = set(json.load(open(PROVATI))) if os.path.exists(PROVATI) else set()
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
def norm(t):
    t = unicodedata.normalize('NFD', t.lower()); t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()
API = 'https://commons.wikimedia.org/w/api.php'
def risolvi(x):
    if x.get('cat'):
        r = get(API, params={'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtype': 'file', 'cmlimit': 10, 'cmtitle': 'Category:' + x['cat']})
        for m in (r.json().get('query', {}).get('categorymembers', []) if r else []):
            if re.search(r'\.(jpe?g|png|webp)$', m['title'], re.I): x['file'] = m['title'][5:]; x['via'] = 'categoria'; return
    if x.get('q'):
        r = get(API, params={'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6, 'gsrlimit': 5,
                             'gsrsearch': x['q'] + ' filetype:bitmap', 'prop': 'categories', 'cllimit': 50})
        pages = sorted((r.json().get('query', {}).get('pages', {}) if r else {}).values(), key=lambda p: p.get('index', 99))
        com = norm(x.get('com', ''))
        for pg in pages:
            cats = ' '.join(norm(c['title']) for c in pg.get('categories', []))
            if com and com in cats or com in norm(pg['title']):
                x['file'] = pg['title'][5:]; x['via'] = 'ricerca'; return

# 9/11/2026 seconda ricerca per i luoghi rimasti senza foto (voce "r2" nella coda): varianti del nome, categorie Commons del luogo,
# file con tutte le parole distintive nel titolo o nelle categorie e il comune nelle categorie.
STOP = set('di del della dei delle degli e la il lo le i gli d l a al alla in con sul sulla da dal dalla san santa santo s'.split())
GENW = set('chiesa museo palazzo castello torre piazza parrocchiale santuario basilica cattedrale duomo civico civica borgo centro storico lago parco rocca teatro fontana abbazia convento monastero villa ponte porta mura eremo oratorio pieve collegiata pinacoteca galleria cappella grotta grotte resti area archeologica archeologico sito antiquarium complesso monumentale riserva naturale oasi giardino orto botanico cascata cascate monte valle via corso nazionale comunale diocesano diocesana arte storia'.split())
BRUTTI = re.compile(r'stemma|coat[ _]of[ _]arms|wappen|blason|logo|mappa|map[ _.]|locator|flag|bandiera|cartina|pianta[ _]|planimetria|schema|diagram|signpost|cartello|targa|lapide|banner|painting|dipinto|olio su tela|oil on canvas|acquerello|watercolou?r|engraving|incisione|postcard|cartolina', re.I)
def distinte(t, com):
    ct = set(norm(com).split())
    return [w for w in norm(t).split() if w not in STOP and w not in GENW and w not in ct and len(w) > 2]
def ha(ws, testo):
    tt = ' ' + testo + ' '; return all((' ' + w + ' ') in tt or (len(w) > 5 and w[:6] in testo) for w in ws)
def varianti(n):
    v = [re.sub(r'\s*\([^)]*\)', '', n).strip()] + re.findall(r'\(([^)]+)\)', n)
    v += [re.split(r'\s+e\s+|,|\s+[–-]\s+|:', v[0])[0].strip()]
    v += [x.strip() for x in re.split(r'\s+[–-]\s+|:', v[0])[1:]]   # 9/11: anche la parte dopo il trattino, di solito la più specifica
    v = [v[0]] + sorted(v[1:], key=lambda x: -len(distinte(x, '')))
    out = []
    for x in v:
        if len(x) > 3 and x not in out: out.append(x)
    return out[:4]
def risolvi2(x):
    com = x.get('com', ''); cn = norm(com)
    for v in varianti(x['n']):
        dv = distinte(v, com)
        if not dv: continue
        r = get(API, params={'action': 'query', 'format': 'json', 'list': 'search', 'srnamespace': 14, 'srlimit': 8, 'srsearch': v + ' ' + com})
        for h in (r.json().get('query', {}).get('search', []) if r else []):
            t = norm(h['title'][9:])
            if not ha(dv, t): continue
            if cn not in t:
                rc = get(API, params={'action': 'query', 'format': 'json', 'prop': 'categories', 'cllimit': 50, 'titles': h['title']})
                pc = ' '.join(norm(c['title']) for pg in (rc.json().get('query', {}).get('pages', {}).values() if rc else []) for c in pg.get('categories', []))
                if cn not in pc: continue
            rm = get(API, params={'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtype': 'file', 'cmlimit': 20, 'cmtitle': h['title']})
            for m in (rm.json().get('query', {}).get('categorymembers', []) if rm else []):
                if re.search(r'\.(jpe?g|png|webp)$', m['title'], re.I) and not BRUTTI.search(m['title']) and m['title'][5:].replace('_', ' ') != (x.get('no') or '').replace('_', ' '):
                    x['file'] = m['title'][5:]; x['via'] = 'categoria'; x['catf'] = h['title'][9:]; return
        r = get(API, params={'action': 'query', 'format': 'json', 'generator': 'search', 'gsrnamespace': 6, 'gsrlimit': 10,
                             'gsrsearch': v + ' ' + com + ' filetype:bitmap', 'prop': 'categories', 'cllimit': 50})
        pages = sorted((r.json().get('query', {}).get('pages', {}) if r else {}).values(), key=lambda p: p.get('index', 99))
        for pg in pages:
            if BRUTTI.search(pg['title']) or pg['title'][5:].replace('_', ' ') == (x.get('no') or '').replace('_', ' '): continue
            cl = [c['title'][9:] for c in pg.get('categories', [])]; cats = ' '.join(norm(c) for c in cl); tit = norm(pg['title'][5:])
            if cn not in cats and cn not in tit: continue
            if ha(dv, tit): x['file'] = pg['title'][5:]; x['via'] = 'ricerca'; return
            cm = [c for c in cl if ha(dv, norm(c))]
            if cm: x['file'] = pg['title'][5:]; x['via'] = 'categoria'; x['catf'] = cm[0]; return

# 9/11/2026 terza ricerca (voce "r3"): luoghi ad area vasta (parchi, monti, laghi, fiumi, riserve, coste, sentieri) che Wikidata non
# colloca nel comune ma nella provincia, nella regione o in un comune vicino, e luoghi la cui foto è stata scartata dal controllo.
# Ricerca per nome su Wikidata, accettata solo se l'elemento sta nel comune, nella sua provincia o regione, o in un comune della
# provincia, e se il nome coincide (stesse parole distintive, tipo compatibile). Foto: P18, altrimenti la categoria Commons P373.
WQ = 'https://query.wikidata.org/sparql'
def parole(t, com): return set(distinte(t, com))
def tipi3(t): return {w for w in norm(t).split() if w in GENW}
def risolvi3(x):
    ist = x.get('istat'); com = x.get('com', '')
    if not ist: return
    for v in varianti(x['n']):
        dv = parole(v, com); esatto = not dv   # nome uguale al comune (es. Monte Cetona a Cetona): serve l'etichetta identica
        if esatto: dv = {w for w in norm(v).split() if w not in STOP}
        if not dv: continue
        lab = v.replace('\\', '').replace('"', ' ')
        q = """SELECT DISTINCT ?it ?itLabel ?img ?cat ?ord WHERE {
 SERVICE wikibase:mwapi { bd:serviceParam wikibase:endpoint "www.wikidata.org"; wikibase:api "EntitySearch"; mwapi:search "%s"; mwapi:language "it"; mwapi:limit "10" . ?it wikibase:apiOutputItem mwapi:item . ?ord wikibase:apiOrdinal true . }
 ?com wdt:P635 "%s" . ?com wdt:P131 ?prov . OPTIONAL{?prov wdt:P131 ?reg}
 { ?it wdt:P131 ?com } UNION { ?it wdt:P131 ?prov } UNION { ?it wdt:P131 ?reg } UNION { ?it wdt:P131 ?a . ?a wdt:P131 ?prov } UNION { ?it wdt:P131 ?b . ?b wdt:P131 ?com }
 OPTIONAL{?it wdt:P18 ?img} OPTIONAL{?it wdt:P373 ?cat}
 SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". } } ORDER BY ?ord LIMIT 8""" % (lab, ist)
        r = get(WQ, params={'query': q, 'format': 'json'})
        for b in (r.json()['results']['bindings'] if r else []):
            el = b.get('itLabel', {}).get('value', '')
            de = {w for w in norm(el).split() if w not in STOP} if esatto else parole(el, com)
            if esatto and de != dv: continue
            if not de or not (de <= dv or dv <= de) or not (de & dv): continue
            ta, tb = tipi3(v), tipi3(el)
            if ta and tb and not (ta & tb): continue
            f = ''
            if 'img' in b: f = urllib.parse.unquote(b['img']['value'].split('Special:FilePath/')[-1])
            elif 'cat' in b:
                rm = get(API, params={'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtype': 'file', 'cmlimit': 20, 'cmtitle': 'Category:' + b['cat']['value']})
                for m in (rm.json().get('query', {}).get('categorymembers', []) if rm else []):
                    if re.search(r'\.(jpe?g|png|webp)$', m['title'], re.I) and not BRUTTI.search(m['title']): f = m['title'][5:]; break
            if f and not BRUTTI.search(f) and f.replace('_', ' ') != (x.get('no') or '').replace('_', ' '):
                x['file'] = f; x['via'] = 'wikidata-area'; x['lab'] = el; return
PROVATI2 = OUT + 'provati2.json'
provati2 = set(json.load(open(PROVATI2))) if os.path.exists(PROVATI2) else set()
da_risolvere = [x for x in coda if not x.get('file') and x['p'] not in provati and not x.get('r2') and not x.get('r3') and not x.get('r4')]
print('da risolvere', len(da_risolvere), flush=True)
for i, x in enumerate(da_risolvere):
    if time.time() > LIM: break
    try: risolvi(x)
    except Exception: pass
    provati.add(x['p'])
    if i % 200 == 0: print('risolti', i, flush=True); json.dump(sorted(provati), open(PROVATI, 'w'))
    time.sleep(0.1)
json.dump(sorted(provati), open(PROVATI, 'w'))
seconda = [x for x in coda if (x.get('r2') and x['p'] not in provati2 or x.get('r2b') and x['p'] + '|b' not in provati2) and not x.get('file')]
print('seconda ricerca', len(seconda), flush=True)
for i, x in enumerate(seconda):
    if time.time() > LIM - 1800: break
    try: risolvi2(x)
    except Exception: pass
    provati2.add(x['p'] + ('|b' if x.get('r2b') else ''))
    if i % 200 == 0: print('seconda', i, sum(1 for y in seconda if y.get('file')), flush=True); json.dump(sorted(provati2), open(PROVATI2, 'w'))
    time.sleep(0.05)
json.dump(sorted(provati2), open(PROVATI2, 'w'))
PROVATI3 = OUT + 'provati3.json'
provati3 = set(json.load(open(PROVATI3))) if os.path.exists(PROVATI3) else set()
terza = [x for x in coda if x.get('r3') and not x.get('file') and x['p'] not in provati3]
print('terza ricerca', len(terza), flush=True)
for i, x in enumerate(terza):
    if time.time() > LIM - 1200: break
    try: risolvi3(x)
    except Exception: pass
    provati3.add(x['p'])
    if i % 100 == 0: print('terza', i, sum(1 for y in terza if y.get('file')), flush=True); json.dump(sorted(provati3), open(PROVATI3, 'w'))
    time.sleep(0.5)
json.dump(sorted(provati3), open(PROVATI3, 'w'))

# 9/11/2026 quarta ricerca (voce "r4"): luoghi ancora senza foto dopo le prime tre.
# A) albero delle categorie Commons del comune (P373 del comune, sottocategorie fino a 2 livelli, es. «Churches in X»):
#    si cerca la sottocategoria che contiene tutte le parole distintive del luogo e se ne prende una foto.
# B) Openverse (foto con licenza libera da Flickr e altri archivi): solo licenze CC BY, CC BY-SA, CC0 e pubblico dominio
#    (mai NC o ND); titolo o etichette devono citare il luogo E il comune.
ALBERI = {}
def albero(ist):
    if ist in ALBERI: return ALBERI[ist]
    cats = []
    r = get(WQ, params={'query': 'SELECT ?cat WHERE { ?c wdt:P635 "%s" ; wdt:P373 ?cat } LIMIT 1' % ist, 'format': 'json'})
    b = r.json()['results']['bindings'] if r else []
    if b:
        radice = b[0]['cat']['value']; cats = [radice]; livello = [radice]
        for _ in range(2):
            nuovi = []
            for c in livello:
                rm = get(API, params={'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtype': 'subcat', 'cmlimit': 500, 'cmtitle': 'Category:' + c})
                for m in (rm.json().get('query', {}).get('categorymembers', []) if rm else []):
                    t = m['title'][9:]
                    if t not in cats: cats.append(t); nuovi.append(t)
                if len(cats) > 600: break
            livello = nuovi[:300]
    ALBERI[ist] = cats; return cats
OV = {'ok': True}
def openverse(x, v, dv, cn):
    if not OV['ok']: return
    r = S.get('https://api.openverse.org/v1/images/', timeout=60, params={'q': v + ' ' + x['com'], 'license': 'by,by-sa,cc0,pdm', 'page_size': 20, 'mature': 'false'})
    if r.status_code == 429: OV['ok'] = False; print('openverse: limite raggiunto', flush=True); return
    if r.status_code != 200: return
    for h in r.json().get('results', []):
        testo = norm((h.get('title') or '') + ' ' + ' '.join(t.get('name', '') for t in (h.get('tags') or [])))
        if BRUTTI.search(h.get('title') or ''): continue
        if not ha(dv, testo) or cn not in testo: continue
        lic = ('CC0' if h.get('license') == 'cc0' else 'Pubblico dominio' if h.get('license') == 'pdm' else 'CC ' + h.get('license', '').upper() + ' ' + (h.get('license_version') or '')).strip()
        x['file'] = (h.get('title') or v) + ' ' + x['com']; x['via'] = 'openverse'
        x['ov'] = [pulisci(h.get('creator')) or 'vedi pagina della foto', lic, h.get('foreign_landing_url') or '', h.get('thumbnail') or h.get('url')]
        return
def risolvi4(x):
    com = x.get('com', ''); cn = norm(com); ist = x.get('istat')
    vs = [(v, distinte(v, com)) for v in varianti(x['n'])]; vs = [(v, d) for v, d in vs if d]
    if not vs: return
    cats = albero(ist) if ist else []
    for v, dv in vs:
        cand = sorted([c for c in cats if ha(dv, norm(c))], key=len)
        for c in cand[:3]:
            rm = get(API, params={'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtype': 'file', 'cmlimit': 20, 'cmtitle': 'Category:' + c})
            for m in (rm.json().get('query', {}).get('categorymembers', []) if rm else []):
                f = m['title'][5:]
                if re.search(r'\.(jpe?g|png|webp)$', f, re.I) and not BRUTTI.search(f) and f.replace('_', ' ') != (x.get('no') or '').replace('_', ' '):
                    x['file'] = f; x['via'] = 'albero'; x['catf'] = c; return
    for v, dv in vs[:2]:
        openverse(x, v, dv, cn)
        if x.get('file'): return
        time.sleep(1)
PROVATI4 = OUT + 'provati4.json'
provati4 = set(json.load(open(PROVATI4))) if os.path.exists(PROVATI4) else set()
quarta = sorted([x for x in coda if x.get('r4') and not x.get('file') and x['p'] not in provati4], key=lambda x: x.get('istat', ''))
print('quarta ricerca', len(quarta), flush=True)
for i, x in enumerate(quarta):
    if time.time() > LIM - 900: break
    try: risolvi4(x)
    except Exception: pass
    provati4.add(x['p'])
    if i % 100 == 0: print('quarta', i, sum(1 for y in quarta if y.get('file')), flush=True); json.dump(sorted(provati4), open(PROVATI4, 'w'))
    time.sleep(0.05)
json.dump(sorted(provati4), open(PROVATI4, 'w'))
# foto Openverse: scaricate dalla miniatura, con autore, licenza e pagina originale
for x in [y for y in coda if y.get('ov')]:
    aut, lic, url, th = x['ov']
    t = get(th) if th else None
    if not t: continue
    try:
        im = Image.open(BytesIO(t.content)).convert('RGB'); w, h = im.size; s2 = min(w, h)
        im = im.crop(((w - s2) // 2, (h - s2) // 2, (w - s2) // 2 + s2, (h - s2) // 2 + s2)).resize((168, 168), Image.LANCZOS)
        fn = slug40(x['p'].replace('--', '-'))[:40] + '-' + hashlib.md5(x['p'].encode()).hexdigest()[:6] + '.webp'
        im.save(OUT + 'img/' + fn, 'WEBP', quality=72, method=6)
        col = '#%02x%02x%02x' % im.resize((1, 1)).getpixel((0, 0))
    except Exception: continue
    meta[x['p']] = [fn, aut, lic, url, col, x['file'], 'openverse']
json.dump(meta, open(OUT + 'meta.json', 'w'), ensure_ascii=False, separators=(',', ':'))
coda = [x for x in coda if x.get('file') and not x.get('ov')]
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
        meta[x['p']] = [fn, aut, lic, ii.get('descriptionurl', ''), col, x['file'], x.get('via', 'wikidata')]
        if x.get('catf'): meta[x['p']].append(x['catf'])
        elif x.get('lab'): meta[x['p']].append('')   # posto della categoria vuoto
        if x.get('lab'): meta[x['p']].append(x['lab'])
        fatti += 1
        time.sleep(0.2)
    json.dump(meta, open(OUT + 'meta.json', 'w'), ensure_ascii=False, separators=(',', ':'))
    print('lotto', i // 50 + 1, 'foto', fatti, flush=True)
    time.sleep(1)
json.dump(meta, open(OUT + 'meta.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print('FINE nuove', fatti, 'totale', len(meta))
