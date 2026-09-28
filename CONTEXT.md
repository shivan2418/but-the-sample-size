# But the Sample Size

An interactive explainer, for readers without a stats background, of why a random poll of about 1,200 people can describe a country of 300+ million.

## Language

**Rung**:
One step of the explainer that proves a single claim the reader can check; each rung relies only on claims proven by the rungs below it, and moves up one level of abstraction.
_Avoid_: Level, stage, chapter

**Population**:
Everyone in the group a poll is trying to describe: Charlotte's or the simulated state's registered voters on those rungs, and the people who voted in the 2024 US presidential election on the national rung.
_Avoid_: Universe, dataset

**Resident**:
One person in the simulated state, with an invented name at a real address. Their party registration, race, age and whether they voted come from a real voter record at that address; the candidate they would choose is always modeled. A resident never stands for a named real individual. The national rung has no residents.
_Avoid_: Voter, citizen, agent, record

**Party registration**:
The party a resident is registered with on the public voter file (Democratic, Republican, unaffiliated, or another party): a known attribute, not a vote.
_Avoid_: Affiliation, party ID, partisanship

**Vote choice**:
How a resident would vote in the election (a candidate, or "wouldn't vote"): what a poll asks. Whether they vote comes from the voter record where one exists; which candidate is always modeled, never known for any real person.
_Avoid_: Affiliation, vote, preference

**Poll**:
One random sample of residents together with its tally of their answers.
_Avoid_: Survey, sample run

**True split**:
The population's actual breakdown on a question, which the simulation can reveal and a real poll never can.
_Avoid_: Ground truth, population parameter (and not the same as the real result, which is what happened in the real election)
On the national rung nothing is modeled, so the true split *is* the real result.

**Real result**:
The actual 2024 presidential election outcome for Charlotte, North Carolina or the whole US (the popular vote), counted among those who voted; a poll's tally is compared against it, and the population's true split among voters is built to match it.
_Avoid_: Ground truth, actual vote, official result

**Red candidate / Blue candidate**:
The two main candidates in the 2024 presidential election, named by their colour on every rung (red the Republican, blue the Democrat, said once); anyone else is **other**.
_Avoid_: Trump, Harris, the parties' names as candidate labels
