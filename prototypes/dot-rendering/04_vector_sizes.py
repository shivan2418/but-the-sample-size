# Per-zoom tile sizes and bytes for one phone viewport (390x844 CSS px, 512 px vector tiles). Usage: uv run --with pmtiles python 04_vector_sizes.py *.pmtiles
import sys, math, collections, gzip
from pmtiles.reader import Reader, MmapSource, all_tiles
def lonlat2tile(lon,lat,z):
    n=2**z; x=(lon+180)/360*n; s=math.sin(math.radians(lat)); y=(0.5-math.log((1+s)/(1-s))/(4*math.pi))*n; return x,y
# phone viewport 390x844 CSS px, 512px vector tiles -> 0.76 x 1.65 tiles
VW,VH=390/512,844/512
def view_tiles(lon,lat,z):
    x,y=lonlat2tile(lon,lat,z)
    return {(z,i,j) for i in range(math.floor(x-VW/2),math.floor(x+VW/2)+1) for j in range(math.floor(y-VH/2),math.floor(y+VH/2)+1)}
for fn in sys.argv[1:]:
    with open(fn,'rb') as f:
        r=Reader(MmapSource(f)); h=r.header()
        sizes={}
        for (z,x,y),data in all_tiles(r.get_bytes): sizes[(z,x,y)]=len(data)
    print(f"# {fn}: {sum(sizes.values())/1e6:.1f} MB, {len(sizes)} tiles, tile compression {h['tile_compression']}")
    by=collections.defaultdict(list)
    for k,v in sizes.items(): by[k[0]].append(v)
    for z in sorted(by):
        v=sorted(by[z]); print(f"z{z}: {len(v)} tiles, {sum(v)/1e6:.2f} MB, median {v[len(v)//2]/1e3:.0f} KB, p95 {v[int(len(v)*.95)]/1e3:.0f} KB, max {v[-1]/1e3:.0f} KB")
    for name,(lon,lat) in {'Charlotte uptown':(-80.8431,35.2271),'Raleigh downtown':(-78.6382,35.7796),'NC centre':(-79.4,35.5)}.items():
        out=[]
        for z in sorted(by):
            t=view_tiles(lon,lat,z); b=sum(sizes.get(k,0) for k in t); out.append(f"z{z} {b/1e3:.0f}KB/{len(t)}t")
        print(' ',name,': ',', '.join(out))
