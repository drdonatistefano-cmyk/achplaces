#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Riapplica alla pagina di Places le correzioni di velocita' del 10/11/2026.

build.py rigenera index.html da template.html, che ha ancora il codice di
prima: senza questo passo, alla prima costruzione la guida tornerebbe a
scaricare 11,5 MB a visita (gli album delle foto per provincia, l'indice
della ricerca, le descrizioni di quattro province) invece di 0,8.

Le correzioni stanno in sorgenti/velocizza.json come coppie vecchio/nuovo.
Il programma guarda in che stato e' la pagina:
  - gia' corretta      -> non tocca niente
  - quella del modello -> applica tutte le coppie, ognuna deve combaciare una
                          volta sola, poi controlla il risultato
  - qualunque altra    -> si ferma con un errore e NON scrive: vuol dire che
                          il modello e' cambiato in quei punti e le correzioni
                          vanno riportate a mano

Uso:  python3 sorgenti/velocizza.py [pagina]      (predefinita: index.html)
Esce 0 se la pagina e' corretta (prima o dopo), 2 se non ha potuto correggerla.
"""
import json
import os
import sys

QUI = os.path.dirname(os.path.abspath(__file__))
RADICE = os.path.dirname(QUI)

NUOVI = ("fotoSrc(", "anticipa(", "caricaCred(", "FOTOM")     # segni della pagina corretta
VECCHI = ("FALB", "FALBQ")                                    # segni di quella del modello


def main():
    pagina = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RADICE, "index.html")
    t = open(pagina, encoding="utf-8").read()
    ha_nuovi = [k for k in NUOVI if k in t]
    ha_vecchi = [k for k in VECCHI if k in t]

    if len(ha_nuovi) == len(NUOVI) and not ha_vecchi:
        print("velocizza: la pagina e' gia' corretta, niente da fare")
        return 0
    if ha_nuovi and ha_vecchi or (not ha_nuovi and not ha_vecchi):
        print(f"velocizza: ERRORE, pagina in uno stato che non riconosco "
              f"(segni nuovi {ha_nuovi}, segni vecchi {ha_vecchi}). Non scrivo niente.")
        return 2

    coppie = json.load(open(os.path.join(QUI, "velocizza.json"), encoding="utf-8"))["sostituzioni"]
    for i, c in enumerate(coppie, 1):
        n = t.count(c["vecchio"])
        if n != 1:
            print(f"velocizza: ERRORE, la correzione {i} di {len(coppie)} combacia {n} volte "
                  f"invece di una: il modello e' cambiato in quel punto "
                  f"(«{c['vecchio'][:70]}»). Non scrivo niente: le correzioni vanno "
                  f"riportate a mano in template.html.")
            return 2
        t = t.replace(c["vecchio"], c["nuovo"], 1)

    if not all(k in t for k in NUOVI) or any(k in t for k in VECCHI):
        print("velocizza: ERRORE, dopo le correzioni la pagina non e' come dovrebbe. Non scrivo niente.")
        return 2
    with open(pagina, "w", encoding="utf-8") as f:
        f.write(t)
    print(f"velocizza: applicate {len(coppie)} correzioni, la pagina e' di nuovo quella veloce")
    return 0


if __name__ == "__main__":
    sys.exit(main())
