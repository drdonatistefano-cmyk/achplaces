/* 13/11/2026 – Ach's Places Guide in English.
   Loaded only when the page is in English (window.ACH_LANG==="en", decided by the small script at the top of the page).
   It translates the page in place, without touching the code that draws it:
   - interface texts: exact dictionary (D) and a few patterns with numbers and names (PAT);
   - texts of places and towns: translation memory per province (en.<prov>.<hash>.json) and for the long interface
     texts (en.ui.<hash>.json), looked up by the fingerprint of the Italian text (same as traduci/estrai.py).
   The texts were translated automatically with Opus-MT it-en (Helsinki-NLP, CC BY 4.0), an open model run
   on GitHub Actions: no third-party service is called by the page. */
(function(){
"use strict";
const W=window;if(W.ACH_EN)return;
const D=/*DIZ*/{};
const MEM=new Map();
function enk(t){let h=0x811c9dc5;for(let i=0;i<t.length;i++){h^=t.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}return h.toString(36)+"."+t.length;}
const MESI={gennaio:"January",febbraio:"February",marzo:"March",aprile:"April",maggio:"May",giugno:"June",luglio:"July",agosto:"August",settembre:"September",ottobre:"October",novembre:"November",dicembre:"December"};
const num=s=>s.replace(/(\d),(\d)/g,"$1.$2");
const PL=(n,a,b)=>(+String(n).replace(/\./g,"")===1?a:b);
function T(s){/* traduzione di una parte (nome di categoria, tipo, regione...) */const v=D[s];return v===undefined?s:v;}
const PAT=[
 [/^(\d[\d.]*) comuni · (\d[\d.]*) luoghi$/,(m,a,b)=>`${a} ${PL(a,"town","towns")} · ${b} ${PL(b,"place","places")}`],
 [/^(\d[\d.]*) province · (\d[\d.]*) luoghi$/,(m,a,b)=>`${a} ${PL(a,"province","provinces")} · ${b} ${PL(b,"place","places")}`],
 [/^(\d[\d.]*) provincia · (\d[\d.]*) luoghi$/,(m,a,b)=>`${a} province · ${b} ${PL(b,"place","places")}`],
 [/^([\d.,]+) km · (\d+) luogh[io]$/,(m,a,b)=>`${num(a)} km · ${b} ${PL(b,"place","places")}`],
 [/^(\d[\d.]*) (luoghi|luogo) su (\d[\d.]*)$/,(m,a,b,c)=>`${a} ${PL(a,"place","places")} of ${c}`],
 [/^(\d[\d.]*) comuni$/,(m,a)=>`${a} ${PL(a,"town","towns")}`],
 [/^(\d[\d.]*) (luoghi|luogo)$/,(m,a)=>`${a} ${PL(a,"place","places")}`],
 [/^Mostra (\d[\d.]*) (luoghi|luogo)$/,(m,a)=>`Show ${a} ${PL(a,"place","places")}`],
 [/^Mostra altri (\d[\d.]*) di (\d[\d.]*)$/,(m,a,b)=>`Show ${a} more of ${b}`],
 [/^Tutti i (\d[\d.]*) luoghi$/,(m,a)=>`All ${a} places`],
 [/^· n\. (\d+) in Italia$/,(m,a)=>`· no. ${a} in Italy`],
 [/^n\. (\d+) in Italia$/,(m,a)=>`no. ${a} in Italy`],
 [/^(Dati|Fonti) verificat[ie] il (\d+) (\w+) (\d{4})$/,(m,a,g,me,y)=>`${a==="Dati"?"Data":"Sources"} checked on ${g} ${MESI[me]||me} ${y}`],
 [/^Verificato il (\d+) (\w+) (\d{4})$/,(m,g,me,y)=>`Checked on ${g} ${MESI[me]||me} ${y}`],
 [/^(Categoria|Tipo|Ideale per|Ingresso|Tempo): (.+), (\d[\d.]*) luoghi$/,(m,a,b,c)=>`${T(a)}: ${T(b)}, ${c} places`],
 [/^Biglietti su (Tiqets|GetYourGuide): (.+)$/,(m,a,b)=>`Tickets on ${a}: ${b}`],
 [/^Biglietti ufficiali: (.+)$/,(m,a)=>`Official tickets: ${a}`],
 [/^Biglietto: vedi la scheda di (.+)$/,(m,a)=>`Ticket: see the page of ${a}`],
 [/^Tariffe sul sito ufficiale: (.+)$/,(m,a)=>`Prices on the official website: ${a}`],
 [/^Ingresso gratuito: vedi la scheda di (.+)$/,(m,a)=>`Free entry: see the page of ${a}`],
 [/^Foto di (.+) su Google Immagini$/,(m,a)=>`Photos of ${a} on Google Images`],
 [/^Cerca (.+) su Wikipedia$/,(m,a)=>`Search ${a} on Wikipedia`],
 [/^Come arrivare a (.+)$/,(m,a)=>`Directions to ${a}`],
 [/^Togli filtro (.+)$/,(m,a)=>`Remove filter ${tr(a)}`],
 [/^Azzera tutti i filtri \((\d+) attivi\)$/,(m,a)=>`Clear all filters (${a} active)`],
 [/^Sei vicino a (.+)$/,(m,a)=>`You are near ${T(a)}`],
 [/^Posizione trovata \(precisione circa (\d+) m\)\.$/,(m,a)=>`Location found (accuracy about ${a} m).`],
 [/^(.+) \(([A-Z]{2})\)$/,(m,a,b)=>D[a]!==undefined?`${D[a]} (${b})`:null],
 [/^([\d.,]+)-([\d.,]+) (h|ore)$/,(m,a,b)=>`${num(a)}-${num(b)} h`],
 [/^(\d+) min$/,(m,a)=>`${a} min`],
 [/^(\d+)-(\d+) minuti$/,(m,a,b)=>`${a}-${b} minutes`],
 [/^(\d+) minuti$/,(m,a)=>`${a} minutes`],
 [/^(\d+) or[ae]$/,(m,a)=>`${a} ${a==="1"?"hour":"hours"}`],
 [/^(\d+) giorni$/,(m,a)=>`${a} days`],
 [/^(\d[\d.]*) luoghi in (\d[\d.]*) comuni di (\d+) province, in (.+)$/,(m,a,b,c,l)=>`${a} places in ${b} towns across ${c} provinces, in ${l.replace(/\.$/,"").split(/, | e /).map(T).join(", ")}`],
 [/^Monumenti, chiese, musei, natura e angoli nascosti del comune di (.+) \((Città metropolitana di|provincia di) (.+)\), con biglietti, orari e come arrivare\. Ogni scheda cita le sue fonti\.$/,(m,a,k,p)=>`Monuments, churches, museums, nature and hidden corners of ${T(a)} (${k==="provincia di"?"province of":"metropolitan city of"} ${T(p)}), with tickets, opening hours and directions. Every entry cites its sources.`],
 [/^Foto: (.+)$/,(m,a)=>`Photo: ${a}`],
 [/^(.+?)(\s*[↗›»→]+)$/,(m,a,b)=>{const x=tr(a);return x!==a?x+b:null;}]
];
/* prefissi: emoji o simboli davanti al testo (🗺️ Lazio, 📍 Bologna) */
const PRE=/^([\p{Extended_Pictographic}\p{Emoji_Presentation}️‍✕✓↗·•–—\s]+)(.+)$/u;
const CACHE=new Map();
function tr(s){
  if(!s)return s;
  let v=D[s];if(v!==undefined)return v;
  v=CACHE.get(s);if(v!==undefined)return v;
  v=tr0(s);if(CACHE.size>30000)CACHE.clear();CACHE.set(s,v);return v;
}
function tr0(s){
  const m=MEM.get(enk(s));if(m)return m;
  for(const [re,f] of PAT){const r=s.match(re);if(r){const o=f(...r);if(o!=null)return o;}}
  const p=s.match(PRE);if(p){const x=tr(p[2]);if(x!==p[2])return p[1]+x;}
  if(s.includes(" · ")){const parts=s.split(" · ");const t=parts.map(tr);if(t.some((x,i)=>x!==parts[i]))return t.join(" · ");}
  const q=s.match(/^(.+?)([.:,;]\s*)$/);if(q){const x=tr(q[1]);if(x!==q[1])return x+q[2];}
  return s;
}
function provDi(id){if(!id)return;const pr=id.includes("--")?id.split("--")[0].split("-").pop():"bo";if(pr&&pr.length===2)caricaMem(pr.toUpperCase());}
const ATTR=["placeholder","aria-label","title","alt"];
const SKIP=new Set(["SCRIPT","STYLE","TEXTAREA","CODE","PRE"]);
const FATTO=new WeakMap(),FATTOA=new WeakMap();/* cio' che ho scritto io non si ritraduce (niente giri infiniti) */
function testo(n){
  const v=n.nodeValue;if(!v||v.length<1||FATTO.get(n)===v)return;
  const t=v.trim();if(!t||!/[A-Za-zÀ-ÿ]/.test(t))return;
  const x=tr(t);if(x!==t){const nv=v.replace(t,x);FATTO.set(n,nv);n.nodeValue=nv;}
}
function attr(e){let m=FATTOA.get(e);for(const a of ATTR){const v=e.getAttribute&&e.getAttribute(a);if(v){if(m&&m[a]===v)continue;const x=tr(v.trim());if(x!==v.trim()){if(!m){m={};FATTOA.set(e,m);}m[a]=x;e.setAttribute(a,x);}}}}
function giro(root){
  if(!root)return;
  if(root.nodeType===3){const p=root.parentNode;if(p&&!SKIP.has(p.nodeName)&&!(p.closest&&p.closest("[data-noen]")))testo(root);return;}
  if(root.nodeType!==1||SKIP.has(root.nodeName))return;
  if(root.closest&&root.closest("[data-noen]"))return;
  attr(root);
  /* schede della Guida: la provincia si legge dall'identificativo del luogo (comune-pr--luogo) */
  const pid=root.getAttribute&&root.getAttribute("data-pid");if(pid)provDi(pid);
  for(const e of root.querySelectorAll("[data-pid]"))provDi(e.getAttribute("data-pid"));
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT,{acceptNode:n=>n.nodeType===1?(SKIP.has(n.nodeName)||n.hasAttribute("data-noen")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_SKIP):NodeFilter.FILTER_ACCEPT});
  let n;while(n=w.nextNode())testo(n);
  for(const e of root.querySelectorAll("[placeholder],[aria-label],[title],[alt]"))attr(e);
}
/* giro su tutta la pagina a pezzi di circa 12 ms, per non bloccare (prima i nodi in alto, cioe' quelli che si vedono) */
let gen=0;
function giroTutto(fine){const g=++gen;let fatti=0;
  const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT,{acceptNode:n=>n.nodeType===1?(SKIP.has(n.nodeName)||n.hasAttribute("data-noen")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT):NodeFilter.FILTER_ACCEPT});
  const pezzo=()=>{if(g!==gen)return;const t0=performance.now();let n,k=0;
    while((k++&31)||performance.now()-t0<10){n=w.nextNode();if(!n)break;fatti++;
      if(n.nodeType===3)testo(n);else{if(n.hasAttribute("data-pid"))provDi(n.getAttribute("data-pid"));if(n.hasAttributes())attr(n);}}
    if(fine&&(fatti>600||!n)){const f=fine;fine=null;f();}
    if(n)setTimeout(pezzo,0);};
  pezzo();}
