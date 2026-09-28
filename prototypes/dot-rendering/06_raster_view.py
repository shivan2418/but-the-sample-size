# Raster bytes for one phone viewport, from 05_raster.py's size pickles. Map zoom m uses raster tiles at z = m+1.
import pickle, math
sz={}; [sz.update(pickle.load(open(f,'rb'))) for f in ['raster_sizes_5_11.pkl','raster_sizes_12_13.pkl']]
VW,VH=390/256,844/256
def t(lon,lat,z):
    s=math.sin(math.radians(lat)); return (lon+180)/360*2**z,(0.5-math.log((1+s)/(1-s))/(4*math.pi))*2**z
for name,(lo,la) in {'NC whole (centre -79.4,35.3)':(-79.4,35.3),'Charlotte uptown':(-80.8431,35.2271),'Raleigh downtown':(-78.6382,35.7796),'rural Sampson':(-78.35,35.0)}.items():
    out=[]
    for z in range(5,14):
        x,y=t(lo,la,z); keys=[('party',z,i,j) for i in range(math.floor(x-VW/2),math.floor(x+VW/2)+1) for j in range(math.floor(y-VH/2),math.floor(y+VH/2)+1)]
        out.append(f"m{z-1}: {sum(sz.get(k,0) for k in keys)/1e3:.0f} KB/{len(keys)}")
    print(name,' | '.join(out))
