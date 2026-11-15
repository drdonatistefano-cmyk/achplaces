L=open('v4_tail.html').read().split('\n')
# lines 42..51 (1-idx) -> header template
H=r""" let fh=`<div class="fx"><div class="frow"><button class="rc${st.regs.size?'':' on'}" data-a="regall">🇮🇹 Tutte <i>${Bn.length}</i></button>${regs.map(r=>`<button class="rc${st.regs.has(r)?' on':''}" data-reg="${r}">${esc(RG(r))} <i>${rc[r]||0}</i></button>`).join('')}</div>
 <input class="search" id="q" type="search" placeholder="🔍 Cerca un comune o un luogo" value="${esc(st.q)}" autocomplete="off">
 <div class="frow mrow">${M.map(x=>{const n=B.filter(p=>p[2]===x.k).length,c=(st.sel[x.k]||new Set()).size;return `<button class="mp${st.open===x.k?' on':''}${c?' has':''}" style="${cv(x.k)}" data-m="${x.k}">${x.e} ${x.l} <i>${c?c+'✓':n}</i></button>`}).join('')}</div>
 ${m?`<div class="frow srow" style="${cv(m.k)}">${sel.size?`<button class="chip clr" data-clr="${m.k}">✕ Togli</button>`:''}${Object.entries(m.s).map(([s,e])=>{const n=B.filter(p=>p[2]===m.k&&p[3].includes(s)).length;return `<button class="chip${sel.has(s)?' on':''}${n?'':' zero'}" data-s="${esc(s)}">${e} ${s} <i>${n}</i></button>`}).join('')}</div>`:''}
 <div class="frow">${TX.map(([k,e,l])=>`<button class="tog${st.tx.has(k)?' on':''}" data-t="${k}">${e} ${l}</button>`).join('')}</div>
 <div class="grp" id="grp">${GR.map(([k,e,l])=>`<button class="${st.grp===k?'on':''}" data-g="${k}">${e} ${l}</button>`).join('')}</div></div>`;
 let h='';"""
L=L[:41]+[H]+L[51:]
t='\n'.join(L)
def R(a,b):
    global t
    assert a in t,a[:70]; t=t.replace(a,b,1)
# remove sum and grp lines from list
import re
i=t.index(' h+=`<div class="sum" id="sum">');j=t.index('\n',i);t=t[:i]+t[j+1:]
i=t.index(' h+=`<div class="lab" id="grp">');j=t.index('\n',i);t=t[:i]+t[j+1:]
R("$('vF').innerHTML=h;","if(!noHead)$('fp').innerHTML=fh;$('vF').innerHTML=h;st.cnt=[R.length,new Set(R.map(p=>p[1])).size];")
R("st.lim=40;const pos=q.selectionStart;renderF();const n2=$('q');n2.focus();try{n2.setSelectionRange(pos,pos)}catch(e){}};",
  "st.lim=40;renderF(true);window.scrollTo(0,0)};")
R("function renderF(){","function renderF(noHead){")
R("const _rF=renderF;renderF=function(){_rF();renderBar()};","const _rF=renderF;renderF=function(n){_rF(n);renderBar()};")
# bar: always visible on F with counts + fold toggle
i=t.index("function renderBar(){");j=t.index("\nfunction tab(t){")
t=t[:i]+r"""function renderBar(){const n=nFil(),b=$('fbar'),L=$('vL').classList.contains('on');
 const bits=[];if(st.regs.size)bits.push(areaOf()?AL[areaOf()]:[...st.regs].map(RG).join(', '));if(st.prov)bits.push(st.prov.split('|')[1]);for(const k in st.sel)for(const s of st.sel[k])bits.push(s);for(const k of st.tx)bits.push(TX.find(x=>x[0]===k)[2]);if(st.q)bits.push('«'+st.q+'»');
 if(L&&!n){b.classList.remove('on');b.innerHTML='';return}
 const c=st.cnt||[0,0];
 b.innerHTML=`${L?'':`<button class="fold" data-a="fold" aria-label="Mostra o nascondi i filtri">${st.fold?'▾':'▴'}</button>`}<span class="ft"><b>${L?n+(n===1?' filtro':' filtri'):c[0]+' luoghi · '+c[1]+' comuni'}</b>${n?esc(bits.join(' · ')):'Nessun filtro'}</span>${n?`<button class="rst" data-a="${L?'resetL':'reset'}">↺ Azzera</button>`:''}`;b.classList.add('on')}"""+t[j:]
