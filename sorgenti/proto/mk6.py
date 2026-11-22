t=open('v5_tail.html').read();h=open('v5_head.html').read()
def R(a,b):
    global t
    assert a in t,a[:70]; t=t.replace(a,b,1)
def H(a,b):
    global h
    assert a in h,a[:70]; h=h.replace(a,b,1)
R("""<div class="lbar"><button class="back" data-a="tolist">‹ Torna all'elenco</button></div>""",
  """<div class="lbar"><button class="back" data-a="tolist">‹ Torna all'elenco</button><a class="toG" href="index.html#${c[5]}">🧭 Apri nella Guida</a></div>""")
R("""<a class="act" href="https://www.google.com/search?tbm=isch&q=${encodeURIComponent(p[0]+' '+c[0])}" target="_blank" rel="noopener">📷 Foto</a></div>""",
  """<a class="act" href="https://www.google.com/search?tbm=isch&q=${encodeURIComponent(p[0]+' '+c[0])}" target="_blank" rel="noopener">📷 Foto</a><a class="act wide" href="index.html#${c[5]}">🧭 Scheda completa nella Guida: ${esc(c[0])}</a></div>""")
R("""<p class="note">Nella versione definitiva qui compaiono anche orari, biglietti, accessibilità e fonti ufficiali, come nella Guida.</p>""","")
H("<title>Ach's Places Guide · Filtri (prototipo 4)</title>","<title>Ach's Places Guide · Filtri</title>")
H('<div class="seg"><button class="tab on" id="tabF"','<div class="seg"><a class="tab gl" href="index.html" aria-label="Torna alla Guida">🧭 <span class="t">Guida</span></a><button class="tab on" id="tabF"')
H('<span class="t">Filtri e comuni</span>','<span class="t">Filtri</span>')
H('</style>',r""".tab.gl{flex:0 0 auto;padding:0 12px;text-decoration:none;color:var(--ink2)}
.toG{display:inline-flex;align-items:center;height:38px;padding:0 13px;border-radius:999px;border:1px solid var(--line);background:var(--paper);color:var(--ink);font-size:13.5px;font-weight:700;text-decoration:none}
.act.wide{grid-column:1/-1}
.frow .rc{height:32px;padding:0 12px;font-size:13.5px}
#fp .search{height:38px;font-size:15.5px}
.mp{height:34px;padding:0 12px;font-size:13.5px}
.srow .chip{height:30px;font-size:13px;padding:0 11px}
#fp .tog{height:30px;font-size:13px;padding:0 11px}
#fp .grp button{min-height:32px;font-size:12.5px;padding:0 10px}
.fx{gap:6px}
</style>""")
open('v6_tail.html','w').write(t);open('v6_head.html','w').write(h)
