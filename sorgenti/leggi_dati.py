"""9/11/2026: dati.<impronta>.json è scritto per colonne (chiave "k"). righe(D) lo riporta alla forma per righe (chiave "c"),
identica a quella di prima: ogni programma che legge i dati della Guida passa di qui."""
def righe(D):
    if "k" not in D: return D
    K = D.pop("k"); C = []; g = 0
    keys = list(K["ck"])
    for i, n in enumerate(K["n"]):
        c = {}
        for k in keys:
            if i in K["cm"].get(k, ()): continue
            c[k] = K["ck"][k][i]
        pl = []
        for j in range(n):
            a = [K["p"][q][g] for q in range(9)]
            if str(g) in K["x"]: a.append(K["x"][str(g)])
            pl.append(a); g += 1
        c["places"] = pl; C.append(c)
    D["c"] = C
    return D
