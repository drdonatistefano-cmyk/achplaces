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

BRUTTI = re.compile(r'stemma|coat[ _]of[ _]arms|wappen|blason|logo|mappa|map[ _.]|locator|locat|flag|bandiera|cartina|pianta[ _]|planimetria|schema|diagram|signpost|cartello|targa|lapide|banner|painting|dipinto|olio su tela|oil on canvas|acquerello|watercolou?r|engraving|incisione|stampa antica|claude monet|postcard|cartolina', re.I)

def distintivi(nome, com):
    ct = set(norm(com))
    return [w for w in norm(nome) if w not in STOP and w not in GEN and w not in ct and len(w) > 2]

scarti, dubbi = {}, []
# esclusioni manuali dopo verifica a vista
ESCLUSI = {'spoleto-pg--basilica-di-san-salvatore': 'foto dubbia (verifica a vista)'}
for k, r in ESCLUSI.items():
    if k in cache and 'img' in cache[k]: scarti[k] = r
con = {k: v for k, v in cache.items() if 'img' in v}

for k, v in con.items():
    fl = norm(os.path.splitext(v.get('file', ''))[0]); fn=' '.join(fl)
    if BRUTTI.search(v.get('file', '')):
        scarti[k] = 'immagine non fotografica (stemma/mappa/cartello)'; continue
    if v.get('via') in ('ricerca', 'categoria'):
        d = distintivi(v['n'], v['com'])
        fw = set(fl)
        cw = norm(v.get('catf', '')); cn = ' '.join(cw)
        if d and v.get('catf') and all(w in cw or (len(w) > 5 and w[:6] in cn) for w in d):
            pass   # 9/11: foto presa dalla categoria Commons del luogo (tutte le parole distintive nel nome della categoria)
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
