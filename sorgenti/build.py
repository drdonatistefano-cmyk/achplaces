#!/usr/bin/env python3
"""Costruisce index.html: legge i file data/spec-*.txt (formato a righe) e data/places-bologna.js,
produce i blocchi JS COMUNI e SOURCES e li inserisce nel template al posto di /*PLACES*/."""
import json, re, os
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
FUS={"barberinotavarnelle":["barberinovaldelsa","tavarnellevaldipesa"],"rivadelpo":["berra","ro"],"tresignana":["formignana","tresigallo"]}
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
            if p["ticketUrl"] or p["hoursUrl"]: p["ownSite"] = True
            for k in ("hoursUrl", "ticketUrl"):
                if p[k] and not any(x[1] == p[k] for x in p["sources"]): p["sources"].append([("Orari ufficiali" if k == "hoursUrl" else "Biglietti ufficiali") + " (pagina del gestore)", p[k], "uff"])
            if extra.get("mic"): p["mic"] = extra["mic"].split()
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
PESANTI = ("why", "access", "official", "ownSite", "sources", "tip", "statusNote", "hoursUrl")   # ticketUrl resta nell'indice: tasto Ticket nelle card (8/11)
VIA = ("hours", "booking", "rev", "mic")          # non usati dalla pagina
_leggeri = copy.deepcopy(comuni); _det = {}
for _c in _leggeri:
    for _p in _c["places"]:
        _d = {k: _p.pop(k) for k in PESANTI if k in _p}
        for k in VIA: _p.pop(k, None)
        if not _p.get("ticketUrl"): _p.pop("ticketUrl", None)
        for k in ("address", "price", "duration"):
            if k in _p: _d[k] = _p.pop(k)
        if _d: _det.setdefault(_c["prov"], {}).setdefault(_c["slug"], {})[_p["id"]] = _d
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
DECODE = r"""function DECODIFICA(D){const Z=D.dz,sl=s=>s.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[^a-z0-9]+/g,"-").replace(/^-+|-+$/g,"").slice(0,40).replace(/-+$/,"");
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
for _old in glob.glob(os.path.join(HERE, "dati.*.json")) + glob.glob(os.path.join(HERE, "det.*.json")) + glob.glob(os.path.join(HERE, "meta.*.json")): os.remove(_old)
def _bonus(x):
    b = (12 if x.get("autonomo") else 0) + {2: 15, 1: 8}.get(x.get("tci", 0), 0) + (6 if x.get("dnp") else 0) + (18 if x.get("unesco_nome") else 0) + min(12, x.get("natura", 0))
    if x.get("visitatori"): b += min(20, max(0, round(4 * math.log10(max(1, x["visitatori"])) - 12)))
    if x.get("fai"): b += max(1, 6 - x["fai"] // 20)
    return b
PB = {k.split("|", 1)[1]: _bonus(v) for k, v in PUNTI.items() if k.startswith("bologna-bo|")}
NOME_DATI = _scrivi("dati", dict(pb=PB, g=list(geo_of("Bologna")), c=_leggeri, l=LINKS["bologna"], dz=_DZ))
NOME_META = _scrivi("meta", dict(q=qc, s=sources, a=ARCH))
DET = {pr: _scrivi("det." + pr.lower(), d) for pr, d in sorted(_det.items())}
json.dump(dict(v=2, dati=NOME_DATI, meta=NOME_META, det=DET), open(os.path.join(HERE, "manifest.json"), "w"))
LOADER = r"""
/* ---- caricamento come la guida osterie (7/11/2026): manifest.json (sempre riletto) -> dati.<hash>.json
   conservato nel telefono (IndexedDB) e riscaricato solo quando cambia ---- */
const MEMO={db:null,apri(){if(this.db)return this.db;this.db=new Promise(ok=>{try{const r=indexedDB.open("luoghi",1);
  r.onupgradeneeded=()=>r.result.createObjectStore("file");r.onsuccess=()=>ok(r.result);r.onerror=()=>ok(null);setTimeout(()=>ok(null),1500);}catch(e){ok(null);}});return this.db;},
  async leggi(k){const db=await this.apri();if(!db)return null;return new Promise(ok=>{try{const q=db.transaction("file").objectStore("file").get(k);q.onsuccess=()=>ok(q.result||null);q.onerror=()=>ok(null);}catch(e){ok(null);}});},
  async scrivi(k,v){const db=await this.apri();if(!db)return;try{const s=db.transaction("file","readwrite").objectStore("file");s.put(v,k);const tieni=MAN?[MAN.dati,MAN.meta,MAN.luoghi,MAN.testi,...Object.values(MAN.det||{})]:[k];const c=s.getAllKeys();c.onsuccess=()=>c.result.forEach(x=>{if(!tieni.includes(x))s.delete(x);});}catch(e){}}};
