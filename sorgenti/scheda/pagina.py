#!/usr/bin/env python3
"""Tasto «Scheda» nelle viste raggruppate di Places (comune, provincia, zona, regione): finestra con breve descrizione,
Wikipedia, luoghi in guida, ricette e prodotti tipici di Ach's Dishes (numeri da scheda.json, rifatto ogni notte da
numeri.py) e il link a Events dove c'è (senza numeri: cambiano ogni settimana).
24/11/2026, Stefano: «sistema tutto» sul prototipo del 23/11 (ramo claude/places-proto-schede).
Rilanciabile: scrive fra <!--SCHEDA--> e <!--/SCHEDA--> nel modello (sorgenti/template.html) e nella pagina (index.html).
Accessibilità: la finestra ha il nome del luogo (aria-labelledby); il tasto dentro la scheda del gruppo è solo visivo,
per tastiera e lettori di schermo c'è un vero pulsante subito dopo («Scheda di …»), così non ci sono pulsanti annidati.
Uso: python3 sorgenti/scheda/pagina.py"""
import os, re, json
RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_REC = ('<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" fill="#a4462b"/><circle cx="50" cy="50" r="41" fill="none" '
            'stroke="#f6efe4" stroke-width="2"/><g transform="translate(9 7) scale(.82)" stroke="#f6efe4" stroke-width="7" stroke-linecap="round" '
            'stroke-linejoin="round" fill="none"><path d="M30 62 C14 60 10 40 24 34 C24 20 40 14 50 22 C60 14 76 20 76 34 C90 40 86 60 70 62"/>'
            '<path d="M30 62 V80 H70 V62"/><path d="M30 71 H70"/></g></svg>')
LOGO_EV = ('<svg viewBox="0 0 100 100" aria-hidden="true"><circle cx="50" cy="50" r="48" fill="#3d5f7d"/><circle cx="50" cy="50" r="44" fill="none" '
           'stroke="#f6efe4" stroke-width="1.6"/><circle cx="50" cy="50" r="33" fill="#f6efe4"/><g transform="translate(29 29) scale(.42)" '
           'stroke="#3d5f7d" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" fill="none">'
           '<path d="M18 30h64v12a8 8 0 0 0 0 16v12H18V58a8 8 0 0 0 0-16Z"/><path d="M60 32v6M60 47v6M60 62v6"/></g></svg>')
CSS = ('.asch{display:inline-flex;align-items:center;gap:5px;margin-top:8px;height:30px;padding:0 12px;border-radius:999px;'
       'border:1px solid var(--terra);color:var(--terra-ink);background:var(--terra-soft);font:600 13px/1 var(--sans,system-ui);cursor:pointer;width:max-content}'
       '.asch:hover{background:var(--terra);color:var(--acc-on,#fff)}'
       '.schk{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0;padding:0}'
       '.acard:has(+ .schk:focus-visible) .asch,.awrap:has(.schk:focus-visible) .asch{outline:3px solid #2F7A5C;outline-offset:2px}'
       '.schv{position:fixed;inset:0;z-index:2147483000;background:rgba(20,16,12,.48);display:flex;align-items:flex-end;justify-content:center}'
       '.schv[hidden]{display:none}.schb{background:var(--paper);color:var(--ink);width:100%;max-width:560px;max-height:88vh;overflow:auto;position:relative;'
       'border-radius:20px 20px 0 0;padding:18px 18px calc(18px + env(safe-area-inset-bottom));box-shadow:0 -12px 34px -6px rgba(20,16,12,.3);border-top:4px solid var(--terra)}'
       '@media (min-width:760px){.schv{align-items:center}.schb{border-radius:20px}}'
       '.schb .sk{font:600 11px/1.3 var(--sans);letter-spacing:.12em;text-transform:uppercase;color:var(--terra-ink)}'
       '.schb h3{font:700 24px/1.15 var(--head,var(--sans));letter-spacing:-.02em;margin:4px 50px 10px 0}'
       '.schb .sd{color:var(--mute);line-height:1.55;margin:0 0 10px}.schb .sw{color:var(--terra-ink);font-weight:600}'
       '.schb .sx{position:absolute;right:14px;top:12px}'
       '.schb .sx button{width:40px;height:40px;border-radius:50%;border:1px solid var(--line2);background:var(--paper);color:var(--ink);font-size:22px;cursor:pointer}'
       '.schr{display:flex;align-items:center;gap:12px;padding:11px 12px;margin:8px 0 0;border:1px solid var(--line);border-radius:14px;'
       'text-decoration:none;color:var(--ink);background:var(--paper)}.schr:hover{border-color:var(--terra)}'
       '.schr svg{width:40px;height:40px;flex:none}.schr b{font:700 20px/1 var(--head,var(--sans));min-width:2ch}'
       '.schr span{flex:1;min-width:0;line-height:1.3}.schr small{display:block;color:var(--mute);font-size:12.5px}.schr i{font-style:normal;color:var(--mute)}'
       '.schr.pl{background:var(--terra-soft);border-color:color-mix(in srgb,var(--terra) 40%,var(--line))}'
       '.schc{display:flex;flex-wrap:wrap;gap:6px;margin-top:7px}.schc a{padding:5px 10px;border-radius:999px;border:1px solid var(--line2);'
       'color:var(--ink);text-decoration:none;font-size:13px;font-weight:600}.schc a:hover{border-color:var(--terra)}')
