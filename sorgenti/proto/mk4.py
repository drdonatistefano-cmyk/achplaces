t=open('v4_tail.html').read()
def R(a,b):
    global t
    assert a in t,a[:70]; t=t.replace(a,b,1)
R("const st={regs:new Set(),q:'',open:'arch',sel:{},tx:new Set(),lim:40,com:null,all:false,y:0};",
"""const st={regs:new Set(),prov:null,grp:'c',q:'',open:'arch',sel:{},tx:new Set(),lim:40,com:null,all:false,y:0,hist:[]};
P.forEach((p,i)=>p._i=i);
const AREE={nord:['piemonte','valle-d-aosta','lombardia','trentino-alto-adige','veneto','friuli-venezia-giulia','liguria','emilia-romagna'],centro:['toscana','umbria','marche','lazio'],sud:['abruzzo','molise','campania','puglia','basilicata','calabria','sicilia','sardegna']};
const AL={nord:'Nord',centro:'Centro',sud:'Sud e Isole'},AE={nord:'🏔️',centro:'🏛️',sud:'🌊'};
const AREA=r=>AREE.nord.includes(r)?'nord':AREE.centro.includes(r)?'centro':'sud';
const GR=[['p','📍','Luoghi'],['c','🏘️','Comuni'],['v','🗺️','Province'],['r','🧭','Regioni'],['a','🇮🇹','Nord·Centro·Sud']];
const GN={p:'luoghi',c:'comuni',v:'province',r:'regioni',a:'Nord · Centro · Sud'};
const nFil=()=>st.regs.size+(st.prov?1:0)+Object.values(st.sel).reduce((a,s)=>a+s.size,0)+st.tx.size+(st.q?1:0);
const snap=()=>({regs:[...st.regs],prov:st.prov,grp:st.grp,y:window.scrollY});
function drill(f){st.hist.push(snap());f();st.lim=40;history.pushState({d:1},'');renderF();window.scrollTo(0,listTop())}
function undrill(){const s=st.hist.pop();if(!s)return;st.regs=new Set(s.regs);st.prov=s.prov;st.grp=s.grp;st.lim=40;renderF();window.scrollTo(0,s.y)}
const listTop=()=>{const e=$('grp');return e?Math.max(0,e.getBoundingClientRect().top+window.scrollY-120):0};
const pvName=c=>c[1]===RG(c[2])?c[1]:'Provincia di '+c[1];""")
R("return(!useReg||!st.regs.size||st.regs.has(c[2]))&&",
  "return(!useReg||((!st.regs.size||st.regs.has(c[2]))&&(!st.prov||st.prov===c[2]+'|'+c[1])))&&")
R(" let h=`<div class=\"brand\">"," const SS=anySel();\n let h=`<div class=\"brand\">")
LIST=open('list4.js').read()
R("<<LIST>>",LIST)
R("function renderL(){","""function cardHTML(p,showC){const m=MM[p[2]],c=C[p[1]];return `<article class="card" style="${cv(p[2])}"><button class="main" data-p="${p._i}"><div class="top"><span class="gtag">${m.e} ${m.l}</span><span class="stag">${p[3].map(s=>(m.s[s]||'')+' '+s).join(' · ')}</span></div><h3>${esc(p[0])}</h3>${showC?`<div class="cn">📍 ${esc(c[0])} · ${esc(c[1])}</div>`:''}<p>${esc(p[5])}</p><div class="meta">${tagsOf(p)}</div></button><div class="foot"><a class="cb" href="https://www.google.com/search?tbm=isch&q=${encodeURIComponent(p[0]+' '+c[0])}" target="_blank" rel="noopener">📷 Foto</a>${showC?`<button class="cb" data-c="${p[1]}">🏘️ ${esc(c[0])}</button>`:''}<button class="cb pri" data-p="${p._i}">Apri ›</button></div></article>`}
function renderL(){""")
i=t.index(' <div class="grid">${list.map(');j=t.index("}).join('')}</div>`;",i)+len("}).join('')}</div>`;")
t=t[:i]+""" <div class="grid">${list.map(p=>cardHTML(p,false)).join('')}</div>`;"""+t[j:]
R("""$('vL').innerHTML=`<div class="hero">""","""$('vL').innerHTML=`<div class="lbar"><button class="back" data-a="tolist">‹ Torna all'elenco</button>${nFil()?`<button class="rst" data-a="resetL">↺ Azzera filtri</button>`:''}</div><div class="hero">""")
R("function tab(t){","""function renderBar(){const n=nFil(),b=$('fbar');if(!n){b.innerHTML='';b.classList.remove('on');return}
 const bits=[];if(st.regs.size)bits.push([...st.regs].map(RG).join(', '));if(st.prov)bits.push(st.prov.split('|')[1]);for(const k in st.sel)for(const s of st.sel[k])bits.push(s);for(const k of st.tx)bits.push(TX.find(x=>x[0]===k)[2]);if(st.q)bits.push('«'+st.q+'»');
 b.innerHTML=`<span class="fn">${n}</span><span class="ft"><small>Filtri attivi</small>${esc(bits.join(' · '))}</span><button class="rst" data-a="${$('vL').classList.contains('on')?'resetL':'reset'}">↺ Azzera</button>`;b.classList.add('on')}
function tab(t){""")
R("if(t==='L')window.scrollTo(0,0);else window.scrollTo(0,st.y||0)}","if(t==='L')window.scrollTo(0,0);else window.scrollTo(0,st.y||0);renderBar()}")
R("function setTabL(){","function goList(){if(history.state&&history.state.v==='L')history.back();else tab('F')}\nfunction setTabL(){")
R(" if(d.c){st.y=window.scrollY;st.com=+d.c;st.all=false;renderL();setTabL();tab('L');return}",
""" if(d.c){closeSheet();if(!$('vL').classList.contains('on'))st.y=window.scrollY;st.com=+d.c;st.all=false;renderL();setTabL();tab('L');history.pushState({v:'L'},'');return}
 if(d.g){st.grp=d.g;st.lim=40;st.hist=[];renderF();window.scrollTo(0,listTop());return}
 if(d.pv){drill(()=>{const[r]=d.pv.split('|');st.regs=new Set([r]);st.prov=d.pv;st.grp='c'});return}
 if(d.rg){drill(()=>{st.regs=new Set([d.rg]);st.prov=null;st.grp='v'});return}
 if(d.ar){drill(()=>{st.regs=new Set(AREE[d.ar]);st.prov=null;st.grp='r'});return}
 if(d.a==='undrill'){history.back();return}
 if(d.a==='tolist'){goList();return}
 if(d.a==='resetL'){st.regs.clear();st.prov=null;st.sel={};st.tx.clear();st.q='';st.hist=[];st.all=true;renderF();renderL();renderBar();return}""")
