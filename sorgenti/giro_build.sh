#!/bin/sh
# Costruzione completa dopo ogni giro: guida, abbinamento Tiqets e GetYourGuide (ripete la costruzione se trova luoghi nuovi), pagina Luoghi, foto.
set -e
cd /home/claude/achs-places-guide
python3 build.py 2>&1 | grep -v "^  W"
cat data/tiqets.json data/gyg.json 2>/dev/null > /tmp/aff_old.txt || true
python3 tiqets_abbina.py
if [ -s /home/claude/achplaces/sorgenti/gyg/prodotti.json ]; then python3 gyg_abbina.py; fi
cat data/tiqets.json data/gyg.json 2>/dev/null > /tmp/aff_new.txt || true
if ! cmp -s /tmp/aff_new.txt /tmp/aff_old.txt; then python3 build.py 2>&1 | grep -v "^  W" | tail -1; fi
/home/claude/proto/mkfiltri.sh | tail -1
python3 foto_build.py | tail -1
python3 sorgenti/foto_split.py | tail -2
python3 sorgenti/esplodi_foto.py | tail -1
python3 sorgenti/velocizza.py | tail -1
