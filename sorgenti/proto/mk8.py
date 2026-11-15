t=open('v7_tail.html').read();h=open('v7_head.html').read()
def R(a,b):
    global t
    assert a in t,a[:70]; t=t.replace(a,b,1)
def H(a,b):
    global h
    assert a in h,a[:70]; h=h.replace(a,b,1)
R('<input class="search" id="q" type="search" placeholder="🔍 Cerca un comune o un luogo" value="${esc(st.q)}" autocomplete="off">',
  '<div class="qrow"><input class="search" id="q" type="search" placeholder="🔍 Cerca un comune o un luogo" value="${esc(st.q)}" autocomplete="off"><button class="near${st.near?\' on\':\'\'}" data-a="near" aria-pressed="${!!st.near}">${st.nearBusy?\'⏳\':\'📍\'} <span>Vicino a me</span></button></div>${st.nearErr?`<div class="nerr">${esc(st.nearErr)}</div>`:\'\'}')
R("else if(st.grp==='c'){","""else if(st.near&&(st.grp==='c'||st.grp==='p')){const km=ci=>{const c=C[ci];if(c[6]==null)return 1e9;const r=Math.PI/180,dl=(c[6]-st.near.lat)*r,dn=(c[7]-st.near.lng)*r,a=Math.sin(dl/2)**2+Math.cos(st.near.lat*r)*Math.cos(c[6]*r)*Math.sin(dn/2)**2;return 12742*Math.asin(Math.sqrt(a))};
  const fk=k=>k>=1e9?'':(k<10?k.toFixed(1).replace('.',','):Math.round(k))+' km';
  h+=`<h2 class="fh">📍 Più vicini a te</h2>`;
  if(st.grp==='p'){const L=[...R].map(p=>[km(p[1]),p]).sort((a,b)=>a[0]-b[0]);h+='<div class="flat">';L.slice(0,st.lim).forEach(([k,p])=>{h+=`<div class="kmw"><span class="kmb">${fk(k)}</span>${cardHTML(p,true)}</div>`});h+='</div>'+more(L.length,'luoghi')}
  else{const m=grpBy(R,p=>p[1]);const L=[...m.entries()].map(([ci,ps])=>[km(ci),ci,ps]).sort((a,b)=>a[0]-b[0]);h+='<section class="reg">';L.slice(0,st.lim).forEach(([k,ci,ps])=>{const c=C[ci];const aw=[...c[3]].filter(x=>AWL[x]).map(x=>`<span class="aw">${AWL[x]}</span>`).join('');h+=row(`data-c="${ci}"`,esc(c[0])+aw,`📍 ${fk(k)} · ${esc(pvName(c))}`,ps)});h+='</section>'+more(L.length,'comuni')}}
 else if(st.grp==='c'){""")
R(" if(d.a==='undrill'){history.back();return}",""" if(d.a==='near'){if(st.near){st.near=null;st.nearErr='';renderF();return}
  if(!navigator.geolocation){st.nearErr='Il dispositivo non permette di conoscere la posizione.';renderF();return}
  st.nearBusy=true;st.nearErr='';renderF();
  navigator.geolocation.getCurrentPosition(pos=>{st.nearBusy=false;st.near={lat:pos.coords.latitude,lng:pos.coords.longitude};if(st.grp!=='p')st.grp='c';st.hist=[];st.lim=40;renderF();window.scrollTo(0,0)},
   err=>{st.nearBusy=false;st.nearErr=err&&err.code===1?'Posizione non consentita: abilitala nelle impostazioni del browser per usare «Vicino a me».':'Posizione non disponibile in questo momento.';renderF()},{enableHighAccuracy:false,timeout:10000,maximumAge:300000});return}
 if(d.a==='undrill'){history.back();return}""")
R("else if(d.a==='reset'){st.regs.clear();","else if(d.a==='reset'){st.near=null;st.nearErr='';st.regs.clear();")
R("const nFil=()=>","const nFil=()=>(st.near?1:0)+")
R("if(st.q)bits.push('«'+st.q+'»');","if(st.q)bits.push('«'+st.q+'»');if(st.near)bits.push('📍 vicino a te');")
H('</style>',r""".qrow{display:flex;gap:6px;align-items:stretch}
.qrow .search{flex:1;min-width:0}
.near{flex:none;display:inline-flex;align-items:center;gap:5px;height:40px;padding:0 13px;border-radius:12px;border:1px solid var(--line);background:var(--paper);color:var(--ink);font-size:14px;font-weight:700;cursor:pointer;white-space:nowrap}
.near.on{background:var(--terra);border-color:var(--terra);color:#fff}
@media(max-width:380px){.near span{display:none}}
.nerr{font-size:12.5px;color:#9a3b2b;padding:2px 4px}
.kmw{position:relative}
.kmb{position:absolute;top:-8px;right:10px;z-index:2;background:var(--terra);color:#fff;font-size:11.5px;font-weight:800;padding:3px 8px;border-radius:999px}
</style>""")
open('v8_tail.html','w').write(t);open('v8_head.html','w').write(h)
