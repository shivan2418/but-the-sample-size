# PROTOTYPE: pull Michigan rows of Overture addresses via row-group bbox pruning.
import pyarrow.parquet as pq, pyarrow as pa, pyarrow.compute as pc, fsspec, re, requests, sys
from concurrent.futures import ThreadPoolExecutor
B="https://overturemaps-us-west-2.s3.amazonaws.com/"
x=requests.get(B+"?list-type=2&prefix=release/2026-08-19.0/theme=addresses/type=address/").text
keys=re.findall(r'<Key>([^<]*parquet)</Key>',x)
X0,X1,Y0,Y1=-90.5,-82.0,41.6,48.4
COLS=['street','number','unit','postcode','postal_city','address_levels','country','bbox']
def rgs(k):
    fs=fsspec.filesystem("http"); p=pq.ParquetFile(fs.open(B+k,block_size=1<<16)); md=p.metadata
    idx={md.schema.column(i).path:i for i in range(md.num_columns)}
    out=[]
    for g in range(md.num_row_groups):
        r=md.row_group(g); s=lambda c:r.column(idx[c]).statistics
        if s('bbox.xmax').min>X1 or s('bbox.xmin').max<X0 or s('bbox.ymax').min>Y1 or s('bbox.ymin').max<Y0: continue
        cs=s('country'); 
        if cs.has_min_max and (cs.max<'US' or cs.min>'US'): continue
        out.append(g)
    return k,out
with ThreadPoolExecutor(16) as ex: plan=list(ex.map(rgs,keys))
tot=sum(len(g) for _,g in plan); print("row groups to read:",tot,flush=True)
def read(kg):
    k,g=kg; fs=fsspec.filesystem("http"); p=pq.ParquetFile(fs.open(B+k,block_size=8<<20))
    t=p.read_row_group(g,columns=COLS)
    st=pc.list_element(pc.struct_field(t['address_levels'],'value'),0) if False else None
    lv=t['address_levels'].combine_chunks()
    first=pc.struct_field(pc.list_element(lv,0),[0])
    m=pc.and_(pc.equal(t['country'],'US'),pc.equal(first,'MI'))
    return t.filter(m)
jobs=[(k,g) for k,gs in plan for g in gs]
tabs=[]
with ThreadPoolExecutor(16) as ex:
    for i,t in enumerate(ex.map(read,jobs)):
        if t.num_rows: tabs.append(t)
        if i%20==0: print(i,len(jobs),sum(x.num_rows for x in tabs),flush=True)
T=pa.concat_tables(tabs)
T=T.append_column('lon',pc.struct_field(T['bbox'],'xmin')).append_column('lat',pc.struct_field(T['bbox'],'ymin'))
lv=T['address_levels'].combine_chunks()
T=T.append_column('city_lvl',pc.struct_field(pc.list_element(lv,1),[0])) if pc.max(pc.list_value_length(lv)).as_py()>1 else T
T=T.drop_columns(['bbox','address_levels','country'])
pq.write_table(T,'mi/mi_addresses.parquet',compression='zstd'); print("MI rows",T.num_rows)
