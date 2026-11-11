#!/usr/bin/env python3
"""Costruisce index.html: legge i file data/spec-*.txt (formato a righe) e data/places-bologna.js,
produce i blocchi JS COMUNI e SOURCES e li inserisce nel template al posto di /*PLACES*/."""
import json, re, os, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "data")
VERIFIED = "6 novembre 2026"
PROV = {"BO": ("Bologna", "Città metropolitana", "emilia-romagna"), "RA": ("Ravenna", "Provincia", "emilia-romagna"),
        "FE": ("Ferrara", "Provincia", "emilia-romagna"), "FC": ("Forlì-Cesena", "Provincia", "emilia-romagna"),
        "RN": ("Rimini", "Provincia", "emilia-romagna"), "FI": ("Firenze", "Città metropolitana", "toscana"),
        "PC": ("Piacenza", "Provincia", "emilia-romagna"), "PR": ("Parma", "Provincia", "emilia-romagna"),
        "RE": ("Reggio Emilia", "Provincia", "emilia-romagna"), "MO": ("Modena", "Provincia", "emilia-romagna"),
        "SI": ("Siena", "Provincia", "toscana")}
PROVSRC = {"SI": ("Visit Tuscany", "https://www.visittuscany.com/en/towns-and-villages/{}/")}
PJ = json.load(open(os.path.join(D, "province.json"), encoding="utf-8"))
for _k,_v in PJ.items():
    PROV[_k] = (_v["name"], _v["kind"], _v["region"])
    if _v.get("src"): PROVSRC[_k] = tuple(_v["src"])
# fonte regionale di base per ogni comune: nome e modello di indirizzo
REGSRC = {"emilia-romagna": ("Emilia Romagna Turismo", "https://emiliaromagnaturismo.it/en/towns/{}"),
          "toscana": ("Feel Florence", "https://www.feelflorence.it/it")}
DUR = {"short": "30-45 minuti", "mid": "1-1,5 ore", "long": "2 ore e oltre"}
WIKI = {"Lugo": "Lugo_(Italia)", "Medicina": "Medicina_(Italia)", "Bentivoglio": "Bentivoglio_(Italia)", "Argenta": "Argenta_(Italia)", "Cento": "Cento_(Italia)", "Vinci": "Vinci_(Italia)", "Cattolica": "Cattolica_(Italia)", "Santa Sofia": "Santa_Sofia_(Italia)"}
AW = {"borghi": "borghi", "arancione": "arancione", "unesco": "unesco", "creative": "creative"}

_STOP = set("chiesa chiese museo musei civico civica parco area archeologica archeologico della delle dello degli dei del di da la le il lo gli san santa santo sant santi madonna basilica cattedrale duomo palazzo castello torre villa piazza centro storico borgo antico antica nazionale regionale comunale e ed con per tra fra sul sulla nel nella al alla ai alle in a casa monumento monumentale complesso".split())
_TK = re.compile(r"bigliett|ticket|tariff|prezz|ingress|admission|prices|biglietteria")
_HR = re.compile(r"orari|opening|hours|apertur|timetable")
def _parole(t):
    t = "".join(ch for ch in unicodedata.normalize("NFD", t.lower()) if not unicodedata.combining(ch))
    return [w for w in re.split(r"[^a-z0-9]+", t) if len(w) >= 4 and w not in _STOP]
AUTO = {"tk": [], "hr": []}
_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
def _jl(n):
    try: return json.load(open(os.path.join(_DATA, n)))
    except Exception: return {}
BIG_GH = _jl("biglietti.json"); BIG_AG = _jl("biglietti_agenti.json")
_LC = _jl("link_correzioni.json"); LINK_RID = _LC.get("rid", {}); LINK_ROTTI = set(_LC.get("rotti", {}))
# 10/11/2026 sera: titolo esatto della voce di it.wikipedia (data/wiki.json da Wikidata, piu' wiki-<gruppo>.json dal lavoro su GitHub)
WIKI = {}
for _wf in [os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "wiki.json")]:   # gia' filtrato da wiki_unisci.py
    try: WIKI.update({k: v for k, v in json.load(open(_wf)).items() if k not in WIKI})
    except Exception: pass
def _via(u):
    """solo percorso e query dell'indirizzo, senza il dominio: «visitmodena.it» non e' una pagina di orari"""
    v = u.split("://", 1)[-1].split("/", 1)[-1].lower() if "/" in u.split("://", 1)[-1] else ""
    # notizie, eventi e aperture straordinarie non sono la pagina stabile di orari o biglietti
    return "" if re.search(r"evento|event|news|novita|notizi|avviso|blog|straordinar|eccezional|riapertura|\d+-hours|itinerar|reopening|nuove-aperture|/20\d\d/", v) else v
def link_da_fonti(name, srcs, csrcs):
    pw = _parole(name.split(",")[0])
    def cerca(rx):
        for s in srcs:
            if (len(s) < 3 or s[2] == "uff") and s[1].startswith("https://") and rx.search(_via(s[1])): return s[1]
        if not pw: return ""
        for n, u in csrcs:
            txt = " ".join(_parole(n + " " + u.replace("-", " ").replace("/", " ")))
            if u.startswith("https://") and rx.search(_via(u)) and sum(1 for w in pw if w in txt) >= min(2, len(pw)): return u
        return ""
    return cerca(_TK), cerca(_HR)

def slugify(s):
    s = s.lower().replace("'", "-").replace("à", "a").replace("è", "e").replace("é", "e").replace("ì", "i").replace("ò", "o").replace("ù", "u")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


import csv, unicodedata
ALIAS={"reggioemilia":"reggionellemilia"}
def norm0(s):
    s=unicodedata.normalize("NFD",s.lower()); s="".join(ch for ch in s if unicodedata.category(ch)!="Mn")
    return re.sub(r"[^a-z]","",s)
def norm(s):
    k=norm0(s); return ALIAS.get(k,k)
GEO={}
for g in json.load(open(os.path.join(D,"geo","italy_geo.json"),encoding="utf-8")):
    try: GEO.setdefault(norm(g["comune"]),(float(g["lat"]),float(g["lng"])))
    except: pass
# comuni nati da fusioni dopo il 2018: media dei comuni d'origine
FUS={"barberinotavarnelle":["barberinovaldelsa","tavarnellevaldipesa"],"rivadelpo":["berra","ro"],"tresignana":["formignana","tresigallo"],"presicceacquarica":["presicce","acquaricadelcapo"],"sangiovannidifassa":["pozzadifassa","vigodifassa"],"borgovalbelluna":["mel","lentiai","trichiana"],"luecuccaromonferrato":["lu","cuccaromonferrato"]}
ISTAT={}
for r in csv.DictReader(open(os.path.join(D,"geo","comuni_istat.csv"),encoding="utf-8")):
    ISTAT[(norm(r["comune"]),r["sigla"])]=r["pro_com_t"]
def geo_of(name):
    k=norm(name)
    if k in GEO: return GEO[k]
    if k in FUS:
        pts=[GEO[x] for x in FUS[k] if x in GEO]
        if pts: return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))
    return None

LINKS = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "links.json"), encoding="utf-8"))

def notip(t):
    import re as _re
    return "" if _re.search(r"€|\d{1,2}[.:]\d{2}|orari|prezz|biglietto", t, _re.I) else t

