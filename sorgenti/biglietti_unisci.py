#!/usr/bin/env python3
"""10/11/2026 notte: tiene solo i link di biglietteria e le frasi di ingresso gratuito sicuri, dai risultati del lavoro
GitHub biglietti-<g>.json. Scrive data/biglietti.json {id: {"tk": url, "da": pagina} | {"free": frase, "da": pagina}}."""
import json, re, glob, subprocess
from urllib.parse import urlparse
G = '/home/claude/achs-places-guide/'
FORTE = re.compile(r'bigliett|ticket|tariff|prezz|orari-e-|entry|admission|ingress')
NO = re.compile(r'appuntament|alloggi|accommodation|dove-dormire|search-book|shopping|bookshop|catalogo|carrello|cart|privacy|faq|domande|workshop|education|didattic|scuol|/book$|/book/|newsletter|disservizio|audizion|\.jpe?g|\.png|eventbrite\.it/e/|eventbrite\.it/o/|aggiornamento|card\b|verona-card|cumulativo|abbonament|gift|regal', re.I)
PORTALI = ('italia.it', 'visittrentino', 'letsmarche', 'visitverona', 'visittuscany', 'emiliaromagnaturismo', 'sardegnaturismo', 'visitlazio', 'in-lombardia', 'visitsicily', 'umbriatourism', 'borghipiubelliditalia', 'touringclub', 'gardatrentino', 'fondoambiente', 'turismo', 'cultura.gov.it', 'welcome', 'parchilazio')
BIGL = ('vivaticket', 'ticketone', 'coopculture', 'midaticket', 'ticketlandia', 'musement', 'eventbrite', 'clappit', 'boxol', 'liveticket', 'ticketsms', 'diyticket', 'b-ticket', 'charta', 'museiitaliani', 'ticketmaster', 'tiqets', 'getyourguide', 'ticket.')
FREE_OK = re.compile(r'Ingresso\s+(Ingresso\s+)?(libero|gratuito)\b|Modalit. di accesso\s+Libera\b|(access|entrance|admission)[^.]{0,40}is free of charge|ingresso (è |e\' )?(libero|gratuito)[.,;]', re.I)
FREE_NO = re.compile(r'under|bambin|minori|prima domenica|domenica del mese|FAI|iscritti|eventi|scuol|ridott|solo ad|4 novembre|giornat|contributo|€|euro', re.I)
def ok_tk(v):
    u = v['tk']; h = urlparse(u).hostname or ''; t = (v.get('t') or '').lower(); path = urlparse(u).path.lower() + '?' + (urlparse(u).query or '').lower()
    if NO.search(t + ' ' + path): return False
    if any(b in h for b in BIGL): return True
    if any(p in h for p in PORTALI): return bool(re.search(r'ticket|bigliett', path)) and 'experiences' in path and False
    if re.match(r'(www\.)?comune\.', h) or '.comune.' in h: return bool(re.search(r'bigliett|tariff|ticket', path))
    return bool(FORTE.search(t + ' ' + path))
def ok_free(v):
    f = v['free']; m = FREE_OK.search(f)
    if not m: return False
    vicino = f[max(0, m.start() - 60): m.end() + 60]
    return not FREE_NO.search(vicino)
D = {}
for f in sorted(glob.glob('/home/claude/foto-ramo/biglietti-*.json')): D.update(json.load(open(f)))
out = {}; stat = {'tk': 0, 'tk_no': 0, 'free': 0, 'free_no': 0}
for k, v in D.items():
    if 'tk' in v:
        if ok_tk(v): out[k] = {'tk': v['tk'], 'da': v['da']}; stat['tk'] += 1
        else: stat['tk_no'] += 1
    elif 'free' in v:
        if ok_free(v): out[k] = {'free': v['free'][:200], 'da': v['da']}; stat['free'] += 1
        else: stat['free_no'] += 1
json.dump(out, open(G + 'data/biglietti.json', 'w'), ensure_ascii=False, indent=0, sort_keys=True)
print('letti', len(D), stat)
