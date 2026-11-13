"""Pagine statiche indicizzabili da Google per Ach's Places Guide.

La guida interattiva (index.html) è una sola pagina: Google non può indicizzare i singoli luoghi.
Questo programma genera, dai file di dati già pubblicati, una pagina per ogni comune e per ogni
luogo con contenuto sufficiente, più gli indici per regione, la mappa del sito e robots.txt.

Uso: python3 sorgenti/pagine.py [--luoghi 0|1] [--out .]
Scrive: comune/<slug>/index.html, luogo/<id>/index.html, regione/<slug>/index.html,
        comuni/index.html, sitemap.xml, sitemap-N.xml, robots.txt, pagine.css
"""
import html, json, os, re, sys, unicodedata, datetime

SITO = "https://achplaces.com"
OGGI = datetime.date.today().isoformat()
RADICE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAT = ["storia", "musei", "sacro", "natura", "locale"]
CATN = {"storia": "Storia e architettura", "musei": "Musei", "sacro": "Luoghi di culto",
        "natura": "Natura e paesaggio", "locale": "Vita e tradizioni locali"}
AWIN, GYG = "3146807", "Y9VWGXI"
MID_TIQETS = 12427

ap = {"luoghi": 1, "out": RADICE}
for i, a in enumerate(sys.argv[1:]):
    if a == "--luoghi": ap["luoghi"] = int(sys.argv[i + 2])
    if a == "--out": ap["out"] = sys.argv[i + 2]
OUT = ap["out"]


def e(s):
    return html.escape(str(s or ""), quote=True)


def slug(s, n=60):
    s = unicodedata.normalize("NFD", str(s).lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:n].strip("-")


def taglia(s, n=155):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n - 1].rsplit(" ", 1)[0] + "…"


# ---------------------------------------------------------------- lettura dei dati pubblicati
M = json.load(open(os.path.join(RADICE, "manifest.json"), encoding="utf-8"))
leggi = lambda n: json.load(open(os.path.join(RADICE, n), encoding="utf-8"))
D = leggi(M["dati"])
TESTI = []
with open(os.path.join(RADICE, M["testi"]), encoding="utf-8") as f:
    for riga in f:
        riga = riga.strip()
        if riga: TESTI += json.loads(riga)
FOTO = leggi(M["foto"])
Z = D["dz"]
K = D["k"]
COL = list(K["ck"].keys())

comuni, g = [], 0
for i in range(len(K["n"])):
    c = {}
    for k in COL:
        m = K["cm"].get(k)
        if m and i in m: continue
        c[k] = K["ck"][k][i]
    for k in ("regione", "provName", "provKind", "verified"):
        if isinstance(c.get(k), int): c[k] = Z[k][c[k]]
    pl = []
    for _ in range(K["n"][i]):
        a = [K["p"][j][g] for j in range(9)]
        x = K["x"].get(str(g)) or {}
        nome = a[1]
        pid = (c["slug"] + "--" + (a[0] if a[0] else slug(nome, 40))) if c["slug"] else a[0]
        f = a[5] or ""
        pl.append({"id": pid, "name": nome, "cat": CAT[a[2]], "sub": Z["sub"][a[3]],
                   "desc": a[4] or "", "gratis": "F" in f, "pagamento": "P" in f,
                   "unesco": "u" in f, "vista": "v" in f, "coperto": "i" in f,
                   "stato": a[6] or "ok", "tempo": Z["t"][a[7]] if a[7] is not None else "",
                   "ps": x.get("ps", ""),  # 13/11: stima del prezzo (numero), non un indice dei testi
                   "tq": x.get("tq", ""), "gy": x.get("gy", ""), "ticketUrl": x.get("ticketUrl", "")})
        g += 1
    c["places"] = pl
    if c.get("slug"): comuni.append(c)

DET = {}
for pr, nome in M["det"].items():
    try:
        for cs, v in leggi(nome).items(): DET[cs] = v
    except Exception as ex:
        print("  dettagli non letti", pr, ex)

