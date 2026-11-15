t=open('v12_tail.html').read();h=open('v12_head.html').read()
def R(a,b):
    global t
    assert t.count(a)==1,a[:70]; t=t.replace(a,b,1)
R("const st={regs:new Set(),prov:null,","const st={regs:new Set(),provs:new Set(),coms:new Set(),prov:null,")
# filter
R("return(!st.near||!st.near.km||kmC(p[1],st.near)<=st.near.km)&&(",
  "return(!st.near||!st.near.km||kmC(p[1],st.near)<=st.near.km)&&(!useReg||((!st.provs.size||st.provs.has(c[2]+'|'+c[1]))&&(!st.coms.size||st.coms.has(p[1]))))&&(")
R("const comsIn=()=>C.map((c,ci)=>[c,ci]).filter(([c])=>(!st.regs.size||st.regs.has(c[2]))&&(!st.prov||st.prov===c[2]+'|'+c[1]));",
  "const comsIn=()=>C.map((c,ci)=>[c,ci]).filter(([c])=>(!st.regs.size||st.regs.has(c[2]))&&(!st.provs.size||st.provs.has(c[2]+'|'+c[1])));")
R("const provV=st.prov?st.prov.split('|')[1]:'Tutte';",
  "const provV=st.provs.size?(st.provs.size===1?[...st.provs][0].split('|')[1]:st.provs.size+' province'):'Tutte';const comV=st.coms.size?(st.coms.size===1?C[[...st.coms][0]][0]:st.coms.size+' comuni'):'Tutti';")
R("<button class=\"mopt${st.prov===k?' on':''}\" data-pp=\"${esc(k)}\">","<button class=\"mopt${st.provs.has(k)?' on':''}\" data-pp=\"${esc(k)}\">")
R("<b>Province</b><span>${st.regs.size?esc(regV):'tutta Italia'}</span>","<b>Province</b><span>puoi sceglierne più di una</span>")
R("<b>Comuni</b><span>tocca un comune per aprirlo</span></div><input class=\"mpq\" id=\"cq\" type=\"search\" placeholder=\"Cerca un comune…\" autocomplete=\"off\"><div class=\"mlist\" id=\"cqlist\"></div><div class=\"mpfoot\"><button class=\"mpdone\" data-a=\"popclose\">Chiudi</button></div>",
  "<b>Comuni</b><span>puoi sceglierne più di uno</span></div><input class=\"mpq\" id=\"cq\" type=\"search\" placeholder=\"Cerca un comune…\" autocomplete=\"off\"><div class=\"mlist\" id=\"cqlist\"></div><div class=\"mpfoot\"><button class=\"mpall\" data-cc=\"\">Tutti i comuni</button><button class=\"mpdone\" data-a=\"popclose\">Fatto</button></div>")
R('<span class="mv">Scegli…</span>','<span class="mv">${esc(comV)}</span>')
R("map(([c,ci])=>`<button class=\"mopt nocb\" data-c=\"${ci}\"><span class=\"t\">${esc(c[0])}</span><small>${esc(c[1])}</small></button>`)",
  "map(([c,ci])=>`<button class=\"mopt${st.coms.has(ci)?' on':''}\" data-cc=\"${ci}\"><span class=\"t\">${esc(c[0])}</span><small>${esc(c[1])}</small></button>`)")
# province toggle multi; comune toggle multi
R("if(d.pp!==undefined){st.prov=d.pp&&st.prov!==d.pp?d.pp:null;if(st.prov){const r=st.prov.split('|')[0];if(!st.regs.has(r))st.regs=new Set([r])}st.hist=[];st.lim=40;st.pop=null;renderF();return}",
  "if(d.pp!==undefined){if(!d.pp)st.provs.clear();else st.provs.has(d.pp)?st.provs.delete(d.pp):st.provs.add(d.pp);for(const c of [...st.coms])if(st.provs.size&&!st.provs.has(C[c][2]+'|'+C[c][1]))st.coms.delete(c);st.hist=[];st.lim=40;renderF();return}\n if(d.cc!==undefined){if(d.cc==='')st.coms.clear();else{const ci=+d.cc;st.coms.has(ci)?st.coms.delete(ci):st.coms.add(ci)}document.querySelectorAll('#cqlist [data-cc]').forEach(x=>x.classList.toggle('on',st.coms.has(+x.dataset.cc)));const mv=document.querySelector('[data-pop=com] .mv');if(mv)mv.textContent=st.coms.size?(st.coms.size===1?C[[...st.coms][0]][0]:st.coms.size+' comuni'):'Tutti';st.hist=[];st.lim=40;renderF(true);return}")
# region toggle prunes provinces/comuni
R("if(d.reg){st.regs.has(d.reg)?st.regs.delete(d.reg):st.regs.add(d.reg);st.prov=null;",
  "if(d.reg){st.regs.has(d.reg)?st.regs.delete(d.reg):st.regs.add(d.reg);st.prov=null;for(const k of [...st.provs])if(st.regs.size&&!st.regs.has(k.split('|')[0]))st.provs.delete(k);for(const c of [...st.coms])if(st.regs.size&&!st.regs.has(C[c][2]))st.coms.delete(c);")
R("else if(d.a==='regall'){st.regs.clear();","else if(d.a==='regall'){st.provs.clear();st.coms.clear();st.regs.clear();")
R("if(d.a==='resetL'){st.regs.clear();","if(d.a==='resetL'){st.provs.clear();st.coms.clear();st.regs.clear();")
R("else if(d.a==='reset'){st.pop=null;","else if(d.a==='reset'){st.provs.clear();st.coms.clear();st.pop=null;")
R("const nFil=()=>(st.near?1:0)+","const nFil=()=>(st.provs.size?1:0)+(st.coms.size?1:0)+(st.near?1:0)+")
R("if(st.q)bits.push('«'+st.q+'»');","if(st.provs.size)bits.push([...st.provs].map(k=>k.split('|')[1]).join(', '));if(st.coms.size)bits.push([...st.coms].map(c=>C[c][0]).join(', '));if(st.q)bits.push('«'+st.q+'»');")
open('v13_head.html','w').write(h);open('v13_tail.html','w').write(t)
print('v13 ok')
