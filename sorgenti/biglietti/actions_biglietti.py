"""10/11/2026 sera: per i luoghi senza link al biglietto, legge le pagine ufficiali gia' citate (sito ufficiale e fonti)
e cerca 1) un link alla biglietteria o alle tariffe, 2) una frase esplicita di ingresso gratuito.
Gira su GitHub Actions (gratuito). Accetta una pagina solo se e' dedicata al luogo (titolo o intestazione con le parole
distintive del nome) oppure se il testo del link nomina il luogo. Scrive out/biglietti-<gruppo>.json:
  {id: {"tk": url, "da": pagina, "t": testo del link}}  oppure  {id: {"free": frase, "da": pagina}}"""
import json, os, re, sys, time, html, unicodedata
from urllib.parse import urljoin, urlparse
import requests
G = int(sys.argv[1]) if len(sys.argv) > 1 else 0
QUI = os.path.dirname(os.path.abspath(__file__))
coda = [x for x in json.load(open(os.path.join(QUI, 'coda.json'))) if x['g'] == G]
FO = f'out/biglietti-{G}.json'; os.makedirs('out', exist_ok=True)
fatto = json.load(open(FO)) if os.path.exists(FO) else {}
S = requests.Session(); S.headers.update({'User-Agent': 'AchsPlacesGuide/0.4 (+https://achplaces.com; guida turistica)', 'Accept-Language': 'it,en;q=0.5'})
def norm(t): return "".join(ch for ch in unicodedata.normalize("NFD", (t or '').lower()) if not unicodedata.combining(ch))
STOP = set('di del della dei delle degli e la il lo le i gli d l a al alla in con sul sulla da dal dalla san santa santo s'.split())
GEN = set('chiesa museo palazzo castello torre piazza parrocchiale santuario basilica cattedrale duomo civico civica borgo centro storico lago parco rocca teatro fontana abbazia convento monastero villa ponte porta mura eremo oratorio pieve collegiata pinacoteca galleria cappella grotta grotte resti area archeologica archeologico sito antiquarium complesso monumentale riserva naturale oasi giardino orto botanico cascata cascate monte valle via corso nazionale comunale diocesano diocesana arte storia cantine cantina sotterranee cattedrali'.split())
def distinte(n, com):
    ct = set(re.split(r'[^a-z0-9]+', norm(com)))
    return [w for w in re.split(r'[^a-z0-9]+', norm(re.split(r'[(]', n)[0])) if w and w not in STOP and w not in GEN and w not in ct and len(w) > 2]
TK = re.compile(r'bigliett|biglietteria|ticket|tariff|prezz|acquista|prenota|booking|admission|ingress[oi]\b|entrance fee|shop')
NO = re.compile(r'evento|event[io]?/|news|notizi|novita|blog|press|newsletter|cookie|privacy|login|facebook|instagram|twitter|youtube|tripadvisor|google|whatsapp|mailto:|tel:|\.pdf$|/20\d\d/', re.I)
BIGL = ('vivaticket', 'ticketone', 'coopculture', 'midaticket', 'ticketlandia', 'musement', 'eventbrite', 'clappit', 'boxol', 'liveticket', 'ticketsms', 'diyticket', 'arteventi', 'charta', 'museiitaliani', 'ticketmaster', 'getyourguide', 'tiqets')
FREE = re.compile(r"(ingresso|accesso|entrata|visita)\s+(e'\s+|è\s+)?(gratuit[oa]|libero|libera|gratis)|free (entry|admission|of charge)|admission is free|entrance is free|ingresso a offerta libera", re.I)
CACHE = {}
def leggi(u):
    if u in CACHE: return CACHE[u]
    t = ''
    try:
        r = S.get(u, timeout=20, allow_redirects=True)
        if r.status_code == 200 and 'html' in r.headers.get('content-type', ''): t = r.text[:900000]; u2 = r.url
        else: u2 = u
    except Exception: u2 = u
    CACHE[u] = (t, u2); time.sleep(0.4); return CACHE[u]
def testo(s): return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()
def esamina(x, u):
    h, base = leggi(u)
    if not h: return None
    dv = distinte(x['n'], x['c'])
    tit = norm(testo(' '.join(re.findall(r'<title[^>]*>(.*?)</title>', h, re.S | re.I)[:1] + re.findall(r'<h1[^>]*>(.*?)</h1>', h, re.S | re.I)[:2])))
    dedicata = bool(dv) and all(w in tit for w in dv)
    corpo = re.sub(r'<(script|style|nav|footer|header)[^>]*>.*?</\1>', ' ', h, flags=re.S | re.I)
    best = None
    for href, inner in re.findall(r'<a\s[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', corpo, re.S | re.I):
        t = testo(inner)[:120]; full = urljoin(base, href.strip())
        if not full.startswith('https://') or NO.search(full): continue
        lt = norm(t) + ' ' + norm(urlparse(full).path)
        if not TK.search(lt): continue
        host = urlparse(full).hostname or ''
        nomina = bool(dv) and all(w in norm(t + ' ' + full) for w in dv)
        if not (dedicata or nomina): continue
        punti = (3 if any(b in host for b in BIGL) else 0) + (2 if host == (urlparse(base).hostname or '') else 0) + (2 if re.search(r'bigliett|ticket|tariff', lt) else 0) + (1 if nomina else 0)
        if not best or punti > best[0]: best = (punti, full, t)
    if best and best[0] >= 2: return {'tk': best[1], 'da': base, 't': best[2]}
    if dedicata:
        m = FREE.search(testo(corpo))
        if m:
            tt = testo(corpo); i = m.start(); return {'free': tt[max(0, i - 90): i + 110], 'da': base}
    return None
print('gruppo', G, 'luoghi', len(coda), 'gia fatti', len(fatto), flush=True)
for k, x in enumerate(coda):
    if x['id'] in fatto: continue
    urls = list(dict.fromkeys([x['off']] + x['src']))[:5]
    r = None
    lette = 0
    for u in urls:
        if not u or not u.startswith('https://'): continue
        r = esamina(x, u)
        if CACHE.get(u, ('', ''))[0]: lette += 1
        if r and 'tk' in r: break
    # (10/11 23:00, coordinamento) Se nessuna pagina si e' aperta (sito lento, bloccato, fuori
    # servizio) il luogo NON si segna come fatto: si riprova al prossimo giro. Prima finiva in
    # «{}», cioe' «niente biglietto», e non veniva piu' guardato.
    if not r and not lette:
        continue
    fatto[x['id']] = r or {}
    if k % 300 == 0:
        json.dump(fatto, open(FO, 'w'), ensure_ascii=False)
        print(k, sum(1 for v in fatto.values() if 'tk' in v), 'biglietti', sum(1 for v in fatto.values() if 'free' in v), 'gratis', flush=True)
json.dump(fatto, open(FO, 'w'), ensure_ascii=False, sort_keys=True)
print('fine', sum(1 for v in fatto.values() if 'tk' in v), 'biglietti', sum(1 for v in fatto.values() if 'free' in v), 'gratis', 'su', len(coda))
