<script lang="ts">
	// PROTOTYPE, throwaway. Variant F, a rethink of D: instead of one handful after another, twenty
	// readers grab at once. Twenty trays sit side by side as a wall of handfuls, so the spread is seen
	// in the marbles themselves. "Line them up" sorts the trays by how red they are and squeezes each
	// into a dot: the wall turns into the chart. The handful size and the jar are two toggles, and
	// switching jar re-grabs, so the reader sees the wall barely change.
	import { onMount } from 'svelte';
	import {
		BIG,
		P,
		SMALL,
		circle,
		drawBig,
		drawSmall,
		ease,
		fit,
		fmt,
		fmtMoe,
		jar,
		moe,
		palettes,
		pctOf,
		shuffle,
		tok,
		type PaletteKey
	} from '../model';

	let {
		speed = 1,
		palette = 'redBlue',
		startSize = 10,
		startJar = 'small',
		startSorted = false
	}: {
		speed?: number;
		palette?: PaletteKey;
		startSize?: 10 | 25 | 100;
		startJar?: 'small' | 'big';
		startSorted?: boolean;
	} = $props();

	const A = $derived(palettes[palette].a.name);
	const B = $derived(palettes[palette].b.name);

	type Tray = { marbles: number[]; red: number; pct: number };
	// Start values only: the story sets them once, the reader changes them after.
	// svelte-ignore state_referenced_locally
	let size = $state<10 | 25 | 100>(startSize);
	// svelte-ignore state_referenced_locally
	let which = $state<'small' | 'big'>(startJar);
	let trays = $state<Tray[]>([]),
		sorted = $state(false),
		history = $state<{ size: number; jar: string; pcts: number[] }[]>([]);
	let canvas: HTMLCanvasElement | undefined = $state();
	let raf = 0,
		t0 = 0,
		mode: 'fill' | 'sort' | 'unsort' | 'idle' = 'idle';

	const kick = () => {
		if (!raf) raf = requestAnimationFrame(frame);
	};
	const DUR = { fill: 900, sort: 800 };

	function grab() {
		trays = Array.from({ length: 20 }, () => {
			const r = which === 'small' ? drawSmall(size) : drawBig(size);
			const marbles =
				which === 'small'
					? r.picked!.map((i) => jar[i])
					: shuffle(Array.from({ length: size }, (_, i) => (i < r.red ? 1 : 0)));
			return { marbles, red: r.red, pct: r.pct };
		});
		history = [...history, { size, jar: which, pcts: trays.map((t) => t.pct) }].slice(-4);
		sorted = false;
		mode = 'fill';
		t0 = performance.now();
		kick();
	}
	function toggleSort() {
		sorted = !sorted;
		mode = sorted ? 'sort' : 'unsort';
		t0 = performance.now();
		kick();
	}

	// geometry: a 5 × 4 wall of trays, then the strip where they line up as dots
	const COLS = 5,
		ROWS = 4,
		GAP = 6,
		TRAY_H = 58,
		WALL_H = ROWS * TRAY_H + (ROWS - 1) * GAP,
		STRIP_Y = WALL_H + 34,
		STRIP_H = 90,
		H = STRIP_Y + STRIP_H + 24;

	function frame(now: number) {
		raf = 0;
		const c = canvas;
		if (!c) return;
		const { g, w } = fit(c, H);
		const colA = tok(c, '--a'),
			colB = tok(c, '--b'),
			ink = tok(c, '--ink'),
			muted = tok(c, '--muted'),
			glass = tok(c, '--glass'),
			pin = tok(c, '--pin'),
			line = tok(c, '--line'),
			mono = tok(c, '--mono'),
			sans = tok(c, '--sans');
		const tw = (w - (COLS - 1) * GAP) / COLS;
		const p =
			mode === 'idle'
				? 1
				: Math.min(1, (now - t0) / ((mode === 'fill' ? DUR.fill : DUR.sort) * speed));

		// where each tray's dot goes on the strip
		const x0 = 30,
			x1 = w - 10,
			X = (v: number) => x0 + ((x1 - x0) * v) / 100;
		const rank = trays.map((_, i) => i).sort((a, b) => trays[a].pct - trays[b].pct);
		const binCount: Record<number, number> = {};
		const dotAt = trays.map((t) => {
			const b = Math.round(t.pct / 2) * 2,
				k = (binCount[b] = (binCount[b] ?? 0) + 1);
			return [X(b), STRIP_Y + STRIP_H - 6 - (k - 1) * 9] as const;
		});
		const e = mode === 'sort' ? ease(p) : mode === 'unsort' ? 1 - ease(p) : sorted ? 1 : 0;

		// history rows under the strip (earlier walls, as faint dots)
		g.fillStyle = muted;
		g.font = '600 11px ' + sans;
		g.textAlign = 'left';
		g.textBaseline = 'bottom';
		g.fillText(`EACH TRAY AS ONE DOT: % ${A.toUpperCase()}`, 0, STRIP_Y - 8);
		g.strokeStyle = line;
		g.beginPath();
		g.moveTo(x0, STRIP_Y + STRIP_H + 0.5);
		g.lineTo(x1, STRIP_Y + STRIP_H + 0.5);
		g.stroke();
		g.fillStyle = muted;
		g.font = '10px ' + mono;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		for (const t of [0, 25, 50, 75, 100]) g.fillText(t + '%', X(t), STRIP_Y + STRIP_H + 4);
		g.strokeStyle = ink;
		g.setLineDash([3, 3]);
		g.beginPath();
		g.moveTo(X(55) + 0.5, STRIP_Y);
		g.lineTo(X(55) + 0.5, STRIP_Y + STRIP_H);
		g.stroke();
		g.setLineDash([]);
		// the previous wall, faint, so two sizes or two jars can be compared
		const prev = history.length > 1 ? history[history.length - 2] : null;
		if (prev && e > 0.99) {
			const bc: Record<number, number> = {};
			for (const v of prev.pcts) {
				const b = Math.round(v / 2) * 2,
					k = (bc[b] = (bc[b] ?? 0) + 1);
				g.strokeStyle = pin;
				g.lineWidth = 1.2;
				g.beginPath();
				g.arc(X(b), STRIP_Y + STRIP_H - 6 - (k - 1) * 9, 3.6, 0, 7);
				g.stroke();
			}
		}

		// the trays
		trays.forEach((t, i) => {
			const slot = rank.indexOf(i),
				sx = (i % COLS) * (tw + GAP),
				sy = Math.floor(i / COLS) * (TRAY_H + GAP),
				rx = (slot % COLS) * (tw + GAP),
				ry = Math.floor(slot / COLS) * (TRAY_H + GAP);
			// sorting first reorders the wall by redness, then collapses each tray into its dot
			const move = Math.min(1, e * 2),
				squeeze = Math.max(0, e * 2 - 1);
			const tx = sx + (rx - sx) * ease(move),
				ty = sy + (ry - sy) * ease(move);
			const [dx, dy] = dotAt[i];
			const cx = tx + tw / 2 + (dx - (tx + tw / 2)) * ease(squeeze),
				cy = ty + TRAY_H / 2 + (dy - (ty + TRAY_H / 2)) * ease(squeeze),
				ww = tw + (8 - tw) * ease(squeeze),
				hh = TRAY_H + (8 - TRAY_H) * ease(squeeze);
			if (squeeze < 1) {
				g.globalAlpha = 1 - squeeze;
				g.fillStyle = glass;
				g.beginPath();
				g.roundRect(cx - ww / 2, cy - hh / 2, ww, hh, 6);
				g.fill();
				// marbles, sorted within the tray once lined up so the share reads at a glance
				const ms = e > 0 ? [...t.marbles].sort((a, b) => b - a) : t.marbles;
				const cols = size <= 10 ? 5 : size <= 25 ? 5 : 10,
					rows = Math.ceil(size / cols),
					cell = Math.min((ww - 6) / cols, (hh - 16) / rows),
					gx = cx - (cols * cell) / 2,
					gy = cy - hh / 2 + 4;
				const shown = mode === 'fill' ? Math.floor(p * size * 1.2) : size;
				ms.forEach((m, j) => {
					if (j >= shown) return;
					circle(
						g,
						gx + ((j % cols) + 0.5) * cell,
						gy + (Math.floor(j / cols) + 0.5) * cell,
						cell / 2 - 0.5,
						m ? colA : colB,
						1 - squeeze
					);
				});
				g.fillStyle = muted;
				g.font = '10px ' + mono;
				g.textAlign = 'center';
				g.textBaseline = 'bottom';
				if (mode !== 'fill' || p >= 1) g.fillText(t.pct.toFixed(0) + '%', cx, cy + hh / 2 - 1);
				g.globalAlpha = 1;
			}
			if (squeeze > 0) circle(g, cx, cy, 3.6 + (1 - squeeze) * 3, ink, squeeze);
		});

		if (p < 1) kick();
		else if (mode !== 'idle') mode = 'idle';
	}

	const stats = $derived.by(() => {
		if (!trays.length) return null;
		const ps = trays.map((t) => t.pct),
			N = which === 'small' ? SMALL : BIG;
		return {
			min: Math.min(...ps),
			max: Math.max(...ps),
			moe: fmtMoe(moe(size, N)),
			of: pctOf(size, N),
			inside: ps.filter((x) => Math.abs(x - P * 100) <= moe(size, N)).length
		};
	});

	onMount(() => {
		grab();
		if (startSorted) {
			sorted = true;
			mode = 'idle';
		}
		const ro = new ResizeObserver(kick);
		if (canvas) ro.observe(canvas);
		return () => {
			ro.disconnect();
			cancelAnimationFrame(raf);
		};
	});
	$effect(() => {
		void palette;
		kick();
	});
