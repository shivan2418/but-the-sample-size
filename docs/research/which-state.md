# Which state to simulate?

Research for issue #3. Question: which real US state, roughly 5–12M people (Ohio / Denmark / Netherlands scale), should the state rung simulate, given that every real address gets synthetic residents whose race, urban/rural setting and political affiliation come from real aggregate data?

Researched 2026-09-27.

## Recommendation

**Michigan.** It has the closest 2024 presidential result of any state near Ohio's size (Trump +1.4), it flipped between 2020 and 2024, and it has everything the build needs from public sources: one statewide address-point source, a statewide 2024 precinct shapefile published by the state, and clean precinct-level 2024 returns with no geographically unplaceable "absentee" pseudo-precincts. With 10.1M people it is almost exactly Ohio's scale. Detroit, its suburbs, the rural north and the college towns give strong clustering of race, setting and vote by place, which is what the rung needs to show.

Political affiliation has to come from vote share. Michigan has no party registration, and neither does any close state near that size except North Carolina and Arizona, where registration is a poor stand-in anyway (see below).

**Runner-up: Wisconsin.** It is closer still (Trump +0.9) and has the easiest election-data join in the country: the Legislature publishes 2024 results already allocated to ward polygons. At 5.9M people it is Denmark scale. The catch is addresses: its statewide address layer comes from parcels, so apartment buildings likely count as one address each, and it is much less racially diverse, which makes the race dimension less interesting.

## Ranked shortlist

