
/* ---- scheda Filtri (prototipo): categorie semplificate, regioni multiple, comuni per regione e provincia ---- */
const FVM=[
 {k:"arch",l:"Archeologia",e:"🏺",c:"var(--c-arch)",s:{"Preistoria":"🦴","Nuragici":"🗿","Etruschi":"⚱️","Greci":"🏛️","Fenici":"⛵","Italici":"🛡️","Romani":"🏟️","Tardoantichi":"✝️","Medievali":"🏰","Altro":"❔"}},
 {k:"mon",l:"Monumenti",e:"🏰",c:"var(--c-storia)",s:{"Castelli":"🏰","Fortezze":"🛡️","Mura":"🧱","Torri":"🗼","Palazzi":"🏛️","Ville":"🏡","Piazze":"⛲","Centri":"🏙️","Borghi":"🏘️","Abbandonati":"🏚️","Portici":"🏛️","Teatri":"🎭","Ponti":"🌉","Fontane":"⛲","Monumenti":"🗽","Memoriali":"🕯️"}},
 {k:"sacro",l:"Sacro",e:"⛪",c:"var(--c-sacro)",s:{"Chiese":"⛪","Pievi":"⛪","Basiliche":"⛪","Duomi":"⛪","Abbazie":"📿","Conventi":"📿","Santuari":"🙏","Oratori":"🕍","Battisteri":"💧","Sinagoghe":"🕎","Monti sacri":"⛰️","Complessi":"🔔","Cimiteri":"🕯️"}},
 {k:"musei",l:"Musei",e:"🖼️",c:"var(--c-musei)",s:{"Pittura":"🖼️","Moderna":"🎨","Ceramica":"🏺","Archeologici":"⚱️","Scienza":"🔭","Storia":"📜","Dimore":"🏠","Diocesani":"✝️","Etnografici":"🧺","Tecnica":"⚙️","Militari":"🎖️","Tematici":"🗂️"}},
 {k:"nat",l:"Natura",e:"🌿",c:"var(--c-natura)",s:{"Parchi":"🌲","Riserve":"🦅","Giardini":"🌷","Orti":"🌱","Laghi":"🏞️","Fiumi":"🌊","Cascate":"💦","Spiagge":"🏖️","Montagna":"⛰️","Vulcani":"🌋","Grotte":"🕳️","Geositi":"🪨","Sentieri":"🥾","Panorami":"🌄"}},
 {k:"trad",l:"Tradizioni",e:"🧺",c:"var(--c-locale)",s:{"Mercati":"🧺","Terme":"♨️","Sapori":"🍷","Ceramica":"🏺","Botteghe":"🧵","Motori":"🏎️","Curiosità":"✨"}}];
