#!/usr/bin/env python3
"""13/11/2026 – pagine per Google in inglese.

Dopo sorgenti/pagine.py (pagine italiane comune/, luogo/, regione/, comuni/) scrive le stesse pagine in inglese
sotto en/ (en/comune/<slug>/, en/luogo/<id>/, en/regione/<slug>/, en/comuni/), con:
- i testi delle schede presi dalla memoria delle traduzioni (ramo «traduzioni», Opus-MT it-en);
- le frasi delle pagine tradotte qui sotto (FRASI, SCHEMI) e il dizionario dell'interfaccia (en_diz.json);
- lang="en", og:locale en_GB, canonical /en/..., link alla guida con ?lang=en;
- rel="alternate" hreflang it/en/x-default sia nella pagina inglese sia in quella italiana;
- sitemap-en-N.xml aggiunte all'indice sitemap.xml.
I nomi dei luoghi, dei comuni e gli indirizzi restano in italiano. Non tocca la guida interattiva.
Uso: python3 pagine_en.py [radice del sito] [cartella della memoria (facoltativa)]
"""
import html, json, os, re, sys, glob, datetime
QUI = os.path.dirname(os.path.abspath(__file__))
RAD = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(QUI))
sys.path.insert(0, QUI)
import estrai, en_build
estrai.HERE = RAD
en_build.SITO = RAD
if len(sys.argv) > 2: en_build.MEMD = sys.argv[2]
SITO = "https://achplaces.com"
OGGI = datetime.date.today().isoformat()

MEM = en_build.memoria()
D = json.load(open(os.path.join(QUI, 'en_diz.json')))
IT = {}  # testo italiano completo per prefisso (descrizioni tagliate con «…»)
for l in open(os.path.join(QUI, 'testi_it.jsonl')):
    r = json.loads(l); IT.setdefault(r['t'][:60], r['t'])