| Rank | State | Pop. (2020 Census) | 2024 pres. margin | 2020 margin | Party registration? | Statewide address source in OpenAddresses | Precinct results (MEDSL 2024) |
|---|---|---|---|---|---|---|---|
| 1 | **Michigan** | 10.08M | R +1.41 | D +2.78 | No | Yes: state "Site/Structure Points", 2026 upload | 4,434 precincts, 0% of votes in pseudo-precincts |
| 2 | **Wisconsin** | 5.89M | R +0.86 | D +0.62 | No | Yes, but parcel-based (State Cartographer's statewide parcels) | 3,601 reporting units, 0% pseudo |
| 3 | **Georgia** | 10.71M | R +2.19 | D +0.24 | No | **No statewide source**: 133 county/city files covering 124 of 159 counties; the rest needs NAD | 2,702 precincts, ~0% pseudo |
| 4 | North Carolina | 10.44M | R +3.21 | R +1.35 | Yes, but 39% unaffiliated | Yes: AddressNC statewide (2024) | 2,908 precincts, 1.9% of votes in absentee/provisional pseudo-precincts |
| 5 | Arizona | 7.15M | R +5.53 | D +0.31 | Yes, about a third "other" | Yes: statewide file | 1,716 precincts |
| — | Ohio (baseline) | 11.80M | R +11.21 | R +8.03 | No | Yes: statewide LBRS address points | 8,878 precincts |
| — | Virginia | 8.63M | D +5.77 | D +10.11 | No | Yes: VDEM statewide points | 2,669 precincts, ~2.6% pseudo (provisionals) |
| — | Minnesota | 5.71M | D +4.24 | D +7.11 | No | Yes: MnGeo statewide | 4,103 precincts |

Margins are computed from vote totals (Republican share minus Democratic share of all presidential votes): 2024 from MEDSL's `2024-president-state.csv`, 2020 by summing county results. Other states in range (NJ, WA, TN, MA, IN, MO, MD, CO, SC) are all 11+ points apart in 2024 except NJ (D +5.9) and CO (D +11.0), so they fail on political balance. Pennsylvania (13.0M) is out of range.

## Criterion by criterion

### 1. Census data: population, race, urban/rural

This does not separate the candidates. It is the same national product for every state:

- **Population and race** down to census block: the 2020 Census redistricting file (P.L. 94-171, tables P1–P4), plus the DHC for more detail. ACS 5-year gives tract and block-group estimates between census years. [Census: 2020 redistricting data](https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html)
- **Urban/rural**: the 2020 urban area delineation classifies every census block as urban or rural, and DHC table P2 gives urban/rural population by block. [Census: urban and rural](https://www.census.gov/programs-surveys/geography/guidance/geo-areas/urban-rural.html)
- **Current totals**: Vintage 2025 estimates by state and county. [Census: Vintage 2025 national and state estimates](https://www.census.gov/newsroom/press-kits/2026/national-state-population-estimates.html)

Since the block is the finest unit for both, any state works: tag each address with its block, then draw race and urban/rural from that block's counts.

What does differ is how interesting the race dimension is. Georgia (about a third Black) and North Carolina show the strongest race-by-place clustering. Michigan has strong clustering concentrated in Detroit and Flint. Wisconsin is the least diverse of the top candidates.

### 2. Political affiliation: registration or vote share?

- **No party registration:** Michigan, Wisconsin, Georgia and Virginia (open primaries), and Ohio (a voter's party is set by which primary ballot they last took, not by registration). [NCSL: state primary election types](https://www.ncsl.org/elections-and-campaigns/state-primary-election-types)
- **Party registration:** North Carolina and Arizona. They're less useful than they sound:
  - North Carolina, start of 2026: unaffiliated 39%, Democrats 30%, Republicans 30% (2.96M / 2.31M / 2.31M at end of 2025). Many older rural registered Democrats vote Republican, so registration and vote diverge by place. [NCSBE voter registration statistics](https://www.ncsbe.gov/results-data/voter-registration-data) (figures as reported by [Carolina Journal](https://www.carolinajournal.com/new-voters-continue-to-register-as-unaffiliated/), from NCSBE data)
  - Arizona reports D / R / Libertarian / Green / No Labels / Other, and "Other" is about a third of voters. [AZ SOS voter registration statistics](https://azsos.gov/elections/election-information/voter-registration-statistics)

**Conclusion:** Use precinct presidential vote share for every candidate. It gives a clean two-way split that matches what polls ask, it exists in every state, and it keeps the method the same whichever state is chosen. Registration only adds a large "unaffiliated" bucket that polls don't report as a result.

**Precinct results:** MIT Election Data + Science Lab publishes official 2024 precinct returns for every state. [MEDSL/2024-elections-official](https://github.com/MEDSL/2024-elections-official); Dataverse: [2024 precincts](https://dataverse.harvard.edu/dataverse/2024_precincts). Checking the per-state files:

- Michigan (by city/township ward and precinct), Wisconsin (reporting units) and Georgia list every presidential vote under a real precinct.
- North Carolina puts 1.9% of votes in county-wide `ABSENTEE` / `ABSENTEE BY MAIL` / `PROVISIONAL` rows. Virginia puts about 2.6% in county-wide provisional rows. Neither can be placed on a map.

**Precinct boundaries** are needed to map votes onto addresses:

- Michigan: the state publishes [2024 Voting Precincts](https://gis-michigan.opendata.arcgis.com/datasets/Michigan::2024-voting-precincts) (also at the [state REST service](https://gisagocss.state.mi.us/arcgis/rest/services/OpenData/boundaries/MapServer/9)).
- Wisconsin: the Legislative Technology Services Bureau publishes [2024 Election Data with 2025 Wards](https://gis-ltsb.hub.arcgis.com/datasets/2024-election-data-with-2025-wards), with results already joined to ward polygons. LTSB splits reporting-unit totals across wards by population, so ward-level numbers are partly modelled.
- Georgia: [Legislative and Congressional Reapportionment Office](https://www.legis.ga.gov/joint-office/reapportionment) shapefiles plus [SOS precinct results](https://sos.ga.gov/page/georgia-election-results). This needs more joining work.
- A fallback for every state is county-level results (83 counties in MI, 72 in WI, 159 in GA), which already show strong urban/rural clustering.

### 3. Address coverage (OpenAddresses + NAD)

From the OpenAddresses source definitions ([openaddresses/openaddresses `sources/us/`](https://github.com/openaddresses/openaddresses/tree/master/sources/us), master as of 2026-09-27):

| State | Source files with an address layer | Statewide layer | Notes |
|---|---|---|---|
| Michigan | 39 | `mi/statewide.json`: state "SiteStructurePoints" geodatabase, uploaded 2026-02-15 | Structure points, with a number, street, unit, municipality and ZIP for each. Plus 31 county files. |
| Wisconsin | 76 | `wi/statewide.json`: [Wisconsin State Cartographer's statewide parcels](https://www.sco.wisc.edu/parcels/data/) | Parcel site addresses, so there are likely few unit-level rows for apartments. Plus 72 county files. |
| Georgia | 133 | **none** | 124 of 159 counties named. The rest depends on NAD. |
| North Carolina | 113 | `nc/statewide.json`: AddressNC, 2024-07-03 | Plus 101 county files. |
| Arizona | 17 | `az/statewide.json` | 10 counties with their own files. |
| Ohio | 21 | `oh/statewide.json`: statewide LBRS address points | |

**NAD:** I couldn't check the current USDOT participation list: transportation.gov and data.transportation.gov were unreachable from this environment. What I could confirm:

- The NAD takes data from volunteer state and local partners, "more than 30" of them, and it has fully participating, partial and non-participating states. [USDOT NAD](https://www.transportation.gov/gis/national-address-database); [NAD disclaimer](https://www.transportation.gov/mission/open/gis/national-address-database/national-address-database-nad-disclaimer)
- Arizona submits its statewide aggregate to NAD. [AGIC NAD partnership](https://publicsafetycommittee.azgeo.az.gov/pages/national-address-database-nad)
- Wisconsin data was being added as of a 2019 FGDC update. [FGDC NGAC 2019 NAD update](https://fgdc.gov/ngac/meetings/june-2019/national-address-database-update-lewis-cackowski.pdf)

For Michigan, Wisconsin, North Carolina, Arizona and Ohio, the OpenAddresses statewide file alone should cover the state, so NAD is only needed for Georgia.

block-addresses itself merges these sources and dedupes them (see its README). None of the five top candidates is one of the states it lists as NAD-only (TX, TN, VA, WV, SC).

### 4. Political balance

2024 margins (MEDSL): WI R +0.86, MI R +1.41, GA R +2.19, NC R +3.21, MN D +4.24, AZ R +5.53, VA D +5.77, OH R +11.21.

A split near 50/50 is best for the explainer: a poll of 1,200 has a margin of error of about ±3 points, so in Michigan or Wisconsin the reader sees polls land on both sides of the true split. That makes "the poll is close to the truth, not exactly right" something the reader can see. In Ohio every poll would show the same winner.

## Caveats

- **Address coverage is unmeasured.** Before committing, run `scripts/compact.py mi` (and `wi`) in block-addresses and compare the address count with 2020 Census housing units for the state and by county. Wisconsin's parcel-based source is the most likely to undercount multi-unit housing, which would under-represent dense, Democratic, more diverse areas.
- **Residents are not voters.** Vote share describes voters. Children, non-citizens and non-voters live at addresses too. The build has to decide whether every resident gets an affiliation drawn from the precinct's two-party share, or whether a "doesn't vote" category exists. This is a modelling decision for a later ticket, not a reason to prefer one state.
- **Michigan precinct names** use `JURISDICTION <n> Ward <w>` keys. Joining the MEDSL rows to the state polygons needs a key-matching step, and some small townships may be combined. Wisconsin's LTSB ward numbers are partly modelled (disaggregated by population).
- **Couldn't reach from this environment:** census.gov, transportation.gov, Harvard Dataverse and state election sites were blocked. Figures from those sources come from search-result excerpts and the well-known 2020 Census counts. The election figures were computed directly from MEDSL's GitHub files, and the address-source facts come from the OpenAddresses repo.

## Sources

- MIT Election Data + Science Lab, 2024 official precinct returns: https://github.com/MEDSL/2024-elections-official (Dataverse: https://dataverse.harvard.edu/dataverse/2024_precincts)
- 2020 county presidential results used for 2020 margins (compiled from official county returns): https://github.com/tonmcg/US_County_Level_Election_Results_08-24
- OpenAddresses US source definitions: https://github.com/openaddresses/openaddresses/tree/master/sources/us
- USDOT National Address Database: https://www.transportation.gov/gis/national-address-database
- Census 2020 redistricting data (P.L. 94-171): https://www.census.gov/programs-surveys/decennial-census/about/rdo/summary-files.html
- Census urban and rural classification: https://www.census.gov/programs-surveys/geography/guidance/geo-areas/urban-rural.html
- Census Vintage 2025 state estimates: https://www.census.gov/newsroom/press-kits/2026/national-state-population-estimates.html
- NCSL state primary types: https://www.ncsl.org/elections-and-campaigns/state-primary-election-types
- Michigan 2024 Voting Precincts: https://gis-michigan.opendata.arcgis.com/datasets/Michigan::2024-voting-precincts
- Wisconsin LTSB 2024 election data by ward: https://gis-ltsb.hub.arcgis.com/datasets/2024-election-data-with-2025-wards
- Georgia SOS election results: https://sos.ga.gov/page/georgia-election-results
- Georgia Reapportionment Office: https://www.legis.ga.gov/joint-office/reapportionment
- NCSBE voter registration data: https://www.ncsbe.gov/results-data/voter-registration-data
- Arizona SOS voter registration statistics: https://azsos.gov/elections/election-information/voter-registration-statistics
- AGIC (Arizona) NAD partnership: https://publicsafetycommittee.azgeo.az.gov/pages/national-address-database-nad
- block-addresses README (coverage, sources, NAD-only states): https://github.com/shivan2418/block-addresses
