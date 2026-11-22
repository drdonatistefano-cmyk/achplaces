"""11/11/2026: verifica degli indirizzi biglietti che le ricerche non hanno potuto aprire (righe «?»).
Per ognuno: codice HTTP, indirizzo finale, titolo e se la pagina parla di biglietti/orari.
Scrive out/verifica.json. Gira su GitHub Actions a mano. Gratuito."""
import json, os, re, requests, urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
QUI = os.path.dirname(os.path.abspath(__file__))
H = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1', 'Accept-Language': 'it-IT,it;q=0.9'}
out = {}
for u in [l.strip() for l in open(os.path.join(QUI, 'verifica.txt')) if l.strip()]:
    try:
        r = requests.get(u, headers=H, timeout=25, verify=False, allow_redirects=True)
        t = r.text[:400000].lower()
        tit = re.search(r'<title[^>]*>(.*?)</title>', t, re.S)
        out[u] = {'c': r.status_code, 'f': r.url, 't': (tit.group(1).strip()[:150] if tit else ''),
                  'bigl': any(k in t for k in ('bigliett', 'ticket', 'acquista', 'prenota')),
                  'orari': any(k in t for k in ('orari', 'opening hours', 'apertura'))}
    except Exception as e:
        out[u] = {'c': 0, 'e': str(e)[:150]}
os.makedirs('out', exist_ok=True)
json.dump(out, open('out/verifica.json', 'w'), ensure_ascii=False, indent=1)