FRASI = {
    "Eventi": "Events", "Osterie": "Dinners", "Mappa e filtri": "Map and filters", "Le guide di Ach": "Ach's guides",
    "Italia": "Italy", "Dove": "Where", "Ingresso": "Entry", "Tempo consigliato": "Suggested time",
    "Accessibilità": "Accessibility", "Sito ufficiale": "Official website", "Scheda sul portale turistico": "Tourist portal page",
    "Orari": "Opening hours", "pagina ufficiale": "official page", "Biglietti": "Tickets", "Fonti": "Sources",
    "Fonti per questo comune": "Sources for this town", "Avviso:": "Notice:", "Perché andarci.": "Why go.",
    "Luogo attualmente chiuso: verifica prima di partire.": "This place is currently closed: check before you go.",
    "Storia e architettura": "History and architecture", "Musei": "Museums", "Luoghi di culto": "Places of worship",
    "Natura e paesaggio": "Nature and landscape", "Vita e tradizioni locali": "Local life and traditions",
    "Patrimonio UNESCO": "UNESCO World Heritage", "Ingresso gratuito": "Free entry", "Ingresso a pagamento": "Paid entry",
    "Punto panoramico": "Viewpoint", "Biglietti su Tiqets": "Tickets on Tiqets",
    "Visite guidate su GetYourGuide": "Guided tours on GetYourGuide", "Biglietti sul sito ufficiale": "Tickets on the official website",
    "Guida completa, mappa e filtri": "Full guide, map and filters", "Tutti i comuni": "All towns",
    "Metodo e fonti": "Method and sources", "Tutti i comuni della guida": "All the towns in the guide",
    "Tutti i comuni | Ach's Places Guide": "All towns | Ach's Places Guide",
    "Gratuito": "Free", "Sito ufficiale del luogo": "Official website of the place", "Da verificare": "To be checked", "Da verificare con il gestore": "To be checked with the operator",
    "Testi originali di Ach's Places Guide; le informazioni pratiche sono riassunte dalle fonti ufficiali citate in ogni scheda. Alcuni link a biglietti e visite guidate sono affiliati: se acquisti, la guida riceve una commissione senza costi in più per te.":
        "Original texts by Ach's Places Guide, machine-translated from Italian (Opus-MT); practical information is summarised from the official sources cited in each entry. Some ticket and guided-tour links are affiliate links: if you buy, the guide receives a commission at no extra cost to you.",
}
def R(x): return T(x)
SCHEMI = [
    (r"^Cosa vedere a (.+) \((\w\w)\): (\d+) luogh[io] da visitare( \| Ach's Places Guide)?$",
     lambda m: f"What to see in {R(m[1])} ({m[2]}): {m[3]} {'place' if m[3] == '1' else 'places'} to visit{m[4] or ''}"),
    (r"^Cosa vedere (?:a|in) (.+): (\d+) luoghi in (\d+) comuni( \| Ach's Places Guide)?$",
     lambda m: f"What to see in {R(m[1])}: {m[2]} places in {m[3]} towns{m[4] or ''}"),
    (r"^Cosa vedere (?:a|in) (.+)$", lambda m: f"What to see in {R(m[1])}"),
    (r"^(\d+) luogh[io] da visitare a (.+), in provincia di (.+) \((.+)\)\. Ogni scheda è verificata su fonti ufficiali\.$",
     lambda m: f"{m[1]} {'place' if m[1] == '1' else 'places'} to visit in {R(m[2])}, in the province of {R(m[3])} ({R(m[4])}). Every entry is checked against official sources."),
    (r"^I luoghi da visitare a (.+), in provincia di (.+): (.+)$",
     lambda m: f"Places to visit in {R(m[1])}, in the province of {R(m[2])}: {m[3]}"),
    (r"^Apri (?:la |il |l')?(.+) nella guida con mappa e filtri$", lambda m: f"Open {R(m[1])} in the guide with map and filters"),
    (r"^Vedi (.+) sulla mappa della guida$", lambda m: f"See {R(m[1])} on the guide's map"),
    (r"^Altri luoghi a (.+)$", lambda m: f"Other places in {R(m[1])}"),
    (r"^Tutti i (\d+) luoghi di (.+)$", lambda m: f"All {m[1]} places in {R(m[2])}"),
    (r"^Altri comuni in provincia di (.+)$", lambda m: f"Other towns in the province of {R(m[1])}"),
    (r"^Provincia di (.+)$", lambda m: f"Province of {R(m[1])}"),
    (r"^(\d+) luoghi da visitare in (\d+) comuni della (.+), scelti e verificati su fonti ufficiali\.$",
     lambda m: f"{m[1]} places to visit in {m[2]} towns in {R(m[3])}, chosen and checked against official sources."),
    (r"^I luoghi da visitare in (.+), comune per comune, con fonti ufficiali, orari e ingressi\.$",
     lambda m: f"Places to visit in {R(m[1])}, town by town, with official sources, opening hours and entry."),
    (r"^(\d+) luoghi da visitare in (\d+) comuni italiani, regione per regione\.$",
     lambda m: f"{m[1]} places to visit in {m[2]} Italian towns, region by region."),
    (r"^I (\d+) luoghi della guida, comune per comune e regione per regione\.$",
     lambda m: f"The guide's {m[1]} places, town by town and region by region."),
    (r"^(.+), (.+) \((\w\w)\): cosa sapere prima di andarci( \| Ach's Places Guide)?$",
     lambda m: f"{m[1]}, {R(m[2])} ({m[3]}): what to know before you go{m[4] or ''}"),
    (r"^Aggiornato il ([\d-]+)$", lambda m: f"Updated on {m[1]}"),
    (r"^(\d+) comuni$", lambda m: f"{m[1]} towns"), (r"^(\d+) luoghi$", lambda m: f"{m[1]} places"),
    (r"^(\d+)-(\d+) minuti$", lambda m: f"{m[1]}-{m[2]} minutes"),
    (r"^([\d,]+)-([\d,]+) ore$", lambda m: f"{m[1].replace(',', '.')}-{m[2].replace(',', '.')} hours"),
    (r"^(\d+) ore e oltre$", lambda m: f"{m[1]} hours or more"),
]
SCHEMI = [(re.compile(a), b) for a, b in SCHEMI]

