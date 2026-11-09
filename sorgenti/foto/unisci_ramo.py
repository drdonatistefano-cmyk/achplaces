"""Porta in foto2.json le foto scaricate da GitHub Actions (ramo «foto» del repository achplaces)."""
import json, os, shutil, subprocess
F = '/home/claude/foto/'; R = '/home/claude/foto-ramo/'
if os.path.isdir(R + '.git'): subprocess.run(['git', '-C', R, 'fetch', '-q', '--depth', '1', 'origin', 'foto'], check=True); subprocess.run(['git', '-C', R, 'reset', '-q', '--hard', 'FETCH_HEAD'], check=True)
else: subprocess.run(['git', 'clone', '-q', '--depth', '1', '-b', 'foto', 'https://github.com/drdonatistefano-cmyk/achplaces', R], check=True)
meta = json.load(open(R + 'meta.json')); c = json.load(open(F + 'foto2.json')); n = 0
for p, v in meta.items():
    img, a, l, u, col = v[:5]
    r = c.get(p)
    if r is None or not os.path.exists(R + 'img/' + img): continue
    shutil.copy2(R + 'img/' + img, F + 'img/' + img)
    r.update({'img': img, 'a': a, 'l': l, 'u': u, 'c': col})
    if len(v) > 5: r['file'] = v[5]; r['via'] = v[6]
    n += 1
json.dump(c, open(F + 'foto2.json.tmp', 'w'), ensure_ascii=False); os.replace(F + 'foto2.json.tmp', F + 'foto2.json')
print('dal ramo foto:', n)
