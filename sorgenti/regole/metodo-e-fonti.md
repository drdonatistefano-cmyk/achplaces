# Ach's Places Guide: dove trovare tutto

- **Guida pubblicata:** https://claude.ai/artifact/Vv3243snAW66CnSMX9nwk4 (v49, 7 novembre 2026)
- **Copertura v49:** 2.849 luoghi; tutti i capoluoghi di provincia presenti.
  - Emilia-Romagna e Toscana: tutte le province.
  - Capoluoghi con copertura MiC completa: Roma, Napoli, Milano, Firenze, Venezia, Palermo, Siena; da v41 Modena, Verona, Bari, Cagliari; da v42 Bergamo, Brescia, Como; da v43 tutti gli altri capoluoghi lombardi (Cremona, Mantova, Monza, Pavia, Varese, Lecco, Lodi, Sondrio); da v44 i capoluoghi laziali Viterbo, Rieti, Latina, Frosinone; da v45 i capoluoghi campani Caserta, Benevento, Avellino, Salerno; da v46 i capoluoghi pugliesi Lecce, Taranto, Brindisi, Foggia, Barletta; da v47 i capoluoghi siciliani Siracusa, Agrigento, Trapani, Messina, Ragusa, Caltanissetta, Enna; da v48 i capoluoghi sardi Sassari, Nuoro, Oristano, Carbonia.
  - Altri capoluoghi inseriti: Catania, Trento, Bolzano e tutti i capoluoghi del Veneto.
  - Novità v39-v40, tutti con copertura MiC completa: i capoluoghi di Umbria (Perugia, Terni), Marche (Ancona, Pesaro, Urbino, Macerata, Ascoli Piceno, Fermo) e Abruzzo (L'Aquila, Teramo, Pescara, Chieti).
- **Approccio "Due livelli":**
  - Livello 1, per ogni nuova provincia: il capoluogo (con inventario completo, vedi regole di completezza), i comuni con riconoscimento, i luoghi statali MiC e i grandi parchi.
  - Livello 2: tutti gli altri comuni.
- **In corso:**
  1. **Priorità dal 7/11 sera, su richiesta di Stefano:** (a) Tuscia completa: dopo v49 mancano Tuscania, Montefiascone, Civita Castellana, Acquapendente, Ronciglione, Vulci (Canino/Montalto), Orte, Soriano, Bassano in Teverina e gli altri Borghi; (b) Sardegna archeologica provincia per provincia: Su Nuraxi di Barumini, domus de janas UNESCO, nuraghi Losa, Santu Antine, Arrubiu, Palmavera, tombe dei giganti, pozzi sacri (Santa Cristina, Santa Vittoria), Tharros, Nora, Monte d'Accoddi, grandi aree naturali.
  2. Livello 2 Umbria, Marche, Abruzzo: fatti in v49 Spello, Bevagna, Montefalco, Trevi, Norcia, Castiglione del Lago, Deruta, Torgiano, Corciano, Panicale; restano gli altri Borghi e Bandiere (elenco da `data/registri.json`).
  3. Link precisi.
  - Stato v50 (base_version 1794072356-3f56): Tuscia aggiunte Tuscania, Montefiascone, Acquapendente, Ronciglione, Bassano in Teverina, Canino (Vulci), Montalto di Castro, Civita Castellana, Abbazia di San Martino al Cimino (Viterbo). Sardegna: Barumini, Paulilatino, Abbasanta, Torralba, Alghero. Prossimi in Sardegna: Orroli (Arrubiu), Serri (Santa Vittoria), Cabras (Tharros, Mont'e Prama), Pula (Nora), Sassari (Monte d'Accoddi), Arzachena (Coddu Vecchiu, Albucciu), Bonorva (Sant'Andrea Priu), Villaperuccio (Montessu), Goni (Pranu Mutteddu), Dorgali (Serra Orrios, Gorropu), Oliena (Tiscali), Baunei, La Maddalena, Stintino, Castelsardo. Fonte efficiente: WebSearch con allowed_domains sardegnaturismo.it / visitlazio.com / italia.it.

## Regole contro le schede povere (bloccanti in `check.py`)
- Minimo di luoghi per comune:
  - capoluogo: almeno 25 (salvo `minimo:` motivato, vedi punto 11);
  - comune UNESCO, Borghi più belli o Bandiera Arancione: almeno 3;
  - altri comuni: almeno 1.
- Ogni capoluogo deve avere un mercato storico, oppure `scarto: mercati | motivo`.
- Inventario ufficiale del comune (`inv:`): ogni voce deve avere una scheda o uno `scarto:` motivato.
- I bollini Borghi e Bandiere si confrontano con `data/registri.json`, che raccoglie gli elenchi ufficiali delle associazioni per regione. Prima di aggiungere una regione si crea il suo registro.
- Si cercano sempre anche i borghi abbandonati (storia → Borghi abbandonati) e i paesaggi o zone d'interesse (natura → Paesaggi e zone d'interesse).

## Regole di completezza (dal 7 novembre 2026, dopo il caso Roma)
Roma era pubblicata con 34 luoghi: il minimo fisso di 25 per capoluogo misurava la soglia, non la completezza. Da quel momento valgono queste regole.

1. **Prima l'inventario, poi le schede.** Per ogni comune l'elenco di partenza si costruisce da sette fonti, in quest'ordine:
   a. luoghi della cultura MiC del comune (open data `data/archivio/raw-mic-luoghi.csv`): fonte obbligatoria, letta in automatico da `check.py`;
   b. componenti dei siti UNESCO presenti nel comune;
   c. indice dei luoghi del portale turistico ufficiale: per le grandi città **tutte** le pagine di quartiere o rione, poi le pagine tematiche (chiese, musei, parchi, mercati);
   d. italia.it: scheda della città e pagine dei singoli luoghi;
   e. aree protette e verde pubblico storico: parchi, riserve, ville, giardini;
   f. cattedrale, basiliche e chiese con opere citate dalle fonti ufficiali;
   g. mercati storici, piazze, fontane, vie storiche, belvedere e quartieri caratteristici.
2. **Ogni voce dell'inventario finisce in una scheda o in uno scarto motivato.**
   - Lo scarto si scrive così: `scarto: DBUnico.xxx Nome | motivo`.
   - Si usa solo per motivi verificabili: chiuso, non aperto al pubblico, duplicato di un'altra scheda, sede amministrativa.
   - Le schede dichiarano l'identificativo MiC con `mic=`.
3. **Il numero di schede segue l'inventario, non una soglia.** 25 resta il minimo per i capoluoghi piccoli; per le città d'arte il riferimento è l'inventario.
4. **Controllo automatico** (`check.py`, file `data/copertura-mic.json`).
   - Per ogni comune calcola quanti luoghi MiC sono coperti.
   - Biblioteche, archivi, istituti e sedi amministrative sono esclusi in automatico.
   - Se un comune è marcato `copertura: completa`, ogni luogo MiC scoperto è un errore che blocca la pubblicazione; altrimenti è un avviso.
5. **Trasparenza per l'utente.** Finché un comune non è completo, la sua scheda mostra l'avviso "Elenco in ampliamento: la guida copre per ora X dei Y luoghi della cultura censiti dal Ministero".
6. **Ordine di lavoro nelle grandi città.** Si procede un quartiere alla volta, chiudendo ogni pagina ufficiale prima di passare alla successiva. Alla fine si confronta il risultato con l'elenco MiC e con le pagine tematiche.
7. **Abbinamento scheda-voce MiC più severo (v38).**
   - Il confronto automatico per nome ignora le parole generiche che producevano falsi "coperti": fondazione, cultura, contemporanea, moderna, raccolta, laboratorio, storia, università, permanente, nazionale, civico e simili.
   - Uno scarto conta solo se nomina l'identificativo MiC come prima parola.
   - I musei ospitati dentro un'altra scheda (per esempio le collezioni del Castello Sforzesco o i musei di Palazzo Pitti) si dichiarano con `mic=` su quella scheda.
8. **Scarti "da rivalutare".** Per i luoghi MiC minori senza informazioni di visita su fonti ufficiali si scrive esattamente questo motivo, senza inventare chiusure o orari. Questi luoghi restano nella lista di lavoro.
9. **Inserimento nei file con più comuni.**
   - `tools/addspec.py <sigla> "<Comune>"` inserisce le schede dentro il blocco del comune indicato.
   - La sigla va scritta in minuscolo: `pu`, non `PU`.
   - Nella colonna extra delle schede si usa sempre `§k`, che diventa `src=…^uff`. La forma `§§k` va usata solo nelle righe `src:` del comune: nella colonna extra blocca la build.
10. **Scarti motivati verificabili usati in v41**: luogo in un altro comune secondo il Catalogo ICCD (Balsignano → Modugno), museo chiuso dal 1990 con raccolte confluite altrove (Risorgimento di Modena), "non al momento visitabile" o "temporaneamente chiuso" quando lo dice la pagina ufficiale, sede di uffici.
11. **Minimo ridotto motivato (`minimo: N | motivo`).**
    - Un capoluogo può scendere sotto i 25 luoghi solo se ha `copertura: completa` (tutto l'inventario MiC chiuso) e un motivo scritto, di solito "ulteriori luoghi in attesa di fonti ufficiali verificate".
    - Il controllo lo segnala come avviso.
    - Casi attuali: Urbino 17, Macerata 16, Fermo 18, L'Aquila 18, Teramo 14, Pescara 14, Chieti 14, Brescia 17, Como 17, Monza 23, Pavia 20, Lodi 14, Varese 9, Lecco 9, Sondrio 9, Rieti 18, Latina 14, Frosinone 10, Caserta 11, Benevento 10, Avellino 7, Salerno 13, Lecce 13, Taranto 15, Brindisi 8, Foggia 6, Barletta 8, Siracusa 16, Agrigento 14, Trapani 10, Messina 12, Ragusa 10, Caltanissetta 9, Enna 8, Sassari 12, Nuoro 9, Oristano 10, Carbonia 5.
    - Principio: meglio una scheda corta e verificata che luoghi senza fonte.

## Dati stabili (dal 7 novembre 2026)
- Le schede non contengono cifre né orari.
  - Indicano solo gratis o a pagamento, con un link alla pagina ufficiale di biglietti e orari del gestore (`off=` nella spec).
  - Il controllo avvisa se un luogo a pagamento non ha il link al gestore e se un testo contiene un prezzo.
- Unico aggiornamento annuale, a settembre, che riguarda:
  - gli elenchi UNESCO, Borghi e Bandiere;
  - i luoghi chiusi o con avviso (`rev=AAAA-MM`, bloccante se scaduta);
  - i link ufficiali.
  Mostre temporanee e chiusure brevi non si inseriscono.
- Ogni luogo ha tre link distinti, in `data/links.json` oppure con `orari=`, `biglietti=` e `off=` nella spec:
  - pagina degli orari;
  - pagina dei biglietti o delle tariffe;
  - home del gestore.
  Se manca la pagina precisa, il link lo dichiara ("Cerca sul sito" oppure "Info sul portale turistico").

## Archivio fonti per regione (`data/archivio/`)
- `comuni-<regione>.json`
  - Regioni presenti: Emilia-Romagna, Toscana, Lombardia, Veneto, Lazio, Campania, Sardegna, Trentino-Alto Adige, Umbria, Marche, Abruzzo.
  - Per ogni comune: dati ISTAT (21/02/2026), sito istituzionale (Indice PA) e luoghi della cultura MiC.
  - Script: `tools/archivio_comuni.py`; copie dei dati grezzi in `raw-*.csv`.
- `fonti-territorio.json`: fonti nazionali, portale regionale, elenchi Borghi e Bandiere, portali provinciali.
- Fonti ufficiali usate per le grandi città:
  - italia.it e cultura.gov.it (MiC);
  - portali regionali: in-Lombardia, Visit Tuscany;
  - portali comunali: Feel Florence, YesMilano, Comune di Napoli;
  - Lombardia Beni Culturali;
  - FAI e Touring Club per la storia dei monumenti.
- Lombardia (v42-v43): mappe turistiche ufficiali "Cult City" di Regione Lombardia (in-lombardia.it, file City_Map_A3_<città>.pdf), guide comunali (Turismo Mantova, Turismo Monza, Turismo Cremona), VisitBergamo, VisitBrescia, Fondazione Brescia Musei, Lombardia Beni Culturali.
- Lazio (v44): italia.it (pagine città e luoghi), VisitLazio, cultura.gov.it e Direzione regionale Musei nazionali Lazio (Rocca Albornoz, Villa Lante, San Francesco alla Rocca, Madonna della Quercia, Castel d'Asso, Ferento), elenco musei riconosciuti della Regione Lazio (2023), FAI, pagine eventi del Comune di Frosinone. Il sito della Direzione regionale Musei Lazio non è raggiungibile via WebFetch per l'elenco generale: si usano le singole pagine trovate con WebSearch.
- Campania (v45): Reggia di Caserta (cartella stampa ufficiale), italia.it, cultura.gov.it, Soprintendenza ABAP Caserta e Benevento, Rete museale della Provincia di Benevento, Arcidiocesi di Salerno (Musei in rete), schede luoghi dell'Università di Salerno, FAI e Touring Club. italia.it/it/campania/salerno non è raggiungibile via WebFetch: si usano le pagine dei singoli luoghi.
- Puglia (v46): italia.it (pagine città e luoghi; le pagine in italiano di Barletta e Brindisi a volte vanno lette nella versione inglese), cultura.gov.it, Direzione regionale Musei nazionali Puglia (museipuglia.cultura.gov.it), MArTA (museotaranto.cultura.gov.it, pagina «Cosa vedere a Taranto»), Catalogo ICCD, ISPRA (schede musei), Università del Salento, FAI (Abbazia di Cerrate), Italy for Movies.
- Sicilia (v47): Visit Sicily (visitsicily.info, portale della Regione Siciliana: pagine «10 cose da vedere» per città), italia.it (itinerari di Siracusa, Enna, Messina; italia.it/it/sicilia/siracusa non è raggiungibile via WebFetch), cultura.gov.it, Guida di Messina dell'Università di Messina, Fondazione Zeri (Università di Bologna).
- Sardegna (v48): Sardegna Turismo (sardegnaturismo.it, portale della Regione), Sardegna Cultura (sardegnacultura.it), italia.it (itinerario di Nuoro; scheda Museo del Carbone di Carbonia).
- Fonti delle nuove regioni (v39-v40):
  - Umbria: Umbria Tourism;
  - Marche: turismo.marche.it, le pagine delle città su eventi.turismo.marche.it e la guida regionale dei musei in PDF;
  - Abruzzo: turismo.abruzzo.it, con le pagine delle città;
  - per ogni luogo statale: cultura.gov.it.
  I registri Borghi e Bandiere Arancioni delle tre regioni sono in `data/registri.json`.
- Problema noto: per Pesaro l'Indice PA riporta il sito di Monteciccardo. È un errore della fonte e non è stato corretto.

## Protocollo di ricerca
1. Elenco comuni ISTAT, fusioni comprese.
2. Registri, in quest'ordine: MiC, UNESCO, Borghi più belli, Bandiere Arancioni, parchi, portale regionale, portale provinciale, card museali.
3. Si procede comune per comune, con ricerche limitate ai siti ufficiali. Per i luoghi a pagamento si cerca "luogo + biglietto + orari + anno" sul sito del gestore.
4. Per gli avvisi si cerca "chiuso / lavori / restauro / riapertura + provincia + anno".
5. Campi obbligatori di ogni scheda:
   - categoria valida;
   - descrizione di almeno 60 caratteri;
   - perché andarci;
   - indirizzo, mai inventato: se manca il civico si scrive la località;
   - prezzo;
   - almeno una fonte ufficiale.
6. Prezzi e orari vengono solo dal gestore o da un ente pubblico, mai da blog. Nessun dettaglio storico senza fonte, nemmeno nella riga "perché andarci": se la fonte non lo dice, non si scrive.
7. Costo zero: solo ricerca web standard e WebFetch, niente Firecrawl. Google compare solo come link (Maps, Immagini); nessun dato Google viene salvato.

## Controllo qualità
- `build.py` esegue `check.py`; qualsiasi errore blocca la pubblicazione.
- Situazione v49: 0 errori e 1.852 avvisi, in gran parte luoghi MiC non ancora coperti nei comuni non completi e luoghi a pagamento senza link al gestore.

## Da fare
- Chiudere l'inventario MiC delle città ancora aperte (vedi "In corso").
- Completare i capoluoghi abruzzesi e marchigiani con minimo ridotto man mano che emergono fonti ufficiali.
- Domus di Largo Madonna delle Grazie (Teramo): da rivalutare.
- Scarti "da rivalutare" introdotti in v41-v42 (piccoli musei universitari o privati senza scheda ufficiale): 3 a Modena, 2 a Verona, 3 a Bari, 3 a Cagliari, 1 a Bergamo, 7 a Brescia, 3 a Como; in v43: 2 a Cremona, 1 a Monza, 6 a Pavia (collezioni universitarie), 3 a Varese, 4 a Lodi, 1 a Sondrio; in v44: 4 a Viterbo (Casa di Santa Rosa, Erbario della Tuscia, Museo Padre Felice Rossetti, Sala capitolare), 2 a Latina (Museo Violo, Museo sessano); in v45: 2 a Caserta, 1 a Benevento, 3 ad Avellino, 5 a Salerno; in v46: 10 a Lecce (soprattutto musei universitari), 1 a Taranto, 3 a Brindisi, 5 a Foggia (musei provinciali), 2 a Barletta; in v47: 6 a Siracusa, 3 ad Agrigento, 7 a Messina, 2 a Ragusa, 1 a Caltanissetta, 3 a Enna; in v48: 1 a Carbonia (Museo Martel).
- Lezione v49 (Viterbo): non scartare chiese e monumenti noti per mancanza di scheda trovata al primo tentativo. italia.it ha schede dei singoli luoghi in `/it/<regione>/<città>/<luogo>`, il Touring Club in `touringclub.it/destinazioni/<città>/vedere/<id>-<luogo>` (leggibili via WebFetch): cercarle sempre prima di ridurre il minimo. Viterbo passa da 23 a 33 luoghi (Santa Maria Nuova, San Sisto, Teatro dell'Unione, piazze e fontane). Ancora da cercare: Chiesa di San Francesco (Rieti), San Giovanni in Zoccoli, Santa Maria della Verità, Valle di Faul, Viterbo Sotterranea.
- Mondello e gli altri luoghi marcati "da rivalutare".
- Link precisi a orari e biglietti per i luoghi che ancora non li hanno.
- Righe `inv:` per i capoluoghi.
- Ricontrollare le 33 fonti non emerse.
- Verificare Sant'Agata Feltria tra le Bandiere Arancioni.

## Classifica (dal 7/11/2026 sera)
- `build.py` calcola `r` (0-100) per ogni luogo con `punteggio()`; la pagina assegna `rk`, la posizione in tutta la guida, e `_sel`, la posizione nella selezione quando ci sono filtri o l'ordinamento per distanza, come nella guida osterie.
- Pesi:
  - UNESCO: 30 se il bene è citato per nome nel sito, 12 se ricade solo nell'area UNESCO;
  - istituto ad autonomia speciale: 12;
  - luogo MiC: 5;
  - Touring Club: 15 con due asterischi, 8 con uno, 6 se è solo citato;
  - italia.it: 8;
  - «da non perdere» del portale regionale: 6;
  - visitatori MiC, su scala logaritmica: fino a 12;
  - FAI Luoghi del Cuore: fino a 5;
  - natura: fino a 12;
  - fonti ufficiali aggiuntive: al massimo 4 punti;
  - chiuso: −10.
- I segnali raccolti a mano vanno in `data/punteggi.json`, con chiave `slug|id`.
- Raccolta capillare da fare: beni UNESCO citati per nome, elenco degli istituti autonomi MiC, visitatori dei musei statali (dati aperti), asterischi Touring scheda per scheda, «da non perdere» dei portali, FAI, Bandiere Blu, parchi nazionali e aree marine, geositi.
- Finché questi dati mancano la classifica è provvisoria: oggi al n. 1 c'è San Paolo Maggiore e al n. 2 Carsulae.
