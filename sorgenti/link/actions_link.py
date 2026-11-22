"""10/11/2026 sera: controllo di tutti i link della guida (siti ufficiali, fonti, biglietterie, orari, partner).
Gira su GitHub Actions. Per ogni indirizzo: codice HTTP, indirizzo finale dopo i reindirizzamenti, errore.
Scrive out/link-<gruppo>.json {url: [codice, finale, errore]}. 0 = non raggiungibile."""
import json, os, sys, time, threading, collections
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urlparse
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
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

import subprocess as _sp
_ULT = [time.time()]
def salva_ramo(fo, msg, forza=False):
    """10/11 notte: salva sul ramo foto ogni 15 minuti, cosi' se il lavoro scade non si perde nulla."""
    if not forza and time.time() - _ULT[0] < 900: return
    _ULT[0] = time.time()
    sh = lambda *a: _sp.run(['git', '-C', 'out'] + list(a), capture_output=True, text=True)
    sh('add', os.path.basename(fo)); sh('commit', '-q', '-m', msg)
    for k in range(5):
        sh('pull', '--rebase', '-q', 'origin', 'foto')
        if sh('push', '-q', 'origin', 'HEAD:foto').returncode == 0: return
        time.sleep(5 + 5 * k)
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
# (11/11, coordinamento) Un sito che non si lascia raggiungere da GitHub non va interrogato link
# per link. L'11/11 cultura.gov.it ha risposto «ConnectTimeout» a 353 link su 377: ogni link
# costava due attese da 25 secondi, uno dopo l'altro, e il lavoro e' arrivato al tempo massimo
# dopo 5 ore e mezza. Dopo 4 errori di collegamento di fila lo stesso sito si lascia stare per il
# resto del giro, e i suoi link restano segnati «SitoNonRaggiungibile».
#
# COME LEGGERE IL RISULTATO [codice, indirizzo finale, errore]:
#   codice 404 o 410          -> link rotto davvero
#   codice 200-399            -> funziona
#   codice 0                  -> NON VERIFICATO da GitHub, non «rotto»: siti che bloccano i server
#                                (cultura.gov.it, letsmarche.it, parchi siciliani), certificati che
#                                Python non accetta ma i browser si' (SSLError). Per una persona
#                                col browser quasi sempre funzionano: non vanno tolti dalla guida.
ERR_SITO = ('ConnectTimeout', 'ConnectionError', 'SSLError')
falliti_di_fila = collections.Counter()
bloccati = set()
def prova(u):
    host = urlparse(u).hostname or ''
    with blocchi[host]:
        if host in bloccati:
            return u, [0, '', 'SitoNonRaggiungibile']
        for k in range(2):
            try:
                r = requests.get(u, headers=H, timeout=15, allow_redirects=True, stream=True)
                c = r.status_code; fin = r.url; r.close()
                falliti_di_fila[host] = 0          # il sito risponde, anche se con un errore
                if c in (429, 503) and k == 0: time.sleep(5); continue
                return u, [c, fin if fin != u else '', '']
            except Exception as e:
                err = type(e).__name__
                if err == 'SSLError':
                    # (11/11) Certificato che Python rifiuta ma i browser di solito accettano: quasi
                    # sempre manca un certificato intermedio, che i browser vanno a prendere da soli.
                    # Si riprova senza verifica solo per leggere se la pagina esiste: non si invia
                    # niente e il contenuto non si usa. Il risultato tiene scritto «SSLError», cosi'
                    # chi lo legge sa che il certificato del sito va guardato.
                    try:
                        r = requests.get(u, headers=H, timeout=15, allow_redirects=True, stream=True, verify=False)
                        c = r.status_code; fin = r.url; r.close()
                        falliti_di_fila[host] = 0
                        return u, [c, fin if fin != u else '', 'SSLError']
                    except Exception as e2:
                        err = type(e2).__name__
                if k == 0 and err != 'SSLError': time.sleep(2); continue
                if err in ERR_SITO:
                    falliti_di_fila[host] += 1
                    if falliti_di_fila[host] >= 4:
                        bloccati.add(host)
                        print('sito non raggiungibile da GitHub, lo lascio stare:', host, flush=True)
                return u, [0, '', err]
            finally:
                time.sleep(0.3)
