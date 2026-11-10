# Pagina Luoghi, 10/11 ore 11:30 (richiesta di Stefano): box di ricerca anche dentro i filtri Regioni e Province (Comuni lo aveva già)
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk19' in h:
    print('mk19 già applicato'); raise SystemExit
def rep(a, b):
    global h
    assert h.count(a) == 1, (h.count(a), a[:70])
    h = h.replace(a, b)
rep("""<div class="mphead"><b>Regioni</b><span>puoi sceglierne più di una</span></div><div class="mlist">""",
    """<div class="mphead"><b>Regioni</b><span>puoi sceglierne più di una</span></div><input class="mpq" id="rq" type="search" placeholder="Cerca una regione…" autocomplete="off"><div class="mlist" id="rqlist">""")
rep("""<div class="mphead"><b>Province</b><span>puoi sceglierne più di una</span></div><div class="mlist">""",
    """<div class="mphead"><b>Province</b><span>puoi sceglierne più di una</span></div><input class="mpq" id="pq" type="search" placeholder="Cerca una provincia…" autocomplete="off"><div class="mlist" id="pqlist">""")
rep(""" const cq=$('cq');if(cq){""",
    """ /* mk19: filtro dal vivo delle voci di Regioni e Province; i titoli di regione restano solo se hanno province visibili */
 for(const [qi,li] of [['rq','rqlist'],['pq','pqlist']]){const q=$(qi);if(!q)continue;const ap=()=>{st['_'+qi]=q.value;const s=norm(q.value),L=$(li);let g=null,gv=false;
  for(const el of L.children){if(el.classList.contains('mgrp')){if(g)g.hidden=!gv;g=el;gv=false;continue}const t=el.querySelector('.t');const ok=!s||norm(t?t.textContent:el.textContent).includes(s);el.hidden=!ok;if(ok)gv=true}
  if(g)g.hidden=!gv};q.oninput=ap;if(st['_'+qi]){q.value=st['_'+qi];ap();}}
 const cq=$('cq');if(cq){""")
rep('.mpq{', '.mlist [hidden]{display:none!important}\n.mpq{')
open(F, 'w').write(h)
print('mk19 ok')
