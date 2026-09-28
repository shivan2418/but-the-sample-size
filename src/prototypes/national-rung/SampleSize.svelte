<script lang="ts">
	// PROTOTYPE, throwaway: the sample-size control, as on the marble rung: type any number or pick
	// one, capped at the population, with the share of everyone it is.
	import { clampN, fmt, pctOf } from './model';

	let {
		n,
		N,
		onchange,
		id = 'n',
		presets = [100, 1200, 12000]
	}: {
		n: number;
		N: number;
		onchange: (n: number) => void;
		id?: string;
		presets?: number[];
	} = $props();

	const shown = $derived(Math.min(n, N));
</script>

<div class="flex flex-col gap-1.5">
	<div class="flex flex-wrap items-center gap-x-3 gap-y-2">
		<label for={id} class="font-bold">How many you ask</label>
		<input
			{id}
			type="number"
			min="1"
			max={N}
			inputmode="numeric"
			value={shown}
			onchange={(e) => onchange(clampN(e.currentTarget.value, N))}
			class="w-[10ch] border-2 border-ink bg-bg px-2 py-1 font-mono text-[17px] font-semibold tabular-nums"
		/>
	</div>
	<div class="flex flex-wrap gap-1.5" role="group" aria-label="Sample sizes">
		{#each presets as p (p)}
			<button
				class="min-h-11 bg-glass px-3 font-semibold tabular-nums shadow-[0_2px_0_var(--line)] aria-pressed:bg-ink aria-pressed:text-bg aria-pressed:shadow-none"
				aria-pressed={shown === p}
				onclick={() => onchange(Math.min(p, N))}>{fmt(p)}</button
			>
		{/each}
	</div>
	<p class="text-[15px] text-muted">
		{#if n > N}
			That’s everyone, so it’s capped at {fmt(N)}.
		{:else}
			That’s {pctOf(shown, N)} of everyone.
		{/if}
	</p>
</div>
