"""Prima schermata gia' pronta anche alla prima visita (13/11/2026).

Alla seconda visita la guida mostra subito le schede salvate nel telefono
(localStorage "istG:<dati>") mentre i dati arrivano. Alla prima visita invece
si aspettavano i dati (451 KB compressi): 1,4 s su 4G prima di vedere una scheda.

Questo programma apre la pagina appena costruita in un browser senza schermo,
prende la stessa istantanea che la pagina salverebbe nel telefono e la mette in
testa a index.html come window.IST_BASE. Chi arriva la prima volta vede subito le
schede; quando i dati arrivano la pagina vera prende il loro posto, come gia'
succede alla seconda visita.

Lo stesso per la mappa (filtri.html): mette in testa window.MAPPA_PRIMA, cioe' i
contorni delle regioni e le bolle delle regioni con i loro numeri, cosi' l'Italia
con le bolle si disegna subito, prima che arrivino i 144 KB della mappa.

Uso: python3 sorgenti/istantanea.py     (dopo build.py, foto_split.py e velocizza.py)
Esce 0 anche se non riesce (la pagina funziona lo stesso, solo senza istantanea).
"""
import functools
import http.server
import json
import os
import re
import sys
import threading

RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAG = os.path.join(RADICE, "index.html")


class Zitto(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


MAPPA = os.path.join(RADICE, "filtri.html")


def mappa(pg, base):
    """MAPPA_PRIMA per filtri.html: regioni, bolle delle regioni, colori dei temi."""
    if not os.path.exists(MAPPA):
        return
    t = open(MAPPA, encoding="utf-8").read()
    t = re.sub(r'<script id="mappaprima-dati">.*?</script>\n?', "", t, flags=re.S)
    open(MAPPA, "w", encoding="utf-8").write(t)
    if "MAPPA_PRIMA" not in t:
        print("istantanea: la mappa non sa usare MAPPA_PRIMA, salto")
        return
    m = re.search(r'const NOME="(mappa\.[0-9a-f]+\.json)"', t)
    if not m or not os.path.exists(os.path.join(RADICE, m.group(1))):
        print("istantanea: file della mappa non trovato, salto")
        return
    R = json.load(open(os.path.join(RADICE, m.group(1)), encoding="utf-8"))["R"]
    pg.goto(base + "filtri.html")
    pg.wait_for_function("window.__mappa&&window.__mappa.gr().length>0&&window.__mappa.TEMI", timeout=90000)
    pg.wait_for_timeout(1500)
    B, T = pg.evaluate("""()=>{const M=window.__mappa;const T={};for(const [k,v] of Object.entries(M.TEMI))T[k]={land:v.land,edge:v.edge,bub:v.bub,fill:v.fill,txt:v.txt,lab:v.lab,halo:v.halo,css:v.css};
      return [M.gr().map(o=>[Math.round(o.x*10)/10,Math.round(o.y*10)/10,o.n,o.lab||'']),T]}""")
    if not B or len(B) > 40:
        print(f"istantanea: la mappa non e' sulla vista d'Italia ({len(B)} bolle), salto")
        return
    dati = json.dumps({"R": R, "B": B, "T": T}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<script id="mappaprima-dati">window.MAPPA_PRIMA=' + dati + ';</script>', 1)
    open(MAPPA, "w", encoding="utf-8").write(t)
    print(f"istantanea: mappa, {len(B)} bolle e {len(R)} regioni, {len(dati)//1024} KB in testa a filtri.html")


def main():
    t = open(PAG, encoding="utf-8").read()
    t = re.sub(r'<script id="istbase">.*?</script>\n?', "", t, flags=re.S)
    open(PAG, "w", encoding="utf-8").write(t)
    if "IST_BASE" not in t:
        print("istantanea: la pagina non sa usare IST_BASE, niente da fare")
        return 0
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("istantanea: playwright non installato, salto")
        return 0
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Zitto, directory=RADICE))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True).new_page()
        pg.goto(url)
        pg.wait_for_function("Object.keys(localStorage).some(k=>k.startsWith('istG:'))", timeout=90000)
        k, v = pg.evaluate("(()=>{const k=Object.keys(localStorage).find(k=>k.startsWith('istG:'));return [k,localStorage.getItem(k)]})()")
        try:
            pg2 = b.new_context(viewport={"width": 1366, "height": 900}).new_page()
            mappa(pg2, url.rsplit("/", 1)[0] + "/")
        except Exception as e:
            print(f"istantanea: mappa non riuscita ({str(e)[:100]}), la pagina funziona lo stesso")
        b.close()
    srv.shutdown()
    nome = k[5:]
    if nome not in t:
        print(f"istantanea: l'istantanea e' di {nome}, che la pagina non usa: salto")
        return 0
    base = json.dumps({"n": nome, "v": json.loads(v)}, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")
    t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<script id="istbase">window.IST_BASE=' + base + ';</script>', 1)
    open(PAG, "w", encoding="utf-8").write(t)
    print(f"istantanea: {len(base)//1024} KB in testa alla pagina, dati {nome}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
