"""PROTOTYPE, throwaway: writes the two resident layouts compared in "Random polls within one town
or city on blockdb" (issue #11), from the real NC snapshot residents.

  state/residents.ndjson   statewide draw order (the layout from issue #5), plus indexed
                           town and county ids so the filtered scan can be measured
  place/residents.ndjson   place-major: every selectable group (each town, each county, urban,
                           rural) stores a copy of its residents under k = gid * 2^23 + rank,
                           rank a random order within the group. A poll is one contiguous k range.
  places.json              gid -> name, kind, size

Names are invented indexes and the vote is dummy (drawn from party): only bytes are measured.
Needs $DATA/residents_geo.parquet, $DATA/scratch.duckdb (municipality_abbrv), muni_names.csv
(see README) and $DATA/ruca2020_zip.csv.
"""
import json, os
import duckdb, numpy as np

D = os.path.expanduser(os.environ.get("DATA", "~/Programming/nc-voter-data"))
OUT = f"{D}/place-polls"
rng = np.random.default_rng(11)
c = duckdb.connect()
c.sql(f"attach '{D}/scratch.duckdb' as s (read_only)")
c.sql(f"create table nm as select * from read_csv('{OUT}/muni_names.csv', all_varchar = true)")
c.sql(f"""
create table r as
select g.rid, g.county, g.aid, g.party, g.race, g.age,
       case when n.muni_desc ilike '%UNINCORP%' or n.muni_desc ilike '%COUNTY' or trim(n.muni_desc) = ''
            then null else n.muni_desc end as town,
       coalesce(z.PrimaryRUCA::int, 10) <= 3 as urban
from '{D}/residents_geo.parquet' g
join '{D}/residents.parquet' q using (rid)
join s.s x on x.ncid = q.ncid and trim(x.county_desc) = q.county and x.status_cd = q.status
left join nm n on n.county = q.county and n.muni = trim(x.municipality_abbrv)
left join read_csv('{D}/ruca2020_zip.csv', all_varchar = true) z on z.ZIPCode = left(q.zip, 5)
""")
n = c.sql("select count(*) from r").fetchone()[0]
assert n == 7854102, n

# groups: towns (by name, merged across county lines), counties, urban, rural
c.sql("create table tid as select town, row_number() over (order by count(*) desc) - 1 as g from r where town is not null group by 1")
c.sql("create table cid as select county, row_number() over (order by count(*) desc) - 1 as g from r group by 1")
towns = [t for (t,) in c.sql("select town from tid order by g").fetchall()]
counties = [t for (t,) in c.sql("select county from cid order by g").fetchall()]
places = [{"kind": "town", "name": t} for t in towns] + [{"kind": "county", "name": t} for t in counties] \
    + [{"kind": "urban", "name": "Urban (RUCA 1-3)"}, {"kind": "rural", "name": "Rural (RUCA 4-10)"}]

a = c.sql("""select coalesce(t.g, -1) town_g, k.g county_g, urban, coalesce(aid, -1) aid, party,
                    case when race in ('W','B','A','I','M','O','P') then race else 'U' end race,
                    case when party in ('DEM','REP','UNA','LIB','GRE','NLB','JFA') then party else 'UNA' end partyc,
                    coalesce(age, 0) age
             from r left join tid t using (town) join cid k using (county)""").fetchnumpy()
a = {k: np.ma.getdata(v) for k, v in a.items()}
m = len(a["aid"])
town_g, county_g, urban, aid, race, partyc, age = (a[k] for k in ("town_g", "county_g", "urban", "aid", "race", "partyc", "age"))
party = a["party"]
# dummy vote: ~27% didn't vote, the rest lean by party, so the column has realistic entropy
u = rng.random(m)
pd = np.select([party == "DEM", party == "REP"], [0.88, 0.07], 0.45)
pr = np.select([party == "DEM", party == "REP"], [0.08, 0.90], 0.45)
vote = np.where(rng.random(m) < 0.27, "N", np.where(u < pd, "D", np.where(u < pd + pr, "R", "O")))
f = rng.integers(0, 4000, m)
l = rng.integers(0, 20000, m)
draw = rng.permutation(m)

def base_rec(i):
    return {"f": int(f[i]), "l": int(l[i]), "addr": int(aid[i]), "race": race[i], "party": partyc[i],
            "age": int(age[i]), "vote": vote[i]}

os.makedirs(f"{OUT}/state", exist_ok=True)
os.makedirs(f"{OUT}/place", exist_ok=True)
with open(f"{OUT}/state/residents.ndjson", "w") as w:
    for i in np.argsort(draw):
        rec = {"draw": int(draw[i]), **base_rec(i), "town": int(town_g[i]), "county": int(county_g[i]),
               "urban": bool(urban[i])}
        w.write(json.dumps(rec, separators=(",", ":")) + "\n")

K = 1 << 23  # > the largest group (7.85M would not fit, but no group is the whole state)
members = [np.flatnonzero(town_g == g) for g in range(len(towns))] \
    + [np.flatnonzero(county_g == g) for g in range(len(counties))] \
    + [np.flatnonzero(urban), np.flatnonzero(~urban)]
with open(f"{OUT}/place/residents.ndjson", "w") as w:
    for g, idx in enumerate(members):
        assert len(idx) < K
        places[g] |= {"gid": g, "size": int(len(idx)), "d": int((vote[idx] == "D").sum()),
                      "voters": int((vote[idx] != "N").sum())}
        for rank, i in enumerate(rng.permutation(idx)):
            w.write(json.dumps({"k": g * K + rank, **base_rec(i)}, separators=(",", ":")) + "\n")
json.dump({"K": K, "n": m, "d": int((vote == "D").sum()), "places": places}, open(f"{OUT}/places.json", "w"))
print(m, "residents;", len(towns), "towns;", sum(len(x) for x in members), "place-major records")
