# Geocoding NC voter-file addresses

Research for issue #10, "Geocoding NC voter-file addresses". Researched 2026-09-27, on the map owner's PC, against the local block-addresses data, the full NCSBE snapshot and the live Census geocoder. Scripts: [`prototypes/geocoding/`](../../prototypes/geocoding/).

**Question.** The state rung puts each resident's dot on their house, but the NC voter snapshot (`VR_Snapshot_20241105`) has street addresses and no coordinates. What share of residents' addresses can be matched to coordinates, and from which source? How does the Census Bureau geocoder compare? Where do misses cluster (county, urban/rural)? What should happen to residents that can't be matched, and how should apartment units share a building's point?

## Answer

- **97.8% of residents (97.5% of distinct addresses) match a rooftop-style address point in local data.** The data already in block-addresses gets 97.75% on its own. Overture/NAD does most of the work (96.0% alone). The OpenAddresses statewide file in block-addresses is a partial copy (2.67M of AddressNC's 5.9M points), so it matches only 44%. Adding the full AddressNC file from September 2024, a free 745 MB download, raises the total by just 0.08 points. Its value is the vintage (seven weeks before the snapshot) and its unit points, not coverage.
- **Plain exact matching gets 94.1% (93.9% with block-addresses data alone).** That means house number, street after block-addresses' normalization, and ZIP. Cheap fixes add 3.8 points: highway spellings, hyphens and the USPS abbreviations the voter file uses inside street names (+1.6), moving directionals, matching by city or county when the ZIP disagrees, ignoring ½ and letter suffixes, and a type-and-direction-free street key (+1.1). Each relaxed key only counts when all its points sit within ~500 m of each other.
- **Misses cluster in a few places.** Urban (metropolitan ZIPs, RUCA 1–3) addresses match at 98.3% and rural (RUCA 4–10) at 96.4%. Counties run from 79.6% (Bertie) to 99.6% (Wake), median 97.4%. The worst counties have a campus (Watauga 82%: App State dorms), a military base (Onslow 94%: Camp Lejeune; Cumberland 96%: Fort Liberty), or rural highway addresses missing from the address points (Bertie).
- **Why addresses miss (2.17%, 170k residents).** In 57% of misses the street is in the data but that house number isn't, a sign of new construction (missed residents are much more often registered since 2023: 25% vs 15%). 13% are spelling variants, 8% on-base military housing, 8% campus dorms, 7% streets absent from every source, and 5% have no house number at all. PO boxes and rural routes are essentially absent (6 residents). NCSBE requires a residential address.
- **The Census geocoder is a fallback, not a replacement.** On a random 30,000 addresses it matched 95.9% (91.0% exact), below the local sources. Its points are interpolated along TIGER street ranges and sit a median 57 m (p90 176 m) from the local address point, more in rural areas. It does match 79.5% of local misses, and bulk runs are fast: 36–45 s per 10,000-row batch. All local misses fit in 10 batches (under 10 minutes). The whole file would take 402 batches (about 4.5 hours in sequence).
- **Recommendation for the unmatched: never drop them.** Place them with a cascade:
  1. Local address point: 97.8%.
  2. Interpolation along the same street between the nearest local house numbers: +1.2 points, 13 m median error on a holdout.
  3. Census geocoder: about +0.6 points.

  That leaves about 0.4% (~33k residents: campus dorms, unnumbered and on-base housing). Keep them in the population and in polls, and give them no house dot (or, if the UI needs a dot, an explicitly approximate one). Dropping them barely moves the statewide split (the DEM−REP registration margin moves 0.05 pt) but removes up to 96% of some campus and base precincts, which the per-precinct vote-choice fit (#9) can't absorb.
- **Apartments: one address point per building, spread the dots on screen.** 11.7% of residents list a unit. Unit-level points exist for 6.4% of residents; the rest share the building's point. Points stack: 6.7% of residents sit at a point with 10 or more others, 568 points hold 100+, and the largest (a Duke campus address) holds 3,677. Keep the real point as the resident's location for lookup and joins. Only at render time, lay a building's residents out on a small deterministic sunflower spiral around it, ordered by unit.

---

## 1. Data

### Residents

The snapshot is UTF-16 LE, tab-delimited, one header row, per NCSBE's `layout_VR_Snapshot.txt` ([layout](https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/layout_VR_Snapshot.txt)). Records end in CRLF, and a few fields contain a bare LF, which has to be removed before parsing. It holds 18,227,728 rows for 14.8M NCIDs: current voters plus ten years of removed history. Every A (active), I (inactive) and S (temporary: overseas and military) NCID appears exactly once, so no dedup is needed beyond filtering on status:

| status | rows | confidential | kept |
|---|---|---|---|
| A active | 6,986,365 | 322 | 6,986,043 |
| I inactive | 853,624 | 40 | 853,584 |
| S temporary (reason SO overseas citizen, SM military) | 14,475 | 0 | 14,475 |
| **residents** | **7,854,464** | **362** | **7,854,102** |

A + I + S is exactly the 7,854,464 that #7 took from NCSBE's count, so #7's population includes the S records. The 362 confidential records have blank addresses. Temporary registrants keep an NC residential address on file.

The residential address comes in `house_num`, `half_code` (½ or a letter), `street_dir`, `street_name`, `street_type_cd`, `street_sufx_cd` (a trailing directional, EXT or BUS), `unit_num`, `res_city_desc` and `zip_code`. The 7.85M residents live at **4,017,056 distinct addresses** (unit included) in **3,452,564 distinct buildings** (unit ignored). No names, phone numbers or mailing addresses are used; step 1 of the scripts drops them.

### Coordinate sources

| source | where | points | notes |
|---|---|---|---|
| **NAD via Overture** | block-addresses `overture/by-state/state=NC/` | 6,098,263 | Overture release 2026-08-19.0. In NC every row is National Address Database (`dataset = NAD`) |
| **OpenAddresses county/city** | block-addresses `addresses/us/nc/*-addresses-{county,city,town}.geojson` | 6,809,990 | 110 files. Most have no city, and 2.37M points have no ZIP (filled here from the Census ZCTA the point falls in, as `compact.py` does) |
| **OpenAddresses statewide** | block-addresses `addresses/us/nc/statewide-addresses-state.geojson` | 2,671,093 | Source `us/nc/statewide` is AddressNC ([source JSON](https://github.com/openaddresses/openaddresses/blob/master/sources/us/nc/statewide.json)). Its `.meta` reports 5,914,208 features for job 413823 (July 2024), but the collection file holds only 2,671,093, covering 78 counties, so it is truncated |
| **AddressNC, full** (fetched for this study) | `https://s3.amazonaws.com/dit-cgia-gis-data/NCOM-data/addresses/AddressNC-addresses-09-18-2024.zip` | 5,977,537 | NC OneMap's statewide address points ([AddressNC](https://www.nconemap.gov/datasets/nconemap::address-points-addressnc/about); public bucket, snapshots from 2023 to 2026). This is the vintage closest before the snapshot. File geodatabase with decimal-degree fields and a `Unit` field |

## 2. Method

Both sides go through block-addresses' own normalization (`scripts/compact.py`, imported rather than copied), so voter and source streets use the same rules: every token mapped to its USPS abbreviation, and spelled or bare ordinals turned into `5TH`. The voter street is `street_dir street_name street_type_cd street_sufx_cd`. The house number splits into a numeric part and a suffix (`106 B` → 106 / B; `12½` → 12 / 1/2).

Each distinct address is tried against each source through a cascade of keys, loosest last ([`04_match.py`](../../prototypes/geocoding/04_match.py)):

| tier | key | fixes | gain (residents) |
|---|---|---|---|
| 1 exact | number, suffix, street, ZIP | block-addresses' normalization as is | 94.07% |
| 2 canon | as 1 with hyphens as spaces, apostrophes dropped, the rest of the USPS Pub 28 suffix list, highway names collapsed | `GIBSONVILLE-OSSIPEE RD`; voter `JACK MOORE MTN RD` vs source `JACK MOORE MOUNTAIN RD`; `NC HWY 62` / `NORTH CAROLINA HIGHWAY 62` / NAD `State Highway HIGHWAY 62 North`; `CHURCH` vs `CH` | +1.64 |
| 3 dirmove | as 2 with directionals moved to the end | voter `2ND ST N` vs AddressNC `N 2ND ST` | +0.26 |
| 4 city | number, suffix, street, city, county | ZIP disagrees | +0.37 |
| 5 county | number, suffix, street, county | ZIP and city disagree | +0.31 |
| 6 nosuffix | number, street, ZIP, ignoring ½ / letter suffixes | `12 1/2 MAIN ST` vs `12 MAIN ST` | +0.14 |
| 7 core | number, street minus type and directional tokens and spaces, ZIP | `MAIN ST` vs `MAIN AVE`, `MC DONALD` vs `MCDONALD` | +1.05 |

For tiers 4–7, a key only counts when all its source points lie within ~500 m (0.005°) of each other, so a relaxed key never chooses between two different places. An eighth tier (the core key within the whole county) was tried and dropped: against the Census geocoder its points were a median 341 m off, and 38% were more than 1 km off.

A key's point is the mean of its unit-less points, or of all its points when the source lists only units. When the resident has a unit and the source has a point for that unit, the unit's point is used. When several sources hit at the same tier, the priority is AddressNC, then OpenAddresses statewide, then OpenAddresses county/city, then NAD.

**Checking the relaxed tiers.** Against Census points (§5), tier-1 matches are a median 57 m off with 0.4% over 1 km. Tiers 2–7 are a median 54–72 m off with 0–4% over 1 km. The relaxed tiers are slightly noisier but not wrong in bulk, and their points still beat the Census's own non-exact matches (4.4% over 1 km).

## 3. Match rates

### By source

| source | residents, tier 1 only | residents, all tiers | distinct addresses, all tiers |
|---|---|---|---|
| AddressNC full (Sept 2024) | 91.35% | 96.92% | 96.52% |
| OA statewide (truncated) | 39.64% | 44.10% | 43.42% |
| OA county/city | 73.20% | 79.41% | 78.57% |
| NAD (Overture) | 89.34% | 95.96% | 95.57% |
| **block-addresses combined** (the three above) | 93.87% | **97.75%** | **97.44%** |
| **all four combined** | 94.07% | **97.83%** | **97.53%** |

NAD in NC is built from the same county and AddressNC feeds, which is why the full AddressNC adds only 0.08 points to what block-addresses already has. Distinct addresses match slightly less often than residents because a missed address holds fewer residents on average (1.7 against 1.96).

### Urban vs rural

"Urban" here is **USDA ERS 2020 Rural-Urban Commuting Area (RUCA) codes, ZIP code version**, applied to the resident's own ZIP ([ERS RUCA](https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes)). This choice has three advantages:

- every resident, matched or not, has a ZIP on file, so a miss can be classified without a coordinate;
- RUCA is built from 2020 Census urban cores plus commuting flows, and ERS adapted it to ZIP codes;
- a ZIP is much finer than a county, where a big metro county like Wake mixes towns and farmland.

The binary split below uses the common metropolitan / non-metropolitan cut (codes 1–3 against 4–10).

| setting (primary RUCA of ZIP) | residents | matched, all sources | block-addresses only | AddressNC alone | NAD alone | unmatched |
|---|---|---|---|---|---|---|
| 1 metropolitan core | 4,822,215 | 98.36% | 98.33% | 97.73% | 97.50% | 79,146 |
| 2–3 metropolitan commuting | 1,174,458 | 97.98% | 97.93% | 96.85% | 95.78% | 23,742 |
| 4–6 micropolitan | 1,136,299 | 96.48% | 96.15% | 94.77% | 92.05% | 40,019 |
| 7–9 small town | 202,460 | 96.60% | 96.57% | 95.73% | 95.48% | 6,878 |
| 10 rural | 518,661 | 96.09% | 95.92% | 94.62% | 90.81% | 20,261 |
| **urban (1–3)** | 5,996,673 | **98.28%** | 98.25% | | | |
| **rural (4–10)** | 1,857,420 | **96.38%** | 96.13% | | | |

Nine residents have a ZIP with no RUCA code.

Rural addresses miss about twice as often. The reasons are rural highway addresses without points, and county feeds that are thinner outside towns: NAD alone gets only 90.8% in RUCA 10.

### By county

The median county matches 97.4%, the 10th percentile 92.9%, and the range runs from 79.6% to 99.6%. The full table is in the appendix. The low ones, with the dominant miss category from [`06_misses.py`](../../prototypes/geocoding/06_misses.py):

| county | matched | main reason |
|---|---|---|
| Bertie | 79.6% | house numbers missing on rural highways (HWY 13, HWY 17, HWY 45) |
| Watauga | 82.4% | App State dorms (`HARDIN DOGWOOD DORM ST`, etc.) |
| Swain | 88.8% | house number missing on a known street |
| Camden, Pasquotank | 89.8%, 90.6% | house number missing on a known street |
| Richmond, Martin, McDowell | 91–92% | house number missing on a known street; spelling variants (Richmond) |
| Onslow | 94.0% | Camp Lejeune and Tarawa Terrace base housing (6,562 residents) |
| Cumberland | 95.9% | Fort Liberty base housing (6,680 residents) |

## 4. Why addresses miss

Every missed address gets the first category that fits:

| category | test | addresses | residents | % of misses | registered since 2023 |
|---|---|---|---|---|---|
| num_gap | street exists in the ZIP, number missing but inside the street's number range | 47,868 | 72,294 | 42.5% | 20.5% |
| num_beyond | street exists in the ZIP, number outside the source's range | 15,719 | 24,663 | 14.5% | 19.0% |
| similar_street | a street in the same ZIP is similarly spelled (Jaro-Winkler ≥ 0.9 on the core key) | 11,965 | 21,526 | 12.7% | 15.6% |
| military | city is a base (Fort Liberty, Camp Lejeune, Tarawa Terrace, …) | 6,689 | 13,587 | 8.0% | 33.5% |
| campus | university prefix (NCSU, WFU, WSSU, AGGIE, …) or HALL / DORM in the street | 5,203 | 12,761 | 7.5% | 57.7% |
| street_absent | no similar street in the ZIP in any source | 7,008 | 11,862 | 7.0% | 23.3% |
| no_number | house number 0 (NCSU dorms, `WFU … HALL`) | 1,633 | 8,001 | 4.7% | 57.4% |
| other_zip | street exists elsewhere in the county but not in this ZIP | 2,744 | 4,643 | 2.7% | 19.7% |
| ambiguous | a relaxed key exists but its points are more than 500 m apart | 449 | 711 | 0.4% | 15.3% |
| po_rural | PO box / rural route / general delivery | 5 | 6 | 0.0% | |

For comparison, 15.3% of matched residents registered since 2023, against 25.4% of missed ones.

What a sample of misses looks like (house numbers left out):

- **New construction or missing points** (num_gap, num_beyond): the street is there and neighbouring numbers are there, but this number is not, as on `TROY MARTIN RD` or `OLD LAKE RD`. The higher share of recent registrants, and the 91% Census match rate for these (TIGER ranges cover the whole block), fit infill and new lots more than typos.
- **Spelling variants**: `SAINT PAULS RD` / `ST PAULS RD`, `DEERFIELD TRCE` / `DEERFIELD TRACE`, `RILEYS RIDGE RD` / `RILEY'S RIDGE RD`, `CEMETARY` / `CEMETERY`, `VICTORIA CIR` / `VICTORIA CR`, `HWY 13 N` / `HWY 13N`. The systematic ones were found by ranking the token differences between each miss and its closest source street, and are now fixed in tier 2. What remains is a long tail of one-off pairs.
- **Campus**: the voter file writes dorm rooms as a street-like hall name, often with house number 0 (`WFU TAYLOR HALL`, `NCSU BRAGAW`, `STADIUM HTS NEWLAND DORM DR`). No address source has these.
- **Military**: base housing on Fort Liberty and Camp Lejeune is largely missing from AddressNC and NAD.
- PO boxes are not an issue. The residential address is required, and a mailing address (not used here) is kept in separate fields.

## 5. Census Bureau geocoder

The batch endpoint is `https://geocoding.geo.census.gov/geocoder/locations/addressbatch`. It takes a CSV of `Unique ID, Street address, City, State, ZIP` with "an upper limit of 10,000 records per batch file", and the benchmark `Public_AR_Current` is the current MAF/TIGER address ranges ([Geocoding Services API](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html), [benchmarks](https://geocoding.geo.census.gov/geocoder/benchmarks)). There is no key, and the documentation states no rate limit. Five batches were run one after another ([`05_census.py`](../../prototypes/geocoding/05_census.py)): three from all resident addresses and two from local misses, each drawn resident-weighted.

| sample | addresses | match | exact | non-exact | tie | no match | time per 10,000 |
|---|---|---|---|---|---|---|---|
| all addresses | 30,000 | 95.9% | 91.0% | 4.9% | 0.4% | 3.7% | 35.6 s (34.7–36.1) |
| local misses (still missed after tiers 1–7) | 14,062 | 79.5% | 65.7% | 13.8% | 1.9% | 18.6% | 44.7 s (42.1–47.2) |

The Census match rate by miss category: num_gap 91%, num_beyond 86%, similar_street 85% (but only 45% exact), other_zip 76%, military 64%, street_absent 63%, campus 16%, no_number 0%.

**Coverage.** Census alone (95.9%) is below local alone (97.8%). Within the all-addresses sample, it matched 96.3% of addresses the local sources matched and 76.7% of those they missed.

**Positional quality.** For the 28,267 sample addresses both matched, the distance from the Census point to the local address point:

| group | n | median | p90 | p99 | > 250 m | > 1 km |
|---|---|---|---|---|---|---|
| all | 28,267 | 57 m | 176 m | 544 m | 4.9% | 0.4% |
| Census exact | 26,866 | 56 m | 173 m | 482 m | 4.5% | 0.2% |
| Census non-exact | 1,401 | 68 m | 274 m | 9.3 km | 11.1% | 4.4% |
| metro core ZIPs | 17,583 | 53 m | 151 m | | 2.9% | |
| rural ZIPs (RUCA 10) | 1,751 | 71 m | 259 m | | 10.6% | |

This is interpolation error. The Census places a number proportionally along the TIGER segment's address range, offset to one side of the street centreline, while AddressNC and NAD points sit on the structure or parcel. Rural lots are long and ranges are sparse, so the error grows there. On a state map a 57 m error is invisible. At town-rung zoom it can put a dot on the neighbour's lot or in the road.

**Bulk cost.** The 99,283 distinct addresses still missed locally fit in 10 batches, under 10 minutes in sequence. Geocoding all 4,017,056 addresses would be 402 batches, about 4.5 hours in sequence. That is feasible but pointless given the lower match rate and coarser points.

## 6. Fallbacks for unmatched residents

A holdout test ([`08_fallbacks.py`](../../prototypes/geocoding/08_fallbacks.py)): 20,000 matched residents were treated as missing, placed by each fallback, and compared with their real point.

| fallback | median error | p90 | > 1 km | can place |
|---|---|---|---|---|
| street interpolation between the nearest lower and higher same-parity house numbers on the same street and ZIP (local data only) | 13 m | 107 m | 1.9% | 61,630 missed residents |
| street interpolation, number beyond the range: nearest end | 44 m | 216 m | 0.9% | 31,012 more |
| Census geocoder (vs local points, §5) | 57 m | 176 m | 0.4% | ~79% of what is left |
| median point of the precinct's matched residents | 1,374 m | 4,216 m | 64% | all but 233 missed residents |
| median point of the ZIP's matched residents | 3,364 m | 8,338 m | 92% | all |

Local street interpolation beats the Census geocoder: the neighbouring points are real address points, and the gap between them is short. It places 92,642 of the 170,054 missed residents (54.5%), nearly all num_gap and num_beyond. Precinct and ZIP centroids are a kilometre or more off, so a dot placed there would visibly sit in the wrong place. A Census-block centroid can't be used, because it needs the block, and the block needs a coordinate: the voter file has no block field.

A projected cascade, using the Census rates by category above:

| step | residents placed | cumulative |
|---|---|---|
| 1. local address point (tiers 1–7) | 7,684,048 | 97.83% |
| 2. local street interpolation | +92,642 | 99.01% |
| 3. Census geocoder on the rest (10 batches) | ≈ +44,000 | ≈ 99.6% |
| residual: mostly campus dorms (~10.6k), house number 0 (8.0k), on-base housing (~4.9k), streets absent everywhere (~4.4k) | ≈ 33,000 | ≈ 0.4% |

## 7. Handling the residual: options and their effect

The unmatched are not a random sample. They are younger (mean age 42.9 against 49.0), less often Republican (27.0% against 30.0%), more often unaffiliated (41.5% against 37.7%), and more often Black (22.8% against 19.6%). The residual after the cascade is more skewed still: students (UNA 58–63%, REP 8–10%, mean age 22) and soldiers (REP 34.5%, DEM 16.8%, mean age 30).

| option | true split | polls | map |
|---|---|---|---|
| **Drop the resident** | Changes. Statewide it barely moves: dropping all 170k local misses shifts the DEM−REP margin from +1.37 to +1.32 (0.05 pt). By county: median shift 0.13 pt, max 1.54 pt. By precinct: median 0.13 pt, p95 1.32 pt, and 210 of 2,697 precincts shift by 1 pt or more. Campus and base precincts lose up to 96% of residents. The population no longer equals the 7.85M registered voters the page names, and #9's per-precinct fit loses whole student precincts | Polls are drawn from a smaller, slightly older and more Republican population. The poll-vs-truth logic still holds, but it's no longer NC's registered voters | Clean: every dot is real |
| **Place at precinct / block centroid** | Unchanged | Unchanged | Dots are a median 1.4 km off, and a precinct's residual stacks on one point (a visible clump on campuses). A block centroid isn't possible without a coordinate |
| **Keep in polls with no dot** | Unchanged | Unchanged. A 1,200-person poll includes about 5 dotless residents (0.4%), so the poll-result UI has to show a sampled resident without highlighting a house | ~33k of 7.85M dots missing, mostly dorm rooms and base housing, which are unaddressable anyway |

**Recommendation.** Run the cascade (local point, then local interpolation, then Census) and keep the residual ~0.4% as residents with no house dot. The true split, poll draws and the "7.85M registered voters" number all stay exact, and every dot on the map stays a real address. The one design cost is that a poll's sampled residents can include someone the map can't point to. The resident card can say "lives in campus housing / on base, not shown on the map". If the design team would rather every resident had a dot, place the residual at the precinct median with a visibly different "approximate" style. Don't draw it as a house.

Store the method with each resident (`point`, `unit point`, `interpolated`, `census`, `none`). Then later rungs can filter or style by precision, and the town rung can hide approximate dots.

## 8. Apartments and units

| measure | value |
|---|---|
| residents listing a unit | 11.7% (917,038; 27,545 of them unmatched) |
| of those, placed at the unit's own point | 500,400 (6.4% of all residents) |
| placed at the building point | 389,093 (5.0%) |
| distinct coordinates carrying residents | 3,511,252 |
| residents sharing a point with at least one other | 82.5% (mostly households at a house) |
| residents at a point with ≥ 10 / ≥ 50 / ≥ 200 residents | 6.7% / 2.4% / 1.1% |
| points with ≥ 100 residents | 568 |
| points shared by more than one distinct address (units) | 85,630; up to 386 units at one point |
| largest stacks | 3,677 (Chapel Dr, Durham: Duke), 3,605 (Fayetteville St, Durham: NCCU), 2,908 (University City Blvd, Charlotte: UNC Charlotte) |

AddressNC and NAD often give each unit its own record at the building's coordinate, so a "unit point" rarely separates dots on screen.

**Recommendation.**

1. The stored location is the matched address point: the unit's point when the source has one, else the building's. Lookup, joins and the address collection use it.
2. Spreading is a render-time layout, not data. Lay the residents who share a point on a sunflower (Vogel) spiral around it: resident *k* at radius *s·√k*, angle *k·137.5°*, with *s* about 1.5–2 m at town zoom. Order them by unit and then by draw number, so a building always looks the same and a unit's residents sit together. The spiral's radius grows with √n: about 20 m for 100 residents and 120 m for the 3,677 at Duke, which reads as a campus-sized cluster.
3. Don't jitter at random, which reshuffles on every load, and don't push dots onto building footprints. Footprints are a separate dataset and a separate join, for no gain at state zoom.

## Caveats

- The OpenAddresses statewide file in block-addresses is truncated. That doesn't matter here because NAD covers the same ground, but block-addresses' own NC address counts are low for the same reason. The full AddressNC file is a drop-in fix there as well.
- Census rates come from 50,000 addresses. The residual after the cascade (≈ 33k, 0.4%) is a projection from category rates, not a full run.
- RUCA is assigned by the resident's ZIP, not their point. A ZIP that straddles a town edge takes one code.
- Tier 7's Census distances show a tail (3.4% over 1 km on 297 checks). A stricter build could stop at tier 6 and send tier-7 addresses to interpolation or Census instead, at a cost of 1.05 points of rooftop matches.
- Every number is for the Nov 2024 snapshot and the sources' 2024–2026 vintages. NAD (Overture 2026-08) postdates the snapshot, so it may contain points that didn't exist in 2024. That helps matching and can't hurt placement.

## Sources

- NCSBE, snapshot file and layout: <https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/VR_Snapshot_20241105.zip>, <https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/layout_VR_Snapshot.txt>. Status and reason descriptions are from the snapshot's own `voter_status_desc` / `voter_status_reason_desc` columns.
- OpenAddresses source `us/nc/statewide`: <https://github.com/openaddresses/openaddresses/blob/master/sources/us/nc/statewide.json>. Job 413823 metadata (5,914,208 features) is in block-addresses' `statewide-addresses-state.geojson.meta`.
- AddressNC (NC OneMap): <https://www.nconemap.gov/datasets/nconemap::address-points-addressnc/about>, terms <https://www.nconemap.gov/pages/terms>. Bucket listing: <https://s3.amazonaws.com/dit-cgia-gis-data?prefix=NCOM-data/addresses/>.
- Overture addresses (NAD in the US): <https://docs.overturemaps.org/guides/addresses/>. How block-addresses fetches them: `scripts/fetch_overture.py` in [block-addresses](https://github.com/shivan2418/block-addresses).
- block-addresses street normalization: `scripts/compact.py` and `scripts/normalize.json` in [block-addresses](https://github.com/shivan2418/block-addresses) (commit acbe80c).
- USPS Publication 28, Appendix C1, street suffix abbreviations: <https://pe.usps.com/text/pub28/28apc_002.htm>.
- Census Geocoding Services API (batch format, 10,000-record limit, benchmarks): <https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.html>, <https://geocoding.geo.census.gov/geocoder/benchmarks>.
- USDA ERS Rural-Urban Commuting Area codes, 2020, ZIP code file: <https://www.ers.usda.gov/data-products/rural-urban-commuting-area-codes>.
- Census cartographic boundary files (county subdivisions 2023, ZCTA 2020) for county and ZIP point-in-polygon: <https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html>.

## Appendix: match rate by county

"All sources" includes the full AddressNC. "block-addresses only" is OA statewide + OA county/city + NAD. Per-source columns are each source on its own, all tiers.

| county | residents | matched %, all sources | block-addresses only % | AddressNC % | OA statewide % | OA county/city % | NAD % | unmatched |
|---|---|---|---|---|---|---|---|---|
| ALAMANCE | 119,766 | 98.45 | 98.31 | 98.16 | 0.01 | 90.95 | 95.11 | 1,862 |
| ALEXANDER | 25,966 | 98.88 | 98.88 | 98.54 | 98.52 | 91.39 | 97.1 | 290 |
| ALLEGHANY | 8,333 | 98.22 | 97.92 | 97.9 | 0.0 | 0.01 | 97.92 | 148 |
| ANSON | 16,745 | 95.18 | 95.18 | 94.55 | 0.0 | 90.24 | 94.55 | 807 |
| ASHE | 20,829 | 96.97 | 96.8 | 95.33 | 0.0 | 81.9 | 94.62 | 632 |
| AVERY | 12,871 | 93.53 | 93.32 | 88.42 | 0.02 | 78.77 | 90.22 | 833 |
| BEAUFORT | 35,125 | 96.87 | 96.87 | 96.72 | 96.65 | 94.29 | 92.02 | 1,100 |
| BERTIE | 12,838 | 79.62 | 79.62 | 79.01 | 0.68 | 50.13 | 79.02 | 2,617 |
| BLADEN | 23,710 | 94.23 | 94.23 | 93.36 | 93.16 | 91.48 | 93.06 | 1,369 |
| BRUNSWICK | 141,256 | 99.32 | 99.32 | 98.78 | 98.75 | 84.44 | 98.88 | 966 |
| BUNCOMBE | 217,700 | 98.64 | 98.64 | 98.4 | 98.36 | 98.53 | 98.27 | 2,959 |
| BURKE | 61,321 | 96.73 | 96.73 | 95.88 | 95.76 | 81.4 | 96.25 | 2,003 |
| CABARRUS | 162,415 | 98.34 | 98.34 | 97.49 | 97.43 | 98.25 | 98.02 | 2,696 |
| CALDWELL | 56,461 | 97.32 | 97.31 | 96.83 | 0.02 | 89.44 | 97.02 | 1,512 |
| CAMDEN | 8,807 | 89.78 | 89.78 | 85.28 | 0.0 | 88.96 | 85.33 | 900 |
| CARTERET | 58,890 | 98.54 | 97.43 | 98.23 | 0.0 | 93.62 | 97.2 | 862 |
| CASWELL | 15,871 | 93.71 | 93.64 | 90.77 | 0.16 | 93.09 | 90.3 | 998 |
| CATAWBA | 117,341 | 99.63 | 99.55 | 99.55 | 0.04 | 95.65 | 93.86 | 440 |
| CHATHAM | 63,790 | 98.04 | 97.97 | 97.96 | 6.31 | 97.88 | 96.3 | 1,253 |
| CHEROKEE | 24,597 | 96.98 | 96.52 | 96.88 | 0.0 | 0.0 | 96.52 | 744 |
| CHOWAN | 10,681 | 98.99 | 98.99 | 95.74 | 95.74 | 92.37 | 96.86 | 108 |
| CLAY | 10,356 | 98.74 | 98.7 | 97.25 | 0.0 | 75.07 | 97.14 | 131 |
| CLEVELAND | 71,050 | 95.27 | 91.78 | 91.19 | 0.03 | 0.09 | 91.77 | 3,358 |
| COLUMBUS | 38,082 | 97.18 | 97.17 | 96.32 | 0.02 | 93.04 | 96.18 | 1,074 |
| CRAVEN | 79,736 | 97.68 | 97.54 | 95.95 | 0.0 | 86.83 | 95.53 | 1,847 |
| CUMBERLAND | 230,308 | 95.9 | 95.75 | 95.86 | 0.0 | 0.0 | 95.75 | 9,432 |
| CURRITUCK | 25,212 | 97.52 | 97.52 | 97.05 | 0.0 | 85.34 | 97.07 | 624 |
| DARE | 34,280 | 95.36 | 95.36 | 89.82 | 89.82 | 89.99 | 90.21 | 1,592 |
| DAVIDSON | 121,752 | 98.7 | 98.58 | 98.55 | 3.82 | 0.06 | 98.56 | 1,588 |
| DAVIE | 33,700 | 98.76 | 98.75 | 98.35 | 0.0 | 92.44 | 98.34 | 419 |
| DUPLIN | 32,693 | 97.42 | 97.37 | 96.3 | 0.01 | 77.41 | 96.22 | 844 |
| DURHAM | 253,353 | 98.33 | 98.33 | 96.81 | 95.81 | 98.23 | 95.65 | 4,234 |
| EDGECOMBE | 36,542 | 92.63 | 92.56 | 78.6 | 0.02 | 79.22 | 78.14 | 2,694 |
| FORSYTH | 279,993 | 97.4 | 97.39 | 97.34 | 0.11 | 97.35 | 97.33 | 7,271 |
| FRANKLIN | 55,589 | 97.96 | 97.96 | 97.55 | 97.54 | 0.8 | 92.96 | 1,134 |
| GASTON | 163,716 | 98.9 | 98.86 | 98.2 | 0.0 | 82.18 | 98.13 | 1,803 |
| GATES | 8,531 | 92.92 | 92.92 | 88.3 | 88.29 | 79.91 | 88.89 | 604 |
| GRAHAM | 6,315 | 93.79 | 93.79 | 92.18 | 91.96 | 69.77 | 92.24 | 392 |
| GRANVILLE | 42,203 | 98.18 | 98.18 | 94.23 | 94.19 | 83.48 | 94.24 | 768 |
| GREENE | 11,278 | 98.16 | 98.14 | 97.32 | 0.01 | 83.24 | 97.38 | 208 |
| GUILFORD | 397,725 | 97.28 | 97.27 | 95.85 | 38.07 | 92.43 | 95.83 | 10,815 |
| HALIFAX | 36,427 | 97.05 | 96.93 | 96.27 | 0.0 | 79.23 | 95.92 | 1,075 |
| HARNETT | 93,454 | 99.14 | 99.11 | 99.1 | 0.04 | 97.02 | 99.06 | 800 |
| HAYWOOD | 48,250 | 99.4 | 99.4 | 98.52 | 98.52 | 84.44 | 98.91 | 291 |
| HENDERSON | 92,782 | 98.79 | 98.78 | 98.2 | 0.01 | 93.6 | 98.24 | 1,121 |
| HERTFORD | 14,356 | 97.56 | 97.56 | 97.27 | 97.19 | 94.3 | 97.34 | 351 |
| HOKE | 37,259 | 96.99 | 96.98 | 96.71 | 0.02 | 80.27 | 96.47 | 1,120 |
| HYDE | 3,186 | 91.81 | 91.81 | 89.11 | 89.11 | 82.11 | 84.24 | 261 |
| IREDELL | 146,563 | 99.48 | 99.48 | 98.38 | 0.0 | 99.48 | 99.36 | 755 |
| JACKSON | 31,639 | 95.91 | 95.89 | 95.39 | 5.47 | 66.35 | 95.32 | 1,295 |
| JOHNSTON | 165,650 | 98.72 | 98.72 | 96.74 | 96.48 | 79.9 | 98.19 | 2,121 |
| JONES | 7,364 | 97.46 | 97.46 | 96.88 | 96.88 | 84.76 | 96.77 | 187 |
| LEE | 41,334 | 97.92 | 97.88 | 97.23 | 0.0 | 87.86 | 96.97 | 859 |
| LENOIR | 39,565 | 97.12 | 97.12 | 95.18 | 95.07 | 79.19 | 95.98 | 1,141 |
| LINCOLN | 70,663 | 96.49 | 96.43 | 96.06 | 0.0 | 96.13 | 92.53 | 2,477 |
| MACON | 29,587 | 97.41 | 97.41 | 96.0 | 95.93 | 82.96 | 95.94 | 765 |
| MADISON | 17,836 | 96.06 | 96.06 | 94.43 | 94.43 | 91.18 | 89.77 | 702 |
| MARTIN | 16,761 | 91.56 | 91.56 | 87.42 | 87.39 | 83.32 | 87.39 | 1,415 |
| MCDOWELL | 31,508 | 91.75 | 91.75 | 90.8 | 90.75 | 87.15 | 90.61 | 2,598 |
| MECKLENBURG | 842,243 | 99.38 | 99.38 | 99.31 | 0.0 | 89.23 | 99.26 | 5,196 |
| MITCHELL | 11,508 | 96.06 | 96.06 | 96.0 | 95.95 | 0.23 | 95.87 | 453 |
| MONTGOMERY | 17,768 | 95.69 | 95.68 | 95.52 | 95.44 | 92.86 | 95.59 | 766 |
| MOORE | 79,453 | 99.55 | 99.49 | 99.11 | 0.0 | 96.41 | 97.33 | 356 |
| NASH | 71,080 | 98.12 | 98.12 | 97.31 | 58.59 | 83.82 | 97.25 | 1,334 |
| NEW HANOVER | 190,662 | 99.46 | 99.46 | 98.54 | 98.54 | 99.4 | 98.51 | 1,039 |
| NORTHAMPTON | 13,279 | 92.88 | 92.88 | 91.42 | 91.4 | 80.29 | 82.63 | 946 |
| ONSLOW | 137,624 | 93.99 | 93.99 | 93.54 | 0.23 | 79.15 | 93.31 | 8,266 |
| ORANGE | 115,623 | 98.89 | 98.89 | 98.62 | 0.02 | 97.99 | 98.57 | 1,280 |
| PAMLICO | 10,648 | 94.9 | 94.9 | 87.98 | 87.84 | 89.57 | 76.02 | 543 |
| PASQUOTANK | 32,027 | 90.56 | 90.56 | 85.77 | 85.82 | 86.18 | 86.31 | 3,023 |
| PENDER | 52,111 | 98.65 | 98.65 | 97.8 | 97.76 | 76.85 | 97.85 | 701 |
| PERQUIMANS | 10,836 | 98.97 | 98.97 | 98.89 | 98.88 | 98.93 | 98.5 | 112 |
| PERSON | 28,748 | 98.99 | 98.99 | 98.45 | 98.42 | 80.94 | 98.46 | 291 |
| PITT | 129,047 | 94.91 | 94.6 | 89.27 | 0.0 | 66.27 | 90.21 | 6,567 |
| POLK | 17,438 | 97.04 | 94.88 | 93.54 | 0.07 | 71.87 | 90.25 | 516 |
| RANDOLPH | 99,775 | 99.49 | 99.34 | 99.46 | 0.02 | 0.47 | 99.34 | 513 |
| RICHMOND | 29,464 | 91.88 | 90.67 | 90.89 | 0.0 | 0.0 | 90.67 | 2,392 |
| ROBESON | 79,175 | 93.01 | 93.0 | 88.36 | 72.51 | 65.77 | 29.8 | 5,534 |
| ROCKINGHAM | 64,704 | 99.35 | 99.32 | 97.22 | 0.01 | 99.29 | 99.25 | 422 |
| ROWAN | 101,919 | 99.27 | 99.02 | 99.0 | 0.08 | 98.14 | 97.71 | 748 |
| RUTHERFORD | 48,084 | 98.41 | 98.4 | 98.07 | 98.03 | 92.08 | 97.87 | 765 |
| SAMPSON | 39,470 | 96.08 | 96.08 | 95.89 | 95.83 | 0.16 | 95.86 | 1,546 |
| SCOTLAND | 22,821 | 93.89 | 93.86 | 90.74 | 0.0 | 68.42 | 90.71 | 1,395 |
| STANLY | 46,711 | 98.74 | 98.74 | 98.25 | 97.92 | 90.48 | 94.99 | 587 |
| STOKES | 33,830 | 98.1 | 98.1 | 97.85 | 97.77 | 94.33 | 88.63 | 644 |
| SURRY | 49,366 | 98.53 | 98.53 | 98.29 | 98.32 | 81.85 | 98.2 | 728 |
| SWAIN | 10,254 | 88.75 | 88.66 | 87.94 | 18.32 | 64.7 | 87.97 | 1,154 |
| TRANSYLVANIA | 27,249 | 96.3 | 96.3 | 96.15 | 96.13 | 0.35 | 96.02 | 1,008 |
| TYRRELL | 2,358 | 96.31 | 96.31 | 89.06 | 89.06 | 82.91 | 92.96 | 87 |
| UNION | 185,310 | 96.24 | 96.24 | 95.85 | 95.8 | 0.04 | 96.12 | 6,971 |
| VANCE | 29,192 | 96.92 | 96.91 | 96.44 | 0.07 | 95.64 | 94.87 | 899 |
| WAKE | 862,880 | 99.62 | 99.62 | 99.34 | 99.29 | 99.19 | 99.34 | 3,305 |
| WARREN | 13,588 | 95.13 | 95.13 | 91.45 | 0.11 | 91.76 | 93.5 | 662 |
| WASHINGTON | 8,218 | 94.28 | 94.28 | 94.17 | 94.17 | 3.2 | 94.24 | 470 |
| WATAUGA | 46,598 | 82.43 | 82.43 | 78.27 | 35.44 | 68.71 | 78.54 | 8,188 |
| WAYNE | 78,034 | 98.84 | 98.84 | 98.31 | 98.29 | 97.36 | 96.23 | 909 |
| WILKES | 45,718 | 97.2 | 96.51 | 95.59 | 0.08 | 66.6 | 95.05 | 1,279 |
| WILSON | 56,903 | 95.89 | 95.87 | 95.83 | 95.6 | 4.74 | 95.7 | 2,337 |
| YADKIN | 25,763 | 97.88 | 97.86 | 97.66 | 0.0 | 95.86 | 97.68 | 547 |
| YANCEY | 14,712 | 97.89 | 97.89 | 97.83 | 97.82 | 0.48 | 97.74 | 310 |

| min county % | p10 | median | max |
|---|---|---|---|
| 79.62 | 92.85 | 97.36 | 99.63 |
