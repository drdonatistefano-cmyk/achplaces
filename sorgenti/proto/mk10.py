t=open('v9_tail.html').read();h=open('v9_head.html').read()
def R(a,b):
    global t
    assert t.count(a)==1,a[:70]; t=t.replace(a,b,1)
def H(a,b):
    global h
    assert h.count(a)==1,a[:70]; h=h.replace(a,b,1)
old_start='let fh=`<div class="fx"><div class="frow"><button class="rc'
i=t.index(old_start); j=t.index('<div class="frow mrow">',i); k=t.index('</div>\n',j)+7
new=r'''const comsIn=()=>C.map((c,ci)=>[c,ci]).filter(([c])=>(!st.regs.size||st.regs.has(c[2]))&&(!st.prov||st.prov===c[2]+'|'+c[1]));
 const provsIn=()=>{const m=new Map();for(const c of C)if(!st.regs.size||st.regs.has(c[2])){const k=c[2]+'|'+c[1];if(!m.has(k))m.set(k,c)}return [...m.entries()].sort((a,b)=>RG(a[1][2]).localeCompare(RG(b[1][2]),'it')||a[1][1].localeCompare(b[1][1],'it'))};
 const regV=st.regs.size?(areaOf()?AL[areaOf()]:st.regs.size===1?RG([...st.regs][0]):st.regs.size+' regioni'):'Tutte';
 const provV=st.prov?st.prov.split('|')[1]:'Tutte';
 const pc={};for(const p of B)pc[p[1]]=(pc[p[1]]||0)+1;
 let pop='';
 if(st.pop==='reg')pop=`<div class="mpop"><div class="mphead"><b>Regioni</b><span>puoi sceglierne più di una</span></div><div class="mlist">${regs.map(r=>`<button class="mopt${st.regs.has(r)?' on':''}" data-reg="${r}"><span class="t">${esc(RG(r))}</span><small>${rc[r]||0}</small></button>`).join('')}</div><div class="mpfoot"><button class="mpall" data-a="regall">Tutte le regioni</button><button class="mpdone" data-a="popclose">Fatto</button></div></div>`;
 if(st.pop==='prov')pop=`<div class="mpop"><div class="mphead"><b>Province</b><span>${st.regs.size?esc(regV):'tutta Italia'}</span></div><div class="mlist">${(()=>{let cr=null,o='';for(const [k,c] of provsIn()){if(c[2]!==cr&&st.regs.size!==1){cr=c[2];o+=`<div class="mgrp">${esc(RG(c[2]))}</div>`}o+=`<button class="mopt${st.prov===k?' on':''}" data-pp="${esc(k)}"><span class="t">${esc(c[1])}</span></button>`}return o})()}</div><div class="mpfoot"><button class="mpall" data-pp="">Tutte le province</button><button class="mpdone" data-a="popclose">Fatto</button></div></div>`;
 if(st.pop==='com')pop=`<div class="mpop"><div class="mphead"><b>Comuni</b><span>tocca un comune per aprirlo</span></div><input class="mpq" id="cq" type="search" placeholder="Cerca un comune…" autocomplete="off"><div class="mlist" id="cqlist"></div><div class="mpfoot"><button class="mpdone" data-a="popclose">Chiudi</button></div></div>`;
 let fh=`<div class="fx"><div class="pick"><div class="msel"><span class="mlab">Regioni</span><button class="mbtn" data-pop="reg" aria-expanded="${st.pop==='reg'}"><span class="mv">${esc(regV)}</span><span class="cv">▼</span></button></div><div class="msel"><span class="mlab">Province</span><button class="mbtn" data-pop="prov" aria-expanded="${st.pop==='prov'}"><span class="mv">${esc(provV)}</span><span class="cv">▼</span></button></div><div class="msel"><span class="mlab">Comuni</span><button class="mbtn" data-pop="com" aria-expanded="${st.pop==='com'}"><span class="mv">Scegli…</span><span class="cv">▼</span></button></div>${pop}</div>
 <div class="row1"><label class="srch"><svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg><input id="q" type="search" placeholder="Cerca un comune o un luogo…" value="${esc(st.q)}" autocomplete="off"></label>${nFil()?`<button class="iconbtn reset" data-a="reset"><span aria-hidden="true">↺</span><span class="rl">Azzera</span><span class="badge">${nFil()}</span></button>`:''}<button class="iconbtn${st.near?' on':''}" data-a="near" aria-pressed="${!!st.near}"><span aria-hidden="true">${st.nearBusy?'⏳':'📍'}</span><span class="rl">Vicino a te</span></button></div>${st.nearErr?`<div class="nerr">${esc(st.nearErr)}</div>`:''}
 <div class="qlab">Cosa vuoi vedere</div>
 <div class="gcat">${M.map(x=>{const n=B.filter(p=>p[2]===x.k).length,c=(st.sel[x.k]||new Set()).size;return `<button class="qc${st.open===x.k?' on':''}${c?' has':''}" style="${cv(x.k)}" data-m="${x.k}"><span class="em">${x.e}</span><span class="ql">${x.l}</span><small>${c?c+' scelti':n}</small></button>`}).join('')}</div>
'''
t=t[:i]+new+t[k:]
# comuni list fill after head render
R("const q=$('q');q.oninput=","const cq=$('cq');if(cq){const fill=()=>{const s=norm(cq.value);$('cqlist').innerHTML=comsIn().filter(([c])=>!s||norm(c[0]).includes(s)).slice(0,300).map(([c,ci])=>`<button class=\"mopt nocb\" data-c=\"${ci}\"><span class=\"t\">${esc(c[0])}</span><small>${esc(c[1])}</small></button>`).join('')};cq.oninput=fill;fill()}\n const q=$('q');q.oninput=")
R(" if(d.c){closeSheet();"," if(d.pop){st.pop=st.pop===d.pop?null:d.pop;renderF();return}\n if(d.a==='popclose'){st.pop=null;renderF();return}\n if(d.pp!==undefined){st.prov=d.pp&&st.prov!==d.pp?d.pp:null;if(st.prov){const r=st.prov.split('|')[0];if(!st.regs.has(r))st.regs=new Set([r])}st.hist=[];st.lim=40;st.pop=null;renderF();return}\n if(d.c){if(st.pop){st.pop=null;renderF()}closeSheet();")
R("else if(d.a==='reset'){st.near=null;","else if(d.a==='reset'){st.pop=null;st.near=null;")
# bold location line in cards
R('<div class="cn">📍 ${esc(c[0])} · ${esc(c[1])}</div>','<div class="cn">📍 <b>${esc(c[0])}</b> · <b>${esc(c[1])}</b> · ${esc(RG(c[2]))}</div>')
H('</style>',r""".pick{position:relative;display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px;margin:2px 0 8px}
.msel{display:grid;gap:3px;min-width:0}
.mlab{font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:var(--mute)}
.mbtn{height:42px;border:1px solid var(--line);border-radius:12px;background:var(--paper);color:var(--ink);font:600 15px var(--sans);padding:0 10px;box-shadow:var(--shadow);display:flex;align-items:center;gap:6px;cursor:pointer;min-width:0;text-align:left}
.mbtn .mv{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mbtn .cv{font-size:10px;opacity:.6}
.mbtn[aria-expanded="true"]{border-color:var(--terra)}
.mpop{position:absolute;left:0;right:0;top:calc(100% + 6px);z-index:40;background:var(--paper);border:1px solid var(--line);border-radius:16px;box-shadow:0 14px 40px rgba(40,25,10,.18);padding:10px}
@media(min-width:640px){.mpop{right:auto;width:min(620px,calc(100vw - 40px))}}
.mphead{display:flex;align-items:baseline;justify-content:space-between;gap:8px;margin:2px 4px 6px}
.mphead b{font-family:var(--serif);font-size:1.15rem;font-weight:600}.mphead span{font-size:12.5px;color:var(--mute)}
.mlist{max-height:min(52vh,420px);overflow-y:auto;display:grid;gap:4px;-webkit-overflow-scrolling:touch}
.mgrp{font:800 11px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--terra);margin:8px 4px 2px}
.mpq{width:100%;height:40px;border:1px solid var(--line);border-radius:10px;background:var(--bg);color:var(--ink);font:600 16px var(--sans);padding:0 12px;margin-bottom:8px}
.mopt{display:flex;align-items:center;gap:9px;min-height:42px;padding:0 10px;border-radius:10px;border:1px solid transparent;background:none;color:var(--ink);font:600 14.5px var(--sans);cursor:pointer;text-align:left;width:100%}
.mopt .t{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.mopt small{color:var(--faint);font-size:12px}
.mopt::before{content:"";width:18px;height:18px;flex:none;border-radius:6px;border:1.5px solid var(--line);display:grid;place-items:center;font-size:12px;font-weight:800;color:#fff}
.mopt.nocb::before{display:none}
.mopt.on{background:var(--terra-soft)}.mopt.on::before{content:"✓";background:var(--terra);border-color:var(--terra)}
.mpfoot{display:flex;gap:8px;justify-content:flex-end;margin-top:8px;padding-top:8px;border-top:1px solid var(--line)}
.mpfoot button{height:38px;padding:0 16px;border-radius:999px;font-weight:800;cursor:pointer}
.mpall{border:1.5px solid var(--terra);background:var(--paper);color:var(--terra);margin-right:auto}
.mpdone{border:0;background:var(--terra);color:var(--on)}
.row1{display:flex;gap:8px;align-items:center;margin:0 0 10px}
.srch{flex:1;position:relative;min-width:0}
.srch svg{position:absolute;left:12px;top:50%;transform:translateY(-50%);color:var(--faint)}
.srch input{width:100%;height:44px;padding:0 12px 0 38px;border:1px solid var(--line);border-radius:12px;background:var(--paper);color:var(--ink);font:16px var(--sans);box-shadow:var(--shadow)}
.iconbtn{position:relative;height:44px;min-width:44px;padding:0 14px;border-radius:12px;border:1px solid var(--line);background:var(--paper);color:var(--ink);font:600 15px var(--sans);cursor:pointer;display:flex;align-items:center;justify-content:center;gap:7px;box-shadow:var(--shadow);white-space:nowrap}
.iconbtn.on{border-color:var(--terra);color:var(--terra)}
.iconbtn.reset{background:var(--terra);border-color:var(--terra);color:#fff;font-weight:800}
.iconbtn .badge{position:absolute;top:-6px;right:-6px;min-width:20px;height:20px;padding:0 5px;border-radius:10px;background:#fff;color:var(--terra);font-size:11.5px;display:grid;place-items:center;font-weight:700;box-shadow:0 0 0 1px var(--terra)}
@media(max-width:699px){.iconbtn .rl{display:none}.iconbtn{padding:0 12px}}
.qlab{font:800 11.5px var(--sans);letter-spacing:.1em;text-transform:uppercase;color:var(--mute);margin:0 0 6px}
.gcat{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(96px,1fr);gap:8px;overflow-x:auto;padding:2px 2px 8px;scrollbar-width:none}
.gcat::-webkit-scrollbar{display:none}
.qc{height:78px;border-radius:16px;border:1px solid var(--line);background:var(--paper);box-shadow:var(--shadow);display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;cursor:pointer;color:var(--ink);font:650 13.5px var(--sans);padding:6px;position:relative}
.qc .em{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;font-size:17px;background:var(--cs)}
.qc small{color:var(--faint);font-size:11.5px;font-weight:600}
.qc.on{border-color:var(--cc);background:var(--cs);box-shadow:inset 0 0 0 1.5px var(--cc)}
.qc.has::after{content:"✓";position:absolute;top:6px;right:8px;width:18px;height:18px;border-radius:50%;background:var(--cc);color:#fff;font-size:11px;display:grid;place-items:center;font-weight:800}
@media(max-width:759px){.gcat{grid-auto-columns:max-content;gap:6px}.qc{height:40px;flex-direction:row;gap:6px;padding:0 12px 0 6px;border-radius:999px;font-size:13.5px}.qc .em{width:28px;height:28px;font-size:15px}.qc small{font-size:11.5px;margin-left:2px}.qc.has::after{top:-5px;right:-5px;width:16px;height:16px;font-size:10px}}
@media(min-width:760px){.gcat{display:flex;flex-wrap:wrap;overflow:visible}.qc{height:46px;border-radius:14px;padding:0 14px 0 8px;flex-direction:row;gap:8px}.qc .em{width:30px;height:30px;font-size:16px}.qc small{margin-left:4px}}
.cn b{color:var(--ink);font-weight:800}
.tabs .seg{background:none!important;border:0!important;padding:0!important;gap:6px;flex-wrap:nowrap}
.tabs .tab{flex:1 1 auto;height:36px;border-radius:999px;border:1px solid var(--line);background:var(--paper);color:var(--ink);font:700 13.5px var(--sans);padding:0 14px;box-shadow:none;white-space:nowrap}
.tabs .tab.on{background:var(--terra);border-color:var(--terra);color:#fff}
.tabs .tab:disabled{opacity:.45}
@media(max-width:560px){.tabs .tab{padding:0 8px;font-size:13px;gap:4px;height:34px;min-width:auto}.tabs .tab:disabled{display:none}.tabs .tab .t{overflow:visible;text-overflow:clip}}
@media(min-width:700px){.tabs .tab{flex:0 0 auto}}
.com .sub,.pvs,.pv{font-weight:800!important;color:var(--ink2)!important}
.com h4,.reg>h2,.fh,.card h3{font-weight:800!important}
</style>""")
open('v10_head.html','w').write(h);open('v10_tail.html','w').write(t)
print('v10 ok')
