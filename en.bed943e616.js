/* 13/11/2026 – Ach's Places Guide in English.
   Loaded only when the page is in English (window.ACH_LANG==="en", decided by the small script at the top of the page).
   It translates the page in place, without touching the code that draws it:
   - interface texts: exact dictionary (D) and a few patterns with numbers and names (PAT);
   - texts of places and towns: translation memory per province (en.<prov>.<hash>.json) and for the long interface
     texts (en.ui.<hash>.json), looked up by the fingerprint of the Italian text (same as traduci/estrai.py).
   The texts were translated automatically with Opus-MT it-en (Helsinki-NLP, CC BY 4.0), an open model run
   on GitHub Actions: no third-party service is called by the page. */
(function(){
"use strict";
const W=window;if(W.ACH_EN)return;
const D={"Guida":"Guide","🧭 Guida":"🧭 Guide","Mappa":"Map","🗺️ Mappa":"🗺️ Map","Mappa dei luoghi":"Map of places","Luoghi":"Places","📍 Luoghi":"📍 Places","Comuni":"Towns","🏘️ Comuni":"🏘️ Towns","Province":"Provinces","🗺️ Province":"🗺️ Provinces","Regioni":"Regions","🧭 Regioni":"🧭 Regions","Nord-Sud":"North-South","🇮🇹 Nord-Sud":"🇮🇹 North-South","Metodo":"Method","📐 Metodo":"📐 Method","Metodo e regole":"Method and rules","Archivio fonti":"Source archive","Archivio delle fonti":"Source archive","Archivio delle fonti per regione":"Source archive by region","Fonti":"Sources","Events":"Events","Dinners":"Dinners","Le guide di Ach":"Ach's guides","Sezioni":"Sections","Filtri":"Filters","Chiudi filtri":"Close filters","Chiudi i filtri":"Close filters","Chiudi":"Close","Azzera":"Reset","Azzera filtri":"Reset filters","✕ Azzera i filtri":"✕ Clear filters","Azzera tutti i filtri":"Clear all filters","Togli tutti":"Remove all","Fatto":"Done","Apri":"Open","Tutto":"All","Tutti":"All","Tutte":"All","Tutti i tipi":"All types","Tutti i comuni":"All towns","Tutte le regioni":"All regions","Tutta l'Italia":"All of Italy","Cerca un luogo":"Search a place","Cerca un luogo…":"Search a place…","Cerca un luogo o un comune":"Search a place or a town","Cerca un comune":"Search a town","Cerca un comune…":"Search a town…","Cerca una provincia":"Search a province","Cerca una provincia…":"Search a province…","Cerca una regione":"Search a region","Cerca una regione…":"Search a region…","Cerca una fonte":"Search a source","Cerca un ente o un comune…":"Search an organisation or a town…","Cancella ricerca":"Clear search","Scegli i comuni":"Choose towns","Scegli le province":"Choose provinces","Scegli le regioni":"Choose regions","Scegli il luogo":"Choose the place","puoi sceglierne più di una":"you can choose more than one","puoi sceglierne più di uno":"you can choose more than one","Raggruppa i luoghi":"Group the places","Cosa vuoi vedere":"What do you want to see","Al volo":"Quick picks","Da dove parti":"Where do you start from","o scegli un comune di partenza":"or choose a starting town","Vicino a te":"Near you","📍 Vicino a te":"📍 Near you","📍 Luoghi vicino a te":"📍 Places near you","📍 Usa la mia posizione":"📍 Use my location","La mia posizione":"My location","Nessuna posizione scelta.":"No location chosen.","Raggio":"Radius","Togli il filtro distanza":"Remove distance filter","Tempo in auto":"Driving time","Posizione non disponibile o non autorizzata: scegli un comune di partenza.":"Location not available or not allowed: choose a starting town.","Categoria":"Category","Tipo":"Type","🏷️ Tipo":"🏷️ Type","Tipo di fonte":"Source type","Regione":"Region","Provincia":"Province","Ingresso":"Entry","🎟️ Ingresso":"🎟️ Entry","Tempo":"Time","⏱️ Tempo":"⏱️ Time","Ideale per":"Ideal for","✨ Ideale per":"✨ Ideal for","Archeologia":"Archaeology","🏺 Archeologia":"🏺 Archaeology","Monumenti":"Monuments","Sacro":"Sacred","Musei":"Museums","Natura":"Nature","Tradizioni":"Traditions","Storia e monumenti":"History and monuments","🏛️ Storia e monumenti":"🏛️ History and monuments","Luoghi sacri":"Sacred places","Vita locale":"Local life","Preistoria":"Prehistory","Nuragici":"Nuragic","Etruschi":"Etruscan","Greci":"Greek","Fenici":"Phoenician","Italici":"Italic peoples","Romani":"Roman","Tardoantichi":"Late antique","Medievali":"Medieval","Altro":"Other","Castelli":"Castles","Fortezze":"Fortresses","Mura":"Walls","Torri":"Towers","Palazzi":"Palaces","Ville":"Villas","Piazze":"Squares","Centri":"Historic centres","Borghi":"Villages","Abbandonati":"Abandoned villages","Portici":"Porticoes","Teatri":"Theatres","Ponti":"Bridges","Fontane":"Fountains","Memoriali":"Memorials","Chiese":"Churches","Pievi":"Parish churches","Basiliche":"Basilicas","Duomi":"Cathedrals","Abbazie":"Abbeys","Conventi":"Convents","Santuari":"Sanctuaries","Oratori":"Oratories","Battisteri":"Baptisteries","Sinagoghe":"Synagogues","Monti sacri":"Sacred Mounts","Complessi":"Religious complexes","Cimiteri":"Cemeteries","Pittura":"Painting","Moderna":"Modern art","Ceramica":"Ceramics","Archeologici":"Archaeological","Scienza":"Science","Storia":"History","Dimore":"House museums","Diocesani":"Diocesan","Etnografici":"Ethnographic","Tecnica":"Technology","Militari":"Military","Tematici":"Themed","Parchi":"Parks","Riserve":"Reserves","Giardini":"Gardens","Orti":"Botanical gardens","Laghi":"Lakes","Fiumi":"Rivers","Cascate":"Waterfalls","Spiagge":"Beaches","Montagna":"Mountains","Vulcani":"Volcanoes","Grotte":"Caves","Geositi":"Geosites","Sentieri":"Trails","Panorami":"Viewpoints","Mercati":"Markets","Terme":"Spas","Sapori":"Food and wine","Botteghe":"Workshops","Motori":"Motors","Curiosità":"Curiosities","Abbazie e monasteri":"Abbeys and monasteries","Angoli nascosti":"Hidden corners","Arte antica":"Old masters","Arte moderna":"Modern art","Artigianato":"Crafts","Borghi abbandonati":"Abandoned villages","Case museo":"House museums","Castelli e fortezze":"Castles and fortresses","Cattedrali e duomi":"Cathedrals","Chiese e pievi":"Churches and parish churches","Cimiteri monumentali":"Monumental cemeteries","Colline e sentieri":"Hills and trails","Complessi monumentali":"Monumental complexes","Enogastronomia":"Food and wine","Giardini botanici":"Botanical gardens","Grotte e geositi":"Caves and geosites","Laghi e fiumi":"Lakes and rivers","Mare e spiagge":"Sea and beaches","Mercati storici":"Historic markets","Monumenti e memoriali":"Monuments and memorials","Paesaggi e zone d'interesse":"Landscapes","Palazzi e ville":"Palaces and villas","Parchi e riserve naturali":"Parks and nature reserves","Parchi urbani":"City parks","Piazze e centro storico":"Squares and old town","Scienza e università":"Science and university","Storia della città":"City history","Teatri storici":"Historic theatres","Piazze e centri storici":"Squares and old towns","Gratis":"Free","Gratuito":"Free","A pagamento":"Paid","🎟️ A pagamento":"🎟️ Paid","Da verificare sul sito":"Check on the website","Da verificare":"To be checked","Gratis con Card":"Free with Card","Con Card":"With Card","con Card":"with Card","Card":"Card","Pagamento":"Paid","❔ ingresso da verificare":"❔ entry to be checked","Se piove":"If it rains","Al coperto":"Indoors","☔ Coperto":"☔ Indoors","Coperto":"Indoors","Panorama":"Views","🌅 Panorama":"🌅 Views","UNESCO":"UNESCO","🌍 UNESCO":"🌍 UNESCO","Borghi più belli":"Most beautiful villages","🏘️ Borghi più belli":"🏘️ Most beautiful villages","Bandiera Arancione":"Orange Flag","Bandiere Arancioni":"Orange Flags","🟠 Bandiere Arancioni":"🟠 Orange Flags","Arancione":"Orange Flag","Fino a 45 min":"Up to 45 min","1-1,5 ore":"1-1.5 hours","2 ore e oltre":"2 hours or more","≤ 45 min":"≤ 45 min","⚡ ≤ 45 min":"⚡ ≤ 45 min","1-1,5 h":"1-1.5 h","⏱️ 1-1,5 h":"⏱️ 1-1.5 h","⏱️ 1-1,5 ore":"⏱️ 1-1.5 hours","2 h e più":"2 h or more","🥾 2 h e più":"🥾 2 h or more","Breve":"Short","Medio":"Medium","Lungo":"Long","1 ora":"1 hour","30 min":"30 min","Biglietti":"Tickets","🎟️ Biglietti":"🎟️ Tickets","Biglietti ufficiali":"Official tickets","Foto":"Photo","Come arrivare":"Directions","Vedi sulla mappa":"See on the map","Apri nella guida":"Open in the guide","Copia indirizzo":"Copy address","Copiato":"Copied","Salva nei miei luoghi":"Save to my places","Salva tra i miei luoghi":"Save to my places","Svuota":"Clear","Cerca su Wikipedia":"Search on Wikipedia","Info sul portale turistico ↗":"Tourist portal info ↗","Scheda sul portale turistico":"Tourist portal page","Sito ufficiale":"Official website","Orari ufficiali":"Official opening hours","Perché andarci.":"Why go.","Perché andarci":"Why go","Indirizzo":"Address","Orari":"Opening hours","Accessibilità":"Accessibility","Tempo consigliato":"Suggested time","Prenotazione":"Booking","Prezzo":"Price","Prezzi":"Prices","Prezzi e orari cambiano: controlla il sito ufficiale prima di partire.":"Prices and opening hours change: check the official website before you go.","Avvisi":"Notices","⚠️ Avviso":"⚠️ Notice","⛔ Chiuso ora":"⛔ Closed now","Chiuso":"Closed","Foto del comune, non del luogo":"Photo of the town, not of the place","Idee per la visita":"Ideas for your visit","⏳ Se hai poco tempo":"⏳ If you are short of time","🌤️ Mezza giornata":"🌤️ Half a day","☀️ Una giornata":"☀️ A whole day","📍 Comuni vicini nella guida":"📍 Nearby towns in the guide","Posizione nella classifica di tutta la guida":"Rank in the whole guide","Posizione nella selezione attuale":"Rank in the current selection","N°":"No.","Ingrandisci":"Zoom in","Rimpicciolisci":"Zoom out","Cambia i colori":"Change colours","Colori":"Colours","Carta":"Paper","Blu notte":"Midnight blue","Ardesia":"Slate","Oceano":"Ocean","Notte":"Night","Nascondi luoghi":"Hide places","Mostra i luoghi":"Show places","Allarga o riduci l'elenco":"Expand or shrink the list","Luoghi in vista":"Places in view","luoghi in vista":"places in view","Torna alla Guida":"Back to the Guide","Mappa d'Italia con i luoghi raggruppati":"Map of Italy with grouped places","Mappa: i luoghi sulla mappa d'Italia, per regione, provincia e comune":"Map: the places on the map of Italy, by region, province and town","Tocca una regione o ingrandisci: i luoghi si dividono per provincia":"Tap a region or zoom in: places split by province","Tocca un comune, poi un luogo per aprire la scheda":"Tap a town, then a place to open its page","Carico i nomi dei luoghi…":"Loading place names…","Nessun luogo qui con questi filtri. Allarga la mappa o togli un filtro.":"No places here with these filters. Zoom out or remove a filter.","Posizione non disponibile su questo dispositivo":"Location not available on this device","Sei fuori dai comuni della guida":"You are outside the towns covered by the guide","Consenti l’accesso alla posizione nelle impostazioni":"Allow location access in your settings","Posizione non trovata, riprova":"Location not found, please try again","Confini di regioni e province: ISTAT (CC BY), elaborazione openpolis. La mappa è disegnata qui, senza servizi di terzi.":"Region and province boundaries: ISTAT (CC BY), processed by openpolis. The map is drawn here, with no third-party services.","Nessun luogo con questi filtri.":"No places with these filters.","luoghi":"places","luogo":"place","comuni":"towns","province":"provinces","regioni":"regions","gratuiti":"free","avvisi":"notices","con avvisi":"with notices","errori":"errors","visibili":"visible","da vedere":"to see","e da scoprire.":"and to discover.","Tutti i luoghi,":"All the places,","dove mangiare":"where to eat","spettacoli, mostre, cinema":"shows, exhibitions, cinema","su Tiqets · partner":"on Tiqets · partner","su GetYourGuide · partner":"on GetYourGuide · partner","Partner: la guida riceve una piccola commissione, il prezzo per te non cambia.":"Partner: the guide receives a small commission, your price does not change.","Alcuni link sono affiliati: se compri un biglietto la guida riceve una piccola commissione, senza costi per te.":"Some links are affiliate links: if you buy a ticket the guide receives a small commission, at no cost to you.","Ach's Places Guide · Tutta la guida":"Ach's Places Guide · The whole guide","Mappa · Ach's Places Guide":"Map · Ach's Places Guide","Fonti secondarie":"Secondary sources","🟠 secondaria":"🟠 secondary","🟢 ufficiale":"🟢 official","Fonte 🟢":"Source 🟢","🟢 fonte ufficiale · 🟠 fonte secondaria, da ricontrollare.":"🟢 official source · 🟠 secondary source, to be rechecked.","Le fonti 🟠 sono le prime da sostituire con una fonte ufficiale.":"🟠 sources are the first to be replaced with an official source.","🟢 Sito ufficiale del luogo o del suo gestore.":"🟢 Official website of the place or its operator.","🟢 Ufficio turistico ufficiale (Comune, destinazione, Regione).":"🟢 Official tourist office (town, destination, region).","🇮🇹 Fonti nazionali":"🇮🇹 National sources","🗂️ Da consultare o scartate":"🗂️ To consult or discarded","🔜 da consultare":"🔜 to consult","Altri enti e associazioni":"Other bodies and associations","Comuni con luoghi MiC":"Towns with Ministry of Culture sites","Comuni già in guida":"Towns already in the guide","Luoghi MiC":"Ministry of Culture sites","Link precisi biglietti e orari*":"Exact ticket and opening-hour links*","Siti dei Comuni":"Town websites","Turismo, Regione e Province":"Tourism, region and provinces","Diocesi, chiese e santuari":"Dioceses, churches and sanctuaries","Musei, ville e castelli":"Museums, villas and castles","Parchi e natura":"Parks and nature","Wikipedia (fonte secondaria)":"Wikipedia (secondary source)","Wikidata (dati aperti CC0)":"Wikidata (open data CC0)","UNESCO, Patrimonio mondiale":"UNESCO, World Heritage","ISTAT, elenco dei comuni":"ISTAT, list of municipalities","Ministero della Cultura (luoghi, musei, soprintendenze)":"Ministry of Culture (sites, museums, superintendencies)","Ministero della Cultura, dati aperti dei luoghi della cultura":"Ministry of Culture, open data on cultural sites","Italia.it, portale turistico nazionale (ENIT)":"Italia.it, national tourism portal (ENIT)","Catalogo generale dei beni culturali (MiC, ICCD)":"General catalogue of cultural heritage (MiC, ICCD)","Commissione Nazionale Italiana per l'UNESCO":"Italian National Commission for UNESCO","FAI, Fondo per l'Ambiente Italiano":"FAI, Italian National Trust","I Borghi più belli d'Italia":"The most beautiful villages in Italy","Bandiere Arancioni (Touring Club)":"Orange Flags (Touring Club)","Parks.it, portale dei parchi italiani":"Parks.it, portal of Italian parks","ISPRA, Istituto superiore per la protezione e la ricerca ambientale":"ISPRA, Italian Institute for Environmental Protection and Research","1. Tassonomia":"1. Taxonomy","2. La scheda di ogni luogo":"2. The page of each place","3. Gerarchia delle fonti":"3. Hierarchy of sources","4. Regole legali":"4. Legal rules","5. Design e dispositivi":"5. Design and devices","6. Struttura dei dati":"6. Data structure","7. Manutenzione":"7. Maintenance","8. Come leggere le schede":"8. How to read the pages","9. Note legali e crediti":"9. Legal notes and credits","10. Controllo di qualità automatico":"10. Automatic quality check","11. Ricerca a costo zero":"11. Zero-cost research","Abruzzo":"Abruzzo","Basilicata":"Basilicata","Calabria":"Calabria","Campania":"Campania","Emilia-Romagna":"Emilia-Romagna","Friuli-Venezia Giulia":"Friuli-Venezia Giulia","Lazio":"Lazio","Liguria":"Liguria","Lombardia":"Lombardy","Marche":"Marche","Molise":"Molise","Piemonte":"Piedmont","Puglia":"Apulia","Sardegna":"Sardinia","Sicilia":"Sicily","Toscana":"Tuscany","Trentino-Alto Adige":"Trentino-South Tyrol","Umbria":"Umbria","Valle d'Aosta":"Aosta Valley","Veneto":"Veneto","Roma":"Rome","Firenze":"Florence","Milano":"Milan","Napoli":"Naples","Venezia":"Venice","Torino":"Turin","Genova":"Genoa","Padova":"Padua","Mantova":"Mantua","Siracusa":"Syracuse","Biglietteria ufficiale":"Official ticket office","Sito del gestore":"Operator's website","Prenota":"Book","Vedi":"See","Fonti della scheda":"Sources for this page","Fonti verificate":"Sources checked","Copiato!":"Copied!","Visite guidate":"Guided tours","Visite ed esperienze":"Tours and experiences","Biglietti su Tiqets":"Tickets on Tiqets","Orari ufficiali (pagina del gestore)":"Official opening hours (operator's page)","Biglietti ufficiali (pagina del gestore)":"Official tickets (operator's page)","consultata, non usata":"consulted, not used","Da consultare o scartate":"To consult or discarded","Nessuna foto ripubblicata: le immagini restano sui siti dei titolari.":"No photos republished: images stay on their owners' websites.","Sito ufficiale del luogo":"Official website of the place","Vista":"View","Mostra per":"Group by","Zona":"Area","Stai guardando":"You are viewing","Raggruppa per":"Group by"};
const MEM=new Map();
function enk(t){let h=0x811c9dc5;for(let i=0;i<t.length;i++){h^=t.charCodeAt(i);h=Math.imul(h,0x01000193)>>>0;}return h.toString(36)+"."+t.length;}
const MESI={gennaio:"January",febbraio:"February",marzo:"March",aprile:"April",maggio:"May",giugno:"June",luglio:"July",agosto:"August",settembre:"September",ottobre:"October",novembre:"November",dicembre:"December"};
const num=s=>s.replace(/(\d),(\d)/g,"$1.$2");
const PL=(n,a,b)=>(+String(n).replace(/\./g,"")===1?a:b);
function T(s){/* traduzione di una parte (nome di categoria, tipo, regione...) */const v=D[s];return v===undefined?s:v;}
const PAT=[
 [/^(\d[\d.]*) comuni · (\d[\d.]*) luoghi$/,(m,a,b)=>`${a} ${PL(a,"town","towns")} · ${b} ${PL(b,"place","places")}`],
 [/^(\d[\d.]*) province · (\d[\d.]*) luoghi$/,(m,a,b)=>`${a} ${PL(a,"province","provinces")} · ${b} ${PL(b,"place","places")}`],
 [/^(\d[\d.]*) provincia · (\d[\d.]*) luoghi$/,(m,a,b)=>`${a} province · ${b} ${PL(b,"place","places")}`],
 [/^([\d.,]+) km · (\d+) luogh[io]$/,(m,a,b)=>`${num(a)} km · ${b} ${PL(b,"place","places")}`],
 [/^(\d[\d.]*) (luoghi|luogo) su (\d[\d.]*)$/,(m,a,b,c)=>`${a} ${PL(a,"place","places")} of ${c}`],
 [/^(\d[\d.]*) comuni$/,(m,a)=>`${a} ${PL(a,"town","towns")}`],
 [/^(\d[\d.]*) (luoghi|luogo)$/,(m,a)=>`${a} ${PL(a,"place","places")}`],
 [/^Mostra (\d[\d.]*) (luoghi|luogo)$/,(m,a)=>`Show ${a} ${PL(a,"place","places")}`],
 [/^Mostra altri (\d[\d.]*) di (\d[\d.]*)$/,(m,a,b)=>`Show ${a} more of ${b}`],
 [/^Tutti i (\d[\d.]*) luoghi$/,(m,a)=>`All ${a} places`],
 [/^· n\. (\d+) in Italia$/,(m,a)=>`· no. ${a} in Italy`],
 [/^n\. (\d+) in Italia$/,(m,a)=>`no. ${a} in Italy`],
 [/^(Dati|Fonti) verificat[ie] il (\d+) (\w+) (\d{4})$/,(m,a,g,me,y)=>`${a==="Dati"?"Data":"Sources"} checked on ${g} ${MESI[me]||me} ${y}`],
 [/^Verificato il (\d+) (\w+) (\d{4})$/,(m,g,me,y)=>`Checked on ${g} ${MESI[me]||me} ${y}`],
 [/^(Categoria|Tipo|Ideale per|Ingresso|Tempo): (.+), (\d[\d.]*) luoghi$/,(m,a,b,c)=>`${T(a)}: ${T(b)}, ${c} places`],
 [/^Biglietti su (Tiqets|GetYourGuide): (.+)$/,(m,a,b)=>`Tickets on ${a}: ${b}`],
 [/^Biglietti ufficiali: (.+)$/,(m,a)=>`Official tickets: ${a}`],
 [/^Biglietto: vedi la scheda di (.+)$/,(m,a)=>`Ticket: see the page of ${a}`],
 [/^Tariffe sul sito ufficiale: (.+)$/,(m,a)=>`Prices on the official website: ${a}`],
 [/^Ingresso gratuito: vedi la scheda di (.+)$/,(m,a)=>`Free entry: see the page of ${a}`],
 [/^Foto di (.+) su Google Immagini$/,(m,a)=>`Photos of ${a} on Google Images`],
 [/^Cerca (.+) su Wikipedia$/,(m,a)=>`Search ${a} on Wikipedia`],
 [/^Come arrivare a (.+)$/,(m,a)=>`Directions to ${a}`],
 [/^Togli filtro (.+)$/,(m,a)=>`Remove filter ${tr(a)}`],
 [/^Azzera tutti i filtri \((\d+) attivi\)$/,(m,a)=>`Clear all filters (${a} active)`],
 [/^Sei vicino a (.+)$/,(m,a)=>`You are near ${T(a)}`],
 [/^Posizione trovata \(precisione circa (\d+) m\)\.$/,(m,a)=>`Location found (accuracy about ${a} m).`],
 [/^(.+) \(([A-Z]{2})\)$/,(m,a,b)=>D[a]!==undefined?`${D[a]} (${b})`:null],
 [/^([\d.,]+)-([\d.,]+) (h|ore)$/,(m,a,b)=>`${num(a)}-${num(b)} h`],
 [/^(\d+) min$/,(m,a)=>`${a} min`],
 [/^(\d+)-(\d+) minuti$/,(m,a,b)=>`${a}-${b} minutes`],
 [/^(\d+) minuti$/,(m,a)=>`${a} minutes`],
 [/^(\d+) or[ae]$/,(m,a)=>`${a} ${a==="1"?"hour":"hours"}`],
 [/^(\d+) giorni$/,(m,a)=>`${a} days`],
 [/^(\d[\d.]*) luoghi in (\d[\d.]*) comuni di (\d+) province, in (.+)$/,(m,a,b,c,l)=>`${a} places in ${b} towns across ${c} provinces, in ${l.replace(/\.$/,"").split(/, | e /).map(T).join(", ")}`],
 [/^Monumenti, chiese, musei, natura e angoli nascosti del comune di (.+) \((Città metropolitana di|provincia di) (.+)\), con biglietti, orari e come arrivare\. Ogni scheda cita le sue fonti\.$/,(m,a,k,p)=>`Monuments, churches, museums, nature and hidden corners of ${T(a)} (${k==="provincia di"?"province of":"metropolitan city of"} ${T(p)}), with tickets, opening hours and directions. Every entry cites its sources.`],
 [/^Foto: (.+)$/,(m,a)=>`Photo: ${a}`],
 [/^(.+?)(\s*[↗›»→]+)$/,(m,a,b)=>{const x=tr(a);return x!==a?x+b:null;}]
];
/* prefissi: emoji o simboli davanti al testo (🗺️ Lazio, 📍 Bologna) */
const PRE=/^([\p{Extended_Pictographic}\p{Emoji_Presentation}️‍✕✓↗·•–—\s]+)(.+)$/u;
const CACHE=new Map();
function tr(s){
  if(!s)return s;
  let v=D[s];if(v!==undefined)return v;
  v=CACHE.get(s);if(v!==undefined)return v;
  v=tr0(s);if(CACHE.size>30000)CACHE.clear();CACHE.set(s,v);return v;
}
function tr0(s){
  const m=MEM.get(enk(s));if(m)return m;
  for(const [re,f] of PAT){const r=s.match(re);if(r){const o=f(...r);if(o!=null)return o;}}
  const p=s.match(PRE);if(p){const x=tr(p[2]);if(x!==p[2])return p[1]+x;}
  if(s.includes(" · ")){const parts=s.split(" · ");const t=parts.map(tr);if(t.some((x,i)=>x!==parts[i]))return t.join(" · ");}
  const q=s.match(/^(.+?)([.:,;]\s*)$/);if(q){const x=tr(q[1]);if(x!==q[1])return x+q[2];}
  return s;
}
function provDi(id){if(!id)return;const pr=id.includes("--")?id.split("--")[0].split("-").pop():"bo";if(pr&&pr.length===2)caricaMem(pr.toUpperCase());}
const ATTR=["placeholder","aria-label","title","alt"];
const SKIP=new Set(["SCRIPT","STYLE","TEXTAREA","CODE","PRE"]);
const FATTO=new WeakMap(),FATTOA=new WeakMap();/* cio' che ho scritto io non si ritraduce (niente giri infiniti) */
function testo(n){
  const v=n.nodeValue;if(!v||v.length<1||FATTO.get(n)===v)return;
  const t=v.trim();if(!t||!/[A-Za-zÀ-ÿ]/.test(t))return;
  const x=tr(t);if(x!==t){const nv=v.replace(t,x);FATTO.set(n,nv);n.nodeValue=nv;}
}
function attr(e){let m=FATTOA.get(e);for(const a of ATTR){const v=e.getAttribute&&e.getAttribute(a);if(v){if(m&&m[a]===v)continue;const x=tr(v.trim());if(x!==v.trim()){if(!m){m={};FATTOA.set(e,m);}m[a]=x;e.setAttribute(a,x);}}}}
function giro(root){
  if(!root)return;
  if(root.nodeType===3){const p=root.parentNode;if(p&&!SKIP.has(p.nodeName)&&!(p.closest&&p.closest("[data-noen]")))testo(root);return;}
  if(root.nodeType!==1||SKIP.has(root.nodeName))return;
  if(root.closest&&root.closest("[data-noen]"))return;
  attr(root);
  /* schede della Guida: la provincia si legge dall'identificativo del luogo (comune-pr--luogo) */
  const pid=root.getAttribute&&root.getAttribute("data-pid");if(pid)provDi(pid);
  for(const e of root.querySelectorAll("[data-pid]"))provDi(e.getAttribute("data-pid"));
  const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT,{acceptNode:n=>n.nodeType===1?(SKIP.has(n.nodeName)||n.hasAttribute("data-noen")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_SKIP):NodeFilter.FILTER_ACCEPT});
  let n;while(n=w.nextNode())testo(n);
  for(const e of root.querySelectorAll("[placeholder],[aria-label],[title],[alt]"))attr(e);
}
/* giro su tutta la pagina a pezzi di circa 12 ms, per non bloccare (prima i nodi in alto, cioe' quelli che si vedono) */
let gen=0;
function giroTutto(fine){const g=++gen;let fatti=0;
  const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT,{acceptNode:n=>n.nodeType===1?(SKIP.has(n.nodeName)||n.hasAttribute("data-noen")?NodeFilter.FILTER_REJECT:NodeFilter.FILTER_ACCEPT):NodeFilter.FILTER_ACCEPT});
  const pezzo=()=>{if(g!==gen)return;const t0=performance.now();let n,k=0;
    while((k++&31)||performance.now()-t0<10){n=w.nextNode();if(!n)break;fatti++;
      if(n.nodeType===3)testo(n);else{if(n.hasAttribute("data-pid"))provDi(n.getAttribute("data-pid"));if(n.hasAttributes())attr(n);}}
    if(fine&&(fatti>600||!n)){const f=fine;fine=null;f();}
    if(n)setTimeout(pezzo,0);};
  pezzo();}
