# PROTOTYPE, throwaway: the national rung

Answers [How the national rung looks and behaves](https://github.com/shivan2418/but-the-sample-size/issues/31). The model is settled in [One US-wide split or per-state proportions?](https://github.com/shivan2418/but-the-sample-size/issues/23): one split of the 155,238,302 who voted for president in 2024, drawn without replacement, with no residents.

Run `pnpm storybook` and open **Prototypes / national-rung**. It's in C2 · Plain compact (`../visual-style/tw.css`).

## First draft

One column, in the order the parts appear. This is only a starting point for the open questions below, not an answer to them.

| Part                  | File                | What it does                                                                                                                                                                                             |
| --------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Country sentence      | `Country.svelte`    | Country, can vote and did vote in one sentence (the first two numbers are rounded placeholders, sources to pick), and the link to _People or percentages_.                                               |
| Split                 | `SplitBar.svelte`   | The popular vote as one stacked bar, with counts, shares and the FEC as the source.                                                                                                                      |
| Sample size           | `SampleSize.svelte` | Type any number or pick 100, 1,200 or 12,000, capped at the population, with the share of everyone it is. No "everyone you ask voted" clause (#29).                                                      |
| Population size       | `PopSlider.svelte`  | A log slider from 1,000 to 155M, starting at 155M. It snaps to the sizes already met (small jar, Charlotte, big jar, North Carolina, US voters), which are also buttons.                                 |
| Polls and ±X          | `Polls.svelte`      | 100 polls as dots over the ±X band (`Strip.svelte`), misses ringed, with the readout above and "Run 100 new polls". Each poll keeps its seed, so dragging the population leaves the dots where they are. |
| Margin-of-error curve | `Curve.svelte`      | ±X against sample size on a linear axis, 1,200 and 12,000 labelled, the reader's size as the dot; tapping sets the sample size. Off 155M, the 155M curve stays behind it dashed.                         |

`model.ts` holds the split, the draws and the margin of error (with the finite-population correction, so it falls to 0 as the sample reaches everyone).

## Still open (#31)

- How the two controls sit together on a phone: here they simply stack, so the dots are below the fold while the reader drags.
- How the reader sees that the spread didn't change as they drag the population: here only the dots staying put and the ±X number. A ghost band (`Strip`'s `ghost`) is wired but unused.
- How the flattening curve is shown and where it goes.
- How much it reuses G · Converge: the strip is redrawn in SVG after its 20-counts line, not imported.

## Stories

- **Draft · Clean start:** 1,200 of 155M.
- **Draft · Charlotte-sized:** 1,200 of 645,000, to see nothing changes.
- **Draft · Sample a big share:** 12,000 of 20,000, where the population finally matters.
- **Draft · 320px:** the clean start on a small phone.
