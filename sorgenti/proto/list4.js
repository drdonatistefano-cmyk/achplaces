 const catsOf=ps=>{const k={};for(const p of ps){if(SS){for(const s of p[3])if(st.sel[p[2]]&&st.sel[p[2]].has(s)){const kk=p[2]+'|'+s;k[kk]=(k[kk]||0)+1}}else k[p[2]]=(k[p[2]]||0)+1}
  return Object.entries(k).sort((a,b)=>b[1]-a[1]).map(([kk,v])=>{const[x,s]=kk.split('|');return `<span class="cat" style="${cv(x)}">${s?MM[x].s[s]:MM[x].e} ${v}${s?' '+s:''}</span>`}).join('')};
 const nCom=new Set(R.map(p=>p[1])).size;
 h+=`<div class="sum" id="sum"><b>${R.length}</b><span>luoghi in ${nCom} comuni${picked.length?'<br>'+esc(picked.join(', ')):''}${st.prov?'<br>📌 '+esc(st.prov.split('|')[1]):''}</span>${nFil()?`<button class="rst" data-a="reset">↺ Azzera tutto</button>`:''}</div>`;
 h+=`<div class="lab" id="grp">Mostra per</div><div class="grp">${GR.map(([k,e,l])=>`<button class="${st.grp===k?'on':''}" data-g="${k}"><span>${e}</span>${l}</button>`).join('')}</div>`;
 if(st.hist.length){const s=st.hist[st.hist.length-1];h+=`<button class="back" data-a="undrill">‹ Torna a ${esc(GN[s.grp])}</button>`}
 const row=(attr,title,sub,ps)=>`<button class="com" ${attr}><span class="bd"><h4>${title}</h4>${sub?`<span class="sub">${sub}</span>`:''}<span class="cats">${catsOf(ps)}</span></span><span class="tot"><b>${ps.length}</b><small>${ps.length===1?'luogo':'luoghi'}</small></span><span class="chev">›</span></button>`;
 const grpBy=(ps,kf)=>{const m=new Map();for(const p of ps){const k=kf(p);let a=m.get(k);if(!a){a=[];m.set(k,a)}a.push(p)}return m};
 const more=(n,w)=>n>st.lim?`<button class="more" data-a="more">Mostra altri ${Math.min(40,n-st.lim)} ${w} di ${n-st.lim}</button>`:'';
 const ord=(a,b)=>{const A=C[a[1]],B2=C[b[1]];return RG(A[2]).localeCompare(RG(B2[2]),'it')||A[1].localeCompare(B2[1],'it')||A[0].localeCompare(B2[0],'it')||a[0].localeCompare(b[0],'it')};
 if(!R.length)h+=`<div class="empty">Nessun luogo con questi filtri.<br>Prova a toglierne qualcuno.</div>`;
 else if(st.grp==='p'){const L=[...R].sort(ord);let cr=null;h+='<div class="flat">';
  L.slice(0,st.lim).forEach(p=>{const c=C[p[1]];if(c[2]!==cr){cr=c[2];h+=`<h2 class="fh">${esc(RG(c[2]))}</h2>`}h+=cardHTML(p,true)});h+='</div>'+more(L.length,'luoghi')}
 else if(st.grp==='c'){const m=grpBy(R,p=>p[1]);const L=[...m.entries()].sort((a,b)=>ord(a[1][0],b[1][0]));
  let cr=null,cp=null;L.slice(0,st.lim).forEach(([ci,ps])=>{const c=C[ci];
   if(c[2]!==cr){if(cr!==null)h+='</section>';cr=c[2];cp=null;h+=`<section class="reg"><h2>${esc(RG(c[2]))}</h2>`}
   if(c[1]!==cp){cp=c[1];h+=`<div class="pv">${esc(pvName(c))}</div>`}
   const aw=[...c[3]].filter(x=>AWL[x]).map(x=>`<span class="aw">${AWL[x]}</span>`).join('');
   h+=row(`data-c="${ci}"`,esc(c[0])+aw,'',ps)});h+='</section>'+more(L.length,'comuni')}
 else if(st.grp==='v'){const m=grpBy(R,p=>{const c=C[p[1]];return c[2]+'|'+c[1]});const L=[...m.entries()].sort((a,b)=>ord(a[1][0],b[1][0]));
  let cr=null;L.slice(0,st.lim).forEach(([k,ps])=>{const c=C[ps[0][1]];if(c[2]!==cr){if(cr!==null)h+='</section>';cr=c[2];h+=`<section class="reg"><h2>${esc(RG(c[2]))}</h2>`}
   const n=new Set(ps.map(p=>p[1])).size;h+=row(`data-pv="${esc(k)}"`,esc(pvName(c)),`${n} ${n===1?'comune':'comuni'}`,ps)});h+='</section>'+more(L.length,'province')}
 else if(st.grp==='r'){const O=['nord','centro','sud'];const m=grpBy(R,p=>C[p[1]][2]);const L=[...m.entries()].sort((a,b)=>O.indexOf(AREA(a[0]))-O.indexOf(AREA(b[0]))||RG(a[0]).localeCompare(RG(b[0]),'it'));
  let ca=null;L.forEach(([r,ps])=>{if(AREA(r)!==ca){if(ca!==null)h+='</section>';ca=AREA(r);h+=`<section class="reg"><h2>${AE[ca]} ${AL[ca]}</h2>`}
   const n=new Set(ps.map(p=>p[1])).size,np=new Set(ps.map(p=>C[p[1]][1])).size;h+=row(`data-rg="${r}"`,esc(RG(r)),`${np} ${np===1?'provincia':'province'} · ${n} comuni`,ps)});h+='</section>'}
 else{const m=grpBy(R,p=>AREA(C[p[1]][2]));['nord','centro','sud'].filter(a=>m.has(a)).forEach(a=>{const ps=m.get(a);const nr=new Set(ps.map(p=>C[p[1]][2])).size,n=new Set(ps.map(p=>p[1])).size;
   h+=row(`data-ar="${a}"`,AE[a]+' '+AL[a],`${nr} ${nr===1?'regione':'regioni'} · ${n} comuni`,ps)})}