R(" if(d.reg){st.regs.has(d.reg)?st.regs.delete(d.reg):st.regs.add(d.reg);st.lim=40}",
  " if(d.reg){st.regs.has(d.reg)?st.regs.delete(d.reg):st.regs.add(d.reg);st.prov=null;st.hist=[];st.lim=40}")
R(" else if(d.a==='regall')st.regs.clear();"," else if(d.a==='regall'){st.regs.clear();st.prov=null;st.hist=[]}")
R(" else if(d.a==='reset'){st.regs.clear();st.sel={};st.tx.clear();st.q=''}",
  " else if(d.a==='reset'){st.regs.clear();st.prov=null;st.sel={};st.tx.clear();st.q='';st.hist=[]}")
R("prototipo 4</span>","prototipo 5</span>")
R("\nrenderF();\n</script>","""
const _rF=renderF;renderF=function(){_rF();renderBar()};
window.addEventListener('popstate',()=>{if($('sheet').classList.contains('open')){closeSheet();return}
 if($('vL').classList.contains('on')){tab('F');return}if(st.hist.length)undrill()});
renderF();
</script>""")
open('v4_tail.html','w').write(t)
h=open('v3_head.html').read()
def H(a,b):
    global h
    assert a in h,a[:60]; h=h.replace(a,b,1)
H('<div class="tabs"><div class="seg">','<div class="tabs"><div class="seg">')
H('</button></div></div>\n<section class="view on" id="vF">','</button></div><div class="fbar" id="fbar"></div></div>\n<section class="view on" id="vF">')
H('</style>',r""".tabs{flex-direction:column;gap:6px}
.tabs .seg{flex:none}
.fbar{display:none;align-items:center;gap:9px;padding:6px 6px 6px 8px;border-radius:14px;background:var(--paper);border:1px solid var(--line);box-shadow:var(--shadow)}
.fbar.on{display:flex}
.fbar .fn{flex:none;width:24px;height:24px;border-radius:50%;background:var(--terra);color:#fff;font-size:12px;font-weight:800;display:grid;place-items:center}
.fbar .ft{flex:1;min-width:0;font-size:12.5px;color:var(--ink2);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;line-height:1.25}
.fbar .ft small{display:block;font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}
.rst{flex:none;height:32px;padding:0 13px;border-radius:999px;border:1.5px solid var(--terra);background:var(--paper);color:var(--terra);font-size:13px;font-weight:750;cursor:pointer;white-space:nowrap}
.rst:active{background:var(--terra);color:#fff}
.sum .rst{margin-left:auto}
.back{display:inline-flex;align-items:center;gap:4px;height:38px;padding:0 15px 0 11px;border-radius:999px;border:1px solid var(--line);background:var(--ink);color:var(--paper);font-size:14px;font-weight:700;cursor:pointer;margin:4px 0 8px}
.back:active{transform:scale(.98)}
.lbar{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:2px 0 6px}
.lbar .back{margin:0}
.grp{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:3px;background:var(--bg2);border:1px solid var(--line);border-radius:14px;padding:3px;margin-bottom:12px}
.grp button{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;min-height:48px;padding:4px 2px;border:0;border-radius:11px;background:transparent;font-size:11px;font-weight:650;color:var(--ink2);cursor:pointer;line-height:1.1;text-align:center}
.grp button span{font-size:17px}
.grp button.on{background:var(--paper);color:var(--ink);box-shadow:var(--shadow);font-weight:800}
.com .sub{display:block;font-size:12px;color:var(--mute);margin:-2px 0 5px}
.flat{display:grid;gap:10px}
@media(min-width:700px){.flat{grid-template-columns:1fr 1fr}.flat .fh{grid-column:1/-1}}
.fh{font-family:var(--serif);font-size:1.25rem;margin:10px 2px 0}
.card .cn{font-size:12px;color:var(--mute);margin:-2px 0 5px;font-weight:600}
</style>""")
open('v4_head.html','w').write(h)
