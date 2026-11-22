// achplaces-link — Worker di Cloudflare per il controllo dei link di Ach's Places Guide.
//
// Perche' esiste: molti siti pubblici italiani (Ministero della Cultura, Regioni,
// Comuni) chiudono la porta ai server di GitHub, che stanno su Microsoft Azure.
// Da un'altra rete rispondono normalmente. Il controllo dei link su GitHub manda qui
// i link che non e' riuscito a raggiungere, e questo programma li prova dalla rete di
// Cloudflare.
//
// Che cosa fa, e solo questo: per ogni indirizzo dice se la pagina esiste
// [codice HTTP, indirizzo finale dopo i rimandi, "cf"]. Non restituisce mai il
// contenuto delle pagine, quindi non si puo' usare per leggere siti per conto d'altri.
//
// Limiti voluti:
//   - solo siti che finiscono in .it, solo http/https, niente porte strane
//     (la guida linka siti italiani; cosi' non serve a nient'altro);
//   - al massimo 15 indirizzi per richiesta, e al massimo 3 insieme, per non
//     bussare troppo forte agli stessi siti;
//   - 15 secondi al massimo per pagina.
//
// Uso:  GET  /?u=https://sito.it/pagina
//       POST /   {"u": ["https://...", "..."]}
//
// Piano gratuito di Cloudflare: 100.000 richieste al giorno; un controllo completo
// dei link bloccati ne usa meno di 100.

const UA = "Mozilla/5.0 (compatible; AchPlacesLinkCheck/1.0; +https://achplaces.com/)";
const MAX = 15;
const INSIEME = 3;
const ATTESA = 15000;

function ammesso(u) {
  try {
    const x = new URL(u);
    return (x.protocol === "https:" || x.protocol === "http:")
      && x.hostname.endsWith(".it")
      && !x.username && !x.password && !x.port;
  } catch {
    return false;
  }
}

async function prova(u) {
  if (!ammesso(u)) return [0, "", "cf:NonAmmesso"];
  const ac = new AbortController();
  const t = setTimeout(() => ac.abort(), ATTESA);
  try {
    const r = await fetch(u, {
      method: "GET",
      redirect: "follow",
      headers: { "User-Agent": UA, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8" },
      signal: ac.signal,
    });
    try { await r.body?.cancel(); } catch {}          // il contenuto non serve
    return [r.status, r.url && r.url !== u ? r.url : "", "cf"];
  } catch (e) {
    const nome = e && e.name === "AbortError" ? "Timeout" : (e && e.name) || "Errore";
    return [0, "", "cf:" + nome];
  } finally {
    clearTimeout(t);
  }
}

async function tutti(lista) {
  const esiti = new Array(lista.length);
  let prossimo = 0;
  async function lavora() {
    while (prossimo < lista.length) {
      const i = prossimo++;
      esiti[i] = await prova(lista[i]);
    }
  }
  await Promise.all(Array.from({ length: Math.min(INSIEME, lista.length) }, lavora));
  return esiti;
}

function risposta(oggetto, stato) {
  return new Response(JSON.stringify(oggetto), {
    status: stato,
    headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" },
  });
}

export default {
  async fetch(request) {
    const url = new URL(request.url);
    let lista;
    if (request.method === "POST") {
      try {
        const j = await request.json();
        lista = Array.isArray(j.u) ? j.u.filter((x) => typeof x === "string") : null;
      } catch {
        lista = null;
      }
      if (!lista) return risposta({ errore: "serve un JSON {\"u\": [indirizzi]}" }, 400);
    } else if (url.searchParams.get("u")) {
      lista = [url.searchParams.get("u")];
    } else {
      return risposta({
        servizio: "achplaces-link",
        uso: "GET /?u=https://sito.it/pagina oppure POST {\"u\": [...]}, al massimo " + MAX + " indirizzi",
        risponde: "[codice HTTP, indirizzo finale, \"cf\"] per ogni indirizzo; solo siti .it",
      }, 200);
    }
    if (lista.length > MAX) return risposta({ errore: "al massimo " + MAX + " indirizzi per richiesta" }, 400);
    const esiti = await tutti(lista);
    const fuori = {};
    lista.forEach((u, i) => { fuori[u] = esiti[i]; });
    return risposta(fuori, 200);
  },
};
