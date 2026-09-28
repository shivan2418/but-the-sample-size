# Pre-render every dot into 512 px raster tiles (shown as 256 CSS px, @2x), WebP lossless after a 64-colour quantize.
# Usage: uv run --with duckdb --with numpy --with pillow python 05_raster.py ZMIN ZMAX NSCHEMES   (1 = party, 2 = party + race)
import duckdb, numpy as np, io, math, sys, time, json
from PIL import Image
a=duckdb.connect().sql("select lon,lat,p,r,clt from 'pts.parquet'").fetchnumpy()
lon,lat=a['lon'],a['lat']
X=(lon+180)/360; s=np.sin(np.radians(lat)); Y=0.5-np.log((1+s)/(1-s))/(4*np.pi)
# class palettes (sRGB)
party_cls=np.select([a['p']==0,a['p']==1,a['p']==2],[0,1,2],3)   # DEM, REP, UNA, other
party_pal=np.array([[37,99,235],[220,38,38],[140,140,140],[202,138,4]],float)
race_cls=np.select([a['r']==0,a['r']==1,a['r']==2],[0,1,2],3)    # W, B, A, other/unknown
race_pal=np.array([[66,133,244],[46,160,67],[234,67,53],[150,150,150]],float)
T=512  # pixels per tile image, shown as 256 CSS px (@2x)
res={}; allsz={}; import pickle
for z in range(int(sys.argv[1]),int(sys.argv[2])+1):
    t0=time.time(); npx=T*2**z
    px=np.floor(X*npx).astype(np.int64); py=np.floor(Y*npx).astype(np.int64)
    tx,ty=px//T,py//T; key=tx*(1<<22)+ty
    o=np.argsort(key,kind='stable'); ks=key[o]
    bounds=np.flatnonzero(np.diff(ks))+1; starts=np.r_[0,bounds]; ends=np.r_[bounds,len(ks)]
    stats={}
    for scheme,cls,pal in [('party',party_cls,party_pal),('race',race_cls,race_pal)][:int(sys.argv[3])]:
        sizes_webp=[]; sizes_png=[]
        for st,en in zip(starts,ends):
            idx=o[st:en]; lx=px[idx]%T; ly=py[idx]%T; c=cls[idx]
            pix=ly*T+lx
            cnt=np.stack([np.bincount(pix[c==k],minlength=T*T) for k in range(4)],1).astype(float)
            n=cnt.sum(1)
            rgb=(cnt@pal)/np.maximum(n,1)[:,None]
            alpha=np.clip(n*0.6+0.35*(n>0),0,1)  # one dot = ~0.95 opaque device px
            out=255*(1-alpha)[:,None]+rgb*alpha[:,None]   # composited on white
            img=Image.fromarray(out.reshape(T,T,3).astype(np.uint8))
            b=io.BytesIO(); img.quantize(64,method=Image.Quantize.MEDIANCUT).convert('RGB').save(b,'WEBP',lossless=True,method=4); sizes_webp.append(b.tell()); allsz[(scheme,z,int(ks[st]>>22),int(ks[st]&((1<<22)-1)))]=b.tell()
            if len(sizes_png)<200:
                b=io.BytesIO(); img.save(b,'PNG',optimize=False); sizes_png.append(b.tell())
            if z==11 and scheme=='party' and 'sample' not in stats:
                # save a Charlotte tile
                cx,cy=int((-80.8431+180)/360*2**z), int((0.5-math.log((1+math.sin(math.radians(35.2271)))/(1-math.sin(math.radians(35.2271))))/(4*math.pi))*2**z)
                if ks[st]==cx*(1<<22)+cy: img.save(f'sample_z{z}_clt_party.png'); stats['sample']=1
        w=np.array(sizes_webp); p=np.array(sizes_png)
        stats[scheme]=dict(tiles=len(w),total_MB=round(w.sum()/1e6,2),median_KB=round(np.median(w)/1e3,1),max_KB=round(w.max()/1e3,1),png_vs_webp=round(p.mean()/w[:len(p)].mean(),2))
    res[z]=stats; print(z,json.dumps(stats),f"{time.time()-t0:.0f}s",flush=True)

pickle.dump(allsz,open(f'raster_sizes_{sys.argv[1]}_{sys.argv[2]}.pkl','wb'))
