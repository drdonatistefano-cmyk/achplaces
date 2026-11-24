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
       '.schb .sk span{text-transform:none;letter-spacing:0;font-weight:600;color:var(--mute)}'
       '.schb h4{font:700 12px/1.2 var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--terra-ink);margin:18px 0 8px}'
       '.sst{display:grid;grid-template-columns:repeat(auto-fit,minmax(70px,1fr));gap:8px;margin:4px 0 0}'
       '.sst div{background:var(--bg);border:1px solid var(--line);border-radius:14px;padding:10px 8px;text-align:center}'
       '.sst b{display:block;font:700 22px/1 var(--head,var(--sans));color:var(--ink)}.sst small{display:block;margin-top:4px;font-size:12px;color:var(--mute)}'
       '.sbd{display:flex;flex-wrap:wrap;gap:6px;margin-top:10px}.sbd span{padding:5px 10px;border-radius:999px;background:var(--terra-soft);color:var(--terra-ink);font-weight:700;font-size:13px}'
       '.stop{list-style:none;margin:0;padding:0;border:1px solid var(--line);border-radius:14px;overflow:hidden;background:var(--paper)}'
       '.stop li+li{border-top:1px solid var(--line)}.stop button{display:flex;align-items:center;gap:12px;width:100%;padding:10px 12px;border:0;background:none;text-align:left;color:var(--ink);cursor:pointer;font:inherit}'
       '.stop button:hover{background:var(--bg)}.stop i{font-style:normal;font-size:20px;width:28px;text-align:center}.stop span{flex:1;min-width:0}'
       '.stop b{display:block;font-size:15px;line-height:1.25}.stop small{display:block;color:var(--mute);font-size:12.5px;margin-top:2px}.stop em{font-style:normal;color:var(--mute);font-size:18px}'
       '.scat{display:flex;flex-wrap:wrap;gap:6px}.scat span{padding:5px 10px;border-radius:999px;border:1.5px solid color-mix(in srgb,var(--g) 45%,var(--line));color:color-mix(in srgb,var(--g) 55%,#1A120C);font-weight:700;font-size:13px}'
       '.scat b{color:var(--ink)}'
       '.scta{display:flex;align-items:center;justify-content:center;gap:8px;margin:18px 0 0;height:48px;border-radius:14px;background:var(--terra);color:var(--on,#fff);font-weight:700;font-size:15.5px;text-decoration:none}'
       '.scta:hover{filter:brightness(1.08)}'
       '.stls{display:grid;grid-template-columns:1fr 1fr;gap:8px}'
       '.stl{display:flex;align-items:center;gap:10px;padding:10px;border:1px solid var(--line);border-radius:14px;text-decoration:none;color:var(--ink);background:var(--paper);min-height:56px}'
       '.stl:hover{border-color:var(--terra)}.stl svg{width:34px;height:34px;flex:none}.stl span{min-width:0;line-height:1.25;font-size:14px}.stl b{font-weight:800}'
       '.stl small{display:block;color:var(--mute);font-size:12px}.stl .wk{width:34px;height:34px;flex:none;display:grid;place-items:center;border-radius:50%;border:1px solid var(--line2);font:700 17px/1 Georgia,serif}'
       '@media (max-width:380px){.stls{grid-template-columns:1fr}}'
       '.swk{display:inline-flex;align-items:center;gap:8px;margin:2px 0 12px;padding:7px 12px 7px 8px;border-radius:999px;border:1px solid var(--line2);'
       'background:var(--paper);color:var(--ink);font-weight:700;font-size:14px;text-decoration:none}.swk:hover{border-color:var(--terra)}'
       '.swk span{width:24px;height:24px;display:grid;place-items:center;border-radius:50%;background:var(--bg);font:700 14px/1 Georgia,serif}.swk i{font-style:normal;color:var(--mute)}'
       '.sdov{display:flex;flex-wrap:wrap;gap:6px}.sdov a{padding:6px 11px;border-radius:999px;background:var(--bg);border:1px solid var(--line);'
       'color:var(--ink);text-decoration:none;font-weight:600;font-size:13.5px}.sdov a:hover{border-color:var(--terra)}.sdov b{color:var(--terra-ink)}'
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
     FP="prodotti-"+(usaPv?pv.toLowerCase():preg),NP=usaPv?npv:nrg;
 if(liv==="z"&&!preg){var zp=(D.zp||{})[k]||[];preg=(D.p2r||{})[zp[0]];nrg=(D.pr||{})[preg]||0;FP="prodotti-"+preg;NP=nrg}
 /* 24/11 sera (Stefano: «informazioni minime per un turista», niente peso in più): tutto calcolato dai luoghi già caricati */
 var N=ps.length,nf=function(v){return v.toLocaleString("it-IT")},
     gr=ps.filter(function(p){return p.free===true}).length,co=ps.filter(function(p){return p.indoor}).length,
     un=ps.filter(function(p){return (p.aw||[]).indexOf("unesco")>=0}).length,
     bo=new Set(ps.filter(function(p){return (p.aw||[]).indexOf("borghi")>=0}).map(function(p){return p.comSlug})).size,ar=new Set(ps.filter(function(p){return (p.aw||[]).indexOf("arancione")>=0}).map(function(p){return p.comSlug})).size,
     nc=new Set(ps.map(function(p){return p.comSlug})).size;
 var cats=[];try{var cc={};ps.forEach(function(p){var g=FVG(p)[0];cc[g]=(cc[g]||0)+1});cats=FVM.filter(function(m){return cc[m.k]}).map(function(m){return [m,cc[m.k]]}).sort(function(a,b){return b[1]-a[1]})}catch(x){}
 var cm={};ps.forEach(function(p){var s=p.comSlug;cm[s]=cm[s]||[s,p.com,0];cm[s][2]++});var ncom=Object.values(cm).sort(function(a,b){return b[2]-a[2]}).slice(0,6);
 var top=ps.slice().sort(function(a,b){return (a.rk||1e9)-(b.rk||1e9)}).slice(0,3);
 var desc=liv==="r"?(D.rd||{})[k]:liv==="z"?(D.zd||{})[k]:"";
 var dove=liv==="c"?(sub||""):liv==="v"?(sub||""):liv==="z"?nf(nc)+(nc===1?" comune":" comuni"):(sub||"");
 if(!desc){var FR2={arch:"archeologia",mon:"monumenti",sacro:"luoghi sacri",musei:"musei",natura:"natura",trad:"tradizioni locali"},
   c0=cats.slice(0,2).map(function(x){return FR2[x[0].k]||x[0].l.toLowerCase()}),
   za=(liv==="c"&&window.ZONE_ACH&&ZONE_ACH.c)?(ZONE_ACH.c[k]||(ZONE_ACH.p||{})[pv.toLowerCase()]||[]).map(function(z){return (ZONE_ACH.n||{})[z]||z}):[];
  desc=(c0.length?"Da vedere soprattutto "+c0.join(" e ")+".":"")+(za.length?" Zona tradizionale: "+za.join(", ")+".":"")}
 var w="https://it.wikipedia.org/w/index.php?search="+encodeURIComponent(n)+"&title=Speciale:Ricerca&go=Vai";
 var cit=[];if(liv==="c"||liv==="v"){if(EV[pv])cit=[pv]}else if(liv==="z"){cit=((D.zp||{})[k]||[]).filter(function(p){return EV[p]})}else{cit=Object.keys(EV).filter(function(p){return (D.p2r||{})[p]===k})}
 var tile=function(href,logo,num,lab,sot){return '<a class="stl" href="'+href+'" target="_blank" rel="noopener">'+logo+'<span>'+(num?'<b>'+nf(num)+'</b> ':'')+lab+'<small>'+sot+'</small></span></a>'};
 var tiles=(nr?tile(REC+"#"+FR,LR,nr,nr===1?"ricetta":"ricette","Ach's Dishes"):"")
  +(NP?tile(REC+"#"+FP,LR,NP,NP===1?"prodotto tipico":"prodotti tipici",usaPv?"della provincia":liv==="r"?"DOP, IGP, Presìdi":"della regione"):"")
  +cit.map(function(p){return tile(EV[p][1],LE,0,"Eventi a "+e(EV[p][0]),"su Events")}).join("")