def parse(path):
    comuni = []; c = None
    for raw in open(path, encoding="utf-8"):
        line = raw.rstrip("\n")
        if not line.strip(): continue
        if line.startswith("@ "):
            f = [x.strip() for x in line[2:].split("|")]
            name, istat, prov, ert = f[0], f[1], f[2], f[3]
            aw = f[4].split() if len(f) > 4 and f[4] else []
            reg = PROV[prov][2]; rname, rfmt = PROVSRC.get(prov) or REGSRC[reg]
            ertu = ert if ert.startswith("http") else rfmt.format(ert)
            c = dict(slug=slugify(name) + "-" + prov.lower(), name=name, istat=istat, regione=reg, prov=prov, rname=rname,
                     provName=PROV[prov][0], provKind=PROV[prov][1], verified=VERIFIED, cardName="", aw=aw, lede="", notice="",
                     ert=ertu, sources=[], places=[])
            comuni.append(c); continue
        if line.startswith("lede:"): c["lede"] = line[5:].strip(); continue
        if line.startswith("inv:"):
            # inventario: luoghi elencati dalla fonte ufficiale del comune, separati da ";" e seguiti da "^url"
            body, _, u = line[4:].strip().partition("^")
            c.setdefault("inv", []).append(([x.strip() for x in body.split(";") if x.strip()], u.strip())); continue
        if line.startswith("scarto:"):
            n, _, why = line[7:].strip().partition("|"); c.setdefault("scarti", {})[n.strip()] = why.strip(); continue
        if line.startswith("notice:"): c["notice"] = line[7:].strip(); continue
        if line.startswith("copertura:"): c["copertura"] = line[10:].strip(); continue
        if line.startswith("minimo:"):
            _n, _m = (line[7:].split("|", 1) + [""])[:2]; c["minimo"] = (int(_n.strip()), _m.strip()); continue
        if line.startswith("card:"): c["cardName"] = line[5:].strip(); continue
        if line.startswith("src:"):
            n, u = line[4:].strip().split("^"); c["sources"].append([n, u]); continue
        if line.startswith("- "):
            f = [x.strip() for x in line[2:].split("|")]
            name, cs, t, flags, price, desc, why, addr = f[:8]
            extra = {}
            srcs = []
            if len(f) > 8:
                for kv in f[8].split(" ; "):
                    if not kv.strip(): continue
                    k, v = kv.split("=", 1); k = k.strip(); v = v.strip()
                    if k == "src":
                        a = v.split("^"); srcs.append([a[0], a[1], a[2] if len(a) > 2 else "uff"])
                    else: extra[k] = v
            cat, sub = cs.split("/")
            free = True if price == "free" else (None if price.lower().startswith("da verificare") else False)
            ptxt = extra.get("price") or ("Gratuito" if price == "free" else price)
            if price == "free" and "price" in extra: free = True
            status = "closed" if "c" in flags else ("warn" if "w" in flags else "ok")
            pid = c["slug"] + "--" + slugify(name)[:40]
            off = extra.get("off", c["ert"])
            base_src = [f"{c['rname']}, {c['name']}", c["ert"], "uff"]
            if not any(s[1] == c["ert"] for s in srcs):
                srcs.append(base_src)
            if "off" in extra and not any(s[1] == extra["off"] for s in srcs):
                srcs.insert(0, ["Sito ufficiale del luogo", extra["off"], "uff"])
            p = dict(id=pid, name=name, cat=cat, sub=sub, desc=desc, why=why, address=addr, price=ptxt, free=free,
                     card="k" in flags, unesco="u" in flags, view="v" in flags, indoor="i" in flags, status=status,
                     statusNote=extra.get("note", "") if status != "ok" else "", rev=extra.get("rev", ""), tip=notip(extra.get("tip") or (extra.get("note", "") if status == "ok" else "")),
                     hours=extra.get("hours", "Verifica sul sito ufficiale prima di partire" if free is not True else "Spazio aperto o accesso libero; verifica eventuali limitazioni"),
                     booking=extra.get("book", "Non indicata dalle fonti"), duration=DUR[t], t=t,
                     access=extra.get("access", "Da verificare con il gestore"), official=off, ownSite=("off" in extra or extra.get("book","").startswith("http")), sources=srcs)
            lk = LINKS["spec"].get(c["name"] + "|" + name, {})
            p["hoursUrl"] = extra.get("orari") or lk.get("orari", "")
            p["ticketUrl"] = extra.get("biglietti") or lk.get("biglietti", "")
            if lk.get("off") and "off" not in extra: p["official"] = lk["off"]; p["ownSite"] = True
            # 10/11/2026 sera: se mancano i link precisi, li prende dalle fonti ufficiali gia' citate (del luogo, o del
            # comune quando il nome della fonte nomina il luogo) che sono pagine di biglietti/tariffe o di orari.
            if not p["ticketUrl"] or not p["hoursUrl"]:
                _tk, _hr = link_da_fonti(name, srcs, c["sources"])
                if not p["ticketUrl"] and _tk and free is not True: p["ticketUrl"] = _tk; AUTO["tk"].append((c["name"], name, _tk))
                if not p["hoursUrl"] and _hr: p["hoursUrl"] = _hr; AUTO["hr"].append((c["name"], name, _hr))
            # 11/11/2026: biglietti e orari dalle ricerche (lavoro GitHub sulle pagine ufficiali, poi ricerche una per una)
            _bg = BIG_AG.get(pid) or {}
            if _bg.get("free") is True and free is not True:
                free = p["free"] = True; p["price"] = "Gratuito"
                if _bg.get("tk"): p["sources"].append(["Ingresso gratuito (pagina ufficiale)", _bg["tk"], "uff"])
            elif _bg.get("free") is False and free is None: free = p["free"] = False
            if _bg.get("tk") and not p["ticketUrl"] and free is not True: p["ticketUrl"] = _bg["tk"]
            if _bg.get("hr") and not p["hoursUrl"]: p["hoursUrl"] = _bg["hr"]
            _bc = BIG_GH.get(pid) or {}
            if _bc.get("tk") and not p["ticketUrl"] and free is not True: p["ticketUrl"] = _bc["tk"]
            if "free" in _bc and free is None:
                free = p["free"] = True; p["price"] = "Gratuito"; p["sources"].append(["Ingresso libero (pagina ufficiale)", _bc["da"], "uff"])
            if p["ticketUrl"] or p["hoursUrl"]: p["ownSite"] = True
            for k in ("hoursUrl", "ticketUrl"):
                if p[k] and not any(x[1] == p[k] for x in p["sources"]): p["sources"].append([("Orari ufficiali" if k == "hoursUrl" else "Biglietti ufficiali") + " (pagina del gestore)", p[k], "uff"])
            if extra.get("mic"): p["mic"] = extra["mic"].split()
            if WIKI.get(pid): p["wk"] = WIKI[pid]
            c["places"].append(p)
    for c in comuni:
        g = geo_of(c["name"])
        if g: c["lat"], c["lng"] = round(g[0], 5), round(g[1], 5)
        else: print("NO GEO:", c["name"])
        ist = ISTAT.get((norm(c["name"]), c["prov"]))
        if ist: c["istat"] = ist
        elif c["istat"] in ("-", ""): print("NO ISTAT:", c["name"])
        w = WIKI.get(c["name"], c["name"].replace(" ", "_"))
        base = [[f"{c['rname']}, scheda di {c['name']}" if c["rname"] != "Feel Florence" else "Feel Florence, portale turistico della Città metropolitana di Firenze", c["ert"]]]
        c["sources"] = c["sources"] + base + [[f"Wikipedia, {c['name']} (fonte secondaria)", "https://it.wikipedia.org/wiki/" + w]]
        del c["ert"]; del c["rname"]
        c["sources"] = list({s[1]: s for s in c["sources"]}.values())
    return comuni

