# But the Sample Size

An interactive explainer, for readers without a stats background, of why a random poll of about 1,200 people can describe a country of 300+ million.

## Language

**Rung**:
One step of the explainer that proves a single claim the reader can check; each rung relies only on claims proven by the rungs below it, and moves up one level of abstraction.
_Avoid_: Level, stage, chapter

**Population**:
Everyone in the group a poll is trying to describe. On the state rung, that's the people registered to vote in North Carolina on election day 2024 (about 7.85 million, not the state's 11 million inhabitants), and a town's population is its share of them. On the national rung, it's the whole US.
_Avoid_: Universe, dataset

**Resident**:
One registered voter in the simulated state, with an invented name at their real registered address. Their party registration, race, age and whether they voted come from their real voter record; only the candidate they would choose is modeled. Nobody is synthesized: people not registered to vote aren't residents, and an address has as many residents as it has registered voters. A resident never stands for a named real individual. The national rung has no residents.
_Avoid_: Voter, citizen, agent, record

**Party registration**:
The party a resident is registered with on the public voter file (Democratic, Republican, unaffiliated, or another party): a known attribute, not a vote.
_Avoid_: Affiliation, party ID, partisanship

**Vote choice**:
How a resident would vote in the election (a candidate, or "wouldn't vote"): what a poll asks. Whether they vote comes from the voter record; which candidate is always modeled, never known for any real person.
_Avoid_: Affiliation, vote, preference

**Poll**:
One random sample of residents together with its tally of their answers.
_Avoid_: Survey, sample run

**True split**:
The population's actual breakdown on a question, which the simulation can reveal and a real poll never can.
_Avoid_: Ground truth, population parameter (and not the same as the real result, which is what happened in the real election)

**Real result**:
The actual 2024 election outcome for a town or state, counted among those who voted; a poll's tally is compared against it, and the population's true split among voters is built to match it.
_Avoid_: Ground truth, actual vote, official result
