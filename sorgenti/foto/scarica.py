"""Scarica a ritmo lento le miniature (upload.wikimedia.org) dei luoghi abbinati in foto2.json che non hanno ancora l'immagine.
Uso: python3 scarica.py [minuti_massimi]"""
import json, os, sys, time, hashlib, urllib.parse, subprocess
from PIL import Image
F = '/home/claude/foto/'
UA = 'AchsPlacesGuide/0.1 (guida turistica non commerciale; https://claude.ai/artifact/UXN4Ykm771EoLEvJAifppr)'
CF = F + 'foto2.json'
LIM = time.time() + 60 * float(sys.argv[1] if len(sys.argv) > 1 else 600)
cache = json.load(open(CF))
def salva():
    json.dump(cache, open(CF + '.tmp', 'w'), ensure_ascii=False); os.replace(CF + '.tmp', CF)
def slug40(s):
    import re, unicodedata
    s = unicodedata.normalize('NFD', s.lower()); s = ''.join(c for c in s if not unicodedata.combining(c))
    return re.sub(r'[^a-z0-9]+', '-', s).strip('-')[:40]
def thumb(fn):
    n = fn.replace(' ', '_'); h = hashlib.md5(n.encode()).hexdigest(); q = urllib.parse.quote(n)
    t = f'https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/250px-{q}'
    if n.lower().endswith(('.tif', '.tiff', '.pdf', '.djvu')): t += '.jpg'
    return t
coda = [p for p, r in cache.items() if r.get('file') and 'img' not in r and not r.get('ko')]
print('da scaricare', len(coda), flush=True)
pausa, ok, n = 1.2, 0, 0
for p in coda:
    if time.time() > LIM: break
    r = cache[p]; url = thumb(r['file']); code = ''
    for k in range(6):
        time.sleep(pausa)
        code = subprocess.run(['curl', '-sL', '--max-time', '40', '-A', UA, '-o', F + 'tmp3', '-w', '%{http_code}', url], capture_output=True, text=True).stdout
        if code == '200': pausa = max(1.0, pausa * 0.9); break
        if code == '404': break
        pausa = min(20, pausa * 1.6); time.sleep(5 + 10 * k)
    n += 1
    if code != '200':
        if code == '404': r['ko'] = 404
        continue
    try:
        im = Image.open(F + 'tmp3').convert('RGB'); w, h = im.size; s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((168, 168), Image.LANCZOS)
        fn = slug40(p.replace('--', '-'))[:40] + '-' + hashlib.md5(p.encode()).hexdigest()[:6] + '.webp'
        im.save(F + 'img/' + fn, 'WEBP', quality=72, method=6)
        r['img'] = fn; r['c'] = '#%02x%02x%02x' % im.resize((1, 1)).getpixel((0, 0))
        r['u'] = 'https://commons.wikimedia.org/wiki/File:' + urllib.parse.quote(r['file'].replace(' ', '_'))
        ok += 1
    except Exception:
        r['ko'] = 'img'
    if n % 20 == 0:
        salva(); print('scaricate', ok, 'su', n, 'pausa %.1fs' % pausa, flush=True)
salva(); print('FINE scaricate', ok, 'su', n, flush=True)
