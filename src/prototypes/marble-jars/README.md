# PROTOTYPE, throwaway: marble jars, G · Converge

Answers [Marble jars in Storybook: D rebuilt, and fresh takes](https://github.com/shivan2418/but-the-sample-size/issues/15). G · Converge is the marble rung's widget, about 90% of the way to final. The real widget is rebuilt from it in `src/lib/` when the rung is built, and this folder is deleted then.

The variants not taken (D · Side jar, E · Pour, F · Twenty hands, and G's stage 3 as markers) are only on [`prototype/marble-jars-storybook`](https://github.com/shivan2418/but-the-sample-size/tree/prototype/marble-jars-storybook/src/prototypes/marble-jars), in `rejected/`. Rounds 1 and 2 (variants A–D as one HTML page) are on [`claude/jar-prototype-vn9bzk`](https://github.com/shivan2418/but-the-sample-size/tree/claude/jar-prototype-vn9bzk/prototypes/marble-jars).

Run `pnpm storybook` and open **Prototypes / marble-jars**. Stories open at phone width, with `palette`, `speed` (multiplies every duration, default 0.75) and `third` (third-party colour) as controls.

## What it does

Three skippable stages: a jar of 1,000 marbles (55% red), a jar of a million with the same 55%, then a million in four colours (40% red, 35% blue, 20% grey for didn't vote, 5% yellow third party).

- The jar stands on the right and drains as marbles leave. The million jars drain at the true rate, so a sample of 1,000 barely dents them. Marbles arc out to a pile on the left, sized for the reader's sample size from the first marble, and glide smaller if the reader takes more.
- The share so far moves on a 0–100% line with the true value marked. Stage 3 shows "In the jar" vs "Your count" as stacked bars.
- The reader types or picks any sample size, capped at the jar. An ⓘ tip gives the ±X points that 95% of counts land within. "Run 20 counts" draws 20 counts and marks the misses, with each count's tally in a tooltip.
- Controls sit in a fixed grid and never shift: "Count for me" (Start / Pause / Keep going / Again), "By hand" (Take 1 | Take 10), Put them back, Run 20 counts.

`model.ts` holds the draws (exact, without replacement) and the margin of error. `Frame.svelte` mocks the page around the widget.
