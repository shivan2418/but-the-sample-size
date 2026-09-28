# Size of one flat binary of every dot (uint16 x/y over the bbox + party + race bytes, Morton-sorted). Run in $DATA/dot-rendering.
import duckdb, numpy as np, gzip, zlib
c=duckdb.connect()
def spread(v):
    v=v.astype(np.uint64); out=np.zeros_like(v)
    for i in range(32): out|=((v>>np.uint64(i))&np.uint64(1))<<np.uint64(2*i)
    return out
for name,where in [('Charlotte','clt=1'),('NC','true')]:
    a=c.sql(f"select lon,lat,p,r from 'pts.parquet' where {where}").fetchnumpy(); n=len(a['lon'])
    lon,lat=a['lon'],a['lat']
    # uint16 over bbox
    qx=np.round((lon-lon.min())/(lon.max()-lon.min())*65535).astype(np.uint32); qy=np.round((lat-lat.min())/(lat.max()-lat.min())*65535).astype(np.uint32)
    res_m=((lon.max()-lon.min())*111320*np.cos(np.radians(35))/65535, (lat.max()-lat.min())*110574/65535)
    o=np.argsort(spread(qx)|(spread(qy)<<np.uint64(1)),kind='stable')
    cols=[qx[o].astype(np.uint16).tobytes(), qy[o].astype(np.uint16).tobytes(), a['p'][o].astype(np.uint8).tobytes(), a['r'][o].astype(np.uint8).tobytes()]
    b=b''.join(cols)
    print(f"{name} n={n} uint16 bbox (res {res_m[0]:.2f} x {res_m[1]:.2f} m): raw {len(b)/1e6:.2f} MB, gzip-9 {len(gzip.compress(b,9))/1e6:.2f} MB; coords only gzip {len(gzip.compress(cols[0]+cols[1],9))/1e6:.2f} MB, party col gzip {len(gzip.compress(cols[2],9))/1e3:.0f} KB, race col gzip {len(gzip.compress(cols[3],9))/1e3:.0f} KB")