let coda=new Set(),pronto=false;
function svuota(){const c=coda;coda=new Set();pronto=false;for(const n of c)if(n.isConnected)giro(n);}
const MO=new MutationObserver(list=>{
  for(const r of list){
    if(r.type==="characterData")coda.add(r.target);
    else if(r.type==="attributes")coda.add(r.target);
    else for(const n of r.addedNodes)coda.add(n);
  }
  if(!pronto){pronto=true;requestAnimationFrame(svuota);}/* prima del disegno, fuori dal compito della pagina */
});
/* memoria delle traduzioni, per provincia */
const MAN=W.ACH_EN_MAN||{};const caricate={},attese={};
function caricaMem(chiave){
  const n=chiave==="ui"?MAN.ui:(MAN.det||{})[chiave];if(!n||caricate[chiave])return attese[chiave]||Promise.resolve();
  caricate[chiave]=1;
  return attese[chiave]=fetch(n).then(r=>r.ok?r.json():null).then(j=>{if(!j)return;for(const k in j)MEM.set(k,j[k]);CACHE.clear();
    requestAnimationFrame(()=>giroTutto());}).catch(()=>{});
}
/* quando la pagina scarica le schede di una provincia, scarico anche le sue traduzioni */
const f0=W.fetch.bind(W);
W.fetch=function(u,o){try{const s=typeof u==="string"?u:(u&&u.url)||"";const m=s.match(/(?:^|\/)det\.([a-z]{2})\.[0-9a-f]{10}\.json/);if(m)caricaMem(m[1].toUpperCase());}catch(e){}return f0(u,o);};
/* ricerca in inglese: la pagina legge la casella di ricerca gia' tradotta in italiano (castle -> castell, Florence -> firenze);
   chi guarda continua a vedere le parole che ha scritto */