for c in comuni:
    d = DET.get(c["slug"]) or {}
    c.update(d.get("_c") or {})
    for p in c["places"]:
        dd = d.get(p["id"])
        if dd: p.update({k: v for k, v in dd.items() if v not in (None, "")})

print(f"Letti {len(comuni)} comuni e {sum(len(c['places']) for c in comuni)} luoghi; {len(FOTO)} foto")

REGIONI = {}
for c in comuni: REGIONI.setdefault(c["regione"], []).append(c)
nomereg = lambda r: " ".join(w if w in ("d'", "e") else w.capitalize() for w in r.replace("-", " ").split())
NOMEREG = {r: {"emilia-romagna": "Emilia-Romagna", "friuli-venezia-giulia": "Friuli-Venezia Giulia",
               "trentino-alto-adige": "Trentino-Alto Adige", "valle-d-aosta": "Valle d'Aosta"}.get(r, nomereg(r))
           for r in REGIONI}

# ---------------------------------------------------------------- pezzi comuni di ogni pagina
CSS = """:root{--ink:#1c1b19;--soft:#6b6762;--line:#e3ded6;--paper:#fffdfa;--acc:#7a5c3e}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);
font:16px/1.65 ui-serif,Georgia,'Iowan Old Style',serif;-webkit-text-size-adjust:100%}
.w{max-width:760px;margin:0 auto;padding:0 20px}
header.top{border-bottom:1px solid var(--line);padding:14px 0;margin-bottom:28px}
header.top .w{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:baseline}
.marchio{font-weight:700;letter-spacing:.01em;text-decoration:none;color:var(--ink)}
nav.guide{margin-left:auto;display:flex;gap:14px;font-size:14px}
nav.guide a{color:var(--soft);text-decoration:none;border-bottom:1px solid var(--line)}
nav.guide a:hover{color:var(--acc)}
.briciole{font-size:14px;color:var(--soft);margin:0 0 10px}
.briciole a{color:var(--soft)}
h1{font-size:30px;line-height:1.25;margin:0 0 10px}
h2{font-size:22px;margin:34px 0 6px;scroll-margin-top:16px}
h3{font-size:17px;margin:26px 0 4px}
.lede{font-size:18px;color:#3b3833;margin:0 0 18px}
.avviso{background:#fdf6e7;border:1px solid #efe0bd;border-radius:8px;padding:12px 14px;margin:18px 0;font-size:15px}
.apri{display:inline-block;margin:6px 0 22px;padding:9px 16px;border:1px solid var(--acc);border-radius:999px;
color:var(--acc);text-decoration:none;font-size:15px}
.apri:hover{background:var(--acc);color:#fff}
article.luogo{border-top:1px solid var(--line);padding-top:18px;margin-top:26px}
.meta{font-size:14px;color:var(--soft);margin:2px 0 8px}
.tag{display:inline-block;margin-right:8px}
ul.fatti{list-style:none;padding:0;margin:10px 0;font-size:15px}
ul.fatti li{margin:3px 0}
ul.fatti b{font-weight:600}
.fonti{font-size:14px;color:var(--soft)}
.fonti a{color:var(--soft)}
ul.elenco{columns:2;column-gap:28px;padding-left:18px}
@media(max-width:560px){ul.elenco{columns:1}h1{font-size:25px}}
a{color:var(--acc)}
footer{border-top:1px solid var(--line);margin-top:48px;padding:20px 0 40px;font-size:14px;color:var(--soft)}
footer a{color:var(--soft)}
"""

NAV = ('<header class="top"><div class="w"><a class="marchio" href="/">Ach\'s Places Guide</a>'
       '<nav class="guide" aria-label="Le guide di Ach">'
       '<a href="https://achevents.com">Eventi</a>'
       '<a href="https://achdinners.com">Osterie</a>'
       '<a href="/">Mappa e filtri</a></nav></div></header>')

