"""Run the Census Bureau batch geocoder on samples of resident addresses.

Samples (resident-weighted: draw residents at random, keep their distinct addresses):
  all     3 batches of 10,000 addresses drawn from every resident address
  miss    2 batches of 10,000 addresses drawn from addresses the local sources missed

Each batch is one POST to /geocoder/locations/addressbatch (benchmark Public_AR_Current),
the documented maximum of 10,000 records per file. Batches run one at a time and are timed.
Results go to $DATA/census/<sample>_<n>.csv (the raw response) and census_results.parquet.

Run: uv run --with duckdb --with requests python 05_census.py
"""

import csv
import io
import os
import time

import duckdb
import requests

import common as c

URL = "https://geocoding.geo.census.gov/geocoder/locations/addressbatch"
BATCH = 10_000
PLAN = {"all": 3, "miss": 2}

out_dir = os.path.join(c.DATA, "census")
os.makedirs(out_dir, exist_ok=True)
con = duckdb.connect()
res = os.path.join(c.DATA, "residents_geo.parquet")

samples = {}
for name, n in PLAN.items():
    where = "" if name == "all" else "where lon is null"
    # Oversample residents, then keep the first BATCH * n distinct addresses in random order.
    rows = con.execute(f"""
        with pick as (
          select aid, num, sfx, street_plain, city, zip, row_number() over (order by hash(rid, '{name}')) as o
          from '{res}' {where}
        )
        select aid, num, sfx, street_plain, city, zip from pick
        qualify row_number() over (partition by aid order by o) = 1
        order by o limit {BATCH * n}
    """).fetchall()
    samples[name] = rows

log = []
for name, rows in samples.items():
    for b in range(PLAN[name]):
        chunk = rows[b * BATCH:(b + 1) * BATCH]
        path = os.path.join(out_dir, f"{name}_{b}.csv")
        if not os.path.exists(path):
            buf = io.StringIO()
            w = csv.writer(buf)
            for aid, num, sfx, street, city, zip_ in chunk:
                w.writerow([aid, " ".join(x for x in (num, sfx, street) if x), city or "", "NC", zip_ or ""])
            t = time.time()
            r = requests.post(URL, files={"addressFile": ("addresses.csv", buf.getvalue(), "text/csv")},
                              data={"benchmark": "Public_AR_Current"}, timeout=3600)
            r.raise_for_status()
            secs = time.time() - t
            with open(path, "w") as f:
                f.write(r.text)
            with open(path + ".secs", "w") as f:
                f.write(f"{secs:.1f}\n")
        secs = float(open(path + ".secs").read())
        log.append((name, b, len(chunk), secs))
        print(f"{name} batch {b}: {len(chunk)} rows in {secs:.0f}s", flush=True)

# Response columns: id, input address, Match/No_Match/Tie, Exact/Non_Exact, matched address,
# "lon,lat", TIGER line id, side (L/R).
recs = []
for name, b, _, secs in log:
    with open(os.path.join(out_dir, f"{name}_{b}.csv"), newline="") as f:
        for row in csv.reader(f):
            row += [""] * (8 - len(row))
            lon = lat = None
            if row[5]:
                lon, lat = (float(x) for x in row[5].split(","))
            recs.append((name, b, int(row[0]), row[2], row[3], row[4], lon, lat, row[6], row[7]))
con.execute("""create table cr (sample varchar, batch int, aid bigint, status varchar, exactness varchar,
    matched varchar, clon double, clat double, tiger varchar, side varchar)""")
con.executemany("insert into cr values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", recs)
con.execute(f"copy cr to '{os.path.join(c.DATA, 'census_results.parquet')}' (format parquet)")
con.execute("create table batches (sample varchar, batch int, n int, secs double)")
con.executemany("insert into batches values (?, ?, ?, ?)", log)
con.execute(f"copy batches to '{os.path.join(c.DATA, 'census_batches.parquet')}' (format parquet)")
print(con.execute("select sample, status, exactness, count(*) from cr group by all order by all").fetchall())
