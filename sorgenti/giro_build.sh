#!/bin/sh
# Costruzione completa dopo ogni giro: guida, abbinamento Tiqets (ripete la costruzione se trova luoghi nuovi), pagina Luoghi, foto.
set -e
cd /home/claude/achs-places-guide
python3 build.py 2>&1 | grep -v "^  W"
cp data/tiqets.json /tmp/tq_old.json 2>/dev/null || echo '{}' > /tmp/tq_old.json
python3 tiqets_abbina.py
if ! cmp -s data/tiqets.json /tmp/tq_old.json; then python3 build.py 2>&1 | grep -v "^  W" | tail -1; fi
/home/claude/proto/mkfiltri.sh | tail -1
python3 foto_build.py | tail -1
python3 foto_split.py | tail -2
python3 esplodi_foto.py | tail -1
