# v13 -> v14: velatura leggera delle card per categoria (colori della guida)
h=open('v13_head.html').read()
css='.card{background:color-mix(in srgb,var(--cc) 12%,var(--paper))}\n'
i=h.rfind('</style>');h=h[:i]+css+h[i:]
open('v14_head.html','w').write(h)
open('v14_tail.html','w').write(open('v13_tail.html').read())