let MAN=null;
/* istantanea della prima schermata (8/11/2026): alla riapertura compare subito l'ultima prima schermata salvata;
   un attimo prima che la pagina vera disegni, si rimette il contenuto originale, così il risultato è identico */
const IST_ID=["stats","count","verified","xtra","grid","active"];let IST_ORIG=null,IST_TOCCO=0;
["pointerdown","keydown","input"].forEach(ev=>document.addEventListener(ev,()=>{IST_TOCCO=1;},{capture:true,passive:true}));
try{const n=localStorage.getItem("datiNome"),o=!location.hash.slice(1)&&n&&JSON.parse(localStorage.getItem("istG:"+n)||"null");
  if(o){IST_ORIG=IST_ID.map(id=>{const e=document.getElementById(id);return [e.innerHTML,e.hidden];});IST_ID.forEach((id,i)=>{const e=document.getElementById(id);e.innerHTML=o[i][0];e.hidden=o[i][1];});}}catch(e){IST_ORIG=null;}
function salvaIst(nome){setTimeout(()=>{if(IST_TOCCO||location.hash.slice(1))return;try{
  localStorage.setItem("istG:"+nome,JSON.stringify(IST_ID.map(id=>{const e=document.getElementById(id);return [e.innerHTML,e.hidden];})));
  for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k&&k.startsWith("istG:")&&k!=="istG:"+nome)localStorage.removeItem(k);}}catch(e){}},1500);}
(async()=>{const cnt=document.getElementById("count");if(cnt&&!IST_ORIG)cnt.textContent="Caricamento dei luoghi…";
  let nome=null;try{nome=localStorage.getItem("datiNome");}catch(e){}
  const ultimo=nome,pIdb=nome?MEMO.leggi(nome):null;
  const ATTESO="""+json.dumps(NOME_DATI)+r""",pPrimo=nome?null:fetch(ATTESO).then(r=>r.ok?r.text():null).catch(()=>null);  /* primo accesso: in parallelo al manifest */
  try{MAN=await (await fetch("manifest.json",{cache:"no-store"})).json();nome=MAN.dati;try{localStorage.setItem("man",JSON.stringify(MAN));}catch(e){}}catch(e){try{MAN=JSON.parse(localStorage.getItem("man")||"null");}catch(e2){}}
  if(!nome){if(cnt)cnt.textContent="Dati non disponibili: controlla la connessione.";return;}
  let t=nome===ultimo&&pIdb?await pIdb:(pPrimo&&nome===ATTESO?await pPrimo:null)||await MEMO.leggi(nome);
  if(t&&pPrimo&&nome===ATTESO)MEMO.scrivi(nome,t);
  if(!t){const r=await fetch(nome);if(!r.ok){if(cnt)cnt.textContent="Dati non disponibili ("+r.status+")";return;}t=await r.text();MEMO.scrivi(nome,t);}
  try{localStorage.setItem("datiNome",nome);}catch(e){}
  const D=DECODIFICA(JSON.parse(t));
  if(IST_ORIG)IST_ID.forEach((id,i)=>{const e=document.getElementById(id);e.innerHTML=IST_ORIG[i][0];e.hidden=IST_ORIG[i][1];});
  AVVIO(D);salvaIst(nome);})();