import glob
ORDER = ["bo", "ra", "fe", "fc", "rn", "mo", "re", "pr", "pc", "fi", "si"] + [k.lower() for k in PJ]
files = sorted(glob.glob(os.path.join(D, "spec-*.txt")), key=lambda f: (ORDER.index(f[-6:-4]) if f[-6:-4] in ORDER else 99, f))
comuni = [c for f in files for c in parse(f)]
sources = json.load(open(os.path.join(D, "sources.json"), encoding="utf-8"))
# 10/11/2026 Archivio fonti riorganizzato: tutte le fonti citate nelle schede, raggruppate per ente (dominio) e per regione.
# Nazionali = enti citati in almeno 3 regioni; le altre stanno nella loro regione, divise per tipo. Il registro di lavoro
# (sources.json) resta solo per le fonti «da consultare» o «consultate ma scartate» e per i nomi degli enti.
def _fonti():
    from urllib.parse import urlsplit
    import collections as _co
    FAM = ("cultura.gov.it", "beniculturali.it", "touringclub.it", "borghipiubelliditalia.it", "fondoambiente.it", "italia.it",
           "unesco.org", "wikipedia.org", "bandierearancioni.it", "parks.it", "isprambiente.gov.it")
    def fam(u):
        h = urlsplit(u).netloc.lower().split(":")[0]
        h = h[4:] if h.startswith("www.") else h
        for f in FAM:
            if h == f or h.endswith("." + f): return f
        return h
    def tipo(h):
        if "wikipedia" in h: return "sec"
        if re.search(r"(^|\.)comune\.|comune-|\.comune|comunedi|^comune", h): return "com"
        if re.search(r"parco|park|riserv|oasi|parchi|natura|geopark|wwf|lipu|cai\.it|sentier", h): return "nat"
        if re.search(r"muse|galleri|pinacotec|fondazione|castell|villa|rocca|teatro", h): return "mus"
        if re.search(r"diocesi|chiesa|chiese|parrocchi|santuari|abbazi|monaster|beweb|duomo|cattedral|basilica|convento|vatican", h): return "sac"
        if re.search(r"regione|turis|visit|welcome|provincia|cittametropolitana|\.tour|travel|guide|unione|gal|proloco|pro-loco|consorzio|ecomuse|apt|iat", h): return "tur"
        return "alt"
    NOMI = {"cultura.gov.it": "Ministero della Cultura (luoghi, musei, soprintendenze)", "beniculturali.it": "Catalogo generale dei beni culturali (MiC, ICCD)",
            "touringclub.it": "Touring Club Italiano", "borghipiubelliditalia.it": "I Borghi più belli d'Italia", "fondoambiente.it": "FAI, Fondo per l'Ambiente Italiano",
            "italia.it": "Italia.it, portale turistico nazionale (ENIT)", "unesco.org": "UNESCO, Patrimonio mondiale", "wikipedia.org": "Wikipedia (fonte secondaria)",
            "bandierearancioni.it": "Bandiere Arancioni (Touring Club)", "parks.it": "Parks.it, portale dei parchi italiani", "isprambiente.gov.it": "ISPRA, Istituto superiore per la protezione e la ricerca ambientale"}
    R = _co.defaultdict(dict)
    def add(reg, comune, s, luogo):
        if not (isinstance(s, (list, tuple)) and len(s) > 1 and str(s[1]).startswith("http")): return
        f = fam(s[1]); e = R[reg].get(f)
        if e is None: e = R[reg][f] = dict(n=_co.Counter(), l=0, c=set(), u=False, h=s[1])
        e["n"][re.split(r",| – | - |\(", s[0])[0].strip()] += 1; e["c"].add(comune); e["l"] += 1 if luogo else 0
        e["u"] |= (len(s) > 2 and s[2] == "uff") or "wikipedia" not in f
    for c in comuni:
        for s in c.get("sources", []): add(c["regione"], c["name"], s, False)
        for p in c["places"]:
            for s in p.get("sources", []): add(c["regione"], c["name"], s, True)
    quante = _co.Counter(f for r in R for f in R[r])
    def voce(f, es):
        n = _co.Counter(); l = 0; cs = set(); u = False
        for e in es: n.update(e["n"]); l += e["l"]; cs |= e["c"]; u |= e["u"]
        nome = NOMI.get(f) or n.most_common(1)[0][0] or f
        return dict(d=f, n=nome, l=l, nc=len(cs), c=sorted(cs, key=str.lower)[:12], t=tipo(f), u=1 if u else 0)
    naz = sorted((voce(f, [R[r][f] for r in R if f in R[r]]) | dict(nr=quante[f]) for f in quante if quante[f] >= 3), key=lambda v: (-v["nc"], v["n"].lower()))
    for v in naz: v.pop("c")
    reg = {r: sorted((voce(f, [e]) for f, e in R[r].items() if quante[f] < 3), key=lambda v: (-v["nc"], v["n"].lower())) for r in sorted(R)}
    reg = {r: v for r, v in reg.items() if v}
    reg_l = {}
    for x in sources:
        if x.get("uso") in ("da consultare", "consultata ma scartata", "consultata"):
            reg_l.setdefault("lavoro", []).append(dict(n=x["name"], h=x["url"], uso=x["uso"], note=x.get("note", ""), quando=x.get("checked", "")))
    tot = len(naz) + sum(len(v) for v in reg.values())
    return dict(naz=naz, reg=reg, lav=reg_l.get("lavoro", []), tot=tot)
FONTI = _fonti()
print("archivio fonti:", FONTI["tot"], "enti,", len(FONTI["naz"]), "nazionali,", len(FONTI["reg"]), "regioni")
import check, sys
n_bo = open(os.path.join(D, "places-bologna.js"), encoding="utf-8").read().count("{id:")
errs, warns, qc = check.run(comuni, PROV, {"BO": n_bo}, {"BO": ["Bologna"]})
for c in comuni:
    r = check.MIC_REPORT.get(f'{c["name"]} ({c["prov"]})')
    if r and r["mancanti"] and c.get("copertura") != "completa":
        msg = f"Elenco in ampliamento: la guida copre per ora {r['coperti']} dei {r['tot']} luoghi della cultura censiti dal Ministero della Cultura in questo comune, oltre a chiese, piazze e natura."
        c["notice"] = (c["notice"] + " " + msg).strip() if c.get("notice") else msg
