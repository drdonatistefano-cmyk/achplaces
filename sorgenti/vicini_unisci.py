"""Unisce le parti di vicini_traghetto_flag.py in vicini.json (radice del sito): {slug: [[slug, km, 0|1], ...]}.
I km sono su strada (OSRM, traghetti compresi); 1 = il tragitto usa un traghetto (in guida l'icona ⛴️)."""
import glob, json
F = json.load(open("sorgenti/data/geo/vicini_traghetto.json"))
P = {}
for f in sorted(glob.glob("sorgenti/data/geo/vicini_f_*.json")): P.update(json.load(open(f)))
OUT = {k: P.get(k, [[a, d, 0] for a, d in v]) for k, v in F.items()}
json.dump(OUT, open("vicini.json", "w"), separators=(",", ":"))
print(len(P), "comuni controllati su", len(F), "·", sum(1 for v in OUT.values() for x in v if x[2]), "tragitti col traghetto")
