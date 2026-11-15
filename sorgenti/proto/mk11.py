t=open('v10_tail.html').read();h=open('v10_head.html').read()
def R(a,b):
    global t
    assert t.count(a)==1,a[:70]; t=t.replace(a,b,1)
R('function openSheet(i){','function openSheet(i){window.__sheetP=i;')
R("function closeSheet(){","function closeSheet(){window.__sheetP=null;")
# lazy load of long texts after first paint
R("renderF();\n</script>","""renderF();
setTimeout(()=>{fetch(TESTI).then(r=>r.json()).then(a=>{const T=a[0],L=a[1];for(let i=0;i<P.length;i++){P[i][5]=T[i][0];P[i][6]=T[i][1]}for(let i=0;i<C.length;i++)C[i][4]=L[i];window.__testi=1;renderF(true);if(st.com!=null)renderL();if(window.__sheetP!=null)openSheet(window.__sheetP)}).catch(()=>{})},0);
</script>""")
t='for(const p of P){p[7]=S7[p[7]];p[8]=S8[p[8]]}\n'+t
open('v11_head.html','w').write(h);open('v11_tail.html','w').write(t)
print('v11 ok')
