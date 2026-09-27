---
status: accepted
---

# North Carolina voter records at real addresses, under invented names

The state rung simulates North Carolina, not Michigan (the earlier choice). Each resident takes party registration, race, age and whether they voted in 2024 from a real NC voter record at that real address, under an invented name; only their vote choice among those who voted is modeled. NC's voter file is a free, open download that carries party and race; Michigan's has neither, so every attribute there would have been invented. Names stay invented: showing a real person next to a modeled vote risks a false-light claim and invites harassment, and using real names wouldn't simplify the build anyway.

## Considered Options

- **Michigan, fully synthetic residents** (the earlier choice): competitive and the right size, but party and race have to be modeled from survey data.
- **Real names from the voter file:** rejected. Vote choice would still be invented, so it would be pinned on real people; the file covers only registered voters (~7M of 11M); precedent sites (VoteRef, the Prop 8 donor map) drew harassment and lawsuits.
- **New York:** bans non-election use of its voter file (Election Law §3-103(5)), records no race, too big (19.9M), not competitive.
- **Pennsylvania, Arizona:** both ban posting the voter file online (PA's ban was upheld in VRF v. Schmidt, 2026).
- **Georgia:** records race but not party. **Florida:** as rich as NC, but 23M people and R +13.

## Consequences

- Dots and resident cards show the *real* party registration, race and 2024 turnout (voted or not) of someone at that house; only the name is invented. We accept this as public information, and we offer no takedown path.
- Phone numbers, birth dates and voter IDs are never published, and voters the state marks as confidential are left out.
- Residents are built from the voter-file snapshot of election day (Nov 2024), not the current file, so party, precinct and turnout line up with the 2024 result.
- The ~4M NC residents not on the voter file must be synthesized and placed at addresses from another source.
- The Michigan work (vote-choice rates, block-addresses as the address source) must be redone for NC. The blockdb layout and per-poll cost should carry over, since the population is the same size.
- Some legal claims (NC has no ban on publishing online) rest on search excerpts because government sites were blocked during research; re-check them before building.
