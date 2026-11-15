t=open('v11_tail.html').read();h=open('v11_head.html').read()
def R(a,b):
    global t
    assert t.count(a)==1,a[:70]; t=t.replace(a,b,1)
def H(a,b):
    global h
    assert h.count(a)==1,a[:70]; h=h.replace(a,b,1)
DLG=open('eat_dialog.html').read().replace("dal punto del luogo, o dal centro del suo comune se il punto esatto non è noto (≈)","dal centro del comune di ogni luogo");CSS=open('eat.css').read()
# distance helper + km filter in base()
R("function base(useReg=true){const q=norm(st.q);return P.filter(p=>{const c=C[p[1]];return(",
  "function kmC(ci,o){const c=C[ci];if(c[6]==null)return 1e9;const r=Math.PI/180,dl=(c[6]-o.lat)*r,dn=(c[7]-o.lng)*r,a=Math.sin(dl/2)**2+Math.cos(o.lat*r)*Math.cos(c[6]*r)*Math.sin(dn/2)**2;return 12742*Math.asin(Math.sqrt(a))}\nfunction base(useReg=true){const q=norm(st.q);return P.filter(p=>{const c=C[p[1]];return(!st.near||!st.near.km||kmC(p[1],st.near)<=st.near.km)&&(")
# button opens dialog
i=t.index(" if(d.a==='near'){");j=t.index(" if(d.a==='undrill')",i)
t=t[:i]+" if(d.a==='near'){openEat();return}\n"+t[j:]
R("if(st.near)bits.push('📍 vicino a te');","if(st.near)bits.push('📍 entro '+Math.round(st.near.km)+' km da '+st.near.label);")
JS=r'''
<script>
const KM_PER_MIN=0.5,EAT={lat:null,lng:null,label:""};
const E$=id=>document.getElementById(id);
const fmtMin=mn=>mn>=60?(mn%60?Math.floor(mn/60)+" h "+(mn%60)+" min":(mn/60)+(mn===60?" ora":" ore")):mn+" min";
const fmtKm=x=>x<10?x.toLocaleString("it-IT",{maximumFractionDigits:1}):Math.round(x).toLocaleString("it-IT");
const effKm=()=>Math.min(+E$("eat-km").value,+E$("eat-min").value*KM_PER_MIN);
function eatUpdate(){
  const km=+E$("eat-km").value,mn=+E$("eat-min").value;
  E$("eat-kmv").textContent=km+" km";E$("eat-minv").textContent=fmtMin(mn);
  document.querySelectorAll(".eatchips").forEach(g=>g.querySelectorAll("button").forEach(b=>b.classList.toggle("on",+b.dataset.v===+E$(g.dataset.for).value)));
  const eff=effKm(),lim=km<=mn*KM_PER_MIN?"dal raggio":"dal tempo in auto",has=EAT.lat!==null;
  const n=has?P.filter(p=>kmC(p[1],EAT)<=eff).length:0;
  E$("eat-res").innerHTML=has?`Entro circa <b>${fmtKm(eff)} km</b> da ${esc(EAT.label)} (il limite viene ${lim}): <b>${n} ${n===1?"luogo":"luoghi"}</b> in tutta la guida.`:"Scegli da dove parti.";
  const a=E$("eat-apply");a.textContent=has?`Mostra ${n} ${n===1?"luogo":"luoghi"}`:"Mostra i luoghi";
  if(has&&n)a.removeAttribute("aria-disabled");else a.setAttribute("aria-disabled","true");
  E$("eat-off").hidden=!st.near;
}
function setOrigin(lat,lng,label){EAT.lat=lat;EAT.lng=lng;EAT.label=label;eatUpdate();}
function openEat(){eatUpdate();try{E$("eat").showModal();}catch(e){E$("eat").setAttribute("open","");}}
E$("eat-coms").innerHTML=C.filter(c=>c[6]!=null).map(c=>`<option value="${esc(c[0])} (${esc(c[1])})"></option>`).join("");
E$("eat").addEventListener("click",e=>{if(e.target===E$("eat"))E$("eat").close();});
E$("eat-km").oninput=eatUpdate;E$("eat-min").oninput=eatUpdate;
E$("eat-txt").addEventListener("input",()=>{const v=E$("eat-txt").value.trim().toLowerCase(),s=E$("eat-st");
  const c=C.find(x=>x[6]!=null&&(`${x[0]} (${x[1]})`.toLowerCase()===v||x[0].toLowerCase()===v));
  if(c){s.className="eatst ok";s.textContent=`Partenza dal centro di ${c[0]}.`;setOrigin(c[6],c[7],"il centro di "+c[0]);}
  else if(v){s.className="eatst";s.textContent="Scegli un comune dall'elenco.";}});
document.querySelectorAll(".eatchips").forEach(g=>g.onclick=e=>{const b=e.target.closest("button");if(!b)return;E$(g.dataset.for).value=b.dataset.v;eatUpdate();});
E$("eat-geo").onclick=()=>{const s=E$("eat-st");
  if(!navigator.geolocation){s.className="eatst bad";s.textContent="Il browser non fornisce la posizione: scegli un comune di partenza.";return;}
  s.className="eatst";s.textContent="Cerco la tua posizione…";
  navigator.geolocation.getCurrentPosition(p=>{E$("eat-txt").value="";s.className="eatst ok";s.textContent=`Posizione trovata (precisione circa ${Math.round(p.coords.accuracy)} m).`;setOrigin(p.coords.latitude,p.coords.longitude,"te");},
    ()=>{s.className="eatst bad";s.textContent="Posizione non disponibile o non autorizzata: scegli un comune di partenza.";},{enableHighAccuracy:false,timeout:10000,maximumAge:300000});};
E$("eat-apply").onclick=()=>{if(EAT.lat===null)return;st.near={lat:EAT.lat,lng:EAT.lng,km:effKm(),label:EAT.label};st.nearErr='';if(st.grp!=='p')st.grp='c';st.hist=[];st.lim=40;E$("eat").close();renderF();window.scrollTo(0,0);};
E$("eat-off").onclick=()=>{st.near=null;E$("eat").close();renderF();};
</script>'''
R("</script></body></html>","</script>"+DLG+JS+"</body></html>")
# button style: active state when near on
H('</style>',CSS+''':root{--terra-ink:var(--terra);--ok:#2e7d4f;--bad:#b3261e}
.tabs #tabL{display:none!important}
.eatfoot small{display:block}
</style>''')
open('v12_head.html','w').write(h);open('v12_tail.html','w').write(t)
print('v12 ok')
