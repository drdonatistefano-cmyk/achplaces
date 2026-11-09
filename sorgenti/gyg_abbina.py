"""Abbina i luoghi della guida alle attività GetYourGuide (sorgenti/gyg/prodotti.json, dalle sitemap pubbliche del sito italiano).
Regola: l'attività deve riguardare proprio quel luogo (tutte le parole distintive del nome nel titolo, stessa città GetYourGuide).
Biglietti d'ingresso e visite guidate valgono; cene, trasferimenti, noleggi, pacchetti di più città no.
Preferenza: biglietto/ingresso prima delle visite. Scrive data/gyg.json {id_luogo: url} e data/gyg-candidati.txt."""
import json, re, sys, unicodedata, subprocess, os
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from leggi_dati import righe
n = lambda s: re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))).strip()
P = json.load(open('/home/claude/achplaces/sorgenti/gyg/prodotti.json'))
ALIAS = {'rome': 'roma', 'florence': 'firenze', 'venice': 'venezia', 'naples': 'napoli', 'milan': 'milano', 'turin': 'torino', 'genoa': 'genova', 'padua': 'padova', 'syracuse': 'siracusa', 'mantua': 'mantova', 'pompeii': 'pompei', 'vatican city': 'roma', 'herculaneum': 'ercolano', 'paestum': 'capaccio paestum'}
# parole inglesi dei titoli GetYourGuide tradotte in italiano prima del confronto
EN = {'museum': 'museo', 'museums': 'musei', 'palace': 'palazzo', 'castle': 'castello', 'church': 'chiesa', 'cathedral': 'cattedrale', 'tower': 'torre', 'square': 'piazza', 'theater': 'teatro', 'theatre': 'teatro', 'bridge': 'ponte', 'gate': 'porta', 'abbey': 'abbazia', 'gallery': 'galleria', 'garden': 'giardino', 'gardens': 'giardini', 'baths': 'terme', 'aquarium': 'acquario', 'cave': 'grotta', 'caves': 'grotte', 'grotto': 'grotta', 'catacombs': 'catacombe', 'amphitheater': 'anfiteatro', 'amphitheatre': 'anfiteatro', 'chapel': 'cappella', 'synagogue': 'sinagoga', 'park': 'parco', 'cloister': 'chiostro', 'dome': 'cupola', 'royal': 'reale', 'national': 'nazionale', 'archaeological': 'archeologico', 'ruins': 'scavi', 'excavations': 'scavi', 'ticket': 'biglietto', 'tickets': 'biglietti', 'entry': 'ingresso', 'entrance': 'ingresso', 'admission': 'ingresso', 'skip': 'salta', 'colosseum': 'colosseo', 'vatican': 'vaticani', 'pompeii': 'pompei', 'herculaneum': 'ercolano', 'last': 'ultima', 'supper': 'cena', 'leaning': 'pendente', 'island': 'isola', 'lake': 'lago', 'mount': 'monte', 'volcano': 'vulcano'}
STOP = set('di del della dei delle degli e la il lo le i gli d l a al alla allo ai agli in con sul sulla da dal dalla per un una uno'.split())
GEN = set('chiesa museo palazzo castello torre piazza basilica cattedrale duomo civico civica centro storico parco rocca teatro villa ponte porta mura abbazia convento galleria nazionale area archeologica archeologico sito complesso monumentale santuario giardino giardini scavi parco'.split())
NO = set('trasferimento trasferimenti transfer dinner lunch cooking class wine tasting food pizza pasta gelato spa rental rent golf cart photoshoot photo shooting airport train hop concert opera exhibition christmas cruise quad atv kayak kayaking snorkelling canoe canyoning dinghy snorkeling snorkel swimming swim transfert minibus bus jeep buggy ebike bike segway horse wine beach club factories factory ferrari lamborghini pagani sailing yacht catamaran rafting zipline paragliding vespa fiat tuk degustazione degustazioni tasting food dinner lunch cooking cucina voucher spa noleggio golf cart app servizio fotografico photoshoot shooting pass card hop treno aeroporto crociera udienza concerto concert opera arie mostra exhibition natale'.split())
ACQUA = set('boat barca motorboat speedboat'.split())
BIG = set('biglietto biglietti ingresso salta fila ticket tickets'.split())
WEAK = set('museo musei romano romana antico antica vecchio nuovo nuova grande san santa santo maggiore'.split())
TIPI = set('chiesa museo musei palazzo castello torre piazza basilica cattedrale duomo teatro villa ponte porta abbazia galleria giardino giardini terme acquario grotte grotta catacombe anfiteatro chiostro campanile cupola cappella sinagoga parco'.split())
ESCLUSI = set()
def citta(slug):
    c = slug.replace('-', ' ')
    return ALIAS.get(c, c)