const QF=[["old town","centro storico"],["historic centre","centro storico"],["historic center","centro storico"],["aosta valley","valle d'aosta"],["south tyrol","alto adige"],["leaning tower","torre pendente"]];
const QC={rome:"roma",florence:"firenze",venice:"venezia",naples:"napoli",milan:"milano",turin:"torino",genoa:"genova",padua:"padova",mantua:"mantova",syracuse:"siracusa",tuscany:"toscana",sicily:"sicilia",sardinia:"sardegna",lombardy:"lombardia",piedmont:"piemonte",apulia:"puglia",leghorn:"livorno",the:"",of:"",and:"",a:"",in:""};
const QS=[["amphitheat","anfiteatr"],["castle","castell"],["fortress","fortezz"],["fort","fort"],["tower","torr"],["wall","mura"],["palace","palazz"],["square","piazz"],["church","chies"],["cathedral","duomo"],["basilica","basilic"],["abbey","abbazi"],["monaster","monaster"],["convent","convent"],["sanctuar","santuari"],["chapel","cappell"],["baptist","battister"],["museum","muse"],["galler","galleri"],["painting","pittur"],["archaeolog","archeolog"],["archeolog","archeolog"],["ruin","rovin"],["roman","roman"],["etruscan","etrusc"],["greek","grec"],["mediev","mediev"],["theat","teatr"],["bridge","ponte"],["fountain","fontan"],["garden","giardin"],["botanic","botanic"],["park","parc"],["reserve","riserv"],["lake","lag"],["river","fium"],["waterfall","cascat"],["beach","spiagg"],["sea","mare"],["island","isol"],["mountain","mont"],["volcan","vulcan"],["cave","grott"],["trail","sentier"],["path","sentier"],["hik","sentier"],["view","panoram"],["panoram","panoram"],["village","borg"],["market","mercat"],["spa","term"],["thermal","term"],["cemeter","cimiter"],["lighthouse","faro"],["harbo","port"],["library","bibliotec"],["science","scienz"],["universit","universit"],["wine","vin"],["cheese","formagg"],["mosaic","mosaic"],["fresco","affresc"],["synagog","sinagog"],["villa","vill"],["gate","porta"],["arch","arco"],["column","colonn"],["temple","tempi"],["necropol","necropol"],["tomb","tomb"],["catacomb","catacomb"]];
function qIt(v){if(!v)return v;let s=" "+v.toLowerCase()+" ";for(const [a,b] of QF)s=s.split(" "+a+" ").join(" "+b+" ");
  return s.trim().split(/\s+/).map(w=>{if(w in QC)return QC[w];for(const [a,b] of QS)if(w.startsWith(a))return b;return w;}).filter(Boolean).join(" ");}
