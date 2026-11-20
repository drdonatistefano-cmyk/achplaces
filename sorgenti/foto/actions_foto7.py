"""19/11/2026 settima ricerca foto, per i luoghi che hanno solo la foto del comune (o nessuna), su richiesta di Stefano.
Uso: python actions_foto7.py <gruppo 0-4>. Eseguito da GitHub Actions (foto7.yml) sul ramo claude/foto-cerca.
Due vie nuove rispetto alle sei ricerche precedenti:
 A) categorie di Commons: ricerca «nome comune» fra le categorie; la categoria vale solo se il suo titolo contiene tutte le
    parole distintive del luogo e se il comune compare nel titolo o in una categoria madre (oppure le coordinate della
    categoria sono entro 15 km dal comune). Dalla categoria si prende una foto (prima quelle col nome del luogo nel titolo).
 B) file di Commons: ricerca «nome comune» fra i file; vale il file il cui titolo ha le parole distintive e il comune.
Scarti come nella sesta: stemmi, mappe, dipinti, cartoline, svg. Solo licenze libere.
Risultati in sorgenti/foto/r7/meta-<gruppo>.json {luogo: [img, autore, licenza, pagina, colore, file, via]} e r7/img/."""
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
UA = {'User-Agent': "AchsPlacesGuide/0.4 (https://achplaces.com; guida turistica non commerciale) python-requests"}
OUT = 'sorgenti/foto/r7/'; os.makedirs(OUT + 'img', exist_ok=True)
FM = OUT + f'meta-{G}.json'; FP = OUT + f'provati-{G}.json'
meta = json.load(open(FM)) if os.path.exists(FM) else {}
provati = set(json.load(open(FP))) if os.path.exists(FP) else set()
coda = [x for x in json.load(open('sorgenti/foto/coda7.json')) if x['reg'] in GRUPPI[G] and x['p'] not in provati and x['p'] not in meta]
if os.environ.get('PROVA'): coda = coda[:int(os.environ['PROVA'])]
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
BRUTTI = re.compile(r'stemma|coat[ _]of[ _]arms|wappen|blason|logo|mappa|map[ _.]|locator|flag|bandiera|cartina|pianta[ _]|planimetria|schema|diagram|signpost|cartello|targa|lapide|banner|painting|dipinto|olio su tela|oil on canvas|acquerello|watercolou?r|engraving|incisione|xilografia|litografia|lithograph|woodcut|postcard|cartolina|\.svg|\.tif', re.I)
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

WAPI = 'https://it.wikipedia.org/w/api.php'; CAPI = 'https://commons.wikimedia.org/w/api.php'

NOCAT = re.compile(r'^(tapestr|objects|collections?|exhibits|items|artifacts|reperti|oggetti|collezion|finds|interior)|people|persone|maps?\b|mappe|stemmi|coats? of arms|flags|bandiere|logos?\b|paintings|dipinti|postcards|cartoline|drawings|disegni|interior|interno|interni|details|dettagli|by year|\d{4}|sculptures|sculture|artworks|works by|events|eventi|sport|aerial', re.I)
DEBOLI = set('ruderi rovine resti madre matrice antico antica antiche vecchio vecchia nuovo nuova principale'.split())
def parole(n):
    return [w for w in norm(n).split() if w not in STOP and w not in DEBOLI and len(w) > 1]
def nome_ok(x, titolo, serve_comune=False, nome=None):
    nome = nome or x['n']
    t = norm(titolo); dv = [w for w in distinte(nome, x['com']) if w not in DEBOLI]; com = norm(x['com'])
    if dv:
        if not ha(dv, t): return False
        return (' ' + com + ' ') in (' ' + t + ' ') if serve_comune else True
    pw = [w for w in parole(nome) if w not in set(com.split())]
    return bool(pw) and ha(pw, t) and (' ' + com + ' ') in (' ' + t + ' ')
def cerca(q, ns, n=8):
    r = get(CAPI, params={'action': 'query', 'format': 'json', 'list': 'search', 'srsearch': q, 'srnamespace': ns, 'srlimit': n, 'maxlag': 5})
    return [h['title'] for h in (r.json().get('query', {}).get('search', []) if r else [])]
def cat_info(titoli):
    r = get(CAPI, params={'action': 'query', 'format': 'json', 'formatversion': 2, 'titles': '|'.join(titoli), 'prop': 'categories|coordinates',
                          'cllimit': 'max', 'clshow': '!hidden', 'maxlag': 5})
    out = {}
    for p in (r.json().get('query', {}).get('pages', []) if r else []):
        co = (p.get('coordinates') or [{}])[0]
        out[p['title']] = ([norm(c['title'][9:]) for c in p.get('categories', [])], co.get('lat'), co.get('lon'))
    return out
