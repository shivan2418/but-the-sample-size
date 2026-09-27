# Vote choice by race and urban/rural setting: data sources and method

Research for issue #4, "Real data on vote choice by race and urban/rural".

**Question.** Where can we get real, public data on how vote choice varies *jointly* by race and urban/rural setting, ideally at state level? We need it so each synthetic **resident** in the simulated state can be given an affiliation that depends on their race and place, while the **population** still adds up to the real county and state results.

**Short answer.** Use the **Cooperative Election Study (CES) 2024 Common Content** as the source of race × urbanicity vote rates. It has about 60,000 respondents, a validated-turnout flag, self-reported race, a county FIPS code, and a self-reported city/suburb/town/rural item. Then **calibrate to real county results** from the MIT Election Lab (CC0) with a per-county logit shift, or with a three-way IPF if we want the statewide race × urbanicity rates to hold exactly. Treat non-voters as their own category, with turnout rates also taken from CES and calibrated to real county ballot totals. AP VoteCast, Pew validated voters and exit polls work as cross-checks, not as inputs. For North Carolina (and Georgia to a lesser degree), public voter-file aggregates give *actual* turnout by race by precinct, which makes that state much stronger if we pick it.

> **Note on sourcing.** The research sandbox blocked direct fetches of cces.gov.harvard.edu, dataverse.harvard.edu, pewresearch.org, apnorc.org, norc.org, icpsr.umich.edu, census.gov and arxiv.org. Claims about those sites come from their own pages as surfaced by web search (URLs cited), and from primary files mirrored on GitHub (the CES cumulative-file guide source, MEDSL repos, and Kuriwaki's R packages), which could be read directly. Before building, open the flagged items (marked *verify*) at the source.

---

## 1. Candidates compared

| Source | Years | Geography | Race × urbanicity jointly? | Sample | Turnout basis | Reuse terms | Verdict |
|---|---|---|---|---|---|---|---|
| **CES Common Content** | Every year since 2006; presidential years 2008–2024 | Respondent's state, county FIPS, ZIP | **Yes, from microdata.** `race`/`race_h` × `urbancity` (self-report) *or* × a county-derived urbanicity code | ~60,000 nationally in 2024; roughly 1,000–2,300 per state for the candidate states (estimate) | Validated against voter files (TargetSmart since 2022) | Public download from Harvard Dataverse; cite. License shown on the Dataverse page (*verify*: likely CC0 or Dataverse standard terms) | **Recommended input** |
| **Pew validated voters (ATP)** | 2016, 2018, 2020, 2022, 2024 | National only in practice | Microdata allow it, but cells get tiny | 8,942 citizens, 7,100 validated voters (2024) | Validated against 3 voter-file vendors | ATP microdata downloadable after registration under Pew terms | National benchmark only |
| **AP VoteCast** | 2018–2024 | All 50 states | Published state crosstabs include race and community type; joint cells only in microdata | 139,938 registered voters in 2024, all states | Self-reported, weighted to results | Microdata via ICPSR (2018–2022 listed) under ICPSR terms; published tables are AP's | Best state-level **cross-check** |
| **Edison / NEP exit polls** | 1970s–2024 | National plus a subset of states | Crosstabs only; joint cells need Roper microdata | Varies; smaller per state | Voters only, self-reported, weighted to results | Roper Center membership; no redistribution | Not recommended |
| **Ecological inference (EI) / MRP papers** | Mostly 2016–2020 | Congressional district, precinct | Race yes; urbanicity only implicitly through geography | Uses all precincts | Precinct results plus Census or voter file | Academic; replication code MIT | Method reference, not a drop-in table |
| **Catalist "What Happened"** | 2016–2024 | National / regional | Published toplines by race and by urbanicity; some regional joint notes | Voter file (~all voters), modelled | Voter file | Proprietary; only the published report | Cross-check only |
| **State voter files with race (NC, GA, and others)** | Current | Precinct / individual | Race × precinct turnout is *observed*, not modelled | Every registrant | Actual vote history | NC is free; GA is sold by the SoS | Big upgrade **if** NC or GA is chosen |

### 1.1 Cooperative Election Study (CES), formerly CCES

- **What it is.** A national online survey run by YouGov before and after each November election. The 2024 Common Content has "data from 60,000 American adults interviewed before & after the election" and is distributed on Harvard Dataverse at doi:10.7910/DVN/X11EP6. Current PIs are Schaffner, Ansolabehere, Pope and Shih. ([Dataverse 2024](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi%3A10.7910%2FDVN%2FX11EP6); [Schaffner announcement](https://x.com/b_schaffner/status/1907487141946442190); [CES home](https://cces.gov.harvard.edu/)). The 2020 and 2022 files are about 61,000 and 60,000 respondents ([2022 Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/PR4L8P), [2020 Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/E9N6PH)).
- **Race.** `race` plus `hispanic`. The cumulative file adds `race_h`, which codes anyone "any-part Hispanic" as Hispanic, so that "White" means non-Hispanic White. That is the coding to match against Census race/ethnicity tables ([cumulative guide source](https://github.com/kuriwaki/cces_cumulative/blob/master/guide/guide_cumulative_2006-2025.qmd), §race_h).
- **Urbanicity.** Two routes:
  1. `urbancity`, "How would you describe the place where you live?", with the options City / Suburb / Town / Rural area / Other. It appears in the annual Common Content files (the 2018 and 2020 codebooks show it: [example codebook](https://github.com/soodoku/partisan_vision/blob/main/data/cces/CCES20_UCM_OUTPUT_codebook.txt)), but it is **not** in the cumulative file, so use the 2024 annual file.
  2. `county_fips` and `zipcode` (both in the annual and cumulative files; [cumulative guide](https://github.com/kuriwaki/cces_cumulative/blob/master/guide/guide_cumulative_2006-2025.qmd) §geography). These let us apply **the same objective urban/rural definition we use for residents** (for example USDA Rural-Urban Continuum Codes for counties, or ZIP-level Census urban share) to the survey respondents. **Prefer this route.** A resident's "urban/rural" comes from their address, not a self-description, so the survey rates must be keyed on the same definition. CES data do not include respondents' exact addresses, so the county (or ZIP) is the finest shared key.
- **Turnout and vote choice.** Even years include validated turnout (`vv_turnout_gvm` in the cumulative file). YouGov matches respondents to voter files, and "starting in 2018, YouGov computed weights after vote validation and weighted to the target population of validated registered voters" (`vvweight`). CES switched vote-match vendor from Catalist to TargetSmart in 2022, and 2024 validation variables are now in the cumulative file (V12) ([cumulative guide](https://github.com/kuriwaki/cces_cumulative/blob/master/guide/guide_cumulative_2006-2025.qmd) §Validated Turnout, changelog). Presidential vote choice comes from the post-election wave.
- **Per-state sample (estimate).** CES is stratified to be representative within states: its "poststratification weights … render state subsamples representative of each state" ([Kuriwaki et al. 2024](https://cces.gov.harvard.edu/sites/g/files/omnuum8901/files/Kuriwaki-et-al_racially-polarized-voting-MRP.pdf)). At about 60,000 adults and population-proportional allocation, expected state *n* is roughly: PA ≈ 2,300, OH ≈ 2,100, GA ≈ 1,900, NC ≈ 1,900, MI ≈ 1,800, AZ ≈ 1,300, WI ≈ 1,050. About 60–65% of those are validated 2024 voters. *Verify with the actual file.* That is enough for the big cells (White urban/suburban/rural, Black urban) but not for small ones (for example rural Black in Wisconsin, rural Asian anywhere). Smooth small cells with partial pooling (§3.2).
- **Why it fits.** It is the only free, large, validated-turnout source whose microdata carry race, a geographic identifier fine enough to classify urbanicity the same way as our residents, and state. The method in §3 is how the CES team itself calibrates CES to election results (Kuriwaki et al. 2024, below).
- **Reuse.** Public download from Dataverse with a citation. We would publish only *derived aggregate rates* (a handful of numbers per cell), not microdata, which is comfortably within normal academic-data terms. *Verify the exact licence on the 2024 Dataverse page before shipping.*

### 1.2 Pew Research Center validated voters

- **2024 study.** "Out of 8,942 voting-age citizens, 8,410 (94%) were matched to at least one of three voter files; 7,100 are considered validated voters", plus 1,842 validated non-voters. The three vendors are one Republican-aligned, one Democratic-aligned and one nonpartisan. Post-election survey on the American Trends Panel, Nov 12–17, 2024 ([Pew methodology](https://www.pewresearch.org/politics/2025/06/26/validated-voters-2024-methodology/)).
- **Urbanicity is self-described** ("describe their communities as rural"). Rural validated voters were 69% Trump and 29% Harris; urban voters were about 65–33 Harris ([Pew report](https://www.pewresearch.org/politics/2025/06/26/behind-trumps-2024-victory-a-more-racially-and-ethnically-diverse-voter-coalition/), [voting patterns](https://www.pewresearch.org/politics/2025/06/26/voting-patterns-in-the-2024-election/)).
- **Limitations for us.** It is national only. About 7,100 voters spread over 50 states gives a few hundred per candidate state, too few for race × urbanicity cells. Its value is as the highest-quality **national benchmark** for race and urbanicity gaps, including non-voters, to sanity-check our CES-derived numbers. Pew also offers ATP microdata after registration, under its own terms.

### 1.3 AP VoteCast (NORC)

- **2024.** 139,938 registered voters in all 50 states, interviewed Oct 28 – Nov 5, 2024 (4,767 by phone, 135,171 on the web). About 121,000 were voters and about 19,000 registered non-voters. It mixes a random sample from state voter files, NORC's probability-based AmeriSpeak panel, and nonprobability online panels. The sample is stratified by state, race/ethnicity, modelled partisanship and response propensity ([AP-NORC methodology PDF](https://apnorc.org/wp-content/uploads/2025/03/Methodology_2024-FINAL.pdf); [AP VoteCast 2024 project](https://apnorc.org/projects/ap-votecast-2024-general-election/); [NORC](https://www.norc.org/research/projects/ap-votecast.html)).
- **Granularity.** AP's published results give state-level crosstabs for all 50 states, including race and community type (urban / suburban / small town / rural; *verify the exact 2024 question wording in the questionnaire*). The *joint* race × community cells need microdata. ICPSR lists the AP VoteCast series with 2018–2022 studies ([ICPSR series 2380](https://www.icpsr.umich.edu/web/ICPSR/series/2380); [2022 study 38835](https://www.icpsr.umich.edu/web/ICPSR/studies/38835)); an [AP VoteCast Public Use Files](https://apnorc.org/projects/ap-votecast-puf/) page also exists. Whether the 2024 general-election file is released yet: *verify*.
- **Caveats.** Much of the sample is nonprobability, turnout is self-reported (not validated), and the estimates are weighted toward the known result. Access and redistribution are governed by ICPSR and AP terms, which are more restrictive than CES.
- **Use.** The best **state-specific cross-check** for the chosen state. Compare our calibrated race × urbanicity rates with AP's published state crosstabs by race and by community type.

### 1.4 Edison Research / National Election Pool exit polls

- Conducted by Edison Research for the NEP (ABC, CBS, CNN, NBC) ([Edison FAQ](https://www.edisonresearch.com/exit-poll-faqs/)). Microdata for past national and state exit polls are archived at the Roper Center and available to member institutions ([Roper exit polls](https://ropercenter.cornell.edu/polls/us-elections/exit-polls/)).
- **Not recommended.** It covers voters only and self-reported vote. State exits cover only some states. Access needs a Roper membership, whose terms bar redistribution. Pew's validated-voter work exists largely because exit-poll demographics are contested. Published crosstabs (TV network sites) give race and urban/suburban/rural separately, rarely jointly.

### 1.5 Ecological inference and calibrated-MRP literature

- **Kuriwaki, Ansolabehere, Dagonel and Yamauchi (2024), "The Geography of Racially Polarized Voting: Calibrating Surveys at the District Level", *APSR* 118(2): 922–939.** They estimate vote by race in every congressional district by fitting MRP to CES and then *calibrating* to district presidential results and to Census composition of adult citizens. Key finding: national race differences explain about 60% of district-level variation and geography about 30%. Black voters are uniformly Democratic, while White and Hispanic preferences vary a lot by place ([paper PDF on CES site](https://cces.gov.harvard.edu/sites/g/files/omnuum8901/files/Kuriwaki-et-al_racially-polarized-voting-MRP.pdf); [Cambridge](https://www.cambridge.org/core/journals/american-political-science-review/article/geography-of-racially-polarized-voting-calibrating-surveys-at-the-district-level/6BEF8C3000B763699C27A4F9E8590516)). This is essentially our problem one level up. It supports letting White and Hispanic rates vary by place (the county logit shift does this), while Black rates barely move.
  - Tooling (all MIT licence): [`ccesMRPprep`](https://github.com/kuriwaki/ccesMRPprep) (CES + ACS + MEDSL / Daily Kos results prep), `ccesMRPrun`, and [`synthjoint`](https://github.com/kuriwaki/synthjoint), which estimates joint population tables from margins plus survey microdata (`synth_prod`, `synth_mlogit`, `synth_smoothfix`, `synth_bmlogit`).
  - They caution that the classic one-parameter "logit shift" can distort *gaps between groups* if group estimates are biased in opposite directions ([search summary of the Political Analysis logit-shift paper](https://www.cambridge.org/core/journals/political-analysis/article/abs/recalibration-of-predicted-probabilities-using-the-logit-shift-why-does-it-work-and-when-can-it-be-expected-to-work-well/67B3C222EB34BBA376AD730F34038CA4)). For an explainer this is acceptable. §3.3 gives the IPF variant if we want the statewide gaps pinned.
- **Ghitza and Gelman (2013), "Deep Interactions with MRP", *AJPS* 57(3): 762–776.** The origin of adjusting subgroup turnout and vote estimates after the fact so they sum to actual results ([Wiley](https://onlinelibrary.wiley.com/doi/abs/10.1111/ajps.12004)).
- **Precinct EI (King's EI, EI:R×C via `eiCompare`)** combines precinct results with precinct racial composition, from the Census or from BISG applied to voter files ([eiCompare methods](https://rpvote.github.io/voting-rights/methods/)). It is used in Voting Rights Act litigation and gives race-specific rates by area, but it is fragile where precincts are racially homogeneous. It needs precinct shapes and a crosswalk to Census blocks, and it says nothing about urbanicity directly. That is more machinery than the explainer needs. Worth it only if the chosen state lacks decent CES cells.

### 1.6 Catalist "What Happened" (2024)

- A voter-file-based analysis built from vote history, precinct results, Census data and proprietary models. National toplines: urban 65–33 Harris, suburban 49–49, rural 69–30 Trump. It includes regional composition notes, such as Midwest rural voters being 94% White ([Catalist 2024](https://catalist.us/whathappened2024/)). The data are proprietary; only the published report can be cited. Use it as a cross-check.

### 1.7 State voter files that record race (strong option for NC, and GA)

- **North Carolina.** The State Board of Elections publishes, free, statewide voter registration files (with race and ethnicity codes and residential address) and voter history. It also publishes **group-level counts of who voted in each election by county and precinct, broken down by race, ethnicity, party, sex and age** ([NCSBE voter history data](https://www.ncsbe.gov/results-data/voter-history-data); [NCSBE registration data](https://www.ncsbe.gov/results-data/voter-registration-data)). Turnout by race by precinct is therefore *observed*, and only vote choice by race needs modelling. **Use only the aggregate counts.** Residents must never be real individuals (see CONTEXT.md), so do not ingest named voter records.
- **Georgia** also records self-reported race on registrations; the lists are sold by the Secretary of State ([GA SoS order page](https://sos.ga.gov/page/order-voter-registration-lists-and-files); [Brennan Center on GA race data](https://www.brennancenter.org/our-work/research-reports/accurate-data-georgia-shows-racial-turnout-gap)). The other states in our shortlist (OH, MI, PA, AZ, WI) do not record race, so turnout by race there has to be modelled.

### 1.8 Supporting data (needed whichever source we choose)

- **Real results.** MIT Election Data + Science Lab *County Presidential Election Returns 2000–2024*, doi:10.7910/DVN/VOQCHQ, **CC0 1.0** ([Dataverse](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VOQCHQ)). Precinct-level 2024 returns are in [MEDSL/2024-elections-official](https://github.com/MEDSL/2024-elections-official). Its README warns about fictitious zero-vote rows, double-counted vote-mode splits, and privacy-suppressed counts in some states.
- **Turnout by race by state (cross-check).** Census CPS November 2024 Voting and Registration Supplement, table "Reported Voting and Registration … by Sex, Race and Hispanic Origin, for States" (public domain; [Census P20-590 tables](https://www.census.gov/data/tables/time-series/demo/voting-and-registration/p20-590.html)). CPS turnout is self-reported and runs high.
- **Urbanicity definitions.** USDA ERS Rural-Urban Continuum Codes for counties ([ERS](https://www.ers.usda.gov/data-products/rural-urban-continuum-codes)), or the NCES City / Suburb / Town / Rural locale scheme, which matches CES's four answer options nicely ([NCES locales](https://nces.ed.gov/programs/edge/Geographic/LocaleBoundaries)). Pick one and use it for both residents and CES respondents.

---

## 2. Recommendation

**Use CES 2024 for the seed rates and MEDSL county results for the totals, joined by a county-level logit-shift calibration. Include non-voters as a fourth affiliation category.**

Why:
1. It is the only free source with validated turnout, race, and a place identifier fine enough to apply our own urbanicity definition. That keeps "urban/rural" on a resident (address-based) and in the rates (survey-based) meaning the same thing.
2. It gives state-level samples of about 1,000–2,300 for every candidate state, enough for the main cells with pooling.
3. It is the approach the CES team published for this very problem (Kuriwaki et al. 2024).
4. The build step is a small, deterministic script run offline. Only the resulting per-resident attributes, or per-cell probabilities, ship to GitHub Pages.
5. If North Carolina is chosen, swap the modelled turnout for NCSBE's observed precinct turnout by race. That is the most defensible version on offer.

## 3. Method sketch

Notation: county *c*; cell *k* = race *r* (White / Black / Hispanic / Asian / Other, per `race_h`) × urbanicity *u* (for example urban / suburban / town / rural, derived from the address); choice *j* ∈ {Rep, Dem, Other, Did not vote}.

### 3.1 Build the adult population by cell
From the resident generation step (separate tickets), count voting-age residents per county and cell, **A[c,k]**. Citizenship matters for turnout. Use CVAP (ACS Citizen Voting-Age Population by race) if available at the resident level. Otherwise fold non-citizens into "did not vote".

### 3.2 Seed rates from CES (state-specific, pooled for small cells)
- Filter CES 2024 to the chosen state. Assign each respondent a cell using `race_h` and the urbanicity of their `county_fips` (or ZIP).
- Turnout seed **t[k]** = weighted share with `vv_turnout_gvm` = voted (use the Common Content weight).
- Choice seed **p[k,j]** among validated voters = weighted post-election presidential vote (use `vvweight_post` or its annual-file equivalent).
- For cells with fewer than about 50 respondents, shrink toward the regional or national estimate for the same cell. A simple empirical-Bayes or beta-binomial pull is enough, or `synthjoint::synth_smoothfix` if working in R. Record *n* per cell next to the output.

### 3.3 Calibrate to real county results
**Turnout first.** For each county, find one shift δ_c so that Σ_k A[c,k] · logistic(logit t[k] + δ_c) = real county total ballots for president (MEDSL `totalvotes`). This is one equation in one unknown per county, solved with a few bisection steps. The result is calibrated voters **V[c,k]**, and non-voters A − V.

**Then vote choice**, with either of two options:

- **(A) Logit shift (recommended, simplest).** For each county, find δ_c so that Σ_k V[c,k] · logistic(logit p[k,Rep] + δ_c) matches real Rep votes, and likewise for Dem. Use a multinomial version with one shift per non-baseline choice, or do Rep vs not-Rep and then split the rest Dem/Other using the seed ratio. The results sum *exactly* to every county's real results, keep CES's between-group gaps on the logit scale, and let a county's White rural voters be more Republican than the state average where the county results demand it. That is the geographic variation Kuriwaki et al. found. Caveat: gaps are inherited from CES, not re-estimated.
- **(B) Three-way IPF (raking) on county × cell × choice.** Seed with V[c,k]·p[k,j] and iterate proportional fitting over three two-way margins:
  (i) county × choice = real county results;
  (ii) county × cell = V[c,k];
  (iii) cell × choice = the CES statewide rates p[k,j] × Σ_c V[c,k], rescaled so their choice totals equal the state's real totals.
  The result matches county totals *and* the statewide race × urbanicity rates. Rescale margin (iii) first so all three margins share the same one-way totals. With three two-way margins, IPF can converge slowly or fail to hit all of them exactly if they are mutually inconsistent, so check the residuals. Use this option if the explainer wants to state "in this state, rural White voters split X–Y" and have the simulation reproduce it exactly.

### 3.4 Assign residents
Within each county × cell, give residents choices in proportion to the calibrated rates. Use **exact allocation** (largest-remainder rounding, then a seeded shuffle) rather than independent coin flips, so county totals match to the vote and not just in expectation. Clustering by place comes for free, because both the cell mix and δ_c vary by county. For within-county clustering (precinct level), repeat §3.3 at precinct level with MEDSL precinct returns, if precinct-to-address assignment is available.

### 3.5 Non-voters and turnout
- Presidential turnout among voting-age citizens is typically around 60–66%. A population of all adults with only a Harris/Trump attribute would misstate the **true split** of the population. Options:
  1. **Recommended:** include "Did not vote" (and optionally "Not eligible", for non-citizens) as a category. A poll of residents then honestly includes non-voters, and the explainer can point out that real polls must decide whom to count (likely voters), which is a nice hook.
  2. Restrict the population to 2024 voters. That is simpler, but the resident set no longer equals "people at addresses".
- If a non-voter's leaning is also wanted, CES records party ID (`pid3`) for validated non-voters, so a leaning can be drawn by cell. Pew's 1,842 validated non-voters are a national benchmark for that distribution.

## 4. Key caveats

- **Urbanicity definition mismatch.** Self-described "suburb" (CES `urbancity`, Pew, VoteCast) is not the same as a Census/USDA classification. Key the seed rates on the same objective, geography-based definition applied to residents (via CES county or ZIP). County-level urbanicity is coarse: a big county holds city, suburb and rural land. ZIP gives finer detail if the resident step classifies at ZIP or tract level.
- **Small cells.** Rural Black, rural Asian and urban Native American cells will be thin in any state survey. Pool them and document it.
- **Survey error.** CES is an opt-in panel that is sample-matched and weighted. A 2026 preprint reports persistent non-response bias in CES 2024 ([arXiv 2606.12889](https://arxiv.org/pdf/2606.12889), not read in full). Calibrating to real results removes level bias but not all gap bias.
- **"Real" is modelled.** Nobody observes vote choice by race; every source here is an estimate. The explainer copy should say "drawn from survey estimates, then adjusted to match real results", and never "the real split by race".
- **Residents must stay synthetic.** Even where voter files with race and addresses exist (NC, GA), use only aggregate counts.
- **Reuse.** CES aggregates and MEDSL (CC0) are safe to publish as derived numbers. Do not ship AP VoteCast, Roper, or Pew microdata or large extracts. Cite everything in the page's sources.
- **Items to verify at source before building:** the CES 2024 Dataverse licence text; the 2024 `urbancity`, `countyfips` and TargetSmart validation variable names in the annual codebook; actual per-state *n*; AP VoteCast 2024 community-type question wording and ICPSR release status.
