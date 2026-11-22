"""Confronto prima/dopo della Guida: stessi luoghi, stesso ordine, stessi conteggi in tutti i filtri, nessun errore JS.
Uso: python3 verifica.py <url_prima> <url_dopo>"""
import json, sys
from playwright.sync_api import sync_playwright

VISTE = ["tutti", "ravenna-ra", "roma-rm", "bologna-bo", "provincia-fi", "provincia-na+provincia-sa", "matera-mt"]
FILTRI = [{}] + [{"cat": [c]} for c in ["storia", "musei", "sacro", "natura", "locale"]] \
    + [{"price": [k]} for k in ["free", "paid", "unk", "card"]] + [{"ideal": [k]} for k in ["rain", "view", "unesco", "borghi", "arancione"]] \
    + [{"time": [k]} for k in ["short", "mid", "long"]] + [{"alerts": True}] \
    + [{"q": q} for q in ["castello", "chiesa", "museo d'arte", "lago", "via", "san giovanni", "romanico", "torre", "vista", "x", "barocc", "Piazza", "città"]] \
    + [{"cat": ["storia"], "q": "torre"}, {"price": ["free"], "ideal": ["view"]}, {"cat": ["natura"], "time": ["long"]}]

JS = """async ([vista,f,pre])=>{const T=window.__T;
 if(pre&&!window.__pre){await Promise.all(T.provs().map(p=>T.det(p)));window.__pre=1;}
 if(window.__vista!==vista){T.setComune(vista);window.__vista=vista;}
 const S=T.S;for(const k of ["cat","sub","price","ideal","time"])S[k].clear();S.alerts=false;S.q="";S.near=null;
 for(const k of ["cat","price","ideal","time"])(f[k]||[]).forEach(x=>S[k].add(x));if(f.alerts)S.alerts=true;if(f.q)S.q=f.q;
 const n0=window.__n||0;T.update();const t0=Date.now();
 while(((window.__n||0)===n0||/Ricerca/.test(document.getElementById('count').textContent))&&Date.now()-t0<30000)await new Promise(r=>setTimeout(r,30));
 return {lista:window.__lista,count:document.getElementById('count').textContent,filtri:(document.getElementById('qbar')||{}).innerText||'',stats:(document.getElementById('stats')||{}).innerText||''};}"""


def raccogli(url, pre):
    out, errs = {}, []
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 390, "height": 844})
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append("console: " + m.text) if m.type == "error" else None)
        pg.goto(url + "/index.html"); pg.wait_for_function("()=>window.__T&&window.__lista&&window.__lista.length>0", timeout=60000)
        for v in VISTE:
            for f in FILTRI:
                out[v + " " + json.dumps(f, ensure_ascii=False)] = pg.evaluate(JS, [v, f, pre])
        b.close()
    return out, errs


A, ea = raccogli(sys.argv[1], True)
B, eb = raccogli(sys.argv[2], False)
diff = [k for k in A if A[k] != B.get(k)]
print("scenari", len(A), "diversi", len(diff), "errori prima", len(ea), "errori dopo", len(eb))
for k in diff[:15]:
    a, b = A[k], B[k]
    print("  ", k, "| count", a["count"], "->", b["count"], "| lista uguale", a["lista"] == b["lista"], "| filtri uguali", a["filtri"] == b["filtri"], "| stats uguali", a["stats"] == b["stats"])
for e in (ea + eb)[:10]: print("  ERR", e[:200])
json.dump({"diff": diff, "errori": ea + eb, "n": len(A)}, open("/tmp/verifica.json", "w"), ensure_ascii=False, indent=1)