function ricercaInglese(el){if(!el||el.__en)return;el.__en=1;const P=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value");
  try{Object.defineProperty(el,"value",{configurable:true,get(){return qIt(P.get.call(this));},set(x){P.set.call(this,x);}});}catch(e){}}
function cercaCaselle(){for(const id of ["q","mq","qs"])ricercaInglese(document.getElementById(id));for(const e of document.querySelectorAll('input[type="search"]'))ricercaInglese(e);}
W.ACH_EN={tr,giro,carica:caricaMem,enk,MEM,D,qIt};
W.ENL=s=>tr(s);
let agganciato=false;
function aggancia(){/* Guida: anche le province lette dalla memoria del telefono (senza fetch) */
  if(agganciato)return;try{if(typeof caricaDet!=="function")return;}catch(e){return;}
  agganciato=true;const o=caricaDet;
  try{caricaDet=function(pr){if(pr)caricaMem(String(pr).toUpperCase());return o.apply(this,arguments);};}catch(e){}
  try{for(const k of Object.keys(DETOK).concat(Object.keys(DETP)))caricaMem(String(k).toUpperCase());}catch(e){}
}
function avvia(){
  cercaCaselle();document.addEventListener("DOMContentLoaded",cercaCaselle);
  aggancia();document.addEventListener("DOMContentLoaded",aggancia);W.addEventListener("load",aggancia);
  document.documentElement.lang="en";
  if(document.title)document.title=tr(document.title);
  MO.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:ATTR});
  giroTutto(()=>document.documentElement.classList.remove("en-wait"));
  try{const f=document.querySelector("footer")||document.querySelector(".foot");if(f&&!document.getElementById("en-nota")){const p=document.createElement("p");p.id="en-nota";p.setAttribute("data-noen","");p.style.cssText="font-size:12px;opacity:.75;margin:10px 0 0";p.textContent="English version: the descriptions are machine-translated from the original Italian texts (Opus-MT, an open model). Place names stay in Italian, as you will find them on site.";f.appendChild(p);}}catch(e){}
}
caricaMem("ui");caricaMem("BO");
if(document.body)avvia();else document.addEventListener("DOMContentLoaded",avvia);
})();
