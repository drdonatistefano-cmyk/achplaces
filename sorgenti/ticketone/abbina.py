"""Abbina i luoghi della guida ai biglietti TicketOne del catalogo Awin (ramo «partner», ticketone.json).
L'abbinamento è a mano, luogo per luogo (MAPPA), perché nel catalogo i musei sono pochi e i nomi non sempre coincidono.
Per ogni luogo si prende il prodotto con la data più lontana: il link (già con l'affiliazione Awin) resta valido più a lungo.
Uso: python3 sorgenti/ticketone/abbina.py <ticketone.json>  →  scrive sorgenti/data/ticketone.json e, nella radice del sito,
biglietti-partner.json {id_luogo: url}: la pagina lo legge all'avvio, così i link si aggiornano senza ricostruire la guida."""
import json, os, sys, datetime
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAPPA = {   # id del luogo nella guida : nome del prodotto nel catalogo TicketOne (controllati il 18/11/2026)
    'roma-rm--galleria-nazionale-d-arte-moderna-e-cont': "Galleria Nazionale d'Arte Moderna e Contemporanea - GNAMC",
    'caserta-ce--reggia-di-caserta-palazzo-reale': 'Reggia di Caserta - Appartamenti Reali',
    'alberobello-ba--museo-del-territorio-casa-pezzolla': 'Museo del Territorio CASA PEZZOLLA',
    'castellana-grotte-ba--grotte-di-castellana': 'Grotte di Castellana - Visita Completa - ITALIANO',
    'siracusa-sr--museo-archeologico-regionale-paolo-orsi': 'Museo Archeologico Regionale Paolo Orsi',
    'siracusa-sr--teatro-greco': 'Parco Archeologico della Neapolis',      # il Teatro Greco si visita con il biglietto del parco
    'noto-sr--villa-romana-del-tellaro': 'Villa Romana del Tellaro',
    'terni-tr--cascata-delle-marmore': 'Cascata delle Marmore',
    'ariccia-rm--palazzo-chigi': 'Palazzo Chigi di Ariccia',
}
P = json.load(open(sys.argv[1]))['prodotti']
oggi = datetime.date.today().isoformat()
out = {}
for pid, nome in MAPPA.items():
    xs = [p for p in P if p.get('product_name') == nome and p.get('aw_deep_link') and (p.get('valid_to') or p.get('Tickets:event_date', '')[:10]) >= oggi]
    if not xs: print('nessun biglietto in vendita:', pid); continue
    x = max(xs, key=lambda p: p.get('Tickets:event_date', ''))
    out[pid] = x['aw_deep_link']
    print(f"{pid}: {len(xs)} date, ultima {x.get('Tickets:event_date','')[:10]}, da {x.get('search_price')} €")
json.dump(out, open(os.path.join(H, 'data', 'ticketone.json'), 'w'), ensure_ascii=False, indent=0)
json.dump({'t1': out}, open(os.path.join(os.path.dirname(H), 'biglietti-partner.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
print('TicketOne: luoghi abbinati', len(out))
