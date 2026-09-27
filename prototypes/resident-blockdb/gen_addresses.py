"""PROTOTYPE, wipe me. The 4.57M resampled addresses as their own collection, id = rank in STREET|CITY order."""
import json, numpy as np, pyarrow.parquet as pq
N=10_077_331; H=round(N*4_570_173/10_077_331); rng=np.random.default_rng(7)
t=pq.read_table('mi_addresses.parquet').to_pydict(); m=len(t['street'])
up=lambda s:(s or '').upper().replace('.','').replace(',','')
k=min(m,H); src=np.concatenate([rng.permutation(m)[:k],rng.integers(0,m,H-k)]); shift=np.concatenate([np.zeros(k,int),rng.integers(1,40,H-k)*2])
rows=[]
for a in range(H):
    s=src[a]; n=up(t['number'][s]); n=str(int(n)+shift[a]) if shift[a] and n.isdigit() else n
    rows.append((up(t['street'][s])+'|'+up(t['city_lvl'][s]), n, t['postcode'][s] or '', a))
rows.sort()
with open('addr/addresses.ndjson','w') as f:
    for i,(key,n,z,a) in enumerate(rows):
        f.write(json.dumps({"id":i,"key":key,"number":n,"zip":z,"tract":str(26_000_000_000+(a%3000)*100)},separators=(',',':'))+'\n')
