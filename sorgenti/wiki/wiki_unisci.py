#!/usr/bin/env python3
"""10/11/2026 sera: unisce le voci di Wikipedia (Wikidata + lavoro GitHub wiki-<g>.json) e scarta gli abbinamenti dubbi:
1) se il nome del luogo comincia con un tipo (museo, chiesa, giardino...) il titolo deve contenere lo stesso tipo o un sinonimo;
2) il titolo non deve nominare un altro comune italiano (fra parentesi o dopo «di») diverso da quello del luogo."""
import json, re, glob, csv, unicodedata
G = '/home/claude/achs-places-guide/'
def norm(t): return "".join(ch for ch in unicodedata.normalize("NFD", (t or '').lower()) if not unicodedata.combining(ch))
TIPI = {
 'museo': 'museo musei antiquarium pinacoteca galleria collezione raccolta casa',
 'pinacoteca': 'pinacoteca museo galleria', 'galleria': 'galleria museo pinacoteca',
 'chiesa': 'chiesa duomo cattedrale concattedrale basilica collegiata pieve santuario oratorio abbazia parrocchiale cappella',
 'duomo': 'duomo cattedrale concattedrale chiesa basilica collegiata', 'cattedrale': 'cattedrale duomo concattedrale basilica chiesa',
 'basilica': 'basilica chiesa duomo cattedrale santuario collegiata', 'santuario': 'santuario chiesa basilica',
 'castello': 'castello castel rocca fortezza forte', 'rocca': 'rocca castello fortezza', 'torre': 'torre torrione campanile',
 'palazzo': 'palazzo palazzina reggia', 'villa': 'villa', 'via': 'via', 'corso': 'corso', 'giardino': 'giardino giardini orto parco', 'orto': 'orto giardino',
 'lago': 'lago laghi', 'grotta': 'grotta grotte', 'grotte': 'grotte grotta', 'teatro': 'teatro anfiteatro', 'ponte': 'ponte',
 'abbazia': 'abbazia monastero convento badia', 'convento': 'convento monastero abbazia', 'monastero': 'monastero convento abbazia certosa',
 'parco': 'parco riserva giardino', 'riserva': 'riserva parco oasi', 'area': 'area parco sito', 'piazza': 'piazza', 'fontana': 'fontana',
 'biblioteca': 'biblioteca', 'cascata': 'cascata cascate', 'cascate': 'cascate cascata', 'forte': 'forte fortezza castello',
}
STRETTI = set('museo pinacoteca galleria chiesa duomo cattedrale basilica santuario abbazia convento monastero castello rocca'.split())
COM = {}
for r in csv.DictReader(open(G + 'data/geo/comuni_istat.csv', encoding='utf-8')):
    n = norm(r.get('comune') or r.get('Comune') or r.get('nome') or list(r.values())[1])
    if len(n) > 4: COM[n] = 1
def ok(pid, n, com, tit):
    t = norm(tit); w0 = re.split(r'[^a-z]+', re.sub(r'^(ex|antic[oa]|nuov[oa]) ', '', norm(n).strip()))[0] if n else ''
    # una persona con il nome del comune («Ciriaco d'Ancona», «Settimio di Jesi») non e' la chiesa a lei dedicata
    if w0 in ('chiesa', 'duomo', 'cattedrale', 'basilica', 'santuario', 'pieve', 'collegiata', 'abbazia', 'oratorio') and re.fullmatch(r"[a-z]+ (di|da|d') ?" + re.escape(norm(com)), t) and t.split()[0] not in TIPI['chiesa'].split(): return False
    # due tipi diversi in testa («Palazzo Merulana» -> «Via Merulana», «Villa Feltrinelli» -> «Palazzo Feltrinelli»)
    t0 = re.split(r'[^a-z]+', t.strip())[0]
    if w0 in TIPI and t0 in TIPI and t0 != w0 and t0 not in TIPI[w0].split(): return False
    if w0 in ('parco', 'cascata', 'cascate', 'lago', 'monte', 'grotta', 'grotte') and t0 in ('villa', 'palazzo', 'chiesa', 'castello'): return False
    if w0 in STRETTI and not any(re.search(r'\b' + s, t) for s in TIPI[w0].split()): return False
    cn = norm(com); nn = norm(n)
    for x in re.findall(r'\(([^)]+)\)', t):
        x = x.strip()
        if x in COM and x != cn and cn not in x and x not in nn: return False
    m2 = re.search(r'\b(?:di|del|della|d\') ?([a-z\' ]+)$', t)
    if m2:
        x = m2.group(1).strip()
        if x in COM and x != cn and x not in nn:
            return False
    return True
import sys; sys.path.insert(0, G); from leggi_dati import righe
m = json.load(open(G + 'manifest.json')); D = righe(json.load(open(G + m['dati'])))
def slug(s): return re.sub(r'[^a-z0-9]+', '-', norm(s)).strip('-')[:40].rstrip('-')
INFO = {}
for c in D['c']:
    for a in c['places']: INFO[c['slug'] + '--' + (a[0] if a[0] else slug(a[1]))] = (a[1], c['name'])
out = {}; scarti = []
fonti = [G + 'sorgenti_wiki_wd.json'] if False else []
src = json.load(open('/home/claude/achplaces/sorgenti/wiki/wiki-wd.json'))
for f in sorted(glob.glob('/home/claude/foto-ramo/wiki-*.json')):
    for k, v in json.load(open(f)).items(): src.setdefault(k, v)
for k, v in src.items():
    if k not in INFO: continue
    n, com = INFO[k]
    if ok(k, n, com, v): out[k] = v
    else: scarti.append((k, v))
json.dump(out, open(G + 'data/wiki.json', 'w'), ensure_ascii=False, indent=0, sort_keys=True)
json.dump(scarti, open('/tmp/wiki_scarti.json', 'w'), ensure_ascii=False, indent=0)
print('voci tenute', len(out), 'scartate', len(scarti))
