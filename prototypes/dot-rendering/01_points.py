# Export one row per resident with a house point: lon, lat, party code, race code, Charlotte flag.
# Inputs from the geocoding study (#10) and the place-polls study (#11) in $DATA.
import duckdb, os
DATA=os.environ.get('DATA', os.path.expanduser('~/Programming/nc-voter-data')); OUT=f'{DATA}/dot-rendering'
os.makedirs(OUT, exist_ok=True); c=duckdb.connect()
c.sql(f'''copy (select r.lon, r.lat,
  list_position(['DEM','REP','UNA','LIB','GRE','JFA','NLB'], r.party)-1 as p,
  list_position(['W','B','A','I','M','O','P','U'], r.race)-1 as r,
  (p.town='CHARLOTTE')::int as clt
  from '{DATA}/residents_geo.parquet' r left join '{DATA}/place-polls/places.parquet' p using(rid)
  where r.lon is not null) to '{OUT}/pts.parquet' ''')
c.sql(f"copy (select round(lon,6) lon, round(lat,6) lat, p, r from '{OUT}/pts.parquet') to '{OUT}/nc.csv'")
c.sql(f"copy (select round(lon,6) lon, round(lat,6) lat, p, r from '{OUT}/pts.parquet' where clt=1) to '{OUT}/clt.csv'")
