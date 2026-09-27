"""Categorize the resident addresses the local sources missed, and why.

Every missed address gets the first category that fits:
  no_number      house number 0 or blank (campus dorms and other unnumbered housing)
  campus         a university residence hall/campus address (NCSU/WFU/WSSU/... prefixes, or
                 HALL / DORM in the street, as App State's 'HARDIN DOGWOOD DORM ST')
  po_rural       PO box, rural route, star route, general delivery in the street field
  military       on-base housing (city is a base: Fort Liberty, Camp Lejeune, ...)
  ambiguous      a relaxed key exists but its points are > ~500 m apart (rejected on purpose)
  num_gap        street exists in the ZIP in some source, number missing but inside the
                 street's number range there (missing point, infill, or a mistyped number)
  num_beyond     street exists in the ZIP, number outside the source's range (new lots at
                 the end of a street, or a mistyped number)
  other_zip      street exists in the county but not in the resident's ZIP
  similar_street a street in the same ZIP is spelled similarly (Jaro-Winkler >= 0.9 on the
                 core key): a spelling variant or typo
  street_absent  no similar street in the ZIP: street missing from every source
                 (new subdivision, private road, or a name the county uses differently)

Also compares registration dates (a proxy for new construction) and, for context, prints a
random sample of misses with house numbers removed.

Run: uv run --with duckdb python 06_misses.py
"""

import os

import duckdb

import common as c

con = duckdb.connect()
con.execute("set preserve_insertion_order = false")
con.execute(f"create table a as select * from '{os.path.join(c.DATA, 'addr_match.parquet')}'")
con.execute(f"create table s as select * from '{os.path.join(c.DATA, 'sources.parquet')}' where county_fips is not null")
con.execute("create table m as select * from a where tier is null")

CAMPUS = ("NCSU|UNC|UNCC|UNCG|UNCW|UNCP|UNCA|WFU|WSSU|ECU|ASU|NCAT|NCCU|FSU|ECSU|WCU|DUKE|"
          "DAVIDSON|ELON|CAMPBELL|GUILFORD COLLEGE|MEREDITH|AGGIE")
BASES = "('FORT LIBERTY', 'FORT BRAGG', 'FT BRAGG', 'CAMP LEJEUNE', 'TARAWA TERRACE', 'POPE AFB', 'SEYMOUR JOHNSON AFB', 'MIDWAY PARK', 'CHERRY POINT', 'MCAS CHERRY POINT')"

con.execute("""
    create table street_zip as
    select zip, core, min(try_cast(num as bigint)) lo, max(try_cast(num as bigint)) hi from s group by all
""")
con.execute("create table street_cty as select distinct county_fips, core from s")
con.execute("create table num_core_zip as select distinct num, core, zip from s")

con.execute(f"""
    create table cat as
    select m.aid, m.n_res, m.county_fips, m.zip, case
      when m.num in ('', '0') then 'no_number'
      when regexp_matches(m.street, '^({CAMPUS}) ') or regexp_matches(m.street, '(^| )(HALL|DORM|LIVING LEARNING)( |$)') then 'campus'
      when regexp_matches(m.street, '^(PO BOX|P O BOX|BOX|RR|RT|RTE|RURAL ROUTE|HC|STAR ROUTE|GENERAL DELIVERY)( |[0-9]|$)') then 'po_rural'
      when m.city in {BASES} then 'military'
      when nz.num is not null then 'ambiguous'
      when sz.core is not null and try_cast(m.num as bigint) between sz.lo and sz.hi then 'num_gap'
      when sz.core is not null then 'num_beyond'
      when sc.core is not null then 'other_zip'
      else 'unknown'
    end as category
    from m
    left join street_zip sz on sz.zip = m.zip and sz.core = m.core
    left join street_cty sc on sc.county_fips = m.county_fips and sc.core = m.core
    left join num_core_zip nz on nz.num = m.num and nz.core = m.core and nz.zip = m.zip
""")
# Spelling variants: a source street in the same ZIP whose core key is close.
con.execute("""
    create table similar_st as
    select distinct u.aid
    from (select c.aid, m.zip, m.core from cat c join m using (aid) where c.category = 'unknown') u
    join (select distinct zip, core from s) k on k.zip = u.zip
    where jaro_winkler_similarity(u.core, k.core) >= 0.9
""")
con.execute("""
    update cat set category = case when aid in (select aid from similar_st) then 'similar_street' else 'street_absent' end
    where category = 'unknown'
""")
out = os.path.join(c.DATA, "miss_categories.parquet")
con.execute(f"copy cat to '{out}' (format parquet)")

total_res = con.execute("select sum(n_res) from a").fetchone()[0]
print("category, missed addresses, missed residents, % of missed residents, % of all residents")
for row in con.execute(f"""
    select category, count(*), sum(n_res), round(100.0 * sum(n_res) / sum(sum(n_res)) over (), 1),
      round(100.0 * sum(n_res) / {total_res}, 2)
    from cat group by 1 order by 3 desc
""").fetchall():
    print(row)

res = os.path.join(c.DATA, "residents_geo.parquet")
print("registered since 2023-01-01, matched vs missed (proxy for new construction):")
print(con.execute(f"""
    select lon is not null as matched, round(100.0 * avg((registr_dt >= date '2023-01-01')::int), 1) pct_recent,
      count(*) from '{res}' group by 1 order by 1
""").fetchall())
print(con.execute(f"""
    select k.category, round(100.0 * avg((r.registr_dt >= date '2023-01-01')::int), 1) pct_recent
    from '{res}' r join cat k using (aid) group by 1 order by 1
""").fetchall())

print("\nsample of misses (house numbers removed):")
for row in con.execute("""
    select k.category, m.sfx, m.street, m.unit <> '' as has_unit, m.city, m.zip
    from (select * from cat using sample reservoir(40 rows) repeatable (11)) k join m using (aid)
    order by 1
""").fetchall():
    print(row)
