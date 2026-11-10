"""10/11/2026 sesta ricerca foto, eseguita da GitHub Actions in 5 lavori paralleli (uno per gruppo di regioni).
Uso: python actions_foto6.py <gruppo 0-4>
Legge sorgenti/foto/coda6.json (luoghi senza foto, da gen_coda6.py) e lavora solo i luoghi del gruppo non ancora in
out/provati6-<gruppo>.json. Due vie:
 A) Wikipedia in italiano: immagine principale della voce (API pageimages, solo immagini libere, 50 titoli per richiesta).
    Titoli provati: nome del luogo, «nome (comune)», varianti del nome. La voce vale solo se non è una disambigua, se il titolo
    contiene le parole distintive del luogo e se la voce ha coordinate entro 25 km dal comune o cita il comune nel titolo.
 B) Commons per coordinate (geosearch entro 150 m): dalle coordinate del luogo, quando ci sono, o della voce di Wikipedia
    trovata ma senza immagine. Preferita la foto con le parole del luogo nel titolo; altrimenti la più vicina entro 50 m.
Ogni 15 minuti salva sul ramo «foto» meta-<gruppo>.json e provati6-<gruppo>.json (poi il ramo viene unito da unisci_ramo.py)."""
import json, os, re, sys, time, html, hashlib, math, subprocess, unicodedata
import requests
from PIL import Image
from io import BytesIO
G = int(sys.argv[1]) if len(sys.argv) > 1 else 0
GRUPPI = [['piemonte', 'valle-d-aosta', 'liguria', 'sardegna'],
          ['lombardia', 'trentino-alto-adige', 'veneto', 'friuli-venezia-giulia'],
          ['emilia-romagna', 'toscana', 'marche', 'umbria'],
          ['lazio', 'abruzzo', 'molise', 'campania'],
          ['puglia', 'basilicata', 'calabria', 'sicilia']]
UA = {'User-Agent': "AchsPlacesGuide/0.3 (https://achplaces.com; guida turistica non commerciale) python-requests"}
OUT = 'out/'; os.makedirs(OUT + 'img', exist_ok=True)
FM = OUT + f'meta-{G}.json'; FP = OUT + f'provati6-{G}.json'
meta = json.load(open(FM)) if os.path.exists(FM) else {}
gia = set(json.load(open(OUT + 'meta.json'))) if os.path.exists(OUT + 'meta.json') else set()
for f in os.listdir(OUT):
    if f.startswith('meta-') and f.endswith('.json'): gia |= set(json.load(open(OUT + f)))
provati = set(json.load(open(FP))) if os.path.exists(FP) else set()
coda = [x for x in json.load(open('sorgenti/foto/coda6.json')) if x['reg'] in GRUPPI[G] and x['p'] not in provati and x['p'] not in gia]
print('gruppo', G, GRUPPI[G], 'da lavorare', len(coda), flush=True)
LIM = time.time() + 60 * float(os.environ.get('MINUTI', '300'))
S = requests.Session(); S.headers.update(UA)
def get(url, **kw):
    for k in range(6):
        try: r = S.get(url, timeout=60, **kw)
        except Exception: time.sleep(3 * (k + 1)); continue
        if r.status_code == 200: return r
        if r.status_code == 404: return None
        time.sleep(int(r.headers.get('retry-after', 0) or 0) + 2 * (k + 1))
    return None
def norm(t):
    t = unicodedata.normalize('NFD', (t or '').lower()); t = ''.join(c for c in t if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', ' ', t).strip()
def pulisci(s):
    s = re.sub(r'<[^>]+>', '', s or ''); s = html.unescape(s); return re.sub(r'\s+', ' ', s).strip()[:120]
def slug40(s):
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40]
STOP = set('di del della dei delle degli e la il lo le i gli d l a al alla in con sul sulla da dal dalla san santa santo s'.split())
GENW = set('chiesa museo palazzo castello torre piazza parrocchiale santuario basilica cattedrale duomo civico civica borgo centro storico lago parco rocca teatro fontana abbazia convento monastero villa ponte porta mura eremo oratorio pieve collegiata pinacoteca galleria cappella grotta grotte resti area archeologica archeologico sito antiquarium complesso monumentale riserva naturale oasi giardino orto botanico cascata cascate monte valle via corso nazionale comunale diocesano diocesana arte storia'.split())
BRUTTI = re.compile(r'stemma|coat[ _]of[ _]arms|wappen|blason|logo|mappa|map[ _.]|locator|flag|bandiera|cartina|pianta[ _]|planimetria|schema|diagram|signpost|cartello|targa|lapide|banner|painting|dipinto|olio su tela|oil on canvas|acquerello|watercolou?r|engraving|incisione|postcard|cartolina|\.svg|\.tif', re.I)
def distinte(t, com):
    ct = set(norm(com).split()); return [w for w in norm(t).split() if w not in STOP and w not in GENW and w not in ct and len(w) > 2]
