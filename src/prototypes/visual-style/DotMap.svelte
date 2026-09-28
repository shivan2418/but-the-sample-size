<script lang="ts">
	// PROTOTYPE, throwaway: a stand-in for the city dot map. Every dot is a resident; polled ones take
	// their answer's colour, the rest stay dim. Colours and shape come from the style's tokens
	// (--dim, --a, --b, --grey, --ink, --surface), so each style re-skins it.
	import { cityDots } from './content';

	let {
		selected = 12,
		radius = 1.6,
		viewBox = '0 0 100 100'
	}: { selected?: number; radius?: number; viewBox?: string } = $props();

	const dots = cityDots();
	const polled = dots.filter((d) => d.polled);
	const pick = $derived(polled[selected % polled.length]);
	const col = { a: 'var(--a)', b: 'var(--b)', none: 'var(--grey)' };
</script>

<svg {viewBox} role="img" aria-label="Map of Charlotte: one dot per registered voter">
	{#each dots as d, i (i)}
		{#if !d.polled}
			<circle cx={d.x * 100} cy={d.y * 100} r={radius * 0.6} fill="var(--dim)" />
		{/if}
	{/each}
	{#each polled as d, i (i)}
		<circle cx={d.x * 100} cy={d.y * 100} r={radius} fill={col[d.choice]} />
	{/each}
	<circle
		cx={pick.x * 100}
		cy={pick.y * 100}
		r={radius * 2.8}
		fill="none"
		stroke="var(--ink)"
		stroke-width="0.8"
	/>
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: auto;
	}
</style>