def taglia(s, n=155):
    s = re.sub(r"\s+", " ", str(s or "")).strip()
    return s if len(s) <= n else s[:n - 1].rsplit(" ", 1)[0] + "…"

CACHE = {}
def T(s):
    if not s or not s.strip(): return s
    if s in CACHE: return CACHE[s]
    v = T0(s); CACHE[s] = v; return v

def T0(s):
    a = s.strip()
    if a != s: x = T(a); return s.replace(a, x) if x != a else s
    if a in FRASI: return FRASI[a]
    if a in D: return D[a]
    k = estrai.en_k(a)
    if k in MEM: return MEM[k]
    if a.endswith("…") and len(a) > 40:
        full = IT.get(a[:60])
        if full and full.startswith(a[:-1].rstrip()):
            k = estrai.en_k(full)
            if k in MEM: return taglia(MEM[k])
    for re_, f in SCHEMI:
        m = re_.match(a)
        if m:
            try: return f(m)
            except Exception: pass
    if " · " in a:
        p = a.split(" · "); t = [T(x) for x in p]
        if t != p: return " · ".join(t)
    m = re.match(r"^(.+?)([:.]\s*)$", a)
    if m:
        x = T(m[1])
        if x != m[1]: return x + m[2]
    return a

TESTO = re.compile(r">([^<>]+)<")
def tr_html(h, url_it, url_en, prof):
    # testa
    h = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]*">', '', h)
    h = h.replace('<html lang="it">', '<html lang="en">', 1).replace('content="it_IT"', 'content="en_GB"')
    h = h.replace(f'<link rel="canonical" href="{url_it}">', f'<link rel="canonical" href="{url_en}">')
    h = h.replace(f'<meta property="og:url" content="{url_it}">', f'<meta property="og:url" content="{url_en}">')
    alt = (f'<link rel="alternate" hreflang="it" href="{url_it}"><link rel="alternate" hreflang="en" href="{url_en}">'
           f'<link rel="alternate" hreflang="x-default" href="{url_it}">')
    h = h.replace('<link rel="stylesheet" href="', alt + '<link rel="stylesheet" href="../' if prof else alt + '<link rel="stylesheet" href="../', 1)
    def meta(m):
        return m[1] + html.escape(T(html.unescape(m[2])), quote=True) + m[3]
    h = re.sub(r'(<meta (?:name="description"|property="og:title"|property="og:description") content=")([^"]*)(")', meta, h)
    h = re.sub(r'(aria-label=")([^"]*)(")', meta, h)
    def ld(m):
        try:
            j = json.loads(m[2])
            if j.get("@type") == "ItemList" and j.get("name"): j["name"] = T(j["name"])
            if j.get("description"): j["description"] = T(j["description"])
            if j.get("url", "").startswith(SITO + "/") and "/luogo/" in j["url"]: j["url"] = j["url"].replace(SITO + "/", SITO + "/en/", 1)
            for it in j.get("itemListElement", []) or []:
                u = it.get("url", "")
                if u.startswith(SITO + "/") and not u.startswith(SITO + "/en/"): it["url"] = u.replace(SITO + "/", SITO + "/en/", 1)
            return m[1] + json.dumps(j, ensure_ascii=False, separators=(",", ":")) + m[3]
        except Exception:
            return m[0]
    h = re.sub(r'(<script type="application/ld\+json">)(.*?)(</script>)', ld, h, flags=re.S)
    # collegamenti interni
    h = re.sub(r'href="/(comune|luogo|regione|comuni)/', r'href="/en/\1/', h)
    h = h.replace('href="/#', 'href="/?lang=en#').replace('href="/"', 'href="/?lang=en"')
    # testi
    i = h.index("<body>")
    testa, corpo = h[:i], h[i:]
    testa = re.sub(r"<title>(.*?)</title>", lambda m: "<title>" + html.escape(T(html.unescape(m[1])), quote=False) + "</title>", testa, flags=re.S)
    def txt(m):
        t = m[1]
        if not t.strip() or t.lstrip().startswith("{"): return m[0]
        u = html.unescape(t); x = T(u)
        return ">" + (html.escape(x, quote=False) if x != u else t) + "<"
    parti = re.split(r"(<script.*?</script>)", corpo, flags=re.S)
    corpo = "".join(p if p.startswith("<script") else TESTO.sub(txt, p) for p in parti)
    return testa + corpo

