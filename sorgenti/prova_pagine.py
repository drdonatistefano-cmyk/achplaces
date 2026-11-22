#!/usr/bin/env python3
"""20/11/2026 – prova delle pagine per Google: un giro senza cambiamenti non deve riscrivere nessuna pagina.

Prima ogni giro di pagine.py + pagine_en.py riscriveva tutte le ~23.600 pagine solo per la data «Aggiornato il …»,
e il repository cresceva di circa 40 MB a giro. La prova, in una copia temporanea del sito:
1. fa due giri «domani» e «dopodomani»: al secondo giro nessuna pagina e nessuna mappa del sito deve cambiare;
2. cambia il testo di una pagina e rifà il giro: quella pagina (e la sua inglese) deve tornare giusta, con la data
   nuova anche nella mappa del sito, e le altre pagine devono restare com'erano.
Uso: python3 sorgenti/prova_pagine.py   (circa un minuto; esce con 1 se una prova non riesce)
"""
import datetime, glob, os, re, shutil, subprocess, sys, tempfile

QUI = os.path.dirname(os.path.abspath(__file__))
SITO = os.path.dirname(QUI)
CARTELLE = ["sorgenti", "comune", "luogo", "regione", "comuni", "en"]
SHIM = ("import datetime, runpy, sys\n"
        "a = datetime.date.fromisoformat(sys.argv[1])\n"
        "class F(datetime.date):\n"
        "    @classmethod\n"
        "    def today(cls): return cls(a.year, a.month, a.day)\n"
        "datetime.date = F\n"
        "sys.argv = sys.argv[2:]\n"
        "runpy.run_path(sys.argv[0], run_name='__main__')\n")


def giro(rad, data):
    shim = os.path.join(rad, "_con_data.py")
    open(shim, "w").write(SHIM)
    for cmd in ([shim, data, os.path.join(rad, "sorgenti", "pagine.py")],
                [shim, data, os.path.join(rad, "sorgenti", "traduci", "pagine_en.py"), rad]):
        r = subprocess.run([sys.executable] + cmd, cwd=rad, capture_output=True, text=True)
        if r.returncode:
            print(r.stdout[-2000:], r.stderr[-2000:]); sys.exit("giro non riuscito")


def istantanea(rad):
    out = {}
    for f in glob.glob(os.path.join(rad, "**", "index.html"), recursive=True) + glob.glob(os.path.join(rad, "sitemap*.xml")):
        if os.sep + "sorgenti" + os.sep in f: continue
        out[os.path.relpath(f, rad)] = open(f, encoding="utf-8").read()
    return out


def main():
    oggi = datetime.date.today()
    d1, d2, d3 = (str(oggi + datetime.timedelta(days=n)) for n in (1, 2, 3))
    errori = []
    with tempfile.TemporaryDirectory() as tmp:
        rad = os.path.join(tmp, "sito")
        os.makedirs(rad)
        for c in CARTELLE:
            if os.path.exists(os.path.join(SITO, c)): shutil.copytree(os.path.join(SITO, c), os.path.join(rad, c), symlinks=True)
        for f in glob.glob(os.path.join(SITO, "*")):
            if os.path.isfile(f): shutil.copy2(f, rad)
        # la memoria delle traduzioni sta nel ramo «traduzioni»: serve il .git del sito
        if os.path.exists(os.path.join(SITO, ".git")): os.symlink(os.path.join(SITO, ".git"), os.path.join(rad, ".git"))

        giro(rad, d1)
        prima = istantanea(rad)
        giro(rad, d2)
        dopo = istantanea(rad)
        cambiati = [k for k in prima if dopo.get(k) != prima[k]]
        if cambiati: errori.append(f"1. giro senza cambiamenti: {len(cambiati)} file riscritti (es. {cambiati[:3]})")
        else: print(f"1. giro senza cambiamenti: 0 file riscritti su {len(prima)} — ok")

        luoghi = sorted(k for k in dopo if k.startswith("luogo" + os.sep))
        k = luoghi[0]
        f = os.path.join(rad, k)
        t = open(f, encoding="utf-8").read()
        open(f, "w", encoding="utf-8").write(t.replace("<h1>", "<h1>VECCHIO ", 1))
        giro(rad, d3)
        terzo = istantanea(rad)
        url = "https://achplaces.com/" + k[:-len("index.html")].replace(os.sep, "/")
        if "VECCHIO" in terzo[k]: errori.append("2. la pagina cambiata non è stata riscritta")
        if f"Aggiornato il {d3}" not in terzo[k]: errori.append("2. la pagina cambiata non ha la data nuova")
        if not re.search(re.escape(url) + r"</loc><lastmod>" + d3, terzo.get("sitemap-1.xml", "")):
            errori.append("2. nella mappa del sito la pagina cambiata non ha la data nuova")
        url_en = url.replace("achplaces.com/", "achplaces.com/en/", 1)
        if not re.search(re.escape(url_en) + r"</loc><lastmod>" + d3, terzo.get("sitemap-en-1.xml", "")):
            errori.append("2. nella mappa inglese la pagina cambiata non ha la data nuova")
        altre = [x for x in dopo if x not in (k, os.path.join("en", k)) and not x.startswith("sitemap") and terzo.get(x) != dopo[x]]
        if altre: errori.append(f"2. cambiate anche {len(altre)} altre pagine (es. {altre[:3]})")
        if not errori or all(not e.startswith("2.") for e in errori): print("2. pagina cambiata riscritta con la data nuova, le altre ferme — ok")

    for e in errori: print("ERRORE", e)
    sys.exit(1 if errori else 0)


if __name__ == "__main__":
    main()
