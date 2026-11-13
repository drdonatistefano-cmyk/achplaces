#!/usr/bin/env python3
"""13/11/2026 – versione inglese di Ach's Places Guide.

Dopo la costruzione (build.py, mappa_build.py, istantanea.py) scrive:
  en.<prov>.<impronta>.json  traduzioni dei testi delle schede di quella provincia {impronta del testo: inglese}
  en.ui.<impronta>.json      traduzioni dei testi lunghi dell'interfaccia (Metodo, note)
  en.<impronta>.js           il motore che traduce la pagina (traduci/en_motore.js + dizionario en_diz.json)
e mette in testa a index.html e filtri.html lo script «en-boot»: sceglie la lingua (scelta salvata, ?lang=,
altrimenti la lingua del browser: chi non ha l'italiano tra le lingue del browser vede l'inglese) e aggiunge
il pulsante IT/EN. La memoria delle traduzioni sta nel ramo «traduzioni» (traduci.yml, Opus-MT it-en).
Uso: python3 en_build.py [cartella del sito] [cartella della memoria]
"""
import glob, hashlib, json, os, re, subprocess, sys
QUI = os.path.dirname(os.path.abspath(__file__))
SITO = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(QUI)
MEMD = sys.argv[2] if len(sys.argv) > 2 else None
sys.path.insert(0, QUI)
import estrai
estrai.HERE = SITO

def memoria():
    mem = {}
    files = glob.glob(os.path.join(MEMD, '*.jsonl')) if MEMD else []
    if not files:  # dal ramo traduzioni del repository
        repo = '/home/claude/achplaces' if os.path.isdir('/home/claude/achplaces/.git') else SITO
        try:
            subprocess.run(['git', '-C', repo, 'fetch', '-q', 'origin', 'traduzioni:refs/remotes/origin/traduzioni'], check=False, timeout=120)
            nomi = subprocess.check_output(['git', '-C', repo, 'ls-tree', '-r', '--name-only', 'origin/traduzioni', 'memoria']).decode().split()
            for n in nomi:
                if n.endswith('.jsonl'):
                    for l in subprocess.check_output(['git', '-C', repo, 'show', 'origin/traduzioni:' + n]).decode().splitlines():
                        try: r = json.loads(l); mem[r['k']] = r['en']
                        except Exception: pass
        except Exception as e:
            print('en_build: memoria non letta:', e)
    for f in files:
        for l in open(f):
            try: r = json.loads(l); mem[r['k']] = r['en']
            except Exception: pass
    return mem

def pulisci(t):
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def scrivi(pref, obj, ext='json'):
    t = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    n = pref + '.' + hashlib.sha256(t.encode()).hexdigest()[:10] + '.' + ext
    for f in glob.glob(os.path.join(SITO, pref + '.*.' + ext)):
        if re.fullmatch(re.escape(pref) + r'\.[0-9a-f]{10}\.' + ext, os.path.basename(f)) and not f.endswith(n): os.remove(f)
    open(os.path.join(SITO, n), 'w').write(t)
    return n

