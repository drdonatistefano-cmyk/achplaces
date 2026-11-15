#!/usr/bin/env python3
"""13/11/2026 – traduzione automatica italiano -> inglese dei testi della guida, su GitHub Actions.

Modello: Helsinki-NLP/opus-mt-it-en (Opus-MT, licenza CC BY 4.0), convertito per CTranslate2 (int8, CPU).
Nessun servizio esterno: il modello gira dentro il job.
Uso: python traduci.py <testi_it.jsonl> <cartella memoria> <parte> <parti>
Traduce solo i testi della sua parte che non sono gia' in memoria/<parte>.jsonl e li aggiunge li'.
"""
import json, os, re, sys, time
import ctranslate2, transformers

src, mem_dir, parte, parti = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
os.makedirs(mem_dir, exist_ok=True)
mem_f = os.path.join(mem_dir, f'{parte}.jsonl')
fatti = set()
for f in os.listdir(mem_dir):
    if f.endswith('.jsonl'):
        for l in open(os.path.join(mem_dir, f)):
            try: fatti.add(json.loads(l)['k'])
            except Exception: pass
righe = [json.loads(l) for l in open(src)]
mie = [r for r in righe if int(r['k'].split('.')[0], 36) % parti == parte and r['k'] not in fatti]
print(f'parte {parte}/{parti}: {len(mie)} testi da tradurre ({len(fatti)} gia\' in memoria)', flush=True)
if not mie: sys.exit(0)

tok = transformers.AutoTokenizer.from_pretrained('Helsinki-NLP/opus-mt-it-en')
tr = ctranslate2.Translator('modello', device='cpu', compute_type='int8', inter_threads=1, intra_threads=os.cpu_count() or 2)

FRASE = re.compile(r'(?<=[.!?;])\s+(?=[A-ZÀ-Ý«"(0-9])')
def frasi(t):
    out = []
    for f in FRASE.split(t.strip()):
        while len(f) > 700:  # le frasi lunghissime si spezzano alle virgole
            i = f.rfind(', ', 0, 700); i = i if i > 200 else 700
            out.append(f[:i + 1]); f = f[i + 1:].lstrip()
        if f: out.append(f)
    return out

def traduci(testi):
    pezzi, idx = [], []
    for i, t in enumerate(testi):
        for f in frasi(t): pezzi.append(f); idx.append(i)
    ris = [''] * len(pezzi)
    ordine = sorted(range(len(pezzi)), key=lambda j: len(pezzi[j]))
    B = 48
    for a in range(0, len(ordine), B):
        blocco = [pezzi[j] for j in ordine[a:a + B]]
        toks = [tok.convert_ids_to_tokens(tok.encode(x)) for x in blocco]
        out = tr.translate_batch(toks, beam_size=2, max_decoding_length=400)
        for j, o in zip(ordine[a:a + B], out):
            ris[j] = tok.decode(tok.convert_tokens_to_ids(o.hypotheses[0]), skip_special_tokens=True)
    fin = [''] * len(testi)
    for j, i in enumerate(idx): fin[i] = (fin[i] + ' ' + ris[j]).strip()
    return fin

t0 = time.time(); fatti_ora = 0
with open(mem_f, 'a') as mf:
    for a in range(0, len(mie), 400):
        g = mie[a:a + 400]
        en = traduci([r['t'] for r in g])
        for r, e in zip(g, en):
            if e: mf.write(json.dumps({'k': r['k'], 'en': e}, ensure_ascii=False) + '\n')
        mf.flush(); fatti_ora += len(g)
        print(f'  {fatti_ora}/{len(mie)} in {time.time() - t0:.0f} s', flush=True)
        if time.time() - t0 > 5.3 * 3600: break  # si riprende al giro dopo