JS = r'''(function(){var CAR=null,v=document.createElement("div");v.className="schv";v.hidden=true;v.setAttribute("role","dialog");v.setAttribute("aria-modal","true");v.setAttribute("aria-labelledby","schtit");
document.body.appendChild(v);var torna=null;v.addEventListener("click",function(e){if(e.target===v||e.target.closest(".sx"))chiudi()});
addEventListener("keydown",function(e){if(e.key==="Escape"&&!v.hidden)chiudi()});
function chiudi(){v.hidden=true;document.documentElement.style.overflow="";if(torna&&torna.focus)try{torna.focus()}catch(x){}}
function carica(){return CAR||(CAR=fetch("scheda.json").then(function(r){return r.json()}))}
function e(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){return{"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]})}
/* Events: solo le città che copre (pagina della città = città e provincia); niente numeri, cambiano ogni settimana */
var EV={BO:["Bologna","https://achevents.com/"],MI:["Milano","https://achevents.com/milano/"],FE:["Ferrara","https://achevents.com/ferrara/"],RA:["Ravenna","https://achevents.com/ravenna/"]};
var TIPO={c:"Comune",v:"Provincia",r:"Regione",z:"Zona tradizionale"},LR=__LOGOREC__,LE=__LOGOEV__,REC="https://achdishes.com/";
function riga(href,logo,num,testo,nota){return '<a class="schr" href="'+href+'" target="_blank" rel="noopener">'+logo+(num?'<b>'+num+'</b>':'')+'<span>'+testo+'<small>'+nota+'</small></span><i aria-hidden="true">↗</i></a>'}
function apri(b,liv,k,n,ps,da){torna=da||null;var sub=(b.querySelector(".as")||{}).textContent||"";carica().then(function(D){
 var pv=((ps[0]&&ps[0].comSlug)||"").split("-").pop().toUpperCase(),rc=D.rc[liv]||{},nr,FR;
 if(liv==="c"){var x=rc[k];nr=x?x[0]:0;FR="comune-"+(x?x[1]:"")}else{var kk=liv==="v"?pv:k;nr=rc[kk]||0;FR=(liv==="v"?"provincia-"+pv.toLowerCase():liv==="r"?"regione-"+k:"zona-"+k)}
 var preg=liv==="r"?k:(D.p2r||{})[pv],npv=(D.pv||{})[pv]||0,nrg=(D.pr||{})[preg]||0,usaPv=liv!=="r"&&liv!=="z"&&npv>0,
     FP="prodotti-"+(usaPv?pv.toLowerCase():preg),NP=usaPv?npv:nrg,DOVEP=liv==="r"?"":usaPv?"della provincia":"della regione "+((D.rn||{})[preg]||"");
 if(liv==="z"&&!preg){var zp=(D.zp||{})[k]||[];preg=(D.p2r||{})[zp[0]];nrg=(D.pr||{})[preg]||0;FP="prodotti-"+preg;NP=nrg;DOVEP="della regione "+((D.rn||{})[preg]||"")}
 var top=ps.slice(0,3).map(function(p){return p.name}).join(", "),d=liv==="r"?(D.rd||{})[k]:liv==="z"?(D.zd||{})[k]:"",nc=new Set(ps.map(function(p){return p.comSlug})).size;
 var gen=((liv==="c"||liv==="v")?(sub||""):"")+". In guida "+ps.length+(ps.length===1?" luogo":" luoghi")+(liv!=="c"?" in "+nc+(nc===1?" comune":" comuni"):"")+(top?"; da non perdere: "+top+".":".");
 var w="https://it.wikipedia.org/w/index.php?search="+encodeURIComponent(n)+"&title=Speciale:Ricerca&go=Vai";
 /* eventi: le città di Events che toccano questo luogo */
 var cit=[];if(liv==="c"||liv==="v"){if(EV[pv])cit=[pv]}else if(liv==="z"){cit=((D.zp||{})[k]||[]).filter(function(p){return EV[p]})}else{cit=Object.keys(EV).filter(function(p){return (D.p2r||{})[p]===k})}
 var evh="";if(cit.length===1){var c=EV[cit[0]],cap=liv==="c"&&n===c[0];evh=riga(c[1],LE,"",cap?"Eventi a "+e(c[0]):"Eventi a "+e(c[0])+" e provincia","spettacoli, mostre, concerti su Events")}
 else if(cit.length>1){evh='<div class="schr">'+LE+'<span>Eventi<small>spettacoli, mostre, concerti su Events</small><span class="schc">'+cit.map(function(p){return '<a href="'+EV[p][1]+'" target="_blank" rel="noopener">'+e(EV[p][0])+' ↗</a>'}).join("")+'</span></span></div>'}
 var h='<div class="sx"><button type="button" aria-label="Chiudi">×</button></div><div class="sk">'+TIPO[liv]+'</div><h3 id="schtit">'+e(n)+'</h3>'
  +(d?'<p class="sd">'+e(d)+'</p>':'')+'<p class="sd">'+e(gen.replace(/^\. /,""))+' <a class="sw" href="'+w+'" target="_blank" rel="noopener">Wikipedia ↗</a></p>'
  +'<a class="schr pl" href="#" data-vai="1"><span><b>'+ps.length+'</b> '+(ps.length===1?"luogo":"luoghi")+' da vedere<small>apri l\'elenco qui in Places</small></span><i aria-hidden="true">›</i></a>'
  +(nr?riga(REC+"#"+FR,LR,nr,nr===1?"ricetta":"ricette","su Ach's Dishes"):"")
  +(NP?riga(REC+"#"+FP,LR,NP,(NP===1?"prodotto tipico":"prodotti tipici")+(DOVEP?" "+e(DOVEP):""),"DOP, IGP, STG, Presìdi su Ach's Dishes"):"")
  +evh;
 v.innerHTML='<div class="schb">'+h+'</div>';v.hidden=false;document.documentElement.style.overflow="hidden";
 v.querySelector("[data-vai]").onclick=function(x){x.preventDefault();torna=null;chiudi();b.click()};v.querySelector(".sx button").focus();});}
window.SCHEDA_AGG=function(b,liv,k,n,ps){if("cvrz".indexOf(liv)<0)return;var ab=b.querySelector(".ab");if(!ab||ab.querySelector(".asch"))return;
 /* tasto visivo dentro la scheda del gruppo (niente ruolo: non si annida un pulsante in un pulsante) */
 var s=document.createElement("span");s.className="asch";s.setAttribute("aria-hidden","true");s.textContent="📋 Scheda";
 s.addEventListener("click",function(x){x.preventDefault();x.stopPropagation();apri(b,liv,k,n,ps,b)});
 s.addEventListener("pointerdown",function(){carica()},{passive:true});ab.appendChild(s);
 /* pulsante vero per tastiera e lettori di schermo, subito dopo la scheda del gruppo */
 var q=document.createElement("button");q.type="button";q.className="schk";q.textContent="Scheda di "+n;
 q.addEventListener("click",function(){apri(b,liv,k,n,ps,q)});q.addEventListener("focus",function(){carica()});
 queueMicrotask(function(){if(b.parentNode)b.after(q)});};})();'''
JS = JS.replace('__LOGOREC__', json.dumps(LOGO_REC)).replace('__LOGOEV__', json.dumps(LOGO_EV))
BLOCCO = f'<!--SCHEDA--><style id="scheda-css">{CSS}</style><script id="scheda-js">{JS}</script><!--/SCHEDA-->'
AGG_A = 'b.onclick=()=>{D.push({g:liv,k,n});'
AGG_B = 'if(window.SCHEDA_AGG)SCHEDA_AGG(b,liv,k,n,ps);\n      '
for nome in ('sorgenti/template.html', 'index.html'):
    P = os.path.join(RAD, nome); t = open(P, encoding='utf-8').read()
    t = re.sub(r'<!--SCHEDA-->.*?<!--/SCHEDA-->', '', t, flags=re.S)
    if AGG_B + AGG_A not in t:
        assert t.count(AGG_A) == 1, nome
        t = t.replace(AGG_A, AGG_B + AGG_A)
    assert t.count('</body>') == 1, nome
    t = t.replace('</body>', BLOCCO + '</body>', 1)
    open(P, 'w', encoding='utf-8').write(t); print(nome, 'ok')
