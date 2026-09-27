# But the Sample Size

An interactive explainer, for readers without a stats background, of why a random poll of about 1,200 people can describe a country of 300+ million. One static page: SvelteKit with `adapter-static`, Svelte 5 widgets developed in Storybook, hosted on GitHub Pages. The plan lives on the issue tracker ([the map](https://github.com/shivan2418/but-the-sample-size/issues/2)); the vocabulary is in [`CONTEXT.md`](CONTEXT.md).

## Commands

Needs Node 24+, pnpm (`corepack enable` picks up the pinned version) and Docker.

| Command | What it does |
| --- | --- |
| `pnpm install` | Install dependencies |
| `pnpm dev` | Dev server for the page at http://localhost:5173 |
| `pnpm storybook` | Storybook at http://localhost:6006, stories open at phone width |
| `pnpm check` | Every check: `check:types`, then `lint`, then `test` |
| `pnpm check:types` | `svelte-check` (TypeScript and Svelte compiler warnings, including a11y) |
| `pnpm lint` | Prettier check + ESLint |
| `pnpm format` | Prettier, writing fixes |
| `pnpm test` | Vitest once: unit tests (`src/**/*.spec.ts`) and every story rendered in headless Chromium |
| `pnpm test:unit` | Vitest in watch mode |
| `pnpm build` | Prerender the page into `build/` |
| `pnpm preview` | Serve `build/` |
| `pnpm build-storybook` | Static Storybook into `storybook-static/` |
| `pnpm pw:stop` | Stop the Playwright browser container the tests start |

The story tests run Chromium in Playwright's official Docker image, never a host install. `pnpm test` and `pnpm test:unit` start it first (`scripts/playwright-server.sh`, image tag matching the installed `playwright`) and leave it running for the next run; `pnpm pw:stop` stops it. Claude Code cloud sessions have no Docker, so there `CHROMIUM_EXECUTABLE=/opt/pw-browsers/chromium` launches their preinstalled Chromium instead.

## GitHub Pages

A project site is served from `/<repo>/`, so the deploy build sets the base path: `BASE_PATH=/but-the-sample-size pnpm build`. Dev and Storybook serve from the root. Internal links go through `resolve()` from `$app/paths` (ESLint's `svelte/no-navigation-without-resolve` enforces it); in-page anchors like `#marbles` need nothing. `static/.nojekyll` stops Pages from hiding `_app/`. The deploy workflow isn't set up yet.

## Layout

- `src/routes/`: the page. Each rung is a `<section>` anchored by its id in `src/lib/rungs.ts`.
- `src/lib/`: real components and logic, each widget with its stories next to it.
- `src/prototypes/`: throwaway UI prototypes, one folder and one story per variant. See [`src/prototypes/README.md`](src/prototypes/README.md).
- `prototypes/`: throwaway logic and data prototypes (scripts, benchmarks), outside the app and its checks.
- `docs/adr/`, `docs/research/`: decisions and research notes.
