#!/usr/bin/env python3
"""10/11/2026 sera: titolo esatto della voce di it.wikipedia per ogni luogo, da Wikidata (gratuito, CC0).
Per ogni comune (codice ISTAT, P635) prende gli elementi che stanno nel comune (P131) e hanno una voce su
it.wikipedia, poi abbina per nome: tutte le parole distintive del luogo devono comparire nel titolo della voce.
Scrive data/wiki.json {id luogo: titolo}. I luoghi senza abbinamento sicuro restano senza: la scheda mostra la ricerca."""
import json, re, sys, time, unicodedata, urllib.request, urllib.parse
G = '/home/claude/achs-places-guide/'
sys.path.insert(0, G); from leggi_dati import righe
m = json.load(open(G + 'manifest.json')); D = righe(json.load(open(G + m['dati'])))
STOP = set("della delle dello degli dei del di da la le il lo gli e ed con per tra fra sul sulla nel nella al alla ai alle in a d l un una".split())
GEN = set("chiesa museo civico civica parco area archeologica archeologico san santa santo sant santi basilica cattedrale duomo palazzo castello torre villa piazza centro storico borgo antico antica nazionale regionale comunale complesso monumentale santuario oratorio abbazia convento monastero pieve rocca fortezza teatro giardino giardini lago monte grotta grotte riserva naturale".split())
def norm(t): return "".join(ch for ch in unicodedata.normalize("NFD", t.lower()) if not unicodedata.combining(ch))
def parole(t): return [w for w in re.split(r"[^a-z0-9]+", norm(t)) if len(w) >= 2 and w not in STOP]
def slug(s):
    s = norm(s); return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
def sparql(q):
    for k in range(5):
        try:
            r = urllib.request.urlopen(urllib.request.Request('https://query.wikidata.org/sparql?format=json&query=' + urllib.parse.quote(q),
                headers={'User-Agent': 'AchsPlacesGuide/0.4 (https://achplaces.com)'}), timeout=120)
            return json.load(r)['results']['bindings']
        except Exception as e:
            print('  riprovo', e); time.sleep(5 * (k + 1))
    return []
com = [c for c in D['c'] if c.get('istat')]
voci = {}
for i in range(0, len(com), 40):
    v = ' '.join('"%s"' % str(c['istat']).zfill(6) for c in com[i:i + 40])
    q = '''SELECT ?ist ?t WHERE { VALUES ?ist { %s } ?c wdt:P635 ?ist. ?x wdt:P131/wdt:P131? ?c.
      ?a schema:about ?x; schema:isPartOf <https://it.wikipedia.org/>; schema:name ?t. }''' % v
    for b in sparql(q): voci.setdefault(b['ist']['value'], set()).add(b['t']['value'])
    print(i, len(voci), flush=True); time.sleep(1)
out = {}; amb = 0
for c in com:
    cand = voci.get(str(c['istat']).zfill(6), set()); cn = set(parole(c['name']))
    for a in c['places']:
        name = a[1]; pid = c['slug'] + '--' + (a[0] if a[0] else slug(name))
        base = re.split(r"[(,:«]", name)[0]
        pw = [w for w in parole(base) if w not in cn]
        dis = [w for w in pw if w not in GEN]
        if not dis: continue          # solo parole generiche («Chiesa di San Pietro»): troppo rischioso
        buoni = []
        for t in cand:
            tw = set(parole(re.sub(r"\s*\(.*\)$", "", t)))
            if all(w in tw for w in pw) and len(tw - set(pw) - cn) <= 2: buoni.append(t)
        if len(buoni) == 1: out[pid] = buoni[0]
        elif len(buoni) > 1:
            esatti = [t for t in buoni if norm(re.sub(r"\s*\(.*\)$", "", t)) == norm(base.strip())]
            if len(esatti) == 1: out[pid] = esatti[0]
            else: amb += 1
json.dump(out, open(G + 'data/wiki.json', 'w'), ensure_ascii=False, indent=0, sort_keys=True)
print('voci abbinate', len(out), 'ambigue', amb, 'luoghi', sum(len(c['places']) for c in com))
