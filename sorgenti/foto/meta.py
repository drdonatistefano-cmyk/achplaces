"""Completa autore e licenza (API di Commons, lotti di 50) per le foto scaricate che non li hanno.
Sui 429 aspetta a lungo. Uso: python3 meta.py [minuti_massimi]"""
import json, os, sys, time, re, html, urllib.parse, subprocess
F = '/home/claude/foto/'
UA = 'AchsPlacesGuide/0.1 (guida turistica non commerciale; https://claude.ai/artifact/UXN4Ykm771EoLEvJAifppr)'
CF = F + 'foto2.json'
LIM = time.time() + 60 * float(sys.argv[1] if len(sys.argv) > 1 else 600)
cache = json.load(open(CF))
def salva():
    json.dump(cache, open(CF + '.tmp', 'w'), ensure_ascii=False); os.replace(CF + '.tmp', CF)
def pulisci(s):
    s = re.sub(r'<[^>]+>', '', s or ''); s = html.unescape(s); return re.sub(r'\s+', ' ', s).strip()[:120]
coda = [p for p, r in cache.items() if r.get('img') and not r.get('l')]
per = {}
for p in coda: per.setdefault(cache[p]['file'].replace('_', ' '), []).append(p)
files = list(per)
print('foto senza licenza', len(coda), flush=True)
fatti = 0; attesa = 60
for i in range(0, len(files), 50):
    if time.time() > LIM: break
    lotto = files[i:i + 50]
    url = ('https://commons.wikimedia.org/w/api.php?action=query&format=json&formatversion=2&prop=imageinfo&iiprop=extmetadata'
           '&iiextmetadatafilter=Artist|LicenseShortName|UsageTerms&titles=' + urllib.parse.quote('|'.join('File:' + f for f in lotto)))
    while time.time() < LIM:
        r = subprocess.run(['curl', '-s', '-w', '\n%{http_code}', '--max-time', '60', '-A', UA, url], capture_output=True, text=True).stdout
        body, _, code = r.rpartition('\n')
        if code == '200': attesa = 60; break
        print('Commons', code, 'aspetto', attesa, 's', flush=True); time.sleep(attesa); attesa = min(900, attesa * 2)
    else:
        break
    j = json.loads(body)
    norm = {x['to']: x['from'] for x in j['query'].get('normalized', [])}
    for pg in j['query']['pages']:
        t = pg['title']; orig = norm.get(t, t)[5:]
        ii = (pg.get('imageinfo') or [{}])[0].get('extmetadata', {})
        lic = pulisci(ii.get('LicenseShortName', {}).get('value')); aut = pulisci(ii.get('Artist', {}).get('value'))
        for key in (orig, t[5:]):
            for p in per.get(key.replace('_', ' '), []):
                if lic: cache[p]['l'] = lic; cache[p]['a'] = aut or 'vedi pagina del file'; fatti += 1
    salva(); print('lotto', i // 50 + 1, 'licenze', fatti, flush=True); time.sleep(3)
salva(); print('FINE licenze aggiunte', fatti, flush=True)