perc = {}
for u, cs, lid, ps, i in P:
    c = citta(cs)
    if c: perc.setdefault(c, []).append((ps, u))
m = json.load(open(os.path.join(H, 'manifest.json'))); D = righe(json.load(open(os.path.join(H, m['dati']))))
def s40(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower(); return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
LU = [(c['slug'] + '--' + (a[0] if a[0] else s40(a[1])), a[1], c['name']) for c in D['c'] for a in c['places']]
bo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs');eval(fs.readFileSync('" + H + "/data/places-bologna.js','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES.map(p=>[p.id,p.name])))"]))
LU += [(i, nm, 'Bologna') for i, nm in bo]
def varianti(nome):
    v = [re.sub(r'\s*\([^)]*\)', '', nome)] + [x for x in re.findall(r'\(([^)]+)\)', nome) if n(x) not in ('unesco', 'sito unesco')]
    v += [re.split(r'\s+e\s+|,|\s+[–-]\s+|:', v[0])[0]]
    return [x for x in dict.fromkeys(x.strip() for x in v) if len(x) > 3]
def ha(w, toks, testo): return w in toks or (len(w) > 5 and any(x[:6] == w[:6] for x in toks))
out, cand = {}, []
for pid, nome, com in LU:
    prods = perc.get(n(com))
    if not prods: continue
    if (com, nome) in ESCLUSI: continue
    cw = set(n(com).split()); best = None
    tipo = [w for w in n(re.sub(r'\s*\([^)]*\)', '', nome)).split() if w in TIPI][:1]   # il tipo di luogo (piazza, ponte, museo…) deve esserci anche nel prodotto
    for v in varianti(nome):
        d = [w for w in n(v).split() if w not in STOP and w not in GEN and w not in cw and len(w) > 2]
        if not d and tipo and cw & set(n(v).split()):
            d = [w for w in n(v).split() if w not in STOP and len(w) > 2]   # «Parco archeologico di Pompei»: tutte le parole, comune compreso
        archeo = False
        if not d and re.search(r'\b(area archeologica|scavi|parco archeologico|sito archeologico)\b', n(v)) and cw & set(n(v).split()):
            d = sorted(cw); archeo = True   # «Area archeologica di Pompei» = biglietto d'ingresso a Pompei
        if d and all(w in WEAK for w in d):
            if tipo: d = d + [w for w in n(re.sub(r'\s*\([^)]*\)', '', nome)).split() if w in TIPI] + sorted(cw)   # «Teatro antico» di Taormina: tipo, parole e comune tutti nel prodotto
            else: continue
        if not d: continue
        for ps, u in prods:
            t = ' '.join(EN.get(w, w) for w in n(ps).split()); toks = set(t.split())
            if t.split()[:len(cw)] == sorted(cw) or t.startswith(n(com) + ' '): t = t[len(n(com)) + 1:]; toks = set(t.split())   # titolo «Roma: …»
            if not all(ha(w, toks, t) for w in d): continue
            if toks & NO: continue
            if toks & ACQUA and not (set(n(nome).split()) & {'grotta', 'grotte', 'isola', 'isole', 'lago', 'faraglioni', 'cala', 'baia'}): continue
            pos = [i for i, w in enumerate(t.split()) if any(ha(x, {w}, w) for x in d)]
            if not pos or pos[0] > 7: continue   # il luogo deve essere il soggetto del titolo, non una tappa
            if archeo and not (toks & BIG): continue
            if tipo and not archeo and not (tipo[0] in toks or (tipo[0] == 'musei' and 'museo' in toks) or (tipo[0] == 'museo' and 'musei' in toks)): continue
            extra = len([w for w in toks if w not in STOP and not any(ha(x, {w}, w) for x in d)])
            pr = [w for w in t.split() if w not in STOP and w not in TIPI and w not in GEN]
            inizio = bool(pr) and ha(pr[0], set(d), ' '.join(d)) or bool(pr) and pr[0] in d
            sc = (len(d), bool(toks & BIG), inizio, -extra, -len(t))
            if best is None or sc > best[0]: best = (sc, u, ps, v)
    if best:
        out[pid] = best[1]; cand.append('%s | %s | %s => %s' % (com, nome, best[3], best[2]))
json.dump(out, open(os.path.join(H, 'data', 'gyg.json'), 'w'), ensure_ascii=False, indent=0, sort_keys=True)
open(os.path.join(H, 'data', 'gyg-candidati.txt'), 'w').write('\n'.join(sorted(cand)) + '\n')
print('luoghi con GetYourGuide', len(out), '| di cui biglietto/ingresso', sum(1 for c in cand if set(n(c.split(' => ')[1]).split()) & BIG))
