"""Eseguito da GitHub Actions (flusso «Catalogo TicketOne da Awin»): scarica dal tuo account Awin l'elenco dei cataloghi
e il catalogo di TicketOne IT (inserzionista 9567) e salva una versione leggera in partner/ticketone.json (ramo «partner»).
La chiave dei cataloghi sta nel segreto AWIN_FEED_KEY del repository: non va mai scritta nei file.
Uscita: {"aggiornato": ..., "colonne": [...], "prodotti": [{colonna: valore, ...}, ...]} senza le descrizioni lunghe."""
import csv, gzip, io, json, os, sys, time, datetime
import requests
PUB = os.environ.get('AWIN_PUBLISHER', '3146807')
KEY = os.environ.get('AWIN_FEED_KEY', '').strip()
INSERZIONISTI = {'9567': 'ticketone'}          # si aggiungono qui altri partner con catalogo (ID inserzionista Awin)
OUT = sys.argv[1] if len(sys.argv) > 1 else 'partner'
if not KEY: sys.exit('manca il segreto AWIN_FEED_KEY')
def get(u):
    for k in range(4):
        try:
            r = requests.get(u, timeout=180)
            if r.status_code == 200:
                b = r.content
                if b[:2] == b'\x1f\x8b': b = gzip.decompress(b)
                return b.decode('utf-8-sig', 'replace')
            print('HTTP', r.status_code)
        except Exception as e: print('errore', type(e).__name__)
        time.sleep(10 * (k + 1))
    return ''
elenco = get(f'https://ui.awin.com/productdata-darwin-download/publisher/{PUB}/{KEY}/1/feedList')
righe = list(csv.DictReader(io.StringIO(elenco)))
print('cataloghi nell\'elenco:', len(righe))
os.makedirs(OUT, exist_ok=True)
for adv, nome in INSERZIONISTI.items():
    feed = [r for r in righe if r.get('Advertiser ID') == adv and r.get('Membership Status', '').lower() == 'active']
    if not feed: print(nome, ': nessun catalogo attivo'); continue
    f = max(feed, key=lambda r: int(r.get('No of products') or 0))
    print(nome, ': catalogo', f.get('Feed ID'), f.get('Feed Name'), f.get('No of products'), 'prodotti, importato', f.get('Last Imported'))
    testo = get(f['URL'])
    rr = list(csv.DictReader(io.StringIO(testo)))
    if not rr: print(nome, ': catalogo vuoto'); continue
    col = [c for c in rr[0].keys() if c and 'description' not in c.lower()]
    print('colonne:', col)
    prodotti = [{c: r[c] for c in col if r.get(c)} for r in rr]
    json.dump({'aggiornato': datetime.date.today().isoformat(), 'feed': f.get('Feed ID'), 'colonne': col, 'prodotti': prodotti},
              open(os.path.join(OUT, nome + '.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(nome, ':', len(prodotti), 'prodotti salvati')
