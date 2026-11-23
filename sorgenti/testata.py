#!/usr/bin/env python3
"""Testata sul telefono in una riga sola (Stefano, 23/11/2026): i cerchi di Events e Dinners più grandi e senza
scritte, Metodo, Fonti ed EN/IT piccoli sulla stessa riga
(senza iconcine; il 🤝 Sostenitori qui si nasconde perché c'è già accanto a Guida/Mappa). Si guadagna una riga di spazio.
Stessa sera: tolta su tutti gli schermi la riga dei numeri (luoghi, gratuiti, comuni, con avvisi); resta il titolo
«Tutti i N luoghi», un po' più grande. iPad: Events, Dinners, Metodo, Fonti, Sostenitori ed EN in una riga;
PC: Sostenitori qui si nasconde perché accanto a Guida e Mappa c'è «Collaborano con noi». Solo stile. Scrive modello e pagina fra <!--TESTATA-TEL-->…<!--/TESTATA-TEL-->.
Si rilancia quante volte si vuole:  python3 sorgenti/testata.py"""
import os, re
RAD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSS = ('@media (max-width:759px){'
 'html .hero .ach-guide{display:flex!important;flex-wrap:nowrap!important;align-items:center!important;gap:10px!important;margin:12px 0 4px!important}'
 'html .ach-guide .ach-guide__btn{flex:none!important;width:52px!important;height:52px!important;min-width:0!important;padding:0!important;'
 'border:0!important;background:none!important;border-radius:50%!important;display:inline-grid!important;place-items:center!important}'
 'html .ach-guide .ach-guide__ico{display:block!important;width:52px!important;height:52px!important;margin:0!important}'
 'html .ach-guide .ach-guide__ico svg{width:52px!important;height:52px!important;display:block;filter:drop-shadow(0 2px 4px rgba(35,29,24,.15))}'
 'html .ach-guide .ach-guide__arr{display:none!important}'
 'html .ach-guide .ach-guide__txt{position:absolute!important;width:1px!important;height:1px!important;overflow:hidden!important;clip:rect(0 0 0 0)!important;white-space:nowrap!important}'
 'html .ach-guide .ach-meta{margin-left:auto!important;display:flex!important;flex-wrap:nowrap!important;align-items:center!important;gap:6px!important}'
 'html .ach-guide .ach-mlink,html .ach-guide #langbtn{height:34px!important;min-height:0!important;padding:0 11px!important;font:600 13px/1 var(--sans)!important;'
 'display:inline-flex!important;align-items:center!important;white-space:nowrap!important;width:auto!important}'
 'html .ach-guide .ach-mlink{font-size:0!important;gap:0!important}html .ach-guide .ach-mlink span{font-size:13px!important}'
 'html .ach-guide .ach-mlink[data-nav="sost"]{display:none!important}}'
 'html #stats{display:none!important}'
 'html .status #count,html #count{font-size:21px!important;line-height:1.2!important}'
 '@media (min-width:760px) and (max-width:1099px){html .hero .ach-guide{display:flex!important;flex-wrap:nowrap!important;align-items:center!important;gap:8px!important}'
 'html .ach-guide .ach-guide__btn{flex:none!important;padding:5px 14px 5px 5px!important;min-height:0!important;gap:8px!important}'
 'html .ach-guide .ach-guide__ico svg{width:30px!important;height:30px!important}html .ach-guide .ach-guide__txt small,html .ach-guide .ach-guide__arr{display:none!important}'
 'html .ach-guide .ach-meta{margin-left:auto!important;display:flex!important;flex-wrap:nowrap!important;gap:6px!important}'
 'html .ach-guide .ach-mlink,html .ach-guide #langbtn{height:40px!important;padding:0 12px!important;font-size:13.5px!important;white-space:nowrap!important}'
 'html .ach-guide .ach-mlink[data-nav="fonti"] .lg{display:none!important}html .ach-guide .ach-mlink[data-nav="fonti"] .sm{display:inline!important}}'
 '@media (min-width:1100px){html .ach-guide .ach-mlink[data-nav="sost"]{display:none!important}}'
 '@media (min-width:760px){html .status #count,html #count{font-size:24px!important}}')
BLOCCO = f'<!--TESTATA-TEL--><style id="testata-tel">{CSS}</style><!--/TESTATA-TEL-->'
for P in (os.path.join(RAD,'sorgenti','template.html'), os.path.join(RAD,'index.html')):
    t = open(P, encoding='utf-8').read()
    t = re.sub(r'<!--TESTATA-TEL-->.*?<!--/TESTATA-TEL-->', '', t, flags=re.S)
    assert t.count('</body>') == 1, P
    t = t.replace('</body>', BLOCCO + '</body>')
    open(P, 'w', encoding='utf-8').write(t)
    print('testata messa in', os.path.relpath(P, RAD))
