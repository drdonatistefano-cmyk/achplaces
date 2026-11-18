"""Applica le proposte di correzione dei link che Stefano ha spuntato (18/11/2026).

Uso: python3 sorgenti/link/applica.py PROPOSTE.json gruppo [gruppo ...]
Gruppi: sicure, spostate, altro_sito, sparite. Aggiunge a sorgenti/data/link_correzioni.json:
  rid[vecchio] = nuovo         per sicure, spostate, altro_sito
  rotti[vecchio] = 404         per sparite, e archivio[vecchio] = copia dell'Internet Archive quando c'è
Non toglie e non cambia nessuna correzione già presente. Le pagine cambiano alla prossima costruzione di Places.
"""
import json
import os
import sys

CORR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "link_correzioni.json")


def main():
    prop = json.load(open(sys.argv[1], encoding="utf-8"))
    gruppi = [g for g in sys.argv[2:] if g in ("sicure", "spostate", "altro_sito", "sparite")]
    corr = json.load(open(CORR, encoding="utf-8"))
    for k in ("rid", "rotti", "archivio"):
        corr.setdefault(k, {})
    n = {"rid": 0, "rotti": 0, "archivio": 0}
    for g in gruppi:
        for vecchio, nuovo in (prop.get(g) or {}).items():
            if vecchio in corr["rid"] or vecchio in corr["rotti"]:
                continue
            if g == "sparite":
                corr["rotti"][vecchio] = 404
                n["rotti"] += 1
                if nuovo:
                    corr["archivio"][vecchio] = nuovo
                    n["archivio"] += 1
            elif nuovo:
                corr["rid"][vecchio] = nuovo
                n["rid"] += 1
    # stesso formato del file (indent 0), le voci nuove in fondo: il confronto delle versioni mostra solo le aggiunte
    json.dump(corr, open(CORR, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(f"applicate: {n['rid']} sostituzioni, {n['rotti']} link tolti ({n['archivio']} con copia d'archivio); gruppi {gruppi}")


if __name__ == "__main__":
    main()