let coda=new Set(),pronto=false;
function svuota(){const c=coda;coda=new Set();pronto=false;for(const n of c)if(n.isConnected)giro(n);}
const MO=new MutationObserver(list=>{
  for(const r of list){
    if(r.type==="characterData")coda.add(r.target);
    else if(r.type==="attributes")coda.add(r.target);
    else for(const n of r.addedNodes)coda.add(n);
  }
  if(!pronto){pronto=true;requestAnimationFrame(svuota);}/* prima del disegno, fuori dal compito della pagina */
});
/* memoria delle traduzioni, per provincia */
const MAN=W.ACH_EN_MAN||{};const caricate={},attese={};
function caricaMem(chiave){
  const n=chiave==="ui"?MAN.ui:(MAN.det||{})[chiave];if(!n||caricate[chiave])return attese[chiave]||Promise.resolve();
  caricate[chiave]=1;
  return attese[chiave]=fetch(n).then(r=>r.ok?r.json():null).then(j=>{if(!j)return;for(const k in j)MEM.set(k,j[k]);CACHE.clear();
    requestAnimationFrame(()=>giroTutto());}).catch(()=>{});
}
/* quando la pagina scarica le schede di una provincia, scarico anche le sue traduzioni */
const f0=W.fetch.bind(W);
W.fetch=function(u,o){try{const s=typeof u==="string"?u:(u&&u.url)||"";const m=s.match(/(?:^|\/)det\.([a-z]{2})\.[0-9a-f]{10}\.json/);if(m)caricaMem(m[1].toUpperCase());}catch(e){}return f0(u,o);};
/* ricerca in inglese: la pagina legge la casella di ricerca gia' tradotta in italiano (castle -> castell, Florence -> firenze);
   chi guarda continua a vedere le parole che ha scritto */
