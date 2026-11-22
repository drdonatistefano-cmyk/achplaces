# Pagina Luoghi, 8/11 ore 18:35 (richiesta di Stefano):
# - telefono: un solo bottone «Filtri» che segue in basso, filtri chiusi all'avvio, più spazio all'elenco
# - telefono: righe dei comuni più basse (icone più compatte)
# - colori meno neri, come nella Guida (titoli blu, sottotitoli grigi, numeri in blu)
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk18' in h:
    print('mk18 già applicato'); raise SystemExit
def rep(a, b):
    global h
    assert h.count(a) == 1, (h.count(a), a[:70])
    h = h.replace(a, b)
# bottone con scritta «Filtri»
rep("""<button class="fold" data-a="fold" aria-label="Mostra o nascondi i filtri">${st.fold?'▾':'▴'}</button>""",
    """<button class="fold" data-a="fold" aria-expanded="${!st.fold}" aria-label="Mostra o nascondi i filtri"><span class="fic">${st.fold?'▾':'▴'}</span><span class="flab">${st.fold?'Filtri':'Chiudi'}</span>${nFil()?`<span class="fnb">${nFil()}</span>`:''}</button>""")
# aprendo i filtri si torna in cima
rep("""if(d.a==='fold'){st.fold=!st.fold;document.body.classList.toggle('ffold',st.fold);renderBar();return}""",
    """if(d.a==='fold'){st.fold=!st.fold;document.body.classList.toggle('ffold',st.fold);renderBar();if(!st.fold)window.scrollTo({top:0,behavior:'smooth'});return}""")
# filtri chiusi all'avvio sul telefono
rep("\nrenderF();\n", "\nif(window.matchMedia&&matchMedia('(max-width:759px)').matches){st.fold=true;document.body.classList.add('ffold')}\nrenderF();\n")
css = """
/* mk18: colori come nella Guida, telefono più compatto, bottone Filtri che segue */
.com h4{font-weight:650!important}
.com .sub{font-weight:600!important;color:var(--mute)!important}
.com .tot b{color:var(--terra)}
.reg>h2,.fh{color:var(--terra)}
.pvs,.pv{color:var(--terra)!important}
.flab,.fnb{display:none}
@media (max-width:759px){
 .tabs{position:static}
 #fbar.on{position:fixed;left:12px;right:12px;bottom:max(12px,env(safe-area-inset-bottom));z-index:30;box-shadow:0 8px 28px rgba(30,20,10,.22);padding:6px 6px 6px 6px;border-color:var(--line2)}
 .wrap{padding-bottom:110px}
 .fold{width:auto;height:38px;padding:0 14px 0 11px;display:inline-flex;align-items:center;gap:6px;border:0;background:var(--terra);color:var(--on);font-weight:750;font-size:14px}
 .flab{display:inline}
 .fnb{display:inline-grid;place-items:center;min-width:20px;height:20px;padding:0 5px;border-radius:999px;background:var(--on);color:var(--terra);font-size:11.5px;font-weight:800}
 .com{padding:7px 10px;gap:8px;margin-bottom:5px;border-radius:12px}
 .reg>h2{top:0}
 .com .bd{display:flex;flex-wrap:wrap;align-items:center;column-gap:8px;row-gap:3px}
 .com h4{font-size:1rem;margin:0}
 .com .sub{flex-basis:100%}
 .com .sub{margin:0;font-size:11.5px}
 .com .cats{gap:3px}
 .cat{height:19px;padding:0 6px 0 4px;font-size:11px;gap:2px}
 .com .tot{min-width:34px}
 .com .tot b{font-size:1.15rem}
 .com .tot small{display:none}
 .com{min-height:0}
 .com .chev{font-size:16px}
}
"""
k = h.rindex('</style>')
h = h[:k] + css + h[k:]
open(F, 'w').write(h)
print('mk18 ok')