"""+DECODE+r"""
function AVVIO(D){
{const CK=["storia","musei","sacro","natura","locale"];for(const c of D.c)c.places=c.places.map(a=>{const f=a[5],o={id:c.slug+"--"+a[0],name:a[1],cat:CK[a[2]],sub:a[3],desc:a[4],free:f.includes("F")?true:f.includes("P")?false:null,card:f.includes("c"),unesco:f.includes("u"),view:f.includes("v"),indoor:f.includes("i"),status:a[6]||"ok",t:a[7],r:a[8],address:"",price:"",duration:""};if(a[9])Object.assign(o,a[9]);return o;});}
const BO_GEO=D.g,COMUNI_EXTRA=D.c,LINKS_BO=D.l;let QC,SOURCES,ARCH;
const caricaMeta=(()=>{let pr=null;return()=>pr||(pr=(async()=>{const n=MAN&&MAN.meta;if(!n)return;let t=await MEMO.leggi(n);if(!t){const r=await fetch(n);if(!r.ok)return;t=await r.text();MEMO.scrivi(n,t);}const m=JSON.parse(t);QC=m.q;SOURCES=m.s;ARCH=m.a;const h=location.hash.slice(1);if(h==="metodo"||h==="fonti")route(true);})());})();
("requestIdleCallback" in window)?requestIdleCallback(()=>caricaMeta(),{timeout:4000}):setTimeout(()=>caricaMeta(),1500);
for(const p of PLACES){const l=LINKS_BO[p.id];if(l){p.hoursUrl=l.orari||"";p.ticketUrl=l.biglietti||"";if(l.off)p.official=l.off;}}
/* dettagli della scheda (perché andarci, fonti, link) per provincia: scaricati in sottofondo o al tocco */
const DETOK={},DETP={},IDPROV={};
for(const c of COMUNI_EXTRA)for(const p of c.places)(IDPROV[p.id]||(IDPROV[p.id]=new Set())).add(c.prov);
function caricaDet(pr){if(!pr||DETOK[pr])return Promise.resolve();if(DETP[pr])return DETP[pr];
  const n=MAN&&MAN.det&&MAN.det[pr];if(!n){DETOK[pr]=1;return Promise.resolve();}
  return DETP[pr]=(async()=>{let t=await MEMO.leggi(n);if(!t){const r=await fetch(n);if(!r.ok)return;t=await r.text();MEMO.scrivi(n,t);}
    const d=JSON.parse(t);for(const c of COMUNI_EXTRA){const dc=c.prov===pr&&d[c.slug];if(dc)for(const p of c.places)if(dc[p.id])Object.assign(p,dc[p.id]);}DETOK[pr]=1;})();}
const precarica=prs=>{const f=()=>prs.forEach(pr=>caricaDet(pr));("requestIdleCallback" in window)?requestIdleCallback(f,{timeout:2500}):setTimeout(f,400);};
/* classifica: punteggio di rilevanza (calcolato in costruzione; per Bologna con le stesse regole) e posizione */
{const sc=p=>{let s=0;const u=(p.sources||[]).map(x=>x[1]||"").join(" ");if(p.unesco)s+=12;if(u.includes("touringclub.it"))s+=6;if(u.includes("italia.it"))s+=8;
  s+=Math.min(2,Math.max(0,(p.sources||[]).length-1))*2;if(p.status==="closed")s-=10;return Math.max(0,s+((D.pb||{})[p.id]||0));};
 const tutti=[...PLACES.map(p=>(p.r==null&&(p.r=sc(p)),p))];for(const c of COMUNI_EXTRA)for(const p of c.places)tutti.push(p);
 tutti.sort((a,b)=>b.r-a.r||a.name.localeCompare(b.name,"it"));tutti.forEach((p,i)=>p.rk=i+1);}
{const _os=openSheet;openSheet=function(id,from){const ps=[...(IDPROV[id]||[])].filter(pr=>!DETOK[pr]);
  if(!ps.length)return _os(id,from);Promise.all(ps.map(caricaDet)).then(()=>_os(id,from));};}
{const _up=update;update=function(){const r=_up.apply(this,arguments);try{const ps=[...new Set((CUR||[]).slice(0,60).map(p=>{const c=COMUNI.find(x=>x.slug===p.comSlug);return c&&c.prov;}).filter(Boolean))].slice(0,4);
  if(ps.length){precarica(ps);try{localStorage.setItem("ultProv",ps[0]);}catch(e){}}}catch(e){}return r;};}
try{const u=localStorage.getItem("ultProv");if(u)precarica([u]);}catch(e){}
"""
t = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()
t = t.replace("/*CAPI*/", ",".join(json.dumps(x, ensure_ascii=False) for x in sorted(set(sum(check.CAPOLUOGHI.values(), [])))))
_i = t.index("/*PLACES*/"); _j = t.rindex("</script>")
t = t[:_i] + bologna_places + "\n" + LOADER + t[_i + len("/*PLACES*/"):_j] + "\n}\n" + t[_j:]
open(os.path.join(HERE, "index.html"), "w", encoding="utf-8").write(t)
print(len(comuni), "comuni extra,", sum(len(c["places"]) for c in comuni), "luoghi extra,", len(sources), "fonti; index", os.path.getsize(os.path.join(HERE, "index.html")), "byte; dati", os.path.getsize(os.path.join(HERE, NOME_DATI)), "byte")