def ha(ws, testo):
    tt = ' ' + testo + ' '; return all((' ' + w + ' ') in tt or (len(w) > 5 and w[:6] in testo) for w in ws)
def varianti(n):
    v = [re.sub(r'\s*\([^)]*\)', '', n).strip()] + re.findall(r'\(([^)]+)\)', n)
    v += [re.split(r'\s+e\s+|,|\s+[–-]\s+|:', v[0])[0].strip()]
    v += [x.strip() for x in re.split(r'\s+[–-]\s+|:', v[0])[1:]]
    out = []
    for x in v:
        if len(x) > 3 and x not in out: out.append(x)
    return out[:3]
def km(a, b, c, d):
    if None in (a, b, c, d): return 1e9
    r = math.pi / 180; x = math.sin((c - a) * r / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin((d - b) * r / 2) ** 2
    return 12742 * math.asin(math.sqrt(x))
WAPI = 'https://it.wikipedia.org/w/api.php'; CAPI = 'https://commons.wikimedia.org/w/api.php'

def via_wikipedia(lotto):
    """lotto: luoghi; per ognuno fino a 3 titoli; richieste da 50 titoli."""
    cand = []
    for x in lotto:
        ts = []
        for v in varianti(x['n']):
            ts += [v, f"{v} ({x['com']})"]
        x['_t'] = list(dict.fromkeys(t[:1].upper() + t[1:] for t in ts))[:4]
        cand += [(t, x) for t in x['_t']]
    for i in range(0, len(cand), 50):
        pezzo = cand[i:i + 50]
        r = get(WAPI, params={'action': 'query', 'format': 'json', 'formatversion': 2, 'redirects': 1, 'titles': '|'.join(t for t, _ in pezzo),
                              'prop': 'pageimages|coordinates|pageprops', 'piprop': 'name', 'pilicense': 'free', 'ppprop': 'disambiguation|wikibase_item'})
        if not r: continue
        q = r.json().get('query', {})
        mappa = {}
        for k in ('normalized', 'redirects'):
            for e in q.get(k, []): mappa[e['from']] = e['to']
        pagine = {p['title']: p for p in q.get('pages', []) if not p.get('missing')}
        for t, x in pezzo:
            if x.get('file'): continue
            tt = t
            for _ in range(3): tt = mappa.get(tt, tt)
            p = pagine.get(tt)
            if not p or 'disambiguation' in (p.get('pageprops') or {}): continue
            dv = distinte(x['n'], x['com']); tit = norm(p['title'])
            if dv and not ha(dv, tit): continue
            if not dv and norm(x['n']) not in tit: continue
            co = (p.get('coordinates') or [{}])[0]
            vicino = km(co.get('lat'), co.get('lon'), x.get('clat'), x.get('clng')) <= 25
            if not vicino and norm(x['com']) not in tit: continue
            if p.get('pageimage') and not BRUTTI.search(p['pageimage']):
                x['file'] = p['pageimage']; x['via'] = 'wikipedia'; x['wp'] = p['title']
            elif co.get('lat') is not None and not x.get('lat'):
                x['lat'], x['lng'] = co['lat'], co['lon']; x['geo_da'] = 'wikipedia'
        time.sleep(0.5)

def via_coordinate(x):
    r = get(CAPI, params={'action': 'query', 'format': 'json', 'list': 'geosearch', 'gscoord': f"{x['lat']}|{x['lng']}", 'gsradius': 150, 'gsnamespace': 6, 'gslimit': 30})
    hits = (r.json().get('query', {}).get('geosearch', []) if r else [])
    hits = [h for h in hits if re.search(r'\.(jpe?g|png|webp)$', h['title'], re.I) and not BRUTTI.search(h['title'])]
    dv = distinte(x['n'], x['com'])
    for h in hits:
        if dv and ha(dv, norm(h['title'])) and (norm(x['com']) in norm(h['title']) or not re.search(r'\d{4}|BEIC|Sicile|Farjasse', h['title'])): x['file'] = h['title'][5:]; x['via'] = 'coordinate'; return
    # niente ripiego sulla foto più vicina: dava edifici diversi dal luogo (verifica del 10/11)

def scarica(lotto):
    lotto = [x for x in lotto if x.get('file')]
    for i in range(0, len(lotto), 50):
        pz = lotto[i:i + 50]
        r = get(CAPI, params={'action': 'query', 'format': 'json', 'formatversion': 2, 'prop': 'imageinfo', 'iiprop': 'extmetadata|url', 'iiurlwidth': 330,
                              'iiextmetadatafilter': 'Artist|LicenseShortName', 'titles': '|'.join('File:' + x['file'].replace('_', ' ') for x in pz), 'maxlag': 5})
        if not r: continue
        q = r.json().get('query', {}); nm = {e['to']: e['from'] for e in q.get('normalized', [])}; info = {}
        for pg in q.get('pages', []):
            ii = (pg.get('imageinfo') or [None])[0]
            if ii: info[nm.get(pg['title'], pg['title'])[5:].replace('_', ' ')] = ii
        for x in pz:
            ii = info.get(x['file'].replace('_', ' '))
            if not ii: continue   # file non su Commons (per esempio solo su it.wikipedia): non si usa
            em = ii.get('extmetadata', {}); lic = pulisci(em.get('LicenseShortName', {}).get('value'))
            if not lic or re.search(r'non.?free|fair.?use', lic, re.I): continue
            aut = pulisci(em.get('Artist', {}).get('value')) or 'vedi pagina del file'
            t = get(ii.get('thumburl') or ii['url'])
            if not t: continue
            try:
                im = Image.open(BytesIO(t.content)).convert('RGB'); w, h = im.size; s = min(w, h)
                im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((168, 168), Image.LANCZOS)
                fn = slug40(x['p'].replace('--', '-'))[:40] + '-' + hashlib.md5(x['p'].encode()).hexdigest()[:6] + '.webp'
                im.save(OUT + 'img/' + fn, 'WEBP', quality=72, method=6)
                col = '#%02x%02x%02x' % im.resize((1, 1)).getpixel((0, 0))
            except Exception: continue
            meta[x['p']] = [fn, aut, lic, ii.get('descriptionurl', ''), col, x['file'], x['via']]
            time.sleep(0.15)
        time.sleep(0.5)

def salva(msg):
    json.dump(meta, open(FM, 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(sorted(provati), open(FP, 'w'))
    if os.environ.get('NO_PUSH'): return
    sh = lambda *a: subprocess.run(['git', '-C', OUT] + list(a), capture_output=True, text=True)
    sh('add', '--sparse', '-A'); c = sh('commit', '-q', '-m', f'Foto gruppo {G}: {msg} ({len(meta)} trovate)')
    if 'nothing to commit' in (c.stdout + c.stderr): return
    for k in range(6):
        sh('pull', '--rebase', '-q', 'origin', 'foto')
        if sh('push', '-q', 'origin', 'HEAD:foto').returncode == 0: print('salvato', msg, len(meta), flush=True); return
        time.sleep(5 + 5 * k)
    print('salvataggio non riuscito', flush=True)

ultimo = time.time()
for i in range(0, len(coda), 50):
    if time.time() > LIM: break
    lotto = coda[i:i + 50]
    try: via_wikipedia([x for x in lotto if not x.get('lat')])
    except Exception as e: print('wikipedia', e, flush=True)
    for x in lotto:
        if not x.get('file') and x.get('lat') is not None:
            try: via_coordinate(x)
            except Exception: pass
            time.sleep(0.2)
    try: scarica(lotto)
    except Exception as e: print('scarica', e, flush=True)
    for x in lotto: provati.add(x['p'])
    if i % 500 == 0: print('fatti', i + len(lotto), 'foto', len(meta), flush=True)
    if time.time() - ultimo > 15 * 60: salva('parziale'); ultimo = time.time()
salva('fine')
print('FINE gruppo', G, 'foto', len(meta), 'provati', len(provati))
