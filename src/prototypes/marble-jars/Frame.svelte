<script lang="ts">
	// PROTOTYPE, throwaway: a mock of the explainer around the marble rung, so a variant is judged
	// in context (the objection above it, prose around it) rather than in a vacuum.
	import type { Snippet } from 'svelte';
	import { palettes, type PaletteKey } from './model';

	let {
		palette = 'redBlue',
		third = 'yellow',
		intro,
		children
	}: {
		palette?: PaletteKey;
		/** Colour of the third-party marbles in the four-colour jar. */
		third?: 'yellow' | 'purple';
		intro: string;
		children: Snippet;
	} = $props();

	const thirds = {
		yellow: { l: '#DDA700', d: '#F2C230' },
		purple: { l: '#8E44AD', d: '#B37FD6' }
	};

	const pal = $derived(palettes[palette]);
</script>

<div
	class="frame"
	style:--a-l={pal.a.light}
	style:--a-d={pal.a.dark}
	style:--b-l={pal.b.light}
	style:--b-d={pal.b.dark}
	style:--t-l={thirds[third].l}
	style:--t-d={thirds[third].d}
>
	<div class="page">
		<div class="proto">Prototype, throwaway. Nothing here is final copy.</div>
		<div class="objection">
			<div class="who">A comment you've probably seen</div>
			"1,200 people out of 300 million? That's 0.0004%. How can that mean anything?"
		</div>
		<h1>A handful of marbles</h1>
		<p class="prose">{intro}</p>
		{@render children()}
		<p class="prose">
			Next, we swap the marbles for people: every registered voter in a real North Carolina town.
		</p>
	</div>
</div>

<style>
	.frame {
		--bg: #f1f3f6;
		--surface: #ffffff;
		--ink: #17202c;
		--muted: #586273;
		--line: #d5dae2;
		--dim: #cdd3dc;
		--pin: #98a1b0;
		--glass: #e6ebf1;
		--note: #fff7d6;
		--note-ink: #5b4a00;
		--a: var(--a-l);
		--b: var(--b-l);
		--grey: #9aa3af;
		--third: var(--t-l);
		--serif: Georgia, 'Times New Roman', serif;
		--sans: system-ui, -apple-system, 'Segoe UI', sans-serif;
		--mono: ui-monospace, Menlo, Consolas, monospace;
		background: var(--bg);
		color: var(--ink);
		font: 16px/1.55 var(--sans);
		padding: 0 16px 48px;
		min-height: 100vh;
	}
	@media (prefers-color-scheme: dark) {
		.frame {
			color-scheme: dark;
			--bg: #10141a;
			--surface: #19202a;
			--ink: #e5e9f0;
			--muted: #98a2b2;
			--line: #2c3441;
			--dim: #343c49;
			--pin: #6f7988;
			--glass: #212936;
			--note: #2e2a14;
			--note-ink: #e9d98a;
			--a: var(--a-d);
			--b: var(--b-d);
			--grey: #6b7482;
			--third: var(--t-d);
		}
	}
	.frame :global(*) {
		box-sizing: border-box;
	}
	.page {
		max-width: 560px;
		margin: 0 auto;
		display: flex;
		flex-direction: column;
		gap: 18px;
	}
	.proto {
		margin-top: 16px;
		background: var(--note);
		color: var(--note-ink);
		font-size: 13px;
		padding: 8px 12px;
		border-radius: 6px;
	}
	.objection {
		background: var(--surface);
		border: 1px solid var(--line);
		border-radius: 10px;
		padding: 12px 14px;
		font-size: 15px;
	}
	.who {
		font-weight: 600;
		font-size: 13px;
		color: var(--muted);
	}
	h1 {
		font: 600 26px/1.2 var(--serif);
		margin: 0;
	}
	.prose {
		font: 17px/1.6 var(--serif);
		margin: 0;
	}

	/* Shared bits every variant uses. */
	.frame :global(.widget) {
		background: var(--surface);
		border: 1px solid var(--line);
		border-radius: 12px;
		padding: 14px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}
	.frame :global(canvas) {
		display: block;
		width: 100%;
	}
	.frame :global(button) {
		font: 500 14px var(--sans);
		color: var(--ink);
		background: var(--bg);
		border: 1px solid var(--line);
		border-radius: 999px;
		padding: 8px 14px;
		cursor: pointer;
	}
	.frame :global(button.primary),
	.frame :global(button[aria-pressed='true']) {
		background: var(--ink);
		color: var(--surface);
		border-color: var(--ink);
	}
	.frame :global(button:disabled) {
		opacity: 0.4;
		cursor: default;
	}
	.frame :global(input[type='number']) {
		font: 500 16px var(--mono);
		width: 9ch;
		padding: 6px 8px;
		border: 1px solid var(--line);
		border-radius: 6px;
		background: var(--bg);
		color: var(--ink);
	}
	.frame :global(input[type='range']) {
		width: 100%;
		accent-color: var(--ink);
	}
	.frame :global(.row) {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		align-items: center;
	}
	.frame :global(.eyebrow) {
		font: 600 12px var(--sans);
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--muted);
	}
	.frame :global(.small) {
		font-size: 13px;
		color: var(--muted);
		line-height: 1.45;
	}
	.frame :global(.num) {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
	}
	.frame :global(.tally) {
		font-size: 14px;
		min-height: 1.4em;
	}
	.frame :global(.tally b) {
		font: 500 15px var(--mono);
	}
	.frame :global(.ca) {
		color: var(--a);
	}
	.frame :global(.cb) {
		color: var(--b);
	}
	.frame :global(.moe) {
		font-size: 14px;
		border-left: 3px solid var(--ink);
		padding-left: 10px;
	}
	.frame :global(.moe b) {
		font-family: var(--mono);
		font-weight: 500;
	}
	.frame :global(h2) {
		font: 600 20px/1.25 var(--serif);
		margin: 0;
	}
	.frame :global(.lede) {
		font: 16px/1.55 var(--serif);
		margin: 0;
	}
</style>
