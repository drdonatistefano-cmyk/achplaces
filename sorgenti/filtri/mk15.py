# v14 -> filtri.html veloce (8/11/2026, tecniche della dashboard osterie), passo automatico dopo mk14:
# - i dati (d2.js) escono dalla pagina: luoghi.<impronta>.js, elencato nel manifest.json (letto sempre fresco);
# - dati e testi restano nel telefono (IndexedDB "luoghi", lo stesso della Guida): alla seconda visita niente rete;
# - lettura da IndexedDB in parallelo alla richiesta del manifest (ultimo nome in localStorage);
# - istantanea della prima schermata in localStorage: alla riapertura compare subito, poi la pagina vera la sostituisce.
# Il codice della pagina e i dati non cambiano: si eseguono insieme, come prima, in un unico script.
import hashlib, json, os, glob
G = '/home/claude/achs-places-guide'
head = open('v15_head.html').read()
tail = open('v15_tail.html').read()
import subprocess
subprocess.run(['node', 'comprimi_d2.js', 'd2.js', 'd2c.js'], check=True)   # dizionari + verifica di equivalenza
data = open('d2c.js').read()
assert head.rstrip().endswith('<script>')
i = tail.index('</script>')
app, resto = tail[:i], tail[i + len('</script>'):]
# il secondo script (finestra «Vicino a te») usa le variabili della pagina: si esegue subito dopo, nello stesso blocco
j = resto.index('<script>'); k = resto.index('</script>', j)
app2 = resto[j + len('<script>'):k]; resto = resto[:j] + resto[k + len('</script>'):]
assert '<script' not in resto
OLD = 'fetch(TESTI).then(r=>r.json())'
assert app.count(OLD) == 1
app = app.replace(OLD, 'prendiT(TESTI)')
# 10/11/2026: i testi (descrizioni, 4,5 MB) si scaricano al primo tocco o tasto, o quando la pagina è ferma da 6 secondi, non all'apertura
_A = 'setTimeout(()=>{prendiT(TESTI)'; _B = '}).catch(()=>{})},0);'
assert app.count(_A) == 1
_i = app.index(_A); _j = app.index(_B, _i)
app = app[:_i] + 'window.__caricaTesti=()=>{if(window.__ct)return;window.__ct=1;prendiT(TESTI)' + app[_i + len(_A):_j] + '}).catch(()=>{window.__ct=0;})};' + \
  '["pointerdown","keydown","focusin"].forEach(ev=>document.addEventListener(ev,()=>window.__caricaTesti(),{once:true,capture:true,passive:true}));' + \
  'setTimeout(()=>{("requestIdleCallback" in window)?requestIdleCallback(()=>window.__caricaTesti(),{timeout:4000}):window.__caricaTesti();},6000);' + app[_j + len(_B):]
