# UI prototypes (throwaway)

A UI prototype answers one design question on the map: a Svelte component in the real app, driven through Storybook. Only the decision carries forward. The code is deleted once the real widget lands.

## Convention

- **One folder per prototype:** `src/prototypes/<name>/`, where `<name>` is short kebab-case (`town-map`, `city-only-toggle`).
- **README first:** `src/prototypes/<name>/README.md` opens with `# PROTOTYPE, throwaway: <what it is>` and links the ticket it answers. It lists the variants and says what was learned once the ticket is resolved.
- **One story per variant or starting state:** `<Name>.stories.svelte` in the folder, titled `Prototypes/<name>/…` so every prototype sits under one "Prototypes" group in Storybook's sidebar. Stories open at phone width.
- **Nothing imports from `src/prototypes/`** outside its own folder: not `src/lib`, not `src/routes`. A prototype may import from `$lib`. When a prototype's variant becomes the real widget, rebuild or move it into `src/lib/` and delete the prototype folder.
- **Same checks as real code:** prototypes are type-checked, linted, formatted, and their stories are rendered by `pnpm test:stories`, so keep them passing (or delete them).

Prototypes of logic or data layout (scripts, benchmarks) aren't UI and stay standalone in the repo-root `prototypes/` folder.