</script>

<div class="widget">
	<p class="lede">
		Twenty people each grab a handful from the same jar of {A} and {B} marbles. Here are their twenty
		trays. Do they agree?
	</p>
	<div class="row" role="group" aria-label="Jar">
		<span class="eyebrow">Jar</span>
		<button aria-pressed={which === 'small'} onclick={() => ((which = 'small'), grab())}
			>1,000 marbles</button
		>
		<button aria-pressed={which === 'big'} onclick={() => ((which = 'big'), grab())}
			>1,000,000</button
		>
	</div>
	<div class="row" role="group" aria-label="Handful size">
		<span class="eyebrow">Handful</span>
		{#each [10, 25, 100] as const as s (s)}
			<button aria-pressed={size === s} onclick={() => ((size = s), grab())}>{s}</button>
		{/each}
	</div>
	<canvas
		bind:this={canvas}
		aria-label="Twenty trays of marbles, each one a handful, and a strip where they line up as dots"
	></canvas>
	<div class="row">
		<button class="primary" onclick={toggleSort}
			>{sorted ? 'Back to the trays' : 'Line them up'}</button
		>
		<button onclick={grab}>Twenty new handfuls</button>
	</div>
	{#if stats}
		<div class="tally">
			Handfuls of <b class="num">{size}</b> ({stats.of} of the jar) came out between
			<b>{stats.min.toFixed(0)}%</b>
			and
			<b>{stats.max.toFixed(0)}%</b>
			{A}.
		</div>
		{#if sorted}
			<div class="moe">
				The jar is really 55% {A}. 95% of handfuls of {fmt(size)} land within
				<b>±{stats.moe} points</b>
				of that: the
				<strong>margin of error</strong>. {stats.inside} of these 20 did. Hollow dots are the twenty before.
			</div>
		{/if}
	{/if}
</div>