lav = [u for u in mie if u not in fatto]
print('gruppo', G, 'link', len(mie), 'da fare', len(lav), flush=True)
with ThreadPoolExecutor(16) as ex:
    for i, (u, v) in enumerate(ex.map(prova, lav)):
        fatto[u] = v
        if i % 100 == 0:
            json.dump(fatto, open(FO, 'w')); salva_ramo(FO, f'Link, gruppo {G}: {len(fatto)}')
        if i % 500 == 0:
            json.dump(fatto, open(FO, 'w')); print(i, collections.Counter(x[0] // 100 for x in fatto.values()), flush=True)
json.dump(fatto, open(FO, 'w'), sort_keys=True)

# (11/11, coordinamento) Seconda passata dalla rete di Cloudflare. Molti siti pubblici italiani
# chiudono la porta ai server di GitHub (Microsoft Azure) ma rispondono da altre reti: i link
# rimasti a 0 per un problema di collegamento si mandano al Worker di sorgenti/link/worker.js,
# 15 alla volta. Se il Worker trova la pagina, il risultato diventa [codice, finale, "cf"]; se
# non la trova nemmeno lui, resta 0 con scritto anche il suo errore. Senza indirizzo in
# worker.json il passo si salta.
DA_CF = ('ConnectTimeout', 'ConnectionError', 'ReadTimeout', 'SitoNonRaggiungibile')
try:
    WORKER = (os.environ.get('LINK_WORKER') or
              json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'worker.json'))).get('url') or '').strip()
except Exception:
    WORKER = ''
if WORKER:
    rip = [u for u in mie if fatto.get(u, [1])[0] == 0 and str(fatto[u][2]).split('+')[0] in DA_CF
           and (urlparse(u).hostname or '').endswith('.it')]
    print('seconda passata da Cloudflare:', len(rip), 'link', flush=True)
    presi = 0
    # 10 alla volta, non 15: nel piano gratuito un Worker fa al massimo 50 richieste per volta e
    # ogni rimando (http -> https, -> www) ne conta una; 10 link con tre rimandi restano sotto.
    for i in range(0, len(rip), 10):
        pezzo = rip[i:i + 10]
        try:
            r = requests.post(WORKER, json={'u': pezzo}, timeout=120, headers={'User-Agent': H['User-Agent']})
            esiti = r.json() if r.status_code == 200 else {}
        except Exception as e:
            print('Worker non raggiungibile:', type(e).__name__, flush=True)
            break
        for u in pezzo:
            v = esiti.get(u)
            if isinstance(v, list) and len(v) == 3:
                # 520-530 sono errori fra Cloudflare e il sito (certificato, DNS), non la
                # risposta del sito: il link resta NON VERIFICATO, mai rotto.
                if v[0] and not 520 <= v[0] <= 530:
                    fatto[u] = v; presi += 1
                elif v[0]:
                    fatto[u] = [0, '', f"{fatto[u][2]}+cf{v[0]}"]
                else:
                    fatto[u] = [0, '', f"{fatto[u][2]}+{v[2]}"]
        if i % 150 == 0:
            json.dump(fatto, open(FO, 'w'), sort_keys=True); salva_ramo(FO, f'Link, gruppo {G}: Cloudflare {i + len(pezzo)}')
        time.sleep(1)
    print('raggiunti da Cloudflare:', presi, 'su', len(rip), flush=True)
    json.dump(fatto, open(FO, 'w'), sort_keys=True)

print('fine', collections.Counter(x[0] for x in fatto.values()).most_common(12))
