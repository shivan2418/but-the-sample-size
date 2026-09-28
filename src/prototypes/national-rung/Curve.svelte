<script lang="ts">
	// PROTOTYPE, throwaway: the margin of error against sample size, on a plain linear axis so the
	// flattening shows: 1,200 → 12,000 buys about 2 points. The reader's sample size is the dot.
	import { moe, fmt, fmtMoe, TOTAL } from './model';

	let {
		n,
		N,
		maxX = 15000,
		height = 170,
		onpick
	}: {
		n: number;
		N: number;
		maxX?: number;
		height?: number;
		/** Tap the chart to set the sample size there. */
		onpick?: (n: number) => void;
	} = $props();

	let w = $state(340);
	const L = 34,
		R = 10,
		T = 10,
		B = 26,
		maxY = 10;
	const x = (v: number) => L + (Math.min(v, maxX) / maxX) * (w - L - R);
	const y = (v: number) => T + (1 - Math.min(v, maxY) / maxY) * (height - T - B);

	function path(pop: number) {
		let d = '';
		for (let i = 0; i <= 120; i++) {
			// dense near the start, where the curve bends
			const v = Math.max(40, Math.round(maxX * Math.pow(i / 120, 2)));
			d += (i ? 'L' : 'M') + x(v).toFixed(1) + ',' + y(moe(v, pop)).toFixed(1);
		}
		return d;
	}

	const ref = [1200, 12000];
	const nm = $derived(moe(n, N));

	function pick(e: PointerEvent) {
		if (!onpick) return;
		const box = (e.currentTarget as SVGElement).getBoundingClientRect();
		const v = ((e.clientX - box.left - L) / (w - L - R)) * maxX;
		const nice = v < 2000 ? Math.round(v / 50) * 50 : Math.round(v / 500) * 500;
		onpick(Math.max(50, Math.min(maxX, nice)));
	}
</script>

<div bind:clientWidth={w} class="w-full">
	<svg
		width={w}
		{height}
		role="img"
		aria-label="Margin of error against sample size. It falls fast at first, then flattens: ±{fmtMoe(
			moe(1200, N)
		)} points at 1,200, ±{fmtMoe(moe(12000, N))} at 12,000."
		onpointerdown={pick}
		class={onpick ? 'cursor-pointer touch-none' : ''}
	>
		{#each [0, 2, 4, 6, 8, 10] as t (t)}
			<line x1={L} x2={w - R} y1={y(t)} y2={y(t)} stroke="var(--dim)" />
			<text
				x={L - 6}
				y={y(t) + 4}
				font-size="11"
				text-anchor="end"
				fill="var(--muted)"
				font-family="var(--mono)">±{t}</text
			>
		{/each}
		{#each [0, 5000, 10000, 15000].filter((t) => t <= maxX) as t (t)}
			<text
				x={x(t)}
				y={height - 8}
				font-size="11"
				text-anchor={t === 0 ? 'start' : t === maxX ? 'end' : 'middle'}
				fill="var(--muted)"
				font-family="var(--mono)">{fmt(t)}</text
			>
		{/each}
		{#if N < TOTAL * 0.9}
			<path
				d={path(TOTAL)}
				fill="none"
				stroke="var(--line)"
				stroke-width="2"
				stroke-dasharray="5 4"
			/>
		{/if}
		<path d={path(N)} fill="none" stroke="var(--ink)" stroke-width="2" />
		{#each ref as v (v)}
			<circle cx={x(v)} cy={y(moe(v, N))} r="3" fill="var(--ink)" />
			<text
				x={v > maxX * 0.7 ? x(v) - 6 : x(v) + 6}
				y={y(moe(v, N)) - 7}
				font-size="12"
				fill="var(--ink)"
				text-anchor={v > maxX * 0.7 ? 'end' : 'start'}>{fmt(v)}: ±{fmtMoe(moe(v, N))}</text
			>
		{/each}
		{#if n <= maxX}
			<circle cx={x(n)} cy={y(nm)} r="6" fill="var(--a)" stroke="var(--bg)" stroke-width="2" />
		{/if}
	</svg>
</div>
