"""Abbina i luoghi della guida alle pagine prodotto Tiqets (sorgenti/tiqets/prodotti.json, dalle sitemap pubbliche).
Regola: il bottone compare solo se Tiqets vende proprio quel luogo (tutte le parole distintive del nome nella pagina prodotto,
stesso comune, niente tour/escursioni/pacchetti). Scrive data/tiqets.json {id_luogo: url} e data/tiqets-candidati.txt."""
import json, re, sys, unicodedata, subprocess, os
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, H)
from leggi_dati import righe
n = lambda s: re.sub(r'[^a-z0-9]+', ' ', ''.join(c for c in unicodedata.normalize('NFD', s.lower()) if not unicodedata.combining(c))).strip()
P = json.load(open('/home/claude/achplaces/sorgenti/tiqets/prodotti.json'))
ALIAS = {'paestum': 'capaccio paestum', 'vaticano': 'roma', 'citta del vaticano': 'roma', 'cinque terre': None}
STOP = set('di del della dei delle degli e la il lo le i gli d l a al alla allo ai agli in con sul sulla da dal dalla per un una uno'.split())
GEN = set('chiesa museo palazzo castello torre piazza basilica cattedrale duomo civico civica centro storico parco rocca teatro villa ponte porta mura abbazia convento galleria nazionale area archeologica archeologico sito complesso monumentale santuario giardino giardini scavi parco'.split())
NO = set('tour tours guidato guidata escursione escursioni gita trasferimento trasferimenti crociera cena pranzo degustazione degustazioni pacchetto combinato combo pass card city treno bus hop navetta privato privata giornata mezza notte notturno notturna serale bici ebike segway kayak barca motoscafo da udienza mostra exhibition concerto concert opera arie tasting food drive test guide guided guida-turistica with transfer dinner lunch cooking voucher spa noleggio biciclette golf cart app servizio fotografico prigioni sotterranei underground multimedia natale'.split())
WEAK = set('museo musei romano romana antico antica vecchio nuovo nuova grande san santa santo maggiore'.split())
TIPI = set('chiesa museo musei palazzo castello torre piazza basilica cattedrale duomo teatro villa ponte porta abbazia galleria giardino giardini terme acquario grotte grotta catacombe anfiteatro chiostro campanile cupola cappella sinagoga parco'.split())
ESCLUSI = {('Venezia', 'Torcello'), ('Dorgali', 'Cala Gonone'), ('Bormio', 'Bormio Terme'), ('Genova', 'Porto Antico e il Bigo')}   # verificati a mano: Tiqets vende altro
def citta(slug):
    c = re.sub(r'-c\d+$', '', slug); c = re.sub(r'^(attrazioni|cose-da-fare)-|-attractions$|^attractions-', '', c).replace('-', ' ')
    return ALIAS.get(c, c)
perc = {}
for u, cs, ps, i in P:
    c = citta(cs)
    if c: perc.setdefault(c, []).append((ps, u))
m = json.load(open(os.path.join(H, 'manifest.json'))); D = righe(json.load(open(os.path.join(H, m['dati']))))
def s40(s):
    s = ''.join(ch for ch in unicodedata.normalize('NFD', s) if not unicodedata.combining(ch)).lower(); return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40].rstrip('-')
LU = [(c['slug'] + '--' + (a[0] if a[0] else s40(a[1])), a[1], c['name']) for c in D['c'] for a in c['places']]
bo = json.loads(subprocess.check_output(['node', '-e', "const fs=require('fs');eval(fs.readFileSync('" + H + "/data/places-bologna.js','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES.map(p=>[p.id,p.name])))"]))
LU += [(i, nm, 'Bologna') for i, nm in bo]
def varianti(nome):
    v = [re.sub(r'\s*\([^)]*\)', '', nome)] + re.findall(r'\(([^)]+)\)', nome)
    v += [re.split(r'\s+e\s+|,|\s+[–-]\s+|:', v[0])[0]]
    return [x for x in dict.fromkeys(x.strip() for x in v) if len(x) > 3]
def ha(w, toks, testo): return w in toks or (len(w) > 7 and w[:7] in testo)
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
        if not d or all(w in WEAK for w in d): continue
        for ps, u in prods:
            t = n(ps.replace('biglietti-per-', '', 1)); toks = set(t.split())
            if not all(ha(w, toks, t) for w in d): continue
            if toks & NO: continue
            if archeo and not ('ingresso' in toks and t.split()[0] in cw): continue
            if tipo and not archeo and not (tipo[0] in toks or (tipo[0] == 'musei' and 'museo' in toks) or (tipo[0] == 'museo' and 'musei' in toks)): continue
            extra = len([w for w in toks if w not in STOP and not any(ha(x, {w}, w) for x in d)])
            pr = [w for w in t.split() if w not in STOP and w not in TIPI and w not in GEN]
            inizio = bool(pr) and ha(pr[0], set(d), ' '.join(d)) or bool(pr) and pr[0] in d
            sc = (len(d), inizio, -extra, -len(t))
            if best is None or sc > best[0]: best = (sc, u, ps, v)
    if best:
        out[pid] = best[1]; cand.append('%s | %s | %s => %s' % (com, nome, best[3], best[2]))
json.dump(out, open(os.path.join(H, 'data', 'tiqets.json'), 'w'), ensure_ascii=False, indent=0, sort_keys=True)
open(os.path.join(H, 'data', 'tiqets-candidati.txt'), 'w').write('\n'.join(sorted(cand)) + '\n')
print('luoghi con Tiqets', len(out))
