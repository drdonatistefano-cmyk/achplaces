#!/usr/bin/env python3
"""24/11/2026, Stefano (foto della mappa di Dinners): «elenco molto più compresso, togli il puntino rosso, sposta le foto
in modo che si possa stringere di molto, caratteristiche più in grassetto, colori della guida anche dentro la scheda,
un bottone per scorrere le schede della selezione sia nella mappa che nella guida; tendere a questa grafica con i colori
di Places».
Mappa (sorgenti/mappa_tpl.html e filtri.html):
- riga dell'elenco compatta: niente pallino colorato e niente freccia; nome, comune, caratteristiche in grassetto;
  Foto e Biglietti diventano tasti quadrati a destra (solo icona, con nome per i lettori di schermo); «Gratis» è
  un'etichetta verde fra le caratteristiche;
- scheda del luogo con i colori della guida (crema, bianco, verde) nel tema chiaro; tolto il 📍 rosso davanti al comune;
- «‹ Precedente · 14 di 80 · Successivo ›» per scorrere i luoghi dell'elenco (anche con le frecce della tastiera).
Guida (sorgenti/template.html e index.html): lo stesso «Precedente · N di M · Successivo» nella scheda, sui luoghi
della selezione in corso.
Rilanciabile: ogni sostituzione si fa solo se non è già fatta."""
import os, sys
RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
def cambia(t, a, b, nome, segno):
    if segno in t: return t
    n = t.count(a)
    if n != 1: sys.exit(f'{nome}: atteso 1 «{a[:70]}…», trovati {n}')
    return t.replace(a, b)

# ---------------------------------------------------------------- mappa
RIGA_A = ('return `<div class="row" style="--g:${g.c}"><button class="it" data-p="${pi}"><span class="ib"><i style="background:${g.c};box-shadow:0 0 14px ${g.c}"></i></span><span style="min-width:0;flex:1"><b>${esc(p.n)}</b><span class="d"><b class="cm">${esc(c.n)}</b> · ${esc(c.pr)}</span><span class="tg"><span style="--gc:${g.c};color:${g.c};border-color:${g.c}55">${g.l}${p.t[0]&&p.t[0]!==\'Altro\'?\' · \'+esc(p.t[0]):\'\'}</span>${tags}</span></span><svg width="16" height="16" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="rgba(210,220,245,.45)" stroke-width="1.8" stroke-linecap="round" style="flex:none;margin-top:14px"><path d="m9 18 6-6-6-6"/></svg></button><div class="rb">${tk}<a href="${photoUrl(p)}" target="_blank" rel="noopener">${ic(\'cam\')}Foto</a></div></div>`;};')
RIGA_B = ('/*compatta*/return `<div class="row" style="--g:${g.c}"><button class="it" data-p="${pi}"><b>${esc(p.n)}</b><span class="d"><b class="cm">${esc(c.n)}</b> · ${esc(c.pr)}</span><span class="tg"><span style="--gc:${g.c};color:${g.c};border-color:${g.c}55">${g.l}${p.t[0]&&p.t[0]!==\'Altro\'?\' · \'+esc(p.t[0]):\'\'}</span>${p.k===-2&&!tags.includes(\'Gratis\')?\'<span class="gr">Gratis</span>\':\'\'}${tags}</span></button>'
          '<div class="rb">${u?`<a class="tk" href="${esc(u[0])}" target="_blank" rel="noopener${u[1]?\' sponsored\':\'\'}" title="Biglietti" aria-label="Biglietti: ${esc(p.n)}">${ic(\'ticket\')}</a>`:\'\'}'
          '<a class="ph" href="${photoUrl(p)}" target="_blank" rel="noopener" title="Foto" aria-label="Foto: ${esc(p.n)}">${ic(\'cam\')}</a></div></div>`;};')
