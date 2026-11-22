# Pagina Luoghi, 11/11 ore 13:25 (Stefano: «metodo e fonti portali a destra stessa riga»).
# Come nella Guida: Metodo e Fonti restano sulla riga delle schede ma allineati a destra.
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk23' in h:
    print('mk23 già applicato'); raise SystemExit
assert h.count('</style></head>') == 1
h = h.replace('</style></head>', """/* mk23 Metodo e Fonti a destra */
.tabs .seg{width:100%;flex:1 1 auto}
.tabs .seg a.tab[href$="#metodo"]{margin-left:auto}
</style></head>""")
open(F, 'w').write(h)
print('mk23 ok')
