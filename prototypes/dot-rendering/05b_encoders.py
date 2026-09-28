# Compare image encoders on a few sample tiles.
import duckdb, numpy as np, io, math
from PIL import Image
exec(open('05_raster.py').read().split('T=512')[0])
T=512
def render(z,tx,ty):
    npx=T*2**z; px=np.floor(X*npx).astype(np.int64); py=np.floor(Y*npx).astype(np.int64)
    m=(px//T==tx)&(py//T==ty); lx=px[m]%T; ly=py[m]%T; c=party_cls[m]; pix=ly*T+lx
    cnt=np.stack([np.bincount(pix[c==k],minlength=T*T) for k in range(4)],1).astype(float); n=cnt.sum(1)
    rgb=(cnt@party_pal)/np.maximum(n,1)[:,None]; alpha=np.clip(n*0.6+0.35*(n>0),0,1)
    return Image.fromarray((255*(1-alpha)[:,None]+rgb*alpha[:,None]).reshape(T,T,3).astype(np.uint8)), m.sum()
def tile(lon,lat,z):
    s=math.sin(math.radians(lat)); return int((lon+180)/360*2**z), int((0.5-math.log((1+s)/(1-s))/(4*math.pi))*2**z)
for name,(lo,la) in {'Charlotte':(-80.8431,35.2271),'rural Sampson':(-78.35,35.0)}.items():
  for z in (6,9,11,13):
    tx,ty=tile(lo,la,z); img,n=render(z,tx,ty); out=[]
    for lab,kw,fmt,im in [('webp80',dict(quality=80,method=6),'WEBP',img),('webp50',dict(quality=50,method=6),'WEBP',img),('webpLL',dict(lossless=True,method=6),'WEBP',img),('png',dict(optimize=True),'PNG',img),('png64',dict(optimize=True),'PNG',img.quantize(64,method=Image.Quantize.MEDIANCUT)),('webpLL64',dict(lossless=True,method=6),'WEBP',img.quantize(64,method=Image.Quantize.MEDIANCUT).convert('RGB'))]:
        b=io.BytesIO(); im.save(b,fmt,**kw); out.append(f"{lab} {b.tell()/1e3:.0f}")
    img.save(f'sample_{name.split()[0]}_z{z}.png'); print(name,z,n,'pts |',', '.join(out),'KB')
