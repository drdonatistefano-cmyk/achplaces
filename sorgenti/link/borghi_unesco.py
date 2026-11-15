#!/usr/bin/env python3
"""15/11/2026 – link diretti alle pagine ufficiali, raccolti su GitHub Actions (la rete di Actions raggiunge i siti).

1) I Borghi più belli d'Italia (borghipiubelliditalia.it, WordPress): elenco di tutte le pagine e gli articoli
   dall'interfaccia pubblica wp-json (titolo, indirizzo, data). Le schede dei borghi si riconoscono dal testo
   «COMUNE DI …» / «MUNICIPALITY OF …» all'inizio della pagina.
2) UNESCO: tutti i beni italiani della Lista del Patrimonio mondiale e le loro componenti, da Wikidata
   (P757 = codice del sito UNESCO, CC0), con comune (P131 -> codice ISTAT P635) e coordinate. Il link è la pagina
   ufficiale https://whc.unesco.org/en/list/<codice>/ ; il nome ufficiale del bene viene dall'elenco XML dell'UNESCO.
Scrive out/borghi.json e out/unesco.json.
"""
import json, os, re, sys, time, urllib.request, urllib.parse, html
OUT = sys.argv[1] if len(sys.argv) > 1 else "out"
os.makedirs(OUT, exist_ok=True)
UA = {"User-Agent": "achplaces.com link checker (+https://achplaces.com/metodo)"}

def get(u, tries=4):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60) as r:
                return r.read().decode("utf-8", "replace"), dict(r.headers)
        except Exception as e:
            print("  errore", u, e, flush=True); time.sleep(3 + 5 * i)
    return None, {}

def norm(t):
    import unicodedata
    t = unicodedata.normalize("NFD", html.unescape(t or "")).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()

def borghi():
    """Elenco completo delle schede dei borghi (tipo dt_portfolio, indirizzi /borgo/<nome>/) dall'interfaccia
    pubblica wp-json del sito ufficiale; dal testo di ogni scheda si legge «COMUNE DI <nome>». Un comune della
    guida (borghi_comuni.json) prende il link della scheda il cui comune (o titolo) coincide con il suo nome.
    Solo schede dei borghi: niente eventi o articoli."""
    QUI = os.path.dirname(os.path.abspath(__file__))
    L = json.load(open(os.path.join(QUI, "borghi_comuni.json")))
    schede = []
    for pg in range(1, 30):
        t, h = get(f"https://borghipiubelliditalia.it/wp-json/wp/v2/dt_portfolio?per_page=100&page={pg}&_fields=link,title,content")
        try: res = json.loads(t) if t else []
        except Exception: res = []
        if not isinstance(res, list) or not res: break
        for r in res:
            u = r.get("link", ""); tit = html.unescape((r.get("title") or {}).get("rendered", ""))
            if not u.startswith("https://borghipiubelliditalia.it/") or "/en/" in u: continue
            testo = html.unescape(re.sub(r"<[^>]+>", " ", (r.get("content") or {}).get("rendered", "")))
            m = re.search(r"COMUNE\s+DI\s+([A-ZÀ-Ýa-zà-ý' .\-]+?)(?:\s{2,}|\(|\n|,|PROVINCIA|$)", testo)
            schede.append({"url": u, "titolo": tit, "comune": m.group(1).strip() if m else ""})
        print("pagina", pg, len(res), flush=True)
        if len(res) < 100: break
        time.sleep(0.5)
    print("schede borghi:", len(schede), flush=True)
    perc = {}; pert = {}
    for x in schede:
        if x["comune"]: perc.setdefault(norm(x["comune"]), []).append(x)
        pert.setdefault(norm(x["titolo"]), []).append(x)
    out = {}
    for c in L:
        nn = norm(c["nome"])
        k = pert.get(nn) or perc.get(nn) or []
        # preferisci la scheda col titolo uguale al comune, poi quella del capoluogo
        out[c["slug"]] = {"url": k[0]["url"], "titolo": k[0]["titolo"], "comune": k[0]["comune"]} if k else None
        print(f"{c['nome']}: {out[c['slug']]['url'] if k else '-'}", flush=True)
    json.dump({"schede": schede, "borghi": out}, open(os.path.join(OUT, "borghi.json"), "w"), ensure_ascii=False, indent=0)
    print("borghi: trovati", sum(1 for v in out.values() if v), "su", len(out))

def unesco():
    q = """SELECT ?item ?itemLabel ?whc ?coord ?com ?comLabel ?istat WHERE {
      ?item wdt:P757 ?whc . ?item wdt:P17 wd:Q38 .
      OPTIONAL { ?item wdt:P625 ?coord }
      OPTIONAL { ?item wdt:P131 ?com . OPTIONAL { ?com wdt:P635 ?istat } }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". } }"""
    t, _ = get("https://query.wikidata.org/sparql?format=json&query=" + urllib.parse.quote(q))
    righe = []
    if t:
        for b in json.loads(t)["results"]["bindings"]:
            g = lambda k: b.get(k, {}).get("value")
            c = g("coord"); lat = lng = None
            if c:
                m = re.match(r"Point\(([-\d.]+) ([-\d.]+)\)", c)
                if m: lng, lat = float(m.group(1)), float(m.group(2))
            righe.append({"q": g("item").rsplit("/", 1)[-1], "nome": g("itemLabel"), "whc": g("whc"), "lat": lat, "lng": lng, "istat": g("istat"), "comune": g("comLabel")})
    # nomi ufficiali dall'elenco UNESCO
    nomi = {}
    t, _ = get("https://whc.unesco.org/en/list/xml/")
    if t:
        for row in re.findall(r"<row>(.*?)</row>", t, flags=re.S):
            idn = re.search(r"<id_number>(\d+)</id_number>", row); st = re.search(r"<states>(.*?)</states>", row, flags=re.S)
            nm = re.search(r"<site>(.*?)</site>", row, flags=re.S)
            if idn and nm and st and "Italy" in st.group(1):
                nomi[idn.group(1)] = html.unescape(re.sub(r"<[^>]+>", "", nm.group(1))).strip()
    json.dump({"componenti": righe, "nomi_ufficiali": nomi}, open(os.path.join(OUT, "unesco.json"), "w"), ensure_ascii=False, indent=0)
    print("unesco: componenti", len(righe), "beni italiani nell'elenco ufficiale", len(nomi))

if __name__ == "__main__":
    if "solo-borghi" not in sys.argv: unesco()
    borghi()