const FVMM=Object.fromEntries(FVM.map(m=>[m.k,m]));
const FVTX=[["u","🌍","UNESCO"],["g","🆓","Gratis"],["i","☔","Coperti"],["v","🌅","Panorama"],["b","🏘️","Più belli"],["a","🟠","Arancioni"]];
const FVA=[["Preistoria",/preistor|paleolit|neolit|età del (bronzo|ferro)|rupestr|palafitt|dolmen|menhir|neanderthal/],["Nuragici",/nurag|tomb[ae] dei giganti|pozzo sacro|domus de janas/],["Etruschi",/etrusc/],["Greci",/\bgrec|magna grecia|ellenist/],["Fenici",/fenic|punic/],["Italici",/sannit|messap|picen|\bvolsc|camun|dauni|celt|\bitalic/],["Romani",/roman|anfiteatr|domus|\bforo\b|augusto|imperial/],["Tardoantichi",/paleocrist|bizantin|longobard|tardoantic|catacomb/],["Medievali",/medieval|castrum/]];
function fvTag(p){
  const t=(p.name+" "+(p.desc||"")).toLowerCase(),s=p.sub,c=p.cat,h=r=>r.test(t);
  if(s==="Archeologia"){const a=FVA.filter(x=>x[1].test(t)).map(x=>x[0]);return ["arch",a.length?a:["Altro"]];}
  if(c==="storia"){
    if(s==="Castelli e fortezze")return ["mon",[h(/fort|rocca|cittadella|bastion/)&&!h(/castell/)?"Fortezze":"Castelli",...(h(/\bmura|porta /)?["Mura"]:[])]];
    if(s==="Palazzi e ville")return ["mon",[h(/^villa|\bvilla /)?"Ville":"Palazzi"]];
    if(s==="Piazze e centro storico")return ["mon",[h(/piazza/)?"Piazze":"Centri",...(h(/portic/)?["Portici"]:[])]];
    if(s==="Portici UNESCO")return ["mon",["Portici"]];
    if(s==="Monumenti e memoriali")return ["mon",[h(/\bponte/)?"Ponti":h(/fontan/)?"Fontane":h(/memorial|caduti|sacrario|guerra|resistenza|shoah/)?"Memoriali":h(/\barco|porta /)?"Mura":"Monumenti"]];
    return ["mon",[{"Borghi":"Borghi","Torri":"Torri","Teatri storici":"Teatri","Borghi abbandonati":"Abbandonati"}[s]||"Monumenti"]];}
  if(c==="sacro"){
    if(s==="Chiese e pievi")return ["sacro",[h(/oratori/)?"Oratori":h(/\bpieve/)?"Pievi":h(/battister/)?"Battisteri":h(/sinagog/)?"Sinagoghe":"Chiese"]];
    if(s==="Abbazie e monasteri")return ["sacro",[h(/convent/)&&!h(/abbazi/)?"Conventi":"Abbazie"]];
    if(s==="Santuari")return ["sacro",[h(/sacro monte/)?"Monti sacri":"Santuari"]];
    return ["sacro",[{"Cattedrali e duomi":"Duomi","Basiliche":"Basiliche","Complessi monumentali":"Complessi","Cimiteri monumentali":"Cimiteri"}[s]||"Chiese"]];}
  if(c==="musei"){let o;
    if(s==="Tematici")o=[h(/diocesan|arte sacra/)?"Diocesani":h(/etnograf|civiltà contadina|tradizion/)?"Etnografici":h(/militar|guerra|armi/)?"Militari":h(/industria|tecnic|ferrovi|\bauto|moto|macchin/)?"Tecnica":"Tematici"];
    else o=[{"Arte antica":"Pittura","Arte moderna":"Moderna","Archeologici":"Archeologici","Case museo":"Dimore","Scienza e università":"Scienza","Storia della città":"Storia"}[s]||"Tematici"];
    if(s==="Arte antica"||s==="Arte moderna"||h(/pittur|pittor|dipint|pinacotec|quadr|affresc|\btel[ae]\b/))o.push("Pittura");
    if(h(/ceramic|maiolic|porcellan|terracott/))o.push("Ceramica");
    return ["musei",[...new Set(o)]];}
  if(c==="natura"){
    if(s==="Parchi e riserve naturali")return ["nat",[h(/riserva|oasi/)&&!h(/parco/)?"Riserve":"Parchi"]];
    if(s==="Laghi e fiumi")return ["nat",[h(/cascat/)?"Cascate":h(/lago|laghi/)?"Laghi":"Fiumi"]];
    if(s==="Grotte e geositi")return ["nat",[h(/grott/)?"Grotte":"Geositi"]];
    if(s==="Montagna")return ["nat",[h(/vulcan|etna|vesuvio/)?"Vulcani":"Montagna"]];
    if(s==="Giardini botanici")return ["nat",[h(/orto botanic/)?"Orti":"Giardini"]];
    return ["nat",[{"Parchi urbani":"Giardini","Colline e sentieri":"Sentieri","Paesaggi e zone d'interesse":"Panorami","Mare e spiagge":"Spiagge"}[s]||"Panorami"]];}
  const o=[{"Mercati storici":"Mercati","Terme":"Terme","Enogastronomia":"Sapori","Artigianato":"Botteghe","Motori":"Motori","Angoli nascosti":"Curiosità"}[s]||"Curiosità"];
  if(h(/ceramic|maiolic/))o.push("Ceramica");return ["trad",o];}
