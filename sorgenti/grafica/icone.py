#!/usr/bin/env python3
"""Icone moderne dei filtri (22/11, Stefano: «icone di Ingresso, Ideale per ecc. grandi uguali, più moderne e compatte»).
Disegni a tratto (stile Lucide, licenza ISC), tutti della stessa misura, in una piastrella verde della coccarda.
Scrive sorgenti/grafica/icone.css, che applica.py mette nella pagina insieme a istituzionale.css.
Le icone si agganciano al nome del pulsante (aria-label) o al suo data-f / data-k: nessuna funzione cambia.
Dove il nome non corrisponde (per esempio in inglese) resta l'emoji di prima.
    python3 sorgenti/grafica/icone.py && python3 sorgenti/grafica/applica.py"""
import os
import urllib.parse

QUI = os.path.dirname(os.path.abspath(__file__))

# disegni 24x24 a tratto
D = {
    "biglietto": '<path d="M2 9a3 3 0 0 1 0 6v2a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-2a3 3 0 0 1 0-6V7a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2Z"/><path d="M13 5v2M13 17v2M13 11v2"/>',
    "regalo": '<rect x="3" y="8" width="18" height="4" rx="1"/><path d="M12 8v13M19 12v7a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2v-7"/><path d="M7.5 8a2.5 2.5 0 0 1 0-5C10.5 3 12 8 12 8s1.5-5 4.5-5a2.5 2.5 0 0 1 0 5"/>',
    "euro": '<path d="M4 10h12M4 14h9"/><path d="M19 6a7.7 7.7 0 0 0-5.2-2A7.9 7.9 0 0 0 6 12c0 4.4 3.5 8 7.8 8 2 0 3.8-.8 5.2-2"/>',
    "domanda": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
    "carta": '<rect x="2" y="5" width="20" height="14" rx="2"/><path d="M2 10h20M6 15h4"/>',
    "scintille": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8z"/>',
    "ombrello": '<path d="M22 12a10 10 0 0 0-20 0Z"/><path d="M12 12v8a2 2 0 0 0 4 0M12 2v1"/>',
    "montagna": '<path d="m8 3 4 8 5-5 5 15H2L8 3z"/>',
    "monumento": '<path d="M3 22h18M6 18v-7M10 18v-7M14 18v-7M18 18v-7M12 2l9 5H3z"/>',
    "borgo": '<path d="M3 21h18M5 21V8l7-5 7 5v13"/><path d="M9 21v-6h6v6"/>',
    "bandiera": '<path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1zM4 22v-7"/>',
    "orologio": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "lampo": '<path d="M13 2 3 14h9l-1 8 10-12h-9l1-8z"/>',
    "clessidra": '<path d="M5 22h14M5 2h14M17 22v-4.2a2 2 0 0 0-.6-1.4L12 12l-4.4 4.4a2 2 0 0 0-.6 1.4V22M7 2v4.2a2 2 0 0 0 .6 1.4L12 12l4.4-4.4a2 2 0 0 0 .6-1.4V2"/>',
    "segnaposto": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "griglia": '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    "occhio": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
}


def uri(nome, colore="#000"):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{colore}" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round">' + D[nome] + '</svg>')
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg, safe=" =:/'") + '")'


# pulsanti -> icona
ETICHETTE = {  # inizio del nome del pulsante (aria-label)
    "Gratis,": "regalo", "A pagamento": "euro", "Da verificare": "domanda", "Gratis con Card": "carta",
    "Se piove": "ombrello", "Panorama": "montagna", "UNESCO": "monumento", "Borghi": "borgo", "Bandiera": "bandiera",
    "Fino a 45": "lampo", "1-1,5": "orologio", "2 ore": "clessidra",
}
FBTN = {"price": "biglietto", "ideal": "scintille", "time": "orologio"}
AW = {"unesco": "monumento", "borghi": "borgo", "arancione": "bandiera"}
SEZIONI = {"g-price": "biglietto", "g-ideal": "scintille", "g-time": "orologio"}

css = ["/* generato da sorgenti/grafica/icone.py: non correggere a mano */"]

righe = []
for pre, nome in ETICHETTE.items():
    sel = f'.qc[aria-label^="{pre}"] .em'
    righe.append((sel, nome))
for k, nome in FBTN.items():
    righe.append((f'.fbtn[data-f="{k}"] .em', nome))
for k, nome in AW.items():
    righe.append((f'.aw[data-k="{k}"] .em', nome))
for k, nome in SEZIONI.items():
    righe.append((f'#qbar section:has(#{k}) h4 .em', nome))

# ogni disegno una volta sola, come variabile; poi i pulsanti la richiamano
css.append(":root{" + "".join(f"--ic-{n}:{uri(n)};" for n in sorted({n for _, n in righe})) + "}")
tutti = ",".join("html " + sel for sel, _ in righe)
css.append(tutti + "{display:inline-block!important;position:relative!important;flex:none;width:28px!important;height:28px!important;border-radius:8px!important;"
           "font-size:0!important;font-style:normal;color:transparent!important;background:var(--terra-soft)!important;"
           "padding:0!important;margin:0!important;line-height:0!important;vertical-align:middle;"
           "box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--terra) 22%,transparent)!important}")
css.append(",".join("html " + sel + "::before" for sel, _ in righe) + "{content:\"\";position:absolute;inset:0;margin:auto!important;width:16px;height:16px;background:var(--terra-ink);"
           "-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat}")
for sel, nome in righe:
    css.append(f"html {sel}{{--ic:var(--ic-{nome})}}")
# acceso: piastrella verde piena, icona bianca
def acceso(s):
    if ".fbtn" in s:
        return s.replace(" .em", '[aria-expanded="true"] .em')
    return s.replace(" .em", '[aria-pressed="true"] .em')
acc = [acceso(s) for s, _ in righe if "section" not in s]
css.append(",".join("html " + a for a in acc) + "{background:var(--terra)!important;box-shadow:none!important}")
css.append(",".join("html " + a + "::before" for a in acc) + "{background:#fff}")
# titoli del pannello del telefono: la stessa piastrella, con segnaposto, griglia e occhio al posto delle emoji
VERDE = "#225c45"
css.append("@media (max-width:759px){"
           "html #qbar .rinv-h::before,html #qbar .qlab::before{content:\"\"!important;width:30px!important;height:30px!important;border-radius:9px!important;"
           "box-shadow:inset 0 0 0 1px color-mix(in srgb,var(--terra) 22%,transparent)!important;background-color:var(--terra-soft)!important;"
           "background-position:center!important;background-size:17px!important;background-repeat:no-repeat!important}"
           f"html #qbar .fsec:has(.mlab) .rinv-h::before{{background-image:{uri('segnaposto', VERDE)}!important}}"
           f"html #qbar .fsec:has(.aggr) .rinv-h::before{{background-image:{uri('griglia', VERDE)}!important}}"
           f"html #qbar .qlab::before{{background-image:{uri('occhio', VERDE)}!important}}"
           "html #qbar h4 .em{width:30px!important;height:30px!important;border-radius:9px!important}"
           "html #qbar h4 .em::before{width:17px!important;height:17px!important}"
           "html #qbar .qchips .qc .em{display:inline-block!important}"
           "}")
open(os.path.join(QUI, "icone.css"), "w", encoding="utf-8").write("\n".join(css) + "\n")
print("icone.css:", len(righe), "pulsanti con icona")
