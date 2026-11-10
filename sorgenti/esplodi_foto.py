#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scompone gli album di miniature in un file per foto.

Prima: le miniature stavano dentro fa.<provincia>.<impronta>.json, in base64.
Per mostrare tre schede di Roma il telefono scaricava 2,6 MB; una prima
visita arrivava a 11,5 MB, quasi tutti album.

Dopo: ogni miniatura e' un file suo, f/<chiave>.webp (168x168, circa 6 KB).
Il browser scarica solo quelle che si vedono davvero, con loading="lazy",
e se le tiene in cache da solo.

Uso:  python3 sorgenti/esplodi_foto.py [--pulisci]
      --pulisci cancella anche i vecchi album fa.*.json
"""

import base64
import glob
import json
import os
import sys

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
USCITA = os.path.join(RADICE, "f")


def main():
    pulisci = "--pulisci" in sys.argv
    os.makedirs(USCITA, exist_ok=True)

    album = sorted(glob.glob(os.path.join(RADICE, "fa.*.json")))
    if not album:
        print("nessun album da scomporre")
        return

    scritte = uguali = saltate = 0
    byte = 0
    for a in album:
        try:
            with open(a, encoding="utf-8") as f:
                j = json.load(f)
        except Exception as ex:
            print(f"  {os.path.basename(a)}: illeggibile ({ex})")
            continue
        for chiave, b64 in j.items():
            if not chiave or "/" in chiave or chiave.startswith("."):
                saltate += 1
                continue
            try:
                dati = base64.b64decode(b64)
            except Exception:
                saltate += 1
                continue
            if not dati[:4] == b"RIFF":
                saltate += 1
                continue
            dove = os.path.join(USCITA, chiave + ".webp")
            if os.path.exists(dove) and os.path.getsize(dove) == len(dati):
                uguali += 1
                byte += len(dati)
                continue
            with open(dove, "wb") as f:
                f.write(dati)
            scritte += 1
            byte += len(dati)
        print(f"  {os.path.basename(a)}: {len(j)} miniature")

    print(f"\n{scritte} file scritti, {uguali} gia' uguali, {saltate} saltate")
    print(f"cartella f/: {byte/1048576:.1f} MB")

    if pulisci:
        tolti = 0
        for a in album:
            os.remove(a)
            tolti += 1
        print(f"{tolti} album fa.*.json cancellati")


if __name__ == "__main__":
    main()