CSS_M = ('/*compatta 24/11*/'
  '.row{display:flex;align-items:stretch;contain-intrinsic-size:auto 82px;padding:0;margin:0 2px 8px;border-radius:14px}'
  '.it{flex:1;min-width:0;display:block;padding:10px 6px 10px 13px;border-radius:14px}.it b{font-size:15px;line-height:1.25}'
  '.it .d{margin-top:2px;font-size:13px}.it .tg{gap:4px;margin-top:6px}'
  '.it .tg span{font-weight:700;font-size:11.5px;padding:2px 8px;border-width:1.5px}'
  '.it .tg .gr{color:#3A7046;border-color:rgba(58,112,70,.45);background:#E3EFE5}'
  '.rb{flex-direction:column;justify-content:center;flex-wrap:nowrap;gap:4px;padding:6px 8px 6px 0}'
  '.rb a{width:44px;height:36px;padding:0;justify-content:center;border-radius:11px}.rb svg{width:18px;height:18px}'
  'html[data-t=carta] .row{background:#FFFDF9;border:1px solid #E6DCCB;box-shadow:0 1px 2px rgba(60,40,20,.05)}'
  'html[data-t=carta] .it:hover{background:#F6EFE4}'
  'html[data-t=carta] .rb a{background:#FFFDF9;border-color:#D9CCB8;color:#231D18}'
  'html[data-t=carta] .rb .tk{background:#E7F1EB;border-color:rgba(47,122,92,.4);color:#225C45}'
  'html[data-t=carta] #gs{--bg:#F6EFE4;--paper:#FFFDF9;--ink:#231D18;--mute:#756A5F;--faint:#7A6F63;--line:#E6DCCB;--terra:#2F7A5C;'
  '--terra-soft:#E7F1EB;--terra-ink:#225C45;--on:#fff;--warn:#8A5A00;--warn-soft:#FBEFD6;--bad:#A1261C;--bad-soft:#F8DFDC;--ok:#3A7046;'
  '--ok-soft:#E3EFE5;box-shadow:0 20px 60px rgba(60,40,20,.28)}'
  'html[data-t=carta] #gsscrim{background:rgba(35,29,24,.45)}'
  'html[data-t=carta] #gs .act.map{background:var(--terra-soft);border-color:rgba(47,122,92,.4);color:var(--terra-ink)}'
  'html[data-t=carta] #gs .skel{background:linear-gradient(90deg,#EFE7DA,#F6EFE4,#EFE7DA);background-size:200% 100%}'
  'html[data-t=carta] #gs .gtag{color:color-mix(in srgb,var(--g) 50%,#1A120C)}'
  '#gs .ctag{color:var(--terra-ink)}'
  'html[data-t=carta] #gs .unbox{border-color:rgba(47,122,92,.35);background:#E7F1EB}html[data-t=carta] #gs .unbox small{color:#225C45}'
  '.gnav{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:12px 0 6px}'
  '.gnav button{height:40px;padding:0 14px;border-radius:999px;border:1px solid var(--terra,#2F7A5C);background:var(--terra-soft,#E7F1EB);'
  'color:var(--terra-ink,#225C45);font:700 14px/1 var(--sans,system-ui);cursor:pointer}.gnav button:disabled{opacity:.35;cursor:default}'
  '.gnav span{font-weight:700;font-size:13.5px;color:var(--mute)}'
  '\n.note{font-size:11px;')
NAV_M = ('/*naviga*/function navM(pi){const L=window.LISTA||[],i=L.indexOf(pi);if(i<0||L.length<2)return \'\';'
         'return `<nav class="gnav" aria-label="Luoghi dell\'elenco"><button type="button" data-nav="${L[i-1]??\'\'}"${i?\'\':\' disabled\'}>‹ Precedente</button>'
         '<span>${i+1} di ${L.length}</span><button type="button" data-nav="${L[i+1]??\'\'}"${i<L.length-1?\'\':\' disabled\'}>Successivo ›</button></nav>`;}\n'
         'function apri(pi){aperta=pi;')
VAI_M = ("$('gsscrim').onclick=chiudi;/*naviga*/$('gs').addEventListener('click',e=>{const b=e.target.closest('[data-nav]');"
         "if(b&&!b.disabled&&b.dataset.nav!==''){const lf=lastFocus;apri(+b.dataset.nav);lastFocus=lf;}});"
         "addEventListener('keydown',e=>{if(aperta==null||(e.key!=='ArrowRight'&&e.key!=='ArrowLeft'))return;const L=window.LISTA||[],i=L.indexOf(aperta),"
         "j=L[i+(e.key==='ArrowRight'?1:-1)];if(i>=0&&j!=null){const lf=lastFocus;apri(j);lastFocus=lf;}});")
