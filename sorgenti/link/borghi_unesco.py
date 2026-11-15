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

def borghi():
    B = "https://borghipiubelliditalia.it/wp-json/wp/v2/"
    righe = []
    for tipo in ("pages", "posts"):
        pag = 1
        while True:
            t, h = get(f"{B}{tipo}?per_page=100&page={pag}&_fields=id,link,title,slug,parent,content")
            if not t: break
            try: lst = json.loads(t)
            except Exception: break
            if not isinstance(lst, list) or not lst: break
            for x in lst:
                testo = re.sub(r"<[^>]+>", " ", (x.get("content") or {}).get("rendered", ""))
                testo = html.unescape(re.sub(r"\s+", " ", testo))[:600]
                m = re.search(r"(?:COMUNE DI|Comune di|MUNICIPALITY OF)\s+([A-ZÀ-Ý][^\n(]{1,60}?)\s*\(", testo)
                righe.append({"tipo": tipo, "id": x["id"], "link": x["link"], "titolo": html.unescape(x["title"]["rendered"]),
                              "slug": x.get("slug"), "comune": m.group(1).strip() if m else None, "inizio": testo[:160]})
            tot = int(h.get("X-WP-TotalPages", h.get("x-wp-totalpages", "1")) or 1)
            print(f"borghi {tipo} pagina {pag}/{tot}: {len(lst)}", flush=True)
            if pag >= tot: break
            pag += 1; time.sleep(1)
    json.dump(righe, open(os.path.join(OUT, "borghi.json"), "w"), ensure_ascii=False, indent=0)
    print("borghi: righe", len(righe), "schede con comune", sum(1 for r in righe if r["comune"]))

def unesco():
    q = """SELECT ?item ?itemLabel ?whc ?coord ?com ?istat WHERE {
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
            righe.append({"q": g("item").rsplit("/", 1)[-1], "nome": g("itemLabel"), "whc": g("whc"), "lat": lat, "lng": lng, "istat": g("istat")})
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
    unesco()
    borghi()