const QF=[["old town","centro storico"],["historic centre","centro storico"],["historic center","centro storico"],["aosta valley","valle d'aosta"],["south tyrol","alto adige"],["leaning tower","torre pendente"]];
const QC={rome:"roma",florence:"firenze",venice:"venezia",naples:"napoli",milan:"milano",turin:"torino",genoa:"genova",padua:"padova",mantua:"mantova",syracuse:"siracusa",tuscany:"toscana",sicily:"sicilia",sardinia:"sardegna",lombardy:"lombardia",piedmont:"piemonte",apulia:"puglia",leghorn:"livorno",the:"",of:"",and:"",a:"",in:""};
const QS=[["amphitheat","anfiteatr"],["castle","castell"],["fortress","fortezz"],["fort","fort"],["tower","torr"],["wall","mura"],["palace","palazz"],["square","piazz"],["church","chies"],["cathedral","duomo"],["basilica","basilic"],["abbey","abbazi"],["monaster","monaster"],["convent","convent"],["sanctuar","santuari"],["chapel","cappell"],["baptist","battister"],["museum","muse"],["galler","galleri"],["painting","pittur"],["archaeolog","archeolog"],["archeolog","archeolog"],["ruin","rovin"],["roman","roman"],["etruscan","etrusc"],["greek","grec"],["mediev","mediev"],["theat","teatr"],["bridge","ponte"],["fountain","fontan"],["garden","giardin"],["botanic","botanic"],["park","parc"],["reserve","riserv"],["lake","lag"],["river","fium"],["waterfall","cascat"],["beach","spiagg"],["sea","mare"],["island","isol"],["mountain","mont"],["volcan","vulcan"],["cave","grott"],["trail","sentier"],["path","sentier"],["hik","sentier"],["view","panoram"],["panoram","panoram"],["village","borg"],["market","mercat"],["spa","term"],["thermal","term"],["cemeter","cimiter"],["lighthouse","faro"],["harbo","port"],["library","bibliotec"],["science","scienz"],["universit","universit"],["wine","vin"],["cheese","formagg"],["mosaic","mosaic"],["fresco","affresc"],["synagog","sinagog"],["villa","vill"],["gate","porta"],["arch","arco"],["column","colonn"],["temple","tempi"],["necropol","necropol"],["tomb","tomb"],["catacomb","catacomb"]];
function qIt(v){if(!v)return v;let s=" "+v.toLowerCase()+" ";for(const [a,b] of QF)s=s.split(" "+a+" ").join(" "+b+" ");
  return s.trim().split(/\s+/).map(w=>{if(w in QC)return QC[w];for(const [a,b] of QS)if(w.startsWith(a))return b;return w;}).filter(Boolean).join(" ");}