for nome in ('sorgenti/mappa_tpl.html', 'filtri.html'):
    P = os.path.join(RAD, nome); t = open(P, encoding='utf-8').read()
    t = cambia(t, RIGA_A, RIGA_B, nome, '/*compatta*/return')
    t = cambia(t, '\n.note{font-size:11px;', CSS_M, nome, '/*compatta 24/11*/')
    t = cambia(t, 'function apri(pi){aperta=pi;', NAV_M, nome, '/*naviga*/function navM')
    t = cambia(t, "$('gsscrim').onclick=chiudi;", VAI_M, nome, "/*naviga*/$('gs')")
    t = cambia(t, "const tags=[...p.fl].filter(x=>FLAG[x]).slice(0,2)", "const tags=[...p.fl].filter(x=>FLAG[x]).slice(0,1)/*1 sola*/", nome, '/*1 sola*/')
    t = cambia(t, '<span class="ic" aria-hidden="true">📍</span><small>Indirizzo', '<span class="ic" aria-hidden="true">🗺️</span><small>Indirizzo', nome, '🗺️</span><small>Indirizzo')
    t = cambia(t, "const box=$('items'),job=++LJ;", "window.LISTA=out;const box=$('items'),job=++LJ;", nome, 'window.LISTA=out;')
    t = cambia(t, 'sh.innerHTML=testata(p)+`<div class="ctag">📍 ${esc(c.n)} (${esc(c.pr)})</div>',
               'sh.innerHTML=testata(p)+navM(pi)+`<div class="ctag">${esc(c.n)} (${esc(c.pr)})</div>', nome, 'testata(p)+navM(pi)+`<div class="ctag">${')
    t = cambia(t, 'sh.innerHTML=testata(p)+`<div class="ctag" style="margin-top:4px">📍 ${esc(c.n)} (${esc(sigla||c.pr)})</div>',
               'sh.innerHTML=testata(p)+navM(pi)+`<div class="ctag" style="margin-top:4px">${esc(c.n)} (${esc(sigla||c.pr)})</div>', nome, 'navM(pi)+`<div class="ctag" style')
    open(P, 'w', encoding='utf-8').write(t); print(nome, 'ok')

# ---------------------------------------------------------------- guida
NAV_G = ('/*naviga*/function gnav(id){const i=CUR.findIndex(x=>x.id===id);if(i<0||CUR.length<2)return "";'
         'return `<nav class="gnav" aria-label="Luoghi della selezione"><button type="button" data-gnav="${i?esc(CUR[i-1].id):""}"${i?"":" disabled"}>‹ Precedente</button>'
         '<span>${(i+1).toLocaleString("it-IT")} di ${CUR.length.toLocaleString("it-IT")}</span>'
         '<button type="button" data-gnav="${i<CUR.length-1?esc(CUR[i+1].id):""}"${i<CUR.length-1?"":" disabled"}>Successivo ›</button></nav>`;}\n'
         'document.addEventListener("click",e=>{const b=e.target.closest("#sheet [data-gnav]");if(b&&!b.disabled&&b.dataset.gnav){const lf=lastFocus;openSheet(b.dataset.gnav,lf);}});\n'
         'document.addEventListener("keydown",e=>{if(!$("sheet").classList.contains("open")||(e.key!=="ArrowRight"&&e.key!=="ArrowLeft"))return;'
         'const b=$("sheet").querySelector(`.gnav button:${e.key==="ArrowRight"?"last-of-type":"first-of-type"}`);if(b&&!b.disabled)b.click();});\n'
         'function openSheet(id,from){')
CSS_G = ('/*naviga*/.gnav{display:flex;align-items:center;justify-content:space-between;gap:8px;margin:12px 0 4px}'
         '.gnav button{height:40px;padding:0 14px;border-radius:999px;border:1px solid var(--terra);background:var(--terra-soft);color:var(--terra-ink);'
         'font:700 14px/1 var(--sans);cursor:pointer}.gnav button:disabled{opacity:.35;cursor:default}.gnav span{font-weight:700;font-size:13.5px;color:var(--mute)}\n</style>')
for nome in ('sorgenti/template.html', 'index.html'):
    P = os.path.join(RAD, nome); t = open(P, encoding='utf-8').read()
    t = cambia(t, 'function openSheet(id,from){', NAV_G, nome, '/*naviga*/function gnav')
    t = cambia(t, '</div></div>\n    <div class="meta smeta">${tg}</div>', '</div></div>\n    ${gnav(p.id)}<div class="meta smeta">${tg}</div>', nome, '${gnav(p.id)}')
    i = t.find('</style>')
    if '/*naviga*/.gnav' not in t: t = t[:i] + CSS_G + t[i + len('</style>'):]
    open(P, 'w', encoding='utf-8').write(t); print(nome, 'ok')
