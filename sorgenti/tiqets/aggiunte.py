"""Biglietti Tiqets abbinati a mano (18/11/2026): luoghi della guida che Tiqets vende ma che l'abbinamento automatico
(tiqets_abbina.py, nei dati della guida) non trova, per nomi in inglese o diversi. Si mettono in /biglietti-partner.json
alla voce «tq»: la pagina li legge all'avvio, senza ricostruire la guida. Un luogo resta solo se il prodotto è ancora
nelle sitemap di Tiqets (sorgenti/tiqets/prodotti.json, aggiornato il primo del mese) e se il luogo non è gratuito.
Solo biglietti d'ingresso: niente visite guidate, tour, trasferimenti o pacchetti."""
import json, os, re, sys, unicodedata
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.dirname(H)
sys.path.insert(0, H); from leggi_dati import righe
AGGIUNTE = {   # (comune, nome del luogo nella guida): parte dell'indirizzo del prodotto Tiqets
    ('Anagni', 'Palazzo di Bonifacio VIII'): 'bonifacio-viii-palace-in-anagni-entry-ticket',
    ('Anagni', 'Museo della Cattedrale'): 'museo-della-cattedrale-di-anagni-muca-biglietto-d-ingresso',
    ('Arezzo', "Mudas - Museo Diocesano d'Arte Sacra"): 'cattedrale-di-arezzo-e-museo-diocesano-di-arte-sacra-biglietto-d-ingresso',
    ('Avio', "Castello di Sabbionara d'Avio (FAI)"): 'castello-di-avio-biglietto-d-ingresso',
    ('Castel Gandolfo', 'Palazzo Apostolico e Ville Pontificie'): 'palazzo-papale-e-giardini-di-castel-gandolfo',
    ('Firenze', "Campanile di Giotto, Battistero e Museo dell'Opera del Duomo"): 'campanile-di-giotto-duomo-e-museo-di-firenze-biglietto-d-ingresso',
    ('Firenze', 'Palazzo Pitti'): 'palazzo-pitti-e-giardino-di-boboli-ingresso-riservato-audioguida',
    ('Firenze', 'Giardino di Boboli'): 'palazzo-pitti-e-giardino-di-boboli-ingresso-riservato-audioguida',
    ('Firenze', 'Museo di Palazzo Vecchio'): 'palazzo-vecchio-e-museo-biglietto-d-ingresso',
    ('Firenze', 'Galleria degli Uffizi'): 'galleria-degli-uffizi-ingresso-riservato-audioguida',
    ('Genova', 'Acquario di Genova e Biosfera'): 'acquario-di-genova-e-citta-dei-bambini-e-dei-ragazzi-biglietto-d-ingresso',
    ('Maranello', 'Museo Ferrari'): 'museo-ferrari-maranello-biglietto-d-ingresso',
    ('Milano', 'Duomo di Milano e Terrazze'): 'duomo-di-milano-biglietto-d-ingresso-accesso-al-tetto',
    ('Milano', 'Museo Nazionale della Scienza e della Tecnologia Leonardo da Vinci'): 'museo-nazionale-della-scienza-e-della-tecnologia-leonardo-da-vinci',
    ('Montalcino', 'Museo della Comunità di Montalcino e del Brunello'): 'museo-del-brunello-di-montalcino-biglietto-d-ingresso',
    ('Napoli', 'Basilica di San Lorenzo Maggiore'): 'complesso-di-san-lorenzo-maggiore-e-area-archeologica',
    ('Napoli', 'Museo Archeologico Nazionale (MANN)'): 'museo-archeologico-nazionale-di-napoli-biglietto-d-ingresso',
    ('Napoli', 'Museo Cappella Sansevero'): 'cappella-sansevero-biglietto-dingresso',
    ('Pisa', 'Cattedrale di Santa Maria Assunta'): 'cattedrale-di-pisa-e-cimitero-monumentale-ingresso-riservato',
    ('Roma', 'Gallerie Nazionali di Arte Antica: Palazzo Barberini e Palazzo Corsini'): 'palazzo-barberini-e-galleria-corsini-biglietto-d-ingresso',
    ('Roma', "Castel Sant'Angelo"): 'castel-sant-angelo-biglietto-d-ingresso-app-di-audioguida',
    ('Roma', 'Foro Romano e Palatino'): 'colle-palatino-e-foro-romano-biglietto-d-ingresso',
    ('Roma', 'Museo di Roma a Palazzo Braschi'): 'museo-di-roma-ingresso-riservato',
    ('Roma', 'Parco Archeologico di Ostia Antica'): 'ostia-antica-ingresso-salta-coda-audioguida',
    ('Trieste', 'Castello e Parco di Miramare'): 'castello-e-parco-di-miramare-biglietto-d-ingresso',
    ('Montefiascone', 'Rocca dei Papi e giardino'): 'montefiascone-rocca-dei-papi-skip-the-line-entry-tickets',
    ('Pompei', 'Area archeologica di Pompei'): 'pompei-biglietto-d-ingresso-non-serve-prenotare',
    ("Sant'Agata Bolognese", 'MUDETEC, Museo Lamborghini'): 'museo-automobili-lamborghini-biglietto-d-ingresso',
    ('Assisi', 'Rocca Maggiore'): 'pinacoteca-roman-forum-rocca-maggiore',          # biglietto unico Pinacoteca, Foro romano e Rocca
    ('Giardini-Naxos', 'Area archeologica di Naxos'): 'museo-e-parco-archeologico-di-naxos',
    ('Venezia', 'Museo Fortuny'): 'palazzo-fortuny-biglietto-d-ingresso',
    ('Venezia', 'Basilica di San Marco'): 'basilica-di-san-marco-biglietto-d-ingresso',
}
def s40(s): return re.sub(r'[^a-z0-9]+', '-', ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower()).strip('-')[:40].rstrip('-')
P = json.load(open(os.path.join(H, 'tiqets', 'prodotti.json')))
m = json.load(open(os.path.join(R, 'manifest.json'))); D = righe(json.load(open(os.path.join(R, m['dati']))))
TQ = json.load(open(os.path.join(H, 'data', 'tiqets.json')))
luoghi = {(c['name'], a[1]): (c['slug'] + '--' + (a[0] or s40(a[1])), a) for c in D['c'] for a in c['places']}
out = {}
for (com, nome), chiave in AGGIUNTE.items():
    if (com, nome) not in luoghi: print('luogo non trovato:', com, nome); continue
    pid, a = luoghi[(com, nome)]
    if pid in TQ: print('ha già Tiqets:', pid); continue
    if 'F' in (a[5] or ''): print('gratuito, niente bottone:', pid); continue
    u = [x[0] for x in P if chiave in x[2] and re.search(r'/it/', x[0])]
    if not u: print('prodotto non più in vendita:', com, nome); continue
    out[pid] = sorted(u, key=len)[0]
f = os.path.join(R, 'biglietti-partner.json')
B = json.load(open(f)) if os.path.exists(f) else {}
B['tq'] = out
json.dump(B, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
print('Tiqets abbinati a mano:', len(out))
