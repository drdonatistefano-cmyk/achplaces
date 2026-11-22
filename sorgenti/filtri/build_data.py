import os
import json,glob,re,collections
_M=json.load(open('/home/claude/achs-places-guide/manifest.json'))
d=json.load(open('/home/claude/achs-places-guide/'+_M['dati']))
import sys as _s9; _s9.path.insert(0,'/home/claude/achs-places-guide'); from leggi_dati import righe as _righe9; d = _righe9(d)   # 9/11: dati per colonne
if 'dz' in d:  # 8/11: dati con dizionari (stessa decodifica di DECODIFICA nella Guida)
    import unicodedata as _ud
    def _slug40(s):
        s=''.join(ch for ch in _ud.normalize('NFD',s) if not _ud.combining(ch)).lower()
        return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:40].rstrip('-')
    _Z=d['dz']
    for _c in d['c']:
        for _k in ('regione','provName','provKind','verified'): _c[_k]=_Z[_k][_c[_k]]
        for a in _c['places']:
            if a[0]==0: a[0]=_slug40(a[1])
            a[3]=_Z['sub'][a[3]];a[7]=_Z['t'][a[7]]
_DET={};_CDET={}
for _n in _M.get('det',{}).values():
    for _sl,_ps in json.load(open('/home/claude/achs-places-guide/'+_n)).items():
        for _id,_x in _ps.items():
            if _id=='_c': _CDET[_sl]=_x   # 9/11: lede, avvisi e fonti del comune nei file per provincia
            else: _DET[_id]=_x
for _c in d['c']:
    for _k,_v in _CDET.get(_c['slug'],{}).items(): _c.setdefault(_k,_v)
_CK=["storia","musei","sacro","natura","locale"]
for _c in d['c']:
    _np=[]
    for a in _c['places']:
        if isinstance(a,dict): _np.append(a);continue
        _id=_c['slug']+'--'+a[0];f=a[5];x=_DET.get(_id,{})
        o=dict(id=_id,name=a[1],cat=_CK[a[2]],sub=a[3],desc=a[4] or x.get('desc',''),free=True if 'F' in f else False if 'P' in f else None,card='c' in f,unesco='u' in f,view='v' in f,indoor='i' in f,status=a[6] or 'ok',t=a[7],r=a[8],address=x.get('address',''),price=x.get('price',''),duration=x.get('duration',''))
        if len(a)>9: o.update(a[9])
        _np.append(o)
    _c['places']=_np
R=lambda s:re.compile(s,re.I)
ARCH=[('Preistoria',R(r'preistor|paleolit|neolit|età del (bronzo|ferro)|incisioni rupestri|rupestr|palafitt|dolmen|menhir|neanderthal')),
('Nuragici',R(r'nurag|tomba dei giganti|tombe dei giganti|pozzo sacro|domus de janas')),
('Etruschi',R(r'etrusc')),('Greci',R(r'\bgrec|magna grecia|ellenist')),('Fenici',R(r'fenic|punic')),
('Italici',R(r'sannit|messap|picen|\bvolsc|camun|dauni|celt|\bitalic')),
('Romani',R(r'roman|anfiteatr|domus|\bforo\b|augusto|imperial')),
('Tardoantichi',R(r'paleocrist|bizantin|longobard|tardoantic|catacomb')),('Medievali',R(r'medieval|castrum'))]
def T(p):
    t=(p['name']+' '+p['desc']).lower(); s=p['sub']; c=p['cat']
    has=lambda r: re.search(r,t)
    if s=='Archeologia':
        return 'arch',[k for k,r in ARCH if r.search(t)] or ['Altro']
    if c=='storia':
        if s=='Castelli e fortezze': return 'mon',['Fortezze' if has(r'fort|rocca|cittadella|bastion') and not has(r'castell') else 'Castelli']+(['Mura'] if has(r'\bmura|porta ') else [])
        if s=='Palazzi e ville': return 'mon',['Ville' if has(r'^villa|\bvilla ') else 'Palazzi']
        if s=='Piazze e centro storico': return 'mon',['Piazze' if has(r'piazza') else 'Centri']+(['Portici'] if has(r'portic') else [])
        if s=='Portici UNESCO': return 'mon',['Portici']
        if s=='Monumenti e memoriali':
            if has(r'\bponte'): return 'mon',['Ponti']
            if has(r'fontan'): return 'mon',['Fontane']
            if has(r'memorial|caduti|sacrario|guerra|resistenza|shoah'): return 'mon',['Memoriali']
            if has(r'\barco|porta '): return 'mon',['Mura']
            return 'mon',['Monumenti']
        return 'mon',[{'Borghi':'Borghi','Torri':'Torri','Teatri storici':'Teatri','Borghi abbandonati':'Abbandonati'}.get(s,'Monumenti')]
    if c=='sacro':
        if s=='Chiese e pievi':
            for r,k in [(r'oratori','Oratori'),(r'\bpieve','Pievi'),(r'battister','Battisteri'),(r'sinagog','Sinagoghe')]:
                if has(r): return 'sacro',[k]
            return 'sacro',['Chiese']
        if s=='Abbazie e monasteri': return 'sacro',['Conventi' if has(r'convent') and not has(r'abbazi') else 'Abbazie']
        if s=='Santuari': return 'sacro',['Monti sacri' if has(r'sacro monte') else 'Santuari']
        return 'sacro',[{'Cattedrali e duomi':'Duomi','Basiliche':'Basiliche','Complessi monumentali':'Complessi','Cimiteri monumentali':'Cimiteri'}.get(s,'Chiese')]
    if c=='musei':
        out=[]
        if s=='Tematici':
            for r,k in [(r'diocesan|arte sacra','Diocesani'),(r'etnograf|civiltà contadina|tradizion','Etnografici'),(r'militar|guerra|armi','Militari'),(r'industria|tecnic|ferrovi|\bauto|moto|macchin','Tecnica')]:
                if has(r): out=[k];break
            out=out or ['Tematici']
        else: out=[{'Arte antica':'Pittura','Arte moderna':'Moderna','Archeologici':'Archeologici','Case museo':'Dimore','Scienza e università':'Scienza','Storia della città':'Storia'}.get(s,'Tematici')]
        if s in('Arte antica','Arte moderna') or has(r'pittur|pittor|dipint|pinacotec|quadr|tele |affresc|tela'): out.append('Pittura')
        if has(r'ceramic|maiolic|porcellan|terracott'): out.append('Ceramica')
        return 'musei',list(dict.fromkeys(out))
    if c=='natura':
        if s=='Parchi e riserve naturali': return 'nat',['Riserve' if has(r'riserva|oasi') and not has(r'parco') else 'Parchi']
        if s=='Laghi e fiumi': return 'nat',['Cascate' if has(r'cascat') else ('Laghi' if has(r'lago|laghi') else 'Fiumi')]
        if s=='Grotte e geositi': return 'nat',['Grotte' if has(r'grott') else 'Geositi']
        if s=='Montagna': return 'nat',['Vulcani' if has(r'vulcan|etna|vesuvio') else 'Montagna']
        if s=='Giardini botanici': return 'nat',['Orti' if has(r'orto botanic') else 'Giardini']
        return 'nat',[{'Parchi urbani':'Giardini','Colline e sentieri':'Sentieri',"Paesaggi e zone d'interesse":'Panorami','Mare e spiagge':'Spiagge'}.get(s,'Panorami')]
    out=[{'Mercati storici':'Mercati','Terme':'Terme','Enogastronomia':'Sapori','Artigianato':'Botteghe','Motori':'Motori','Angoli nascosti':'Curiosità'}.get(s,'Curiosità')]
    if has(r'ceramic|maiolic'): out.append('Ceramica')
    return 'trad',out
