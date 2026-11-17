"""Quali tragitti dei «Comuni vicini» usano il traghetto (17/11/2026).
OSRM pubblico non permette di escludere i traghetti nella tabella, ma il percorso con i passi dice il mezzo:
per ogni comune un solo percorso origine→v1→origine→v2→… e ogni tratto origine→vicino dice se c'è un tratto «ferry».
Legge sorgenti/data/geo/vicini_traghetto.json, scrive sorgenti/data/geo/vicini_f_<PARTE>.json = {slug: [[slug, km, 0|1], ...]}.
Salva e fa push ogni 150 comuni (SALVA_GIT=1) e riprende da dove era arrivato."""
import json, os, re, subprocess, time, urllib.request, glob
PARTE, PARTI = int(os.environ.get("PARTE", "0")), int(os.environ.get("PARTI", "1"))
F = json.load(open("sorgenti/data/geo/vicini_traghetto.json"))
s = open(glob.glob("luoghi.*.js")[0], encoding="utf-8").read()
pat = re.compile(r'\["([^"]+)","([^"]+)","[a-z-]+","[^"]*","[^"]*","([a-z0-9-]+)",([\d.\-]+),([\d.\-]+)\]')
C = {m.group(3): (float(m.group(4)), float(m.group(5))) for m in pat.finditer(s)}
out_f = f"sorgenti/data/geo/vicini_f_{PARTE}.json"
try: OUT = json.load(open(out_f))
except Exception: OUT = {}
def salva():
    json.dump(OUT, open(out_f, "w"), separators=(",", ":"))
    if os.environ.get("SALVA_GIT"):
        subprocess.run(f'git add {out_f} && git commit -qm "Comuni vicini, traghetti: parte {PARTE} ({len(OUT)})" && (git pull -q --rebase && git push -q || (sleep 9; git pull -q --rebase && git push -q))', shell=True)
fatti = 0
for i, slug in enumerate(sorted(F)):
    if i % PARTI != PARTE or slug in OUT or slug not in C: continue
    v = [x for x in F[slug] if x[0] in C]
    if not v: OUT[slug] = []; continue
    o = C[slug]; pts = []
    for k, _ in v: pts += [o, C[k]]
    pts.append(o)
    url = "https://router.project-osrm.org/route/v1/driving/" + ";".join(f"{b:.5f},{a:.5f}" for a, b in pts) + "?steps=true&overview=false&continue_straight=false"
    r = None
    for t in range(3):
        try:
            r = json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "AchPlacesGuide/1.0 (+https://achplaces.com)"}), timeout=40)); break
        except Exception as e:
            print("riprovo", slug, str(e)[:80], flush=True); time.sleep(4 * (t + 1))
    if not r or r.get("code") != "Ok":
        OUT[slug] = [[k, d, 0] for k, d in v]; print("senza esito", slug, flush=True)
    else:
        legs = r["routes"][0]["legs"]
        OUT[slug] = [[k, d, int(any(st.get("mode") == "ferry" for st in legs[2 * j]["steps"]))] for j, (k, d) in enumerate(v)]
    fatti += 1
    if fatti % 150 == 0: salva(); print(fatti, "fatti", flush=True)
    time.sleep(1.05)
salva(); print("fatti", fatti, "totale", len(OUT))
