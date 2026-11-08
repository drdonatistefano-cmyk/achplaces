"""Controllo di qualità e coerenza, uguale per tutte le province.

Si esegue dentro build.py. Gli errori (E) bloccano la pubblicazione; gli avvisi (W)
finiscono nella tabella di copertura del Metodo e nella lista di lavoro.
"""
import csv, os, re, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
TPL = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()

def _cats():
    m = re.search(r"const CATS=\{(.*?)\n\};", TPL, re.S)
    out = {}
    for cat, body in re.findall(r"\n\s*(\w+):\{label:.*?subs:\{(.*?)\}\}", m.group(1)):
        out[cat] = set(re.findall(r'"([^"]+)":', body))
    return out
CATS = _cats()
AW_OK = {"borghi", "arancione", "unesco", "creative"}
DEFAULT_HOURS = ("Verifica sul sito ufficiale", "Spazio aperto")

# Regole anti-scarsità (protocollo v2, 7 novembre 2026): sotto questi minimi il build si ferma.
CAPOLUOGHI = {"SI": ["Siena"], "BO": ["Bologna"], "FC": ["Forlì", "Cesena"], "RN": ["Rimini"], "RA": ["Ravenna"], "FE": ["Ferrara"],
              "FI": ["Firenze"], "MO": ["Modena"], "RE": ["Reggio Emilia"], "PR": ["Parma"], "PC": ["Piacenza"]}
import json as _j, os as _o
for _k,_v in _j.load(open(_o.path.join(_o.path.dirname(_o.path.abspath(__file__)),"data","province.json"),encoding="utf-8")).items(): CAPOLUOGHI[_k]=_v["capo"]
MIN_CAPO = 25        # capoluogo di provincia o città metropolitana
MIN_UNESCO = 3       # comune con un sito UNESCO o una sua parte (non capoluogo)
MIN_AW = 3           # comune Borgo più bello o Bandiera Arancione
MIN_ALTRI = 1        # ogni altro comune presente nella guida

def _fold(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9 ]", " ", "".join(c for c in s if unicodedata.category(c) != "Mn"))

def inv_found(item, names):
    """Un elemento dell'inventario è coperto se le sue parole principali compaiono nel nome di una scheda."""
    words = [w for w in _fold(item).split() if len(w) > 3 and w not in ("chiesa", "museo", "palazzo", "piazza", "della", "delle", "degli", "dello", "basilica", "castello", "parco", "teatro", "santa", "santo", "torre")]
    if not words: words = _fold(item).split()
    return any(all(w in _fold(n) for w in words) for n in names)

def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))

def official_list():
    rows = {}
    for r in csv.DictReader(open(os.path.join(HERE, "data", "geo", "comuni_istat.csv"), encoding="utf-8")):
        rows.setdefault(r["sigla"], []).append(r["comune"])
    return rows

import json, datetime
# Inventario nazionale MiC dei luoghi della cultura (open data): base minima di completezza per ogni comune
NONTUR = re.compile(r"\b(biblioteca|archivio|istituto|direzione generale|comando|fototeca|centro per il libro|iccu|segretariato|soprintendenza)\b", re.I)
MIC = {}
for _r in csv.DictReader(open(os.path.join(HERE, "data", "archivio", "raw-mic-luoghi.csv"), encoding="utf-8")):
    MIC.setdefault((_fold(_r["Comune"]).strip(), _fold(_r["Provincia"]).strip()), []).append((_r["Identifier"], _r["Nome_Istituzionale"]))
def mic_items(comune, provname):
    k = _fold(comune).strip()
    out = MIC.get((k, _fold(provname).strip()))
    if out is None:
        out = [x for (cc, pp), v in MIC.items() if cc == k for x in v]
    return [(i, n) for i, n in out if not NONTUR.search(n)]
MIC_REPORT = {}
_STOP = set("museo musei civico civica civici nazionale archeologico archeologica area resti della delle degli dello dell del dei chiesa palazzo piazza basilica castello parco teatro santa santo torre centro casa villa galleria collezione raccolta anfiteatro complesso monumentale storico storica",)
_STOP = set("museo musei civico civica civici nazionale archeologico archeologica area resti della delle degli dello dell del dei chiesa palazzo piazza basilica castello parco teatro santa santo torre centro casa villa galleria collezione raccolta anfiteatro complesso monumentale storico storica arte fondazione culture cultura contemporanea contemporaneo contemporanei moderna moderno raccolte raccolta laboratorio storia universita dipartimento sezione permanente nazionale regionale civiche civico".split())
def mic_found(item, names, city=""):
    w = {x for x in _fold(item).split() if len(x) > 2 and x not in _STOP and x not in _fold(city).split()}
    if not w: return inv_found(item, names)
    for n in names:
        nw = set(_fold(n).split())
        com = w & nw
        if com and (len(com) / len(w) >= 0.5) and any(len(x) >= 4 for x in com): return True
        if any(len(x) >= 7 for x in com): return True
    return False
