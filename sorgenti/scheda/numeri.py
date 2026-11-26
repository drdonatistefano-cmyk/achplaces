#!/usr/bin/env python3
"""Numeri della «Scheda» di Places (24/11/2026, Stefano: «sistema tutto»).
Apre Ach's Dishes (copia locale del suo repository pubblico) in un browser senza schermo e, per ogni comune, provincia,
zona e regione, legge lo stesso numero che vede chi clicca il link della scheda (#comune-…, #provincia-…, #zona-…,
#regione-…, #prodotti-…). Così i numeri della scheda coincidono sempre con Ach's Dishes.
Scrive scheda.json nella cartella del sito (caricato dalla pagina solo al primo tocco su «Scheda»).
Lo fa ogni notte il flusso «Numeri della Scheda» (.github/workflows/scheda-numeri.yml), gratis.
Gli eventi di Events NON hanno numeri (cambiano ogni settimana): la scheda mostra solo il link alla città.
Uso: python3 sorgenti/scheda/numeri.py CARTELLA_DI_ACHDISHES [--prova]"""
import sys, os, re, json, time, threading, functools, http.server, socketserver, unicodedata
from playwright.sync_api import sync_playwright
RAD = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DISHES = sys.argv[1]; PROVA = '--prova' in sys.argv
def slug(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')
# descrizioni brevi delle regioni: testo nostro (23/11)
RD = json.load(open(os.path.join(os.path.dirname(__file__), 'regioni.json'), encoding='utf-8'))
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
class S(socketserver.ThreadingMixIn, http.server.HTTPServer): daemon_threads = True
sv = S(('127.0.0.1', 0), functools.partial(Q, directory=DISHES)); threading.Thread(target=sv.serve_forever, daemon=True).start()
BASE = f'http://127.0.0.1:{sv.server_address[1]}/index.html'
def leggi(pg, h, sel_js, prima):
    # svuota il contatore, cambia l'indirizzo e aspetta che Ach's Dishes lo riscriva (così due luoghi di fila con lo
    # stesso numero non fanno aspettare)
    pg.evaluate('h=>{for(const e of document.querySelectorAll("#count,.prtot"))e.textContent="";location.hash=h}', h)
    for _ in range(60):
        t = pg.evaluate(sel_js) or ''
        if t: return t
        pg.wait_for_timeout(25)
    return ''
CONTA = '(document.getElementById("count")||{}).textContent'
PROD = '(document.querySelector(".prtot")||{}).textContent'
OUT = {'rc': {'c': {}, 'v': {}, 'r': {}, 'z': {}}, 'pv': {}, 'pr': {}, 'p2r': {}, 'rn': {}, 'zd': {}, 'zp': {}, 'pn': {}, 'rd': RD}
with sync_playwright() as pw:
    b = pw.chromium.launch(); pg = b.new_page(viewport={'width': 390, 'height': 844})
    pg.goto(BASE); pg.wait_for_function('typeof COM!=="undefined"&&typeof PROV!=="undefined"&&document.getElementById("count")', timeout=60000)
    info = pg.evaluate('''()=>({com:Object.values(COM).map(c=>[c.id,c.nome,c.prov]),
        prov:Object.values(PROV).map(p=>[p.sigla,p.reg,p.nome||p.sigla]),reg:Object.entries(REG).map(([k,r])=>[k,r.nome]),
        zone:(Array.isArray(ZONE)?ZONE:Object.values(ZONE)).map(z=>[z.id,z.desc||z.descrizione||z.d||"",z.prov||[]])})''')
    if PROVA: info['com'] = info['com'][:15]; info['prov'] = info['prov'][:6]
    OUT['p2r'] = {s: r for s, r, _ in info['prov']}; OUT['pn'] = {s: n for s, _, n in info['prov']}; OUT['rn'] = {k: n for k, n in info['reg']}
    OUT['zd'] = {z: d for z, d, _ in info['zone'] if d}; OUT['zp'] = {z: p for z, _, p in info['zone']}
    def n_di(t):
        m = re.match(r'\s*([\d.]+)', t); return int(m.group(1).replace('.', '')) if m else 0
    prima = ''
    lavori = ([('c', c, 'comune-' + c) for c, _, _ in info['com']] + [('v', s, 'provincia-' + s.lower()) for s, _, _ in info['prov']]
              + [('z', z, 'zona-' + z) for z, _, _ in info['zone']] + [('r', r, 'regione-' + r) for r, _ in info['reg']])
    nomi = {c: (nome, pv) for c, nome, pv in info['com']}
    t0 = time.time()
    for liv, k, h in lavori:
        txt = leggi(pg, h, CONTA, prima); prima = txt; n = n_di(txt)
        if not n: continue
        if liv == 'c':
            nome, pv = nomi[k]; OUT['rc']['c'][slug(nome) + '-' + (pv or '').lower()] = [n, k]
        else: OUT['rc'][liv][k] = n
    prima = ''
    for liv, k in [('pv', s) for s, _, _ in info['prov']] + [('pr', r) for r, _ in info['reg']]:
        pg.evaluate('location.hash="#"'); pg.wait_for_timeout(30)
        txt = leggi(pg, 'prodotti-' + (k.lower() if liv == 'pv' else k), PROD, '')
        n = n_di(txt)
        if n: OUT[liv][k] = n
    b.close()
sv.shutdown()
# controllo: se Ach's Dishes non si è aperto bene, meglio tenere i numeri di ieri che scriverne di sbagliati
tot = sum(OUT['rc']['r'].values())
if not PROVA and (tot < 1000 or len(OUT['rc']['c']) < 100 or len(OUT['pr']) < 15):
    sys.exit(f'Numeri sospetti (ricette nelle regioni {tot}, comuni {len(OUT["rc"]["c"])}, regioni con prodotti {len(OUT["pr"])}): scheda.json non cambia')
s = json.dumps(OUT, ensure_ascii=False, separators=(',', ':'), sort_keys=True)
dest = os.path.join(RAD, 'scheda.json') if not PROVA else '/tmp/scheda-prova.json'
open(dest, 'w', encoding='utf-8').write(s)
print(f'{os.path.basename(dest)}: {len(s)//1024} KB · comuni {len(OUT["rc"]["c"])} · province {len(OUT["rc"]["v"])} · zone {len(OUT["rc"]["z"])} · regioni {len(OUT["rc"]["r"])} · prodotti prov {len(OUT["pv"])} reg {len(OUT["pr"])} · {round(time.time()-t0)} s')
