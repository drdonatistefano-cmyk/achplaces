#!/bin/bash
# 11/11/2026: copia la costruzione locale nel repository achplaces (sito + sorgenti) e fa commit e push.
set -e
L=/home/claude/achs-places-guide; R=/home/claude/achplaces
cd $R; git pull -q
for f in $(ls -p | grep -v / | grep -vE '^(CNAME|README.md|pagine.css|robots.txt|sitemap.*xml)$'); do [ -e $L/$f ] || git rm -q $f; done
cd $L; cp index.html filtri.html manifest.json $(ls | grep -E '^(cerca|cr\.[a-z]{2}|dati|det\.[a-z]{2}|fonti|foto|fotom\.[a-z]{2}|fotom|meta|testi|mappa|mappan)\.[0-9a-f]{10}\.json$|^luoghi\.[0-9a-f]{10}\.js$') $R/
cd $R; cp -r $L/f/. f/; comm -23 <(ls f|sort) <(ls $L/f|sort) | sed 's#^#f/#' | xargs -r git rm -q
cp $L/build.py $L/template.html $L/foto_build.py $L/biglietti_agenti.py $L/biglietti_unisci.py $L/sync_repo.sh $L/fvtipi.py $L/mappa_build.py $L/mappa_tpl.html sorgenti/; cp $L/data/italia_geo.json sorgenti/data/
cp $L/data/biglietti_agenti.json $L/data/biglietti.json $L/data/verifica_link.json $L/data/link_correzioni.json $L/data/wiki.json sorgenti/data/
cp /home/claude/proto/mk2[0-9].py /home/claude/proto/mkfiltri.sh sorgenti/filtri/
git add -A .
git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01ACcrpvVomkgGZtxFEtwykb"
git push -q origin main; git log --oneline -1
