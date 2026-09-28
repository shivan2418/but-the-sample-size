<script lang="ts">
	// PROTOTYPE, throwaway: the share line from G · Converge, redrawn in SVG. Each poll is one dot at
	// the red candidate's share it found, stacked where they pile up, over the ±X band around the
	// 2024 popular vote. Misses (outside the band) are ringed.
	import { TRUE_RED, fmtMoe, type Poll } from './model';

	let {
		polls,
		m,
		ghost = null,
		lo = 35,
		hi = 65,
		height = 150,
		compact = false
	}: {
		polls: Poll[];
		m: number;
		/** An earlier band to compare against, drawn as an outline. */
		ghost?: { m: number; label: string } | null;
		lo?: number;
		hi?: number;
		height?: number;
		/** For small multiples: no tick labels, no truth label. */
		compact?: boolean;
	} = $props();

	let w = $state(340);
	const pad = 16;
	const axisY = $derived(compact ? height - 4 : height - 22);
	const x = (v: number) => pad + ((Math.max(lo, Math.min(hi, v)) - lo) / (hi - lo)) * (w - 2 * pad);
	const r = $derived(compact ? 2.4 : 3.2);

	const placed = $derived.by(() => {
		const bin = (2 * r + 0.4) / ((w - 2 * pad) / (hi - lo)); // one dot wide, in points
		const counts: Record<number, number> = {};
		const top = compact ? 4 : 18;
		const room = axisY - top - r;
		const out = polls.map((p) => {
			const b = Math.round((p.pct - TRUE_RED) / bin);
			const k = (counts[b] ?? 0) + 1;
			counts[b] = k;
			return { b, k, p };
		});
		const max = Math.max(1, ...Object.values(counts));
		const step = Math.min(2 * r + 0.6, room / max);
		return out.map(({ b, k, p }) => ({
			cx: x(TRUE_RED + b * bin),
			cy: axisY - r - 1 - (k - 1) * step,
			miss: Math.abs(p.pct - TRUE_RED) > m + 1e-9,
			p
		}));
	});

	const ticks = $derived(Array.from({ length: (hi - lo) / 5 + 1 }, (_, i) => lo + i * 5));
</script>

<div bind:clientWidth={w} class="w-full">
	<svg
		width={w}
		{height}
		role="img"
		aria-label="{polls.length} polls, each a dot at the red candidate’s share it found. 95% land within ±{fmtMoe(
			m
		)} points of the 2024 popular vote, {TRUE_RED.toFixed(1)}%."
	>
		{#if ghost}
			<rect
				x={x(TRUE_RED - ghost.m)}
				y={compact ? 2 : 16}
				width={Math.max(1, x(TRUE_RED + ghost.m) - x(TRUE_RED - ghost.m))}
				height={axisY - (compact ? 2 : 16)}
				fill="none"
				stroke="var(--muted)"
				stroke-dasharray="4 3"
			/>
		{/if}
		<rect
			x={x(TRUE_RED - m)}
			y={compact ? 2 : 16}
			width={Math.max(1, x(TRUE_RED + m) - x(TRUE_RED - m))}
			height={axisY - (compact ? 2 : 16)}
			fill="var(--glass)"
		/>
		<line
			x1={x(TRUE_RED)}
			x2={x(TRUE_RED)}
			y1={compact ? 0 : 14}
			y2={axisY}
			stroke="var(--ink)"
			stroke-dasharray="3 3"
		/>
		{#if !compact}
			<text x={x(TRUE_RED) + 4} y="11" font-size="12" fill="var(--ink)" font-weight="600"
				>2024 popular vote, {TRUE_RED.toFixed(1)}%</text
			>
		{/if}
		{#each placed as d, i (i)}
			<circle cx={d.cx} cy={d.cy} {r} fill="var(--a)">
				<title
					>Poll {i + 1}: {d.p.red.toLocaleString('en-US')} of {d.p.n.toLocaleString('en-US')} red = {d.p.pct.toFixed(
						1
					)}%</title
				>
			</circle>
			{#if d.miss}
				<circle cx={d.cx} cy={d.cy} r={r + 2} fill="none" stroke="var(--ink)" stroke-width="1.2" />
			{/if}
		{/each}
		<line x1={pad} x2={w - pad} y1={axisY + 0.5} y2={axisY + 0.5} stroke="var(--line)" />
		{#if !compact}
			{#each ticks as t (t)}
				<line x1={x(t)} x2={x(t)} y1={axisY} y2={axisY + 4} stroke="var(--muted)" />
				<text
					x={x(t)}
					y={axisY + 16}
					font-size="11"
					text-anchor="middle"
					fill="var(--muted)"
					font-family="var(--mono)">{t}%</text
				>
			{/each}
		{/if}
	</svg>
</div>
