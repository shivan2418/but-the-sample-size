"""Tabulate everything the findings doc reports, as Markdown, to stdout and $DATA/report.md.

Needs the outputs of 02-06 and $DATA/ruca2020_zip.csv (USDA ERS 2020 RUCA codes by ZIP,
https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes).

Run: uv run --with duckdb python 07_report.py
"""

import os

import duckdb

import common as c

D = c.DATA
con = duckdb.connect()
con.execute("install spatial; load spatial")
con.execute(f"create table r as select * from '{D}/residents_geo.parquet'")
con.execute(f"create table a as select * from '{D}/addr_match.parquet'")
con.execute(f"create table cr as select * from '{D}/census_results.parquet'")
con.execute(f"create table cb as select * from '{D}/census_batches.parquet'")
con.execute(f"create table mc as select * from '{D}/miss_categories.parquet'")
con.execute(f"""
    create table ruca as
    select ZIPCode as zip, PrimaryRUCA::int as ruca from read_csv('{D}/ruca2020_zip.csv', all_varchar = true)
""")
SETTING = """case when ruca = 1 then '1 metro core' when ruca in (2, 3) then '2 metro commuting'
  when ruca between 4 and 6 then '3 micropolitan' when ruca between 7 and 9 then '4 small town'
  when ruca = 10 then '5 rural' else '6 no RUCA code' end"""
con.execute(f"create table rs as select r.*, {SETTING} as setting from r left join ruca using (zip)")

out = []


def p(s=""):
    out.append(s)
    print(s)


def table(sql, header):
    rows = con.execute(sql).fetchall()
    p("| " + " | ".join(header) + " |")
    p("|" + "|".join("---" for _ in header) + "|")
    for row in rows:
        p("| " + " | ".join("" if v is None else (f"{v:,}" if isinstance(v, int) else str(v)) for v in row) + " |")
    p()


N = con.execute("select count(*) from r").fetchone()[0]
NA = con.execute("select count(*) from a").fetchone()[0]
NB = con.execute("select count(*) from (select distinct num, sfx, street_plain, zip from a)").fetchone()[0]
p(f"residents {N:,}; distinct addresses (with unit) {NA:,}; distinct buildings (no unit) {NB:,}\n")

p("## Match rate by source")
pct = lambda e: f"round(100.0 * {e}, 2)"  # noqa: E731
rows = []
BA = "coalesce(tier_oa_state, tier_oa_local, tier_nad) is not null"
for label, cond in [("addressnc", "tier_addressnc is not null"), ("oa_state", "tier_oa_state is not null"), ("oa_local", "tier_oa_local is not null"),
                    ("nad", "tier_nad is not null"), ("block-addresses combined", BA),
                    ("all four combined", "tier is not null")]:
    strict = "coalesce(" + cond.replace("is not null", "= 1") + ", false)"
    if label == "block-addresses combined":
        strict = "coalesce(least(tier_oa_state, tier_oa_local, tier_nad) = 1, false)"
    if label == "all four combined":
        strict = "coalesce(tier = 1, false)"
    rows.append(f"""select '{label}',
      {pct(f"avg(({strict})::int)")}, {pct(f"avg(({cond})::int)")},
      (select {pct(f"avg(({cond})::int)")} from a) from r""")
table(" union all ".join(rows), ["source", "residents, exact key only (%)", "residents, all tiers (%)", "distinct addresses, all tiers (%)"])

p("## Gain by tier (combined, cumulative)")
table(f"""
    select tier, count(*) residents, {pct("count(*) / " + str(N))} pct,
      {pct("sum(count(*)) over (order by tier) / " + str(N))} cumulative_pct
    from r where tier is not null group by tier order by tier
""", ["tier", "residents", "% of residents", "cumulative %"])

p("## Winning source (combined)")
table(f"select coalesce(src, 'unmatched'), count(*), {pct('count(*) / ' + str(N))} from r group by 1 order by 2 desc",
      ["source", "residents", "%"])

p("## Urban vs rural (2020 RUCA by the resident's ZIP)")
table(f"""
    select setting, count(*) residents, {pct("avg((tier is not null)::int)")} matched_pct,
      {pct(f"avg(({BA})::int)")} ba_pct, {pct("avg((tier_addressnc is not null)::int)")} anc_pct,
      {pct("avg((tier_nad is not null)::int)")} nad_pct, count(*) - count(tier) unmatched
    from rs group by 1 order by 1
""", ["setting (primary RUCA)", "residents", "matched %, all sources", "block-addresses only %", "AddressNC alone %", "NAD alone %", "unmatched"])
table(f"""
    select case when setting < '3' then 'urban (RUCA 1-3, metropolitan)' else 'rural (RUCA 4-10)' end,
      count(*), {pct("avg((tier is not null)::int)")}, {pct(f"avg(({BA})::int)")}
    from rs where setting not like '6%' group by 1 order by 1
""", ["binary", "residents", "matched %, all sources", "block-addresses only %"])