INGL = {'roma': 'rome', 'milano': 'milan', 'firenze': 'florence', 'venezia': 'venice', 'napoli': 'naples', 'torino': 'turin', 'genova': 'genoa', 'padova': 'padua', 'mantova': 'mantua', 'siracusa': 'syracuse'}
STORICHE = re.compile(r'Paolo Monti|BEIC|\b1[89]\d\d\b', re.I)
def file_della(cat, x):
    r = get(CAPI, params={'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtitle': cat, 'cmtype': 'file', 'cmlimit': 50, 'maxlag': 5})
    fs = [m['title'][5:] for m in (r.json().get('query', {}).get('categorymembers', []) if r else [])]
    fs = [f for f in fs if re.search(r'\.(jpe?g|png|webp)$', f, re.I) and not BRUTTI.search(f)]
    if not fs: return None
    dv = distinte(x['n'], x['com'])
    buoni = [f for f in fs if dv and ha(dv, norm(f))]
    ordina = lambda l: sorted(l, key=lambda f: bool(STORICHE.search(f)))
    return ordina(buoni or fs)[0]
def via_categorie(x):
    com = norm(x['com']); visti = []
    for v in varianti(x['n']):
        for q in (f'{v} {x["com"]}', v):
            for t in cerca(q, 14):
                if t in visti: continue
                visti.append(t)
                ct = t[9:]
                if NOCAT.search(ct) or not (nome_ok(x, ct) or nome_ok(x, ct, nome=v)): continue
                yield t
def via_A(x):
    cand = list(dict.fromkeys(via_categorie(x)))[:6]
    if not cand: return
    info = cat_info(cand); com = norm(x['com'])
    for t in cand:
        madri, la, lo = info.get(t, ([], None, None))
        vicino = km(la, lo, x.get('clat'), x.get('clng')) <= 5
        par = re.findall(r'\(([^)]+)\)', t)
        if par and not vicino and not any((' ' + com + ' ') in (' ' + norm(q) + ' ') or norm(q) == INGL.get(com) for q in par): continue   # «(Bologna)» per un luogo di Ozzano: è un altro posto
        dentro = (' ' + com + ' ') in (' ' + norm(t) + ' ') or any((' ' + com + ' ') in (' ' + m + ' ') or (INGL.get(com) and (' ' + INGL[com] + ' ') in (' ' + m + ' ')) for m in madri)
        if not dentro and km(la, lo, x.get('clat'), x.get('clng')) > 15: continue
        f = file_della(t, x)
        if f: x['file'] = f; x['via'] = 'categoria'; x['catf'] = t; return
def via_B(x):
    for v in varianti(x['n'])[:2]:
        if not [w for w in distinte(v, x['com']) if w not in DEBOLI]: continue
        for t in cerca(f'{v} {x["com"]}', 6):
            f = t[5:]
            if not re.search(r'\.(jpe?g|png|webp)$', f, re.I) or BRUTTI.search(f): continue
            if nome_ok(x, f, serve_comune=True) or nome_ok(x, f, serve_comune=True, nome=v): x['file'] = f; x['via'] = 'file'; return

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
    sh = lambda *a: subprocess.run(['git'] + list(a), capture_output=True, text=True)
    sh('add', OUT); c = sh('commit', '-q', '-m', f'Foto, settima ricerca, gruppo {G}: {msg} ({len(meta)} trovate)')
    if 'nothing to commit' in (c.stdout + c.stderr): return
    ramo = os.environ.get('RAMO', 'claude/foto-cerca')
    for k in range(8):
        sh('pull', '--rebase', '-q', 'origin', ramo)
        if sh('push', '-q', 'origin', 'HEAD:' + ramo).returncode == 0: print('salvato', msg, len(meta), flush=True); return
        time.sleep(5 + 5 * k)
    print('salvataggio non riuscito', flush=True)

ultimo = time.time(); vie = {}
for i in range(0, len(coda), 25):
    if time.time() > LIM: break
    lotto = coda[i:i + 25]
    for x in lotto:
        try:
            via_A(x)
            if not x.get('file'): via_B(x)
        except Exception as e: print('errore', x['p'], e, flush=True)
        time.sleep(0.2)
    try: scarica(lotto)
    except Exception as e: print('scarica', e, flush=True)
    for x in lotto:
        provati.add(x['p'])
        if x['p'] in meta:
            vie[x['via']] = vie.get(x['via'], 0) + 1
            if x.get('catf') and len(meta[x['p']]) == 7: meta[x['p']].append(x['catf'])
    if i % 250 == 0: print('fatti', i + len(lotto), 'foto', len(meta), vie, flush=True)
    if time.time() - ultimo > 15 * 60: salva('parziale'); ultimo = time.time()
salva('fine')
print('FINE gruppo', G, 'foto', len(meta), 'provati', len(provati), vie)
