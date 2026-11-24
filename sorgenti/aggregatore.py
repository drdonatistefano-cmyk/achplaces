#!/usr/bin/env python3
"""Aggregatore con − e + (Stefano, 23/11/2026: «pubblica Places con l'aggregatore»).
Sul telefono, sotto la ricerca: «+» aggrega (raggruppa di più), «−» disaggrega (scende nel dettaglio), al centro il livello
(regola di Stefano 23/11 23:30 per tutte le guide, come Dinners e Dishes; corretto il verso il 24/11)
(Nord-Sud · Regioni · Zone · Province · Comuni · Luoghi; Zone solo se c'è il tasto, vedi zone.py).
Anteprima 23/11 sera: su iPad e PC sta a destra di «Tutti i N luoghi», riga che resta fissa scorrendo; sul PC (≥1100 px)
accanto a Guida e Mappa i menu Regioni, Province, Comuni e «Collaborano con noi»; sull'iPad la ricerca (più corta),
Azzera e Vicino a te accanto a Guida e Mappa. Usa i tasti di raggruppamento che la guida ha già (.agg[data-grp]): li preme lui.
Mette il blocco in sorgenti/template.html e in index.html (i flussi lavorano sulla pagina) fra i segni
<!--AGGREGATORE-->…<!--/AGGREGATORE-->; si può rilanciare quante volte si vuole:  python3 sorgenti/aggregatore.py
I nomi dei livelli si leggono dai tasti che già esistono, così la versione inglese li ha tradotti."""
import os, re
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGINE = [os.path.join(RAD, 'sorgenti', 'template.html'), os.path.join(RAD, 'index.html')]
HTML = ('<!--AGGREGATORE--><div class="aggpm" id="aggpm" hidden>'
        '<button type="button" class="pm meno" aria-label="Disaggrega: più dettaglio">−</button>'
        '<div class="aggliv" aria-live="polite"><b></b><span class="aggdots"></span></div>'
        '<button type="button" class="pm piu" aria-label="Aggrega: raggruppa di più">+</button></div><!--/AGGREGATORE-->')
CSS = ('.aggpm:not([hidden]){display:flex;align-items:center;gap:8px;margin:8px 0 2px}'
       '@media (min-width:760px){html .topnav .aggr{display:none!important}'
       '.conta .aggpm{margin:0 0 0 auto!important;width:280px;flex:none}'
       '.conta .aggpm .pm{width:38px;height:38px;font-size:21px;border-radius:12px}.conta .aggpm .aggliv{height:38px;border-radius:12px;gap:3px}'
       '.conta .aggpm .aggliv b{font-size:14.5px}'
       '.topnav .collab{flex:none;margin-left:auto;height:40px;padding:0 16px;display:inline-flex!important;align-items:center;gap:7px;border-radius:999px;'
       'border:1px solid var(--line);background:var(--paper);color:var(--ink);font:600 14.5px/1 var(--sans,system-ui);text-decoration:none;white-space:nowrap}'
       '.topnav .collab:hover{border-color:var(--terra);background:var(--terra-soft)}'
       '.topnav #searchwrap{flex:1 1 auto;min-width:0;max-width:340px;margin:0 0 0 12px}.topnav #eatbtn,.topnav #resetbtn{flex:none}'
       'html .topnav #q{height:40px!important}'
'.topnav .pick{display:flex!important;gap:8px!important;margin:0 0 0 14px!important;flex:1 1 auto;min-width:0}'
       '.topnav .pick .msel{flex:1 1 0;min-width:0;max-width:190px;position:relative}.topnav .pick .mlab{display:none!important}'
       '.topnav .pick .mbtn{height:40px!important;min-height:0!important;width:100%;display:flex!important;align-items:center;gap:6px}'
       '.topnav .pick .mbtn::before{content:attr(data-l);font:600 12px/1 var(--sans,system-ui);color:var(--mute);flex:none}'
       '.topnav .pick .mbtn .mv{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;text-align:left}}'
       '.aggpm .pm{flex:none;width:46px;height:46px;border-radius:14px;border:1px solid var(--line);background:var(--paper);'
       'font:700 24px/1 var(--sans,system-ui);color:var(--ink);display:flex;align-items:center;justify-content:center;cursor:pointer}'
       '.aggpm .pm:disabled{opacity:.35;cursor:default}'
       '.aggpm .aggliv{flex:1;min-width:0;height:46px;border-radius:14px;border:1px solid var(--line);background:var(--paper);'
       'display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px}'
       '.aggpm .aggliv b{font-size:16px;font-weight:700;white-space:nowrap}'
       '.aggpm .aggdots{display:flex;gap:5px}.aggpm .aggdots i{width:6px;height:6px;border-radius:50%;background:var(--line)}'
       '.aggpm .aggdots i.on{background:#2f7a5c}')
