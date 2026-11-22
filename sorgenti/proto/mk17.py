# Pagina Luoghi, 8/11 (richiesta di Stefano): più spazio per l'elenco.
# - su PC larghezza uguale alla Guida; selettori e ricerca sulla stessa riga
# - UNESCO, Gratis, Coperti, Panorama, Borghi, Arancioni spostati nella riga delle categorie (una riga in meno)
# - «Più belli» diventa «Borghi»
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk17' not in h:
    def rep(a, b):
        global h
        assert a in h, a[:60]
        h = h.replace(a, b)
    rep("['b','🏘️','Più belli']", "['b','🏘️','Borghi']")
    rep("""<div class="frow">${TX.map(([k,e,l])=>`<button class="tog${st.tx.has(k)?' on':''}" data-t="${k}">${e} ${l}</button>`).join('')}</div>\n""", "")
    rep("""<small>${c?c+' scelti':n}</small></button>`}).join('')}</div>""",
        """<small>${c?c+' scelti':n}</small></button>`}).join('')}<span class="gsep" aria-hidden="true"></span>${TX.map(([k,e,l])=>`<button class="tog${st.tx.has(k)?' on':''}" data-t="${k}" aria-pressed="${st.tx.has(k)}">${e} ${l}</button>`).join('')}</div>""")
    css = """
/* mk17: più spazio per l'elenco */
.gcat .tog{align-self:center;white-space:nowrap}
.gsep{width:1px;align-self:stretch;margin:6px 2px;background:var(--line)}
@media (max-width:759px){.gcat{align-items:center}}
@media (min-width:900px){
 .wrap{max-width:1096px}
 .fx{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);column-gap:12px;align-items:end}
 .fx>*{grid-column:1/-1}
 .fx>.pick{grid-column:1;margin-bottom:6px}
 .fx>.row1{grid-column:2;margin-bottom:6px}
 .gcat{align-items:center}
 .gsep{display:none}
}
"""
    k = h.rindex('</style>')
    h = h[:k] + css + h[k:]
    open(F, 'w').write(h)
    print('mk17 ok')
else:
    print('mk17 già applicato')