PIE = ('<footer><div class="w"><p>Testi originali di Ach\'s Places Guide; le informazioni pratiche sono '
       'riassunte dalle fonti ufficiali citate in ogni scheda. Alcuni link a biglietti e visite guidate sono '
       'affiliati: se acquisti, la guida riceve una commissione senza costi in più per te.</p>'
       f'<p>Aggiornato il {OGGI} · <a href="/">Guida completa, mappa e filtri</a> · '
       '<a href="/comuni/">Tutti i comuni</a> · <a href="/#metodo">Metodo e fonti</a></p></div></footer>')

GC = '<script data-goatcounter="https://achplaces.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'


def pagina(titolo, descr, url, corpo, jsonld=None, prof=0):
    su = "../" * prof
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False, separators=(",", ":"))}</script>' if jsonld else ""
    return ("<!doctype html><html lang=\"it\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>{e(titolo)}</title><meta name=\"description\" content=\"{e(descr)}\">"
            f"<link rel=\"canonical\" href=\"{e(url)}\">"
            f"<meta property=\"og:title\" content=\"{e(titolo)}\"><meta property=\"og:description\" content=\"{e(descr)}\">"
            f"<meta property=\"og:type\" content=\"article\"><meta property=\"og:url\" content=\"{e(url)}\">"
            "<meta property=\"og:site_name\" content=\"Ach's Places Guide\"><meta property=\"og:locale\" content=\"it_IT\">"
            f"<link rel=\"stylesheet\" href=\"{su}pagine.css\">{ld}{GC}</head><body>"
            + NAV + "<main class=\"w\">" + corpo + "</main>" + PIE + "</body></html>")


def link_biglietti(p):
    """Tiqets passa dalla rete Awin; GetYourGuide ha il codice partner nell'indirizzo."""
    out = []
    if p.get("tq"):
        import urllib.parse
        out.append((f"https://www.awin1.com/cread.php?awinmid={MID_TIQETS}&awinaffid={AWIN}&ued="
                    + urllib.parse.quote(p["tq"], safe=""), "Biglietti su Tiqets"))
    if p.get("gy"):
        u = p["gy"] + ("&" if "?" in p["gy"] else "?") + f"partner_id={GYG}&utm_medium=online_publisher"
        out.append((u, "Visite guidate su GetYourGuide"))
    if p.get("ticketUrl"):
        out.append((p["ticketUrl"], "Biglietti sul sito ufficiale"))
    return out


def ricco(p):
    """Ha una pagina propria solo il luogo con abbastanza contenuto da reggerla da solo."""
    return p.get("ps") not in ("", None) or p.get("pagamento") or p.get("unesco")


def etichette(p):
    t = [CATN[p["cat"]], p.get("sub")]
    if p.get("unesco"): t.append("Patrimonio UNESCO")
    if p.get("gratis"): t.append("Ingresso gratuito")
    elif p.get("pagamento"): t.append("Ingresso a pagamento")
    if p.get("vista"): t.append("Punto panoramico")
    return '<p class="meta">' + " · ".join(e(x) for x in t if x) + "</p>"


def fatti(p, breve):
    f = []
    if p.get("address"): f.append(f"<li><b>Dove</b> {e(p['address'])}</li>")
    if p.get("price"): f.append(f"<li><b>Ingresso</b> {e(p['price'])}</li>")
    if p.get("duration") or p.get("tempo"): f.append(f"<li><b>Tempo consigliato</b> {e(p.get('duration') or p['tempo'])}</li>")
    if not breve and p.get("access"): f.append(f"<li><b>Accessibilità</b> {e(p['access'])}</li>")
    if p.get("official"):
        q = "Scheda sul portale turistico" if p.get("ownSite") is False else "Sito ufficiale"
        f.append(f'<li><b>{q}</b> <a href="{e(p["official"])}" rel="nofollow noopener">{e(p["official"].split("/")[2])}</a></li>')
    if not breve and p.get("hoursUrl"): f.append(f'<li><b>Orari</b> <a href="{e(p["hoursUrl"])}" rel="nofollow noopener">pagina ufficiale</a></li>')
    for u, q in link_biglietti(p):
        f.append(f'<li><b>Biglietti</b> <a href="{e(u)}" rel="sponsored nofollow noopener">{e(q)}</a></li>')
    return ('<ul class="fatti">' + "".join(f) + "</ul>") if f else ""


