"""Biglietti GetYourGuide abbinati a mano (18/11/2026): luoghi della guida che Tiqets vende ma che l'abbinamento automatico
(gyg_abbina.py, nei dati della guida) non trova, per nomi in inglese o diversi. Si mettono in /biglietti-partner.json
alla voce «gy»: la pagina li legge all'avvio, senza ricostruire la guida. Un luogo resta solo se il prodotto è ancora
nelle sitemap di GetYourGuide (sorgenti/gyg/prodotti.json, aggiornato il primo del mese) e se il luogo non è gratuito.
Solo biglietti d'ingresso: niente visite guidate, tour, trasferimenti o pacchetti."""
import json, os, re, sys, unicodedata
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); R = os.path.dirname(H)
sys.path.insert(0, H); from leggi_dati import righe
AGGIUNTE = {   # (comune, nome del luogo nella guida): parte dell'indirizzo del prodotto GetYourGuide (solo biglietti d'ingresso)
    ('Bolzano', 'Messner Mountain Museum Firmian'): 'bolzano-messner-mountain-museum-firmian-entry-ticket',
    ('Brunico', 'Castello di Brunico e Messner Mountain Museum Ripa'): 'brunico-messner-mountain-museum-ripa-entry-ticket',
    ('Calatafimi-Segesta', 'Parco archeologico di Segesta'): 'segesta-archaeological-site-shuttle-entry-ticket',
    ('Gradara', 'Rocca di Gradara'): 'gradara-entry-ticket-to-rocca',
    ('Stresa', 'Villa Pallavicino'): 'stresa-parco-pallavicino-entry-ticket',
    ('Vicenza', 'Palladio Museum'): 'vicenza-entry-ticket-to-palladio-museum',
    ('Urbino', 'Palazzo Ducale e Galleria Nazionale delle Marche'): 'urbino-galleria-nazionale-delle-marche-ticket',
    # 18/11/2026 22:20, terzo giro
    ('Modena', 'Collezione Maserati Umberto Panini'): 'modena-umberto-panini-maserati-collection-entrance-ticket',
    ('Rapolano Terme', 'Terme Antica Querciolaia e Terme San Giovanni'): 'rapolano-admission-ticket-to-the-san-giovanni-thermal-baths',
    ('Pisa', 'Battistero di San Giovanni'): 'pisa-entry-ticket-to-the-baptistery-of-san-giovanni',
    ('Pisa', "Museo dell'Opera del Duomo"): 'pisa-opera-del-duomo-museum-cathedral-ticket',
    ('Sorrento', 'Museo Correale di Terranova'): 'sorrento-admission-ticket-to-the-splendid-correale-museum',
    ('Bari', 'Castello Normanno-Svevo'): 'bari-norman-swabian-castle-entry-ticket',
    ('Mamoiada', 'Museo delle maschere mediterranee'): 'mamoiada-museum-of-mediterranean-masks-ticket',
}
def s40(s): return re.sub(r'[^a-z0-9]+', '-', ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower()).strip('-')[:40].rstrip('-')
P = json.load(open(os.path.join(H, 'gyg', 'prodotti.json')))
m = json.load(open(os.path.join(R, 'manifest.json'))); D = righe(json.load(open(os.path.join(R, m['dati']))))
TQ = {**json.load(open(os.path.join(H, 'data', 'tiqets.json'))), **json.load(open(os.path.join(H, 'data', 'gyg.json')))}
luoghi = {(c['name'], a[1]): (c['slug'] + '--' + (a[0] or s40(a[1])), a) for c in D['c'] for a in c['places']}
out = {}
for (com, nome), chiave in AGGIUNTE.items():
    if (com, nome) not in luoghi: print('luogo non trovato:', com, nome); continue
    pid, a = luoghi[(com, nome)]
    if pid in TQ: print('ha già Tiqets o GetYourGuide:', pid); continue
    if 'F' in (a[5] or ''): print('gratuito, niente bottone:', pid); continue
    u = [x[0] for x in P if chiave in x[3]]
    if not u: print('prodotto non più in vendita:', com, nome); continue
    out[pid] = sorted(u, key=len)[0]
f = os.path.join(R, 'biglietti-partner.json')
B = json.load(open(f)) if os.path.exists(f) else {}
B['gy'] = out
json.dump(B, open(f, 'w'), ensure_ascii=False, separators=(',', ':'))
print('GetYourGuide abbinati a mano:', len(out))
