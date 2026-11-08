# v14 -> v15: pulsanti uniformi con icone a linea, come la Guida (8/11/2026)
from icone import IC_JS, IC_CSS
h=open('v14_head.html').read(); t=open('v14_tail.html').read()
def R(s,a,b,n=1):
    assert s.count(a)==n,(a,s.count(a)); return s.replace(a,b)
t=R(t,'target="_blank" rel="noopener">📷 Foto</a>${showC?`<button class="cb" data-c="${p[1]}">🏘️ ${esc(c[0])}</button>`:\'\'}<button class="cb pri" data-p="${p._i}">Apri ›</button>',
     'target="_blank" rel="noopener">${ic(\'cam\')}Foto</a>${showC?`<button class="cb" data-c="${p[1]}">${ic(\'pin\')}${esc(c[0])}</button>`:\'\'}<button class="cb pri" data-p="${p._i}">Apri${ic(\'chev\')}</button>')
t=R(t,'target="_blank" rel="noopener">🧭 Come arrivare</a>','target="_blank" rel="noopener">${ic(\'nav\')}Come arrivare</a>')
t=R(t,'target="_blank" rel="noopener">📷 Foto</a><a class="act wide" href="index.html#${c[5]}">🧭 Scheda completa nella Guida: ${esc(c[0])}</a>',
     'target="_blank" rel="noopener">${ic(\'cam\')}Foto</a><a class="act wide" href="index.html#${c[5]}">${ic(\'book\')}Scheda completa nella Guida: ${esc(c[0])}</a>')
t=R(t,'<button class="back" data-a="tolist">‹ Torna all\'elenco</button><a class="toG" href="index.html#${c[5]}">🧭 Apri nella Guida</a>',
     '<button class="back" data-a="tolist">${ic(\'back\')}Torna all\'elenco</button><a class="toG" href="index.html#${c[5]}">${ic(\'book\')}Apri nella Guida</a>')
t=IC_JS+t
css=IC_CSS+""".cb{box-shadow:0 1px 2px rgba(35,29,24,.05);transition:background .15s,border-color .15s,transform .1s;gap:6px}
.cb .ic{color:var(--terra)}
.cb:hover{background:var(--terra-soft);border-color:color-mix(in srgb,var(--terra) 30%,var(--line))}
.cb:active,.act:active,.toG:active{transform:scale(.97)}
.cb.pri{background:var(--terra);border-color:var(--terra);color:#fff;gap:2px;padding-right:9px}
.cb.pri .ic{color:#fff;width:16px;height:16px}
.act{gap:8px;box-shadow:0 1px 2px rgba(35,29,24,.05);transition:background .15s,border-color .15s,transform .1s}
.act .ic{color:var(--terra)}
.act:hover{background:var(--terra-soft)}
.act.pri .ic{color:#fff}
.act.pri:hover{background:var(--terra);filter:brightness(1.08)}
.back{gap:2px;padding-left:9px}.back .ic{color:var(--paper)}
.toG{display:inline-flex;align-items:center;gap:6px}.toG .ic{color:var(--terra)}
"""
k=h.rindex('</style>');h=h[:k]+css+h[k:]
open('v15_head.html','w').write(h);open('v15_tail.html','w').write(t);print('v15 ok')