REG = json.load(open(os.path.join(HERE, "data", "registri.json"), encoding="utf-8"))
TODAY = datetime.date.today().strftime("%Y-%m")

def run(comuni, prov_names, extra_counts=None, extra_comuni=None):
    """comuni: lista dei comuni costruiti da build.py. extra_counts: {sigla: n luoghi fuori dagli spec} (Bologna città)."""
    errs, warns = [], []
    ids = {}
    off = official_list()
    stats = {}
    for c in comuni:
        P = c["prov"]
        st = stats.setdefault(P, dict(prov=P, name=prov_names[P][0], kind=prov_names[P][1], comuni=set(), places=0, paid=0,
                                      paid_ok=0, unk=0, official=0, hours=0, exact=0, warn=0, closed=0, aw=0))
        st["comuni"].add(norm(c["name"]))
        where = f'{c["name"]} ({P})'
        if not re.fullmatch(r"\d{6}", c.get("istat", "")): errs.append(f"{where}: codice ISTAT mancante o non valido")
        if c.get("lat") is None: errs.append(f"{where}: coordinate del comune mancanti (filtro Vicino a te)")
        for a in c.get("aw", []):
            if a not in AW_OK: errs.append(f"{where}: riconoscimento sconosciuto '{a}'")
        if c.get("aw"): st["aw"] += 1
        has_u = False
        if re.search(r"€\s?\d|\d\s?euro", c.get("lede", "") + " " + c.get("notice", ""), re.I): warns.append(f"{c['name']} ({c['prov']}): presentazione o avviso con un prezzo, che invecchia")
        for p in c["places"]:
            st["places"] += 1
            w = f'{where} · {p["name"]}'
            if p["id"] in ids: errs.append(f"{w}: identificativo duplicato")
            ids[p["id"]] = 1
            if p["cat"] not in CATS: errs.append(f"{w}: categoria '{p['cat']}' non valida")
            elif p["sub"] not in CATS[p["cat"]]: errs.append(f"{w}: sottocategoria '{p['sub']}' non prevista per {p['cat']}")
            for k in ("desc", "why", "address"):
                if not p.get(k): errs.append(f"{w}: campo '{k}' vuoto")
            if len(p.get("desc", "")) < 60: warns.append(f"{w}: descrizione molto breve")
            if re.search(r"€\s?\d|\d\s?euro", p.get("desc", "") + " " + p.get("why", "") + " " + p.get("statusNote", ""), re.I): warns.append(f"{w}: il testo contiene un prezzo, che invecchia: togliere e rimandare al sito del gestore")
            srcs = p.get("sources", [])
            if not any(s[2] == "uff" for s in srcs): errs.append(f"{w}: nessuna fonte ufficiale 🟢")
            else: st["official"] += 1
            for s in srcs:
                if not s[1].startswith("https://"): errs.append(f"{w}: link fonte non https ({s[1][:40]})")
            if p["free"] is None:
                st["unk"] += 1
            elif p["free"] is False:
                st["paid"] += 1
            if p["free"] is False or (p["free"] is None and p.get("indoor") and p.get("cat") != "sacro"):
                if p.get("ticketUrl", "x") and p.get("hoursUrl", "x"): st["paid_ok"] += 1
                else: warns.append(f"{w}: mancano i link precisi a " + " e ".join(x for x, k in (("biglietti", "ticketUrl"), ("orari", "hoursUrl")) if not p.get(k, "x")))
            for k in ("ticketUrl", "hoursUrl"):
                if p.get(k) and not p[k].startswith("https://"): errs.append(f"{w}: link {k} non https")
            if p.get("lat") is not None: st["exact"] += 1
            if p["status"] != "ok":
                rv = p.get("rev", "")
                if not re.fullmatch(r"\d{4}-\d{2}", rv): errs.append(f"{w}: chiusura o avviso senza data di ricontrollo (rev=AAAA-MM)")
                elif rv < TODAY: errs.append(f"{w}: data di ricontrollo {rv} scaduta: verifica se ha riaperto")
            if p["status"] == "closed":
                st["closed"] += 1
                if not p.get("statusNote"): errs.append(f"{w}: chiuso senza spiegazione")
            if p["status"] == "warn":
                st["warn"] += 1
                if not p.get("statusNote"): errs.append(f"{w}: avviso senza spiegazione")
            if p.get("unesco"): has_u = True
        # minimi di copertura
        n_here = len(c["places"]) + ((extra_counts or {}).get(P, 0) if c["name"] in (extra_comuni or {}).get(P, []) else 0)
        capo = c["name"] in CAPOLUOGHI.get(P, [])
        need = MIN_CAPO if capo else MIN_UNESCO if "unesco" in c.get("aw", []) else MIN_AW if set(c.get("aw", [])) & {"borghi", "arancione"} else MIN_ALTRI
        if c.get("minimo"):
            _mn, _mm = c["minimo"]
            if not _mm or c.get("copertura") != "completa":
                errs.append(f"{where}: 'minimo:' ammesso solo con motivo e con copertura MiC completa")
            elif _mn < need:
                warns.append(f"{where}: minimo ridotto a {_mn} ({_mm})"); need = _mn
        if n_here < need:
            errs.append(f"{where}: {n_here} luoghi, il minimo per questo comune è {need}")
        # inventario ufficiale: ogni voce deve avere una scheda o uno scarto motivato
        names = [p["name"] for p in c["places"]] + list(c.get("scarti", {}).keys())
        for items, u in c.get("inv", []):
            for it in items:
                if not inv_found(it, names):
                    errs.append(f"{where}: '{it}' è nell'inventario ufficiale ma non ha scheda né scarto motivato")
        # completezza MiC: ogni luogo della cultura censito dal Ministero nel comune va coperto da una scheda o da uno scarto motivato
        micl = mic_items(c["name"], c["provName"]) if "provName" in c else mic_items(c["name"], "")
        if micl:
            ids_here = {i for p in c["places"] for i in p.get("mic", [])}
            sc = c.get("scarti", {})
            miss = [(i, n) for i, n in micl if i not in ids_here and i not in sc and n not in sc and not any(k.split()[0] == i for k in sc if k) and not mic_found(n, names, c["name"])]
            MIC_REPORT[where] = dict(tot=len(micl), coperti=len(micl) - len(miss), mancanti=[f"{i} | {n}" for i, n in miss])
            if miss:
                msg = f"{where}: {len(miss)} di {len(micl)} luoghi della cultura MiC senza scheda né scarto (es. {', '.join(n for _, n in miss[:3])})"
                (errs if c.get("copertura") == "completa" else warns).append(msg)
        if capo and not any(p["sub"] == "Mercati storici" for p in c["places"]) and "mercati" not in c.get("scarti", {}) and P != "BO":
            errs.append(f"{where}: capoluogo senza mercato storico verificato (scheda 'Mercati storici' o 'scarto: mercati | motivo')")
        if capo and not c.get("inv") and P != "BO":
            warns.append(f"{where}: capoluogo senza inventario ufficiale (righe inv:)")
        if has_u and "unesco" not in c.get("aw", []) and P != "BO":
            warns.append(f"{where}: un luogo è UNESCO ma il comune non ha il riconoscimento")
    # registri ufficiali: i bollini devono coincidere con gli elenchi degli enti
    for aw in ("borghi", "arancione"):
        for regione, r in REG.get(aw, {}).items():
            off_set = set(r["comuni"])
            have = {c["name"] for c in comuni if c["regione"] == regione and aw in c.get("aw", [])}
            present = {c["name"] for c in comuni if c["regione"] == regione}
            for n in sorted(have - off_set): errs.append(f"{n}: bollino '{aw}' non presente nel registro ufficiale ({r['src']})")
            for n in sorted((off_set - have) & present): errs.append(f"{n}: è nel registro ufficiale '{aw}' ma manca il bollino")
            for n in sorted(off_set - present): warns.append(f"{n}: comune del registro '{aw}' non ancora nella guida")
    for P, names in (extra_comuni or {}).items():
        if P in stats: stats[P]["comuni"].update(norm(x) for x in names)
    table = []
    for P, st in stats.items():
        tot = off.get(P, [])
        present = st["comuni"]
        missing = [n for n in tot if norm(n) not in present]
        n = st["places"] + (extra_counts or {}).get(P, 0)
        row = dict(prov=P, name=st["name"], kind=st["kind"], comuni=len(present), comuniTot=len(tot), places=n,
                   official=round(100 * st["official"] / max(1, st["places"])),
                   paidOk=round(100 * st["paid_ok"] / max(1, st["paid"] + st["unk"])) if (st["paid"] + st["unk"]) else 100,
                   unk=st["unk"], hours=round(100 * st["hours"] / max(1, st["places"])),
                   avvisi=st["warn"] + st["closed"], missing=missing)
        table.append(row)
        if len(present) < len(tot):
            warns.append(f"{st['name']} ({P}): {len(tot)-len(present)} comuni ancora senza schede")
    json.dump(MIC_REPORT, open(os.path.join(HERE, "data", "copertura-mic.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return errs, warns, table
