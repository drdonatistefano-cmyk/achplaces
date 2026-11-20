"""20/11/2026 ottava ricerca foto, per i luoghi che hanno solo la foto del comune (o nessuna), su decisione di Stefano.
Uso: python actions_foto8.py <gruppo 0-4>. Eseguito da GitHub Actions (foto8.yml) sul ramo claude/foto-cerca8.
Via nuova rispetto alle sette ricerche precedenti: Wikidata.
 1) si cerca l'elemento Wikidata col nome del luogo (fino a 3 varianti del nome, in italiano);
 2) vale solo se il nome dell'elemento ha le parole distintive del luogo, non è una persona né un comune, e le sue
    coordinate sono entro 1,5 km dal luogo (se la guida ha le coordinate del luogo) o entro 8 km dal comune;
 3) foto: l'immagine dell'elemento (P18); se manca, una foto dalla sua categoria di Commons (P373), prima quelle col nome
    del luogo nel titolo.
Scarti come nella settima: stemmi, mappe, dipinti, cartoline, svg. Solo licenze libere, verificate su Commons.
Risultati in sorgenti/foto/r8/meta-<gruppo>.json {luogo: [img, autore, licenza, pagina, colore, file, via, (categoria), qid]}
e r8/img/. Li porta nella guida sorgenti/foto/integra8.py, dopo il controllo e il «pubblica» di Stefano."""
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
UA = {'User-Agent': "AchsPlacesGuide/0.5 (https://achplaces.com; guida turistica non commerciale) python-requests"}
OUT = 'sorgenti/foto/r8/'; os.makedirs(OUT + 'img', exist_ok=True)
FM = OUT + f'meta-{G}.json'; FP = OUT + f'provati-{G}.json'
meta = json.load(open(FM)) if os.path.exists(FM) else {}
provati = set(json.load(open(FP))) if os.path.exists(FP) else set()
coda = [x for x in json.load(open('sorgenti/foto/coda8.json')) if x['reg'] in GRUPPI[G] and x['p'] not in provati and x['p'] not in meta]
if os.environ.get('PROVA'): coda = coda[:int(os.environ['PROVA'])]
print('gruppo', G, GRUPPI[G], 'da lavorare', len(coda), flush=True)
LIM = time.time() + 60 * float(os.environ.get('MINUTI', '300'))
S = requests.Session(); S.headers.update(UA)
WD = 'https://www.wikidata.org/w/api.php'; CAPI = 'https://commons.wikimedia.org/w/api.php'


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
DEBOLI = set('ruderi rovine resti madre matrice antico antica antiche vecchio vecchia nuovo nuova principale'.split())
BRUTTI = re.compile(r'stemma|coat[ _]of[ _]arms|wappen|blason|logo|mappa|map[ _.]|locator|flag|bandiera|cartina|pianta[ _]|planimetria|schema|diagram|signpost|cartello|targa|lapide|banner|painting|dipinto|olio su tela|oil on canvas|acquerello|watercolou?r|engraving|incisione|xilografia|litografia|lithograph|woodcut|postcard|cartolina|\.svg|\.tif', re.I)
STORICHE = re.compile(r'Paolo Monti|BEIC|\b1[89]\d\d\b', re.I)
NO_TIPI = {'Q5', 'Q747074', 'Q515', 'Q1549591', 'Q3146899', 'Q4167410'}   # persona, comune d'Italia, città, frazione, diocesi, disambigua
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
def nome_ok(x, titolo, nome=None):
    nome = nome or x['n']; t = norm(titolo); com = norm(x['com'])
    dv = [w for w in distinte(nome, x['com']) if w not in DEBOLI]
    if dv: return ha(dv, t)
    pw = [w for w in norm(nome).split() if w not in STOP and w not in DEBOLI and len(w) > 1 and w not in set(com.split())]
    return bool(pw) and ha(pw, t) and (' ' + com + ' ') in (' ' + t + ' ' + ' '.join(x.get('_desc', [])) + ' ')


def candidati(x):
    ids = []
    for v in varianti(x['n']):
        for q in (v, f'{v} {x["com"]}'):
            r = get(WD, params={'action': 'wbsearchentities', 'format': 'json', 'search': q, 'language': 'it', 'uselang': 'it',
                                'type': 'item', 'limit': 7, 'maxlag': 5})
            for h in (r.json().get('search', []) if r else []):
                if h['id'] not in ids: ids.append(h['id'])
            time.sleep(0.1)
    return ids[:20]
def entita(ids):
    out = {}
    for i in range(0, len(ids), 50):
        r = get(WD, params={'action': 'wbgetentities', 'format': 'json', 'ids': '|'.join(ids[i:i + 50]), 'props': 'labels|aliases|claims|descriptions',
                            'languages': 'it|en', 'maxlag': 5})
        if r: out.update(r.json().get('entities', {}))
    return out
