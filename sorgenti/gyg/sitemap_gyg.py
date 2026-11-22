"""Eseguito da GitHub Actions: legge robots.txt e le sitemap pubbliche di GetYourGuide (sito italiano) e salva le pagine
attività https://www.getyourguide.it/<città>-l<id>/<titolo>-t<id>/ in sorgenti/gyg/prodotti.json:
[[url, slug_città, id_città, slug_titolo, id_attività], ...]."""
import gzip, json, re, time
import requests
UA = {'User-Agent': "AchsPlacesGuide/0.3 (https://achplaces.com; guida turistica) python-requests"}
S = requests.Session(); S.headers.update(UA)
def get(u):
    for k in range(4):
        try:
            r = S.get(u, timeout=60)
            if r.status_code == 200:
                b = r.content
                if u.endswith('.gz') or b[:2] == b'\x1f\x8b': b = gzip.decompress(b)
                return b.decode('utf-8', 'replace')
            if r.status_code in (403, 404): print('HTTP', r.status_code, u); return ''
        except Exception as e: print('err', u, e)
        time.sleep(3 * (k + 1))
    return ''
RX = re.compile(r'https://www\.getyourguide\.(?:com|it)/([^/]+)-l(\d+)/([^/]+)-t(\d+)/?$')
# solo le città italiane: nomi dei comuni ISTAT (come slug) più i nomi inglesi usati da GetYourGuide
import csv, unicodedata
def sl(x): return re.sub(r'[^a-z0-9]+', '-', ''.join(c for c in unicodedata.normalize('NFD', x.lower()) if not unicodedata.combining(c))).strip('-')
CITTA = {sl(r['comune']) for r in csv.DictReader(open('sorgenti/data/geo/comuni_istat.csv', encoding='utf-8'))}
CITTA |= set('rome florence venice naples milan turin genoa padua syracuse mantua pompeii vatican-city herculaneum amalfi-coast cinque-terre lake-como lake-garda capri sicily sardinia tuscany dolomites puglia apulia sorrento positano'.split())
coda = []
for base in ('https://www.getyourguide.it', 'https://www.getyourguide.com'):
    rob = get(base + '/robots.txt'); print(base, rob[:1200])
    coda += re.findall(r'(?im)^sitemap:\s*(\S+)', rob)
coda += ['https://www.getyourguide.it/sitemap.xml']
viste, prod = set(), {}
while coda:
    u = coda.pop(0)
    if u in viste or len(viste) > 4000: continue
    viste.add(u)
    t = get(u)
    locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', t)
    alt = re.findall(r'href="(https://www\.getyourguide\.it/[^"]+)"', t)   # versioni linguistiche (hreflang)
    if '<sitemapindex' in t:
        coda += [l for l in locs if l not in viste]
        continue
    for l in locs + alt:
        m = RX.match(l)
        if m and m.group(1) in CITTA: prod[m.group(4)] = [l, m.group(1), m.group(2), m.group(3), m.group(4)]
    if len(viste) % 50 == 0: print('sitemap', len(viste), 'attività Italia', len(prod), flush=True)
    time.sleep(0.2)
print('sitemap lette', len(viste), 'attività Italia', len(prod))
json.dump(sorted(prod.values(), key=lambda x: (x[1], x[4])), open('sorgenti/gyg/prodotti.json', 'w'), ensure_ascii=False, separators=(',', ':'))