def blocco_breve(p, c):
    """Scheda corta nella pagina del comune: il testo lungo sta solo nella pagina del luogo."""
    nome = (f'<a href="/luogo/{e(p["id"])}/">{e(p["name"])}</a>') if (ap["luoghi"] and ricco(p)) else e(p["name"])
    t = [f'<h3 id="{e(slug(p["id"], 80))}">{nome}</h3>', etichette(p)]
    if p.get("desc"): t.append(f"<p>{e(p['desc'])}</p>")
    if p.get("statusNote"): t.append(f'<p class="avviso">{e(p["statusNote"])}</p>')
    elif p.get("stato") == "closed": t.append('<p class="avviso">Luogo attualmente chiuso: verifica prima di partire.</p>')
    t.append(fatti(p, True))
    src = [s for s in (p.get("sources") or []) if len(s) > 1]
    if src:
        viste, dom = set(), []
        for s in src:
            d = s[1].split("/")[2].replace("www.", "")
            if d not in viste: viste.add(d); dom.append(f'<a href="{e(s[1])}" rel="nofollow noopener">{e(d)}</a>')
        t.append('<p class="fonti">Fonti: ' + " · ".join(dom) + "</p>")
    return "".join(t)


def blocco_pieno(p, c):
    """Scheda completa nella pagina del luogo."""
    t = [etichette(p)]
    if p.get("desc"): t.append(f"<p>{e(p['desc'])}</p>")
    if p.get("why"): t.append(f"<p><b>Perché andarci.</b> {e(p['why'])}</p>")
    if p.get("statusNote"): t.append(f'<p class="avviso">{e(p["statusNote"])}</p>')
    elif p.get("stato") == "closed": t.append('<p class="avviso">Luogo attualmente chiuso: verifica prima di partire.</p>')
    t.append(fatti(p, False))
    src = [s for s in (p.get("sources") or []) if len(s) > 1]
    if src:
        t.append('<h2>Fonti</h2><p class="fonti">' + " · ".join(
            f'<a href="{e(s[1])}" rel="nofollow noopener">{e(s[0])}</a>' for s in src) + "</p>")
    return "".join(t)


def ld_luogo(p, c):
    d = {"@context": "https://schema.org", "@type": "TouristAttraction", "name": p["name"],
         "description": taglia(p.get("desc") or p["name"], 300),
         "address": {"@type": "PostalAddress", "addressLocality": c["name"],
                     "addressRegion": c.get("prov", ""), "addressCountry": "IT"}}
    if p.get("address"): d["address"]["streetAddress"] = p["address"]
    if c.get("lat") and c.get("lng"):
        d["geo"] = {"@type": "GeoCoordinates", "latitude": c["lat"], "longitude": c["lng"]}
    if p.get("official"): d["sameAs"] = p["official"]
    if p.get("gratis"): d["isAccessibleForFree"] = True
    return d


def scrivi(percorso, testo):
    f = os.path.join(OUT, percorso)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    vecchio = open(f, encoding="utf-8").read() if os.path.exists(f) else None
    if vecchio != testo: open(f, "w", encoding="utf-8").write(testo)


# ---------------------------------------------------------------- generazione
url_comune = lambda c: f"{SITO}/comune/{c['slug']}/"
url_luogo = lambda p: f"{SITO}/luogo/{p['id']}/"
url_reg = lambda r: f"{SITO}/regione/{r}/"
urls = []
nluo = 0

