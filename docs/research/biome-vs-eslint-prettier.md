# Biome or ESLint + Prettier?

Research for the ticket "Biome or ESLint + Prettier for a SvelteKit repo". Question: should this repo (one static page, SvelteKit with `adapter-static`, Svelte 5, pnpm, GitHub Pages, much of the code written by agents) lint and format with **Biome**, or with **ESLint + Prettier** (`eslint-plugin-svelte`, `prettier-plugin-svelte`)?

Researched 2026-09-27. Every claim below cites a primary source or a test run on the pinned versions listed.

## Recommendation

**Use ESLint + Prettier, exactly as `sv create --add prettier eslint` generates it, and keep `svelte-check`.** It is the only lint/format path the Svelte CLI offers, it is stable for `.svelte` files, and it needs no hand-written config. Biome's Svelte support is still labelled experimental and sits behind an opt-in flag. In a test on Biome 2.5.14 it failed to parse a valid Svelte 5 component and changed rendered `<textarea>` content when formatting. Biome's speed (about 0.1 s versus about 3 s here) doesn't matter on a one-page site.

Revisit when Biome removes the `html.experimentalFullSupportEnabled` flag. Its own docs say that will happen once the HTML parser is stable.

Don't use a hybrid (Biome for TS/JS/JSON, Prettier for `.svelte`). It works, but neither project documents it as a recommended setup, and it means two formatters and two configs for no real gain at this size.

## Versions tested

All current on npm as of 2026-09-27.

| Package | Version | Released |
|---|---|---|
| `@biomejs/biome` | 2.5.14 | 2026-09-16 |
| `eslint` | 10.11.0 | 2026-09-18 |
| `eslint-plugin-svelte` | 3.23.0 | 2026-08-13 |
| `typescript-eslint` | 8.70.1 | |
| `eslint-config-prettier` | 10.1.8 | |
| `prettier` | 3.9.9 | 2026-09-23 |
| `prettier-plugin-svelte` | 4.1.1 | 2026-06-15 |
| `sv` (Svelte CLI) | 0.17.1 | 2026-09-19 |
| `svelte` | 5.57.1 | 2026-09-18 |
| `@sveltejs/kit` | 2.70.3 | 2026-08-18 |
| `svelte-check` | 4.7.6 | 2026-08-13 |

The test project was scaffolded with `npx sv@0.17.1 create --template minimal --types ts --add prettier eslint sveltekit-adapter=adapter:static --install pnpm`. Biome was run on copies of the same `src/`.

## 1. How much of a `.svelte` file Biome handles

### What the docs say

