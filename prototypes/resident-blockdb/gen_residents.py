"""PROTOTYPE, wipe me. Synthetic Michigan residents at real addresses, sorted by a random draw number.

Real: 869k Overture (NAD/OpenAddresses) Michigan address points. Resampled to 4.57M addresses
(MI 2020 housing units) so size numbers are at full state scale. Everything else is dummy:
households, race, setting, vote and "tract" come from coarse lat/lon cells, standing in for
Census blocks / precinct results that are unreachable from this environment.
Usage: python gen_residents.py <layout: full|slim> <out.ndjson> [n_residents]
"""
import sys, json, numpy as np, pyarrow.parquet as pq
layout, out = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 10_077_331   # MI 2020 census population
H = round(N * 4_570_173 / 10_077_331)                          # MI 2020 housing units, scaled with N
rng = np.random.default_rng(7)
t = pq.read_table('mi_addresses.parquet').to_pydict()
m = len(t['street'])
up = lambda s: (s or '').upper().replace('.', '').replace(',', '')
num = [up(x) for x in t['number']]; st = [up(x) for x in t['street']]
city = [up(x) for x in t['city_lvl']]; zp = [x or '' for x in t['postcode']]
lat = np.array(t['lat']); lon = np.array(t['lon'])
# address ids: resample real addresses up to H (house number shifted so resampled copies differ)
k = min(m, H)
src = np.concatenate([rng.permutation(m)[:k], rng.integers(0, m, H - k)])
shift = np.concatenate([np.zeros(k, int), rng.integers(1, 40, H - k) * 2])
# household sizes: dummy ~ MI mean 2.2 (Poisson+1 scaled to hit N exactly)
hh = rng.poisson(N / H - 1, H) + 1
diff = N - hh.sum()
adj = rng.integers(0, H, abs(diff)); np.add.at(hh, adj, 1 if diff > 0 else 0)
if diff < 0:
    idx = np.flatnonzero(hh > 1); np.add.at(hh, rng.choice(idx, -diff, replace=False), -1)