JS = r'''(function(){var LV=["a","r","z","v","c","p"].filter(function(g){return document.querySelector('.agg[data-grp="'+g+'"]')}),w=document.getElementById("aggpm");if(!w)return;
var en=(document.documentElement.lang||"").indexOf("en")===0;
w.querySelector(".meno").setAttribute("aria-label",en?"Ungroup: more detail":"Disaggrega: più dettaglio");
w.querySelector(".piu").setAttribute("aria-label",en?"Group more":"Aggrega: raggruppa di più");
function nome(g){var b=document.querySelector('.agg[data-grp="'+g+'"]');return b?b.textContent.replace(/^[^\p{L}]+/u,"").trim():g;}
var CUR=(function(){var o=document.querySelector(".agg.on[data-grp]");return o?o.dataset.grp:"p"})();function ora(){return CUR}
function disegna(){var g=ora(),i=LV.indexOf(g);if(i<0)i=LV.length-1;w.querySelector("b").textContent=nome(LV[i]);
 w.querySelector(".aggdots").innerHTML=LV.map(function(x,k){return '<i class="'+(k===i?"on":"")+'"></i>'}).join("");
 w.querySelector(".piu").disabled=i<=0;w.querySelector(".meno").disabled=i>=LV.length-1;
 document.querySelectorAll(".agg").forEach(function(x){var on=x.dataset.grp===LV[i];x.classList.toggle("on",on);x.setAttribute("aria-pressed",on)});}
function vai(d){var i=LV.indexOf(ora());if(i<0)i=LV.length-1;var j=i+d;if(j<0||j>=LV.length)return;
 var b=document.querySelector('.agg[data-grp="'+LV[j]+'"]');if(!b)return;b.click();CUR=LV[j];setTimeout(disegna,30);}
w.querySelector(".piu").onclick=function(){vai(-1)};w.querySelector(".meno").onclick=function(){vai(1)};
document.addEventListener("click",function(e){var a=e.target.closest&&e.target.closest(".agg[data-grp]");if(a){CUR=a.dataset.grp;setTimeout(disegna,30)}});
var mq=matchMedia("(min-width:760px)"),mqpc=matchMedia("(min-width:1100px)"),casa=w.parentNode,dopo=w.nextSibling,pk=document.querySelector(".pick"),pkCasa=pk&&pk.parentNode,pkDopo=pk&&pk.nextSibling;
var SP=["searchwrap","resetbtn","eatbtn"].map(function(i){var e=document.getElementById(i);return e?[e,e.parentNode,e.nextSibling]:null}).filter(Boolean);
var co=document.createElement("a");co.className="collab";co.href="sostenitori/";co.innerHTML='<span aria-hidden="true">🤝</span> '+(en?"Our partners":"Collaborano con noi");
function posto(){var nav=document.querySelector("nav.topnav"),ct=document.getElementById("count");if(!nav)return;ct=ct&&ct.parentNode;
 if(mq.matches&&ct)ct.appendChild(w);else if(w.parentNode!==casa)casa.insertBefore(w,dopo);
 var a=nav.querySelector(".aggr");
 if(pk){if(mqpc.matches)nav.insertBefore(pk,a?a.nextSibling:null);else if(pk.parentNode!==pkCasa)pkCasa.insertBefore(pk,pkDopo);}
 if(mqpc.matches)nav.insertBefore(co,pk&&pk.parentNode===nav?pk.nextSibling:(a?a.nextSibling:null));else if(co.parentNode)co.remove();
 var ipad=mq.matches&&!mqpc.matches;
 if(ipad)SP.forEach(function(x,i){nav.insertBefore(x[0],i?SP[i-1][0].nextSibling:(a?a.nextSibling:null))});
 else SP.slice().reverse().forEach(function(x){if(x[0].parentNode!==x[1])x[1].insertBefore(x[0],x[2]&&x[2].parentNode===x[1]?x[2]:null)});}
function etichette(){document.querySelectorAll(".pick .msel").forEach(function(m){var l=m.querySelector(".mlab"),b=m.querySelector(".mbtn");if(l&&b)b.setAttribute("data-l",l.textContent.trim())})}
etichette();setTimeout(etichette,1500);setTimeout(etichette,4000);
mq.addEventListener("change",posto);mqpc.addEventListener("change",posto);posto();
w.hidden=false;disegna();})();'''
# 23/11 sera: su iPhone e iPad (dalle 20:34 anche senza averlo mai usato), quando l'aggregatore esce dallo schermo compaiono in basso un «−» a
# sinistra e un «+» a destra (ai lati del tasto Filtri / Azzera); se toccherebbero qualcosa salgono sopra.
# 24/11 (velocità): niente più lavoro a ogni movimento dello scorrimento (forzava l'impaginazione e faceva scattare la pagina):
# se l'aggregatore o l'elenco entrano o escono dallo schermo lo dicono due IntersectionObserver.
CSS += ('.aggfl{position:fixed;bottom:calc(16px + env(safe-area-inset-bottom));z-index:38;width:52px;height:52px;border-radius:50%;'
        'border:1px solid var(--line2);background:var(--paper);color:var(--terra-ink);font:700 26px/1 var(--sans,system-ui);'
        'display:grid;place-items:center;box-shadow:0 8px 22px -8px rgba(20,16,12,.45);cursor:pointer;transition:opacity .18s,transform .18s}'
        '.aggfl.meno{left:12px}.aggfl.piu{right:12px}.aggfl[hidden]{display:none}.aggfl:disabled{opacity:.4}'
        '.aggfl.via{opacity:0;transform:translateY(80px);pointer-events:none}'
        '.aggtoast{position:fixed;left:50%;transform:translateX(-50%);z-index:38;padding:7px 14px;border-radius:999px;background:var(--ink);'
        'color:var(--paper);font:600 14px/1 var(--sans,system-ui);pointer-events:none;opacity:0;transition:opacity .2s;white-space:nowrap}'
        '.aggtoast.on{opacity:.92}')
