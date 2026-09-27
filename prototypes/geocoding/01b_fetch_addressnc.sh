#!/usr/bin/env bash
# Fetch the full AddressNC statewide address points (NC 911 Board / NC OneMap) closest before
# the snapshot date, and flatten the file geodatabase to parquet. The OpenAddresses
# us/nc/statewide file in block-addresses is the same dataset (July 2024) but holds only
# 2.67M of its 5.9M points. Bucket listing: https://s3.amazonaws.com/dit-cgia-gis-data?prefix=NCOM-data/addresses/
set -euo pipefail
DATA=${DATA:-$HOME/Programming/nc-voter-data}
VINTAGE=${VINTAGE:-09-18-2024}
mkdir -p "$DATA/addressnc" && cd "$DATA/addressnc"
[ -f "AddressNC-addresses-$VINTAGE.zip" ] || curl -sS -O "https://s3.amazonaws.com/dit-cgia-gis-data/NCOM-data/addresses/AddressNC-addresses-$VINTAGE.zip"
unzip -q -o "AddressNC-addresses-$VINTAGE.zip"
uv run --with duckdb python -c "
import duckdb
c = duckdb.connect(); c.execute('install spatial; load spatial')
c.execute(\"copy (select * exclude (Shape) from st_read('AddressNC.gdb')) to 'addressnc.parquet' (format parquet, compression zstd)\")
print(c.execute(\"select count(*) from 'addressnc.parquet'\").fetchone()[0], 'points')
"