R("function tab(t){","function tab(t){document.body.classList.toggle('tL',t==='L');")
R(" if(d.a==='undrill'){history.back();return}"," if(d.a==='undrill'){history.back();return}\n if(d.a==='fold'){st.fold=!st.fold;document.body.classList.toggle('ffold',st.fold);renderBar();return}")
# scroll to top of list after filter changes
R(" renderF();if(st.com!=null)renderL()});"," renderF();if(st.com!=null)renderL();if(!d.a||d.a!=='more')window.scrollTo(0,0)});")
R("const listTop=()=>{const e=$('grp');return e?Math.max(0,e.getBoundingClientRect().top+window.scrollY-120):0};","const listTop=()=>0;")
R("prototipo 5</span>","prototipo 6</span>") if "prototipo 5</span>" in t else None
open('v5_tail.html','w').write(t)

h=open('v4_head.html').read()
def Hh(a,b):
    global h
    assert a in h,a[:60]; h=h.replace(a,b,1)
Hh('</button></div><div class="fbar" id="fbar"></div></div>','</button></div><div id="fp"></div><div class="fbar" id="fbar"></div></div>')
Hh('</style>',r""".tabs{gap:5px;padding:6px 0 7px;box-shadow:0 8px 14px -12px rgba(0,0,0,.25)}
body.tL #fp,body.ffold #fp{display:none}
.fx{display:flex;flex-direction:column;gap:5px}
.frow{display:flex;gap:5px;overflow-x:auto;scrollbar-width:none;-webkit-overflow-scrolling:touch;padding:1px 0}
.frow::-webkit-scrollbar{display:none}
.frow>button{flex:none}
.frow .rc{height:30px;padding:0 11px;font-size:13px}
#fp .search{height:36px;margin:0;font-size:15px;padding:0 13px}
.mp{height:32px;padding:0 11px;border-radius:999px;border:1px solid var(--line);background:var(--paper);font-size:13px;font-weight:700;color:var(--ink);cursor:pointer;white-space:nowrap}
.mp i{font-style:normal;font-size:11px;color:var(--mute);font-weight:650;margin-left:2px}
.mp.on{background:var(--mc);border-color:var(--mc);color:#fff}.mp.on i{color:rgba(255,255,255,.85)}
.mp.has:not(.on){border-color:var(--mc);box-shadow:inset 0 0 0 1px var(--mc)}
.srow{background:var(--ms);border-radius:12px;padding:4px}
.srow .chip{height:28px;font-size:12.5px;padding:0 10px;margin:0}
.srow .chip.clr{background:var(--paper);font-weight:700}
#fp .tog{height:28px;font-size:12.5px;padding:0 10px;margin:0}
#fp .grp{margin:0;padding:2px;border-radius:12px;display:flex;overflow-x:auto;scrollbar-width:none}
#fp .grp::-webkit-scrollbar{display:none}
#fp .grp button{flex:1 0 auto;flex-direction:row;min-height:30px;gap:3px;font-size:12px;padding:0 9px;white-space:nowrap}
.fbar{padding:4px 5px 4px 5px;gap:7px;border-radius:12px}
.fbar .ft{font-size:12px}
.fbar .ft b{display:block;font-size:13px;color:var(--ink)}
.fold{flex:none;width:30px;height:30px;border-radius:50%;border:1px solid var(--line);background:var(--bg2);font-size:13px;cursor:pointer;color:var(--ink2)}
.fbar .rst{height:30px;padding:0 11px;font-size:12.5px}
#vF{padding-top:4px}
</style>""")
open('v5_head.html','w').write(h)
