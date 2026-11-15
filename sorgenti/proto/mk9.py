t=open('v8_tail.html').read();h=open('v8_head.html').read()
def H(a,b):
    global h
    assert a in h,a[:70]; h=h.replace(a,b,1)
H('<button class="tab on" id="tabF" data-tab="F">🔎 <span class="t">Luoghi</span></button><button class="tab" id="tabL" data-tab="L" disabled>📍 <span class="t" id="tabLt">Elenco</span></button>',
  '<button class="tab on" id="tabF" data-tab="F">🔎 <span class="t">Luoghi</span></button><button class="tab" id="tabL" data-tab="L" disabled>📍 <span class="t" id="tabLt">Elenco</span></button><a class="tab gl sm" href="index.html#metodo" aria-label="Metodo">📐 <span class="t">Metodo</span></a><a class="tab gl sm" href="index.html#fonti" aria-label="Fonti">📚 <span class="t">Fonti</span></a>')
H('</style>',r""".tab.gl{text-decoration:none}
.tab.sm{flex:0 1 auto;padding:0 9px}
@media(max-width:560px){.tab{font-size:12.5px;gap:3px;padding:0 4px}.tab.sm{padding:0 4px}}
@media(max-width:350px){.tab.sm .t{display:none}.tab.sm{padding:0 8px}}
.com h4,.card h3,.reg>h2,.fh,.sheet h2,.hero h1,h1{font-weight:800}
.pv,.pvs{font-weight:800;color:var(--ink2)}
</style>""")
open('v9_head.html','w').write(h);open('v9_tail.html','w').write(t)
print('v9 ok')
