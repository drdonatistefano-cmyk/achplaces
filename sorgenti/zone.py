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
CSSZ = ('<style id="zone-css">html .pick{grid-template-columns:repeat(4,minmax(0,1fr))!important;max-width:820px!important}'
        '@media (max-width:759px){html #qbar .pick{grid-template-columns:1fr 1fr!important}}</style>')
BLOCCO = f'<!--ZONE-->{CSSZ}<script id="zone-dati">window.ZONE_ACH={DATI};</script><!--/ZONE-->'
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
# 23/11 sera (Stefano: «aggiungi un filtro anche per le zone in alto»): menu «Zone» accanto a Regioni, Province, Comuni.
# Scegliere una zona = scegliere i suoi comuni (o le province intere: Romagna, Salento) con lo stesso goView dei menu.
MSEL_COM = '<div class="msel"><span class="mlab">Comuni</span><button class="mbtn" id="com-btn"'
MSEL_ZON = ('<div class="msel msel-zon"><span class="mlab">Zone</span><button class="mbtn" id="zon-btn" type="button" aria-haspopup="true" '
            'aria-expanded="false"><span class="mv" id="zon-val">Tutte</span><span class="cv" aria-hidden="true">▼</span></button></div>\n      ')
POP_COM_FINE = '<button type="button" class="mpdone" data-close="com">Fatto</button></div>\n      </div>'
POP_ZON = ('\n      <div class="mpop" id="zon-pop" hidden role="dialog" aria-label="Scegli le zone">\n'
           '        <div class="mphead"><b>Zone</b><span>le zone tradizionali di AchRecipes</span></div>\n'
           '        <input class="mpq" id="zon-q" type="search" placeholder="Cerca una zona…" aria-label="Cerca una zona" autocomplete="off">\n'
           '        <div class="mlist" id="zon-list"></div>\n'
           '        <div class="mpfoot"><button type="button" class="mpall" id="zon-all">Tutte le zone</button><button type="button" class="mpdone" data-close="zon">Fatto</button></div>\n'
           '      </div>')
JSZ = ('let ZSEL=[],ZH="";function zonComuni(z){const Z=window.ZONE_ACH;if(!Z)return [];return COMUNI.filter(c=>(Z.c[c.slug]||[]).includes(z)||(Z.p[c.prov.toLowerCase()]||[]).includes(z));}'
 'function zonProv(z){const Z=window.ZONE_ACH;return Z?Object.keys(Z.p).filter(p=>Z.p[p].includes(z)).map(p=>p.toUpperCase()):[];}'
 'function zonVal(){const Z=window.ZONE_ACH;if(!Z)return;if(ZSEL.length&&location.hash!==ZH)ZSEL=[];'
 '$("zon-val").innerHTML=!ZSEL.length?"Tutte":ZSEL.length===1?esc(Z.n[ZSEL[0]]):`<span class="mc">${ZSEL.length}</span> zone`;$("zon-all").hidden=!ZSEL.length;}'
 'function renderZon(){const Z=window.ZONE_ACH;if(!Z)return;const q=fold(($("zon-q").value||"").trim());'
 'const L=Object.keys(Z.n).map(z=>{const cs=zonComuni(z);return [z,Z.n[z],cs.length,cs.reduce((a,c)=>a+c.places.length,0)]}).filter(x=>x[3]&&(!q||fold(x[1]).includes(q))).sort((a,b)=>a[1].localeCompare(b[1],"it"));'
 '$("zon-list").innerHTML=L.map(x=>{const on=ZSEL.includes(x[0]);return `<button type="button" class="mopt${on?" on":""}" data-z="${x[0]}" aria-pressed="${on}"><span class="t">${esc(x[1])}</span><small>${x[2]} comun${x[2]===1?"e":"i"} · ${x[3]}</small></button>`}).join("")||`<p class="fhint" style="padding:8px">Nessuna zona.</p>`;zonVal();}'
 'function zonApplica(){if(!ZSEL.length){setComune("tutti");return;}const cs=ZSEL.flatMap(z=>zonComuni(z)),pv=[...new Set(cs.map(c=>c.prov))];'
 'const intere=ZSEL.every(z=>zonProv(z).length)?[...new Set(ZSEL.flatMap(zonProv))]:null;'
 'if(intere)goView(intere,[]);else goView(pv,[...new Set(cs.map(c=>c.slug))]);ZH=location.hash;zonVal();}'
 '$("zon-btn").onclick=()=>popToggle("zon");$("zon-q").addEventListener("input",renderZon);'
 '$("zon-all").onclick=()=>{ZSEL=[];zonApplica();popToggle("zon",true);};'
 '$("zon-list").onclick=e=>{const b=e.target.closest(".mopt");if(!b)return;const z=b.dataset.z;ZSEL=ZSEL.includes(z)?ZSEL.filter(x=>x!==z):[...ZSEL,z];zonApplica();popToggle("zon",true);};'
 'addEventListener("hashchange",()=>setTimeout(zonVal,0));new MutationObserver(()=>zonVal()).observe($("com-val"),{childList:true,characterData:true,subtree:true});zonVal();\n')
SOST += [
 ('for(const w of ["reg","prov","com"])', 'for(const w of ["reg","prov","com","zon"])'),
 ('if(which==="com"&&!$("com-pop").hidden){renderComList();', 'if(which==="zon"&&!$("zon-pop").hidden){renderZon();if(!isPhone())$("zon-q").focus();}if(which==="com"&&!$("com-pop").hidden){renderComList();'),
 ('$("com-btn").onclick=()=>popToggle("com");\n', '$("com-btn").onclick=()=>popToggle("com");\n' + JSZ),
]
for P_ in (os.path.join(RAD, 'sorgenti', 'template.html'), os.path.join(RAD, 'index.html')):
    t = open(P_, encoding='utf-8').read()
    t = re.sub(r'<!--ZONE-->.*?<!--/ZONE-->', '', t, flags=re.S)
    if 'id="zon-btn"' not in t:
        assert t.count(MSEL_COM) == 1 and t.count(POP_COM_FINE) == 1, P_
        t = t.replace(MSEL_COM, MSEL_ZON + MSEL_COM.replace('<div class="msel">', '<div class="msel">'), 1)
        # il menu Zone va dopo Comuni: lo sposto dietro il blocco di Comuni
        i = t.index(MSEL_ZON); t = t[:i] + t[i+len(MSEL_ZON):]
        j = t.index(MSEL_COM); k = t.index('</div>', t.index('</button>', j)) + 6
        t = t[:k] + '\n      ' + MSEL_ZON.rstrip() + t[k:]
        t = t.replace(POP_COM_FINE, POP_COM_FINE + POP_ZON, 1)
    for a, b in SOST:
        if b in t: continue
        assert t.count(a) == 1, (P_, a[:50], t.count(a))
        t = t.replace(a, b)
    i = t.index('<script')  # i dati prima del codice dell'app
    t = t[:i] + BLOCCO + t[i:]
    open(P_, 'w', encoding='utf-8').write(t)
    print('zone messe in', os.path.relpath(P_, RAD))
print('zone', len(N), '· comuni assegnati', len(C), '· province intere', sorted(P), '· comuni delle zone senza luoghi in guida', len(manca), '· dati', len(DATI), 'byte')
