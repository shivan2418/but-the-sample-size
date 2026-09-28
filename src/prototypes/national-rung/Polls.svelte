<script lang="ts">
	// PROTOTYPE, throwaway: the repeated polls and the ±X readout. Each poll keeps its seed, so while
	// the reader drags a control the dots move only as far as the change really moves them: dragging
	// the population leaves them where they are until the sample is a big share of everyone.
	import Strip from './Strip.svelte';
	import { polls, misses, moe, fmt, fmtMoe, pctOf, TRUE_RED } from './model';

	let {
		n,
		N,
		count = 100,
		ghost = null
	}: {
		n: number;
		N: number;
		count?: number;
		/** An earlier band to compare against, drawn as an outline. */
		ghost?: { m: number; label: string } | null;
	} = $props();

	let batch = $state(0);
	const k = $derived(Math.min(n, N));
	const m = $derived(moe(k, N));
	const ps = $derived(polls(k, N, count, batch));
	const missed = $derived(misses(ps, m));
</script>

<div class="flex flex-col gap-2">
	<p class="border-l-[5px] border-l-b pl-3" aria-live="polite">
		{#if k >= N}
			You asked everyone, so every poll gets the exact result: <b>{TRUE_RED.toFixed(1)}%</b> red.
		{:else}
			With <b class="tabular-nums">{fmt(k)}</b> asked out of {fmt(N)}, 95% of polls land within
			<b class="tabular-nums">±{fmtMoe(m)} points</b> of the real result.
		{/if}
	</p>
	<Strip polls={ps} {m} {ghost} />
	<div class="flex flex-wrap items-center gap-x-3 gap-y-2">
		<button
			class="min-h-11 cursor-pointer bg-glass px-3 py-1.5 font-semibold shadow-[0_2px_0_var(--line)]"
			onclick={() => batch++}>Run {count} new polls</button
		>
		<p class="text-[15px] text-muted">
			{count} polls of {fmt(k)} ({pctOf(k, N)} of everyone).
			{#if k < N}
				{missed === 0 ? 'None' : missed} missed{missed ? ' (ringed)' : ''}; expect about {Math.round(
					count / 20
				)}.
			{/if}
		</p>
	</div>
</div>
