#!/usr/bin/env python3
"""20/11/2026 – prova dei clic sui partner (pagina delle visite servizi.achplaces.com/visite).

Ogni pulsante verso un partner affiliato (Tiqets, GetYourGuide, TicketOne) deve avere
data-goatcounter-click="partner/<dominio di arrivo>/<id del luogo>" e data-goatcounter-title="Partner: <Nome>":
1. nella guida: la funzione gcPar di index.html (e di build.py, da cui nasce) dà il dominio giusto anche per i link
   che passano da Awin; i tre pulsanti partner (card, scheda, visite guidate) la usano;
2. nelle pagine per Google, italiane e inglesi: nessun link a un partner senza l'attributo, e nessun attributo su un
   link che non è di un partner.
Uso: python3 sorgenti/prova_partner_clic.py   (esce con 1 se una prova non riesce)
"""
import glob, json, os, re, subprocess, sys

SITO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTNER = re.compile(r"awin1\.com|tiqets\.com|getyourguide\.|ticketone\.it")
errori = []

# 1. guida
idx = open(os.path.join(SITO, "index.html"), encoding="utf-8").read()
bld = open(os.path.join(SITO, "sorgenti", "build.py"), encoding="utf-8").read()
tpl = open(os.path.join(SITO, "sorgenti", "template.html"), encoding="utf-8").read()
m = re.search(r"function gcPar\(.*?\n", idx)
if not m or m[0] not in bld:
    errori.append("1. gcPar manca in index.html o è diversa da quella di build.py")
else:
    esc = re.search(r"(?:const|function) esc\b[^\n]*", idx)
    casi = [
        ("https://www.awin1.com/cread.php?awinmid=12427&awinaffid=3146807&ued=" + "https%3A%2F%2Fwww.tiqets.com%2Fit%2Fx%2F",
         {"id": "firenze-fi--galleria-degli-uffizi"}, "Tiqets", "partner/tiqets.com/firenze-fi--galleria-degli-uffizi", "Partner: Tiqets"),
        ("https://www.getyourguide.com/florence-l32/x/?partner_id=Y9VWGXI", {"id": "firenze-fi--galleria-degli-uffizi"},
         "GetYourGuide", "partner/getyourguide.com/firenze-fi--galleria-degli-uffizi", "Partner: GetYourGuide"),
        ("https://www.ticketone.it/artist/reggia-di-caserta/", {"id": "caserta-ce--reggia-di-caserta"},
         "TicketOne", "partner/ticketone.it/caserta-ce--reggia-di-caserta", "Partner: TicketOne"),
        ("https://www.tiqets.com/it/y/", {"id": "torre-degli-asinelli", "comSlug": "bologna-bo"},
         "Tiqets", "partner/tiqets.com/bologna-bo--torre-degli-asinelli", "Partner: Tiqets"),
    ]
    js = (esc[0] if esc else "") + "\n" + m[0] + "\nconst C=" + json.dumps(casi) + ";\n" \
        "for(const [u,p,n,a,t] of C){const s=gcPar(u,p,n);" \
        "if(!s.includes(`data-goatcounter-click=\"${a}\"`)||!s.includes(`data-goatcounter-title=\"${t}\"`))console.log('NO',u,s)}"
    r = subprocess.run(["node", "-e", js], capture_output=True, text=True)
    if r.returncode or r.stdout.strip(): errori.append("1. gcPar: " + (r.stdout + r.stderr).strip()[:500])
    else: print("1. gcPar: dominio e luogo giusti in 4 casi (Awin/Tiqets, GetYourGuide, TicketOne, Bologna) — ok")
for nome, s in (("index.html", idx), ("template.html", tpl)):
    n = s.count("gcPar(")
    if n < 5 - (nome == "template.html"):
        errori.append(f"1. {nome}: gcPar usata {n} volte (attese: card, scheda e visite guidate)")
    if "visite/getyourguide-places" in s or 'biglietti/${t[1]==="Tiqets"' in s:
        errori.append(f"1. {nome}: resta un pulsante partner con il vecchio nome del clic")

# 2. pagine per Google
pagine = glob.glob(os.path.join(SITO, "luogo", "*", "index.html")) + glob.glob(os.path.join(SITO, "comune", "*", "index.html")) \
    + glob.glob(os.path.join(SITO, "en", "luogo", "*", "index.html")) + glob.glob(os.path.join(SITO, "en", "comune", "*", "index.html"))
link = senza = sbagliati = 0
for f in pagine:
    for a in re.findall(r"<a [^>]*>", open(f, encoding="utf-8").read()):
        h = re.search(r'href="([^"]*)"', a)
        if not h: continue
        par = bool(PARTNER.search(h[1]))
        gc = re.search(r'data-goatcounter-click="partner/([^/"]+)/([^"]+)"', a)
        if par:
            link += 1
            if not gc or "data-goatcounter-title=\"Partner: " not in a: senza += 1
        elif gc: sbagliati += 1
if senza: errori.append(f"2. pagine per Google: {senza} link a partner senza il clic registrato")
if sbagliati: errori.append(f"2. pagine per Google: {sbagliati} link non di partner con il clic dei partner")
if not senza and not sbagliati: print(f"2. pagine per Google: {link} link a partner in {len(pagine)} pagine, tutti registrati — ok")

for e in errori: print("ERRORE", e)
sys.exit(1 if errori else 0)
