"""Tempi di apertura della Guida (index.html) come servita da GitHub Pages (servi_gh.py: gzip, max-age=600).
390 px, latenza 150 ms, 1,6 Mbit/s, CPU x4; prima visita (contesto nuovo) e seconda visita (stesso contesto); mediana di N prove.
«pronto» = conteggio e prime card disegnati; «completo» = anche le descrizioni delle prime 6 card.
Uso: python3 misura2.py <base_url> <uscita.json> [prove]"""
import json, sys, statistics
from playwright.sync_api import sync_playwright

BASE = sys.argv[1].rstrip("/"); OUT = sys.argv[2]; RUNS = int(sys.argv[3]) if len(sys.argv) > 3 else 3
PRONTO = "()=>{const c=document.getElementById('count');return c&&/\\d/.test(c.textContent)&&!c.textContent.includes('Caricamento')&&document.querySelectorAll('.card').length>0}"
COMPLETO = "()=>{const d=[...document.querySelectorAll('#grid .card .desc')].slice(0,6);return d.length>=6&&d.every(e=>e.textContent.trim().length>0)}"


def rallenta(ctx, pg):
    s = ctx.new_cdp_session(pg)
    s.send("Network.enable")
    s.send("Network.emulateNetworkConditions", {"offline": False, "latency": 150, "downloadThroughput": 1.6e6 / 8, "uploadThroughput": 0.75e6 / 8})
    s.send("Emulation.setCPUThrottlingRate", {"rate": 4})


def tempo(pg, url):
    pg.add_init_script("(()=>{const f=" + PRONTO + ",h=" + COMPLETO + ";const g=()=>{try{if(!window.__tP&&f())window.__tP=performance.now();if(!window.__tC&&h())window.__tC=performance.now();}catch(e){}if(!window.__tC)setTimeout(g,10);};"
                       "document.readyState==='loading'?document.addEventListener('readystatechange',g,{once:true}):g();setTimeout(g,0);})()")
    byt = [0]
    pg.on("response", lambda r: byt.__setitem__(0, byt[0] + int(r.headers.get("content-length") or 0)))
    pg.goto(url, wait_until="commit")
    pg.wait_for_function("()=>window.__tP&&window.__tC", timeout=120000, polling=50)
    return round(pg.evaluate("()=>window.__tP") / 1000, 2), round(pg.evaluate("()=>window.__tC") / 1000, 2), byt[0]


ris = {}
with sync_playwright() as p:
    b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
    url = BASE + "/index.html"
    prime, seconde, errs = [], [], []
    for k in range(RUNS):
        ctx = b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2)
        pg = ctx.new_page(); pg.on("pageerror", lambda e: errs.append(str(e)))
        rallenta(ctx, pg)
        prime.append(tempo(pg, url))
        pg.wait_for_timeout(5000)  # scritture in IndexedDB, istantanea, anticipi
        pg2 = ctx.new_page(); pg2.on("pageerror", lambda e: errs.append(str(e)))
        rallenta(ctx, pg2); pg.close()
        seconde.append(tempo(pg2, url))
        ctx.close()
    med = lambda L, i: statistics.median(x[i] for x in L)
    ris = dict(prima=prime, seconda=seconde, errori=errs,
               mediana=dict(prima_pronto=med(prime, 0), prima_completo=med(prime, 1), prima_kb=round(med(prime, 2) / 1024),
                            seconda_pronto=med(seconde, 0), seconda_completo=med(seconde, 1)))
    print(json.dumps(ris["mediana"]), "errori", len(errs))
    b.close()
json.dump(ris, open(OUT, "w"), ensure_ascii=False, indent=1)
