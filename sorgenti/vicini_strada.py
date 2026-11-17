"""Comuni vicini con la distanza su strada (17/11/2026, segnalazione del Comune di Verbania:
le distanze in linea d'aria sui laghi ingannano, es. Verbania-Laveno 5 km in linea d'aria, molti di più in auto).
Per ogni comune prende i 15 più vicini in linea d'aria e chiede a OSRM (dati OpenStreetMap) i km su strada;
tiene i 6 più vicini su strada. Scrive sorgenti/data/geo/vicini_strada.json = {slug: [[slug, km], ...]}.
Gira su GitHub Actions (OSRM non è raggiungibile dalla sessione), una richiesta al secondo."""
import glob, json, math, re, sys, time, urllib.request
s = open(glob.glob("luoghi.*.js")[0], encoding="utf-8").read()
pat = re.compile(r'\["([^"]+)","([^"]+)","[a-z-]+","[^"]*","[^"]*","([a-z0-9-]+)",([\d.\-]+),([\d.\-]+)\]')
C = {m.group(3): (float(m.group(4)), float(m.group(5))) for m in pat.finditer(s)}
print(len(C), "comuni con coordinate")
def hav(a, b, c, d):
    r = math.pi / 180; x = math.sin((c - a) * r / 2) ** 2 + math.cos(a * r) * math.cos(c * r) * math.sin((d - b) * r / 2) ** 2
    return 2 * 6371 * math.asin(math.sqrt(x))
out_f = "sorgenti/data/geo/vicini_strada.json"
try: OUT = json.load(open(out_f))
except Exception: OUT = {}
solo = sys.argv[1:]  # facoltativo: solo alcuni comuni
fatti = 0
for slug, (la, lo) in C.items():
    if solo and slug not in solo: continue
    if slug in OUT and not solo: continue
    cand = sorted(((hav(la, lo, *C[k]), k) for k in C if k != slug))[:15]
    pts = [(lo, la)] + [(C[k][1], C[k][0]) for _, k in cand]
    url = "https://router.project-osrm.org/table/v1/driving/" + ";".join(f"{x:.5f},{y:.5f}" for x, y in pts) + "?sources=0&annotations=distance"
    for t in range(4):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "AchPlacesGuide/1.0 (+https://achplaces.com)"}), timeout=30))
            break
        except Exception as e:
            print("riprovo", slug, e); time.sleep(5 * (t + 1)); r = None
    if not r or r.get("code") != "Ok": continue
    dist = r["distances"][0][1:]
    v = sorted((round(d / 1000, 1), k) for d, (_, k) in zip(dist, cand) if d is not None)
    OUT[slug] = [[k, d] for d, k in v[:6]]
    fatti += 1
    if fatti % 200 == 0:
        json.dump(OUT, open(out_f, "w"), separators=(",", ":")); print(fatti, "fatti")
    time.sleep(1.1)
json.dump(OUT, open(out_f, "w"), separators=(",", ":"))
print("fatti", fatti, "totale", len(OUT))
