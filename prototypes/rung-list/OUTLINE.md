# PROTOTYPE: rung list (draft 1, throwaway)

Rough outline for [Draft the list of rungs](https://github.com/shivan2418/but-the-sample-size/issues/6), written to be reacted to, not a spec.
Each rung: **claim** (the one thing it proves) · **widget** · **inspect** (what the reader can check) · **relies on**.

---

## 0. The objection

- **Claim:** none. It names the question: "1,200 people out of 300 million? That's 0.0004%. How can that mean anything?"
- **Widget:** the objection quoted back as a comment-thread card, plus one line promising "by the end you'll have run the polls yourself."
- **Inspect:** nothing.
- **Relies on:** nothing.

## 1. A handful of marbles

- **Claim:** a random handful tells you roughly what's in the jar. Small handfuls are rough; bigger handfuls land closer.
- **Widget:** a jar of 1,000 marbles (for example 55% red / 45% blue). Draw 10, 50 or 200; the tally shows. A "draw again ×20" button stacks results in a dot plot, so the spread is visible and narrows as the handful grows.
- **Inspect:** every marble (the whole jar can be counted), the true split, every draw.
- **Relies on:** nothing.

## 2. Big jar, same handful

- **Claim:** the size of the jar barely matters. A handful of 200 from a jar of 1,000 and from a jar of 1,000,000 spread the same way.
- **Widget:** two jars side by side with the same mix and the same handful size. Repeat both; the two dot plots overlap.
- **Inspect:** both jars' true splits; draw counts.
- **Relies on:** 1.
- _This is the core claim in its cleanest form. Rung 8 pays it off at national scale._

## 3. A town

- **Claim:** people work like marbles. In a real town where every resident can be browsed, a random poll lands near the town's true split, with the same spread as the marbles.
- **Widget:** a map of the town with every resident as a dot. "Poll 100" highlights the drawn residents and tallies them; repeat to build the dot plot.
- **Inspect:** click any resident (name, address, race, urban/rural, affiliation); the full town count (audit the true split); each poll's list of drawn residents.
- **Relies on:** 1.

## 4. Random, or just convenient?

- **Claim:** all of this only holds if the poll is random. Ask only the people downtown (or only one neighbourhood) and you're confidently wrong, and asking more of them doesn't help.
- **Widget:** the same town with a toggle: "random" vs "stand on Main Street". Because attributes cluster by place, the convenient poll's dot plot is tight *and* off-target. A poll-size slider shows it doesn't converge on the truth.
- **Inspect:** which residents each method reached (on the map); the true split.
- **Relies on:** 3.

## 5. A state: Michigan

- **Claim:** scale the town up to about 10 million residents and a random poll of 1,200 is just as accurate as it was in the town.
- **Widget:** a Michigan map. "Poll 1,200" draws residents at real addresses (one blockdb run), shows them on the map and tallies them against the true split. Repeats are capped (people-level).
- **Inspect:** any drawn resident; their precinct; the statewide true split and where it comes from.
- **Relies on:** 2, 3, 4.

## 6. People or percentages: same answer

- **Claim:** simulating only the percentages gives the same spread as drawing actual people, so the people can be dropped.
- **Widget:** two dot plots overlaid: the capped people-level repeats from rung 5, and thousands of proportion-only repeats. Same shape.
- **Inspect:** both sets of results; the rule the proportion simulation uses (in one plain sentence).
- **Relies on:** 5.

## 7. Why 1,200 and not 12,000?

- **Claim:** accuracy improves with poll size, but more and more slowly. Going from 1,200 to 12,000 buys about 2 points, which is why pollsters stop around 1,000–1,500.
- **Widget:** a poll-size slider (100 → 20,000) with a live "95% of polls land within ±X points" readout and a dot plot.
- **Inspect:** the repeats behind the readout.
- **Relies on:** 6.

## 8. The whole country

- **Claim:** at 330 million people, a random poll of 1,200 is as accurate as it was for the marbles, the town and Michigan.
- **Widget:** a population-size slider (1,000 → 330 million) next to the poll-size slider. Moving population size doesn't change the spread; moving poll size does.
- **Inspect:** the repeats; the US true split being simulated.
- **Relies on:** 2, 6, 7.

## 9. Back to the objection

- **Claim:** none new. It restates the answer: "1,200 is enough, *if it's random*." Links back to rung 4 for "so why are polls sometimes wrong?"
- **Widget:** the objection card again, now answered.

---

## Open questions this draft raises

1. **Where does "population size doesn't matter" first land?** Here it's seeded with marbles (2) and paid off nationally (8). Alternative: only at 8.
2. **Random vs non-random at the town (4) or the state?** The town is small enough to see the clustering on one screen.
3. **Is "Why 1,200 and not 12,000?" (7) its own rung?** It answers the headline number directly, but it's a new claim that isn't in the original sketch.
4. **"Margin of error":** say it once as "±X points, where 95% of polls land", or never name it?
5. **Nine rungs plus an opener is long for a phone.** Candidates to merge: 1+2, 7+8, 0+9.
