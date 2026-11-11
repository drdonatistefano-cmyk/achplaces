#!/bin/sh
# dopo ogni build della Guida: rigenera la pagina Filtri con i dati aggiornati
set -e
cd /home/claude/proto
python3 build_data.py >/dev/null
python3 mk6.py && python3 mk7.py && python3 mk8.py && python3 mk9.py && python3 mk10.py && python3 mk11.py && python3 mk12.py && python3 mk13.py && python3 mk14.py && python3 mk16.py
python3 mk15.py
python3 mk17.py
python3 mk18.py
python3 mk19.py
python3 mk20.py
python3 mk21.py
python3 mk22.py
python3 mk23.py
cp /home/claude/achs-places-guide/filtri.html /home/claude/proto5/index.html
echo filtri.html ok