p("## Misses by category")
table(f"""
    select category, count(*) addresses, sum(n_res) residents,
      {pct("sum(n_res) / sum(sum(n_res)) over ()")} pct_of_missed, {pct("sum(n_res) / " + str(N))} pct_of_all
    from mc group by 1 order by 3 desc
""", ["category", "addresses", "residents", "% of missed", "% of all residents"])

p("## Party and race, matched vs unmatched")
table(f"""
    select case when tier is null then 'unmatched' else 'matched' end, count(*),
      {pct("avg((party = 'DEM')::int)")} dem, {pct("avg((party = 'REP')::int)")} rep,
      {pct("avg((party = 'UNA')::int)")} una, {pct("avg((race = 'B')::int)")} black,
      {pct("avg((race = 'W')::int)")} white, round(avg(age), 1) mean_age
    from r group by 1 order by 1
""", ["group", "residents", "DEM %", "REP %", "UNA %", "Black %", "White %", "mean age"])
table(f"""
    select 'all residents', {pct("avg((party = 'DEM')::int)")}, {pct("avg((party = 'REP')::int)")}, {pct("avg((party = 'UNA')::int)")} from r
    union all
    select 'matched only', {pct("avg((party = 'DEM')::int)")}, {pct("avg((party = 'REP')::int)")}, {pct("avg((party = 'UNA')::int)")} from r where tier is not null
""", ["population", "DEM %", "REP %", "UNA %"])

p("Shift in DEM-minus-REP registration margin if unmatched residents were dropped (points):")
for level in ["county_fips", "county_fips, precinct"]:
    table(f"""
        with g as (
          select {level}, count(*) n, count(tier) nm,
            100.0 * (avg((party = 'DEM')::int) - avg((party = 'REP')::int)) m_all,
            100.0 * (avg((party = 'DEM')::int) filter (where tier is not null)
                   - avg((party = 'REP')::int) filter (where tier is not null)) m_matched
          from r group by {level} having count(tier) > 0
        )
        select '{level}', count(*),
          round(quantile_cont(abs(m_matched - m_all), 0.5), 2), round(quantile_cont(abs(m_matched - m_all), 0.95), 2),
          round(max(abs(m_matched - m_all)), 2), round(max(100.0 * (n - nm) / n), 1),
          count(*) filter (where abs(m_matched - m_all) >= 1)
        from g
    """, ["level", "groups", "median |shift|", "p95 |shift|", "max |shift|", "max % unmatched", "groups shifting >= 1 pt"])

p("## Residents per coordinate (apartments)")
con.execute("create table pts as select round(lon, 7) x, round(lat, 7) y, count(*) n, count(distinct aid) addrs, bool_or(unit <> '') any_unit from r where lon is not null group by 1, 2")
table(f"""
    select count(*) points, max(n) max_residents,
      {pct(f"sum(n) filter (where n >= 2) / {N}")} share_ge2,
      {pct(f"sum(n) filter (where n >= 10) / {N}")} share_ge10,
      {pct(f"sum(n) filter (where n >= 50) / {N}")} share_ge50,
      {pct(f"sum(n) filter (where n >= 200) / {N}")} share_ge200,
      count(*) filter (where n >= 100) pts_ge100
    from pts
""", ["points", "max residents at one point", "% of residents at a point with >= 2", ">= 10", ">= 50", ">= 200", "points with >= 100"])
table(f"""
    select case when unit = '' then 'no unit' when unit_hit then 'unit, own point' else 'unit, building point' end,
      count(*), {pct(f"count(*) / {N}")}
    from r where lon is not null group by 1 order by 1
""", ["resident address", "residents", "% of residents"])
table(f"""
    select count(*) filter (where addrs > 1) pts_multi_unit, max(addrs) max_units_at_point,
      round(avg(n) filter (where addrs > 1), 1) mean_res_multi
    from pts
""", ["points shared by >1 distinct address (units)", "max distinct units at one point", "mean residents at such points"])

