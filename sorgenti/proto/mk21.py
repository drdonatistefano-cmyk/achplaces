# Pagina Luoghi, 10/11 ore 14:50 (coordinamento/AZZERA-FILTRI.md): «✕ Azzera i filtri» con il numero dei filtri attivi,
# un tocco toglie tutto (anche il testo della ricerca) e torna all'inizio. Su telefono la barra del conteggio è già fissa
# in fondo e resta sempre visibile; su schermo largo è ferma in alto e si aggiunge la pillola in fondo dopo 260 px.
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk21' in h:
    print('mk21 già applicato'); raise SystemExit
def rep(a, b):
    global h
    assert h.count(a) == 1, (h.count(a), a[:70])
    h = h.replace(a, b)
rep("""${n?`<button class="rst" data-a="${L?'resetL':'reset'}">↺ Azzera</button>`:''}""",
    """${n?`<button class="rst azzera" data-a="${L?'resetL':'reset'}" data-goatcounter-click="filtri/azzera-places" data-goatcounter-title="Azzera i filtri">✕ Azzera i filtri <span class="n">${n}</span></button>`:''}""")
rep("renderBar(){const n=nFil(),b=$('fbar'),L=$('vL').classList.contains('on');",
    "renderBar(){const n=nFil(),b=$('fbar'),L=$('vL').classList.contains('on');setTimeout(()=>mostraGiu(n),0);")
rep(" else if(d.a==='reset'){", " else if(d.a==='reset'){const qi=$('q');if(qi)qi.value='';")
rep("if(d.a==='resetL'){", "if(d.a==='resetL'){const qi=$('q');if(qi)qi.value='';window.scrollTo({top:0,behavior:'smooth'});")
rep("renderF();if(st.com!=null)renderL();if(!d.a||d.a!=='more')window.scrollTo(0,0)});",
    "renderF();if(st.com!=null)renderL();if(d.a==='reset')window.scrollTo({top:0,behavior:'smooth'});else if(!d.a||d.a!=='more')window.scrollTo(0,0)});")
rep('</style></head>', """/* mk21 azzeramento */
.rst.azzera{display:inline-flex;align-items:center;gap:6px;height:auto;padding:7px 12px;border:1px solid var(--terra);background:var(--paper);color:var(--terra);font-weight:600;font-size:13.5px;border-radius:999px}
.azzera .n,.giu .n{border-radius:999px;min-width:19px;height:19px;display:inline-grid;place-items:center;font-size:12px;line-height:1;padding:0 4px}
.azzera .n{background:var(--terra);color:var(--on)}
.giu{position:fixed;left:50%;transform:translateX(-50%);bottom:18px;z-index:40;border:0;background:var(--terra);color:var(--on);border-radius:999px;padding:12px 20px;font-size:15px;font-weight:700;box-shadow:0 6px 24px rgba(0,0,0,.28);display:inline-flex;align-items:center;gap:8px;transition:transform .18s ease,opacity .18s ease;white-space:nowrap;cursor:pointer}
.giu .n{background:var(--on);color:var(--terra)}
.giu.via{transform:translateX(-50%) translateY(90px);opacity:0;pointer-events:none}
.giu[hidden]{display:none}
@media (max-width:759px){.giu{display:none!important}.rst.azzera{padding:6px 10px;font-size:12.5px}}
</style></head>""")
rep('\n</body>', """
<button class="giu via" id="giu" type="button" hidden data-a="reset" data-goatcounter-click="filtri/azzera-places" data-goatcounter-title="Azzera i filtri (in fondo)">✕ Azzera i filtri <span class="n">0</span></button>
<script>/* mk21 */function mostraGiu(n){const g=document.getElementById('giu');if(!g)return;const L=document.getElementById('vL').classList.contains('on');g.dataset.a=L?'resetL':'reset';g.querySelector('.n').textContent=n;g.hidden=!n;giuVia()}
function giuVia(){const g=document.getElementById('giu');if(g&&!g.hidden)g.classList.toggle('via',window.scrollY<260)}addEventListener('scroll',giuVia,{passive:true});</script>
</body>""")
open(F, 'w').write(h)
print('mk21 ok')