C=[];P=[]
import subprocess
BO=json.loads(subprocess.check_output(['node','-e',"const fs=require('fs');eval(fs.readFileSync('/home/claude/achs-places-guide/data/places-bologna.js','utf8').replace('const PLACES','globalThis.PLACES'));console.log(JSON.stringify(PLACES))"]))
C.append(['Bologna','Bologna','emilia-romagna','uc','','bologna-bo',44.4939,11.3428])
for p in BO:
    g,subs=T(p)
    f=('u' if p.get('unesco') else '')+('g' if p.get('free') else '')+('i' if p.get('indoor') else '')+('v' if p.get('view') else '')
    P.append([p['name'],0,g,subs,f,p['desc'],p.get('address',''),p.get('price',''),p.get('duration','')])
for c in d['c']:
    ci=len(C)
    aw=c.get('aw') or []
    C.append([c['name'],c.get('provName') or c['prov'],c['regione'],''.join(x[0] for x in aw),(c.get('lede') or '')[:240],c['slug'],c.get('lat'),c.get('lng')])
    for p in c.get('places',[]):
        g,subs=T(p)
        f=('u' if p.get('unesco') else '')+('g' if p.get('free') else '')+('i' if p.get('indoor') else '')+('v' if p.get('view') else '')+('b' if 'borghi' in aw else '')+('a' if 'arancione' in aw else '')
        P.append([p['name'],ci,g,subs,f,p['desc'],p.get('address',''),p.get('price',''),p.get('duration','')])
print(collections.Counter(s for p in P if p[2]=='musei' for s in p[3]))
import hashlib,glob as _g
T=[[x[5],x[6]] for x in P]
for x in P: x[5]='';x[6]=''
L=[c[4] for c in C]
for c in C: c[4]=''
S7=sorted(set(x[7] for x in P));S8=sorted(set(x[8] for x in P))
for x in P: x[7]=S7.index(x[7]);x[8]=S8.index(x[8])
# 10/11/2026: testi a righe (2.000 luoghi per riga, ultima riga = presentazioni dei comuni), lette una alla volta nel telefono
_tj='\n'.join([json.dumps(T[i:i+2000],ensure_ascii=False,separators=(',',':')) for i in range(0,len(T),2000)]+[json.dumps(L,ensure_ascii=False,separators=(',',':'))])
_tn='testi.'+hashlib.md5(_tj.encode()).hexdigest()[:10]+'.json'
for f in _g.glob('/home/claude/achs-places-guide/testi.*.json'):
    if not f.endswith(_tn): os.remove(f)
open('/home/claude/achs-places-guide/'+_tn,'w').write(_tj)
import shutil;os.makedirs('/home/claude/proto5',exist_ok=True);shutil.copy('/home/claude/achs-places-guide/'+_tn,'/home/claude/proto5/'+_tn)
open('/home/claude/proto/d2.js','w').write('const TESTI="'+_tn+'";\nconst S7='+json.dumps(S7,ensure_ascii=False)+';\nconst S8='+json.dumps(S8,ensure_ascii=False)+';\nconst C='+json.dumps(C,ensure_ascii=False,separators=(',',':'))+';\nconst P='+json.dumps(P,ensure_ascii=False,separators=(',',':'))+';\n')
import os;print(os.path.getsize('/home/claude/proto/d2.js'),set(x for c in d['c'] for x in (c.get('aw') or [])))
