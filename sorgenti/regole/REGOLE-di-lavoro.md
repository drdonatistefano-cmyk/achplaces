# Ach's Places Guide: regole di lavoro (vincolanti, dal 7/11/2026)

## 0. Lavoro continuo senza Stefano
- Alla fine di ogni turno di lavoro Claude programma da solo, con send_later, un messaggio nella stessa sessione dopo circa 2 minuti: «AUTO: continua dalla coda».
- In questo modo il lavoro prosegue anche di notte, senza che Stefano scriva nulla.
- Ogni turno lavora sulla coda (sezione 6), aggiorna lo «Stato» e riprogramma il turno successivo.
- Ci si ferma solo quando la coda è finita. A quel punto si scrive a Stefano la richiesta di pubblicazione e non si riprogramma più.

## 1. Criteri identici ovunque: TUTTE le 20 regioni
- **Fonti di partenza, nello stesso ordine per tutti:**
  1. luoghi MiC (open data);
  2. componenti UNESCO;
  3. pagine luogo di italia.it;
  4. portale turistico regionale;
  5. schede del Touring Club;
  6. aree protette.
- **Livello 1:** tutti i capoluoghi, tutti i comuni UNESCO, Borghi e Bandiere Arancioni, tutti i comuni con almeno un luogo MiC.
- **Livello 2:** tutti gli altri comuni con almeno una fonte ufficiale.
- **Minimi:**
  - capoluogo: 25 luoghi;
  - comune premiato: 3 luoghi;
  - comune con luoghi MiC: tutti i suoi luoghi MiC, più quelli di italia.it e del portale regionale.
- **Scarti:** niente scarti per «fonte non trovata al primo tentativo».
- **UNESCO:** il simbolo «u» si mette solo ai luoghi dentro un sito del Patrimonio Mondiale. Non vale per città creative, patrimonio immateriale generico o lista propositiva. L'eccezione è Collemaggio (Perdonanza).
- **Prima della pubblicazione:** controllo di omogeneità, luoghi per comune e per provincia confrontati con l'Emilia-Romagna.

## 2. Niente domande intermedie
Si chiede a Stefano solo alla fine, per la pubblicazione.

## 3. Architettura veloce (modello: guida osterie), già pronta in locale
- **File:**
  - index.html leggero;
  - manifest.json;
  - dati.<hash>.json;
  - det.<prov>.<hash>.json, uno per provincia, caricati in sottofondo;
  - cache nel telefono (IndexedDB).
- **Pubblicazione:** con publish_files in modo «replace».

## 4. Classifica (come nella guida osterie), già pronta in locale
- **Numerazione:** «n. X» è la posizione fissa in tutta la guida, nella riga in alto della scheda. «X°» compare in nero quando ci sono filtri.
- **Punteggio:** da 0 a 100, calcolato con `punteggio()` in build.py. I segnali stanno in `data/punteggi.json`. Per Bologna i bonus arrivano dal campo `pb` dei dati.
- **Pesi:**
  - UNESCO: 30 se il bene è citato per nome, 12 se ricade solo nell'area;
  - istituto ad autonomia speciale: 12;
  - luogo MiC: 5;
  - Touring Club: 15 con due asterischi, 8 con uno, 6 se solo citato;
  - italia.it: 8;
  - «da non perdere» del portale regionale: 6;
  - visitatori MiC: fino a 12;
  - FAI Luoghi del Cuore: fino a 5;
  - natura: fino a 12;
  - chiuso: −10.

## 4b. Estetica della scheda in elenco (7/11 ore 19, richiesta di Stefano)
- Il pulsante «Apri ›» è piccolo, a pillola, e sta a destra insieme a «Foto».
- Le informazioni sono più grandi (27 px) e più complete: prezzo, UNESCO, tempo, al coperto, panorama.
- La classifica sta nella riga in alto e il nome della sottocategoria si accorcia con i puntini.
- **Aggiornamento 8/11 (approvato da Stefano):** «N°» grande a sinistra, pallino colorato della categoria in alto a destra, cornice sottile nel colore della categoria; primo tasto «Biglietti» (o «Gratis» se la gratuità è confermata).

