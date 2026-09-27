# PROTOTYPE, throwaway: random polls within one town or city on blockdb

Answers "Random polls within one town or city on blockdb" (issue #11). What's the cheapest blockdb layout that gives a random poll inside one place (a town, a city, a county, or urban areas only) at phone cost comparable to a statewide poll? This is not production code. Only the decision carries forward.

## What was built

All 7,854,102 real residents from the Nov 2024 snapshot (`residents_geo.parquet` from the geocoding research). Names are invented indexes and the vote is dummy, drawn from party. Only bytes are measured, so the D% columns below check randomness and aren't real splits.

- **Place membership:** `municipality_abbrv` from the snapshot, joined to `municipality_desc` (`muni_names.csv`, extracted from the raw file) and merged by name across county lines. "UNINCORPORATED" and "WATAUGA COUNTY" count as no town. The result is **567 towns holding 4.53M residents (58%)**. Half have fewer than 1,200 registered voters, 57 have 12k–100k and 7 have more than 100k. Urban means RUCA 1–3 by ZIP (6.0M residents, 76%), as in the geocoding research.
- **Layouts,** built with blockdb 0.6.0, gzip, `blockBytes` 64 KB, as in issue #5:
  - **Statewide + filtered scan** (`configs/state.config.json`): draw-sorted, with indexed `town`, `county` and `urban` ids. A poll is `where: { town: { equals }, draw: { gte: r } }, limit: n`, which blockdb walks in draw order, 4 blocks at a time, until the page fills. **172 MB.** The build itself warns that `county` sits in 82% of files and `urban` in 100%.
  - **Place-major** (`configs/place.config.json`): one collection that holds a copy of every selectable group's residents under `k = group × 2²³ + rank`, where the rank is a random order within the group. A poll is `where: { k: { gte: base + r, lt: base + size } }`, wrapping to the group's start when it comes up short. With every town, every county, urban and rural, that's 20.2M records and **361 MB, 17.8 B per record.**
  - **Slice per place** (a collection per place) costs the same bytes as place-major, plus one manifest per place. It wasn't built separately.

## Results

A fresh client runs each poll (no block cache carried over). The manifest isn't counted. Index chunks were at most 24 KB. Local times are from disk. Phone times are modeled from issue #5's measurement: slow 4G, 150 ms per round of 4 files plus ~200 KB/s. That model reproduces issue #5's 0.41 s for 4 files and 42 KB.

| Place (registered voters) | Poll | Filtered scan: files, KB, ~phone | Place-major: files, KB, ~phone |
|---|---|---|---|
| North Carolina (7.85M), baseline | 1,200 | 4, 43 KB, 0.4 s | — |
| | 12,000 | 28, 300 KB, 2.5 s | — |
| Urban only (6.0M) | 1,200 | 5, 43 KB, 0.5 s | 4, 48 KB, 0.4 s |
| | 12,000 | 33, 343 KB, 2.9 s | 20, 242 KB, 2 s |
| Wake County (863k) | 1,200 | 25, 257 KB, 2 s | 4, 48 KB, 0.4 s |
| | 12,000 | 221, 2.4 MB, 20 s | 20, 241 KB, 2 s |
| Charlotte (645k) | 1,200 | 33, 343 KB, 3 s | 4, 50 KB, 0.4 s |
| | 12,000 | 289, 3.1 MB, 27 s | 20, 249 KB, 2 s |
| Chapel Hill (46.7k) | 1,200 | 389, 4.2 MB, 35 s | 4, 48 KB, 0.4 s |
| | 12,000 | 3,841, 41 MB | 20, 241 KB, 2 s |
| | all 46.7k | 14,735, 158 MB | 69, 830 KB, 7 s |
| Lenoir (11.9k) | 1,200 | 845, 9 MB | 4, 48 KB, 0.4 s |
| | all 11.9k | 8,295, 89 MB | 19, 229 KB, 2 s |
| Rutherfordton (3.0k) | 1,200 | 1,101, 12 MB | 4, 47 KB, 0.4 s |
| | all 3.0k | 2,707, 29 MB | 6, 71 KB, 0.6 s |
| Hyde County (3.2k) | all 3.2k | 2,897, 31 MB | 7, 83 KB, 0.6 s |

Poll D% landed in the expected band around each place's true dummy share, for both layouts (`bench.txt`).

## Takeaways

1. **A filtered scan only works for big groups.** The cost is about `n ÷ (the place's share of the state)` residents' worth of blocks. Urban-only (76%) costs the same as statewide, so it needs no copy. A county or a big city (8–11%) is 6–8× statewide at 1,200 and impractical at 12,000. Any town is hopeless: a 1,200 poll of a 3,000-voter town reads 1,100 files.
2. **Place-major is flat.** Every place costs what a statewide poll costs: ~4 files and ~48 KB for 1,200, ~20 files and ~245 KB for 12,000, and 17.8 B per resident to poll a whole town. The price is build bytes, one copy of each offered place's residents at 17.8 B each.
3. **What each place set adds to the 172 MB statewide build:**
   - the 10 biggest cities (Charlotte … High Point): +38 MB
   - the 281 towns with 1,200+ voters: +78 MB
   - all 567 towns: +81 MB
   - all 100 counties: +140 MB
   - urban/rural: 0, served by a filtered scan
   - everything: 172 + 81 + 140 = ~393 MB, well under GitHub Pages' 1 GB.
4. **Towns don't overlap,** so every offered town fits in one place-major collection, with one manifest (≤ 470 KB gzipped for all groups). The town rung's own town is just one entry in it, which replaces the separate "small draw-sorted collection" from *How many residents live at each address?*.

## Run

```sh
DATA=~/Programming/nc-voter-data   # residents.parquet, residents_geo.parquet, scratch.duckdb, ruca2020_zip.csv
mkdir -p $DATA/place-polls
# muni_names.csv: (county, municipality_abbrv, municipality_desc, n) from the raw snapshot, see build notes below
uv run --with duckdb --with numpy python build_ndjson.py        # → $DATA/place-polls/{state,place}/residents.ndjson, places.json
cp configs/state.config.json $DATA/place-polls/state/blockdb.config.json
cp configs/place.config.json $DATA/place-polls/place/blockdb.config.json
(cd $DATA/place-polls/state && node ~/Programming/blockdb/packages/blockdb-cli/dist/bin.js build)   # ~30 s
(cd $DATA/place-polls/place && node ~/Programming/blockdb/packages/blockdb-cli/dist/bin.js build)   # ~70 s
node poll_bench.mjs ~/Programming/blockdb $DATA/place-polls
```

`muni_names.csv` came from one DuckDB query over `VR_Snapshot_20241105.txt`: `read_csv(delim='\t', encoding='utf-16', all_varchar=true, quote='', strict_mode=false, null_padding=true)`, grouped by `county_desc, municipality_abbrv, municipality_desc` for status A/I/S. The data isn't committed.
