# Pagina Luoghi, 11/11 ore 9:30 (Stefano: «i sotto filtri non si vedono bene, vulcano non compare su pc»).
# Le righe di filtri scorrevano di lato con la barra nascosta: col mouse le ultime voci (Vulcani, Grotte, Geositi,
# Sentieri, Panorami) restavano fuori dallo schermo. Su schermo largo ora vanno a capo e si vedono tutte.
# Su telefono restano a scorrimento col dito, come prima.
F = '/home/claude/achs-places-guide/filtri.html'
h = open(F).read()
if 'mk22' in h:
    print('mk22 già applicato'); raise SystemExit
assert h.count('</style></head>') == 1
h = h.replace('</style></head>', """/* mk22 sottofiltri visibili */
@media (min-width:760px){.frow{flex-wrap:wrap;overflow:visible;row-gap:6px}}
</style></head>""")
open(F, 'w').write(h)
print('mk22 ok')
