# PROTOTYPE, throwaway: resident build pipeline and blockdb layout

Answers the question in "Resident build pipeline and blockdb layout" (issue #5): can the state's residents be pre-built and served with blockdb so that a random poll of 1,200 costs about one block, and can any resident be looked up by address? This is not production code. Only the decision carries forward.

## What was built

- **Addresses (real):** `fetch_mi.py` range-reads Overture's addresses GeoParquet (release 2026-08-19.0), fetching only row groups whose bbox overlaps Michigan and keeping rows whose first address level is `MI`. Result: **869,433** address points, from Oakland County and parts of southwest Michigan. **There is nothing for Detroit/Wayne.** The statewide OpenAddresses source (MI state structure points) isn't in Overture, and OpenAddresses, the Census and block-addresses' live site were all unreachable from the build environment.
- **Scaled to full state size:** `gen_residents.py` resamples those addresses up to 4,570,173 (MI 2020 housing units) and places 10,077,331 residents (MI 2020 population) on them. Everything besides the addresses is dummy: household sizes, race, setting, vote and "tract" come from 0.1° lat/lon cells, standing in for Census blocks and precinct results.
- **Draw number:** a random permutation `0..N-1`, which is also the blockdb sort field and primary key. Any contiguous run of draws is a simple random sample.
- **Two layouts:**
  - `full`: each resident carries name, number, street, city, zip, tract, race, setting and vote.
  - `slim`: each resident carries first-name and last-name indexes, an address id, race, setting and vote. The addresses live in a separate `addresses` collection (`gen_addresses.py`) whose id is the address's rank in `STREET|CITY` order. That lets one collection sort, compress and look up like block-addresses does.

Built with blockdb 0.6.0 from source, gzip, `blockBytes` 64 KB for residents (the cap is on **raw** bytes: blocks come out at about 11 KB gzipped, ~790 residents each for slim and ~380 for full) and 256 KB for addresses.

## Results

| | full | slim + addresses |
|---|---|---|
| Deployed size | **301 MB** (26,421 blocks) | **137 MB** residents (12,717 blocks) + **43 MB** addresses (1,717 blocks) = **180 MB** |
| Per resident, gzipped | 29.9 B | 13.6 B (+ 9.5 B per address) |
| Manifest (once) | 430 KB | 204 KB |
| One poll of 1,200 (`draw: { gte: r }, limit: 1200`) | 4 files, 45 KB (p95 89 KB) | 4 files, 42 KB |
| Build time / machine | ~2 min, 15 GB box | ~1 min + ~1 min |

The spread of the dummy Dem share across 300 polls was 30.3–38.3% against a true 34.6%. That's the ±4 pt a 1,200 poll should show, so contiguous draw runs behave as random samples.

Emulated mid-range phone (Chromium, 4× CPU throttle):

| | slow 4G (150 ms, 1.6 Mbps) | 4G (60 ms, 9 Mbps) |
|---|---|---|
| First poll incl. manifest, slim / full | 1.7 s / 2.8 s | 0.5 s / 0.7 s |
| Each later poll, either layout | ~0.41 s | ~0.13 s |
| 100 polls in one range (120k residents), slim / full | 15 s, 1.6 MB / 32 s, 3.4 MB | 5 s / 10 s |
| Address lookup by id (slim), cold | 0.75 s, 76 KB | 0.25 s |

## Takeaways

1. **Feasible.** A poll costs ~40–90 KB and well under half a second on a phone. Both layouts fit far under the 1 GB GitHub Pages limit.
2. **Random order kills compression.** Draw-sorted residents gzip to ~30 B each when they carry their address text. Moving addresses into a street-sorted collection and referencing them by id halves the dataset.
3. **Repeating people-level polls is expensive.** 100 polls cost 1.6–3.4 MB and 5–30 s on a phone. Heavy repetition (thousands of polls) belongs to the proportion-level simulation, which the state rung ends by licensing.
4. **"One block per poll" isn't what happens.** blockdb reads ~4 small blocks per poll, whatever the block size. That's fine at this size.
5. **The address source isn't settled.** Overture has only ~19% of Michigan's housing units, so the pipeline needs OpenAddresses' MI statewide source (as block-addresses uses). Coverage against Census housing units is still unmeasured.
6. **Tract/precinct join:** block-addresses' `compact.py` drops coordinates after its Census spatial joins (ZIP and place). Adding block, tract and precinct to that same join is the pipeline change. It wasn't prototyped, because the Census and precinct shapes were unreachable.

## Run

```sh
uv run --with pyarrow --with fsspec --with aiohttp --with requests python fetch_mi.py  # → mi_addresses.parquet
python gen_residents.py slim slim/residents.ndjson     # or: full full/residents.ndjson
python gen_addresses.py                                # → addr/addresses.ndjson
# copy configs/<layout>.config.json to <layout>/blockdb.config.json, then in each dir: blockdb build
node --experimental-strip-types poll_bench.mjs slim 300
# phone: bundle phone/bench.ts with esbuild, serve the dir, node phone/run.mjs
```

Paths assume the scripts sit in one working directory next to a blockdb checkout. The data isn't committed.
