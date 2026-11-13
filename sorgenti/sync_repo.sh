#!/bin/bash
# 11/11/2026: copia la costruzione locale nel repository achplaces (sito + sorgenti) e fa commit e push.
set -e
L=/home/claude/achs-places-guide; R=/home/claude/achplaces
cd $R; git pull -q --rebase
# 13/11: se un'altra sessione ha cambiato le sorgenti che copio (mappa_tpl.html, template.html, build.py...) dopo l'ultima mia pubblicazione, mi fermo: prima vanno riprese in locale
U=$(cat $L/.ultimo_sync 2>/dev/null); if [ -n "$U" ]; then for f in $(git diff --name-only $U HEAD -- sorgenti/ | sed 's#^sorgenti/##'); do [ -e "$L/$f" ] && ! cmp -s "sorgenti/$f" "$L/$f" && { echo "FERMO: sorgenti/$f cambiato da altri dopo $U: riprenderlo in locale e unire le modifiche"; exit 1; }; done; fi
for f in $(ls -p | grep -v / | grep -vE '^(CNAME|README.md|pagine.css|robots.txt|sitemap.*xml|statistiche.html)$'); do [ -e $L/$f ] || git rm -q $f; done
cd $L; cp index.html filtri.html manifest.json $(ls | grep -E '^(cerca|cr\.[a-z]{2}|dati|det\.[a-z]{2}|fonti|foto|fotom\.[a-z]{2}|fotom|meta|testi|mappa|mappan)\.[0-9a-f]{10}\.json$|^luoghi\.[0-9a-f]{10}\.js$|^en\.([a-z]{2}\.|ui\.)?[0-9a-f]{10}\.json$|^en\.[0-9a-f]{10}\.js$') $R/
cd $R; cp -r $L/f/. f/; comm -23 <(ls f|sort) <(ls $L/f|sort) | sed 's#^#f/#' | xargs -r git rm -q
cp $L/build.py $L/template.html $L/foto_build.py $L/biglietti_agenti.py $L/biglietti_unisci.py $L/sync_repo.sh $L/fvtipi.py $L/mappa_build.py $L/mappa_tpl.html sorgenti/; cp $L/data/italia_geo.json sorgenti/data/
cp $L/sw.js $R/sw.js; mkdir -p $R/font && cp $L/font/* $R/font/; mkdir -p sorgenti/traduci; cp $L/traduci/estrai.py $L/traduci/traduci.py $L/traduci/en_build.py $L/traduci/en_motore.js $L/traduci/en_diz.json $L/traduci/ui_it.json sorgenti/traduci/ 2>/dev/null; cmp -s $L/traduci/testi_it.jsonl sorgenti/traduci/testi_it.jsonl || cp $L/traduci/testi_it.jsonl sorgenti/traduci/
cp $L/data/biglietti_agenti.json $L/data/biglietti.json $L/data/verifica_link.json $L/data/link_correzioni.json $L/data/wiki.json sorgenti/data/
cp /home/claude/proto/mk2[0-9].py /home/claude/proto/mkfiltri.sh sorgenti/filtri/
git add -A .
# Regola 12 (coordinamento/REGOLE.md): i file degli altri non si cancellano mai
for f in statistiche.html CNAME robots.txt $(git ls-files 'sitemap*.xml'); do
  if git diff --cached --name-status | grep -qP "^D\t$f$"; then git reset -q HEAD -- "$f"; git checkout HEAD -- "$f"; echo "ripristinato $f"; fi
done
git status --short | grep '^D ' && { echo "ATTENZIONE: cancellazioni nel commit, controllare"; git diff --cached --name-status | grep '^D' | head; }
git commit -q -m "$1

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01ACcrpvVomkgGZtxFEtwykb"
git pull -q --rebase; for f in statistiche.html CNAME robots.txt; do [ -e "$f" ] || { echo "MANCA $f: non pubblico"; exit 1; }; done
git push -q origin main && git rev-parse HEAD > $L/.ultimo_sync; git log --oneline -1
