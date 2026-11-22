#!/usr/bin/env python3
"""11/11/2026: raccoglie gli esiti delle ricerche dei biglietti (bozze/bigl/esito-*.txt) in data/biglietti_agenti.json.
Riga: id | biglietti | orari | ingresso | nota. Tiene solo indirizzi https, scarta portali generici e campi '-'."""
import glob, json, re
PORT = re.compile(r'italia\.it|tripadvisor|google\.|visit[a-z]*\.(com|it|info)|turismo|booking\.com|getyourguide|tiqets|viator|musement', re.I)
out = {}
# Righe «?»: indirizzi che le ricerche non hanno potuto aprire, verificati poi su GitHub (data/verifica_link.json).
# Valgono solo se rispondono 200. Le schede del Ministero (cultura.gov.it/luogo/) danno orari e tariffe ma non vendono:
# vanno come orari, mai come biglietteria.
try: VER = json.load(open('/home/claude/achs-places-guide/data/verifica_link.json'))
except Exception: VER = {}
def _ok(v):
    if v.startswith('?'):
        u = v[1:].strip()
        return u if VER.get(u, {}).get('c') == 200 else ''
    return v
for f in sorted(glob.glob('/home/claude/bozze/bigl/esito-*.txt')):
    for r in open(f, encoding='utf-8'):
        c = [x.strip() for x in r.split('|')]
        if len(c) < 4 or '--' not in c[0]: continue
        e = {}
        for k, v in (('tk', _ok(c[1])), ('hr', _ok(c[2]))):
            if v.startswith('https://') and not PORT.search(v):
                if k == 'tk' and 'cultura.gov.it/luogo/' in v: e.setdefault('hr', v)
                else: e[k] = v
        if c[3].lower().startswith('gratis'): e['free'] = True
        elif c[3].lower().startswith('pagamento'): e['free'] = False
        if len(c) > 4 and c[4]: e['nota'] = c[4][:120]
        if e: out[c[0]] = e
json.dump(out, open('/home/claude/achs-places-guide/data/biglietti_agenti.json', 'w'), ensure_ascii=False, indent=0, sort_keys=True)
print('luoghi', len(out), 'biglietti', sum(1 for v in out.values() if 'tk' in v), 'orari', sum(1 for v in out.values() if 'hr' in v), 'gratis', sum(1 for v in out.values() if v.get('free') is True))
