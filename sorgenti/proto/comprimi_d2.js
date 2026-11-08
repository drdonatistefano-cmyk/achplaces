// 8/11/2026: d2.js -> versione con dizionari (categoria e sottocategorie dei luoghi come numeri) + verifica di equivalenza
const fs=require('fs');const src=fs.readFileSync(process.argv[2],'utf8');
const leggi=t=>new Function(t+';return {TESTI,S7,S8,C,P};')();
const A=leggi(src);
const DC=[],DS=[];const ix=(L,v)=>{let i=L.indexOf(v);if(i<0){L.push(v);i=L.length-1;}return i;};
const P=A.P.map(p=>{const q=p.slice();q[2]=ix(DC,p[2]);q[3]=p[3].map(s=>ix(DS,s));return q;});
const J=x=>JSON.stringify(x);
let out=`const TESTI=${J(A.TESTI)};\nconst S7=${J(A.S7)};\nconst S8=${J(A.S8)};\nconst C=${J(A.C)};\nconst P=${J(P)};\n`+
 `{const DC=${J(DC)},DS=${J(DS)};for(const p of P){p[2]=DC[p[2]];p[3]=p[3].map(x=>DS[x]);}}\n`;
const B=leggi(out);
for(const k of ['TESTI','S7','S8','C','P'])if(J(A[k])!==J(B[k])){console.error('DIVERSO',k);process.exit(1);}
fs.writeFileSync(process.argv[3],out);console.log('d2 compresso',Buffer.byteLength(src),'->',Buffer.byteLength(out));
