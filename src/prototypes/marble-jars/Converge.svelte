<script lang="ts">
	// PROTOTYPE, throwaway. Variant G, from the map owner's reaction to E (Pour): keep the pour's
	// convergence, drop the technical chart. The jar stands on the right; each marble flies out and
	// lands on the left. Below, one line from 0% to 100% with the true split marked, and a marker for
	// "% red so far" that moves after every marble. It jumps about at first and settles as N grows.
	import { onMount } from 'svelte';
	import {
		P,
		SMALL,
		circle,
		fit,
		fmt,
		jar,
		jarPath,
		palettes,
		shuffle,
		tok,
		type PaletteKey
	} from './model';

	let {
		speed = 1,
		palette = 'redBlue',
		startWith = 0
	}: {
		speed?: number;
		palette?: PaletteKey;
		/** Marbles already counted when the story opens. */
		startWith?: number;
	} = $props();

	const A = $derived(palettes[palette].a.name);
	const B = $derived(palettes[palette].b.name);

	// geometry
	const JW = 100,
		JH = 160,
		TOP = 34,
		LINE_Y = TOP + JH + 62,
		H = LINE_Y + 44;
	const pile = (() => {
		const iw = JW - 8,
			ih = JH * 0.93 - 8,
			d = Math.sqrt(((iw * ih) / SMALL) * (2 / Math.sqrt(3))) * 0.97,
			pts: [number, number][] = [];
		for (let row = 0; pts.length < SMALL; row++) {
			const y = JH - 4 - d / 2 - row * d * 0.866,
				off = row % 2 ? d / 2 : 0;
			for (let x = 4 + d / 2 + off; x <= JW - 4 - d / 2 && pts.length < SMALL; x += d)
				pts.push([x, y]);
		}
		return { pts, r: d / 2 - 0.3 };
	})();

	// the order marbles come out in; landed[i] is the i-th marble counted
	let order = shuffle(Array.from({ length: SMALL }, (_, i) => i));
	let taken = 0; // marbles that have left the jar (some may still be flying)
	const out = new Uint8Array(SMALL);
	let landed: number[] = [];
	let flying: { m: number; t0: number; dur: number }[] = [];
	let trail: { pct: number; t: number }[] = [];
	let shown = 0; // the marker's drawn position, eased toward the real value
	let auto = $state(false),
		counted = $state(0),
		red = $state(0);
	let canvas: HTMLCanvasElement | undefined = $state();
	let raf = 0,
		nextAt = 0;
	const kick = () => {
		if (!raf) raf = requestAnimationFrame(frame);
	};

	/** Time between marbles: slow enough to follow one by one at first, then faster and faster. */
	const gap = (k: number) => Math.max(8, 650 * Math.pow(0.93, k)) * speed;
	const flight = (k: number) => Math.max(180, 600 * Math.pow(0.97, k)) * speed;

	function launch(now: number) {
		if (taken >= SMALL) return;
		const m = order[taken++];
		out[m] = 1;
		flying.push({ m, t0: now, dur: flight(taken) });
	}
	function land(m: number) {
		landed.push(m);
		counted = landed.length;
		red += jar[m];
		trail.push({ pct: (red / counted) * 100, t: performance.now() });
		if (trail.length > 60) trail.shift();
	}
	function takeOne() {
		auto = false;
		launch(performance.now());
		kick();
	}
	function toggleAuto() {
		auto = !auto;
		nextAt = performance.now();
		kick();
	}
	function putBack() {
		auto = false;
		order = shuffle(order);
		taken = 0;
		out.fill(0);
		landed = [];
		flying = [];
		trail = [];
		counted = 0;
		red = 0;
		kick();
	}

	function frame(now: number) {
		raf = 0;
		const c = canvas;
		if (!c) return;
		if (auto) {
			while (now >= nextAt && taken < SMALL) {
				launch(now);
				nextAt += gap(taken);
			}
			if (taken >= SMALL) auto = false;
		}
		// land in the order they left, so each marble keeps its slot
		while (flying.length && now - flying[0].t0 >= flying[0].dur) land(flying.shift()!.m);

		const { g, w } = fit(c, H);
		const colA = tok(c, '--a'),
			colB = tok(c, '--b'),
			ink = tok(c, '--ink'),
			muted = tok(c, '--muted'),
			line = tok(c, '--line'),
			glass = tok(c, '--glass'),
			mono = tok(c, '--mono'),
			sans = tok(c, '--sans');
		const col = (m: number) => (jar[m] ? colA : colB);

		// the jar, on the right; it drains as marbles leave
		const jx = w - JW - 4;
		g.fillStyle = glass;
		jarPath(g, jx, TOP, JW, JH);
		g.fill();
		g.strokeStyle = line;
		g.lineWidth = 1.5;
		jarPath(g, jx, TOP, JW, JH);
		g.stroke();
		for (let m = 0; m < SMALL; m++)
			if (!out[m]) circle(g, jx + pile.pts[m][0], TOP + pile.pts[m][1], pile.r, col(m));
		g.fillStyle = muted;
		g.font = '12px ' + mono;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		g.fillText(`${fmt(SMALL - taken)} left`, jx + JW / 2, TOP + JH + 6);

		// where they land, on the left: the grid shrinks to fit everything counted
		const lw = jx - 16,
			lh = JH * 0.93,
			ly = TOP + JH * 0.07,
			total = Math.max(10, landed.length + flying.length),
			cols = Math.max(5, Math.ceil(Math.sqrt((total * lw) / lh))),
			size = Math.min(22, lw / cols),
			slot = (i: number): [number, number, number] => [
				((i % cols) + 0.5) * size,
				ly + lh - (Math.floor(i / cols) + 0.5) * size,
				Math.max(0.8, size / 2 - 0.6)
			];
		g.fillStyle = glass;
		g.globalAlpha = 0.5;
		g.beginPath();
		g.roundRect(0, ly - 4, lw + 4, lh + 8, 8);
		g.fill();
		g.globalAlpha = 1;
		landed.forEach((m, i) => {
			const [x, y, r] = slot(i);
			circle(g, x + 2, y, r, col(m));
		});
		if (!landed.length && !flying.length) {
			g.fillStyle = muted;
			g.font = '12px ' + sans;
			g.textAlign = 'center';
			g.textBaseline = 'middle';
			g.fillText('Counted marbles', lw / 2, ly + lh / 2 - 8);
			g.fillText('land here', lw / 2, ly + lh / 2 + 8);
		}
		g.fillStyle = muted;
		g.font = '12px ' + mono;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		g.fillText(`${fmt(landed.length)} counted`, lw / 2, TOP + JH + 6);

		// marbles in the air: up out of the mouth, then an arc to the left
		flying.forEach((f, j) => {
			const p = Math.min(1, (now - f.t0) / f.dur),
				idx = landed.length + j,
				[tx, ty, tr] = slot(idx),
				mx = jx + JW / 2,
				my = TOP - 6;
			const x = mx + (tx + 2 - mx) * p,
				y = my + (ty - my) * p * p - Math.sin(Math.PI * p) * 26;
			circle(g, x, y, pile.r + (tr - pile.r) * p + 1, col(f.m));
		});

		// the line: 0% to 100%, the true split marked, and the marker for "so far"
		const x0 = 14,
			x1 = w - 14,
			X = (v: number) => x0 + ((x1 - x0) * v) / 100;
		g.strokeStyle = line;
		g.lineWidth = 6;
		g.lineCap = 'round';
		g.beginPath();
		g.moveTo(x0, LINE_Y);
		g.lineTo(x1, LINE_Y);
		g.stroke();
		g.lineCap = 'butt';
		g.fillStyle = muted;
		g.font = '11px ' + mono;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		for (const t of [0, 25, 50, 75, 100]) g.fillText(t + '%', X(t), LINE_Y + 16);
		// true value
		g.strokeStyle = ink;
		g.lineWidth = 2;
		g.beginPath();
		g.moveTo(X(P * 100), LINE_Y - 12);
		g.lineTo(X(P * 100), LINE_Y + 12);
		g.stroke();
		g.fillStyle = ink;
		g.font = '600 11px ' + sans;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		// where the marker has been lately: fading ticks, so the settling shows
		for (const t of trail) {
			const age = (now - t.t) / (2500 * speed);
			if (age >= 1) continue;
			g.globalAlpha = 0.5 * (1 - age);
			g.fillStyle = ink;
			g.fillRect(X(t.pct) - 1, LINE_Y - 5, 2, 10);
		}
		g.globalAlpha = 1;
		g.fillStyle = ink;
		if (counted) {
			const target = (red / counted) * 100;
			shown = shown + (target - shown) * 0.25;
			if (Math.abs(target - shown) < 0.05) shown = target;
			const mx = X(shown);
			g.beginPath();
			g.moveTo(mx, LINE_Y - 6);
			g.lineTo(mx - 7, LINE_Y - 18);
			g.lineTo(mx + 7, LINE_Y - 18);
			g.closePath();
			g.fillStyle = colA;
			g.fill();
			g.font = '600 13px ' + mono;
			g.textBaseline = 'bottom';
			g.fillStyle = ink;
			g.fillText(`${shown.toFixed(0)}%`, Math.max(x0 + 12, Math.min(x1 - 12, mx)), LINE_Y - 20);
			g.font = '600 11px ' + sans;
			g.textBaseline = 'top';
			g.fillText('true 55%', X(P * 100), LINE_Y + 30);
		} else {
			g.textBaseline = 'bottom';
			g.fillText('true 55%', X(P * 100), LINE_Y - 14);
		}

		const moving = counted > 0 && shown !== (red / counted) * 100;
		const fading = trail.some((t) => now - t.t < 2500 * speed);
		if (auto || flying.length || moving || fading) kick();
	}

	onMount(() => {
		for (let i = 0; i < Math.min(startWith, SMALL); i++) {
			out[order[taken]] = 1;
			land(order[taken++]);
		}
		shown = counted ? (red / counted) * 100 : 0;
		trail = [];
		kick();
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
		This jar holds 1,000 marbles, and 55% of them are {A}. Take them out one at a time and keep
		count. How close is your count to 55%?
	</p>
	<canvas
		bind:this={canvas}
		aria-label="A jar on the right, the marbles counted so far on the left, and a line showing the share of {A} so far against the true 55%"
	></canvas>
	<div class="tally" aria-live="polite">
		{#if counted}
			<b class="num">{fmt(counted)}</b> counted: <b class="ca">{fmt(red)}</b>
			{A}, <b class="cb">{fmt(counted - red)}</b>
			{B}. That’s <b>{((red / counted) * 100).toFixed(1)}% {A}</b>.
		{:else}
			Nothing counted yet.
		{/if}
	</div>
	<div class="row">
		<button class="primary" onclick={toggleAuto} disabled={counted >= SMALL}>
			{auto ? 'Pause' : counted ? 'Keep going' : 'Start'}
		</button>
		<button onclick={takeOne} disabled={auto || counted >= SMALL}>Take one out</button>
		<button onclick={putBack} disabled={!counted && !auto}>Put them back</button>
	</div>
	{#if counted >= SMALL}
		<div class="moe">You counted every marble, so your count is exactly 55%.</div>
	{:else if counted >= 100}
		<div class="moe">
			After {fmt(counted)} marbles your count is {Math.abs((red / counted) * 100 - 55).toFixed(1)} points
			from the truth.
		</div>
	{/if}
</div>
