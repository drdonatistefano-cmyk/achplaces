"""Unisce le bozze in data/spec-<SIGLA>.txt. Minimo (9/11): 3 luoghi per i comuni premiati (Borghi, Arancioni, UNESCO), 2 per gli altri."""
import glob,os,re,shutil
B='/home/claude/bozze/'
for f in sorted(glob.glob(B+'*.txt')):
    b=os.path.basename(f)
    if b.startswith('rinviati'):continue
    t=open(f).read();m=re.search(r'^@ ([^|]+)\|[^|]+\|\s*([A-Z]{2})\s*\|[^|]*\|?(.*)$',t,re.M)
    if not m: print('SENZA INTESTAZIONE',b);continue
    premi=m.group(3).strip(); n=len(re.findall(r'^- ',t,re.M)); minimo=3 if premi else 2
    r=B+'rinviati-'+b
    if n<minimo:
        if os.path.exists(r): os.remove(f)
        else: shutil.move(f,r)
        print("RINVIATO",b,n);continue
    # 10/11/2026: le vecchie sigle sarde (OT, OG, CI, VS) diventano quelle usate dalla guida (SS, NU, SU)
    sig={'OT':'SS','OG':'NU','CI':'SU','VS':'SU'}.get(m.group(2),m.group(2))
    if sig!=m.group(2): t=re.sub(r'^(@ [^|]+\|[^|]+\|\s*)'+m.group(2)+r'(\s*\|)',r'\g<1>'+sig+r'\2',t,count=1,flags=re.M)
    open(f'/home/claude/achs-places-guide/data/spec-{sig}.txt','a').write('\n'+t.strip()+'\n')
    shutil.move(f,B+'fatte/'+b)
    if os.path.exists(r): shutil.move(r,B+'fatte/rinviati-'+b)
    print(b,m.group(2),n)
