"""Residents: the snapshot's active, inactive and temporary, non-confidential records.

Issue #7 fixed the population at 7,854,464 records (NCSBE's own count of voters not cancelled
before 2024-11-05) minus confidential ones. In the snapshot that count is status A + I + S:
A 6,986,365, I 853,624, S 14,475 (S = temporary registrants, military and overseas, reason
codes SM/SO). Each of those NCIDs appears once; the other rows are removed (R) and denied (D)
history. Confidential records (362 among A/I/S) have a blank address and are dropped.

Writes $DATA/residents.parquet with normalized address keys and the few attributes the study
tabulates (county, ZIP, precinct, party, race, ethnicity, age, registration date). No names.

Run: uv run --with duckdb python 03_residents.py   (after 01_extract_voters.sh)
"""

import os

import duckdb

import common as c

con = duckdb.connect(os.path.join(c.DATA, "work.duckdb"))
con.execute("set preserve_insertion_order = false")
tsv = os.path.join(c.DATA, "snapshot_cols.tsv")
con.execute(f"""
    create or replace table snap as
    select * from read_csv('{tsv}', delim = '\t', header = true, all_varchar = true, quote = '', escape = '')
""")
print(con.execute("""
    select status_cd, count(*), count(distinct ncid), count(*) filter (where confidential_ind = 'Y')
    from snap group by 1 order by 1
""").fetchall())

# The street as one string, in the order a mailing address writes it.
full_street = ("concat_ws(' ', nullif(trim(street_dir), ''), nullif(trim(street_name), ''), "
               "nullif(trim(street_type_cd), ''), nullif(trim(street_sufx_cd), ''))")
half = "trim(half_code)"
con.execute(f"""
    create or replace table residents as
    select row_number() over (order by ncid) as rid, ncid,
      lpad(cast(2 * cast(trim(county_id) as int) - 1 as varchar), 3, '0') as county_fips,
      trim(county_desc) as county, status_cd as status,
      regexp_extract(trim(house_num), '^0*([0-9]+)', 1) as num,
      case when {half} = '½' then '1/2' else {half} end as sfx,
      {c.street(full_street)} as street_plain,
      {c.unit('unit_num')} as unit,
      {c.city_cleaned('res_city_desc')} as city,
      left(trim(zip_code), 5) as zip,
      trim(precinct_abbrv) as precinct, trim(party_cd) as party, trim(race_code) as race,
      trim(ethnic_code) as ethnic, try_cast(age as int) as age,
      try_strptime(registr_dt, '%m/%d/%Y')::date as registr_dt
    from snap
    where status_cd in ('A', 'I', 'S') and coalesce(confidential_ind, '') <> 'Y'
""")
con.execute(f"create or replace table residents as select *, {c.canon('street_plain')} as street from residents")
con.execute(f"create or replace table residents as select *, {c.core('street')} as core, {c.dirkey('street')} as dirkey from residents")
out = os.path.join(c.DATA, "residents.parquet")
con.execute(f"copy residents to '{out}' (format parquet, compression zstd)")
print(con.execute(f"select count(*), count(*) filter (where num in ('', '0')) no_number, count(*) filter (where unit <> '') with_unit from '{out}'").fetchall())
con.execute("drop table snap")
