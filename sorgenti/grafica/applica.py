#!/usr/bin/env python3
"""Mette la grafica istituzionale (sorgenti/grafica/istituzionale.css) dentro sorgenti/template.html e index.html.
Il foglio di stile va dentro la pagina (niente file in più da scaricare) fra due segni:
<!--ISTITUZIONALE-->...<!--/ISTITUZIONALE-->, subito prima di </head>. Rilanciare dopo ogni modifica del .css:
    python3 sorgenti/grafica/applica.py
Mette anche la coccarda del logo al posto della sagoma dell'Italia nell'intestazione e il colore della barra del browser."""
import os
import re

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(os.path.dirname(QUI))
# il modello e la pagina pubblicata (i flussi lavorano sulla pagina, non la rifanno dal modello)
PAGINE = [os.path.join(RADICE, "sorgenti", "template.html"), os.path.join(RADICE, "index.html")]
css = open(os.path.join(QUI, "istituzionale.css"), encoding="utf-8").read().strip()
# icone moderne dei filtri (generate da icone.py)
if os.path.exists(os.path.join(QUI, "icone.css")):
    css += "\n" + open(os.path.join(QUI, "icone.css"), encoding="utf-8").read()
# toglie i commenti e gli a capo inutili: pesa meno
css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
css = re.sub(r"\s*\n\s*", "", css)

LOGO = ('<svg class="italy logo" viewBox="0 0 100 100" width="42" height="42" role="img" aria-label="Ach\'s Places">'
        '<circle cx="50" cy="50" r="48" fill="#2f7a5c"/><circle cx="50" cy="50" r="42" fill="none" stroke="#f6efe4" stroke-width="2.4"/>'
        '<g transform="translate(17 15) scale(.66)" stroke="#f6efe4" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none">'
        '<path d="M50 86C50 86 24 58 24 40a26 26 0 0 1 52 0C76 58 50 86 50 86Z"/><circle cx="50" cy="40" r="5" fill="#f6efe4"/></g></svg>')
BLOCCO = ('<!--ISTITUZIONALE-->'
          '<link rel="preload" href="/font/space-grotesk-700.woff2" as="font" type="font/woff2" crossorigin>'
          f'<style id="istituzionale">{css}</style><!--/ISTITUZIONALE-->')

for TPL in PAGINE:
    t = open(TPL, encoding="utf-8").read()
    if "<!--ISTITUZIONALE-->" in t:
        t = re.sub(r"<!--ISTITUZIONALE-->.*?<!--/ISTITUZIONALE-->", lambda m: BLOCCO, t, flags=re.S)
    else:
        assert t.count("</head>") == 1
        t = t.replace("</head>", BLOCCO + "\n</head>")
    # coccarda nell'intestazione (la prima volta sostituisce la sagoma dell'Italia)
    t = re.sub(r'<div class="kick"><svg class="italy[^"]*".*?</svg>', lambda m: '<div class="kick">' + LOGO, t, count=1, flags=re.S)
    # marchio come Dinners: nome della guida (resta quello di prima, che cambia col comune) e motto sotto, italiano e inglese
    if 'class="marca"' not in t:
        t = re.sub(r'(<div class="kick"><svg class="italy logo".*?</svg>)(<span id="kicktxt">[^<]*</span>)',
                   lambda m: m.group(1) + '<span class="marca">' + m.group(2) + '<small class="motto"><span class="it">Guida ai luoghi da visitare in Italia</span>'
                   '<span class="en">The guide to places to visit in Italy</span></small></span>', t, count=1, flags=re.S)
    # emoji dei pulsanti Ingresso / Ideale per / Tempo e dei riconoscimenti dentro <i class="em">, per poterle disegnare come icone
    for em, resto in [("🎟️", " Ingresso <span"), ("✨", " Ideale per <span"), ("⏱️", " Tempo <span")]:
        t = t.replace('aria-expanded="false">' + em + resto, 'aria-expanded="false"><i class="em" aria-hidden="true">' + em + '</i>' + resto, 1)
    t = t.replace('aria-pressed="${S.ideal.has(k)}">${em} ${l}</button>', 'aria-pressed="${S.ideal.has(k)}"><i class="em" aria-hidden="true">${em}</i> ${l}</button>', 1)
    # sul telefono «Da verificare sul sito» si legge «Da verificare», come le altre voci accorciate
    t = t.replace('"Prezzo da verificare":"Da verificare"', '"Prezzo da verificare":"Da verificare","Da verificare sul sito":"Da verificare"', 1) if '"Da verificare sul sito":"Da verificare"' not in t else t
    # barra del browser: crema di giorno, scura di notte
    t = re.sub(r'<meta name="theme-color"[^>]*>(?:<meta name="theme-color"[^>]*>)?',
               '<meta name="theme-color" content="#f6efe4" media="(prefers-color-scheme: light)">'
               '<meta name="theme-color" content="#141210" media="(prefers-color-scheme: dark)">', t, count=1)
    open(TPL, "w", encoding="utf-8").write(t)
print("grafica istituzionale messa nel modello:", len(css), "caratteri di stile")
