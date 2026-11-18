"""Proposte di correzione dei link di Places (18/11/2026, richiesta di Stefano: «proposta, poi il mio sì»).

Legge i risultati del controllo settimanale (out/link-*.json sul ramo «foto»: {url: [codice, indirizzo finale, errore]})
e le correzioni già decise (sorgenti/data/link_correzioni.json: rid = sostituzioni, rotti = da togliere, archivio =
copia dell'Internet Archive). Propone solo le correzioni NUOVE, divise in gruppi:

  sicure     stesso indirizzo con https, «www» o la barra finale: si sostituisce
  spostate   la pagina si è spostata nello stesso sito e risponde: si sostituisce
  altro sito la pagina ora sta su un altro sito (spesso un ente che ha cambiato dominio): una per una
  sparite    404 o 410, oppure il sito rimanda alla sua pagina iniziale: si toglie il link, e se c'è una copia
             dell'Internet Archive la si usa al suo posto
  da guardare  il sito non risponde: niente proposta finché non succede due settimane di fila

Uso: python3 sorgenti/link/proposte.py RISULTATI_DIR [--archivio]   (--archivio chiede le copie a archive.org)
Scrive RISULTATI_DIR/proposte-link.json e RISULTATI_DIR/proposte-link.md (il testo della segnalazione su GitHub).
Non cambia nulla: le correzioni le applica sorgenti/link/applica.py, solo per i gruppi che Stefano spunta.
"""
import glob
import json
import os
import sys
import time
import urllib.parse
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
CORR = os.path.join(QUI, "..", "data", "link_correzioni.json")
GRUPPI = [("sicure", "Sicure: solo https, «www» o barra finale"), ("spostate", "Pagine spostate nello stesso sito"),
          ("altro_sito", "Pagine passate a un altro sito"), ("sparite", "Pagine sparite (si tolgono; copia d'archivio se c'è)")]


def host(u):
    return (urllib.parse.urlsplit(u).hostname or "").lower().removeprefix("www.")


def chiave(u):
    p = urllib.parse.urlsplit(u)
    return host(u) + urllib.parse.unquote(p.path).rstrip("/") + ("?" + p.query if p.query else "")


def pagina_iniziale(u):
    return urllib.parse.urlsplit(u).path.strip("/") in ("", "home", "index.html", "index.php", "it", "en")


def copia_archivio(u):
    try:
        q = "https://archive.org/wayback/available?" + urllib.parse.urlencode({"url": u})
        j = json.load(urllib.request.urlopen(urllib.request.Request(q, headers={"User-Agent": "achplaces-link/1.0"}), timeout=30))
        s = (j.get("archived_snapshots") or {}).get("closest") or {}
        return s["url"].replace("http://web.archive.org", "https://web.archive.org") if s.get("available") and str(s.get("status", "200")) == "200" else None
    except Exception:  # noqa: BLE001
        return None


def main():
    cart = sys.argv[1]
    ris = {}
    for f in sorted(glob.glob(os.path.join(cart, "link-*.json"))):
        ris.update(json.load(open(f, encoding="utf-8")))
    prima = {}
    p_prima = os.path.join(cart, "proposte-link.json")
    if os.path.exists(p_prima):
        prima = json.load(open(p_prima, encoding="utf-8"))
    corr = json.load(open(CORR, encoding="utf-8"))
    gia = set(corr.get("rid", {})) | set(corr.get("rotti", {})) | set(corr.get("archivio", {}))
    nuove = {g: {} for g, _ in GRUPPI}
    da_guardare = {}
    for u, (codice, fin, err) in sorted(ris.items()):
        if u in gia:
            continue
        if codice == 200 and fin and fin != u and not fin.startswith("http:"):
            if urllib.parse.unquote(fin).rstrip("/") == urllib.parse.unquote(u).rstrip("/"):
                continue                                # stesso indirizzo scritto con le lettere accentate: va bene così
            if chiave(fin) == chiave(u):
                nuove["sicure"][u] = fin
            elif pagina_iniziale(fin) and not pagina_iniziale(u):
                nuove["sparite"][u] = None              # rimanda alla pagina iniziale: la pagina non c'è più
            elif host(fin) == host(u):
                nuove["spostate"][u] = fin
            else:
                nuove["altro_sito"][u] = fin
        elif codice in (404, 410):
            nuove["sparite"][u] = None
        elif codice == 0:
            # due settimane di fila irraggiungibile prima di proporre qualcosa
            if u in (prima.get("da_guardare") or {}) and prima.get("settimana", "") <= time.strftime("%Y-%m-%d", time.localtime(time.time() - 6 * 86400)):
                nuove["sparite"][u] = None
            else:
                da_guardare[u] = err or "non risponde"
    if "--archivio" in sys.argv:
        for u in list(nuove["sparite"]):
            nuove["sparite"][u] = copia_archivio(u)
            time.sleep(1)
    out = {"settimana": time.strftime("%Y-%m-%d"), **nuove, "da_guardare": da_guardare}
    json.dump(out, open(p_prima, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    righe = [f"Proposte di correzione dei link di Places, controllo della settimana del {out['settimana']}.",
             "Spunta i gruppi da applicare: le correzioni vanno in `sorgenti/data/link_correzioni.json` e si vedono sul sito "
             "alla prossima costruzione di Places, dopo il «pubblica». Non spuntare = non cambia nulla.", ""]
    for g, titolo in GRUPPI:
        n = len(nuove[g])
        if not n:
            continue
        extra = f", {sum(1 for v in nuove[g].values() if v)} con copia d'archivio" if g == "sparite" else ""
        righe.append(f"- [ ] **{titolo}**: {n}{extra} <!-- gruppo:{g} -->")
        for u, v in list(nuove[g].items())[:12]:
            righe.append(f"  - {u}" + (f" → {v}" if v else " → si toglie"))
        if n > 12:
            righe.append(f"  - … e altre {n - 12} (elenco completo in `proposte-link.json` sul ramo «foto»)")
    righe += ["", f"Da guardare (non rispondono, nessuna proposta prima della seconda settimana): {len(da_guardare)}.",
              "", "_Scritto da `sorgenti/link/proposte.py`. Lo applica `sorgenti/link/applica.py` quando una casella è spuntata._"]
    open(os.path.join(cart, "proposte-link.md"), "w", encoding="utf-8").write("\n".join(righe) + "\n")
    print("proposte:", {g: len(nuove[g]) for g, _ in GRUPPI}, "da guardare:", len(da_guardare))


if __name__ == "__main__":
    main()