JS += r'''(function(){var w=document.getElementById("aggpm");if(!w)return;var mq=matchMedia("(max-width:1099px), (hover:none)");
var en=(document.documentElement.lang||"").indexOf("en")===0,usato=true,fuori=false,tt;
function mk(c,s,l){var b=document.createElement("button");b.type="button";b.className="aggfl via "+c;b.textContent=s;b.setAttribute("aria-label",l);document.body.appendChild(b);return b}
var m=mk("meno","−",en?"Ungroup: more detail":"Disaggrega: più dettaglio"),p=mk("piu","+",en?"Group more":"Aggrega: raggruppa di più"),to=document.createElement("div");to.className="aggtoast";to.setAttribute("aria-live","polite");document.body.appendChild(to);
function vis(e){if(!e||e.hidden)return null;var s=getComputedStyle(e);if(s.display==="none"||s.visibility==="hidden"||+s.opacity<.1)return null;var r=e.getBoundingClientRect();return r.width&&r.height&&r.bottom>0&&r.top<innerHeight?r:null}
function sopra(a,b){return !(a.right<=b.left||a.left>=b.right||a.bottom<=b.top||a.top>=b.bottom)}
var gIn=true;function sistema(){var vista=!document.querySelector("main[hidden]")&&gIn;
 var on=mq.matches&&usato&&fuori&&vista;[m,p].forEach(function(b){b.classList.toggle("via",!on);b.style.bottom=""});
 m.disabled=w.querySelector(".meno").disabled;p.disabled=w.querySelector(".piu").disabled;
 if(!on)return;var ost=["nAm","giu","nMap"].map(function(i){return vis(document.getElementById(i))}).filter(Boolean),alto=16;
 [m,p].forEach(function(b){b.style.bottom="calc(16px + env(safe-area-inset-bottom))";var r=b.getBoundingClientRect();
  ost.forEach(function(o){if(sopra(r,o))alto=Math.max(alto,innerHeight-o.top+10)})});
 if(alto>16)[m,p].forEach(function(b){b.style.bottom=alto+"px"});
 var rb=m.getBoundingClientRect();to.style.bottom=(innerHeight-rb.top+10)+"px";}
function annuncia(){clearTimeout(tt);to.textContent=w.querySelector("b").textContent;to.classList.add("on");tt=setTimeout(function(){to.classList.remove("on")},1300)}
m.onclick=function(){w.querySelector(".meno").click();setTimeout(function(){sistema();annuncia()},60)};
p.onclick=function(){w.querySelector(".piu").click();setTimeout(function(){sistema();annuncia()},60)};
w.addEventListener("click",function(){usato=true;setTimeout(sistema,60)});
document.addEventListener("click",function(e){if(e.target.closest&&e.target.closest(".agg[data-grp]")){usato=true;setTimeout(sistema,60)}});
new IntersectionObserver(function(es){fuori=!es[0].isIntersecting;sistema()}).observe(w);
(function(){var g=document.getElementById("grid");if(g)new IntersectionObserver(function(es){gIn=es[es.length-1].isIntersecting;sistema()}).observe(g)})();
addEventListener("resize",sistema);mq.addEventListener("change",sistema);
var ro=window.ResizeObserver?new ResizeObserver(function(){sistema();setTimeout(sistema,250)}):null;
function guarda(){["nAm","giu","nMap"].forEach(function(i){var e=document.getElementById(i);if(e&&!e._aggro&&ro){e._aggro=1;ro.observe(e);new MutationObserver(function(){setTimeout(sistema,30);setTimeout(sistema,300)}).observe(e,{attributes:true,childList:true,subtree:true,characterData:true})}})}
guarda();setTimeout(guarda,2000);})();'''
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
