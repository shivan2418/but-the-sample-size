# PROTOTYPE, throwaway: one slider for the marble sample size

The map owner's idea for the marble rung's sample-size control (G · Converge, [#15](https://github.com/shivan2418/but-the-sample-size/issues/15)), as a self-contained component.

Run `pnpm storybook` and open **Prototypes / sample-slider**.

- **One slider, two markers.** The thumb is the target, from what's already counted up to the whole jar. A marker under the track shows how many are counted. The track is filled solid up to the count and lighter from there to the target.
- **Sample** takes marbles out until the count reaches the target (Pause while it runs, Keep sampling after). It goes at least 12 a second, so small targets can be watched one by one; big ones take about a second and a half.
- **Take 1** takes one marble at once, without pressing Sample. When the count reaches the target, the target moves up with it.
- **The jar** stands to the right of the slider and drains as marbles come out. Draws are real: each marble comes from a random place in a shuffled jar, and the one on top drops into the gap. A jar of 1,000 shows every marble; a million is a red-and-blue speckle that drains at the true rate.
- **Presets** set the target only. One below the count is disabled: you can't put marbles back by moving the target. **Put them back** resets everything.
- The target can't be dragged below the count.

Stories: a jar of 1,000 on a straight track, and a jar of a million on a log track and on a straight one. On a straight track a million wide, anything under about 10,000 is squeezed into the first pixel, hence the log option.
