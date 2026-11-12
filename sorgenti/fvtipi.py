"""12/11/2026: tipi della pagina Luoghi (stesse regole di proto/build_data.py e di fvTag in fv.js), usati anche dalla Guida."""
import re
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