function ricercaInglese(el){if(!el||el.__en)return;el.__en=1;const P=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value");
  try{Object.defineProperty(el,"value",{configurable:true,get(){return qIt(P.get.call(this));},set(x){P.set.call(this,x);}});}catch(e){}}
function cercaCaselle(){for(const id of ["q","mq","qs"])ricercaInglese(document.getElementById(id));for(const e of document.querySelectorAll('input[type="search"]'))ricercaInglese(e);}
W.ACH_EN={tr,giro,carica:caricaMem,enk,MEM,D,qIt};
W.ENL=s=>tr(s);
let agganciato=false;
function aggancia(){/* Guida: anche le province lette dalla memoria del telefono (senza fetch) */
  if(agganciato)return;try{if(typeof caricaDet!=="function")return;}catch(e){return;}
  agganciato=true;const o=caricaDet;
  try{caricaDet=function(pr){if(pr)caricaMem(String(pr).toUpperCase());return o.apply(this,arguments);};}catch(e){}
  try{for(const k of Object.keys(DETOK).concat(Object.keys(DETP)))caricaMem(String(k).toUpperCase());}catch(e){}
}
function avvia(){
  cercaCaselle();document.addEventListener("DOMContentLoaded",cercaCaselle);
  aggancia();document.addEventListener("DOMContentLoaded",aggancia);W.addEventListener("load",aggancia);
  document.documentElement.lang="en";
  if(document.title)document.title=tr(document.title);
  MO.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTR});
  giroTutto(()=>document.documentElement.classList.remove("en-wait"));
  try{const f=document.querySelector("footer")||document.querySelector(".foot");if(f&&!document.getElementById("en-nota")){const p=document.createElement("p");p.id="en-nota";p.setAttribute("data-noen","");p.style.cssText="font-size:12px;opacity:.75;margin:10px 0 0";p.textContent="English version: the descriptions are machine-translated from the original Italian texts (Opus-MT, an open model). Place names stay in Italian, as you will find them on site.";f.appendChild(p);}}catch(e){}
}
caricaMem("ui");caricaMem("BO");
if(document.body)avvia();else document.addEventListener("DOMContentLoaded",avvia);
})();