def main():
    mem = memoria()
    M = json.load(open(os.path.join(SITO, 'manifest.json')))
    R = estrai.raccogli()
    det = {}; tot = 0; man = 0
    for pr, d in sorted(R.items()):
        o = {k: pulisci(mem[k]) for k in d if k in mem}
        man += sum(1 for k in d if k not in mem)
        if not o: continue
        det[pr] = scrivi('en.' + pr.lower(), o); tot += len(o)
    ui = {}
    for t in json.load(open(os.path.join(QUI, 'ui_it.json'))):
        k = estrai.en_k(t)
        if k in mem: ui[k] = pulisci(mem[k])
    nui = scrivi('en.ui', ui)
    diz = json.load(open(os.path.join(QUI, 'en_diz.json')))
    js = open(os.path.join(QUI, 'en_motore.js')).read().replace('/*DIZ*/{}', json.dumps(diz, ensure_ascii=False, separators=(',', ':')))
    njs = scrivi('en', js, 'js')
    M['en'] = {'js': njs, 'ui': nui, 'det': det}
    json.dump(M, open(os.path.join(SITO, 'manifest.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    boot = BOOT.replace('__MAN__', json.dumps({'ui': nui, 'det': det}, separators=(',', ':'))).replace('__JS__', njs)
    for pag in ('index.html', 'filtri.html'):
        f = os.path.join(SITO, pag)
        if not os.path.exists(f): continue
        h = open(f, encoding='utf-8').read()
        h = re.sub(r'<script id="en-boot">.*?</script>\s*<style id="en-boot-css">.*?</style>\n?', '', h, flags=re.S)
        i = h.index('<head>') + len('<head>')
        j = h.find('<meta charset="utf-8">', i)
        if j >= 0: i = j + len('<meta charset="utf-8">')
        h = h[:i] + '\n' + boot + h[i:]
        open(f, 'w', encoding='utf-8').write(h)
    print(f'en_build: {tot} testi tradotti in {len(det)} province, {man} ancora da tradurre; interfaccia {len(ui)} testi lunghi; {njs}')

BOOT = '''<script id="en-boot">/* 13/11/2026: lingua della pagina. Scelta salvata, oppure ?lang=, altrimenti la lingua del browser
   (senza l'italiano tra le lingue del browser la guida si apre in inglese). Pulsante IT/EN in alto. */
(function(){var L=null,d=document.documentElement;try{L=localStorage.getItem("lang");}catch(e){}
var q=location.search.match(/[?&]lang=(it|en)\\b/);if(q){L=q[1];try{localStorage.setItem("lang",L);}catch(e){}}
if(L!=="it"&&L!=="en"){var ls=navigator.languages&&navigator.languages.length?navigator.languages:[navigator.language||"it"];L="en";for(var i=0;i<ls.length;i++)if(/^it\\b/i.test(ls[i]||"")){L="it";break;}}
window.ACH_LANG=L;
if(L==="en"){d.lang="en";d.classList.add("en-wait");setTimeout(function(){d.classList.remove("en-wait");},1200);
window.ACH_EN_MAN=__MAN__;var s=document.createElement("script");s.src="__JS__";s.async=true;document.head.appendChild(s);}
function bottone(){if(document.getElementById("langbtn"))return;var b=document.createElement("button");b.id="langbtn";b.type="button";b.setAttribute("data-noen","");
b.setAttribute("aria-label",L==="en"?"Versione italiana":"English version");b.title=L==="en"?"Italiano":"English";
b.innerHTML=L==="en"?"<span>IT</span>":"<span>EN</span>";
b.onclick=function(){var n=L==="en"?"it":"en";try{localStorage.setItem("lang",n);}catch(e){}var u=location.href.replace(/([?&])lang=(it|en)&?/,"$1").replace(/[?&]$/,"");location.href=u;if(u===location.href)location.reload();};
var g=document.querySelector(".ach-guide")||document.getElementById("gbtn");
if(g&&g.id==="gbtn"){g.parentNode.insertBefore(b,g.nextSibling);b.classList.add("lb-map");}else if(g){g.appendChild(b);}else{b.classList.add("lb-float");document.body.appendChild(b);}}
if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",bottone);else bottone();})();</script>
<style id="en-boot-css">html.en-wait body{opacity:0}
#langbtn{font:600 12.5px/1 Inter,system-ui,sans-serif;letter-spacing:.04em;display:inline-flex;align-items:center;justify-content:center;min-width:38px;height:30px;padding:0 10px;margin-left:6px;border-radius:999px;border:1.5px solid currentColor;background:transparent;color:inherit;cursor:pointer;opacity:.85}
#langbtn:hover{opacity:1}#langbtn.lb-map{position:relative;z-index:6;height:40px;min-width:44px;background:var(--panel,#fff);color:var(--ink,#1d1b18);border:1px solid var(--ln,rgba(0,0,0,.12));box-shadow:0 2px 10px rgba(0,0,0,.08);margin-left:8px}
#langbtn.lb-float{position:fixed;top:10px;right:10px;z-index:99;background:#fff;color:#222}</style>
'''

if __name__ == '__main__':
    main()
