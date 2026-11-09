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
    open(f'/home/claude/achs-places-guide/data/spec-{m.group(2)}.txt','a').write('\n'+t.strip()+'\n')
    shutil.move(f,B+'fatte/'+b)
    if os.path.exists(r): shutil.move(r,B+'fatte/rinviati-'+b)
    print(b,m.group(2),n)