const FV={regs:new Set(),q:"",open:"arch",sel:{},tx:new Set(),lim:40,com:null,all:false,ready:false};
function fvInit(){if(FV.ready)return;for(const c of COMUNI)for(const p of c.places){const [g,s]=fvTag(p);p._g=g;p._s=s;p._f=(p.unesco?"u":"")+(p.free===true?"g":"")+(p.indoor?"i":"")+(p.view?"v":"")+((c.aw||[]).includes("borghi")?"b":"")+((c.aw||[]).includes("arancione")?"a":"");p._c=c;}FV.ready=true;}
const fvAny=()=>Object.values(FV.sel).some(s=>s.size);
const fvMatch=p=>{if(!fvAny())return true;const s=FV.sel[p._g];return !!(s&&s.size&&p._s.some(x=>s.has(x)));};
const fvTx=p=>[...FV.tx].every(f=>p._f.includes(f));
const fvNorm=s=>s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"");
function fvBase(useReg=true){const q=fvNorm(FV.q);const out=[];for(const c of COMUNI){if(useReg&&FV.regs.size&&!FV.regs.has(c.regione))continue;for(const p of c.places)if(fvTx(p)&&(!q||fvNorm(p.name+" "+c.name).includes(q)))out.push(p);}return out;}
function fvRender(){fvInit();
  const v=$("view-filtri");
  if(FV.com){fvDetail();return;}
  const B=fvBase(),R=B.filter(fvMatch),Bn=fvBase(false).filter(fvMatch);
  const rc={};for(const p of Bn)rc[p._c.regione]=(rc[p._c.regione]||0)+1;
  const regs=[...new Set(COMUNI.map(c=>c.regione))].sort((a,b)=>REGN(a).localeCompare(REGN(b),"it"));
  const m=FVMM[FV.open],sel=m&&(FV.sel[m.k]||new Set());
  const chips=[];for(const k in FV.sel)for(const s of FV.sel[k])chips.push([k,s]);
  // comuni raggruppati per regione e provincia
  const by=new Map();for(const p of R){const c=p._c;let o=by.get(c.slug);if(!o){o={c,n:0,k:{}};by.set(c.slug,o);}o.n++;
    if(fvAny()){for(const s of p._s)if(FV.sel[p._g]&&FV.sel[p._g].has(s)){const kk=p._g+"|"+s;o.k[kk]=(o.k[kk]||0)+1;}}else o.k[p._g]=(o.k[p._g]||0)+1;}
  const L=[...by.values()].sort((a,b)=>REGN(a.c.regione).localeCompare(REGN(b.c.regione),"it")||a.c.provName.localeCompare(b.c.provName,"it")||a.c.name.localeCompare(b.c.name,"it"));
  let html=`<div class="fv-h"><h1>Cosa <em>cerchi</em>?</h1></div><p class="fv-lead">Scegli regioni e categorie, poi tocca un comune per vederne i luoghi.</p>
  <div class="fv-lab">Regioni${FV.regs.size?`<button class="fv-clr" data-fv="regall">Tutte</button>`:""}</div>
  <div class="fv-row"><button class="fv-rc${FV.regs.size?"":" on"}" data-fv="regall">Tutte <i>${Bn.length}</i></button>${regs.map(r=>`<button class="fv-rc${FV.regs.has(r)?" on":""}" data-reg="${r}">${esc(REGN(r))} <i>${rc[r]||0}</i></button>`).join("")}</div>
  <input class="fv-q" id="fv-q" type="search" placeholder="Cerca un comune o un luogo" value="${esc(FV.q)}" autocomplete="off">
  <div class="fv-lab">Categorie</div>
  <div class="fv-mac">${FVM.map(x=>{const n=B.filter(p=>p._g===x.k).length,c=(FV.sel[x.k]||new Set()).size;return `<button class="fv-m${FV.open===x.k?" on":""}" style="--mc:${x.c}" data-mac="${x.k}">${c?`<span class="dot">${c}</span>`:""}<span class="e">${x.e}</span><span class="t"><b>${x.l}</b><small>${n}</small></span></button>`;}).join("")}</div>
  ${m?`<div class="fv-p" style="--mc:${m.c}"><h3>${m.e} ${m.l} <small>scegline una o più</small>${sel.size?`<button data-clr="${m.k}">Togli</button>`:""}</h3><div class="fv-ch">${Object.entries(m.s).map(([s,e])=>{const n=B.filter(p=>p._g===m.k&&p._s.includes(s)).length;return `<button class="fv-c${sel.has(s)?" on":""}${n?"":" zero"}" data-sub="${esc(s)}">${e} ${s} <i>${n}</i></button>`;}).join("")}</div></div>`:""}
  <div class="fv-lab">Filtri</div>
  <div class="fv-tx">${FVTX.map(([k,e,l])=>`<button class="fv-t${FV.tx.has(k)?" on":""}" data-tx="${k}">${e} ${l}</button>`).join("")}</div>
  <div class="fv-sum"><b>${L.length}</b><span>comuni<br>${R.length} luoghi${chips.length?" · "+chips.map(([k,s])=>FVMM[k].s[s]+" "+s).join(", "):""}</span>${(chips.length||FV.tx.size||FV.regs.size||FV.q)?`<button data-fv="reset">Azzera</button>`:""}</div>`;
  if(!L.length)html+=`<div class="fv-empty">Nessun comune con questi filtri.<br>Prova a toglierne qualcuno.</div>`;
  else{let shown=0,curR=null,curP=null;
    const rn={},pn={};for(const o of L){rn[o.c.regione]=(rn[o.c.regione]||0)+1;const pk=o.c.regione+"|"+o.c.prov;pn[pk]=(pn[pk]||0)+1;}
    for(const o of L){if(shown>=FV.lim)break;const c=o.c;
      if(c.regione!==curR){if(curR!==null)html+=`</section>`;curR=c.regione;curP=null;html+=`<section class="fv-reg"><h2>${esc(REGN(c.regione))} <small>${rn[c.regione]} comuni</small></h2>`;}
      if(c.prov!==curP){curP=c.prov;html+=`<div class="fv-pv">${esc(provLong(c))} <i>· ${pn[c.regione+"|"+c.prov]}</i></div>`;}
      const aw=(c.aw||[]).map(a=>({unesco:"UNESCO",borghi:"Borghi",arancione:"Arancione",creative:"Creativa"}[a])).filter(Boolean).map(a=>`<span class="fv-aw">${a}</span>`).join("");
      const ks=Object.entries(o.k).map(([kk,n])=>{const [k,s]=kk.split("|");const mm=FVMM[k];return `<span class="fv-k" style="--mc:${mm.c}">${s?mm.s[s]:mm.e} ${n}${s?" "+s:""}</span>`;}).join("");
      html+=`<button class="fv-co" data-com="${c.slug}"><span class="bd"><h4>${esc(c.name)}${aw}</h4><span class="fv-cats">${ks}</span></span><span class="fv-n"><b>${o.n}</b><small>${o.n===1?"luogo":"luoghi"}</small></span><span class="fv-chev">›</span></button>`;shown++;}
    html+=`</section>`;if(L.length>FV.lim)html+=`<button class="fv-more" data-fv="more">Mostra altri ${Math.min(40,L.length-FV.lim)} comuni di ${L.length-FV.lim}</button>`;}
  html+=`<p class="fv-note">Prototipo: tipi e civiltà sono assegnati in automatico dalle descrizioni prese dalle fonti ufficiali e vanno controllati prima della versione definitiva.</p>`;
  v.innerHTML=html;
  const q=$("fv-q");q.oninput=()=>{FV.q=q.value;FV.lim=40;const pos=q.selectionStart;fvRender();const n=$("fv-q");n.focus();try{n.setSelectionRange(pos,pos);}catch(e){}};
}
function fvDetail(){
  const c=COMUNI.find(x=>x.slug===FV.com);if(!c){FV.com=null;return fvRender();}
  const all=c.places.slice().sort((a,b)=>(a.rk||1e9)-(b.rk||1e9));
  const filt=all.filter(p=>fvMatch(p)&&fvTx(p));
  const list=FV.all||filt.length===all.length?all:filt;
  CUR=all;list.forEach(p=>p._sel=0);
  const v=$("view-filtri");
  v.innerHTML=`<button class="fv-back" data-fv="back">‹ Comuni</button>
  <div class="fv-dh"><div class="w">${esc(provLong(c))} · ${esc(REGN(c.regione))}</div><h1>${esc(c.name)}</h1>${c.lede?`<p>${esc(c.lede)}</p>`:""}</div>
  <div class="fv-dbar">${filt.length<all.length?`<button class="${FV.all?"":"on"}" data-fv="dfilt">Filtrati · ${filt.length}</button><button class="${FV.all?"on":""}" data-fv="dall">Tutti · ${all.length}</button>`:`<span class="info">${all.length} luoghi</span>`}<a class="fv-rc" style="margin-left:auto;text-decoration:none" href="#${c.slug}">Apri nella Guida ›</a></div>
  <div class="grid" id="fv-grid"></div>`;
  const g=$("fv-grid");for(const p of list)g.appendChild(cardEl(p));
}
$("view-filtri").addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;const d=b.dataset;
  if(d.reg){FV.regs.has(d.reg)?FV.regs.delete(d.reg):FV.regs.add(d.reg);FV.lim=40;}
  else if(d.mac)FV.open=FV.open===d.mac?null:d.mac;
  else if(d.sub){const k=FV.open;(FV.sel[k]=FV.sel[k]||new Set());FV.sel[k].has(d.sub)?FV.sel[k].delete(d.sub):FV.sel[k].add(d.sub);FV.lim=40;}
  else if(d.clr)FV.sel[d.clr]=new Set();
  else if(d.tx){FV.tx.has(d.tx)?FV.tx.delete(d.tx):FV.tx.add(d.tx);FV.lim=40;}
  else if(d.com){FV.com=d.com;FV.all=false;FV.y=window.scrollY;fvRender();window.scrollTo(0,0);return;}
  else if(d.fv==="regall")FV.regs.clear();
  else if(d.fv==="more")FV.lim+=40;
  else if(d.fv==="reset"){FV.regs.clear();FV.sel={};FV.tx.clear();FV.q="";}
  else if(d.fv==="back"){FV.com=null;fvRender();window.scrollTo(0,FV.y||0);return;}
  else if(d.fv==="dall")FV.all=true;
  else if(d.fv==="dfilt")FV.all=false;
  else return;
  fvRender();});
