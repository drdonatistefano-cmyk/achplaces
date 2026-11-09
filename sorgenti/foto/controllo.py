#!/usr/bin/env python3
# Controllo foto: unisce le cache, scarta abbinamenti sospetti, elenca i dubbi.
import json, glob, os, re, sys
F = '/home/claude/foto/'
src = open(F + 'foto.py').read().split('PARTE=None')[0]
exec(src)  # norm, GEN, STOP, TIPO, tipi, punteggio

cache = {}
for f in sorted(glob.glob(F + 'foto-[0-9]*.json')) + [F + 'foto-umbria-test.json', F + 'foto2.json']:
    if os.path.exists(f):
        for k, v in json.load(open(f)).items():
            if k not in cache or ('img' in v and 'img' not in cache[k]):
                cache[k] = v

BRUTTI = re.compile(r'stemma|coat[ _]of[ _]arms|wappen|blason|logo|mappa|map[ _.]|locator|locat|flag|bandiera|cartina|pianta[ _]|planimetria|schema|diagram|signpost|cartello|targa|lapide|banner|painting|dipinto|olio su tela|oil on canvas|acquerello|watercolou?r|engraving|incisione|stampa antica|claude monet|postcard|cartolina|\\b1[0-9]{3} circa\\b|\\bcirca 1[0-9]{3}\\b|pelike|\\bvaso\\b|\\bvase\\b', re.I)

def distintivi(nome, com):
    ct = set(norm(com))
    return [w for w in norm(nome) if w not in STOP and w not in GEN and w not in ct and len(w) > 2]

import csv as _csv
ALTRI = {' '.join(norm(r['comune'])) for r in _csv.DictReader(open('/home/claude/achs-places-guide/data/geo/comuni_istat.csv', encoding='utf-8'))}
GENC = set('ponte ponti prato valle montagna monte bianco laghi lago aosta trinita santa sant onofrio barbara corbara chiesa piana marina porto torre castello rocca villa palazzo fontana'.split())
scarti, dubbi = {}, []
# esclusioni manuali dopo verifica a vista
ESCLUSI = {'spoleto-pg--basilica-di-san-salvatore': 'foto dubbia (verifica a vista)'}
# 9/11: foto scelte a mano dopo verifica (esenti dal controllo «gemelli»): luoghi senza foto specifica su Commons,
# a cui si dà una foto diversa del complesso a cui appartengono (es. le Cattedrali sotterranee UNESCO di Canelli)
MANUALI = json.load(open(F + 'manuali.json')) if os.path.exists(F + 'manuali.json') else {}
for k, r in ESCLUSI.items():
    if k in cache and 'img' in cache[k]: scarti[k] = r
con = {k: v for k, v in cache.items() if 'img' in v}

for k, v in con.items():
    fl = norm(os.path.splitext(v.get('file', ''))[0]); fn=' '.join(fl)
    if BRUTTI.search(v.get('file', '')):
        scarti[k] = 'immagine non fotografica (stemma/mappa/cartello)'; continue
    if v.get('via') in ('ricerca', 'categoria', 'albero', 'openverse'):
        # 9/11: il nome del file cita un altro comune (e non il proprio): foto di un altro luogo
        cm = ' '.join(norm(v['com']))
        nn = ' ' + ' '.join(norm(v['n'])) + ' '
        if cm not in fn and any((' ' + x + ' ') in (' ' + fn + ' ') for x in ALTRI if x != cm and x not in cm and len(x) > 4 and (' ' + x + ' ') not in nn and x not in GENC):
            scarti[k] = 'il nome del file cita un altro comune'; continue
        d = distintivi(v['n'], v['com'])
        fw = set(fl)
        cw = norm(v.get('catf', '')); cn = ' '.join(cw)
        comw = norm(v['com']); paren = re.findall(r'\(([^)]+)\)', v.get('catf', ''))
        if v.get('catf') and paren and not any(set(comw) <= set(norm(x)) for x in paren):
            scarti[k] = 'categoria di un altro luogo («%s»)' % v['catf']; continue
        if d and v.get('catf') and all(w in cw or (len(w) > 5 and w[:6] in cn) for w in d):
            # 9/11: foto presa dalla categoria Commons del luogo: il nome del file deve citare il luogo o il comune
            if not (any(w in fw or (len(w) > 5 and w[:6] in fn) for w in d) or ' '.join(comw) in fn):
                scarti[k] = 'foto della categoria senza riferimento al luogo nel nome del file'; continue
        elif d:
            if not any(w in fw or (len(w) > 5 and w[:6] in fn) for w in d):
                scarti[k] = 'nome del file senza parole distintive del luogo'; continue
        else:
            t = tipi(norm(v['n']))
            tf = tipi(fl)
            if t and tf and t != tf:
                scarti[k] = 'tipo di luogo diverso'; continue
            if not t or not tf:
                scarti[k] = 'nome generico, tipo non verificabile'; continue
    elif v.get('via') == 'wikidata':
        if v.get('s', 1) < 0.8:
            ct = set(norm(v['com']))
            nt = [w for w in norm(v['n']) if w not in ct]; lt = [w for w in norm(v.get('lab', '')) if w not in ct]
            nd = [w for w in nt if w not in GEN and len(w) > 2]; ld = [w for w in lt if w not in GEN and len(w) > 2]
            simile = lambda w, ws: any(w == x or (len(w) > 5 and len(x) > 5 and w[:6] == x[:6]) for x in ws)
            if not all(simile(w, nt) for w in ld):
                scarti[k] = 'etichetta Wikidata con parole estranee («%s»)' % v.get('lab', ''); continue
            if nd and not any(simile(w, lt) for w in nd):
                scarti[k] = 'nessuna parola distintiva in comune con «%s»' % v.get('lab', ''); continue
            dubbi.append((k, 'somiglianza bassa con «%s»' % v.get('lab', '')))

