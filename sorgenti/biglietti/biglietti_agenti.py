#!/usr/bin/env python3
"""11/11/2026: raccoglie gli esiti delle ricerche dei biglietti (bozze/bigl/esito-*.txt) in data/biglietti_agenti.json.
Riga: id | biglietti | orari | ingresso | nota. Tiene solo indirizzi https, scarta portali generici e campi '-'."""
import glob, json, re
PORT = re.compile(r'italia\.it|tripadvisor|google\.|visit[a-z]*\.(com|it|info)|turismo|booking\.com|getyourguide|tiqets|viator|musement', re.I)
out = {}
for f in sorted(glob.glob('/home/claude/bozze/bigl/esito-*.txt')):
    for r in open(f, encoding='utf-8'):
        c = [x.strip() for x in r.split('|')]
        if len(c) < 4 or '--' not in c[0]: continue
        e = {}
        for k, v in (('tk', c[1]), ('hr', c[2])):
            if v.startswith('https://') and not PORT.search(v): e[k] = v
        if c[3].lower().startswith('gratis'): e['free'] = True
        elif c[3].lower().startswith('pagamento'): e['free'] = False
        if len(c) > 4 and c[4]: e['nota'] = c[4][:120]
        if e: out[c[0]] = e
json.dump(out, open('/home/claude/achs-places-guide/data/biglietti_agenti.json', 'w'), ensure_ascii=False, indent=0, sort_keys=True)
print('luoghi', len(out), 'biglietti', sum(1 for v in out.values() if 'tk' in v), 'orari', sum(1 for v in out.values() if 'hr' in v), 'gratis', sum(1 for v in out.values() if v.get('free') is True))
