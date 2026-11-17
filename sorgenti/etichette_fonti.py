"""17/11/2026: corregge le etichette delle fonti che non corrispondono all indirizzo (es. «Visit Piemonte» su italia.it).
Si lancia nella radice del sito dopo la costruzione; rinomina i det.*.json cambiati e aggiorna manifest, index.html e filtri.html.
Poi vanno rigenerate le pagine statiche con sorgenti/pagine.py."""
import json,glob,hashlib,os,re,unicodedata
from urllib.parse import urlparse, unquote
s=open(glob.glob("luoghi.*.js")[0],encoding="utf-8").read()
NOMI={m.group(3):m.group(1) for m in re.finditer(r'\["([^"]+)","([^"]+)","[a-z-]+","[^"]*","[^"]*","([a-z0-9-]+)",',s)}
ORG={'italia.it':'italia.it','turismotorino.org':'Turismo Torino e Provincia','visitcuneese.it':'Visit Cuneese (ATL del Cuneese)',
 'visitlmr.it':'Ente Turismo Langhe Monferrato Roero','langheroero.it':'Ente Turismo Langhe Monferrato Roero','visitvalsesiavercelli.it':'ATL Valsesia Vercelli',
 'touringclub.it':'Touring Club Italiano','alexala.it':'Alexala (ATL della provincia di Alessandria)','turismonovara.it':'ATL della Provincia di Novara',
 'pngp.it':'Parco Nazionale Gran Paradiso','borghipiubelliditalia.it':"I Borghi più belli d'Italia",'atl.biella.it':'ATL Biella Valsesia Vercelli',
 'distrettolaghi.it':'Distretto Turistico dei Laghi','fondoambiente.it':"FAI – Fondo per l'Ambiente Italiano",'cultura.gov.it':'Ministero della Cultura',
 'lavenaria.it':'Reggia di Venaria','vallemaira.org':'Valle Maira','areeprotetteappenninopiemontese.it':"Aree protette dell'Appennino piemontese",
 'ecomuseo.it':'Ecomusei del Piemonte','lang.fondazionevaldese.org':'Fondazione Centro Culturale Valdese','munlabtorino.it':'MuNLab Ecomuseo dell\'Argilla',
 'ecomuseodellerocche.it':'Ecomuseo delle Rocche del Roero','provincia.biella.it':'Provincia di Biella','vallesusa-tesori.it':'Valle di Susa. Tesori di Arte e Cultura Alpina',
 'emiliaromagnaturismo.it':'Emilia-Romagna Turismo'}
def norm(x): return re.sub(r'[^a-z]','',unicodedata.normalize('NFKD',x.lower()).encode('ascii','ignore').decode())
def nome_dom(u,com):
    if 'web.archive.org' in u:
        m=re.search(r'web\.archive\.org/web/\d+[a-z_]*/(https?://.*)',u)
        if not m: return None
        n=nome_dom(m.group(1),com); return n
    dom=urlparse(u).netloc.lower().replace('www.','')
    if dom in ORG: return ORG[dom]
    for d,n in ORG.items():
        if dom.endswith('.'+d): return n
    m=re.match(r'comune\.([a-z0-9-]+)\.([a-z]{2})\.it$',dom) or re.match(r'comune\.([a-z0-9-]+)\.it$',dom)
    if m:
        cn=NOMI.get(com,'')
        if cn and norm(cn)==norm(m.group(1)): return 'Comune di '+cn
        return 'Comune di '+m.group(1).replace('-',' ').title()
    return dom
tot=0; files={}
for f in glob.glob('det.*.json'):
    D=json.load(open(f)); n=0
    for com,ent in D.items():
        for pid,p in ent.items():
            if not isinstance(p,dict): continue
            for s_ in p.get('sources',[]):
                lab,u=s_[0],s_[1]
                for pre in ('Visit Piemonte','Touring Club - Emilia-Romagna Turismo'):
                    if lab.startswith(pre):
                        dom=urlparse(u).netloc
                        if pre=='Visit Piemonte' and ('visitpiemonte' in dom or 'piemonteitalia' in dom): continue
                        if pre.startswith('Touring') and 'touringclub' in dom: continue
                        nn=nome_dom(u,com)
                        if nn: s_[0]=nn+lab[len(pre):]; n+=1
    if n:
        txt=json.dumps(D,ensure_ascii=False,separators=(',',':'))
        pv=f.split('.')[1]; h=hashlib.sha256(txt.encode()).hexdigest()[:10]; new=f'det.{pv}.{h}.json'
        open(new,'w').write(txt); os.remove(f); files[f]=new; tot+=n
for p in ['manifest.json','filtri.html','index.html']:
    t=open(p).read()
    for a,b in files.items(): t=t.replace(a,b)
    open(p,'w').write(t)
print('etichette corrette',tot,'file',len(files))
