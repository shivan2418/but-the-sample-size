# Vote choice from registration and race in North Carolina

Research for the ticket "Vote choice from registration and race in North Carolina". Context: [ADR 0001](../docs/adr/0001-north-carolina-voter-records-invented-names.md). Each resident takes party registration, race and precinct from a real NC voter record. Only **vote choice** (Harris / Trump / other / wouldn't vote) is modeled.

Researched 2026-09-27. The NCSBE public-data bucket (`s3.amazonaws.com/dl.ncsbe.gov`) was reachable, so every NCSBE figure below was **computed here from the raw files**. The proxy blocked ncsbe.gov, Harvard Dataverse, cces.gov.harvard.edu, apnorc.org, cnn.com, catalist.us, pewresearch.org and ncleg.gov. Claims about those sources come from **search snippets only** and are marked *(snippet)*.

## TL;DR

- **Turnout can be real, not modeled.** The NCSBE vote-history file says who voted in the 2024 general election, and how. It joins to the voter record by `ncid`, and it records the voter's precinct and party *at the time of the election*. For every registered resident, "wouldn't vote" is therefore a fact. For unregistered (synthesized) residents it is true by definition.
- **The early-vote problem is already solved by NCSBE.** `results_pct_20241105` puts 1.78M votes (31%) in county-level pseudo-precincts such as "EARLY VOTING" and "ABSENTEE". NCSBE also publishes `results_precinct_sort/`, which assigns early and mail votes to the voter's home precinct. It leaves only 2,224 votes (0.04%) unassigned, and its 2,658 precinct codes match the vote-history precinct codes exactly.
- **Precinct boundaries don't matter.** Calibration is done on the precinct *label* each voter had on 2024-11-05, taken from the vote-history record. No shapefiles and no crosswalk are needed.
- **A survey prior is still needed.** An ecological regression that uses only precinct results and composition puts cells at 0% or 100% (for example "white registered Democrats 100% Harris"). That is implausible, and it would show up in any poll crosstab the reader sees. **CES 2024** is the one open survey that carries *registered party from the voter file* (`TS_partyreg`), which is the attribute our residents have. AP VoteCast and the exit polls only have self-reported party ID. CES is the one to keep; VoteCast can be dropped.
- **Model:** take a prior P(choice | party × race) from CES among validated 2024 voters (NC, pooled with the South for small cells). Then apply IPF / raking per precinct, so the simulated Harris / Trump / other counts among that precinct's real voters equal its real result. Finally assign choices by controlled rounding, so totals match exactly.

## 1. Data sources

| Source | What it gives | Size | Access / terms |
|---|---|---|---|
| **NCSBE vote history** `ncvhis_Statewide.zip` — <https://s3.amazonaws.com/dl.ncsbe.gov/data/ncvhis_Statewide.zip>, layout <https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvhis.txt> | One row per voter per election (last 10 years). Columns: `ncid`, `election_lbl`, `voting_method`, `voted_party_cd` (party at time of voting), `pct_label` (precinct at time of election), `vtd_label` | 351 MB zip / 5.8 GB text (snapshot of 2026-09-20). Per-county `ncvhis{N}.zip` files also exist | Public record. The bucket's [ReadMe](https://s3.amazonaws.com/dl.ncsbe.gov/data/ReadMe_PUBLIC_DATA.txt) cites G.S. §132-1 and §163-82.10 |
| **NCSBE voter snapshot on election day** `VR_Snapshot_20241105.zip` — <https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/VR_Snapshot_20241105.zip>, layout <https://s3.amazonaws.com/dl.ncsbe.gov/data/Snapshots/layout_VR_Snapshot.txt> | Voter registration (address, party, race, ethnicity, age, precinct, `confidential_ind`, `cancellation_dt`) as of 2024-11-05. UTF-16 LE | 1.29 GB zip | Public record |
| **NCSBE aggregates** `voter_stats_20241105.zip`, `history_stats_20241105.zip` — <https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/> | Counts of registered voters (voter_stats) and of 2024 voters by method (history_stats), per precinct × party × race × ethnicity × sex × age band | 6.5 MB and 4.7 MB zipped | Public record |
| **Precinct results, home-precinct sort** — <https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/results_precinct_sort/STATEWIDE_PRECINCT_SORT.txt> (and per county) | Votes per contest × precinct × candidate × method, with early and mail votes assigned to the voter's home precinct | 412 MB (statewide, all contests; president only is about 148k rows) | Public record |
| Precinct results, as reported — <https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/results_pct_20241105.zip> | Same data with a `Real Precinct` Y/N flag. Early and mail votes sit in county pseudo-precincts | 3.7 MB | Public record. Matches the certified totals (Trump 2,898,423; Harris 2,715,375) |
| **CES 2024 Common Content** — doi:10.7910/DVN/X11EP6 | About 60k adults *(snippet)*. Includes the TargetSmart match: `TS_partyreg` (registered party from the file) *(snippet, cumulative guide)* and validated 2024 turnout, plus self-reported race and vote | Tens of MB (CSV / .dta) | Free with a Dataverse login *(snippet)*. License not verified (CES Dataverse sets are usually CC0; **check**) |
| AP VoteCast 2024 PUF — <https://apnorc.org/projects/ap-votecast-puf/> | 139,938 registered voters in all states *(snippet)*. Self-reported party ID, not registration | — | Free download *(snippet)*. Terms not verified |
| CNN / NEP exit poll NC — <https://www.cnn.com/election/2024/exit-polls/north-carolina/general/president/0> | 3,773 NC voters *(snippet)*. Race, party ID and area-type crosstabs, published only as tables | — | Toplines only; not open microdata |
| Pew validated voters — <https://www.pewresearch.org/politics/2025/06/26/validated-voters-2024-methodology/> | 8,942 adults, 7,100 matched *(snippet)*. National only, so NC n is around 250 | — | Useful as a national sanity check only |
| Catalist What Happened 2024 — <https://catalist.us/whathappened2024/> | Modeled; publishes only a "Southeast battleground" (GA+NC) aggregate *(snippet)* | — | Proprietary microdata; not usable |

**CES NC subsample size: not verified** (Dataverse blocked). A proportional estimate from NC's ~3.2% share of US adults is about 1,900 respondents, of whom roughly 1,200 are validated 2024 voters. Before relying on NC-only cells, count `inputstate == 37` with `TS_g2024` voted. Small cells such as Black Republicans (22.6k real voters statewide), Hispanic voters of any party, and Libertarian or other-party voters will have too few NC respondents. For those, pool with the South (or nationally) and include a state term.

### Turnout by registration × race, 2024 general, computed from NCSBE aggregates

`history_stats` / `voter_stats`: 5,705,861 voters out of 7,854,464 registered (72.6%). Voters are counted by `voted_party_cd`. Registered voters are counted by the snapshot's party (active + inactive). The denominator omits same-day registrants, so these rates are overstated by at most a few tenths of a point.

| Party | Registered | Turnout | White | Black | Hispanic | Asian | Other/undesignated |
|---|---|---|---|---|---|---|---|
| DEM | 2,457,532 | 73.2% | 80% | 71% | 60% | 68% | 65% |
| REP | 2,350,382 | 79.9% | 82% | 52% | 64% | 72% | 73% |
| UNA | 2,965,094 | 66.9% | 74% | 54% | 51% | 67% | 52% |
| LIB | 49,940 | 57.0% | 60% | 46% | 47% | 51% | 53% |
| Other parties (GRE, NLB, JFA, CST, WTP) | 31,516 | ~62–81% | | | | | |

Method mix (history_stats): early in person 4,029,071; early curbside 185,711; election day 1,142,368; mail 298,076; provisional 17,149; curbside 18,215; transfer 15,271.

## 2. Turnout from the vote-history file: yes, it can be real

- **Coverage.** The current ncvhis file has 5,722,843 rows with `election_lbl = 11/05/2024` (5,722,765 unique `ncid`; 78 duplicates). Of these, 5,721,500 (99.98%) join to a record in the current voter file. The file keeps removed voters for 10 years ([layout](https://s3.amazonaws.com/dl.ncsbe.gov/data/layout_ncvoter.txt)). Ballot counts per precinct agree with the precinct-sort results: median gap +0.3%, 5th–95th percentile −0.9% to +2.9%, across precincts with more than 200 voters.
- **Use the 2024-11-05 snapshot, not the current file, as the resident base.** Joining 2024 voters to the *current* (2026-09) file shows that since 2024:
  - 4.1% have changed party (231,786);
  - 14.4% have a different precinct label (823,358), from moving or re-precincting;
  - 135,950 have been removed and 157,446 are now inactive.

  The current file also includes people who registered after the election, who would all look like "wouldn't vote". The Nov 2024 snapshot, joined to ncvhis for 2024, gives a consistent 2024 population: party, race and precinct as they stood, with real turnout. `voted_party_cd` and `pct_label` in ncvhis are the party and precinct at the time of voting, so voters stay consistent even if the current file is used.
- **Restrictions.** Voter registration records are public in NC except for SSN, date of birth, driver's licence number, the agency where the voter registered, and the email of a military / overseas voter. Addresses of voters under protective orders or in the Address Confidentiality Program are confidential (G.S. §163-82.10 *(snippet — ncleg.gov blocked)*). NCSBE publishes vote history as public data under the same statutes ([ReadMe](https://s3.amazonaws.com/dl.ncsbe.gov/data/ReadMe_PUBLIC_DATA.txt), primary). No statutory ban on republishing was found (same caveat as the ADR: re-check). Consequences for the ADR:
  - The "real" attributes shown at an address now include *whether that household member voted in 2024, and how*.
  - This is public information, but it is a new category of real fact, and the ADR should say so.
  - Keep excluding `confidential_ind = Y` (265 of the 2024 voters).
  - Never publish `ncid` or `voter_reg_num`.
  - Voting method (early / mail / election day) need not be shown at all.
  - Keep "Resident: vote choice is always modeled" true: turnout becomes known, and only the candidate choice stays modeled.

## 3. Calibrating to each precinct's real result

**Pseudo-precincts.** In `results_pct_20241105`, 250 pseudo-precincts ("EARLY VOTING …", "ABSENTEE", "PROVISIONAL", "TRANSFER") hold 1,775,402 presidential votes. That is 31% of the statewide total and 70–86% in Wake, Durham, Orange, Guilford, Pitt and others; 34 of 100 counties have more than 5% there. **`results_precinct_sort` fixes this.** In it:

- all 2,658 real precincts carry their early, mail and provisional votes;
- only 54 pseudo rows with votes remain, holding 2,224 votes (for example Halifax "EV SCOTLAND NECK", 306);
- every precinct code with votes matches a `pct_label` in the vote history.

The precinct-sort file differs from the certified county totals by about 900 votes, mostly in Bladen (+448 Harris / +427 Trump in `results_pct`). Handle both gaps with a final county-level rake to the `results_pct` county totals.

**Boundary changes.** None to handle. Every 2024 voter carries the `pct_label` of their 2024 precinct, which is the key the results use. Geography only matters for placing a dot at an address, and the snapshot address already does that.

**Procedure** (tested here on the real files for feasibility):

1. For each precinct *p*, count the real 2024 voters *n_pc* in each cell *c* = party × race (four race groups: White / Black / Hispanic / other), using ncvhis joined to the snapshot, or `history_stats` for the counts alone.
2. Prior π_c(k) for *k* ∈ {Harris, Trump, other}: from CES validated 2024 voters, keyed on `TS_partyreg` × race. Add an urban/rural term to the prior only if CES shows it matters within a cell. The per-precinct step below absorbs most geographic variation.
3. **IPF per precinct** on the table (cells × choices):
   - seed: *n_pc · π_c(k)*;
   - row margins: *n_pc*;
   - column margins: the precinct's Harris / Trump / other shares × its voter count.

   This is equivalent to one log-odds shift per choice per precinct, applied to every cell. With a crude statewide prior it converged in a median of 14 iterations. The implied Harris-vs-Trump log-odds shift had a median of |0.27| (90th percentile 0.67).
4. Assign each real voter a choice by sampling within cell and precinct, with controlled (integer) rounding, so each precinct's simulated totals equal its real counts exactly. Non-voters and synthesized unregistered residents get "wouldn't vote".
5. Decide where undervotes and overvotes (about 31k blank presidential ballots) go: fold them into "other", or treat them as voters with no choice.

**Why a survey prior (evidence).** A Goodman-style constrained regression of precinct Harris and Trump counts on the 16 cell counts, with no survey, hits the bounds:

- DEM-White 100% Harris
- REP-Black and REP-Hispanic 100% Trump
- UNA-Black and UNA-Hispanic 100% Harris

It still misses precinct Harris share by a median of 5.5 points (90th percentile 12.5). Raking would fix the totals, but the within-precinct crosstabs a simulated poll displays would be absurd.

## 4. Is CES still needed?

Yes, but only as the prior, and it is the *only* survey needed.

- Vote history plus precinct results fix turnout and each precinct's totals exactly.
- What they cannot identify is how a precinct's votes split across its registration × race cells, and that is exactly what a poll crosstab shows the reader.
- VoteCast's larger NC sample doesn't help, because its party variable is self-identification. NC's registration and self-ID differ a lot: for example, conservative registered Democrats in the east, and 2.97M unaffiliated registrants.
- Exit polls and Pew are tables or national-only. Catalist is proprietary.
- The one gap left open is the NC-specific CES cell sizes; pooling with the South covers the small cells.

## 5. Recommendation: minimal data set and model

1. `VR_Snapshot_20241105.zip` (1.29 GB). Residents on the voter file: address, party, race, age, 2024 precinct. Drop `confidential_ind = Y` and records cancelled before 2024-11-05.
2. `ncvhis_Statewide.zip` (351 MB), filtered to `election_lbl = 11/05/2024`. This gives real turnout; join on `ncid`.
3. `results_precinct_sort/STATEWIDE_PRECINCT_SORT.txt` filtered to `US PRESIDENT` (412 MB raw → about 10 MB). Precinct targets.
4. `results_pct_20241105.zip` (3.7 MB). Certified county and state totals for the final rake.
5. CES 2024 Common Content (Harvard Dataverse, login; confirm the license). One small table: P(Harris / Trump / other | `TS_partyreg` × race) among validated 2024 voters, NC pooled with the South. Commit only the derived table, not the microdata.

The four NCSBE files are public records with no license terms. `voter_stats` and `history_stats` (about 11 MB together) can stand in for files 1 and 2 when checking or prototyping the calibration on counts, before joining individual records.

**Model:** turnout comes from the records; the choice among voters is the CES prior raked per precinct (IPF, then integer assignment); every non-voter, and every synthesized resident, is "wouldn't vote". The population's true split among voters then equals the real result in every precinct, every county and the state. The only modeled quantity left is which voter in a precinct cell picked whom.

Open checks:

- CES NC n per cell.
- CES license.
- VoteCast PUF terms (only if a second opinion on the prior is wanted).
- G.S. §163-82.10 text, from ncleg.gov directly.
