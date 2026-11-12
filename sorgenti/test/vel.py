# Tre punti di vista: A turista 4G primo accesso, B uso (interazioni) CPU x4, C ritorno con cache
import sys,json,time
from playwright.sync_api import sync_playwright
BASE=sys.argv[1] if len(sys.argv)>1 else "http://localhost:8790/"
INIT="""window.__LT=[];window.__EV=[];window.__LCP=0;
new PerformanceObserver(l=>{for(const e of l.getEntries())__LT.push([Math.round(e.startTime),Math.round(e.duration)])}).observe({type:'longtask',buffered:true});
new PerformanceObserver(l=>{for(const e of l.getEntries())__LCP=Math.round(e.startTime)}).observe({type:'largest-contentful-paint',buffered:true});
try{new PerformanceObserver(l=>{for(const e of l.getEntries())if(e.interactionId)__EV.push([e.name,Math.round(e.duration)])}).observe({type:'event',buffered:true,durationThreshold:16});}catch(e){}"""
RETI={'4G':dict(latency=150,downloadThroughput=int(4e6/8),uploadThroughput=int(1.5e6/8)),
      '3G':dict(latency=300,downloadThroughput=int(1.6e6/8),uploadThroughput=int(0.75e6/8))}
def ctx(b,phone=True):
  return b.new_context(viewport={"width":390,"height":844} if phone else {"width":1366,"height":900},device_scale_factor=3 if phone else 1,is_mobile=phone,has_touch=phone,
    geolocation={'latitude':44.4949,'longitude':11.3426},permissions=['geolocation'])
def prep(c,pg,rete,cpu):
  s=c.new_cdp_session(pg);s.send("Emulation.setCPUThrottlingRate",{"rate":cpu})
  s.send("Network.enable");
  if rete:s.send("Network.emulateNetworkConditions",{"offline":False,**RETI[rete]})
  return s
def carica(pg,s,url,pronto,timeout=60000):
  byt={'n':0,'req':[]}
  def fin(p):
    byt['n']+=p.get('encodedDataLength',0)
  s.on("Network.loadingFinished",fin)
  t0=time.time();pg.goto(url,wait_until='commit')
  pg.wait_for_function(pronto,timeout=timeout);tp=time.time()-t0
  pg.wait_for_timeout(2500)
  r=pg.evaluate("({fcp:Math.round((performance.getEntriesByName('first-contentful-paint')[0]||{}).startTime||0),lcp:__LCP,lt:__LT.slice()})")
  r['pronto_ms']=round(tp*1000);r['kb']=round(byt['n']/1024);r['tbt']=sum(max(0,d-50) for _,d in r['lt']);r['maxlt']=max([d for _,d in r['lt']],default=0)
  del r['lt'];return r
PAG={'guida':('index.html',"document.querySelectorAll('#grid > *').length>5"),
     'mappa':('filtri.html',"window.__mappa&&document.querySelector('canvas')")}
def vistaA(b,rete):
  out={}
  for k,(u,pr) in PAG.items():
    c=ctx(b);pg=c.new_page();pg.add_init_script(INIT);s=prep(c,pg,rete,4)
    out[k]=carica(pg,s,BASE+u,pr);c.close()
  return out
def vistaC(b):
  out={}
  for k,(u,pr) in PAG.items():
    c=ctx(b);pg=c.new_page();pg.add_init_script(INIT);s=prep(c,pg,'4G',4)
    carica(pg,s,BASE+u,pr);pg.goto('about:blank');
    out[k]=carica(pg,s,BASE+u,pr);c.close()
  return out
def interazioni_guida(pg):
  res={}
  def mis(nome,fn):
    pg.evaluate("__LT.length=0;__EV.length=0");fn();pg.wait_for_timeout(900)
    ev=pg.evaluate("__EV.slice()");lt=pg.evaluate("__LT.slice()")
    res[nome]=dict(inp=max([d for _,d in ev],default=0),maxlt=max([d for _,d in lt],default=0))
  if pg.is_visible('#ftog'):mis('apri filtri',lambda:pg.tap('#ftog'))
  mis('categoria',lambda:pg.locator('#g-cat button, #g-cat .chip').nth(1).tap())
  mis('togli categoria',lambda:pg.locator('#g-cat button, #g-cat .chip').nth(1).tap())
  q=pg.locator('#q')
  if q.is_visible():mis('cerca "torre"',lambda:(q.tap(),pg.keyboard.type('torre',delay=80)))
  mis('scroll',lambda:[ (pg.mouse.wheel(0,1500),pg.wait_for_timeout(200)) for _ in range(8)])
  pg.mouse.wheel(0,-20000);pg.wait_for_timeout(500);card=pg.locator('#grid > *').nth(2)
  mis('apri scheda',lambda:card.tap())
  return res
def interazioni_mappa(pg):
  res={}
  def mis(nome,fn):
    pg.evaluate("__LT.length=0;__EV.length=0");fn();pg.wait_for_timeout(900)
    ev=pg.evaluate("__EV.slice()");lt=pg.evaluate("__LT.slice()")
    res[nome]=dict(inp=max([d for _,d in ev],default=0),maxlt=max([d for _,d in lt],default=0))
  mis('zoom +',lambda:pg.tap('#zin'))
  mis('trascina',lambda:(pg.mouse.move(200,300),pg.mouse.down(),[pg.mouse.move(200+i*8,300+i*5) for i in range(20)],pg.mouse.up()))
  mis('posizione',lambda:(pg.tap('#gps'),pg.wait_for_timeout(800)))
  it=pg.locator('#list .it').first
  if it.count():mis('apri luogo',lambda:it.tap())
  mis('casa',lambda:(pg.keyboard.press('Escape'),pg.tap('#home')))
  return res
def vistaB(b):
  out={}
  c=ctx(b);pg=c.new_page();pg.add_init_script(INIT);s=prep(c,pg,None,4)
  pg.goto(BASE+'index.html');pg.wait_for_function(PAG['guida'][1]);pg.wait_for_timeout(4000)
  out['guida']=interazioni_guida(pg);c.close()
  c=ctx(b);pg=c.new_page();pg.add_init_script(INIT);s=prep(c,pg,None,4)
  pg.goto(BASE+'filtri.html');pg.wait_for_function(PAG['mappa'][1]);pg.wait_for_timeout(3000)
  out['mappa']=interazioni_mappa(pg);c.close()
  return out
with sync_playwright() as p:
  b=p.chromium.launch()
  V=sys.argv[3].split(',') if len(sys.argv)>3 else ['A_4G','A_3G','C_ritorno','B_uso']
  F={'A_4G':lambda:vistaA(b,'4G'),'A_3G':lambda:vistaA(b,'3G'),'C_ritorno':lambda:vistaC(b),'B_uso':lambda:vistaB(b)}
  R={k:F[k]() for k in V}
  b.close()
open(sys.argv[2] if len(sys.argv)>2 else "/tmp/perf/r.json","w").write(json.dumps(R,ensure_ascii=False));print(json.dumps(R,ensure_ascii=False))