p("## Census geocoder")
table("""
    select sample, count(*), round(avg(secs), 1) mean_secs, round(min(secs), 1), round(max(secs), 1)
    from cb group by 1 order by 1
""", ["sample", "batches of 10,000", "mean s/batch", "min s", "max s"])
con.execute("create table crm as select cr.*, a.tier, a.lon, a.lat, a.n_res, a.zip, mc.category from cr join a using (aid) left join mc using (aid)")
table("""
    select sample, count(*),
      round(100.0 * avg((status = 'Match')::int), 1) match_pct,
      round(100.0 * avg((status = 'Match' and exactness = 'Exact')::int), 1) exact_pct,
      round(100.0 * avg((status = 'Match' and exactness = 'Non_Exact')::int), 1) nonexact_pct,
      round(100.0 * avg((status = 'Tie')::int), 1) tie_pct,
      round(100.0 * avg((status = 'No_Match')::int), 1) nomatch_pct
    from (select *, case when sample = 'miss' and tier is not null then 'miss (now matched locally, excluded)' else sample end as s2 from crm)
    where s2 in ('all', 'miss') group by 1 order by 1
""", ["sample", "addresses", "match %", "exact %", "non-exact %", "tie %", "no match %"])
p("The 'miss' sample is restricted to addresses the final local matching still misses.\n")
table("""
    select category, count(*), round(100.0 * avg((status = 'Match')::int), 1),
      round(100.0 * avg((status = 'Match' and exactness = 'Exact')::int), 1)
    from crm where sample = 'miss' and tier is null group by 1 order by 2 desc
""", ["miss category", "addresses", "Census match %", "Census exact %"])
table("""
    select case when tier is null then 'local miss' else 'local match' end, count(*),
      round(100.0 * avg((status = 'Match')::int), 1)
    from crm where sample = 'all' group by 1 order by 1
""", ["'all' sample", "addresses", "Census match %"])

p("Distance, Census point vs local point, 'all' sample, both matched (metres):")
con.execute("""
    create table dist as
    select *, st_distance_sphere(st_point(clat, clon), st_point(lat, lon)) m
    from crm where sample = 'all' and status = 'Match' and lon is not null
""")
table("""
    select 'all' g, count(*), round(quantile_cont(m, 0.5)), round(quantile_cont(m, 0.9)), round(quantile_cont(m, 0.99)),
      round(100.0 * avg((m > 250)::int), 1), round(100.0 * avg((m > 1000)::int), 1) from dist
    union all
    select 'Census ' || exactness, count(*), round(quantile_cont(m, 0.5)), round(quantile_cont(m, 0.9)), round(quantile_cont(m, 0.99)),
      round(100.0 * avg((m > 250)::int), 1), round(100.0 * avg((m > 1000)::int), 1) from dist group by exactness
    union all
    select 'local tier ' || tier, count(*), round(quantile_cont(m, 0.5)), round(quantile_cont(m, 0.9)), round(quantile_cont(m, 0.99)),
      round(100.0 * avg((m > 250)::int), 1), round(100.0 * avg((m > 1000)::int), 1) from dist group by tier
    order by 1
""", ["group", "addresses", "median m", "p90 m", "p99 m", "% > 250 m", "% > 1 km"])
con.execute(f"create table dists as select d.*, {SETTING} as setting from dist d left join ruca using (zip)")
table("""
    select setting, count(*), round(quantile_cont(m, 0.5)), round(quantile_cont(m, 0.9)),
      round(100.0 * avg((m > 250)::int), 1) from dists group by 1 order by 1
""", ["setting", "addresses", "median m", "p90 m", "% > 250 m"])

missed_addr = con.execute("select count(*) from a where tier is null").fetchone()[0]
secs = con.execute("select avg(secs) from cb").fetchone()[0]
p(f"Extrapolation: {missed_addr:,} missed distinct addresses = {-(-missed_addr // 10000)} batches; "
  f"{NA:,} addresses = {-(-NA // 10000)} batches; mean {secs:.0f} s/batch sequential.\n")

p("## Per county")
table(f"""
    select county, count(*) residents, {pct("avg((tier is not null)::int)")} matched_pct,
      {pct(f"avg(({BA})::int)")} ba, {pct("avg((tier_addressnc is not null)::int)")} anc,
      {pct("avg((tier_oa_state is not null)::int)")} oa_state, {pct("avg((tier_oa_local is not null)::int)")} oa_local,
      {pct("avg((tier_nad is not null)::int)")} nad, count(*) - count(tier) unmatched
    from r group by county order by county
""", ["county", "residents", "matched %, all sources", "block-addresses only %", "AddressNC %", "OA statewide %", "OA county/city %", "NAD %", "unmatched"])
table(f"""
    select round(min(m), 2), round(quantile_cont(m, 0.1), 2), round(median(m), 2), round(max(m), 2)
    from (select county, 100.0 * avg((tier is not null)::int) m from r group by 1)
""", ["min county %", "p10", "median", "max"])

with open(os.path.join(D, "report.md"), "w") as f:
    f.write("\n".join(out) + "\n")
