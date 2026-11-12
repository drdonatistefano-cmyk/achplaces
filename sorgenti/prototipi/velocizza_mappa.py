# Velocizza il prototipo «Luoghi sulla mappa» (12/11/2026). Si applica all'index.html pubblicato (orig.html) e scrive srv2/index.html + srv2/dati.js.
# Misure a 390 px con CPU 4 volte piu' lenta: apertura 1,7 s -> 0,7 s; blocco piu' lungo 553 -> 208 ms; ridisegno dopo zoom e filtri circa dimezzato. Aspetto identico.
import re,json,sys
s=open('orig.html').read()
n=0
def rep(a,b,cnt=1):
    global s,n
    assert s.count(a)==cnt,(a[:80],s.count(a)); s=s.replace(a,b); n+=1
# 1 dati come JSON (si legge 2-3 volte piu' in fretta di un oggetto JavaScript)
i=s.find('const DATA=');j=s.find(';\n',i)
data=json.loads(s[i+len('const DATA='):j])
dj=json.dumps(data,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
s=s[:i]+"const DATA=JSON.parse(document.getElementById('dati').textContent);document.getElementById('dati').remove();"+s[j:]
k=s.rfind('<script>',0,i)
s=s[:k]+'<script type="application/json" id="dati">'+dj+'</script>\n'+s[k:]
# 2 caratteri senza bloccare la prima visualizzazione
rep('<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">',
    '<link rel="preload" as="style" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap" onload="this.onload=null;this.rel=\'stylesheet\'"><noscript><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600&display=swap"></noscript>')
# 3 ricerca: la parola si normalizza una volta sola
rep("if(S.q){const w=fold(S.q.trim());","if(S.q){const w=QF;")
rep("function conti(){const key=","let QF='';function conti(){QF=S.q?fold(S.q.trim()):'';const key=")
# 4 alone delle bolle calcolato una volta
rep("g.textAlign='center';g.textBaseline='middle';\n  for(let i=keep.length-1;","g.textAlign='center';g.textBaseline='middle';const HF=TH.fill.replace(/[\\d.]+\\)$/,'0.08)');\n  for(let i=keep.length-1;")
rep("g.fillStyle=sel?'rgba(255,184,107,.10)':TH.fill.replace(/[\\d.]+\\)$/,'0.08)');","g.fillStyle=sel?'rgba(255,184,107,.10)':HF;")
# 5 prima la mappa, poi testi ed elenco (nel fotogramma dopo)
rep("  layer.style.transform='';\n  let near=null,bd=1e18;","  layer.style.transform='';\n  const gen=++GEN;requestAnimationFrame(()=>setTimeout(()=>{if(gen!==GEN)return;\n  let near=null,bd=1e18;")
rep("  if(S.sel!=null&&!inV(C[S.sel].x,C[S.sel].y,0))S.sel=null;\n  lista(m,inV);}","  if(S.sel!=null&&!inV(C[S.sel].x,C[S.sel].y,0))S.sel=null;\n  lista(m,inV);},0));}")
rep("let R={cx:S.cx,cy:S.cy,k:S.k},GR=[],LEV=-1,timer=0;","let R={cx:S.cx,cy:S.cy,k:S.k},GR=[],LEV=-1,timer=0,GEN=0,LK='',LJ=0;")
# 6 elenco: niente lavoro se non cambia; prime righe subito, le altre a pezzi
rep("  $('items').innerHTML=out.length?out.map(pi=>{","  const key=(sel??'')+'/'+out.join(',')+'/'+TH.n;if(key===LK)return;LK=key;const riga=pi=>{")
rep("<a href=\"${photoUrl(p)}\" target=\"_blank\" rel=\"noopener\">${ic('cam')}Foto</a></div></div>`;}).join('')\n    :'<div class=\"empty\">Nessun luogo qui con questi filtri. Allarga la mappa o togli un filtro.</div>';}",
    "<a href=\"${photoUrl(p)}\" target=\"_blank\" rel=\"noopener\">${ic('cam')}Foto</a></div></div>`;};\n  const box=$('items'),job=++LJ;if(!out.length){box.innerHTML='<div class=\"empty\">Nessun luogo qui con questi filtri. Allarga la mappa o togli un filtro.</div>';return;}\n  box.innerHTML=out.slice(0,12).map(riga).join('');let i=12;\n  const piu=()=>{if(job!==LJ||i>=out.length)return;box.insertAdjacentHTML('beforeend',out.slice(i,i+17).map(riga).join(''));i+=17;(window.requestIdleCallback||setTimeout)(piu);};(window.requestIdleCallback||setTimeout)(piu);}")
# 7 righe fuori schermo: il browser non le impagina finche' non servono
rep(".row{border-radius:16px;",".row{content-visibility:auto;contain-intrinsic-size:auto 104px;border-radius:16px;")
# 8 caratteri arrivati: ridisegno le scritte della mappa
rep("misura();{const h=casa();S.cx=h[0];S.cy=h[1];}filtri(desk());disegnaFiltri();sheetTo('low',false);",
    "misura();{const h=casa();S.cx=h[0];S.cy=h[1];}filtri(desk());disegnaFiltri();sheetTo('low',false);\ntry{document.fonts.ready.then(()=>{if(W)completo();});}catch(e){}")
open('srv2/index.html','w').write(s)
print('ok',n,len(s))
# 9 si disegnano solo le bolle che cadono nel foglio (le altre servono solo per il tocco)
s=open('srv2/index.html').read()
a="  for(let i=keep.length-1;i>=0;i--){const o=keep[i],x=o.px+MG,y=o.py+MG,r=o.r,sel=o.cs.length===1&&S.sel===o.cs[0];"
assert s.count(a)==1
s=s.replace(a,"  const CW=W+2*MG,CH=H+2*MG;\n  for(let i=keep.length-1;i>=0;i--){const o=keep[i],x=o.px+MG,y=o.py+MG,r=o.r,sel=o.cs.length===1&&S.sel===o.cs[0];if(x<-r*2-80||y<-r*2-20||x>CW+r*2+80||y>CH+r*2+20)continue;")
open('srv2/index.html','w').write(s)
print('cull ok')
# 10 i dati in un file a parte, scaricato in parallelo: la pagina si legge subito
s=open('srv2/index.html').read()
i=s.find('<script type="application/json" id="dati">');j=s.find('</script>\n',i)
dj=s[i+len('<script type="application/json" id="dati">'):j]
open('srv2/dati.js','w').write('window.DATA=JSON.parse('+json.dumps(dj,ensure_ascii=False)+');\n')
s=s[:i]+'<script src="dati.js"></script>\n'+s[j+len('</script>\n'):]
a="const DATA=JSON.parse(document.getElementById('dati').textContent);document.getElementById('dati').remove();"
assert s.count(a)==1; s=s.replace(a,"const DATA=window.DATA;")
a='<meta charset="utf-8">'
assert s.count(a)==1; s=s.replace(a,a+'\n<link rel="preload" href="dati.js" as="script">')
open('srv2/index.html','w').write(s)
print('file dati ok',len(s))
