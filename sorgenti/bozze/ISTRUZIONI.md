# Istruzioni per gli assistenti della coda comuni (Ach's Places Guide)

Compito: per ogni comune assegnato scrivi una bozza `/home/claude/bozze/<Nome comune>.txt` con i luoghi da visitare. Non toccare nient'altro: niente file in /home/claude/achs-places-guide, niente build, niente pubblicazioni.

## Regole vincolanti
- **Solo fonti ufficiali**: italia.it, cultura.gov.it / musei statali (MiC), portali turistici regionali e provinciali, siti dei Comuni e delle ATL/APT, Touring Club (emiliaromagnaturismo.it/tci-itinerari ecc.), FAI, UNESCO, parchi, borghipiubelliditalia.it, bandierearancioni.it. Mai blog, giornali, Wikipedia, TripAdvisor, Google.
- **Niente Google, niente Firecrawl.** Usa WebSearch (mode "standard", con allowed_domains sui siti ufficiali quando possibile) e WebFetch con prompt brevi.
- **Mai inventare.** Ogni fatto (date, artisti, prezzi, orari) deve venire da una fonte letta. Se non trovi una fonte che descriva il luogo, NON scrivere una descrizione ricavata dal nome: metti il luogo negli scarti «da rivalutare».
- **Link solo https.**
- Ogni flag «w» (avviso) o «c» (chiuso) richiede `note=<motivo dalla fonte>` e `rev=AAAA-MM` (di norma rev=2027-01). Senza motivo dalla fonte, non mettere il flag.
- La riga `minimo:` si scrive solo se la copertura MiC è completa (tutti i luoghi MiC inseriti o scartati con motivo). Se non hai potuto verificare tutto: `copertura: parziale` e niente riga minimo.
- Minimi: capoluogo 25 luoghi; comune premiato (Borghi, Bandiera Arancione, UNESCO) 3 luoghi; comune con luoghi MiC: tutti i suoi luoghi MiC (inseriti o scartati con motivo), più quelli di italia.it e del portale regionale.
- Bollino «borghi» nell'intestazione solo se il comune è membro certificato su borghipiubelliditalia.it (non «Borgo Ospite»). «arancione» solo se Bandiera Arancione del Touring. «unesco» solo se nel comune c'è un sito del Patrimonio Mondiale.

## Dati di partenza
Luoghi MiC e premi noti del comune (ISTAT dalla coda):
```
python3 -c "import json,glob;[print(c['nome'],c['prov'],c['premi'],c['mic'],c.get('sito')) for f in glob.glob('/home/claude/achs-places-guide/data/archivio/comuni-*.json') for c in json.load(open(f))['comuni'] if c['nome']=='NOME']"
```
`mic` è una lista di [nome, codice]: ogni voce va inserita (con `mic=codice` nella riga del luogo) o messa in `scarto:` con motivo.

## Formato del file (esempio reale)
```
@ Soragna | 034036 | PR | https://www.italia.it/en/emilia-romagna/parma/soragna |
lede: Una o due frasi sul comune, con i luoghi principali (solo fatti da fonte).
src: Italia.it, Soragna^https://www.italia.it/en/emilia-romagna/parma/soragna
src: Parma Welcome, Sinagoga e Museo ebraico Fausto Levi^https://parmawelcome.it/scheda/...
- Rocca Meli Lupi | storia/Castelli e fortezze | mid | i | Da verificare | Descrizione di 2-4 frasi con fatti dalla fonte. | Perché andarci, una riga. | Piazza Meli Lupi 5, Soragna | src=Italia.it, Soragna^https://www.italia.it/...^uff ; mic=DBUnico.102187
- Centro storico, chiese e oratori | storia/Piazze e centro storico | short | v | free | ... | ... | Piazza Garibaldi, Soragna | src=Musei del Cibo, Intorno al museo^https://...^uff
scarto: DBUnico.102154 Museo naturalistico | da rivalutare: nessuna descrizione nelle fonti ufficiali lette
copertura: completa
minimo: 5 | MiC (3 luoghi, tutti inseriti), italia.it, portale regionale eseguite; sito del Comune non letto
```
Intestazione: `@ Nome | ISTAT | SIGLA | url principale (italia.it o portale ufficiale) | premi separati da spazio (borghi arancione unesco) o vuoto`.

