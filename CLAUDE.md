## Agent skills

### Issue tracker

Issues and specs are tracked in this repo's GitHub Issues. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary: `needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: one `CONTEXT.md` plus `docs/adr/` at the repo root. See `docs/agents/domain.md`.

## Standing orders

- **Push every branch you create or commit to before finishing.** Cloud containers are ephemeral: unpushed work is lost. This includes throwaway `research/*` and prototype branches, and branches used by subagents.
