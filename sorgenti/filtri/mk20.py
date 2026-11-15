# Pagina Luoghi, 10/11 ore 12:15 (richiesta di Stefano): il sotto menu (Archeologia, Castelli…) sta subito sotto le categorie,
# sopra la striscia UNESCO / Gratis / Al coperto…; le voci del sotto menu sono in grassetto, un po' più visibili
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk20' in h:
    print('mk20 già applicato'); raise SystemExit
def rep(a, b):
    global h
    assert h.count(a) == 1, (h.count(a), a[:70])
    h = h.replace(a, b)
A = """<span class="gsep" aria-hidden="true"></span>${TX.map(([k,e,l])=>`<button class="tog${st.tx.has(k)?' on':''}" data-t="${k}" aria-pressed="${st.tx.has(k)}">${e} ${l}</button>`).join('')}</div>"""
assert h.count(A) == 1
TXROW = """<div class="gcat gtx">${TX.map(([k,e,l])=>`<button class="tog${st.tx.has(k)?' on':''}" data-t="${k}" aria-pressed="${st.tx.has(k)}">${e} ${l}</button>`).join('')}</div>"""
h = h.replace(A, "</div>")
# il sotto menu: si chiude con </div>`:''} subito dopo l'elenco dei chip; la striscia va dopo
B = """<button class="chip${sel.has(s)?' on':''}${n?'':' zero'}" data-s="${esc(s)}">${e} ${s} <i>${n}</i></button>`}).join('')}</div>`:''}"""
rep(B, B + "\n " + TXROW)
rep('.gsep{width:1px;', '/* mk20 */\n.srow .chip{font-weight:700}.srow .chip i{font-weight:600}.srow{margin:2px 0 6px}\n.gtx{padding-top:0}\n.gsep{width:1px;')
open(F, 'w').write(h)
print('mk20 ok')
