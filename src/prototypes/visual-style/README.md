# PROTOTYPE, throwaway: visual style and design language

Answers [Visual style and design language](https://github.com/shivan2418/but-the-sample-size/issues/16).

**Verdict:** C2 · Plain compact, in Tailwind v4: a basic white look, compact, mobile first with a working desktop layout. A · Newsprint, B · Instrument and C · Plain are here for reference only. The marble widget's stacked stages and its 20-counts strip under the controls were changed in `../marble-jars/Converge.svelte` along the way (resolution on the ticket).

Run `pnpm storybook` and open **Prototypes / visual-style**. Each style is a whole-page mock: masthead, the objection, the accepted marble widget (G · Converge, imported from `../marble-jars/`), a mocked city rung (dot map, resident card, poll against the real result), the later rungs as stubs, and the answer. Every style has a light, a dark and a 320px story; `theme` and `speed` are controls. The copy and mock data are shared (`content.ts`), so only the design language differs. The city numbers are placeholders.

Priorities from the map owner: easy to read, and nothing that looks like AI slop (no grid-paper backgrounds, gradients, status badges, accent-bar callouts or uppercase letter-spaced labels).

| Style              | What it is                                                                                                                                                                                                                                            |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **A · Newsprint**  | An editorial essay. Serif body (Newsreader) on warm paper, a double rule under the masthead, hairline rules between rungs, the widgets set as numbered figures with captions, square outlined buttons, poll vs result as a small table.               |
| **B · Instrument** | A tool you work with. Sans (Inter) with monospaced numbers, a sticky 8-segment progress bar, the objection and answer as dark panels, each rung a white panel with one bold line saying what it shows, readouts above the map, segmented sample size. |
| **C · Plain**      | Legibility over everything, in the spirit of GOV.UK. 19px system type, no web fonts, black on white, one column, no cards or shadows, underlined links, big square buttons, the poll result as one plain sentence.                                    |

| **C2 · Plain compact (Tailwind)** | Round 2, after the map owner picked C in light: the same look with tighter spacing, built in Tailwind v4 with a desktop layout. Mobile first: 17px body, numbered headings, contents folded away. From 1024px, a sticky contents list sits beside a 40rem column, body steps up to 19px, and the city rung puts the map beside the card and result. The marble rung's three stages stack down the page, and Back / Next step smooth-scroll between them (a jump under reduced motion). “Run 20 counts” draws in its own strip under the controls, only once run, so the jar, the share line and the controls fit in one 390 × 844 screen. Stories at 320px, 390px, tablet and desktop. |

A, B and C use plain CSS custom properties. C2 uses Tailwind v4 (`tw.css`): the raw tokens stay as CSS variables (the canvas widgets read them), exposed as utilities (`bg-ink`, `text-muted`, `text-b`) through `@theme inline`, with a `dark:` variant on `data-theme`. The marble widget still styles through its class hooks, in an unlayered block at the end of `tw.css`.
