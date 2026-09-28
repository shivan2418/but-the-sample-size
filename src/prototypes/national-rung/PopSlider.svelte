<script lang="ts">
	// PROTOTYPE, throwaway: the population-size slider. A log scale from 1,000 to 155M with the sizes
	// the reader has already met marked on it; it snaps to a mark when it's close. The marks are
	// also buttons, so a size can be picked exactly.
	import { marks, toT, fromT, fmt, fmtBig, markFor } from './model';

	let {
		N,
		onchange,
		id = 'pop',
		chips = true
	}: { N: number; onchange: (N: number) => void; id?: string; chips?: boolean } = $props();

	const mark = $derived(markFor(N));
	// alternate the tick labels above and below the track so the close ones don't collide
	const pos = (i: number) => (i % 2 ? 'top-0' : 'bottom-0');
</script>

<div class="flex flex-col gap-1">
	<label for={id} class="font-bold">How many people there are</label>
	<p class="tabular-nums">
		<b>{fmt(N)}</b>
		<span class="text-muted">{mark ? `· ${mark.long}` : N >= 1e6 ? `· ${fmtBig(N)}` : ''}</span>
	</p>
	<div class="relative h-[62px]">
		<input
			{id}
			type="range"
			min="0"
			max="1000"
			step="1"
			value={toT(N)}
			oninput={(e) => onchange(fromT(Number(e.currentTarget.value)))}
			aria-valuetext="{fmt(N)} people{mark ? `, ${mark.long}` : ''}"
			class="absolute top-1/2 left-0 h-11 w-full -translate-y-1/2 accent-ink"
		/>
		{#each marks as m, i (m.N)}
			{@const t = toT(m.N) / 1000}
			<span
				aria-hidden="true"
				class="pointer-events-none absolute {pos(i)} text-[12px]/none whitespace-nowrap {m.N === N
					? 'font-bold text-ink'
					: 'text-muted'}"
				style:left="calc({t} * (100% - 16px) + 8px)"
				style:translate={t < 0.05 ? '-8px 0' : t > 0.95 ? '-100% 0' : '-50% 0'}>{m.label}</span
			>
		{/each}
	</div>
	{#if chips}
		<div class="flex flex-wrap gap-1.5" role="group" aria-label="Sizes you’ve met">
			{#each marks as m (m.N)}
				<button
					class="min-h-9 bg-glass px-2 text-[15px] shadow-[0_2px_0_var(--line)] aria-pressed:bg-ink aria-pressed:text-bg aria-pressed:shadow-none"
					aria-pressed={m.N === N}
					onclick={() => onchange(m.N)}>{m.label}</button
				>
			{/each}
		</div>
	{/if}
</div>
