#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Divide foto.<impronta>.json in due parti, per non scaricarlo tutto all'avvio.

foto.json porta, per ognuna delle 16.646 foto, autore, licenza, indirizzo della
pagina su Wikimedia Commons e colore medio. Pesa 586 KB compressi e si
scaricava tutto all'avvio, mentre autore e licenza servono solo quando si apre
una scheda.

Da qui escono:
  fotom.<impronta>.json   il minimo per disegnare la scheda: per ogni luogo il
                          colore medio e, per le foto del comune, la chiave
                          dell'immagine. Una riga e' "#81807c" oppure
                          "#81807c @037032". Si scarica all'avvio.
  cr.<prov>.<impronta>.json  i crediti, una provincia per file: autore,
                          licenza, indirizzo e, per le foto del comune, il nome
                          del comune. Si scaricano all'apertura di una scheda.

foto.json resta dov'e': lo legge pagine.py per le pagine statiche.
Il manifest riceve le chiavi "fotom" e "cr".

Uso:  python3 sorgenti/foto_split.py
"""

import glob
import hashlib
import json
import os

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def scrivi(nome_base, dati):
    b = json.dumps(dati, ensure_ascii=False, separators=(",", ":")).encode()
    n = f"{nome_base}.{hashlib.sha256(b).hexdigest()[:10]}.json"
    with open(os.path.join(RADICE, n), "wb") as f:
        f.write(b)
    return n, len(b)


def main():
    man_p = os.path.join(RADICE, "manifest.json")
    with open(man_p, encoding="utf-8") as f:
        man = json.load(f)
    nome_foto = man.get("foto")
    if not nome_foto or not os.path.exists(os.path.join(RADICE, nome_foto)):
        raise SystemExit("foto.json non trovato nel manifest")
    with open(os.path.join(RADICE, nome_foto), encoding="utf-8") as f:
        foto = json.load(f)
    print(f"foto.json: {len(foto)} voci, "
          f"{os.path.getsize(os.path.join(RADICE, nome_foto))/1024:.0f} KB")

    mini = {}
    crediti = {}
    senza_colore = 0
    for k, v in foto.items():
        # v = [provincia, autore, licenza, indirizzo, colore] e, per le foto
        #     del comune, + [chiave immagine, nome del comune]
        prov = v[0] if v else ""
        colore = v[4] if len(v) > 4 and v[4] else ""
        if not colore:
            colore = "#8a8a88"          # grigio neutro: il posto non salta
            senza_colore += 1
        chiave = v[5] if len(v) > 5 and v[5] else ""
        mini[k] = colore + (" " + chiave if chiave else "")
        riga = [v[1] if len(v) > 1 else "", v[2] if len(v) > 2 else "",
                v[3] if len(v) > 3 else ""]
        if len(v) > 6 and v[6]:
            riga.append(v[6])
        crediti.setdefault(prov, {})[k] = riga

    # via i file vecchi, cosi' non restano impronte morte
    for vecchio in glob.glob(os.path.join(RADICE, "fotom.*.json")) + \
            glob.glob(os.path.join(RADICE, "cr.*.json")):
        os.remove(vecchio)

    n_mini, peso_mini = scrivi("fotom", mini)
    cr = {}
    peso_cr = 0
    for prov, d in sorted(crediti.items()):
        n, p = scrivi(f"cr.{prov}", d)
        cr[prov] = n
        peso_cr += p

    man["fotom"] = n_mini
    man["cr"] = cr
    with open(man_p, "w", encoding="utf-8") as f:
        json.dump(man, f, ensure_ascii=False)

    print(f"fotom: {n_mini}, {peso_mini/1024:.0f} KB non compressi, "
          f"{len(mini)} luoghi ({senza_colore} senza colore, messo il grigio)")
    print(f"crediti: {len(cr)} province, {peso_cr/1024:.0f} KB in tutto, "
          f"in media {peso_cr/max(1,len(cr))/1024:.0f} KB a provincia")


if __name__ == "__main__":
    main()
