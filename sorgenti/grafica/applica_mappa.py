#!/usr/bin/env python3
"""Grafica istituzionale sulla Mappa (sorgenti/mappa_tpl.html e filtri.html, la pagina pubblicata).
Il tema chiaro «Carta» (quello che si apre per primo) prende il verde del logo al posto del verde acqua;
nella testata del pannello la coccarda del logo al posto della goccia; titoli col carattere del logo.
Gli altri temi (Blu notte, Ardesia, Oceano, Notte) restano com'erano. Si può rilanciare: rifà sempre lo stesso.
    python3 sorgenti/grafica/applica_mappa.py"""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))
PAGINE = [os.path.join(RADICE, "sorgenti", "mappa_tpl.html"), os.path.join(RADICE, "filtri.html")]

# verde acqua di «Carta» -> verdi del logo (stessa chiarezza, contrasto AA sul bianco)
COLORI = [("#0E8F82", "#2F7A5C"), ("#0e8f82", "#2f7a5c"), ("#0B6E63", "#235E46"), ("#0B5F55", "#225C45"),
          ("#0B4F47", "#1D4A38"), ("#0B3F39", "#1D4A38"), ("14,143,130", "47,122,92"), ("#E6F4F1", "#E7F1EB")]
GOCCIA = re.compile(r'<svg width="26" height="26" viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="#5EEAD4".*?</svg>', re.S)
LOGO = ('<svg class="logo" width="34" height="34" viewBox="0 0 100 100" aria-hidden="true">'
        '<circle cx="50" cy="50" r="48" fill="#2f7a5c"/><circle cx="50" cy="50" r="42" fill="none" stroke="#f6efe4" stroke-width="2.4"/>'
        '<g transform="translate(17 15) scale(.66)" stroke="#f6efe4" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        '<path d="M50 86C50 86 24 58 24 40a26 26 0 0 1 52 0C76 58 50 86 50 86Z"/><circle cx="50" cy="40" r="5" fill="#f6efe4"/></g></svg>')
STILE = ('<!--ISTITUZIONALE--><style id="istituzionale">'
         'html[data-t=carta]{--bg:#efe7da;--bg1:#f6efe4;--ln:#e3d8c6}'
         'html[data-t=carta] .gl{box-shadow:0 1px 2px rgba(35,29,24,.05),0 10px 28px -10px rgba(35,29,24,.18)}'
         'html[data-t=carta] .row:hover{border-color:#2f7a5c}'
         'html[data-t=carta] #levels button.on{color:#225c45;box-shadow:0 1px 2px rgba(35,29,24,.1),0 0 0 1px #e3d8c6}'
         'html[data-t=carta] #nv,html[data-t=carta] #sheet h2{color:#231d18}'
         '</style><!--/ISTITUZIONALE-->')

for p in PAGINE:
    t = open(p, encoding="utf-8").read()
    for a, b in COLORI:
        t = t.replace(a, b)
    t = GOCCIA.sub(lambda m: LOGO, t, count=1)
    if "<!--ISTITUZIONALE-->" in t:
        t = re.sub(r"<!--ISTITUZIONALE-->.*?<!--/ISTITUZIONALE-->", lambda m: STILE, t, flags=re.S)
    else:
        assert t.count("</head>") == 1, p
        t = t.replace("</head>", STILE + "\n</head>")
    open(p, "w", encoding="utf-8").write(t)
    print("mappa:", os.path.relpath(p, RADICE), "aggiornata")
