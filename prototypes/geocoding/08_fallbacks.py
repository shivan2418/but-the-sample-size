"""How far off would each fallback place an unmatched resident?

Measured on matched addresses as a holdout: pretend a random 20,000 of them (resident-
weighted) are missing, place them with each fallback, and measure the distance to their
real local point.

  street_interp  interpolate along the same street in the same ZIP from the nearest lower and
                 higher house numbers of the same parity in the local sources (the nearest
                 end when the number lies outside the range); needs only local data
  precinct       median point of the other matched residents of the same precinct
  zip            median point of the other matched residents of the same ZIP

Also counts how many actual misses each fallback can place.

Run: uv run --with duckdb python 08_fallbacks.py
"""

import os

import duckdb

import common as c

D = c.DATA
con = duckdb.connect()
con.execute("install spatial; load spatial; set preserve_insertion_order = false")
con.execute(f"create table r as select * from '{D}/residents_geo.parquet'")
con.execute(f"create table a as select * from '{D}/addr_match.parquet'")
con.execute(f"create table mc as select * from '{D}/miss_categories.parquet'")
# One point per building and street key in the local sources.
con.execute(f"""
    create table bld as
    select zip, core, try_cast(num as bigint) n, avg(lon) lon, avg(lat) lat
    from '{D}/sources.parquet' where county_fips is not null and try_cast(num as bigint) is not null
    group by all
""")
con.execute("""
    create table hold as
    select aid, core, zip, try_cast(num as bigint) n, lon, lat, precinct, county_fips
    from (select * from r where tier = 1 and sfx = '') using sample reservoir(20000 rows) repeatable (3)
""")


def interp(target: str) -> None:
    """Interpolated point for each row of `target` (aid, core, zip, n), excluding the row's own number."""
    con.execute(f"""
        create or replace table interp as
        with lo as (
          select t.aid, arg_max(b.n, b.n) ln, arg_max(b.lon, b.n) llon, arg_max(b.lat, b.n) llat
          from {target} t join bld b on b.zip = t.zip and b.core = t.core and b.n < t.n and b.n % 2 = t.n % 2
          group by 1
        ), hi as (
          select t.aid, arg_min(b.n, b.n) hn, arg_min(b.lon, b.n) hlon, arg_min(b.lat, b.n) hlat
          from {target} t join bld b on b.zip = t.zip and b.core = t.core and b.n > t.n and b.n % 2 = t.n % 2
          group by 1
        )
        select t.aid,
          case when ln is not null and hn is not null then llon + (hlon - llon) * (t.n - ln) / (hn - ln)
               else coalesce(llon, hlon) end ilon,
          case when ln is not null and hn is not null then llat + (hlat - llat) * (t.n - ln) / (hn - ln)
               else coalesce(llat, hlat) end ilat,
          ln is not null and hn is not null as between
        from {target} t left join lo using (aid) left join hi using (aid)
        where ln is not null or hn is not null
    """)


interp("hold")
con.execute("create table cen_p as select county_fips, precinct, median(lon) lon, median(lat) lat from r where lon is not null group by all")
con.execute("create table cen_z as select zip, median(lon) lon, median(lat) lat from r where lon is not null group by all")
rows = con.execute("""
    with d as (
      select 'street_interp (between neighbours)' m, st_distance_sphere(st_point(h.lat, h.lon), st_point(i.ilat, i.ilon)) x
      from hold h join interp i using (aid) where i.between
      union all
      select 'street_interp (beyond range, nearest end)', st_distance_sphere(st_point(h.lat, h.lon), st_point(i.ilat, i.ilon))
      from hold h join interp i using (aid) where not i.between
      union all
      select 'precinct median point', st_distance_sphere(st_point(h.lat, h.lon), st_point(p.lat, p.lon))
      from hold h join cen_p p using (county_fips, precinct)
      union all
      select 'ZIP median point', st_distance_sphere(st_point(h.lat, h.lon), st_point(z.lat, z.lon))
      from hold h join cen_z z using (zip)
    )
    select m, count(*), round(median(x)), round(quantile_cont(x, 0.9)), round(100.0 * avg((x > 1000)::int), 1)
    from d group by 1 order by 1
""").fetchall()
print("| fallback (holdout of 20,000 matched addresses) | n | median m | p90 m | % > 1 km |")
print("|---|---|---|---|---|")
for row in rows:
    print("| " + " | ".join(f"{v:,}" if isinstance(v, int) else str(v) for v in row) + " |")

# What the fallbacks can place among the real misses.
con.execute("""
    create table miss as
    select a.aid, a.core, a.zip, try_cast(a.num as bigint) n, a.n_res, k.category
    from a join mc k using (aid) where a.tier is null and try_cast(a.num as bigint) > 0
""")
interp("miss")
N = con.execute("select count(*) from r").fetchone()[0]
missed = con.execute("select count(*) from r where lon is null").fetchone()[0]
placed = con.execute("select sum(n_res) from miss join interp using (aid)").fetchone()[0]
between = con.execute("select sum(n_res) from miss join interp using (aid) where between").fetchone()[0]
no_prec = con.execute("""
    select count(*) from r where lon is null
      and (county_fips, precinct) not in (select (county_fips, precinct) from cen_p)
""").fetchone()[0]
print(f"\nmissed residents {missed:,} ({100 * missed / N:.2f}%)")
print(f"street interpolation places {placed:,} of them ({100 * placed / missed:.1f}%), {between:,} between two neighbours")
print(f"missed residents whose precinct has no matched resident: {no_prec:,}")
print(con.execute("""
    select category, sum(n_res) filter (where i.aid is not null) placed, sum(n_res) total
    from miss m left join interp i using (aid) group by 1 order by 3 desc
""").fetchall())