# istantanea: dopo ogni disegno della prima schermata (elenco senza comune aperto) si salva l'HTML visibile
app += '\n;' + app2 + '\n;try{window.__salvaIst&&window.__salvaIst();}catch(e){}\n'
for f in glob.glob(os.path.join(G, 'luoghi.*.js')): os.remove(f)
h = hashlib.sha256(data.encode()).hexdigest()[:10]
NOME = f'luoghi.{h}.js'
open(os.path.join(G, NOME), 'w').write(data)
man = json.load(open(os.path.join(G, 'manifest.json')))
testi = data.split('const TESTI="', 1)[1].split('"', 1)[0]
man['luoghi'] = NOME; man['testi'] = testi
json.dump(man, open(os.path.join(G, 'manifest.json'), 'w'))
LOADER = r"""
(function(){
const MEMO={db:null,apri(){if(this.db)return this.db;this.db=new Promise(ok=>{try{const r=indexedDB.open("luoghi",1);
  r.onupgradeneeded=()=>r.result.createObjectStore("file");r.onsuccess=()=>ok(r.result);r.onerror=()=>ok(null);setTimeout(()=>ok(null),1500);}catch(e){ok(null);}});return this.db;},
  async leggi(k){if(!k)return null;const db=await this.apri();if(!db)return null;return new Promise(ok=>{try{const q=db.transaction("file").objectStore("file").get(k);q.onsuccess=()=>ok(q.result||null);q.onerror=()=>ok(null);}catch(e){ok(null);}});},
  async scrivi(k,v,man){const db=await this.apri();if(!db)return;try{const s=db.transaction("file","readwrite").objectStore("file");s.put(v,k);
    if(!man)return;const tieni=[man.dati,man.meta,man.luoghi,man.testi,man.cerca,man.fonti,man.foto,...Object.values(man.det||{})];const c=s.getAllKeys();c.onsuccess=()=>c.result.forEach(x=>{if(!tieni.includes(x))s.delete(x);});}catch(e){}}};
const LS={get(k){try{return localStorage.getItem(k);}catch(e){return null;}},set(k,v){try{localStorage.setItem(k,v);}catch(e){}}};
let MAN=null;
async function testo(nome){let t=await MEMO.leggi(nome);if(t)return t;const r=await fetch(nome);if(!r.ok)throw Error(nome+": "+r.status);t=await leggiAPezzi(r);MEMO.scrivi(nome,t,MAN);return t;}
/* 10/11/2026: il testo arriva e si decodifica a pezzi man mano che scende dalla rete (niente blocco unico a fine download) */
async function leggiAPezzi(r){if(!r.body||typeof TextDecoder==="undefined")return r.text();const rd=r.body.getReader(),dec=new TextDecoder(),parti=[];for(;;){const {done,value}=await rd.read();if(done)break;parti.push(dec.decode(value,{stream:true}));}parti.push(dec.decode());return parti.join("");}
window.prendiT=async n=>{const t=await testo((MAN&&MAN.testi)||n),R=t.split("\n"),T=[];
  const pausa=()=>new Promise(r=>{const m=new MessageChannel();m.port1.onmessage=()=>r();m.port2.postMessage(0);});
  if(R.length===1)return JSON.parse(t);for(let i=0;i<R.length-1;i++){await pausa();const a=JSON.parse(R[i]);for(const x of a)T.push(x);}await pausa();return [T,JSON.parse(R[R.length-1])];};
/* istantanea della prima schermata: chiave = nome dei dati */
const vF=document.getElementById('vF'),fp=document.getElementById('fp'),fbar=document.getElementById('fbar');
const ultimo=LS.get('luoghiNome');
const ist=ultimo&&!location.hash.slice(1)&&LS.get('ist:'+ultimo);
if(ist){try{const o=JSON.parse(ist);vF.innerHTML=o.v;if(o.p!=null)fp.innerHTML=o.p;if(o.b!=null)fbar.innerHTML=o.b;}catch(e){}}
window.__salvaIst=function(){if(window.__ist)return;window.__ist=1;const n=MAN&&MAN.luoghi;if(!n)return;
  const salva=()=>{if(location.hash.slice(1))return;LS.set('ist:'+n,JSON.stringify({v:vF.innerHTML,p:fp.innerHTML,b:fbar.innerHTML}));
    for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k&&k.startsWith('ist:')&&k!=='ist:'+n)localStorage.removeItem(k);}};
  setTimeout(salva,800);};
/* dati: IndexedDB (ultimo nome) in parallelo al manifest */
const ATTESO='"""+NOME+r"""';const pIdb=MEMO.leggi(ultimo);
const pPrimo=ultimo?null:fetch(ATTESO).then(r=>r.ok?leggiAPezzi(r):null).catch(()=>null);
const pMan=fetch("manifest.json",{cache:"no-store"}).then(r=>r.json()).catch(()=>{try{return JSON.parse(LS.get('man')||'null');}catch(e){return null;}});
(async()=>{MAN=await pMan;const nome=(MAN&&MAN.luoghi)||ultimo;if(!nome){vF.textContent='Dati non disponibili: controlla la connessione.';return;}
  let t=nome===ultimo?await pIdb:null;if(!t&&pPrimo&&nome===ATTESO){t=await pPrimo;if(t)MEMO.scrivi(nome,t,MAN);}if(!t)t=await testo(nome);else if(nome===ultimo)MEMO.scrivi(nome,t,MAN);
  LS.set('luoghiNome',nome);if(MAN)LS.set('man',JSON.stringify(MAN));
  const app=document.getElementById('app').textContent;
  /* 10/11/2026: dati e programma in due passi separati, così il telefono non resta bloccato in un solo blocco lungo */
  const pz=()=>new Promise(r=>{const m=new MessageChannel();m.port1.onmessage=()=>r();m.port2.postMessage(0);});
  /* le righe «const X=[...]» dei dati sono JSON: si leggono con JSON.parse, una per volta (più veloce che compilarle come programma) */
  const resto=[];for(const riga of t.split('\n')){const mm=/^const ([A-Za-z_$][\w$]*)=([\[{"].*);$/.exec(riga);let ok=false;
    if(mm){try{window[mm[1]]=JSON.parse(mm[2]);ok=true;}catch(e){}await pz();}if(!ok)resto.push(riga);}
  const s0=document.createElement('script');s0.textContent=resto.join('\n');if(nome!==ultimo&&ist)vF.innerHTML='';document.body.appendChild(s0);
  await new Promise(r=>{const m=new MessageChannel();m.port1.onmessage=()=>r();m.port2.postMessage(0);});
  const s=document.createElement('script');s.textContent=app+'\n;window.__pronta=1;';
  if(nome!==ultimo&&ist)vF.innerHTML='';
  document.body.appendChild(s);
})();
})();
"""
out = head + LOADER + '</script>\n<script type="text/plain" id="app">' + app.replace('</script', '<\\/script') + '</script>' + resto
open(os.path.join(G, 'filtri.html'), 'w').write(out)
print('filtri.html', len(out), 'byte;', NOME, len(data), 'byte')
