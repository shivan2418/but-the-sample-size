# PROTOTYPE, throwaway: measuring dot-map options

Scripts behind `docs/research/dot-rendering.md` (issue #22). They take every resident with a house point (7,684,048 statewide, 641,030 in Charlotte) and measure what each way of drawing them costs: one flat binary, vector tiles (tippecanoe), and pre-rendered raster tiles. The numbers carry forward. The scripts don't.

## Inputs (not in git)

`$DATA` (default `~/Programming/nc-voter-data`) from the geocoding study (#10): `residents_geo.parquet`, plus `place-polls/places.parquet` from #11. Every output goes to `$DATA/dot-rendering/`. Only coordinates, party and race are exported. No names or addresses are used.

## Run (from `$DATA/dot-rendering`)

```sh
uv run --with duckdb python 01_points.py                                  # pts.parquet, nc.csv, clt.csv
uv run --with duckdb --with numpy python 02_raw_sizes.py                  # one flat binary of every dot
sh 03_tippecanoe.sh                                                       # builds tippecanoe in Docker, 4 tile sets (~3 min)
uv run --with pmtiles python 04_vector_sizes.py *.pmtiles                 # per-zoom and per-viewport sizes
uv run --with duckdb --with numpy --with pillow python 05_raster.py 5 11 2   # raster z5-11, party + race (~1 min)
uv run --with duckdb --with numpy --with pillow python 05_raster.py 12 13 1  # raster z12-13, party only (~4 min)
uv run python 06_raster_view.py                                           # raster bytes per phone viewport
sh 07_ghpages_check.sh                                                    # GitHub Pages Range + compression behaviour
```

`05b_encoders.py` compares WebP lossy, WebP lossless, PNG and 64-colour PNG on sample tiles. It picked WebP lossless after a 64-colour quantize.
