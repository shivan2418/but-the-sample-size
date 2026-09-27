# PROTOTYPE, throwaway: marble jars

Answers [How the marble jars look and behave](https://github.com/shivan2418/but-the-sample-size/issues/12). This is not production code; only the decision carries forward.

`index.html` is one self-contained page: a mock of the explainer around four variants of the marble rung's widget. Switch variants with the bar at the bottom, the arrow keys, or `#D` / `#A` / `#B` / `#C`. It is published as a private artifact (the link is on the ticket). The file has no `<html>`/`<head>` wrapper because the artifact host adds one; opening it straight from disk also works.

| | Jars | Sample size control | Spread | Compare sizes |
|---|---|---|---|---|
| **D · Tactile to abstract** (round 2, default) | One jar first; a zoom out 10× reveals a jar 10× as tall, wide and deep (1,000× the marbles), drawn to scale next to the first | Guided steps: take out one marble (slow) → grab 10 (faster) → grab 100 (faster still) and ×20 (dots only) → big jar → free play | Each counted handful collapses into one dot that flies to the chart; one row per jar and size | Rows per size and jar; free play last |
| **A · Twin jars** | Same-size jars side by side. The small jar shows all 1,000 marbles (drawn ones lit up); the big one is fine grain. | Typed number + presets, with buttons ("Grab a handful", "Grab 20 more") | One dot plot per jar | Every size tried keeps its own row |
| **B · One plot, to scale** | One square to scale: the small jar is a speck in the big one's corner | Log slider (10 → 1,000,000); 20 polls re-run live on every move | Both jars mirrored on one dot plot (small up, big down) | Explicit "Pin" (hollow dots) + margin-of-error table |
| **C · Guided steps** | Step 1 counts the small jar; step 4 shows the big jar as 1,000 small jars | Fixed per step, free in the last step | Histograms | Built into the steps (10 vs 200, small vs big, whole jar) |

All variants: 55% red, draws are exact (without replacement), the margin of error is 1.96·√(p(1−p)/n · (N−n)/(N−1)), and "x of your 20 did" counts the actual repeats that landed inside it.
