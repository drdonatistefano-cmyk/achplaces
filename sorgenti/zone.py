#!/usr/bin/env python3
"""Zone tradizionali in Places (Stefano, 23/11/2026: «introdurre il concetto di zona di Dinners e Recipes»). ANTEPRIMA.
Le zone sono le 41 di AchRecipes (sorgenti/zone/zone-recipes.json, copia: id, nome, tipo, province, comuni); come nel
prototipo di Dinners, Romagna = province FC, RA, RN e Salento = provincia LE, le altre per i comuni elencati.
Mette nella guida il livello «Zone» (fra Province e Regioni, come Dinners) con una tabellina di pochi KB dentro la
pagina: nessun file in più da scaricare. Un luogo di un comune che sta in più zone va nella prima.
Scrive modello e pagina: blocco dati fra <!--ZONE-->…<!--/ZONE--> e poche sostituzioni nel codice dei raggruppamenti
(rilanciabile: se il codice è già cambiato non lo tocca).  python3 sorgenti/zone.py"""
import os, re, json, unicodedata
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTERE = {"romagna": ["FC", "RA", "RN"], "salento": ["LE"]}
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')
Z = json.load(open(os.path.join(RAD, 'sorgenti', 'zone', 'zone-recipes.json'), encoding='utf-8'))
man = json.load(open(os.path.join(RAD, 'manifest.json')))
CS = set()
for f in man['det'].values():
    CS |= set(json.load(open(os.path.join(RAD, f), encoding='utf-8')).keys())
N, C, P, manca = {}, {}, {}, []
for z in Z:
    N[z['id']] = z['nome']
    for pr in INTERE.get(z['id'], []): P.setdefault(pr.lower(), []).append(z['id'])
    for nome, pr in z.get('comuni', []):
        s = slug(nome) + '-' + pr.lower()
        if s in CS: C.setdefault(s, []).append(z['id'])
        else: manca.append(s)
DATI = json.dumps({'n': N, 'c': C, 'p': P}, ensure_ascii=False, separators=(',', ':'))
BLOCCO = f'<!--ZONE--><script id="zone-dati">window.ZONE_ACH={DATI};</script><!--/ZONE-->'
KZ = 'z:p=>{const Z=window.ZONE_ACH;if(!Z)return "";const s=p.comSlug||"";return ((Z.c[s]||Z.p[s.slice(s.lastIndexOf("-")+1)]||[])[0])||"";},'
SOST = [
 ('const ORD=["a","r","v","c","p"],K={c:', 'const ORD=["a","r","v","c","p"],K={' + KZ + 'c:'),
 ('const liv=D.length?ORD[ORD.indexOf(D[D.length-1].g)+1]:S.grp;',
  'const liv=D.length?({a:"r",r:"v",v:"c",z:"c",c:"p"})[D[D.length-1].g]:S.grp;if(liv==="z")list=list.filter(p=>K.z(p));'),
 ('const NOMI={a:"Nord-Sud",r:"Regioni",v:"Province",c:"Comuni"};', 'const NOMI={a:"Nord-Sud",r:"Regioni",v:"Province",z:"Zone",c:"Comuni"};'),
 ('const nome=(k,ps)=>{const c=infoCom(ps[0]);', 'const nome=(k,ps)=>{const c=infoCom(ps[0]);if(liv==="z")return [(window.ZONE_ACH&&ZONE_ACH.n[k])||k,"Zona tradizionale"];'),
 ('const nx={a:"r",r:"v",v:"c"}[liv]', 'const nx={a:"r",r:"v",v:"c",z:"c"}[liv]'),
 ('<i class="em">🗺️</i> Province</button>', '<i class="em">🗺️</i> Province</button><button type="button" class="agg" data-grp="z" aria-pressed="false"><i class="em">🍇</i> Zone</button>'),
]
for P_ in (os.path.join(RAD, 'sorgenti', 'template.html'), os.path.join(RAD, 'index.html')):
    t = open(P_, encoding='utf-8').read()
    t = re.sub(r'<!--ZONE-->.*?<!--/ZONE-->', '', t, flags=re.S)
    for a, b in SOST:
        if b in t: continue
        assert t.count(a) == 1, (P_, a[:50], t.count(a))
        t = t.replace(a, b)
    i = t.index('<script')  # i dati prima del codice dell'app
    t = t[:i] + BLOCCO + t[i:]
    open(P_, 'w', encoding='utf-8').write(t)
    print('zone messe in', os.path.relpath(P_, RAD))
print('zone', len(N), '· comuni assegnati', len(C), '· province intere', sorted(P), '· comuni delle zone senza luoghi in guida', len(manca), '· dati', len(DATI), 'byte')
