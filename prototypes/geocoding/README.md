# PROTOTYPE, throwaway: geocoding NC voter-file addresses

Scripts behind `docs/research/geocoding-nc-voter-addresses.md` (issue #10). They match every resident's residential address in the NCSBE Nov 2024 snapshot to local coordinate sources, sample the Census Bureau geocoder, and tabulate the results. This is not production code. The method carries forward, the scripts don't.

## Inputs (not in git)

- `$DATA` (default `~/Programming/nc-voter-data`): `VR_Snapshot_20241105.txt` unzipped from `https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/VR_Snapshot_20241105.zip`, and `ruca2020_zip.csv` from USDA ERS (2020 RUCA codes, ZIP code file).
- `$BLOCK_ADDRESSES` (default `~/Programming/block-addresses`), read only: `addresses/us/nc/*-addresses-*.geojson` (OpenAddresses), `overture/by-state/state=NC/` (Overture = NAD), `census/*.zip` (Census cartographic boundaries), and `scripts/compact.py`, whose street normalization is imported.

Every intermediate file is written to `$DATA`. Names, phone numbers and mailing addresses are dropped in step 1 and never reach later steps.

## Run

```sh
./01_extract_voters.sh                                    # UTF-16 snapshot -> snapshot_cols.tsv (~20 s)
./01b_fetch_addressnc.sh                                  # optional: full AddressNC, Sept 2024 (745 MB)
uv run --with duckdb python 02_sources.py                 # sources.parquet, 14.4M points (~1 min)
uv run --with duckdb python 03_residents.py               # residents.parquet, 7,854,102 rows (~1 min)
uv run --with duckdb python 04_match.py                   # addr_match / residents_geo.parquet (~1 min)
uv run --with duckdb --with requests python 05_census.py  # 5 Census batches of 10,000 (~4 min, network)
uv run --with duckdb python 06_misses.py                  # miss_categories.parquet
uv run --with duckdb python 07_report.py                  # report.md: every table in the doc
uv run --with duckdb python 08_fallbacks.py               # fallback accuracy on a holdout
```

`common.py` holds the shared paths and the normalization SQL (block-addresses' `compact.py` plus the NC fixes the doc measures). Address ids are stable across reruns, so `05_census.py` results still join after `04_match.py` changes. It skips batches that are already on disk, so delete `$DATA/census/` to resample.