def valore(e, p):
    for c in e.get('claims', {}).get(p, []):
        v = c.get('mainsnak', {}).get('datavalue', {}).get('value')
        if v is not None: return v
    return None


def cerca(x):
    ids = candidati(x)
    if not ids: return
    E = entita(ids)
    for q in ids:
        e = E.get(q) or {}
        tipi = {c.get('mainsnak', {}).get('datavalue', {}).get('value', {}).get('id') for c in e.get('claims', {}).get('P31', [])}
        if tipi & NO_TIPI: continue
        nomi = [l['value'] for l in (e.get('labels') or {}).values()] + [a['value'] for v in (e.get('aliases') or {}).values() for a in v]
        x['_desc'] = [norm(d['value']) for d in (e.get('descriptions') or {}).values()]
        if not any(nome_ok(x, n) or any(nome_ok(x, n, nome=v) for v in varianti(x['n'])) for n in nomi): continue
        co = valore(e, 'P625') or {}
        la, lo = co.get('latitude'), co.get('longitude')
        if x.get('lat') is not None: vicino = km(la, lo, x['lat'], x['lng']) <= 1.5
        else: vicino = km(la, lo, x.get('clat'), x.get('clng')) <= 8
        if not vicino: continue
        img = valore(e, 'P18')
        if isinstance(img, str) and re.search(r'\.(jpe?g|png|webp)$', img, re.I) and not BRUTTI.search(img):
            x['file'] = img; x['via'] = 'wikidata-P18'; x['qid'] = q; return
        cat = valore(e, 'P373')
        if isinstance(cat, str):
            f = file_della('Category:' + cat, x)
            if f: x['file'] = f; x['via'] = 'wikidata-P373'; x['catf'] = 'Category:' + cat; x['qid'] = q; return


def file_della(cat, x):
    r = get(CAPI, params={'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtitle': cat, 'cmtype': 'file', 'cmlimit': 50, 'maxlag': 5})
    fs = [m['title'][5:] for m in (r.json().get('query', {}).get('categorymembers', []) if r else [])]
    fs = [f for f in fs if re.search(r'\.(jpe?g|png|webp)$', f, re.I) and not BRUTTI.search(f)]
    if not fs: return None
    dv = distinte(x['n'], x['com'])
    buoni = [f for f in fs if dv and ha(dv, norm(f))]
    return sorted(buoni or fs, key=lambda f: bool(STORICHE.search(f)))[0]


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
            if not ii: continue
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
            meta[x['p']] = [fn, aut, lic, ii.get('descriptionurl', ''), col, x['file'], x['via'], x.get('catf', ''), x.get('qid', '')]
            time.sleep(0.15)
        time.sleep(0.5)


def salva(msg):
    json.dump(meta, open(FM, 'w'), ensure_ascii=False, separators=(',', ':'))
    json.dump(sorted(provati), open(FP, 'w'))
    if os.environ.get('NO_PUSH'): return
    sh = lambda *a: subprocess.run(['git'] + list(a), capture_output=True, text=True)
    sh('add', OUT); c = sh('commit', '-q', '-m', f'Foto, ottava ricerca, gruppo {G}: {msg} ({len(meta)} trovate)')
    if 'nothing to commit' in (c.stdout + c.stderr): return
    ramo = os.environ.get('RAMO', 'claude/foto-cerca8')
    for k in range(8):
        sh('pull', '--rebase', '-q', 'origin', ramo)
        if sh('push', '-q', 'origin', 'HEAD:' + ramo).returncode == 0: print('salvato', msg, len(meta), flush=True); return
        time.sleep(5 + 5 * k)
    print('salvataggio non riuscito', flush=True); sys.exit(1)


if __name__ == '__main__':
    ultimo = time.time(); vie = {}
    for i in range(0, len(coda), 25):
        if time.time() > LIM: break
        lotto = coda[i:i + 25]
        for x in lotto:
            try: cerca(x)
            except Exception as e: print('errore', x['p'], e, flush=True)
        try: scarica(lotto)
        except Exception as e: print('scarica', e, flush=True)
        for x in lotto:
            provati.add(x['p'])
            if x['p'] in meta: vie[x['via']] = vie.get(x['via'], 0) + 1
        if i % 250 == 0: print('fatti', i + len(lotto), 'foto', len(meta), vie, flush=True)
        if time.time() - ultimo > 15 * 60: salva('parziale'); ultimo = time.time()
    salva('fine')
    print('FINE gruppo', G, 'foto', len(meta), 'provati', len(provati), vie)
