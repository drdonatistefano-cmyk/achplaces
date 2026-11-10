"""10/11/2026 sera: controllo di tutti i link della guida (siti ufficiali, fonti, biglietterie, orari, partner).
Gira su GitHub Actions. Per ogni indirizzo: codice HTTP, indirizzo finale dopo i reindirizzamenti, errore.
Scrive out/link-<gruppo>.json {url: [codice, finale, errore]}. 0 = non raggiungibile."""
import json, os, sys, time, threading, collections
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import requests
G = int(sys.argv[1]) if len(sys.argv) > 1 else 0
QUI = os.path.dirname(os.path.abspath(__file__))
tutti = json.load(open(os.path.join(QUI, 'tutti.json')))
# (10/11 23:00, coordinamento) Ogni sito sta in UN solo lavoro. Prima i link erano divisi a caso
# (i % 5): i cinque lavori bussavano insieme agli stessi siti - 2.804 link su it.wikipedia.org,
# 1.949 su italia.it, 1.244 su cultura.gov.it - e un sito che rallenta o blocca avrebbe fatto
# risultare rotti centinaia di link buoni. Divisione stabile: siti dal piu' grande al piu' piccolo,
# ognuno al lavoro meno carico.
_per = collections.Counter(urlparse(u).hostname or '' for u in tutti)
_carico, _gruppo = [0] * 5, {}
for _h, _n in sorted(_per.items(), key=lambda x: (-x[1], x[0])):
    _g = _carico.index(min(_carico)); _gruppo[_h] = _g; _carico[_g] += _n
mie = [u for u in tutti if _gruppo[urlparse(u).hostname or ''] == G]
FO = f'out/link-{G}.json'; os.makedirs('out', exist_ok=True)
# (10/11 23:00, coordinamento) Il controllo e' settimanale: i risultati di una settimana
# precedente non valgono, altrimenti un link che si rompe dopo il primo giro non verrebbe mai
# visto. La settimana del file sta accanto, in link-<gruppo>.giro.
import datetime as _dt
_sett = '%d-W%02d' % _dt.date.today().isocalendar()[:2]
_FG = f'out/link-{G}.giro'
_vecchio = open(_FG).read().strip() if os.path.exists(_FG) else ''
fatto = json.load(open(FO)) if os.path.exists(FO) and _vecchio == _sett else {}
open(_FG, 'w').write(_sett)
H = {'User-Agent': 'Mozilla/5.0 (compatible; AchsPlacesGuide-linkcheck/1.0; +https://achplaces.com)', 'Accept': 'text/html,application/xhtml+xml,*/*;q=0.8', 'Accept-Language': 'it,en;q=0.5'}
blocchi = collections.defaultdict(threading.Lock)
def prova(u):
    host = urlparse(u).hostname or ''
    with blocchi[host]:
        for k in range(2):
            try:
                r = requests.get(u, headers=H, timeout=25, allow_redirects=True, stream=True)
                c = r.status_code; fin = r.url; r.close()
                if c in (429, 503) and k == 0: time.sleep(5); continue
                return u, [c, fin if fin != u else '', '']
            except Exception as e:
                err = type(e).__name__
                if k == 0: time.sleep(2); continue
                return u, [0, '', err]
            finally:
                time.sleep(0.3)
lav = [u for u in mie if u not in fatto]
print('gruppo', G, 'link', len(mie), 'da fare', len(lav), flush=True)
with ThreadPoolExecutor(16) as ex:
    for i, (u, v) in enumerate(ex.map(prova, lav)):
        fatto[u] = v
        if i % 500 == 0:
            json.dump(fatto, open(FO, 'w')); print(i, collections.Counter(x[0] // 100 for x in fatto.values()), flush=True)
json.dump(fatto, open(FO, 'w'), sort_keys=True)
print('fine', collections.Counter(x[0] for x in fatto.values()).most_common(12))
