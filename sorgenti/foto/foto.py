"""Raccoglie foto libere (Wikimedia Commons) per i luoghi della guida.
Uso: python3 foto.py Comune1 Comune2 ...   (incrementale: usa la cache foto.json)"""
import json,subprocess,time,unicodedata,re,difflib,sys,os,urllib.parse,io
from PIL import Image
G='/home/claude/achs-places-guide/';F='/home/claude/foto/'
UA='AchsPlacesGuide/0.1 (guida turistica non commerciale; https://claude.ai/artifact/UXN4Ykm771EoLEvJAifppr) curl'
STOP={'di','del','della','dei','delle','degli','e','la','il','lo','le','i','gli','d','l','a','al','alla','in'}
GEN={'chiesa','museo','palazzo','castello','torre','piazza','parrocchiale','santuario','basilica','cattedrale','duomo','civico','borgo','centro','storico','lago','forra','parco','rocca','teatro','fontana','abbazia','convento','monastero','villa','ponte','porta','mura','acquedotto','anfiteatro','speco','eremo','oratorio','pieve','collegiata','pinacoteca','galleria','biblioteca','cappella','grotta','grotte','riserva','bosco','monte','valle','cascata','necropoli','area','archeologico','archeologica','casa','loggia','arco'}
TIPO={'chiesa':'sacro','basilica':'sacro','cattedrale':'cattedrale','duomo':'cattedrale','santuario':'sacro','pieve':'sacro','collegiata':'sacro','oratorio':'sacro','cappella':'sacro','abbazia':'sacro','convento':'sacro','monastero':'sacro','eremo':'sacro','speco':'sacro','museo':'museo','pinacoteca':'museo','galleria':'museo','lago':'lago','forra':'forra','parco':'parco','riserva':'parco','rocca':'forte','castello':'forte','fortezza':'forte','teatro':'teatro','anfiteatro':'anfiteatro','palazzo':'palazzo','piazza':'piazza','torre':'torre','fontana':'fontana','ponte':'ponte','acquedotto':'acquedotto','villa':'villa','mura':'mura','grotta':'grotta','grotte':'grotta','necropoli':'necropoli','casa':'casa','cisterna':'cisterna'}
def norm(s):
  s=unicodedata.normalize('NFD',s.lower());s=''.join(c for c in s if not unicodedata.combining(c))
  return [w for w in re.sub(r"[^a-z0-9 ]"," ",s).split() if w not in STOP]
def slug40(s):
  s="".join(c for c in unicodedata.normalize("NFD",s) if not unicodedata.combining(c)).lower()
  return re.sub(r"[^a-z0-9]+","-",s).strip("-")[:40].rstrip("-")
_ult=[0.0]
def curl(args,tries=10):
  for k in range(tries):
    if 'wikimedia.org' in ' '.join(args):
      w=_ult[0]+1.1-time.time()
      if w>0:time.sleep(w)
      _ult[0]=time.time()
    r=subprocess.run(['curl','-s','-w','\n%{http_code}','--max-time','60','-A',UA]+args,capture_output=True,text=True).stdout
    body,_,code=r.rpartition('\n')
    if code=='200':return body
    if code=='404':return None
    time.sleep(3+4*k)
  return None
def sparql(q):
  b=curl(['-G','https://query.wikidata.org/sparql','--data-urlencode','query='+q,'-H','Accept: application/sparql-results+json'])
  return json.loads(b)['results']['bindings'] if b else []
def tipi(w):
  for x in w:
    if x in TIPO:return {TIPO[x]}
  return set()
def punteggio(a,b,com=''):
  C=set(norm(com))
  A=[w for w in norm(a) if w not in C];B=[w for w in norm(b) if w not in C]
  if not A or not B:return 0
  ta,tb=tipi(A[:3]),tipi(B[:3])
  if ta and tb and not (ta&tb):return 0
  if ta and not tb and len(B)<=2:return 0
  r=difflib.SequenceMatcher(None,' '.join(A),' '.join(B)).ratio()
  sa,sb=set(A)-GEN,set(B)-GEN
  if sb and sb<=set(A) and (set(B)&GEN)<=set(A): r=max(r,0.8 if len(sb)>=2 else 0.76)
  if sa and sa<=set(B) and len(sa)>=2: r=max(r,0.8)
  return r
m=json.load(open(G+'manifest.json'));D=json.load(open(G+m['dati']))
PARTE=None
if len(sys.argv)>2 and sys.argv[1]=='--parte':PARTE=(int(sys.argv[2]),int(sys.argv[3]))
CF=F+('foto-%d.json'%PARTE[0] if PARTE else 'foto.json')
cache=json.load(open(CF)) if os.path.exists(CF) else {}
def salva():
  json.dump(cache,open(CF+'.tmp','w'),ensure_ascii=False);os.replace(CF+'.tmp',CF)
# Bologna: luoghi in data/places-bologna.js
try:
  import subprocess as _s
  BO=json.loads(_s.check_output(['node','-e',"const fs=require('fs');eval(fs.readFileSync('"+G+"data/places-bologna.js','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES.map(p=>[p.id,p.name])))"]))
  D['c'].append({'name':'Bologna','istat':'037006','slug':'','places':[[i,n] for i,n in BO]})