for c in sorted(comuni, key=lambda c: (c["regione"], c["prov"], c["name"])):
    pl = c["places"]
    if not pl: continue
    reg, prov = NOMEREG[c["regione"]], c.get("provName") or c["prov"]
    titolo = f"Cosa vedere a {c['name']} ({c['prov']}): {len(pl)} luoghi da visitare"
    descr = taglia(c.get("lede") or f"I luoghi da visitare a {c['name']}, in provincia di {prov}: "
                   + ", ".join(p["name"] for p in pl[:4]) + ".")
    corpo = [f'<p class="briciole"><a href="/">Italia</a> › <a href="/regione/{e(c["regione"])}/">{e(reg)}</a> › {e(prov)}</p>',
             f"<h1>Cosa vedere a {e(c['name'])}</h1>"]
    if c.get("lede"): corpo.append(f'<p class="lede">{e(c["lede"])}</p>')
    corpo.append(f'<p>{len(pl)} luogh{"i" if len(pl) > 1 else "o"} da visitare a {e(c["name"])}, '
                 f'in provincia di {e(prov)} ({e(reg)}). Ogni scheda è verificata su fonti ufficiali.</p>')
    if c.get("notice"): corpo.append(f'<p class="avviso"><b>Avviso:</b> {e(c["notice"])}</p>')
    corpo.append(f'<a class="apri" href="/#{e(c["slug"])}">Apri {e(c["name"])} nella guida con mappa e filtri</a>')
    for p in pl:
        corpo.append('<article class="luogo">' + blocco_breve(p, c) + "</article>")
    vicini = [x for x in REGIONI[c["regione"]] if x["prov"] == c["prov"] and x["slug"] != c["slug"] and x["places"]][:12]
    if vicini:
        corpo.append(f"<h2>Altri comuni in provincia di {e(prov)}</h2><ul class=\"elenco\">" + "".join(
            f'<li><a href="/comune/{e(x["slug"])}/">{e(x["name"])}</a></li>' for x in vicini) + "</ul>")
    if c.get("sources"):
        corpo.append('<h2>Fonti per questo comune</h2><p class="fonti">' + " · ".join(
            f'<a href="{e(s[1])}" rel="nofollow noopener">{e(s[0])}</a>' for s in c["sources"] if len(s) > 1) + "</p>")
    ld = {"@context": "https://schema.org", "@type": "ItemList", "name": titolo,
          "numberOfItems": len(pl),
          "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": p["name"],
                               "url": url_luogo(p) if (ap["luoghi"] and ricco(p)) else url_comune(c) + "#" + slug(p["id"], 80)}
                              for i, p in enumerate(pl[:60])]}
    scrivi(f"comune/{c['slug']}/index.html", pagina(titolo + " | Ach's Places Guide", descr, url_comune(c), "".join(corpo), ld, 2))
    urls.append((url_comune(c), "0.8"))

    if ap["luoghi"]:
        for p in pl:
            if not ricco(p): continue
            t2 = f"{p['name']}, {c['name']} ({c['prov']}): cosa sapere prima di andarci"
            d2 = taglia(p.get("desc"))
            b = [f'<p class="briciole"><a href="/">Italia</a> › <a href="/regione/{e(c["regione"])}/">{e(reg)}</a> › '
                 f'<a href="/comune/{e(c["slug"])}/">{e(c["name"])}</a></p>',
                 "<h1>" + e(p["name"]) + "</h1>",
                 blocco_pieno(p, c),
                 f'<a class="apri" href="/#{e(c["slug"])}">Vedi {e(c["name"])} sulla mappa della guida</a>']
            altri = [x for x in pl if x["id"] != p["id"]][:10]
            if altri:
                b.append(f'<h2>Altri luoghi a {e(c["name"])}</h2><ul class="elenco">' + "".join(
                    (f'<li><a href="/luogo/{e(x["id"])}/">{e(x["name"])}</a></li>' if ricco(x)
                     else f'<li><a href="/comune/{e(c["slug"])}/#{e(slug(x["id"], 80))}">{e(x["name"])}</a></li>')
                    for x in altri)
                    + f'</ul><p><a href="/comune/{e(c["slug"])}/">Tutti i {len(pl)} luoghi di {e(c["name"])}</a></p>')
            scrivi(f"luogo/{p['id']}/index.html", pagina(t2 + " | Ach's Places Guide", d2, url_luogo(p), "".join(b), ld_luogo(p, c), 2))
            urls.append((url_luogo(p), "0.6"))
            nluo += 1

