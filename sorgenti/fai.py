#!/usr/bin/env python3
"""Beni FAI (28/11/2026, Stefano: «raccogli tutti i luoghi FAI, metti un bottone come UNESCO»).

Mette il pulsante «Beni FAI» accanto a UNESCO, Borghi più belli e Bandiere Arancioni, nella guida e nella mappa:
  - guida (template.html e la pagina index.html): pulsante rapido, voce nei filtri «Ideale per», etichetta FAI sulla
    scheda breve e su quella aperta, riga «FAI» con il link alla pagina ufficiale del bene;
  - mappa (mappa_tpl.html e la pagina filtri.html): pulsante «Beni FAI» in «Al volo» ed etichetta FAI nell'elenco.
Icona a tratto «scudo» come le altre: sorgenti/grafica/icone.py (poi grafica/applica.py).
I dati: nel campo 9 di data/spec-*.txt l'extra «fai=URL della scheda su fondoambiente.it» (build.py lo porta in p.fai;
mappa_build.py ne fa la lettera «f»). Rilanciabile: ogni sostituzione si fa una volta sola; se un pezzo atteso non c'è
il programma si ferma senza scrivere nulla, così non resta una pagina a metà.
Uso: python3 sorgenti/fai.py [--prova]   (--prova dice che cosa cambierebbe, senza scrivere)
"""
import os, sys

QUI = os.path.dirname(os.path.abspath(__file__))
CASA = os.path.dirname(QUI)
EM = "🛡️"

GUIDA = [  # (pezzo che c'è oggi, pezzo nuovo); il nuovo contiene sempre il segno «fai»
    # come UNESCO: nel pannello dei filtri sta nella fila dei riconoscimenti, non anche in «Ideale per»
    ('#g-ideal .qc[aria-label*="UNESCO"],', '#g-ideal .qc[aria-label*="UNESCO"],#g-ideal .qc[aria-label*="Beni FAI"],'),
    ('["unesco","🌍","UNESCO","UNESCO"],',
     f'["unesco","🌍","UNESCO","UNESCO"],["fai","{EM}","Beni FAI","FAI"],'),
    ('const idealOk=(p,x)=>x==="rain"?p.indoor:',
     'const idealOk=(p,x)=>x==="fai"?!!p.fai:x==="rain"?p.indoor:'),
    ('const quick=[["unesco","🌍","UNESCO"],',
     f'const quick=[["unesco","🌍","UNESCO"],["fai","{EM}","Beni FAI"],'),
    ('f={free:0,card:0,alerts:0,indoor:0,unesco:0,borghi:0,arancione:0};for(const p of CUR){',
     'f={free:0,card:0,alerts:0,indoor:0,unesco:0,fai:0,borghi:0,arancione:0};for(const p of CUR){if(p.fai)f.fai++;'),
    ('(p.unesco?`<span class="mst"><i class="em">🌍</i> UNESCO</span>`:"")',
     f'(p.unesco?`<span class="mst"><i class="em">🌍</i> UNESCO</span>`:"")+(p.fai?`<span class="mst"><i class="em">{EM}</i> FAI</span>`:"")'),
    ('(p.unesco?`<span class="mst">🌍 UNESCO</span>`:"")',
     f'(p.unesco?`<span class="mst">🌍 UNESCO</span>`:"")+(p.fai?`<span class="mst">{EM} FAI</span>`:"")'),
    ('${p.wh?`<div class="srow"><span>UNESCO</span>',
     '${p.fai?`<div class="srow"><span>FAI</span><div><a class="flink" href="${esc(p.fai)}" target="_blank" rel="noopener" data-goatcounter-click="fai-bene">Bene del FAI, pagina ufficiale ↗</a></div></div>`:""}${p.wh?`<div class="srow"><span>UNESCO</span>'),
]
MAPPA = [
    ("un:p.fl.includes('u'),", "un:p.fl.includes('u'),fa:p.fl.includes('f'),"),
    ("const QK=[['g','Gratis'],['u','UNESCO'],",
     "const QK=[['g','Gratis'],['u','UNESCO'],['f','Beni FAI'],"),
    ("const FLAG={g:'Gratis',u:'UNESCO',",
     "const FLAG={g:'Gratis',u:'UNESCO',f:'FAI',"),
    ("(d.un?'<span class=\"mst\">🌍 UNESCO</span>':'')",
     f"(d.un?'<span class=\"mst\">🌍 UNESCO</span>':'')+(d.fa?'<span class=\"mst\">{EM} FAI</span>':'')"),
]


def applica(percorso, pezzi, prova):
    t = open(percorso, encoding="utf-8").read()
    n = 0
    for vecchio, nuovo in pezzi:
        if nuovo in t:
            continue  # già fatto
        if t.count(vecchio) != 1:
            raise SystemExit(f"FERMO: in {os.path.relpath(percorso, CASA)} il pezzo atteso c'è {t.count(vecchio)} volte: {vecchio[:60]}…")
        t = t.replace(vecchio, nuovo, 1); n += 1
    if n and not prova:
        open(percorso, "w", encoding="utf-8").write(t)
    print(f"{os.path.relpath(percorso, CASA)}: {n} modifiche{' (prova)' if prova else ''}")
    return n


def main():
    prova = "--prova" in sys.argv
    for p in (os.path.join(QUI, "template.html"), os.path.join(CASA, "index.html")):
        applica(p, GUIDA, prova)
    for p in (os.path.join(QUI, "mappa_tpl.html"), os.path.join(CASA, "filtri.html")):
        if os.path.exists(p):
            applica(p, MAPPA, prova)


if __name__ == "__main__":
    main()
