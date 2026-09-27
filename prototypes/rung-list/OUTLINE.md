# PROTOTYPE: rung list (draft 2, throwaway)

Rough outline for [Draft the list of rungs](https://github.com/shivan2418/but-the-sample-size/issues/6), written to be reacted to, not a spec.
Draft 2 applies the map owner's answers (ticket comments at 17:12, 17:18, 17:43) and the North Carolina decisions (ADR 0001, `CONTEXT.md`). Draft 1 is in git history.

Each rung: **claim** (the one thing it proves) · **widget** · **inspect** (what the reader can check) · **relies on**.

## Applies to every rung from the marbles on

- **Sample size is the reader's.** A size control (typing and presets such as 100 · 1,200 · 12,000), capped at the population size.
- **"% of population" readout** next to it, e.g. "1,200 is 0.015% of 7.85 million".
- **Side-by-side sizes.** Pin one size and try another: two spreads of repeated polls, e.g. 1,200 vs 12,000.
- **Margin of error.** A live readout: "95% of polls land within ±X points". It's named "margin of error" once, on the marble rung, so readers can match it to news reports. After that it's just the readout.
- **Residents are reached only through polls.** You can't look up a name or an address.

---

## 0. The objection

- **Claim:** none. It names the question: "1,200 people out of 300 million? That's 0.0004%. How can that mean anything?"
- **Widget:** the objection quoted back as a comment-thread card, plus one line: "by the end you'll have run the polls yourself."
- **Inspect:** nothing.
- **Relies on:** nothing.

## 1. Marbles: a small jar and a big jar

- **Claim:** a random handful tells you roughly what's in a jar, and bigger handfuls land closer. The size of the jar barely matters: the same handful from a jar of 1,000 and a jar of 1,000,000 spreads the same way. It only starts to matter when the handful is a big share of the jar.
- **Widget:** two jars side by side from the start, with the same mix (e.g. 55% red / 45% blue): 1,000 marbles and 1,000,000. One sample-size control draws from both. "Repeat ×20" stacks each jar's results in its own dot plot. The two plots overlap until the handful nears 1,000. From there the small jar's plot tightens: at 1,000 it's the whole jar, and the "poll" is exact. The big jar keeps going.
- **Inspect:** every marble in the small jar (it can be counted), both jars' true splits, every draw, "% of jar" for each jar.
- **Relies on:** nothing.
- _"Population size doesn't matter" lands here first, and the whole-country rung pays it off._

## 2. A town

- **Claim:** people work like marbles. In a real North Carolina town, a random poll of its residents lands near the town's real 2024 result, with the same spread as the marbles.
- **Widget:** a dot map of the town, one dot per resident on their house, with a race/party toggle. The reader polls a sample size of their choosing (up to the whole town). Drawn residents light up, and the tally shows their vote choice, with "wouldn't vote" as an answer. Next to it: the town's real 2024 result, compared on the shares among those who voted. The size cap is the town's registered-voter count, so polling everyone is possible, and the result then matches the town's true split exactly: the marble rung's small jar again.
- **Inspect:** each poll's list of drawn residents (full addresses), and each drawn resident's card: invented name, real address, real party registration, race, age and 2024 turnout, modeled candidate, and the "Invented resident · real address" tag. Also the town's true split and real result. A whole-town poll lets the reader audit the full count.
- **Relies on:** 1.
- _The residents are the town's slice of the state's residents: the same people and the same houses as rungs 3 and 4._

## 3. Sample only in a city

- **Claim:** all of this only holds if the poll is random. Poll only one city and you're confidently wrong about the state, and asking more people doesn't help.
- **Widget:** the reader limits the poll to one city (or one county, or only urban areas, etc.), drawn from the real NC residents. The target is North Carolina's real statewide 2024 result. As the sample-size control goes up, the dot plot gets tighter, but around the city's own split, not the state's. Because attributes cluster by place, the miss is large and visible.
- **Inspect:** where the drawn residents live (on the map), their cards, the city's split next to the state's real result.
- **Relies on:** 2.
- _It comes before the state rung, so the state's real result appears here first, as the target the city poll misses. The state rung then shows the random poll hitting it._

## 4. A state: North Carolina

- **Claim:** scale up to North Carolina's 7.85 million registered voters, and a random poll of 1,200 is as accurate as it was in the town.
- **Widget:** a statewide dot map, one dot per resident on their house, with the race/party toggle. Houses with no registered voter have no dot. The reader picks the sample size (1,200 by default; one poll of 12,000 is fine at about 0.4 MB). Each poll is one blockdb run, and its drawn residents light up. The tally sits next to the real 2024 result (R +3.2). People-level repeats are capped. One sentence says "registered voters" with both numbers: 7.85 million of the state's 11 million people. A one-line credit sits under the widget.
- **Inspect:** each drawn resident's card (as in rung 2) and their dot; the statewide true split; where it comes from, in one plain sentence: real registration, race and turnout; the candidate is our estimate, fitted to each precinct's real result.
- **Relies on:** 1, 2, 3.

## 5. People or percentages: same answer

- **Claim:** simulating only the percentages gives the same spread as drawing actual people, so from here on the people can be dropped.
- **Widget:** two dot plots overlaid: the capped people-level repeats from rung 4, and thousands of proportion-only repeats. Same shape. The side-by-side comparison (e.g. 1,200 vs 12,000 with many repeats) runs on proportions from here on.
- **Inspect:** both sets of results; the rule the proportion simulation uses, in one plain sentence.
- **Relies on:** 4.

## 6. The whole country

- **Claim:** at 330 million people, a random poll of 1,200 is as accurate as it was for the marbles, the town and North Carolina. Bigger polls help, but less and less: going from 1,200 to 12,000 buys about 2 points (±2.8 → ±0.9), which is why pollsters stop around 1,000–1,500.
- **Widget:** a population-size slider (1,000 → 330 million) next to the sample-size control. Moving population size doesn't change the spread; moving sample size does. The margin-of-error readout, plotted against sample size, shows the curve flattening.
- **Inspect:** the repeats behind the readout; the US split being simulated.
- **Relies on:** 1, 5.

## 7. Back to the objection

- **Claim:** none new. It restates the answer: "1,200 is enough, *if it's random*." It links back to rung 3 for "so why are polls sometimes wrong?"
- **Widget:** the objection card again, now answered.

---

## Questions this draft raises

1. **Where the disclaimer and "registered voters" line go.** The decisions put both on the state rung. But residents now first appear on the town rung (2), and rung 3 uses them too. Proposal: move the disclaimer sentence and the "registered voters, 7.85M of 11M" line to rung 2. The state rung then restates the numbers for the whole state. The card tag is everywhere regardless.
2. **What "sample size" counts.** Polls ask every drawn registered voter, and roughly one in four didn't vote in 2024, so a poll of 1,200 compares only about 900 voters' answers with the real result. Its margin on that comparison is closer to ±3.3 than ±2.8. Options: (a) the size counts everyone asked, and the readout reflects the voters among them; (b) the size counts voters, and the page keeps drawing until it has that many, like a "likely voter" poll. (a) is simpler and honest; (b) keeps "1,200" matching the headline.
3. **Town dots before a poll.** The draft shows every resident's dot (colour only) on the town and state maps, but opens a card only for drawn residents. That keeps "reached only through polls" true for cards. Confirm that the dots themselves aren't a lookup.
4. **Restricted polls need a restricted random order.** The residents are sorted by one statewide random draw number, so a contiguous run is a random statewide poll. A random poll of one town (2) or one city (3) needs either per-place ordering in blockdb or a filtered scan. That's a build question for the resident layout, not for this list. Flagging it so the town and city rungs aren't assumed to be free.