json.dump(dict(errors=errs, warnings=warns, table=qc), open(os.path.join(D, "qc-report.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"Controllo qualità: {len(errs)} errori, {len(warns)} avvisi")
for e in errs[:40]: print("  E", e)
if errs and "--force" not in sys.argv: sys.exit("Build fermato: correggi gli errori (o usa --force)")
bologna_places = open(os.path.join(D, "places-bologna.js"), encoding="utf-8").read()
ARCH = []
for _f in sorted(glob.glob(os.path.join(D, "archivio", "comuni-*.json"))):
    _d = json.load(open(_f, encoding="utf-8")); _c = _d["comuni"]
    _g = {c["name"] for c in comuni if c["regione"] == _d["regione"]} | ({"Bologna"} if _d["regione"] == "emilia-romagna" else set())
    ARCH.append(dict(r=_d["regione"], n=len(_c), sito=sum(1 for x in _c if x["sito"]), mic=sum(1 for x in _c if x["mic"]), micl=sum(len(x["mic"]) for x in _c), guida=len(_g)))
import hashlib
import copy
import math
PUNTI = json.load(open(os.path.join(D, "punteggi.json"), encoding="utf-8"))
def punteggio(p, slug):
    """Rilevanza 0-100: albi, guide, classifiche pubbliche, natura. Stesse regole per ogni comune."""
    s = 0; u = " ".join(x[1] for x in p.get("sources", []) if isinstance(x, (list, tuple)) and len(x) > 1)
    x = PUNTI.get(f"{slug}|{p['id']}", {})
    if p.get("unesco"): s += 30 if x.get("unesco_nome") else 12
    if x.get("autonomo"): s += 12
    if p.get("mic"): s += 5
    s += {2: 15, 1: 8}.get(x.get("tci", 0), 6 if "touringclub.it" in u else 0)
    if "italia.it" in u: s += 8
    if x.get("dnp"): s += 6
    if x.get("visitatori"): s += min(20, max(0, round(4 * math.log10(max(1, x["visitatori"])) - 12)))
    if x.get("fai"): s += max(1, 6 - x["fai"] // 20)
    s += min(12, x.get("natura", 0))
    s += min(2, max(0, len(p.get("sources", [])) - 1)) * 2
    if p.get("status") == "closed": s -= 10
    return max(0, min(100, s))
for _c in comuni:
    for _p in _c["places"]: _p["r"] = punteggio(_p, _c["slug"])
# 9/11/2026 Tiqets: pagina prodotto esatta per i luoghi che vende (data/tiqets.json da tiqets_abbina.py)
TQ = json.load(open(os.path.join(D, "tiqets.json"))) if os.path.exists(os.path.join(D, "tiqets.json")) else {}
for _c in comuni:
    for _p in _c["places"]:
        if _p["id"] in TQ: _p["tq"] = TQ[_p["id"]]
# 9/11/2026 GetYourGuide (partner Y9VWGXI): pagina attività esatta per i luoghi che vende (data/gyg.json da gyg_abbina.py)
GY = json.load(open(os.path.join(D, "gyg.json"))) if os.path.exists(os.path.join(D, "gyg.json")) else {}
for _c in comuni:
    for _p in _c["places"]:
        if _p["id"] in GY: _p["gy"] = GY[_p["id"]]
_tqp=[_p for _c in comuni for _p in _c["places"] if _p.get("tq")]
print("GetYourGuide: luoghi abbinati", sum(1 for _c in comuni for _p in _c["places"] if _p.get("gy")))
print("Tiqets: luoghi abbinati", len(_tqp), "| bottone in card", sum(1 for _p in _tqp if _p.get("free") is not True and not _p.get("ticketUrl")), "| link in scheda", sum(1 for _p in _tqp if _p.get("free") is not True), "| gratuiti esclusi", sum(1 for _p in _tqp if _p.get("free") is True))
PESANTI = ("why", "access", "official", "ownSite", "sources", "tip", "statusNote", "hoursUrl", "wk")   # ticketUrl resta nell'indice: tasto Ticket nelle card (8/11)
VIA = ("hours", "booking", "rev", "mic")          # non usati dalla pagina
# 9/11/2026 prezzo stimato (richiesta di Stefano) per i luoghi con ingresso «da verificare»: dai luoghi verificati dello stesso
# tipo (nella stessa regione se ce ne sono almeno 8, altrimenti in tutta la guida). Se almeno 3 su 4 sono gratuiti → «probabilmente
# gratis»; altrimenti la mediana dei prezzi interi. È sempre mostrato come stima, con il rimando al sito ufficiale.
import statistics as _st
def _eur(t):
    m = re.search(r'(\d+(?:[.,]\d+)?)\s*€|€\s*(\d+(?:[.,]\d+)?)', t or '')
    if not m: return None
    v = float((m.group(1) or m.group(2)).replace(',', '.'))
    return v if 0 < v < 60 else None
_campioni = {}
for _c in comuni:
    for _p in _c["places"]:
        if _p.get("free") is True: v = 0.0
        elif _p.get("free") is False: v = _eur(_p.get("price"))
        else: continue
        if v is None: continue
        _campioni.setdefault((_p["sub"], _c.get("regione")), []).append(v); _campioni.setdefault((_p["sub"], None), []).append(v)
_nst = [0, 0]
for _c in comuni:
    for _p in _c["places"]:
        if _p.get("free") is not None: continue
        cs = _campioni.get((_p["sub"], _c.get("regione")), [])
        if len(cs) < 8: cs = _campioni.get((_p["sub"], None), [])
        if len(cs) < 5: continue
        if sum(1 for v in cs if v == 0) / len(cs) >= 0.75: _p["ps"] = 0; _nst[0] += 1
        else:
            pag = [v for v in cs if v > 0]
            if pag: _p["ps"] = int(round(_st.median(pag))); _nst[1] += 1
print("prezzo stimato: probabilmente gratis", _nst[0], "| stima in euro", _nst[1])
for _cc in comuni:   # 11/11: fonti dei comuni, stessa correzione dei link
    _fs = [[_s[0], LINK_RID.get(_s[1], _s[1])] + list(_s[2:]) for _s in _cc["sources"]]
    _cc["sources"] = [_s for _s in _fs if _s[1] not in LINK_ROTTI] or _fs
_leggeri = copy.deepcopy(comuni); _det = {}
# 9/11/2026 velocità: nella prima schermata solo nome, categoria, comune, etichette e filtri.
# Le descrizioni vanno nei file per provincia, tranne quelle dei luoghi più in alto in classifica (prime card della vista «tutti»);
# lede, avvisi e fonti dei comuni vanno nei file per provincia (chiave "_c").
_TOP = {p["id"] for p in sorted((p for c in comuni for p in c["places"]), key=lambda p: (-p.get("r", 0), p["name"]))[:100]}
for _c in _leggeri:
    _cc = {k: _c.pop(k) for k in ("lede", "notice", "sources") if k in _c}
    if _cc: _det.setdefault(_c["prov"], {}).setdefault(_c["slug"], {})["_c"] = _cc
    for _p in _c["places"]:
        if _p["id"] not in _TOP and _p.get("desc"): _det.setdefault(_c["prov"], {}).setdefault(_c["slug"], {}).setdefault(_p["id"], {})["desc"] = _p.pop("desc")
        # 11/11/2026: correzione dei link dal controllo settimanale (link.yml): reindirizzamenti -> indirizzo nuovo,
        # pagine sparite (404/410 o rimandate alla home) -> tolte; il sito ufficiale rotto lascia il posto alla prima fonte ufficiale viva.
        for _k in ("official", "ticketUrl", "hoursUrl", "tf"):
            if _p.get(_k): _p[_k] = LINK_RID.get(_p[_k], _p[_k])
        _p["sources"] = [[_s[0], LINK_RID.get(_s[1], _s[1])] + list(_s[2:]) for _s in _p["sources"]]
        _vive = [_s for _s in _p["sources"] if _s[1] not in LINK_ROTTI]
        if _vive: _p["sources"] = _vive
        for _k in ("ticketUrl", "hoursUrl", "tf"):
            if _p.get(_k) in LINK_ROTTI: _p.pop(_k)
        if _p.get("official") in LINK_ROTTI:
            _alt = [_s[1] for _s in _vive if len(_s) < 3 or _s[2] == "uff"] or [_s[1] for _s in _vive] or [_s[1] for _s in c["sources"] if _s[1] not in LINK_ROTTI]
            if _alt: _p["official"] = _alt[0]; _p["ownSite"] = False
        # 10/11 21:48: il tasto Biglietti delle card non apre mai la scheda e basta: senza biglietteria ne' partner porta alla
        # pagina delle tariffe del gestore (o del portale ufficiale), come il bottone della scheda.
        if _p.get("free") is not True and not _p.get("ticketUrl") and not _p.get("tq") and _p.get("official"): _p["tf"] = _p["official"]
        _d = {k: _p.pop(k) for k in PESANTI if k in _p}
        for k in VIA: _p.pop(k, None)
        if not _p.get("ticketUrl"): _p.pop("ticketUrl", None)
        for k in ("address", "price", "duration"):
            if k in _p: _d[k] = _p.pop(k)
        if _d: _det.setdefault(_c["prov"], {}).setdefault(_c["slug"], {}).setdefault(_p["id"], {}).update(_d)
CK = ["storia", "musei", "sacro", "natura", "locale"]
for _c in _leggeri:
    for k in ("scarti", "copertura", "minimo", "inv"): _c.pop(k, None)
    _pl = []
    for _p in _c["places"]:
        f = ("F" if _p.get("free") is True else "P" if _p.get("free") is False else "") + ("c" if _p.get("card") else "") + ("u" if _p.get("unesco") else "") + ("v" if _p.get("view") else "") + ("i" if _p.get("indoor") else "")
        a = [_p["id"][len(_c["slug"]) + 2:], _p["name"], CK.index(_p["cat"]), _p["sub"], _p.get("desc", ""), f, "" if _p.get("status", "ok") == "ok" else _p["status"], _p.get("t", ""), _p.get("r", 0)]
        extra = {k: v for k, v in _p.items() if k not in ("id", "name", "cat", "sub", "desc", "free", "card", "unesco", "view", "indoor", "status", "t", "r")}
        if extra: a.append(extra)
        _pl.append(a)
    _c["places"] = _pl
# ---- 8/11/2026 tecniche osterie: dizionari per valori ripetuti e id ricavabili dal nome ----
import unicodedata as _ud
def _slug40(s):
    s = "".join(ch for ch in _ud.normalize("NFD", s) if not _ud.combining(ch)).lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:40].rstrip("-")
_ORIG = copy.deepcopy(_leggeri)
_DZ = {"sub": [], "t": [], "regione": [], "provName": [], "provKind": [], "verified": []}
def _dz(k, v):
    L = _DZ[k]
    if v not in L: L.append(v)
    return L.index(v)
for _c in _leggeri:
    for k in ("regione", "provName", "provKind", "verified"): _c[k] = _dz(k, _c[k])
    for a in _c["places"]:
        if a[0] == _slug40(a[1]): a[0] = 0
        a[3] = _dz("sub", a[3]); a[7] = _dz("t", a[7])
DECODE = r"""function DECODIFICA(D){const Z=D.dz,sl=s=>(/[^\x00-\x7f]/.test(s)?s.normalize("NFD").replace(/[\u0300-\u036f]/g,""):s).toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,40).replace(/-+$/,"");
  for(const c of D.c){for(const k of ["regione","provName","provKind","verified"])c[k]=Z[k][c[k]];for(const a of c.places){if(a[0]===0)a[0]=sl(a[1]);a[3]=Z.sub[a[3]];a[7]=Z.t[a[7]];}}return D;}"""
import subprocess as _sp, tempfile as _tf
with _tf.NamedTemporaryFile("w", suffix=".js", delete=False) as _f:
    _f.write(DECODE + "\nconst fs=require('fs');const D=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify(DECODIFICA(D).c));")
_dec = json.loads(_sp.run(["node", _f.name], input=json.dumps(dict(c=_leggeri, dz=_DZ), ensure_ascii=False), capture_output=True, text=True, check=True).stdout)
assert _dec == _ORIG, "DECODIFICA non restituisce i dati originali"
def _scrivi(pref, obj):
    t = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
    n = f"{pref}.{hashlib.sha256(t.encode('utf-8')).hexdigest()[:10]}.json"
    open(os.path.join(HERE, n), "w", encoding="utf-8").write(t); return n
for _old in glob.glob(os.path.join(HERE, "dati.*.json")) + glob.glob(os.path.join(HERE, "det.*.json")) + glob.glob(os.path.join(HERE, "meta.*.json")) + glob.glob(os.path.join(HERE, "fonti.*.json")): os.remove(_old)
def _bonus(x):
    b = (12 if x.get("autonomo") else 0) + {2: 15, 1: 8}.get(x.get("tci", 0), 0) + (6 if x.get("dnp") else 0) + (18 if x.get("unesco_nome") else 0) + min(12, x.get("natura", 0))
    if x.get("visitatori"): b += min(20, max(0, round(4 * math.log10(max(1, x["visitatori"])) - 12)))
    if x.get("fai"): b += max(1, 6 - x["fai"] // 20)
    return b
PB = {k.split("|", 1)[1]: _bonus(v) for k, v in PUNTI.items() if k.startswith("bologna-bo|")}
# 9/11/2026 indice per colonne (tecnica A3 della guida osterie): una lista per campo, comuni e luoghi; compresso ~14% più piccolo.
_ck = {}
for _c in _leggeri:
    for k in _c:
        if k != "places" and k not in _ck: _ck[k] = None
_K = dict(n=[len(c["places"]) for c in _leggeri], ck={k: [c.get(k) for c in _leggeri] for k in _ck},
          cm={k: [i for i, c in enumerate(_leggeri) if k not in c] for k in _ck}, p=[[a[q] for c in _leggeri for a in c["places"]] for q in range(9)], x={})
_K["cm"] = {k: v for k, v in _K["cm"].items() if v}
_g = 0
for _c in _leggeri:
    for a in _c["places"]:
        if len(a) > 9: _K["x"][str(_g)] = a[9]
        _g += 1
import sys as _sys; _sys.path.insert(0, HERE); from leggi_dati import righe as _righe
assert _righe(json.loads(json.dumps(dict(k=_K))))["c"] == json.loads(json.dumps(_leggeri)), "colonne: la decodifica Python non restituisce i dati"
COLONNE = r"""function COLONNE(D){if(!D.k)return D;const K=D.k,C=[],ks=Object.keys(K.ck);let g=0;
  for(let i=0;i<K.n.length;i++){const c={};for(const k of ks){const m=K.cm[k];if(m&&m.includes(i))continue;c[k]=K.ck[k][i];}
    const pl=new Array(K.n[i]);for(let j=0;j<K.n[i];j++,g++){const a=[K.p[0][g],K.p[1][g],K.p[2][g],K.p[3][g],K.p[4][g],K.p[5][g],K.p[6][g],K.p[7][g],K.p[8][g]];const x=K.x[g];if(x)a.push(x);pl[j]=a;}
    c.places=pl;C.push(c);}D.c=C;D.k=undefined;return D;}"""
with _tf.NamedTemporaryFile("w", suffix=".js", delete=False) as _f:
    _f.write(COLONNE + "\nconst fs=require('fs');process.stdout.write(JSON.stringify(COLONNE(JSON.parse(fs.readFileSync(0,'utf8'))).c));")
assert json.loads(_sp.run(["node", _f.name], input=json.dumps(dict(k=_K), ensure_ascii=False), capture_output=True, text=True, check=True).stdout) == json.loads(json.dumps(_leggeri)), "colonne: la decodifica JS non restituisce i dati"
# 10/11/2026 classifica calcolata qui e non nel browser: punteggio dei luoghi di Bologna (stesse regole della pagina) e posizione
# di ogni luogo nell'ordine [luoghi di Bologna..., luoghi degli altri comuni...]; stesso confronto dei nomi (Intl.Collator "it").
_RKJS = open(os.path.join(D, "places-bologna.js"), encoding="utf-8").read() + r"""
;const fs=require('fs');const I=JSON.parse(fs.readFileSync(0,'utf8'));const PB=I.pb;
const sc=p=>{let s=0;const u=(p.sources||[]).map(x=>x[1]||"").join(" ");if(p.unesco)s+=12;if(u.includes("touringclub.it"))s+=6;if(u.includes("italia.it"))s+=8;
  s+=Math.min(2,Math.max(0,(p.sources||[]).length-1))*2;if(p.status==="closed")s-=10;return Math.max(0,s+(PB[p.id]||0));};
const rb=PLACES.map(p=>p.r==null?sc(p):p.r);const T=PLACES.map((p,i)=>[rb[i],p.name]).concat(I.x);
const ix=T.map((_,i)=>i);const CO=new Intl.Collator("it");ix.sort((a,b)=>T[b][0]-T[a][0]||CO.compare(T[a][1],T[b][1]));
const rk=new Array(T.length);ix.forEach((g,i)=>rk[g]=i+1);process.stdout.write(JSON.stringify({rb,rk}));"""
with _tf.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as _f: _f.write(_RKJS)
_RK = json.loads(_sp.run(["node", _f.name], input=json.dumps(dict(pb=PB, x=[[a[8], a[1]] for c in _leggeri for a in c["places"]]), ensure_ascii=False), capture_output=True, text=True, check=True).stdout)
print("classifica pronta:", len(_RK["rk"]), "luoghi")
NOME_DATI = _scrivi("dati", dict(rk=_RK["rk"], rb=_RK["rb"], pb=PB, g=list(geo_of("Bologna")), k=_K, l=LINKS["bologna"], dz=_DZ, tb={k: v for k, v in TQ.items() if "--" not in k}, gb={k: v for k, v in GY.items() if "--" not in k}))
NOME_META = _scrivi("meta", dict(q=qc, s=sources, a=ARCH))
NOME_FONTI = _scrivi("fonti", FONTI)
DET = {pr: _scrivi("det." + pr.lower(), d) for pr, d in sorted(_det.items())}
# 9/11/2026 indice delle parole per la ricerca (stesso risultato di «ogni parola cercata è contenuta nel testo del luogo»):
# vocabolario delle parole (separate da spazi) di nome, descrizione e indirizzo, già ripiegate come nella pagina; per ogni parola
# l'elenco dei luoghi (posizione in [luoghi di Bologna..., luoghi degli altri comuni...]) a differenze, numeri a lunghezza variabile.
# Tipo, comune e categoria si confrontano nella pagina (pochi valori).
CERCA_JS = r"""const fs=require('fs');const inp=JSON.parse(fs.readFileSync(0,'utf8'));
const src=fs.readFileSync(inp.bo,'utf8').replace('const PLACES','globalThis.PLACES');eval(src);
const fold=s=>s.toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g,"");
const L=PLACES.map(p=>[p.id,p.name,p.desc||"",p.address||""]).concat(inp.extra);const post=new Map();
L.forEach((r,i)=>{for(const w of new Set(fold(r[1]+" "+r[2]+" "+r[3]).split(/\s+/))){if(!w)continue;let a=post.get(w);if(!a)post.set(w,a=[]);a.push(i);}});
const A="0123456789abcdefghijklmnopqrstuv",T="ABCDEFGHIJKLMNOPQRSTUVWXYZ!#$%&*";
const enc=n=>{const d=[];do{d.unshift(n%32);n=Math.floor(n/32);}while(n);return d.slice(0,-1).map(x=>A[x]).join("")+T[d[d.length-1]];};
const v=[...post.keys()].sort(),p=v.map(w=>{let pr=-1,o="";for(const x of post.get(w)){o+=enc(x-pr-1);pr=x;}return o;});
process.stdout.write(JSON.stringify({n:L.length,ids:L.length?[L[0][0],L[L.length-1][0]]:[],v,p}));"""
with _tf.NamedTemporaryFile("w", suffix=".js", delete=False) as _f: _f.write(CERCA_JS)
_cerca = _sp.run(["node", _f.name], input=json.dumps(dict(bo=os.path.join(D, "places-bologna.js"), extra=[[p["id"], p["name"], p.get("desc", ""), p.get("address", "")] for c in comuni for p in c["places"]]), ensure_ascii=False), capture_output=True, text=True, check=True).stdout
for _old in glob.glob(os.path.join(HERE, "cerca.*.json")): os.remove(_old)
NOME_CERCA = _scrivi("cerca", json.loads(_cerca))
_senza = [dict(id=_p["id"], r=_p.get("r", 0), c=c["name"], pr=c["prov"], n=_p["name"], cat=_p["cat"], sub=_p["sub"], free=_p["free"], price=_p.get("price", ""), off=_p.get("official", ""), src=[x[1] for x in _p["sources"]], tq=bool(_p.get("tq")), gy=bool(_p.get("gy"))) for c in comuni for _p in c["places"] if _p["free"] is not True and not _p.get("ticketUrl") and not _p.get("tq")]
json.dump(_senza, open("/tmp/senza_biglietto.json", "w"), ensure_ascii=False); print("senza link al biglietto:", len(_senza), "(da verificare", sum(1 for x in _senza if x["free"] is None), ")")
json.dump(AUTO, open("/tmp/link_auto.json", "w"), ensure_ascii=False); print("link dalle fonti: biglietti", len(AUTO["tk"]), "orari", len(AUTO["hr"]))
json.dump(dict(v=2, dati=NOME_DATI, meta=NOME_META, fonti=NOME_FONTI, det=DET, cerca=NOME_CERCA), open(os.path.join(HERE, "manifest.json"), "w"))
LOADER = r"""
/* 9/11/2026 Tiqets (Awin, publisher 3146807 come Events): mid a 0 = link diretto alla pagina del prodotto; con l'ID inserzionista il clic passa da Awin */
var AFF={awin:"3146807",mid:{"tiqets.com":12427},par:{"getyourguide":"partner_id=Y9VWGXI&utm_medium=online_publisher"},ord:["tq","gy"],nome:{tq:"Tiqets",gy:"GetYourGuide"}};
/* tasto Biglietti: prima il venditore affiliato che paga di più (AFF.ord), poi la biglietteria ufficiale */
function tkUrl(p){for(const k of AFF.ord)if(p[k]&&(k!=="gy"||/biglietto|ingresso|salta|ticket/.test(p[k])))return [p[k],AFF.nome[k]];return p.ticketUrl?[p.ticketUrl,""]:null}
function affUrl(u){try{const h=new URL(u).hostname.replace(/^www\./,"");for(const d in AFF.mid){if(AFF.awin&&AFF.mid[d]&&(h===d||h.endsWith("."+d)))return "https://www.awin1.com/cread.php?awinmid="+AFF.mid[d]+"&awinaffid="+AFF.awin+"&ued="+encodeURIComponent(u)}for(const d in AFF.par){if(h.split(".").includes(d)&&!/[?&]partner_id=/.test(u))return u+(u.includes("?")?"&":"?")+AFF.par[d]}}catch(_){}return u}
document.addEventListener("click",e=>{const a=e.target.closest&&e.target.closest("a[href^='https://']");if(a&&!a.dataset.aff){const v=affUrl(a.href);if(v!==a.href){a.dataset.aff=a.href;a.href=v}}},true);
/* ---- caricamento come la guida osterie (7/11/2026): manifest.json (sempre riletto) -> dati.<hash>.json
   conservato nel telefono (IndexedDB) e riscaricato solo quando cambia ---- */
const MEMO={db:null,apri(){if(this.db)return this.db;this.db=new Promise(ok=>{try{const r=indexedDB.open("luoghi",1);
  r.onupgradeneeded=()=>r.result.createObjectStore("file");r.onsuccess=()=>ok(r.result);r.onerror=()=>ok(null);setTimeout(()=>ok(null),1500);}catch(e){ok(null);}});return this.db;},
  async leggi(k){const db=await this.apri();if(!db)return null;return new Promise(ok=>{try{const q=db.transaction("file").objectStore("file").get(k);q.onsuccess=()=>ok(q.result||null);q.onerror=()=>ok(null);}catch(e){ok(null);}});},
  async scrivi(k,v){const db=await this.apri();if(!db)return;try{const s=db.transaction("file","readwrite").objectStore("file");s.put(v,k);const tieni=MAN?[MAN.dati,MAN.meta,MAN.luoghi,MAN.testi,MAN.cerca,MAN.fonti,MAN.foto,...Object.values(MAN.det||{})]:[k];const c=s.getAllKeys();c.onsuccess=()=>c.result.forEach(x=>{if(!tieni.includes(x))s.delete(x);});}catch(e){}}};
let MAN=null;
/* istantanea della prima schermata (8/11/2026): alla riapertura compare subito l'ultima prima schermata salvata;
   un attimo prima che la pagina vera disegni, si rimette il contenuto originale, così il risultato è identico */
const IST_ID=["stats","count","verified","xtra","grid","active"],IST_SUBITO=["count","verified","grid"];
/* 10/11/2026: l'avvio è diviso in pezzi brevi, così il telefono non resta bloccato */
/* 10/11/2026: i file scaricati si decodificano a pezzi man mano che arrivano (niente blocco unico a fine download) */
async function leggiAPezzi(r){if(!r.body||typeof TextDecoder==="undefined")return r.text();const rd=r.body.getReader(),dec=new TextDecoder(),parti=[];for(;;){const {done,value}=await rd.read();if(done)break;parti.push(dec.decode(value,{stream:true}));}parti.push(dec.decode());return parti.join("");}
const PAUSA=()=>new Promise(r=>{if(typeof MessageChannel!=="undefined"){const m=new MessageChannel();m.port1.onmessage=()=>r();m.port2.postMessage(0);}else setTimeout(r,0);});let IST_ORIG=null,IST_TOCCO=0;
["pointerdown","keydown","input"].forEach(ev=>document.addEventListener(ev,()=>{IST_TOCCO=1;},{capture:true,passive:true}));
try{const n=localStorage.getItem("datiNome"),o=!location.hash.slice(1)&&n&&JSON.parse(localStorage.getItem("istG:"+n)||"null");
  if(o){IST_ORIG=IST_ID.map(id=>{const e=document.getElementById(id);return [e.innerHTML,e.hidden];});IST_ID.forEach((id,i)=>{const e=document.getElementById(id);e.innerHTML=o[i][0];e.hidden=o[i][1];});}}catch(e){IST_ORIG=null;}
function salvaIst(nome){setTimeout(()=>{if(IST_TOCCO||location.hash.slice(1))return;try{
  localStorage.setItem("istG:"+nome,JSON.stringify(IST_ID.map(id=>{const e=document.getElementById(id);return [e.innerHTML,e.hidden];})));
  for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k&&k.startsWith("istG:")&&k!=="istG:"+nome)localStorage.removeItem(k);}}catch(e){}},1500);}
(async()=>{const cnt=document.getElementById("count");if(cnt&&!IST_ORIG)cnt.textContent="Caricamento dei luoghi…";
  let nome=null;try{nome=localStorage.getItem("datiNome");}catch(e){}
  const ultimo=nome,pIdb=nome?MEMO.leggi(nome):null;
  const ATTESO="""+json.dumps(NOME_DATI)+r""",pPrimo=nome?null:fetch(ATTESO).then(r=>r.ok?leggiAPezzi(r):null).catch(()=>null);  /* primo accesso: in parallelo al manifest */
  try{MAN=await (await fetch("manifest.json",{cache:"no-store"})).json();nome=MAN.dati;try{localStorage.setItem("man",JSON.stringify(MAN));}catch(e){}}catch(e){try{MAN=JSON.parse(localStorage.getItem("man")||"null");}catch(e2){}}
  if(!nome){if(cnt)cnt.textContent="Dati non disponibili: controlla la connessione.";return;}
  let t=nome===ultimo&&pIdb?await pIdb:(pPrimo&&nome===ATTESO?await pPrimo:null)||await MEMO.leggi(nome);
  if(t&&pPrimo&&nome===ATTESO)MEMO.scrivi(nome,t);
  if(!t){const r=await fetch(nome);if(!r.ok){if(cnt)cnt.textContent="Dati non disponibili ("+r.status+")";return;}t=await leggiAPezzi(r);MEMO.scrivi(nome,t);}
  try{localStorage.setItem("datiNome",nome);}catch(e){}
  const J=JSON.parse(t);await PAUSA();COLONNE(J);await PAUSA();const D=DECODIFICA(J);await PAUSA();
  if(IST_ORIG)IST_ID.forEach((id,i)=>{if(!IST_SUBITO.includes(id))return;const e=document.getElementById(id);e.innerHTML=IST_ORIG[i][0];e.hidden=IST_ORIG[i][1];});
  await AVVIO(D);salvaIst(nome);})();
"""+DECODE+"\n"+COLONNE+r"""
async function AVVIO(D){
{const CK=["storia","musei","sacro","natura","locale"];for(const c of D.c)c.places=c.places.map(a=>{const f=a[5],o={id:c.slug+"--"+a[0],name:a[1],cat:CK[a[2]],sub:a[3],desc:a[4],free:f.includes("F")?true:f.includes("P")?false:null,card:f.includes("c"),unesco:f.includes("u"),view:f.includes("v"),indoor:f.includes("i"),status:a[6]||"ok",t:a[7],r:a[8],address:"",price:"",duration:"",sources:[]};if(a[9])Object.assign(o,a[9]);return o;});
 for(const c of D.c){if(c.lede==null)c.lede="";if(c.notice==null)c.notice="";if(!c.sources)c.sources=[];}}
await PAUSA();
const BO_GEO=D.g,COMUNI_EXTRA=D.c,LINKS_BO=D.l;let QC,SOURCES,ARCH;var RKALL=null;
const caricaMeta=(()=>{let pr=null;return()=>pr||(pr=(async()=>{const n=MAN&&MAN.meta;if(!n)return;let t=await MEMO.leggi(n);if(!t){const r=await fetch(n);if(!r.ok)return;t=await leggiAPezzi(r);MEMO.scrivi(n,t);}const m=JSON.parse(t);QC=m.q;SOURCES=m.s;ARCH=m.a;const h=location.hash.slice(1);if(h==="metodo"||h==="fonti")route(true);})());})();
("requestIdleCallback" in window)?requestIdleCallback(()=>caricaMeta(),{timeout:4000}):setTimeout(()=>caricaMeta(),1500);
for(const p of PLACES){const l=LINKS_BO[p.id];if(l){p.hoursUrl=l.orari||"";p.ticketUrl=l.biglietti||"";if(l.off)p.official=l.off;}}
if(D.tb)for(const p of PLACES)if(D.tb[p.id])p.tq=D.tb[p.id];if(D.gb)for(const p of PLACES)if(D.gb[p.id])p.gy=D.gb[p.id];
{const n=document.getElementById("aff-nota");if(n&&(AFF.awin&&Object.values(AFF.mid).some(Boolean)||Object.keys(AFF.par).length))n.hidden=false;}
/* dettagli della scheda (perché andarci, fonti, link) per provincia: scaricati in sottofondo o al tocco */
const DETOK={},DETP={},IDPROV={};
for(const c of COMUNI_EXTRA)for(const p of c.places)(IDPROV[p.id]||(IDPROV[p.id]=new Set())).add(c.prov);
function caricaDet(pr){if(!pr||DETOK[pr])return Promise.resolve();if(DETP[pr])return DETP[pr];
  const n=MAN&&MAN.det&&MAN.det[pr];if(!n){DETOK[pr]=1;return Promise.resolve();}
  return DETP[pr]=(async()=>{let t=await MEMO.leggi(n);if(!t){const r=await fetch(n);if(!r.ok)return;t=await leggiAPezzi(r);MEMO.scrivi(n,t);}
    const d=JSON.parse(t);for(const c of COMUNI_EXTRA){const dc=c.prov===pr&&d[c.slug];if(dc){if(dc._c)Object.assign(c,dc._c);for(const p of c.places)if(dc[p.id])Object.assign(p,dc[p.id]);}}DETOK[pr]=1;riempiDesc();})();}
/* 9/11/2026: le card già disegnate ricevono la descrizione appena arriva il file della provincia */
let PMAP=null;function riempiDesc(){if(!PMAP){PMAP=new Map();for(const c of COMUNI_EXTRA)for(const p of c.places)if(!PMAP.has(p.id))PMAP.set(p.id,p);}
  document.querySelectorAll("#grid .card[data-pid]").forEach(el=>{const d=el.querySelector(".desc");if(d&&!d.textContent){const p=PMAP.get(el.dataset.pid);if(p&&p.desc)d.textContent=p.desc;}});}
/* 9/11/2026 ricerca con indice delle parole (cerca.<impronta>.json), scaricato in sottofondo; stesso risultato della ricerca sul testo */
const CERCA={ok:false,fail:false,pr:null,V:null,P:null,ids:null,dec:new Map(),memo:new Map()};
function caricaCerca(){if(CERCA.pr)return CERCA.pr;return CERCA.pr=(async()=>{try{const n=MAN&&MAN.cerca;if(!n)throw 0;let t=await MEMO.leggi(n);
  if(!t){const r=await fetch(n);if(!r.ok)throw 0;t=await leggiAPezzi(r);MEMO.scrivi(n,t);}const j=JSON.parse(t);await PAUSA();
  const ids=PLACES.map(p=>p.id);for(const c of COMUNI_EXTRA)for(const p of c.places)ids.push(p.id);
  if(j.n!==ids.length||(ids.length&&(j.ids[0]!==ids[0]||j.ids[1]!==ids[ids.length-1])))throw 0;
  CERCA.V=j.v;CERCA.P=j.p;CERCA.ids=ids;CERCA.ok=true;}catch(e){CERCA.fail=true;}})();}
function cercaPost(i){let a=CERCA.dec.get(i);if(a)return a;a=[];const s=CERCA.P[i];let n=0,pr=-1;
  for(let k=0;k<s.length;k++){const c=s.charCodeAt(k);let v;if(c>=65&&c<=90){v=c-65;}else{const T="!#$%&*".indexOf(s[k]);if(T>=0)v=26+T;else{n=n*32+(c<=57?c-48:c-87);continue;}}
    n=n*32+v;pr=pr+n+1;a.push(pr);n=0;}CERCA.dec.set(i,a);return a;}
function cercaParola(w){let r=CERCA.memo.get(w);if(r)return r;const ids=new Set(),V=CERCA.V;
  for(let i=0;i<V.length;i++)if(V[i].includes(w))for(const x of cercaPost(i))ids.add(CERCA.ids[x]);
  r={ids,f:new Map()};CERCA.memo.set(w,r);return r;}
const CERCAF=new Map();const cf=s=>{let r=CERCAF.get(s);if(r===undefined){r=fold(s);CERCAF.set(s,r);}return r;};
let QOK_Q=null,QOK_W=null;
function QOK(p){if(!CERCA.ok){if(!p._t)p._t=fold(p.name+" "+p.desc+" "+p.sub+" "+p.address+" "+p.com+" "+CATS[p.cat].long);return fold(S.q).split(/\s+/).every(w=>p._t.includes(w));}
  if(QOK_Q!==S.q){QOK_Q=S.q;QOK_W=fold(S.q).split(/\s+/).map(w=>[w,cercaParola(w)]);}
  return QOK_W.every(([w,r])=>r.ids.has(p.id)||cf(p.sub).includes(w)||cf(p.com).includes(w)||cf(CATS[p.cat].long).includes(w));}
const precarica=prs=>{const f=()=>prs.forEach(pr=>caricaDet(pr));("requestIdleCallback" in window)?requestIdleCallback(f,{timeout:2500}):setTimeout(f,400);};
/* 10/11/2026: l'anticipo delle descrizioni di provincia non parte piu' da solo
   all'avvio. Chi apre la guida e legge non scarica 290 KB che non ha chiesto;
   l'anticipo parte al primo gesto (tocco, tasto, rotella, scorrimento). Al
   tocco di una scheda la sua provincia parte comunque, dal gancio pointerdown. */
let GESTO=false,DAANT=[];
const anticipa=prs=>{if(GESTO){precarica(prs);return;}DAANT=prs;};
["pointerdown","keydown","wheel","touchstart"].forEach(ev=>addEventListener(ev,()=>{if(GESTO)return;GESTO=true;if(DAANT.length)precarica(DAANT);},{once:true,passive:true,capture:true}));
/* classifica: punteggio di rilevanza (calcolato in costruzione; per Bologna con le stesse regole) e posizione */
{const sc=p=>{let s=0;const u=(p.sources||[]).map(x=>x[1]||"").join(" ");if(p.unesco)s+=12;if(u.includes("touringclub.it"))s+=6;if(u.includes("italia.it"))s+=8;
  s+=Math.min(2,Math.max(0,(p.sources||[]).length-1))*2;if(p.status==="closed")s-=10;return Math.max(0,s+((D.pb||{})[p.id]||0));};
 const tutti=[...PLACES];for(const c of COMUNI_EXTRA)for(const p of c.places)tutti.push(p);
 if(D.rk&&D.rk.length===tutti.length){PLACES.forEach((p,i)=>{if(p.r==null)p.r=D.rb[i];});RKALL=new Array(tutti.length);tutti.forEach((p,i)=>{p.rk=D.rk[i];RKALL[p.rk-1]=p;});}
 else{PLACES.forEach(p=>{if(p.r==null)p.r=sc(p);});const CO=new Intl.Collator("it");tutti.sort((a,b)=>b.r-a.r||CO.compare(a.name,b.name));tutti.forEach((p,i)=>p.rk=i+1);RKALL=tutti;}}
await PAUSA();
{const _os=openSheet;openSheet=function(id,from){const ps=[...(IDPROV[id]||[])].filter(pr=>!DETOK[pr]),sh=$("sheet");
  sh.dataset.pid=id;sh.classList.toggle("sload",ps.length>0);_os(id,from);if(!ps.length)return;
  Promise.all(ps.map(caricaDet)).then(()=>{if(sh.dataset.pid!==id||!sh.classList.contains("open"))return;const y=sh.scrollTop,f=lastFocus;sh.classList.remove("sload");_os(id,f);sh.scrollTop=y;});};}
/* anticipo al tocco: la provincia della card o del comune toccato si scarica già alla pressione del dito */
document.addEventListener("pointerdown",e=>{try{const t=e.target.closest(".card[data-pid],[data-c],a[href^='#']");if(!t)return;
  if(t.dataset.pid){(IDPROV[t.dataset.pid]||[]).forEach(pr=>caricaDet(pr));return;}
  const sl=t.dataset.c||t.getAttribute("href").slice(1);const c=COMUNI.find(x=>x.slug===sl);if(c)caricaDet(c.prov);}catch(err){}},{capture:true,passive:true});
/* apertura di un comune: la presentazione arriva con il file della provincia */
{const _sc=setComune;setComune=function(){const r=_sc.apply(this,arguments);try{if(!C.all&&!C.isProv&&!C.provs&&C.prov&&!DETOK[C.prov]){const el=$("lede"),cc=C;el.style.visibility="hidden";
  caricaDet(C.prov).then(()=>{if(C===cc)el.textContent=ledeTxt(cc);el.style.visibility="";});}}catch(e){}return r;};}
/* ricerca: se l'indice non è ancora arrivato, lo si aspetta (di solito è già in memoria) */
{const _u2=update;update=function(){if(S.q&&!CERCA.ok&&!CERCA.fail){const n=$("count");if(n)n.textContent="Ricerca in corso…";caricaCerca().then(()=>update());return;}return _u2.apply(this,arguments);};}
document.getElementById("q").addEventListener("focus",()=>caricaCerca(),{once:true});
/* 10/11/2026: l'indice della ricerca (circa 1 MB) non si scarica piu' da solo:
   parte quando si tocca il campo di ricerca (riga sopra) o alla prima parola
   digitata. Chi non cerca non lo scarica. */
{const _up=update;update=function(){const r=_up.apply(this,arguments);try{const ps=[...new Set((CUR||[]).slice(0,60).map(p=>{const c=COMUNI.find(x=>x.slug===p.comSlug);return c&&c.prov;}).filter(Boolean))].slice(0,2);
  if(ps.length){anticipa(ps);try{localStorage.setItem("ultProv",ps[0]);}catch(e){}}}catch(e){}return r;};}
try{const u=localStorage.getItem("ultProv");if(u)anticipa([u]);}catch(e){}
"""
t = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
t = t.replace("/*CAPI*/", ",".join(json.dumps(x, ensure_ascii=False) for x in sorted(set(sum(check.CAPOLUOGHI.values(), [])))))
_i = t.index("/*PLACES*/"); _j = t.rindex("</script>")
t = t[:_i] + bologna_places + "\n" + LOADER + t[_i + len("/*PLACES*/"):_j] + "\n}\n" + t[_j:]
# 9/11/2026 il file dei dati parte subito, in testa alla pagina, mentre il resto della pagina arriva (fetch lo riprende dalla memoria)
# (solo se nel telefono non c'è già: alla seconda visita i dati si leggono da IndexedDB)
t = t.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<script>try{if(localStorage.getItem("datiNome")!==' + json.dumps(NOME_DATI) + '){var l=document.createElement("link");l.rel="preload";l.as="fetch";l.crossOrigin="anonymous";l.href=' + json.dumps(NOME_DATI) + ';document.head.appendChild(l);}}catch(e){}</script>', 1)
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(t)
print(len(comuni), "comuni extra,", sum(len(c["places"]) for c in comuni), "luoghi extra,", len(sources), "fonti; index", os.path.getsize(os.path.join(HERE, "index.html")), "byte; dati", os.path.getsize(os.path.join(HERE, NOME_DATI)), "byte")
