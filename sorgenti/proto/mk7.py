t=open('v6_tail.html').read();h=open('v6_head.html').read()
def R(a,b):
    global t
    assert a in t,a[:70]; t=t.replace(a,b,1)
def H(a,b):
    global h
    assert a in h,a[:70]; h=h.replace(a,b,1)
# clickable category stats in comune view
R("const list=st.all||filt.length===all.length?all:filt;","const list0=st.all||filt.length===all.length?all:filt;const list=st.lc?list0.filter(p=>p[2]===st.lc):list0;")
R("const g=M.map(m=>[m,list.filter(p=>p[2]===m.k).length]).filter(x=>x[1]);","const g=M.map(m=>[m,list0.filter(p=>p[2]===m.k).length]).filter(x=>x[1]);")
R("""<span class="st" style="${cv(m.k)}"><em>${m.e}</em><span><b>${n}</b><small>${m.l}</small></span></span>`""",
  """<button class="st${st.lc===m.k?' on':''}${st.lc&&st.lc!==m.k?' off':''}" style="${cv(m.k)}" data-lc="${m.k}" aria-pressed="${st.lc===m.k}"><em>${m.e}</em><span><b>${n}</b><small>${m.l}</small></span></button>`""")
R("""<div class="stats">""","""<div class="lab lch">Tocca una categoria per vedere solo quella${st.lc?' · <button class="lcx" data-lc="'+st.lc+'">✕ Mostra tutte</button>':''}</div><div class="stats">""")
R(" if(d.p){openSheet(+d.p);return}"," if(d.p){openSheet(+d.p);return}\n if(d.lc){st.lc=st.lc===d.lc?null:d.lc;renderL();return}")
R("st.com=+d.c;st.all=false;","st.com=+d.c;st.all=false;st.lc=null;")
R(" else if(d.a==='dall'){st.all=true;renderL();return}"," else if(d.a==='dall'){st.all=true;renderL();return}")
H('<span class="t">Filtri</span>','<span class="t">Luoghi</span>')
H("<title>Ach's Places Guide · Filtri</title>","<title>Ach's Places Guide · Luoghi</title>")
H('</style>',r""".st{transition:transform .1s,opacity .15s,box-shadow .15s}
.st:active{transform:scale(.97)}
.st.on{background:var(--cc);color:#fff;box-shadow:0 4px 12px -6px var(--cc)}.st.on b,.st.on small{color:#fff}
.st.off{opacity:.45}
.lch{margin:12px 0 0;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.lcx{height:26px;padding:0 10px;border-radius:999px;border:1px solid var(--line);background:var(--paper);font-size:12px;font-weight:700;cursor:pointer;letter-spacing:0;text-transform:none;color:var(--ink)}

.pvs{display:none;width:100%;font:600 11.5px var(--sans);color:var(--mute);letter-spacing:.04em;margin-top:2px}
@media(min-width:700px){.reg{display:grid;grid-template-columns:1fr 1fr;column-gap:10px;align-items:stretch}.reg>h2,.reg>.pv{grid-column:1/-1}.reg>.com{height:calc(100% - 6px)}.reg>.pv{display:none}.pvs{display:block}}
.frow .rc{height:34px;padding:0 13px;font-size:14.5px}
#fp .search{height:40px;font-size:16px}
.mp{height:36px;padding:0 13px;font-size:14.5px}
.mp i{font-size:12px}
.srow .chip{height:32px;font-size:14px;padding:0 12px}
#fp .tog{height:32px;font-size:14px;padding:0 12px}
#fp .grp button{min-height:34px;font-size:13.5px;padding:0 11px}
.fbar .ft{font-size:13px}.fbar .ft b{font-size:14px}
</style>""")
R("h+=row(`data-c=\"${ci}\"`,esc(c[0])+aw,'',ps)","h+=row(`data-c=\"${ci}\"`,esc(c[0])+aw+`<span class=\"pvs\">${esc(pvName(c))}</span>`,'',ps)")
R("Tocca una categoria per vedere solo quella","Tocca una categoria per filtrare")
R("open:'arch'","open:null")
open('v7_tail.html','w').write(t);open('v7_head.html','w').write(h)
