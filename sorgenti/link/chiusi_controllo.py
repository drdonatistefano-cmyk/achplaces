"""21/11/2026 controllo dei luoghi segnati CHIUSI (richiesta di Stefano: verificare le schede). Per ogni luogo legge le
pagine delle sue fonti (sorgenti/link/chiusi_input.json) e annota SOLO: codice HTTP e quali parole compaiono
(chiusura / riapertura / anni). Nessun testo delle pagine viene salvato. Scrive sorgenti/link/chiusi_esito.json.
I casi senza piu' parole di chiusura sono candidati «forse ha riaperto», da verificare a mano prima di cambiare la scheda."""
import json, os, re, requests, html
QUI = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(QUI, "chiusi_input.json")))
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36 AchPlacesGuide (controllo chiusure)"
CH = re.compile(r"temporaneamente chius|momentaneamente chius|attualmente chius|chius[oa] (?:al pubblico|per|fino|dal|tutti)|non (?:è )?(?:visitabile|agibile|accessibile)|inagibil|in restauro|chiusura (?:temporanea|straordinaria)|temporarily closed|closed for|currently closed|sospes[oa]", re.I)
RI = re.compile(r"riapert[oa]|riapre|riaprir|riapertura|ha riaperto|reopen|nuovamente (?:visitabile|aperto)|torna visitabile", re.I)
OR = re.compile(r"orari(?:o)? (?:di apertura|di visita)|opening hours|aperto (?:dal|tutti|da )|biglietti|tickets", re.I)
out = {}
for x in L:
    r_ = []
    for u in x["u"]:
        try:
            r = S.get(u, timeout=30); t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", r.text, flags=re.S | re.I)
            t = html.unescape(re.sub(r"<[^>]+>", " ", t))
            anni = sorted(set(re.findall(r"\b(202[4-7])\b", t)))
            r_.append([u, r.status_code, len(CH.findall(t)), len(RI.findall(t)), len(OR.findall(t)), anni, len(t)])
        except Exception as e:
            r_.append([u, 0, 0, 0, 0, [], type(e).__name__])
    out[x["id"]] = r_
json.dump(out, open(os.path.join(QUI, "chiusi_esito.json"), "w"), ensure_ascii=False, indent=0)
print(len(out), "luoghi;", sum(1 for v in out.values() if v and all(a[1] == 200 and a[2] == 0 for a in v)), "senza parole di chiusura in nessuna fonte")