assert hh.sum() == N
addr_of = np.repeat(np.arange(H), hh)
# dummy place clustering: 0.1-degree cells drive race / setting / vote shares
cell = (np.floor((lat[src] - 41) * 10).astype(int) * 100 + np.floor((lon[src] + 91) * 10).astype(int))
uc, inv = np.unique(cell, return_inverse=True)
dens = np.bincount(inv); urban_p = np.clip(dens[inv] / np.percentile(dens, 90), 0.05, 0.98)
black_p = rng.beta(0.5, 6, len(uc))[inv]; dem_p = rng.beta(4, 4, len(uc))[inv]
R = addr_of; ra = rng.random(N)
race = np.where(ra < black_p[R], 'B', np.where(ra < black_p[R] + 0.05, 'H', np.where(ra < black_p[R] + 0.09, 'A', np.where(ra < black_p[R] + 0.12, 'O', 'W'))))
urban = np.where(rng.random(N) < urban_p[R], 'U', 'R')
vr = rng.random(N)
vote = np.where(vr < 0.35, 'N', np.where(vr < 0.35 + 0.63 * dem_p[R], 'D', np.where(vr < 0.985, 'R', 'O')))
FIRST = "James Mary Robert Patricia John Jennifer Michael Linda David Elizabeth William Barbara Richard Susan Joseph Jessica Thomas Sarah Charles Karen Christopher Lisa Daniel Nancy Matthew Betty Anthony Sandra Mark Margaret Donald Ashley Steven Kimberly Andrew Emily Paul Donna Joshua Michelle Kenneth Carol Kevin Amanda Brian Melissa Timothy Deborah Ronald Stephanie George Dorothy Jason Rebecca Edward Sharon Jeffrey Laura Ryan Cynthia Jacob Amy Gary Kathleen Nicholas Angela Eric Shirley Jonathan Brenda Stephen Emma Larry Anna Justin Pamela Scott Nicole Brandon Samantha Benjamin Katherine Samuel Christine Gregory Helen Alexander Debra Patrick Rachel Frank Carolyn Raymond Janet Jack Maria Dennis Olivia Jerry Heather Tyler Diane Aaron Julie Jose Joyce Adam Victoria Nathan Ruth Henry Virginia Zachary Lauren Douglas Kelly Peter Christina Kyle Joan Noah Evelyn Ethan Judith Jeremy Andrea Christian Hannah Walter Megan Keith Cheryl Austin Jacqueline Roger Martha Terry Madison Sean Teresa Gerald Kathryn Carl Gloria Dylan Sara Harold Janice Jordan Ann Jesse Kathryn Bryan Abigail Lawrence Sophia Arthur Frances Gabriel Jean Bruce Alice Logan Judy Billy Isabella Joe Julia Alan Grace Juan Amber Elijah Denise Willie Danielle Albert Marilyn Wayne Beverly Randy Charlotte Mason Natalie Vincent Theresa Liam Diana Roy Brittany Bobby Doris Caleb Kayla Bradley Alexis Russell Lori Lucas Marie".split()
LAST = "Smith Johnson Williams Brown Jones Garcia Miller Davis Rodriguez Martinez Hernandez Lopez Gonzalez Wilson Anderson Thomas Taylor Moore Jackson Martin Lee Perez Thompson White Harris Sanchez Clark Ramirez Lewis Robinson Walker Young Allen King Wright Scott Torres Nguyen Hill Flores Green Adams Nelson Baker Hall Rivera Campbell Mitchell Carter Roberts Gomez Phillips Evans Turner Diaz Parker Cruz Edwards Collins Reyes Stewart Morris Morales Murphy Cook Rogers Gutierrez Ortiz Morgan Cooper Peterson Bailey Reed Kelly Howard Ramos Kim Cox Ward Richardson Watson Brooks Chavez Wood James Bennett Gray Mendoza Ruiz Hughes Price Alvarez Castillo Sanders Patel Myers Long Ross Foster Jimenez Powell Jenkins Perry Russell Sullivan Bell Coleman Butler Henderson Barnes Gonzales Fisher Vasquez Simmons Romero Jordan Patterson Alexander Hamilton Graham Reynolds Griffin Wallace Moreno West Cole Hayes Bryant Herrera Gibson Ellis Tran Medina Aguilar Stevens Murray Ford Castro Marshall Owens Harrison Fernandez McDonald Woods Washington Kennedy Wells Vargas Henry Chen Freeman Webb Tucker Guzman Burns Crawford Olson Simpson Porter Hunter Gordon Mendez Silva Shaw Snyder Mason Dixon Munoz Hunt Hicks Holmes Palmer Wagner Black Robertson Boyd Rose Stone Salazar Fox Warren Mills Meyer Rice Schmidt Garza Daniels Ferguson Nichols Stephens Soto Weaver Ryan Gardner Payne Grant Dunn Kelley Spencer Hawkins Arnold Pierce Vazquez Hansen Peters Santos Hart Bradley Knight Elliott Cunningham Duncan Armstrong Hudson Carroll Lane Riley Andrews Alvarado Ray Delgado Berry Perkins Hoffman Johnston Matthews Pena Richards Willis Carpenter Lawrence Sandoval Kowalski Nowak Wisniewski Kaminski Schultz Novak Haddad Hassan".split()
fi = rng.integers(0, len(FIRST), N)
hh_last = rng.integers(0, len(LAST), H); li = hh_last[R]
mix = rng.random(N) < 0.15; li[mix] = rng.integers(0, len(LAST), mix.sum())
draw = rng.permutation(N)                          # the draw number: a random permutation 0..N-1
order = np.argsort(draw)
tract = (26_000_000_000 + (cell % 100_000_0) * 100).astype(np.int64)
with open(out, 'w') as f:
    for i in order:
        a = R[i]; s = src[a]
        n = str(int(num[s]) + shift[a]) if shift[a] and num[s].isdigit() else num[s]
        if layout == 'full':
            rec = {"draw": int(draw[i]), "name": FIRST[fi[i]] + " " + LAST[li[i]], "number": n, "street": st[s],
                   "city": city[s], "zip": zp[s], "tract": str(tract[a]), "race": race[i], "setting": urban[i], "vote": vote[i]}
        else:  # slim: address id into a separate address collection, names as list indexes
            rec = {"draw": int(draw[i]), "f": int(fi[i]), "l": int(li[i]), "addr": int(a), "race": race[i], "setting": urban[i], "vote": vote[i]}
        f.write(json.dumps(rec, separators=(',', ':')) + '\n')
# true split for audit
print(json.dumps({"N": N, "vote": {k: int((vote == k).sum()) for k in 'DRON'}}))
