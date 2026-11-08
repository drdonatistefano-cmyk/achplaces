# Ach's Places Guide

Luoghi da visitare in Italia, comune per comune, con fonti ufficiali.
Sito: https://achplaces.com

## Struttura
- **Cartella principale:** il sito pubblicato, identico all'artefatto principale su claude.ai.
  - `index.html`: la guida.
  - `filtri.html`: la pagina «Luoghi».
  - `manifest.json`: elenca i file di dati con il loro hash.
  - `dati.*.json`, `meta.*.json`, `testi.*.json`, `det.<provincia>.*.json`: i dati.
  - `CNAME`: il dominio achplaces.com.
- **`sorgenti/`:** tutto ciò che serve a ricostruire la guida.
  - `data/`: spec dei comuni (`spec-<sigla>.txt`), archivio MiC, province, punteggi, registri.
  - `build.py` + `check.py` + `template.html`: costruzione e controllo di qualità.
  - `proto/`: generazione della pagina «Luoghi» (`mkfiltri.sh`).
  - `tools_coda.py`: coda dei comuni da fare.
  - `test_pagina.py`: test automatico della pagina.
  - `regole/`: regole di lavoro e metodo delle fonti.

## Ricostruire
```
cd sorgenti && python3 build.py && proto/mkfiltri.sh
```
Gli script di `proto/` usano percorsi assoluti dell'ambiente di lavoro (/home/claude/...): vanno adattati se si lavora altrove.

Nessun dato di Google: Google compare solo come link (Maps, Immagini).
