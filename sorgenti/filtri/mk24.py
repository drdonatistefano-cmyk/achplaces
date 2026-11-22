# Pagina Luoghi, 12/11 ore 20:55 (Stefano): gli aggregatori (Luoghi, Comuni, Province, Regioni, Nord-Sud) salgono nella riga
# di Guida e Luoghi, allineati a destra; Metodo e Fonti restano in fondo alla riga. La Guida apre questa pagina con #g=c ecc.
# Passando con il mouse sopra un filtro col nome tagliato compare il nome intero.
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk24' in h:
    print('mk24 già applicato'); raise SystemExit
def rep(a, b):
    global h
    assert h.count(a) == 1, (h.count(a), a[:60]); h = h.replace(a, b)
rep('<a class="tab gl sm" href="index.html#metodo" aria-label="Metodo">',
    '<span class="grp2" role="group" aria-label="Raggruppa per"><button class="g2" data-g="p">📍 <span class="t">Luoghi</span></button><button class="g2" data-g="c">🏘️ <span class="t">Comuni</span></button><button class="g2" data-g="v">🗺️ <span class="t">Province</span></button><button class="g2" data-g="r">🧭 <span class="t">Regioni</span></button><button class="g2" data-g="a">🇮🇹 <span class="t">Nord-Sud</span></button></span><a class="tab gl sm" href="index.html#metodo" aria-label="Metodo">')
rep('</style></head>', """/* mk24 aggregatori nella riga in alto */
.tabs .seg a.tab[href$="#metodo"]{margin-left:0}
.grp2{margin-left:auto;display:flex;gap:2px;padding:3px;border-radius:999px;background:color-mix(in srgb,var(--ink) 6%,var(--bg));border:1px solid var(--line);flex:none}
.grp2 .g2{height:32px;padding:0 12px;border:0;border-radius:999px;background:transparent;color:var(--mute);font:650 13px var(--sans);cursor:pointer;white-space:nowrap}
.grp2 .g2:hover{color:var(--ink);background:var(--paper)}
.grp2 .g2.on{background:var(--paper);color:var(--ink);box-shadow:0 1px 3px rgba(0,0,0,.12)}
#grp{display:none!important}
@media (max-width:759px){.tabs .seg{overflow-x:auto;scrollbar-width:none;flex-wrap:nowrap}.tabs .seg::-webkit-scrollbar{display:none}.grp2 .g2{padding:0 9px;font-size:12.5px}}
.tipz{position:fixed;z-index:9999;left:0;top:0;transform:translate(-50%,-100%) translateY(6px);opacity:0;pointer-events:none;background:var(--ink);color:var(--paper);font:650 13px/1.2 var(--sans);padding:7px 11px;border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.22);transition:opacity .14s,transform .14s;white-space:nowrap}
.tipz::after{content:"";position:absolute;left:50%;top:100%;margin-left:-6px;border:6px solid transparent;border-top-color:var(--ink)}
.tipz.on{opacity:1;transform:translate(-50%,-100%) translateY(-2px)}
</style></head>""")
i = h.rfind('</body>')
h = h[:i] + """<script>/* mk24 */
(function(){const top=[...document.querySelectorAll('.grp2 .g2')];
  const sync=()=>{const on=document.querySelector('#grp button.on');const g=on?on.dataset.g:'c';top.forEach(b=>{b.classList.toggle('on',b.dataset.g===g);b.setAttribute('aria-pressed',b.dataset.g===g);});};
  document.addEventListener('click',()=>setTimeout(sync,0));
  const m=location.hash.match(/g=([pcvra])/);
  const avvia=()=>{if(!document.querySelector('#grp button')){setTimeout(avvia,60);return;}
    if(m){const b=document.querySelector('#grp button[data-g="'+m[1]+'"]');if(b&&!b.classList.contains('on'))b.click();history.replaceState(null,'',location.pathname);}sync();};avvia();
  const t=document.createElement('div');t.className='tipz';t.setAttribute('aria-hidden','true');document.body.appendChild(t);let cur=null;const hide=()=>{cur=null;t.classList.remove('on');};
  document.addEventListener('pointerover',e=>{if(e.pointerType&&e.pointerType!=='mouse')return;const b=e.target.closest('#vF button,.grp2 button,.tabs .tab');if(!b){if(cur)hide();return;}if(b===cur)return;cur=b;
    const sp=[...b.querySelectorAll('span')],corto=sp.some(s=>s.scrollWidth>s.clientWidth+1)||b.scrollWidth>b.clientWidth+1;
    if(!corto){t.classList.remove('on');return;}const nome=(b.getAttribute('aria-label')||b.textContent).replace(/\\s+/g,' ').trim();
    t.textContent=nome;const r=b.getBoundingClientRect();t.style.left=(r.left+r.width/2)+'px';t.style.top=(r.top-6)+'px';t.classList.add('on');});
  document.addEventListener('pointerout',e=>{if(cur&&!(e.relatedTarget&&cur.contains(e.relatedTarget)))hide();});
  addEventListener('scroll',hide,{passive:true});document.addEventListener('click',hide,true);})();
</script>
""" + h[i:]
open(F, 'w').write(h)
print('mk24 ok')
