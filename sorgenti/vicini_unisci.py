"""Unisce i due calcoli OSRM dei «Comuni vicini» (17/11/2026) in vicini.json, pubblicato nella radice del sito.
vicini_traghetto.json: i 6 più vicini con i traghetti; vicini_strada.json: i 6 più vicini senza traghetti.
Un tragitto usa il traghetto (terzo campo 1, in guida l'icona ⛴️) quando senza traghetto è più lungo del 10%
o non entra tra i 6 più vicini. Risultato: {slug: [[slug, km, 0|1], ...]} con i 6 più vicini."""
import json
F = json.load(open("sorgenti/data/geo/vicini_traghetto.json"))
import glob
R = {}
for f in sorted(glob.glob("sorgenti/data/geo/vicini_strada_*.json")):   # le 4 parti senza traghetti
    R.update(json.load(open(f)))
print(len(R), "comuni calcolati senza traghetti su", len(F))
OUT = {}
for slug in set(F) | set(R):
    r = {k: d for k, d in R.get(slug, [])}
    r6 = max(r.values()) if len(r) >= 6 else float("inf")
    c = {k: [k, d, 0] for k, d in r.items()}
    for k, d in F.get(slug, []):
        if k in r:
            if r[k] > d * 1.1 + 0.5: c[k] = [k, d, 1]
        elif d < r6: c[k] = [k, d, 1]
    OUT[slug] = sorted(c.values(), key=lambda x: x[1])[:6]
json.dump(OUT, open("vicini.json", "w"), separators=(",", ":"))
n = sum(1 for v in OUT.values() for x in v if x[2])
print(len(OUT), "comuni,", n, "tragitti col traghetto")