- Biome's language-support table lists Svelte as **Experimental** for parsing, formatting and linting, and "Not in progress" for plugins. The HTML formatter itself is also marked experimental. [Biome: Language support](https://biomejs.dev/internals/language-support/) (source: [biomejs/website `language-support.mdx`](https://github.com/biomejs/website/blob/main/src/content/docs/en/internals/language-support.mdx))
- Full Svelte support arrived in **v2.3.0** (blog dated 2025-10-07, npm release 2025-10-24). The post calls it experimental and names "Svelte control-flow syntax" as not yet fully supported. [Biome v2.3 blog](https://biomejs.dev/blog/biome-v2-3/)
- **v2.4.0** (2026-02-10) "significantly improved parsing for Vue and Svelte" and cut false positives in `noUnusedVariables`, `useConst`, `useImportType` and `noUnusedImports`. It also added 15 HTML a11y rules that "work seamlessly with Vue, Svelte, and Astro files". [Biome v2.4 blog](https://biomejs.dev/blog/biome-v2-4/)
- The language-support page says v2.4 "should be sufficient for the majority of Svelte 5 projects, but newer features, rare syntax, or edge cases might not be covered yet". It also says cross-language lint rules "may flag some false positives, as the work is still in progress". [Biome: Language support](https://biomejs.dev/internals/language-support/)
- **It is still behind a flag.** Both of these must be set, or Biome only reads the `<script>` blocks:
  ```json
  { "html": { "experimentalFullSupportEnabled": true, "formatter": { "enabled": true } } }
  ```
  The docs say the option "will be removed once the HTML parser becomes stable". [Biome: Configuration, `html.experimentalFullSupportEnabled`](https://biomejs.dev/reference/configuration/#htmlexperimentalfullsupportenabled); [Biome v2.3 blog](https://biomejs.dev/blog/biome-v2-3/)
- The 2026 roadmap lists "Stabilize everything around HTML" as a goal. It also admits the v2.3 announcement was badly framed "especially after some users rightfully complained about the poor support of the Svelte files". [Biome: Roadmap 2026](https://biomejs.dev/blog/roadmap-2026/)
- The Svelte fixes are still coming fast. The 2.5.x changelog has dozens of Svelte entries: parse fixes for `{#each}` destructuring, `{:then}` without a binding, `{@const}`, snippets and attachments, plus fixes for non-idempotent formatting and a comment-duplication bug that "caused the file to grow exponentially" (2.5.6). [Biome CHANGELOG](https://github.com/biomejs/biome/blob/main/packages/@biomejs/biome/CHANGELOG.md)

### What a test on 2.5.14 showed

I ran one Svelte 5 component with runes (`$props`, `$bindable`, `$state`, `$derived`, `$derived.by`, `$effect`), snippets, `{@render}`, `{@attach}`, `<svelte:boundary>`, keyed and unkeyed `{#each}`, `{#await}` and `{#key}`, plus 22 small single-construct files.

- **Flag off (default):** Biome only sees `<script>`. It reported 7 false "unused" warnings for bindings used only in the markup (`fade`, `header`, `children`, `doubled`, `total`, `tooltip`, `inc`).
- **Flag on, lint:** no false positives. It caught the unused import and variable, and the a11y problems (`<div onclick>` with no key handler or role, `<img>` with no `alt`, `<button>` with no `type`).
- **Flag on, parse failures (2 of 23 files):**
  - `<script lang="ts" generics="T extends { id: number }">` fails with "Template expressions can only contain a single expression". Biome reads the `{` inside the attribute string as a Svelte expression. Generic components are documented Svelte 5 TypeScript syntax, and the same file compiles with `svelte` 5.57.1 and formats with Prettier.
  - `{#each { length: 3 }}` (each without `as`) fails with "Expected 'as' keyword".
- **Flag on, formatting changed rendered output:** `<textarea>  a\n  b</textarea>` became `<textarea>a\n  b</textarea>`, and trailing whitespace inside `<pre>` was removed. The same input in a plain `.html` file was left alone. The changelog records a fix for exactly this in plain HTML in 2.5.7 ("collapsed the whitespace inside `<textarea>` ... changing what the page renders"), so the Svelte path seems to have been missed.
- **Flag on, everything else:** the other 21 files parsed, formatted without repeated changes on a second run, and still compiled with the Svelte compiler afterwards. That covers function bindings, `style:` directives, `class={{...}}`, `<script module>`, `{@debug}`, `svelte:element`, `{await ...}` in markup and `:global {}` blocks.
- **Style vs Prettier:** Biome's defaults differ from `prettier-plugin-svelte`. Biome doesn't indent `<script>`/`<style>` content and removes the `/` from `<input />`. With `html.formatter.indentScriptAndStyle: true` and `selfCloseVoidElements: "always"`, the only remaining difference on the test file was that Biome expands inline `{#if}...{/if}` and `{#key}` blocks onto separate lines. [Biome: Configuration, `html.formatter.*`](https://biomejs.dev/reference/configuration/#htmlformatterindentscriptandstyle)

I didn't find an upstream Biome issue for the `generics` or `<textarea>` bugs; they should be filed if Biome is adopted.

## 2. What ESLint + `eslint-plugin-svelte` gives that Biome lacks

- `eslint-plugin-svelte` 3.23.0 has **86 rules**. Its `recommended` config turns on **35 Svelte rules** (not counting two internal ones), including `require-each-key`, `no-at-html-tags`, `valid-each-key`, `infinite-reactive-loop`, `no-dom-manipulating`, `prefer-svelte-reactivity`, `prefer-writable-derived`, `no-unused-props`, `no-unnecessary-state-wrap`, `no-export-load-in-svelte-module-in-kit-pages`, `valid-prop-names-in-kit-pages` and `no-navigation-without-resolve`. (Counted from the installed package's `configs.recommended`.) [eslint-plugin-svelte README](https://github.com/sveltejs/eslint-plugin-svelte#readme)
- **`svelte/no-navigation-without-resolve` matters for this repo.** It flags internal links and `goto()` calls that skip `resolve()`. On GitHub Pages a project site is served from `/<repo-name>/`, so SvelteKit needs `paths.base` and links must respect it. [SvelteKit docs: adapter-static, GitHub Pages](https://svelte.dev/docs/kit/adapter-static#GitHub-Pages). In the test it flagged a bare `href="/about"`.
- **Biome has 5 Svelte-specific rules, all in nursery:** `noSvelteAtHtmlTags`, `noSvelteAtDebugTags`, `useSvelteRequireEachKey`, `noSvelteUnnecessaryStateWrap` and `noSvelteLegacyConst`. Biome's domain docs say: "Since all rules in this domain are nursery rules, no rules will be activated when enabling the domain." That is why the test didn't flag the missing each-key or the `{@html}`. Biome's rule-source tables map only 4 `eslint-plugin-svelte` rules to Biome rules. [Biome: Domains, Svelte](https://biomejs.dev/linter/domains/#svelte); [Biome: HTML rule sources](https://biomejs.dev/linter/html/sources/); [Biome: JavaScript rule sources](https://biomejs.dev/linter/javascript/sources/)
- **a11y:** `eslint-plugin-svelte` has no a11y rule set of its own. The Svelte compiler already raises a11y warnings, and `svelte-check` reports them. `svelte/valid-compile` can pass them into ESLint too, but it isn't in `recommended`. In the test, `svelte-check` reported `a11y_click_events_have_key_events`, `a11y_no_static_element_interactions` and `a11y_missing_attribute`, plus `css_unused_selector`. Biome has about 36 HTML a11y rules ported from `eslint-plugin-jsx-a11y`, which overlap heavily with the compiler's warnings. So a11y is not a reason to pick either one. [sv docs: `sv check`](https://svelte.dev/docs/cli/sv-check); [Biome: HTML rule sources](https://biomejs.dev/linter/html/sources/)
- **One ESLint false positive:** `@eslint/js` 10 recommended includes `no-useless-assignment`. It flags a `$bindable()` prop that the component only writes to, which is the normal pattern for two-way binding. Biome fixed the same false positive in its own rule in 2.5.3. If it comes up, turn the rule off for `*.svelte`.

## 3. What the SvelteKit scaffold gives you

- `sv` 0.17.1's **official add-ons for lint and format are `prettier` and `eslint`.** There is no Biome add-on, official or community. An npm search of the `sv-add` keyword (52 packages) found none. (`npx sv@0.17.1 add --help`; [sv docs: add-ons](https://svelte.dev/docs/cli/sv-add))
- `sv add eslint` installs `eslint-plugin-svelte`, writes `eslint.config.js`, and wires it up for TypeScript and Prettier. `sv add prettier` adds scripts, `.prettierignore` and a Prettier config, and updates the ESLint config. [sv docs: eslint](https://svelte.dev/docs/cli/eslint); [sv docs: prettier](https://svelte.dev/docs/cli/prettier)
- Together they generated a flat `eslint.config.js` (`@eslint/js` recommended, `typescript-eslint` recommended, `svelte.configs.recommended`, `eslint-config-prettier`, `svelte.configs.prettier`, and `projectService` for `.svelte` files), a `prettier.config.js` (tabs, single quotes, no trailing commas, width 100, `prettier-plugin-svelte`), and these scripts:
  - `"lint": "prettier --check . && eslint ."`
  - `"format": "prettier --write ."`
  - `"check": "svelte-kit sync && svelte-check --tsconfig ./tsconfig.json"`

  Nothing had to be written by hand.
- The Svelte FAQ's answer to "Is there a tool to automatically format my .svelte files?" is Prettier with `prettier-plugin-svelte`. Biome isn't mentioned anywhere in the Svelte docs. [Svelte FAQ](https://svelte.dev/docs/svelte/faq)
- `prettier-plugin-svelte` 4 "only works with `prettier@3` and Svelte 5+" (peer deps `prettier ^3.0.0`, `svelte ^5.0.0`). `eslint-plugin-svelte` 3.23.0 supports ESLint 8.57.1, 9 and 10, and Svelte 3–5. [prettier-plugin-svelte README](https://github.com/sveltejs/prettier-plugin-svelte#readme); [eslint-plugin-svelte README](https://github.com/sveltejs/eslint-plugin-svelte#readme)
- **`svelte-check` is still needed either way.** Neither Biome nor ESLint type-checks `.svelte` markup, and neither runs the Svelte compiler's warnings by default. `svelte-check` does both: TypeScript errors, a11y hints and unused CSS. The Svelte TypeScript docs point to it for CI. [sv docs: `sv check`](https://svelte.dev/docs/cli/sv-check); [Svelte docs: TypeScript](https://svelte.dev/docs/svelte/typescript)

## 4. Is a hybrid common and supported?

- **It works.** With `html.experimentalFullSupportEnabled: true`, `html.formatter.enabled: false` and an `overrides` entry turning off Biome's formatter for `**/*.svelte`, Biome left `.svelte` files alone when formatting but still linted them fully (same results as above). Prettier then formats `.svelte`. The override is documented. [Biome: Configuration, `overrides`](https://biomejs.dev/reference/configuration/#overrides)
- **Neither project recommends it.** Biome's docs describe the flag-off `overrides` only as a way to avoid false positives in `.svelte` files. They don't describe a Biome + Prettier split. The Svelte docs and `sv` only mention Prettier and ESLint.
- **Downsides at this size:** two formatters with two style configs that have to agree, two editor integrations, and Biome's Svelte linting still behind the experimental flag. The `generics` parse error also affects linting, not just formatting.

## 5. Speed

On the scaffolded project (a handful of files), `biome check .` took about 0.1 s. `prettier --check . && eslint .` took about 3 s, mostly ESLint with the type-aware `projectService`. That is a real difference on a big codebase, but not for one static page.

## What would change the call

- Biome removes the `experimentalFullSupportEnabled` flag, or marks Svelte stable on its language-support page.
- The `generics` parse error and the `<textarea>`/`<pre>` whitespace change are fixed.
- Biome's Svelte domain gets recommended (non-nursery) rules, or `sv` ships a Biome add-on.

Any one of these makes Biome worth another look. The first two are the important ones, because formatting that changes output is not safe to run on agent-written code without review.