## 5. Ricerca efficiente
- WebSearch con `allowed_domains` sui siti ufficiali.
- WebFetch con prompt brevi.
- Lavoro a blocchi per provincia.
- Vincoli sempre validi: nessun dato Google, niente Firecrawl, solo fonti ufficiali.

## 6. Coda di lavoro
1. **Segnali nazionali:**
   - ~~istituti MiC ad autonomia speciale~~ FATTO;
   - ~~beni UNESCO citati per nome~~ FATTO;
   - visitatori dei musei statali;
   - FAI;
   - Bandiere Blu, parchi nazionali, aree marine, geositi.
2. **Regioni MAI iniziate**, da portare al Livello 1 e poi al Livello 2: Piemonte, Valle d'Aosta, Liguria, Friuli-Venezia Giulia, Molise, Basilicata, Calabria.
3. **Regioni iniziate ma incomplete**, da portare al livello dell'Emilia-Romagna: Lazio (22 comuni), Toscana, Umbria, Marche, Abruzzo, Sardegna, Lombardia, Veneto, Sicilia, Campania, Puglia, Trentino-Alto Adige.
4. **Emilia-Romagna:** completare i segnali di classifica.
5. **Controllo di omogeneità**, poi il messaggio a Stefano per la pubblicazione.

## 7. Pubblicazione: «pubblica» = artefatto + repository (dall'8/11/2026, ore 16:58)
Quando Stefano scrive «pubblica», si aggiornano **entrambi**, nello stesso turno:
1. **Artefatto principale** ea278bc7-ce09-4034-ba7f-13c17f055421 (https://claude.ai/artifact/Vv3243snAW66CnSMX9nwk4), con publish_files in modo «replace».
2. **Repository GitHub drdonatistefano-cmyk/achplaces**, ramo `main` (sito achplaces.com, dominio registrato da Stefano su Cloudflare):
   - **cartella principale:** esattamente gli stessi file pubblicati nell'artefatto (index.html, manifest.json, filtri.html, dati/meta/testi/luoghi e tutti i det.*), più `CNAME` con scritto `achplaces.com` e `.nojekyll`. I vecchi file con hash diverso si cancellano, così la cartella resta identica all'artefatto;
   - **sorgenti/:** tutto ciò che serve a ricostruire la guida: `data/`, `build.py`, `check.py`, `template.html`, `tools_coda.py`, `proto/` (senza immagini di prova e copie .bak), `regole/` (questo file e metodo-e-fonti.md), `test_pagina.py`;
   - **controllo prima del push:** le impronte sha256 dei file della cartella principale devono coincidere con quelle dell'artefatto (list_files);
   - **nessun dato Google** nel repository: Google compare solo come link (Maps, Immagini);
   - commit su `main` con messaggio «Pubblicazione AAAA-MM-GG: …» e push.
- L'anteprima (dee4094c-…, UXN4…) **non** va nel repository.
- Copia locale del repository: /home/claude/achplaces (se manca: add_repo con accesso push, poi clone).

## 8. Statistiche GoatCounter (dall'8/11/2026, ore 18)
- Il contatore si chiama **achplaces** e ha il cruscotto su https://achplaces.goatcounter.com. Non usa cookie e non cambia l'aspetto della pagina.
- Conta solo le visite alle pagine, e solo quando la pagina è aperta su achplaces.com o www.achplaces.com. Sull'artefatto claude.ai non parte.
- Il codice sta in fondo a `template.html` (costante `GC`, controllo del dominio `ON_WEB`) e quindi resta a ogni «pubblica».
- Fino alla prossima «pubblica», l'index.html del repository differisce dall'artefatto solo per questo blocco. È un'eccezione voluta al controllo sha256 del §7.
- Per la guida osterie il contatore è «achdinners», sul dominio achdinners.com (lo gestisce l'altra chat).
