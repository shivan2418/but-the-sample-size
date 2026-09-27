## Agent skills

### Issue tracker

Issues and specs are tracked in this repo's GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Standing orders

- **Prototype in the real stack.** A UI prototype is a Svelte component in the SvelteKit app with one Storybook story per variant or starting state, in place of the `prototype` skill's `?variant=` switcher or single HTML file. It lives in `src/prototypes/<name>/`, following `src/prototypes/README.md`. Prototypes of logic or data layout (scripts, benchmarks) stay standalone in `prototypes/`.
- **Run `pnpm check` before pushing app changes.** It runs types, lint and tests (commands in `README.md`). In cloud sessions, set `CHROMIUM_EXECUTABLE=/opt/pw-browsers/chromium` so the story tests find a browser.
- **Push every branch you create or commit to before finishing.** Cloud containers are ephemeral: unpushed work is lost. This includes throwaway `research/*` and prototype branches, and branches used by subagents.
