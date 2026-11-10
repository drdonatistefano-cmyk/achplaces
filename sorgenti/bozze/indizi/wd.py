import json,csv,urllib.parse,urllib.request,time,os,re,sys
S={r['comune']:(r['pro_com_t'],r['sigla']) for r in csv.DictReader(open('/home/claude/achs-places-guide/data/geo/comuni_istat.csv'))}
names=[os.path.basename(f)[9:-4] for f in __import__('glob').glob('/home/claude/bozze/rinviati-*.txt')]
Q='''SELECT ?it ?itLabel ?tipoLabel ?sito ?wiki ?tutela ?coord WHERE {
 ?c wdt:P635 "%s" .
 { ?it wdt:P131 ?c } UNION { ?it wdt:P131 ?f . ?f wdt:P131 ?c . }
 ?it wdt:P31 ?tipo .
 OPTIONAL { ?it wdt:P856 ?sito }
 OPTIONAL { ?wiki schema:about ?it ; schema:isPartOf <https://it.wikipedia.org/> }
 OPTIONAL { ?it wdt:P1435 ?t . ?t rdfs:label ?tutela FILTER(lang(?tutela)="it") }
 OPTIONAL { ?it wdt:P625 ?coord }
 FILTER NOT EXISTS { ?it wdt:P31 wd:Q747074 } FILTER NOT EXISTS { ?it wdt:P31 wd:Q5 }
 SERVICE wikibase:label { bd:serviceParam wikibase:language "it,en". }
} LIMIT 400'''
out={}
for n in sorted(names):
    if n not in S: print('no istat',n);continue
    code=S[n][0]
    url='https://query.wikidata.org/sparql?format=json&query='+urllib.parse.quote(Q%code)
    req=urllib.request.Request(url,headers={'User-Agent':'AchPlacesGuide/1.0 (indizi rinviati)'})
    for t in range(3):
        try: d=json.load(urllib.request.urlopen(req,timeout=60));break
        except Exception as e: time.sleep(5);d=None
    rows=d['results']['bindings'] if d else []
    items={}
    for r in rows:
        k=r['it']['value'];e=items.setdefault(k,dict(nome=r['itLabel']['value'],tipi=set(),sito=None,wiki=None,tutela=None))
        e['tipi'].add(r['tipoLabel']['value'])
        for f,key in (('sito','sito'),('wiki','wiki'),('tutela','tutela')):
            if f in r and not e[key]: e[key]=r[f]['value']
    L=[dict(e,tipi=sorted(e['tipi'])) for e in items.values() if not re.match(r'^Q\d+$',e['nome'])]
    skip=('frazione','località','comune','strada','via ','piazza','fiume','torrente','monte ','collina','stazione','scuola','cimitero','azienda','impresa','squadra','associazione')
    L=[e for e in L if not any(s in ' '.join(e['tipi']).lower() for s in ('frazione','località abitata','comune italiano','fermata','stazione ferroviaria','scuola','azienda','società'))]
    out[n]=L;print(n,len(L));time.sleep(1)
json.dump(out,open('wd.json','w'),ensure_ascii=False,indent=1)
