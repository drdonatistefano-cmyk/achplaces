"""Eseguito da GitHub Actions: legge robots.txt e le sitemap pubbliche di Tiqets e salva le pagine prodotto in italiano
(https://www.tiqets.com/it/...-p<id>/) in sorgenti/tiqets/prodotti.json: [[url, slug_città, slug_prodotto, id], ...]."""
import gzip, io, json, re, sys, time
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
rob = get('https://www.tiqets.com/robots.txt')
print(rob[:1500])
coda = re.findall(r'(?im)^sitemap:\s*(\S+)', rob) or ['https://www.tiqets.com/sitemap.xml']
viste, prod = set(), {}
while coda:
    u = coda.pop(0)
    if u in viste or len(viste) > 3000: continue
    viste.add(u)
    t = get(u)
    locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', t)
    if '<sitemapindex' in t:
        # solo sitemap che possono contenere pagine italiane o prodotti
        coda += [l for l in locs if not re.search(r'/(de|fr|es|nl|pt|ja|ko|zh|ru|pl|sv|da|cs|ca|el|tr)[-_/.]', l)]
        continue
    for l in locs:
        m = re.match(r'https://www\.tiqets\.com/it/([^/]+)/([^/]+)-p(\d+)/?$', l)
        if m: prod[m.group(3)] = [l, m.group(1), m.group(2), m.group(3)]
    time.sleep(0.3)
print('sitemap lette', len(viste), 'prodotti it', len(prod))
json.dump(sorted(prod.values(), key=lambda x: x[1]), open('sorgenti/tiqets/prodotti.json', 'w'), ensure_ascii=False, indent=0)
