#!/usr/bin/env python3
"""Aggregatore con − e + (Stefano, 23/11/2026: «pubblica Places con l'aggregatore»).
Sul telefono, sotto la ricerca: «−» raggruppa di più, «+» scende nel dettaglio, al centro il livello
(Nord-Sud · Regioni · Province · Comuni · Luoghi). Usa i tasti di raggruppamento che la guida ha già (.agg[data-grp]): li preme lui.
Mette il blocco in sorgenti/template.html e in index.html (i flussi lavorano sulla pagina) fra i segni
<!--AGGREGATORE-->…<!--/AGGREGATORE-->; si può rilanciare quante volte si vuole:  python3 sorgenti/aggregatore.py
I nomi dei livelli si leggono dai tasti che già esistono, così la versione inglese li ha tradotti."""
import os, re
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINE = [os.path.join(RAD, 'sorgenti', 'template.html'), os.path.join(RAD, 'index.html')]
HTML = ('<!--AGGREGATORE--><div class="aggpm" id="aggpm" hidden>'
        '<button type="button" class="pm meno" aria-label="Meno dettaglio">−</button>'
        '<div class="aggliv" aria-live="polite"><b></b><span class="aggdots"></span></div>'
        '<button type="button" class="pm piu" aria-label="Più dettaglio">+</button></div><!--/AGGREGATORE-->')
CSS = ('.aggpm{display:none}@media (max-width:759px){.aggpm:not([hidden]){display:flex;align-items:center;gap:8px;margin:8px 0 2px}}'
       '.aggpm .pm{flex:none;width:46px;height:46px;border-radius:14px;border:1px solid var(--line);background:var(--paper);'
       'font:700 24px/1 var(--sans,system-ui);color:var(--ink);display:flex;align-items:center;justify-content:center;cursor:pointer}'
       '.aggpm .pm:disabled{opacity:.35;cursor:default}'
       '.aggpm .aggliv{flex:1;min-width:0;height:46px;border-radius:14px;border:1px solid var(--line);background:var(--paper);'
       'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}'
       '.aggpm .aggliv b{font-size:16px;font-weight:700;white-space:nowrap}'
       '.aggpm .aggdots{display:flex;gap:5px}.aggpm .aggdots i{width:6px;height:6px;border-radius:50%;background:var(--line)}'
       '.aggpm .aggdots i.on{background:#2f7a5c}')
JS = r'''(function(){var LV=["a","r","v","c","p"],w=document.getElementById("aggpm");if(!w)return;
var en=(document.documentElement.lang||"").indexOf("en")===0;
w.querySelector(".meno").setAttribute("aria-label",en?"Less detail: group more":"Meno dettaglio: raggruppa di più");
w.querySelector(".piu").setAttribute("aria-label",en?"More detail":"Più dettaglio");
function nome(g){var b=document.querySelector('.agg[data-grp="'+g+'"]');return b?b.textContent.replace(/^[^\p{L}]+/u,"").trim():g;}
var CUR=(function(){var o=document.querySelector(".agg.on[data-grp]");return o?o.dataset.grp:"p"})();function ora(){return CUR}
function disegna(){var g=ora(),i=LV.indexOf(g);if(i<0)i=LV.length-1;w.querySelector("b").textContent=nome(LV[i]);
 w.querySelector(".aggdots").innerHTML=LV.map(function(x,k){return '<i class="'+(k===i?"on":"")+'"></i>'}).join("");
 w.querySelector(".meno").disabled=i<=0;w.querySelector(".piu").disabled=i>=LV.length-1;
 document.querySelectorAll(".agg").forEach(function(x){var on=x.dataset.grp===LV[i];x.classList.toggle("on",on);x.setAttribute("aria-pressed",on)});}
function vai(d){var i=LV.indexOf(ora());if(i<0)i=LV.length-1;var j=i+d;if(j<0||j>=LV.length)return;
 var b=document.querySelector('.agg[data-grp="'+LV[j]+'"]');if(!b)return;b.click();CUR=LV[j];setTimeout(disegna,30);}
w.querySelector(".meno").onclick=function(){vai(-1)};w.querySelector(".piu").onclick=function(){vai(1)};
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest(".agg[data-grp]");if(a){CUR=a.dataset.grp;setTimeout(disegna,30)}});
w.hidden=false;disegna();})();'''
BLOCCO_FINE = f'<!--AGGREGATORE--><style id="aggpm-css">{CSS}</style><script id="aggpm-js">{JS}</script><!--/AGGREGATORE-->'
for P in PAGINE:
    t = open(P, encoding='utf-8').read()
    t = re.sub(r'<!--AGGREGATORE-->.*?<!--/AGGREGATORE-->', '', t, flags=re.S)
    i = t.index('<div class="row1">'); j = t.index('id="morebtn"', i); k = t.index('</button>', j); k = t.index('</div>', k) + 6
    t = t[:k] + HTML + t[k:]
    assert t.count('</body>') == 1, P
    t = t.replace('</body>', BLOCCO_FINE + '</body>')
    open(P, 'w', encoding='utf-8').write(t)
    print('aggregatore messo in', os.path.relpath(P, RAD))
