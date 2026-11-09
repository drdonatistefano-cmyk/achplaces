# genera data/coda-globale.json: comuni non ancora nella guida con voci MiC, ordinati per numero di voci MiC (strategia «importanza prima»)
import json,glob,os,unicodedata,re
def n(s):s=unicodedata.normalize('NFD',s.lower());s=''.join(c for c in s if not unicodedata.combining(c));return re.sub(r"[^a-z]","",s)
AL={n("Reggio nell'Emilia"):n('Reggio Emilia'),n('Reggio di Calabria'):n('Reggio Calabria')}
CAPN=['Agrigento','Alessandria','Ancona','Aosta','Arezzo','Ascoli Piceno','Asti','Avellino','Bari','Barletta','Andria','Trani','Belluno','Benevento','Bergamo','Biella','Bologna','Bolzano','Brescia','Brindisi','Cagliari','Caltanissetta','Campobasso','Carbonia','Caserta','Catania','Catanzaro','Chieti','Como','Cosenza','Cremona','Crotone','Cuneo','Enna','Fermo','Ferrara','Firenze','Foggia','Forlì','Cesena','Frosinone','Genova','Gorizia','Grosseto','Imperia','Isernia',"L'Aquila",'La Spezia','Latina','Lecce','Lecco','Livorno','Lodi','Lucca','Macerata','Mantova','Massa','Carrara','Matera','Messina','Milano','Modena','Monza','Napoli','Novara','Nuoro','Oristano','Padova','Palermo','Parma','Pavia','Perugia','Pesaro','Urbino','Pescara','Piacenza','Pisa','Pistoia','Pordenone','Potenza','Prato','Ragusa','Ravenna','Reggio Calabria','Reggio Emilia','Rieti','Rimini','Roma','Rovigo','Salerno','Sassari','Savona','Siena','Siracusa','Sondrio','Taranto','Teramo','Terni','Torino','Trapani','Trento','Treviso','Trieste','Udine','Varese','Venezia','Verbania','Vercelli','Verona','Vibo Valentia','Vicenza','Viterbo']
CAP={AL.get(n(x),n(x)) for x in CAPN}
m=json.load(open('manifest.json'));d=json.load(open(m['dati']))
import sys as _s9; _s9.path.insert(0,'/home/claude/achs-places-guide'); from leggi_dati import righe as _righe9; d = _righe9(d)   # 9/11: dati per colonne
if 'dz' in d:
  for _c in d['c']: _c['regione']=d['dz']['regione'][_c['regione']]  # dati con dizionari (8/11)
ist={x.get('istat') for x in d['c']}|{'037006'}
nm={(x.get('regione'),n(x['name'])) for x in d['c']}|{('emilia-romagna',n('Bologna'))}
rows=[]
for f in sorted(glob.glob('data/archivio/comuni-*.json')):
  r=os.path.basename(f)[7:-5];j=json.load(open(f));cs=j['comuni'] if isinstance(j,dict) else j
  for c in cs:
    k=n(c['nome']);k=AL.get(k,k)
    if c.get('istat') in ist or (r,k) in nm: continue
    cap=k in CAP; pr=bool(c.get('premi'))
    if c.get('mic') or cap or pr:
      tier=0 if cap else (1 if (pr or len(c.get('mic') or [])>=3) else 2)
      rows.append({'tier':tier,'mic':len(c.get('mic') or []),'premi':c.get('premi') or [],'regione':r,'nome':c['nome'],'prov':c.get('prov'),'istat':c.get('istat')})
rows.sort(key=lambda x:(x['tier'],-x['mic'],x['regione'],x['nome']))
json.dump(rows,open('data/coda-globale.json','w'),ensure_ascii=False,indent=0)
import collections;print(len(rows),collections.Counter(x['tier'] for x in rows))
for x in rows[:40]:print(x['tier'],x['mic'],x['premi'],x['regione'],x['nome'],x['prov'])