except Exception as e:print('Bologna non letta',e)
def fasi(scelti):
  # categorie senza foto principale: primo file immagine della categoria
  for pid in scelti:
    r=cache[pid]
    if 'cat' in r and 'file' not in r:
      b=curl(['https://commons.wikimedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtype=file&cmlimit=10&cmtitle='+urllib.parse.quote('Category:'+r['cat'])])
      if b:
        for x in json.loads(b)['query']['categorymembers']:
          if re.search(r'\.(jpe?g|png|webp)$',x['title'],re.I):r['file']=x['title'][5:];r['via']='categoria';break
      time.sleep(0.5)
  # ricerca diretta su Commons con controllo del comune nelle categorie
  for pid in scelti:
    r=cache[pid]
    if 'file' in r:continue
    q=r['n']+' '+r['com']
    b=curl(['https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrlimit=5&gsrsearch='+urllib.parse.quote(q+' filetype:bitmap')+'&prop=categories&cllimit=50'])
    time.sleep(0.5)
    if not b:continue
    pages=sorted(json.loads(b).get('query',{}).get('pages',{}).values(),key=lambda x:x.get('index',99))
    cn=' '.join(norm(r['com']))
    for pg in pages:
      cats=' '.join(' '.join(norm(x['title'][9:])) for x in pg.get('categories',[]))
      tit=' '.join(norm(pg['title'][5:]))
      nome=set(norm(r['n']))-GEN
      if cn in cats and nome and len(nome&set(tit.split()+cats.split()))>=max(1,min(2,len(nome))):
        r['file']=pg['title'][5:];r['via']='ricerca';break
  # metadati e miniature, 50 alla volta
  need=[p for p in scelti if 'file' in cache[p]]
  for i in range(0,len(need),50):
    grp=need[i:i+50];tit='|'.join('File:'+cache[p]['file'] for p in grp)
    b=curl(['https://commons.wikimedia.org/w/api.php?action=query&format=json&formatversion=2&prop=imageinfo&iiprop=extmetadata|url&iiurlwidth=250&titles='+urllib.parse.quote(tit)])
    if not b:continue
    j=json.loads(b)['query'];norm2={n['to']:n['from'] for n in j.get('normalized',[])}
    info={}
    for pg in j['pages']:
      if 'imageinfo' not in pg:continue
      ii=pg['imageinfo'][0];em=ii.get('extmetadata',{})
      aut=re.sub(r'\s+',' ',re.sub('<[^>]+>','',em.get('Artist',{}).get('value',''))).strip()
      if not aut or len(aut)>60 or 'machine-readable' in aut:aut=''
      info[norm2.get(pg['title'],pg['title'])[5:]]=dict(t=ii.get('thumburl'),u=ii.get('descriptionurl'),a=aut,l=em.get('LicenseShortName',{}).get('value',''))
    for p in grp:
      x=info.get(cache[p]['file'])
      if x and x['t'] and x['l']:cache[p].update(x)
      else:cache[p].pop('file',None)
    time.sleep(1)
  # scarico e converto
  for p in need:
    r=cache[p]
    if 'file' not in r:continue
    for k in range(5):
      w=_ult[0]+1.1-time.time()
      if w>0:time.sleep(w)
      _ult[0]=time.time()
      b=subprocess.run(['curl','-sL','--max-time','40','-A',UA,'-o',F+'tmp','-w','%{http_code}',r['t']],capture_output=True,text=True).stdout
      if b in('200','404'):break
      time.sleep(3+4*k)
    if b!='200':continue
    try:
      im=Image.open(F+'tmp').convert('RGB');w,h=im.size;s=min(w,h)
      im=im.crop(((w-s)//2,(h-s)//2,(w-s)//2+s,(h-s)//2+s)).resize((168,168),Image.LANCZOS)
      import hashlib;fn=slug40(p.replace('--','-'))[:40]+'-'+hashlib.md5(p.encode()).hexdigest()[:6]+'.webp'
      im.save(F+'img/'+fn,'WEBP',quality=72,method=6);r['img']=fn
      r['c']='#%02x%02x%02x'%im.resize((1,1)).getpixel((0,0))
    except Exception as e:r.pop('file',None)


TOT=[]
for c in D['c']:
  scelti=[]
  if PARTE:
    if (D['c'].index(c)%PARTE[1])!=PARTE[0]:continue
  elif c['name'] not in sys.argv[1:]:continue
  if all(((c['slug']+'--'+(a[0] if a[0] else slug40(a[1]))) if c['slug'] else a[0]) in cache for a in c['places']):continue
  items=sparql('''SELECT ?it ?itLabel ?img ?cat WHERE { ?com wdt:P635 "%s". ?it wdt:P131+ ?com. OPTIONAL{?it wdt:P18 ?img} OPTIONAL{?it wdt:P373 ?cat} FILTER(BOUND(?img)||BOUND(?cat)) SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". } }'''%c['istat'])
  time.sleep(1)
  for a in c['places']:
    pid=(c['slug']+'--'+(a[0] if a[0] else slug40(a[1]))) if c['slug'] else a[0]
    if pid in cache:continue
    best,bs=None,0
    for b in items:
      s=punteggio(a[1],b['itLabel']['value'],c['name'])
      if s>bs:bs,best=s,b
    rec={'n':a[1],'com':c['name'],'s':round(bs,2)}
    if best and bs>=0.76:
      rec['wd']=best['it']['value'].rsplit('/',1)[1];rec['lab']=best['itLabel']['value']
      if 'img' in best:rec['file']=urllib.parse.unquote(best['img']['value'].split('FilePath/')[1]);rec['via']='wikidata'
      elif 'cat' in best:rec['cat']=best['cat']['value']
    cache[pid]=rec;scelti.append(pid)
  fasi(scelti);TOT+=scelti;salva();print(c['name'],sum('img' in cache[p] for p in scelti),'/',len(scelti),flush=True)

salva()
from collections import Counter
print(Counter(cache[p].get('via','nessuna') if 'img' in cache[p] else 'nessuna' for p in TOT),len(TOT))
