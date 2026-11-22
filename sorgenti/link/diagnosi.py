"""15/11/2026: diagnosi dei link che il controllo settimanale non riesce ad aprire, e copie d'archivio per le pagine sparite.
1) Per ogni sito irraggiungibile: il nome esiste (DNS)? la porta 443 risponde? il certificato e' valido, scaduto, per un altro
   nome, o manca solo un intermedio (i browser lo accettano)? e in http semplice?
2) Per ogni pagina sparita (404/410/home): c'e' una copia nell'Internet Archive (API ufficiale archive.org/wayback/available)?
Scrive out/diagnosi.json. Nessun dato inventato: solo quello che rispondono i server."""
import json, os, socket, ssl, time, requests
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor
QUI = os.path.dirname(os.path.abspath(__file__))
I = json.load(open(os.path.join(QUI, "diagnosi_input.json")))
H = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Safari/604.1", "Accept-Language": "it-IT,it;q=0.9"}

def sito(host):
    r = {"host": host}
    try: r["ip"] = sorted({a[4][0] for a in socket.getaddrinfo(host, 443, proto=socket.IPPROTO_TCP)})[:3]
    except Exception as e: r["dns"] = "non esiste"; return r
    for porta in (443, 80):
        try: socket.create_connection((host, porta), timeout=12).close(); r[f"p{porta}"] = "aperta"
        except Exception as e: r[f"p{porta}"] = type(e).__name__
    if r.get("p443") == "aperta":
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((host, 443), timeout=12) as s:
                with ctx.wrap_socket(s, server_hostname=host) as t: r["tls"] = "valido"; r["ver"] = t.version()
        except ssl.SSLCertVerificationError as e: r["tls"] = "certificato: " + (e.verify_message or str(e))[:120]
        except Exception as e: r["tls"] = type(e).__name__ + ": " + str(e)[:120]
    try:
        x = requests.get("http://" + host + "/", headers=H, timeout=15, allow_redirects=True)
        r["http"] = [x.status_code, x.url[:120]]
    except Exception as e: r["http"] = [0, type(e).__name__]
    return r

hosts = sorted({urlparse(u).hostname for u in I["irraggiungibili"]})
with ThreadPoolExecutor(16) as ex: siti = {x["host"]: x for x in ex.map(sito, hosts)}
print("siti", len(siti), flush=True)

def archivio(u):
    for prova in range(3):
        try:
            j = requests.get("https://archive.org/wayback/available", params={"url": u}, timeout=30).json()
            s = (j.get("archived_snapshots") or {}).get("closest") or {}
            if s.get("available") and str(s.get("status", "200")) == "200": return u, {"url": s["url"], "data": s.get("timestamp", "")[:8]}
            return u, None
        except Exception: time.sleep(4 * (prova + 1))
    return u, "errore"
with ThreadPoolExecutor(4) as ex: arch = dict(ex.map(archivio, I["rotti"]))
print("archivio", sum(1 for v in arch.values() if isinstance(v, dict)), "su", len(arch), flush=True)
os.makedirs("out", exist_ok=True)
json.dump({"siti": siti, "archivio": arch}, open("out/diagnosi.json", "w"), ensure_ascii=False, indent=0)
