"""Load every local NC coordinate source into one normalized table.

Sources:
  addressnc AddressNC statewide address points, Sept 2024 vintage, fetched by
            01b_fetch_addressnc.sh (used when $DATA/addressnc/addressnc.parquet exists)
and, in the block-addresses checkout (read only):
  oa_state  OpenAddresses us/nc/statewide (NC OneMap AddressNC), statewide-addresses-state.geojson
  oa_local  every other OpenAddresses NC file: county, city and town sources
  nad       Overture addresses for NC, which in NC are all National Address Database rows

Each point gets a normalized house number, suffix, street, unit, city and ZIP, and, by
point-in-polygon against Census cartographic boundaries, its county FIPS and (where the
source has no ZIP) its ZCTA. Writes $DATA/sources.parquet.

Run: uv run --with duckdb python 02_sources.py
"""

import os
import time

import duckdb

import common as c

t0 = time.time()
con = duckdb.connect(os.path.join(c.DATA, "work.duckdb"))
con.execute("install spatial; load spatial; set preserve_insertion_order = false")

cousub = "cb_2023_us_cousub_500k"
zcta = "cb_2020_us_zcta520_500k"
con.execute(f"""
    create or replace table nc_county as
    select COUNTYFP as county_fips, st_union_agg(geom) as geom
    from st_read('/vsizip/{c.CENSUS}/{cousub}.zip/{cousub}.shp') where STATEFP = '37' group by 1
""")
con.execute(f"""
    create or replace table nc_zcta as
    select z.ZCTA5CE20 as zip, z.geom
    from st_read('/vsizip/{c.CENSUS}/{zcta}.zip/{zcta}.shp') z
    where exists (select 1 from nc_county k where st_intersects(k.geom, z.geom))
""")
print("boundaries:", con.execute("select count(*) from nc_county").fetchone(), con.execute("select count(*) from nc_zcta").fetchone())

oa = os.path.join(c.OA_DIR, "*-addresses-*.geojson")
num, sfx = c.house_number("number")
anc = os.path.join(c.DATA, "addressnc", "addressnc.parquet")
addressnc = ""
if os.path.exists(anc):
    street = ("concat_ws(' ', St_PreMod, St_PreDir, St_PreTyp, St_PreSep, St_Name, St_PosTyp, St_PosDir, St_PosMod)")
    addressnc = f"""union all
      select 'addressnc' as src, 'addressnc' as file, concat_ws(' ', Add_Number, AddNum_Suf) as number,
        {street} as street, Unit as unit, Post_Comm as city, Post_Code as postcode,
        DDLong::double as lon, DDLat::double as lat
      from '{anc}'"""
con.execute(f"""
    create or replace table raw_src as
    with oa as (
      select case when parse_filename(filename) = 'statewide-addresses-state.geojson' then 'oa_state' else 'oa_local' end as src,
        replace(parse_filename(filename), '.geojson', '') as file,
        properties.number as number, properties.street as street, properties.unit as unit,
        properties.city as city, properties.postcode as postcode,
        geometry.coordinates[1] as lon, geometry.coordinates[2] as lat
      from read_json('{oa}', format = 'newline_delimited', filename = true,
        columns = {{'properties': 'STRUCT(number VARCHAR, street VARCHAR, unit VARCHAR, city VARCHAR, postcode VARCHAR)',
                   'geometry': 'STRUCT(coordinates DOUBLE[])'}})
    ),
    nad as (
      select 'nad' as src, 'overture-nad' as file, number, street, unit,
        coalesce(postal_city, address_levels[2].value) as city, postcode, lon, lat
      from read_parquet('{c.NAD_DIR}/*.parquet')
    )
    select * from oa union all select * from nad {addressnc}
""")
print("raw rows:", con.execute("select src, count(*) from raw_src group by 1 order by 1").fetchall(), f"{time.time()-t0:.0f}s")

con.execute(f"""
    create or replace table src_norm as
    select row_number() over () as pid, src, file,
      {num} as num, {sfx} as sfx,
      {c.street('street')} as street_plain,
      {c.unit('unit')} as unit,
      {c.city_cleaned('city')} as city,
      case when regexp_matches(trim(postcode), '^[0-9]{{5}}') then left(trim(postcode), 5) else '' end as zip,
      lon, lat
    from raw_src
    where regexp_matches(trim(number), '^0*[1-9]') and regexp_matches(street, '[A-Za-z0-9]')
      and lon is not null and lat is not null
""")
con.execute(f"create or replace table src_norm as select *, {c.canon('street_plain')} as street from src_norm")
con.execute(f"create or replace table src_norm as select *, {c.core('street')} as core, {c.dirkey('street')} as dirkey from src_norm")
print("normalized:", con.execute("select count(*) from src_norm").fetchone(), f"{time.time()-t0:.0f}s")

con.execute("""
    create or replace table src_county as
    select s.pid, any_value(k.county_fips) as county_fips
    from src_norm s join nc_county k on st_contains(k.geom, st_point(s.lon, s.lat))
    group by 1
""")
con.execute("""
    create or replace table src_zcta as
    select s.pid, any_value(z.zip) as zcta
    from src_norm s join nc_zcta z on st_contains(z.geom, st_point(s.lon, s.lat))
    where s.zip = ''
    group by 1
""")
out = os.path.join(c.DATA, "sources.parquet")
con.execute(f"""
    copy (
      select s.* exclude (zip), coalesce(nullif(s.zip, ''), z.zcta, '') as zip, (s.zip = '') as zip_filled,
        k.county_fips
      from src_norm s left join src_county k using (pid) left join src_zcta z using (pid)
    ) to '{out}' (format parquet, compression zstd)
""")
print(con.execute(f"""
    select src, count(*) n, count(*) filter (where county_fips is null) outside_nc,
      count(*) filter (where zip_filled) zip_filled, count(*) filter (where unit <> '') with_unit
    from '{out}' group by 1 order by 1
""").fetchall())
print(f"wrote {out} in {time.time()-t0:.0f}s")