def alt_it(h, url_it, url_en):
    h = re.sub(r'<link rel="alternate" hreflang="[^"]+" href="[^"]*">', '', h)
    alt = (f'<link rel="alternate" hreflang="it" href="{url_it}"><link rel="alternate" hreflang="en" href="{url_en}">'
           f'<link rel="alternate" hreflang="x-default" href="{url_it}">')
    return h.replace('<link rel="stylesheet" href="', alt + '<link rel="stylesheet" href="', 1)

def main():
    urls = []; n = 0
    pag = sorted(glob.glob(os.path.join(RAD, "comune", "*", "index.html")) + glob.glob(os.path.join(RAD, "luogo", "*", "index.html"))
                 + glob.glob(os.path.join(RAD, "regione", "*", "index.html")) + [os.path.join(RAD, "comuni", "index.html")])
    vivi = set()
    for f in pag:
        if not os.path.exists(f): continue
        rel = os.path.relpath(f, RAD).replace(os.sep, "/")
        dirr = rel[:-len("index.html")]
        url_it, url_en = f"{SITO}/{dirr}", f"{SITO}/en/{dirr}"
        h = open(f, encoding="utf-8").read()
        prof = dirr.count("/")
        en = tr_html(h, url_it, url_en, prof)
        dest = os.path.join(RAD, "en", rel); os.makedirs(os.path.dirname(dest), exist_ok=True)
        vivi.add(os.path.normpath(dest))
        old = open(dest, encoding="utf-8").read() if os.path.exists(dest) else None
        if old != en: open(dest, "w", encoding="utf-8").write(en)
        hi = alt_it(h, url_it, url_en)
        if hi != h: open(f, "w", encoding="utf-8").write(hi)
        pr = "0.8" if rel.startswith("comune/") else "0.6" if rel.startswith("luogo/") else "0.9"
        urls.append((url_en, pr)); n += 1
    # pagine inglesi di luoghi o comuni che non esistono piu'
    for f in glob.glob(os.path.join(RAD, "en", "*", "*", "index.html")):
        if os.path.normpath(f) not in vivi: os.remove(f);
    # mappa del sito
    for f in glob.glob(os.path.join(RAD, "sitemap-en-*.xml")): os.remove(f)
    parti = [urls[i:i + 40000] for i in range(0, len(urls), 40000)]
    for i, p in enumerate(parti, 1):
        open(os.path.join(RAD, f"sitemap-en-{i}.xml"), "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"<url><loc>{u}</loc><lastmod>{OGGI}</lastmod><priority>{pr}</priority></url>\n" for u, pr in p) + "</urlset>\n")
    si = os.path.join(RAD, "sitemap.xml")
    if os.path.exists(si):
        s = open(si).read()
        s = re.sub(r"<sitemap><loc>[^<]*sitemap-en-\d+\.xml</loc>.*?</sitemap>\n?", "", s)
        s = s.replace("</sitemapindex>", "".join(f"<sitemap><loc>{SITO}/sitemap-en-{i}.xml</loc><lastmod>{OGGI}</lastmod></sitemap>\n" for i in range(1, len(parti) + 1)) + "</sitemapindex>")
        open(si, "w").write(s)
    print(f"pagine_en: {n} pagine inglesi in en/, {len(parti)} file di mappa del sito")

if __name__ == "__main__":
    main()