;
 var h='<div class="sx"><button type="button" aria-label="Chiudi">×</button></div>'
  +'<div class="sk">'+TIPO[liv]+(dove?' · <span>'+e(dove)+'</span>':'')+'</div><h3 id="schtit">'+e(n)+'</h3>'
  +'<p class="sd">'+e(desc)+'</p><a class="swk" href="'+w+'" target="_blank" rel="noopener"><span aria-hidden="true">W</span>Storia e curiosità su Wikipedia <i aria-hidden="true">↗</i></a>'
  +'<div class="sst"><div><b>'+nf(N)+'</b><small>'+(N===1?"luogo":"luoghi")+'</small></div><div><b>'+nf(gr)+'</b><small>gratis</small></div><div><b>'+nf(co)+'</b><small>se piove</small></div>'+(liv!=="c"?'<div><b>'+nf(nc)+'</b><small>'+(nc===1?"comune":"comuni")+'</small></div>':'')+'</div>'
  +((un||bo||ar)?'<div class="sbd">'+(un?'<span>🌍 Patrimonio UNESCO</span>':'')
   +(bo?'<span>🏘️ '+(liv==="c"?"Borgo più bello d'Italia":nf(bo)+(bo===1?" Borgo più bello":" Borghi più belli"))+'</span>':'')
   +(ar?'<span>🟠 '+(liv==="c"?"Bandiera arancione":nf(ar)+(ar===1?" Bandiera arancione":" Bandiere arancioni"))+'</span>':'')+'</div>':'')
  +(top.length?'<h4>Da non perdere</h4><ol class="stop">'+top.map(function(p){var g=(FVM.find(function(m){return m.k===FVG(p)[0]})||{});return '<li><button type="button" data-luogo="'+e(p.id)+'"><i aria-hidden="true">'+(g.e||"•")+'</i><span><b>'+e(p.name)+'</b><small>'+e((g.l||"")+(p.sub?" · "+p.sub:"")+(liv!=="c"?" · "+p.com:""))+'</small></span><em aria-hidden="true">›</em></button></li>'}).join("")+'</ol>':'')
  +(cats.length>1?'<h4>Cosa trovi</h4><div class="scat">'+cats.map(function(x){return '<span style="--g:'+x[0].c+'">'+x[0].e+' '+x[0].l+' <b>'+nf(x[1])+'</b></span>'}).join("")+'</div>':'')
  +(liv!=="c"&&ncom.length>1?'<h4>Dove andare</h4><div class="sdov">'+ncom.map(function(x){return '<a href="#'+e(x[0])+'">'+e(x[1])+' <b>'+nf(x[2])+'</b></a>'}).join("")+'</div>':'')
  +(liv==="c"?'<div id="svic"></div>':'')
  +'<a class="scta" href="#" data-vai="1">Vedi '+(N===1?"il luogo":"tutti i "+nf(N)+" luoghi")+' <i aria-hidden="true">›</i></a>'
  +'<h4>Da gustare e da fare</h4><div class="stls">'+tiles+'</div>';
 v.innerHTML='<div class="schb">'+h+'</div>';v.hidden=false;document.documentElement.style.overflow="hidden";
 v.querySelector("[data-vai]").onclick=function(x){x.preventDefault();torna=null;chiudi();b.click()};
 v.querySelectorAll("[data-luogo]").forEach(function(q){q.onclick=function(){var id=q.getAttribute("data-luogo");torna=null;chiudi();if(window.APRI_LUOGO)APRI_LUOGO(id,b);else b.click()}});
 v.querySelector(".sx button").focus();
 if(liv==="c"){(window.VIC||(window.VIC=fetch("vicini.json").then(function(r){return r.json()}))).then(function(V){var l=(V[k]||[]).slice(0,6),box=v.querySelector("#svic");if(!box||!l.length)return;
  box.innerHTML='<h4>Nei dintorni</h4><div class="sdov">'+l.map(function(x){var nm=window.NOME_COM?NOME_COM(x[0]):x[0];return '<a href="#'+e(x[0])+'">'+e(nm)+' <b>'+String(Math.round(x[1])).replace(".",",")+' km</b></a>'}).join("")+'</div>';
  box.querySelectorAll("a").forEach(function(a){a.addEventListener("click",function(){torna=null;chiudi()})})}).catch(function(){})}
 v.querySelectorAll(".sdov a").forEach(function(a){a.addEventListener("click",function(){torna=null;chiudi()})});});}
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
    if 'window.APRI_LUOGO=' in t and 'window.NOME_COM=s=>' not in t:
        t = t.replace('window.APRI_LUOGO=(id,f)=>openSheet(id,f);/*scheda*/', 'window.APRI_LUOGO=(id,f)=>openSheet(id,f);window.NOME_COM=s=>{const c=COMUNI.find(x=>x.slug===s);return c?c.name:s};/*scheda*/')
    if 'window.APRI_LUOGO=' not in t:
        assert t.count('function closeSheet(){') == 1, nome
        t = t.replace('function closeSheet(){', 'window.APRI_LUOGO=(id,f)=>openSheet(id,f);window.NOME_COM=s=>{const c=COMUNI.find(x=>x.slug===s);return c?c.name:s};/*scheda*/\nfunction closeSheet(){')
    if AGG_B + AGG_A not in t:
        assert t.count(AGG_A) == 1, nome
        t = t.replace(AGG_A, AGG_B + AGG_A)
    assert t.count('</body>') == 1, nome
    t = t.replace('</body>', BLOCCO + '</body>', 1)
    open(P, 'w', encoding='utf-8').write(t); print(nome, 'ok')
