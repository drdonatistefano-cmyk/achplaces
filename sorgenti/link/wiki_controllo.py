"""15/11/2026: controllo dei titoli Wikipedia dei luoghi (tasto W). Per ogni titolo, dall'API ufficiale di it.wikipedia:
esiste? e' un rinvio (redirect) e verso cosa? e' una pagina di disambiguazione? Scrive out/wiki_controllo.json."""
import json, os, time, requests
QUI = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(QUI, "wiki_titoli.json")))
S = requests.Session(); S.headers["User-Agent"] = "AchPlacesGuide/1.0 (https://achplaces.com; controllo link)"
tit = sorted({x["wk"] for x in L}); res = {}
for i in range(0, len(tit), 50):
    blocco = tit[i:i + 50]
    for prova in range(4):
        try:
            r = S.get("https://it.wikipedia.org/w/api.php", params={"action": "query", "format": "json", "formatversion": 2,
                "redirects": 1, "prop": "pageprops", "ppprop": "disambiguation", "titles": "|".join(blocco)}, timeout=40)
            q = r.json()["query"]; break
        except Exception as e:
            time.sleep(5 * (prova + 1)); q = None
    if not q:
        for t in blocco: res[t] = {"stato": "errore"}
        continue
    norm = {x["from"]: x["to"] for x in q.get("normalized", [])}
    red = {x["from"]: x["to"] for x in q.get("redirects", [])}
    pag = {p["title"]: p for p in q.get("pages", [])}
    for t in blocco:
        t1 = norm.get(t, t); t2 = red.get(t1, t1); p = pag.get(t2, {})
        if p.get("missing") or p.get("invalid"): res[t] = {"stato": "mancante"}
        elif "disambiguation" in (p.get("pageprops") or {}): res[t] = {"stato": "disambigua", "a": t2}
        elif t2 != t1: res[t] = {"stato": "rinvio", "a": t2}
        else: res[t] = {"stato": "ok"}
    time.sleep(0.3)
os.makedirs("out", exist_ok=True)
json.dump({"titoli": res}, open("out/wiki_controllo.json", "w"), ensure_ascii=False, indent=0)
from collections import Counter; print(Counter(v["stato"] for v in res.values()))
