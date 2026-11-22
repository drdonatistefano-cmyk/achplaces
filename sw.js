/* 14/11/2026 – Ach's Places Guide: copia nel telefono per i ritorni e per quando manca la rete.
   - file con impronta nel nome (dati.<h>.json, det.*, mappa*, en.*, luoghi.*.js, font/): dalla copia, se c'è; non cambiano mai;
   - pagine e manifest.json: sempre dalla rete, con la copia solo se la rete manca;
   - foto, altri siti e statistiche: non toccati. */
const V="achp-1";
const IMPRONTA=/\/(?:[a-z]+|det\.[a-z]{2}|en\.[a-z]{2}|en\.ui)\.[0-9a-f]{10}\.(?:json|js)$|\/font\/[a-z-]+-\d00\.woff2$/;
self.addEventListener("install",e=>self.skipWaiting());
self.addEventListener("activate",e=>e.waitUntil((async()=>{
  for(const k of await caches.keys())if(k!==V)await caches.delete(k);
  await self.clients.claim();
})()));
self.addEventListener("fetch",e=>{
  const r=e.request;if(r.method!=="GET")return;
  const u=new URL(r.url);if(u.origin!==location.origin)return;
  if(IMPRONTA.test(u.pathname)){
    e.respondWith((async()=>{const c=await caches.open(V);const h=await c.match(r,{ignoreVary:true});if(h)return h;
      const n=await fetch(r);if(n.ok)c.put(r,n.clone());return n;})());
    return;
  }
  const pag=r.mode==="navigate"||u.pathname==="/"||/\/(index|filtri)\.html$/.test(u.pathname)||u.pathname.endsWith("/manifest.json");
  if(pag){
    e.respondWith((async()=>{const c=await caches.open(V);
      try{const n=await fetch(r);if(n.ok&&!u.pathname.startsWith("/comune/")&&!u.pathname.startsWith("/luogo/")&&!u.pathname.startsWith("/en/"))c.put(r,n.clone());return n;}
      catch(x){const h=await c.match(r,{ignoreSearch:true});if(h)return h;throw x;}})());
  }
});
/* pulizia: al massimo 400 file con impronta (le vecchie versioni escono da sole quando cambia V o si superano) */
self.addEventListener("message",async e=>{if(e.data!=="pulisci")return;const c=await caches.open(V);const k=await c.keys();for(const x of k.slice(0,Math.max(0,k.length-400)))await c.delete(x);});
