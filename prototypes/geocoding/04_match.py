"""Match residents' residential addresses to local coordinate sources.

Works on distinct resident addresses (house number + suffix + street + unit + city + ZIP +
county), then joins back to residents. Each address is tried against each source through a
cascade of keys, loosest last; the first tier that hits wins. Tiers:

  1 exact     number, suffix, street (block-addresses normalization), ZIP
  2 canon     as 1, hyphens as spaces and highway names canonicalized (common.canon)
  3 dirmove   as 2, directional tokens moved to the end ('2ND ST N' = 'N 2ND ST')
  4 city      number, suffix, street, city, county        (ZIP disagrees)
  5 county    number, suffix, street, county              (ZIP and city disagree)
  6 nosuffix  number, street, ZIP, ignoring '1/2' / letter suffixes on both sides
  7 core      number, street without type/directional tokens or spaces, ZIP

Tier 1 is block-addresses' matching as is; 2-7 are the cheap improvements whose gain the
report measures. (A tier 8, the core key within the county instead of the ZIP, was tried and
dropped: against the Census geocoder its points were a median 341 m off and 38% over 1 km.)
For tiers 4-7 a key only counts if all its source points lie within ~500 m
of each other, so a relaxed key never picks between two different places.

A key's building point is the mean of its unit-less points, or of all its points when the
source lists only units. When the resident has a unit and the source has a point for that
unit under the same (tier 1-3) key, the unit's own point is used instead ("unit hit").

Source priority for the combined result: addressnc (full AddressNC, when fetched), oa_state
(OpenAddresses' partial copy of AddressNC), oa_local (county/city feeds), then nad; within a tier, the first source that hits wins.

Writes $DATA/addr_match.parquet and $DATA/residents_geo.parquet.

Run: uv run --with duckdb python 04_match.py
"""

import os
import time

import duckdb

import common as c

TIERS = [
    (1, "exact", ["num", "sfx", "street_plain", "zip"]),
    (2, "canon", ["num", "sfx", "street", "zip"]),
    (3, "dirmove", ["num", "sfx", "dirkey", "zip"]),
    (4, "city", ["num", "sfx", "street", "city", "county_fips"]),
    (5, "county", ["num", "sfx", "street", "county_fips"]),
    (6, "nosuffix", ["num", "street", "zip"]),
    (7, "core", ["num", "core", "zip"]),
]
STRICT = 3  # tiers up to this one change only spelling, never which place is meant
SOURCES = ["addressnc", "oa_state", "oa_local", "nad"]
# street, core and dirkey are functions of street_plain, so ordering by the first seven keeps
# address ids stable when common.canon() changes.
ADDR_COLS = ["num", "sfx", "street_plain", "unit", "city", "zip", "county_fips", "street", "core", "dirkey"]
SPREAD = 0.005  # degrees, ~450-550 m in NC

t0 = time.time()
con = duckdb.connect(os.path.join(c.DATA, "work.duckdb"))
con.execute("set preserve_insertion_order = false")
src = os.path.join(c.DATA, "sources.parquet")
res = os.path.join(c.DATA, "residents.parquet")

con.execute(f"""
    create or replace table addr as
    select row_number() over (order by {', '.join(ADDR_COLS)}) as aid, *
    from (select {', '.join(ADDR_COLS)}, count(*) as n_res
          from '{res}' group by all)
""")
print("distinct addresses:", con.execute("select count(*) from addr").fetchone()[0], f"{time.time()-t0:.0f}s")
con.execute(f"create or replace table src as select * from '{src}' where county_fips is not null")

hits = []
for tier, name, keys in TIERS:
    k = ", ".join(keys)
    on = " and ".join(f"a.{x} = b.{x}" for x in keys)
    check = "" if tier <= STRICT else f"having max(lat) - min(lat) < {SPREAD} and max(lon) - min(lon) < {SPREAD}"
    con.execute(f"""
        create or replace table key_{tier} as
        select src, {k},
          coalesce(avg(lon) filter (where unit = ''), avg(lon)) as lon,
          coalesce(avg(lat) filter (where unit = ''), avg(lat)) as lat,
          count(*) as n_pts
        from src group by src, {k} {check}
    """)
    con.execute(f"""
        create or replace table hit_{tier} as
        select a.aid, b.src, {tier} as tier, b.lon, b.lat
        from addr a join key_{tier} b on {on}
    """)
    n = con.execute(f"select count(distinct aid) from hit_{tier}").fetchone()[0]
    print(f"tier {tier} {name}: {n:,} addresses hit (any source)  {time.time()-t0:.0f}s", flush=True)
    hits.append(f"select * from hit_{tier}")

con.execute(f"create or replace table hits as {' union all '.join(hits)}")

# Unit points for tier 1-3 keys.
con.execute("""
    create or replace table unit_pts as
    select src, num, sfx, street, street_plain, dirkey, zip, unit, avg(lon) lon, avg(lat) lat
    from src where unit <> '' group by all
""")
con.execute("""
    create or replace table unit_hit as
    select a.aid, u.src, any_value(u.lon) lon, any_value(u.lat) lat
    from addr a join unit_pts u
      on a.num = u.num and a.sfx = u.sfx and a.zip = u.zip and a.unit = u.unit
     and (a.street_plain = u.street_plain or a.street = u.street or a.dirkey = u.dirkey)
    where a.unit <> ''
    group by all
""")

prio = "case src when 'addressnc' then 0 when 'oa_state' then 1 when 'oa_local' then 2 else 3 end"
per_src = ", ".join(
    f"min(tier) filter (where src = '{s}') as tier_{s}" for s in SOURCES
)
con.execute(f"""
    create or replace table best as
    select aid, {per_src},
      arg_min(struct_pack(tier, src, lon, lat), tier * 10 + {prio}) as b
    from hits group by aid
""")
con.execute(f"""
    create or replace table addr_match as
    select a.*, b.tier_addressnc, b.tier_oa_state, b.tier_oa_local, b.tier_nad,
      b.b.tier as tier, b.b.src as src,
      case when b.b.tier <= {STRICT} and u.aid is not null then u.lon else b.b.lon end as lon,
      case when b.b.tier <= {STRICT} and u.aid is not null then u.lat else b.b.lat end as lat,
      b.b.tier <= {STRICT} and u.aid is not null as unit_hit
    from addr a left join best b using (aid)
      left join unit_hit u on u.aid = a.aid and u.src = b.b.src
""")
out_a = os.path.join(c.DATA, "addr_match.parquet")
con.execute(f"copy addr_match to '{out_a}' (format parquet, compression zstd)")
out_r = os.path.join(c.DATA, "residents_geo.parquet")
con.execute(f"""
    copy (
      select r.* exclude (ncid), m.aid, m.tier, m.src, m.lon, m.lat, m.unit_hit,
        m.tier_addressnc, m.tier_oa_state, m.tier_oa_local, m.tier_nad
      from '{res}' r join addr_match m
        on {" and ".join(f"r.{x} is not distinct from m.{x}" for x in ADDR_COLS)}
    ) to '{out_r}' (format parquet, compression zstd)
""")
print(con.execute(f"""
    select count(*), count(lon), round(100.0 * count(lon) / count(*), 2) from '{out_r}'
""").fetchall(), f"{time.time()-t0:.0f}s")