Riga luogo, 9 campi separati da ` | `:
1. Nome
2. categoria/sottocategoria (solo quelle sotto)
3. durata: short (30-45 min), mid (1-1,5 ore), long (2 ore e oltre)
4. flag, anche vuoto: i = al coperto, v = panorama, u = dentro un sito UNESCO, k = card/pass, w = avviso, c = chiuso
5. prezzo: `free`, `Da verificare`, oppure il prezzo dalla fonte (es. `€5, ridotto €3`, `Offerta libera`)
6. descrizione (fatti da fonte)
7. perché andarci (una riga)
8. indirizzo
9. `src=Nome fonte, titolo^url^uff` (più fonti separate da ` ; `), poi eventuali `mic=codice`, `note=...`, `rev=AAAA-MM`, `off=url sito ufficiale verificato`

## Sottocategorie ammesse (esatte)
- storia: Piazze e centro storico, Borghi, Torri, Castelli e fortezze, Palazzi e ville, Portici UNESCO, Archeologia, Monumenti e memoriali, Teatri storici, Borghi abbandonati
- sacro: Basiliche, Cattedrali e duomi, Complessi monumentali, Abbazie e monasteri, Santuari, Cimiteri monumentali, Chiese e pievi
- musei: Arte antica, Arte moderna, Storia della città, Scienza e università, Archeologici, Tematici, Case museo
- natura: Parchi urbani, Colline e sentieri, Montagna, Mare e spiagge, Laghi e fiumi, Parchi e riserve naturali, Grotte e geositi, Giardini botanici, Paesaggi e zone d'interesse
- locale: Mercati storici, Enogastronomia, Terme, Artigianato, Angoli nascosti, Motori

## Efficienza
- Parti dalla lista MiC e da italia.it; poi portale regionale e sito del Comune. Non insistere oltre 2 tentativi su una pagina che non si apre: annotalo nella riga minimo/copertura.
- Risposta finale in UNA riga: file scritti e numero di luoghi per comune, più eventuali punti da controllare (bollini incerti, comuni sotto il minimo).

## Alleggerimento (9/11, deciso da Stefano): meno ricerche, stesse regole sulle fonti
- **Prezzi:** se la prima fonte ufficiale letta non dà il prezzo, scrivi `Da verificare` e vai avanti. Non cercare il prezzo altrove: la guida mostra da sola una stima («circa N €» o «probabilmente gratis») ricavata dai luoghi dello stesso tipo, con il link al sito ufficiale.
- **Orari:** non cercarli apposta; riportali solo se sono nella pagina che stai già leggendo.
- **Siti che bloccano la lettura automatica: non provarli nemmeno.** Le schede di `cultura.gov.it` (catalogo MiC), `lombardiabeniculturali.it`, `parcoaveto.it`, `parcoantola.it`, `myspezia.it`, `franciacorta.wine`. I dati MiC che ti servono (nome, codice, comune, indirizzo) sono già nella lista che ricevi.
- **Prima scelta:** italia.it e il portale turistico regionale (una ricerca con `allowed_domains` sul portale dà spesso tutti i luoghi del comune in una sola pagina). Il sito del Comune solo se i primi due non bastano.
- **Una ricerca per comune per i luoghi, non una per luogo:** cerca «<comune> cosa vedere» sul portale ufficiale e leggi quella pagina.
- **Tetto:** al massimo 15 ricerche web in tutto per i tre comuni.

## Nota per la Calabria (9/11)
Le pagine web di calabriastraordinaria.it non restituiscono testo: cerca invece i PDF dello stesso portale (guide e itinerari, `site:calabriastraordinaria.it filetype:pdf <comune>`), il portale della Città metropolitana di Reggio Calabria, i siti dei parchi (Sila, Pollino, Aspromonte, Serre), le pagine italia.it e le schede MiC. Prima di chiudere un comune sotto i 3 luoghi prova almeno queste fonti.

## Nota per il Friuli-Venezia Giulia (9/11)
turismofvg.it blocca la lettura automatica: usa invece le schede di italia.it, il catalogo regionale del patrimonio culturale (SIRPAC / ERPAC, regione.fvg.it), i siti dei parchi (Prealpi Giulie, Dolomiti Friulane), degli ecomusei riconosciuti dalla Regione, il Touring e le schede MiC. Prima di chiudere un comune sotto i 3 luoghi prova almeno queste fonti.

## Comuni difficili (10/11/2026)
Se dopo le ricerche normali un comune resta sotto il minimo, si usa la tattica degli indizi: in /home/claude/bozze/indizi/indizi-<Comune>.txt c'è l'elenco Wikidata dei luoghi che esistono (non è una fonte). Per ogni indizio si cerca il nome esatto e si aprono fonti ufficiali trasversali: sito del gestore, parrocchia o Diocesi, chieseitaliane.chiesacattolica.it, sigecweb.beniculturali.it (schede ICCD), Touring, FAI, ISPRA (musei), portali turistici provinciali e consorzi (es. BIM), PDF e pagine alternative del Comune. Wikipedia solo per trovare link ufficiali nelle note.