for r, cs in REGIONI.items():
    cs = sorted([x for x in cs if x["places"]], key=lambda x: (x["prov"], x["name"]))
    if not cs: continue
    nl = sum(len(x["places"]) for x in cs)
    titolo = f"Cosa vedere in {NOMEREG[r]}: {nl} luoghi in {len(cs)} comuni"
    prov = {}
    for x in cs: prov.setdefault(x.get("provName") or x["prov"], []).append(x)
    corpo = [f'<p class="briciole"><a href="/">Italia</a></p><h1>Cosa vedere in {e(NOMEREG[r])}</h1>',
             f'<p class="lede">{nl} luoghi da visitare in {len(cs)} comuni della {e(NOMEREG[r])}, '
             "scelti e verificati su fonti ufficiali.</p>",
             f'<a class="apri" href="/#{e(cs[0]["slug"])}">Apri la {e(NOMEREG[r])} nella guida con mappa e filtri</a>']
    for pn, xs in sorted(prov.items()):
        corpo.append(f"<h2>Provincia di {e(pn)}</h2><ul class=\"elenco\">" + "".join(
            f'<li><a href="/comune/{e(x["slug"])}/">{e(x["name"])}</a> <span class="meta">({len(x["places"])})</span></li>'
            for x in xs) + "</ul>")
    scrivi(f"regione/{r}/index.html", pagina(titolo + " | Ach's Places Guide",
           taglia(f"I luoghi da visitare in {NOMEREG[r]}, comune per comune, con fonti ufficiali, orari e ingressi."),
           url_reg(r), "".join(corpo), None, 2))
    urls.append((url_reg(r), "0.9"))

tot = sum(len(c["places"]) for c in comuni)
corpo = ['<h1>Tutti i comuni della guida</h1>',
         f'<p class="lede">{tot} luoghi da visitare in {len([c for c in comuni if c["places"]])} comuni italiani, '
         "regione per regione.</p>"]
for r in sorted(REGIONI, key=lambda r: NOMEREG[r]):
    cs = [x for x in REGIONI[r] if x["places"]]
    if cs:
        corpo.append(f'<h2><a href="/regione/{e(r)}/">{e(NOMEREG[r])}</a></h2>'
                     f'<p class="meta">{len(cs)} comuni · {sum(len(x["places"]) for x in cs)} luoghi</p>')
scrivi("comuni/index.html", pagina("Tutti i comuni | Ach's Places Guide",
       f"I {tot} luoghi della guida, comune per comune e regione per regione.",
       f"{SITO}/comuni/", "".join(corpo), None, 1))
urls.append((f"{SITO}/comuni/", "0.9"))
urls.append((f"{SITO}/", "1.0"))

scrivi("pagine.css", CSS)

PER = 20000
parti = [urls[i:i + PER] for i in range(0, len(urls), PER)]
for i, parte in enumerate(parti, 1):
    scrivi(f"sitemap-{i}.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
               f"<url><loc>{e(u)}</loc><lastmod>{OGGI}</lastmod><priority>{p}</priority></url>\n" for u, p in parte)
           + "</urlset>\n")
scrivi("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
       '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
           f"<sitemap><loc>{SITO}/sitemap-{i}.xml</loc><lastmod>{OGGI}</lastmod></sitemap>\n"
           for i in range(1, len(parti) + 1)) + "</sitemapindex>\n")
scrivi("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITO}/sitemap.xml\n")

print(f"Scritte {len(urls)} pagine: {len([u for u, _ in urls if '/comune/' in u])} comuni, "
      f"{nluo} luoghi, {len(REGIONI)} regioni; {len(parti)} file di mappa del sito")