# 9/11: luoghi «gemelli» (stesso nome generico, es. «Cattedrali sotterranee – Cantine Gancia/Contratto/Coppo»): la foto
# deve citare nel nome del file o nella categoria la parte che distingue il luogo dai suoi gemelli, altrimenti è di un altro.
pergen = {}
for k, v in con.items():
    base = re.split(r'\s+[–-]\s+|:', re.sub(r'\s*\([^)]*\)', '', v['n']))[0].strip().lower()
    pergen.setdefault((v['com'], base), []).append(k)
for (com, base), ks in pergen.items():
    tutti = [k2 for k2 in cache if cache[k2].get('com') == com and re.split(r'\s+[–-]\s+|:', re.sub(r'\s*\([^)]*\)', '', cache[k2].get('n', '')))[0].strip().lower() == base]
    if len(tutti) < 2: continue
    for k in ks:
        if k in scarti or (k in MANUALI and con[k].get('file','').replace('_',' ') == MANUALI[k]['file']): continue
        v = con[k]; mie = set(distintivi(v['n'], v['com']))
        altre = set().union(*[set(distintivi(cache[x]['n'], cache[x]['com'])) for x in tutti if x != k])
        proprie = [w for w in mie - altre]
        if not proprie: continue
        testo = ' '.join(norm(os.path.splitext(v.get('file', ''))[0])) + ' ' + ' '.join(norm(v.get('catf', '')))
        if not any(w in testo.split() or (len(w) > 5 and w[:6] in testo) for w in proprie):
            scarti[k] = 'foto generica, non del luogo specifico (manca «%s»)' % ', '.join(proprie)

# stessa foto usata per luoghi diversi dello stesso comune: tiene il migliore
per = {}
for k, v in con.items():
    if k in scarti: continue
    per.setdefault((v['com'], v['file']), []).append(k)
for (com, f), ks in per.items():
    if len(ks) > 1:
        ks.sort(key=lambda k: (con[k].get('via') == 'wikidata', con[k].get('s', 0)), reverse=True)
        for k in ks[1:]:
            scarti[k] = 'stessa foto di «%s»' % con[ks[0]]['n']

json.dump({'scarti': scarti, 'dubbi': dubbi}, open(F + 'controllo.json', 'w'), ensure_ascii=False, indent=1)
ok = {k: v for k, v in con.items() if k not in scarti}
json.dump(ok, open(F + 'foto-finale.json', 'w'), ensure_ascii=False)
from collections import Counter
print('luoghi', len(cache), 'con foto', len(con), 'scartate', len(scarti), 'finali', len(ok), 'dubbi', len(dubbi))
print(Counter(scarti.values()).most_common(8))
if '-v' in sys.argv:
    for k, r in list(scarti.items())[:60]:
        print('X', cache[k]['com'], '|', cache[k]['n'], '->', cache[k].get('file'), '|', r)
    for k, r in dubbi[:60]:
        print('?', cache[k]['com'], '|', cache[k]['n'], '->', cache[k].get('file'), '|', r)
