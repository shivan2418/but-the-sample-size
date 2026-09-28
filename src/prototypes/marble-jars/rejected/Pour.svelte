<script lang="ts">
	// PROTOTYPE, throwaway. Variant E, a rethink of D: no handfuls and no dots. Both jars pour at once,
	// slowly at first (you can follow single marbles), then faster and faster. A line traces "% red so
	// far" as the count grows, against the band 95% of pours stay inside. The small jar runs dry at
	// 1,000 and its line lands exactly on the true split; the big jar's line keeps narrowing.
	import { onMount } from 'svelte';
	import {
		BIG,
		P,
		SMALL,
		circle,
		clampN,
		fit,
		fmt,
		fmtMoe,
		jar,
		jarPath,
		moe,
		palettes,
		pctOf,
		pourer,
		seeded,
		tok,
		type PaletteKey
	} from '../model';

	let {
		speed = 1,
		axisRange = 'full',
		palette = 'redBlue',
		startWithPours = 0
	}: {
		speed?: number;
		axisRange?: 'full' | 'zoomed';
		palette?: PaletteKey;
		/** Pours already done when the story opens (drawn instantly). */
		startWithPours?: number;
	} = $props();

	const A = $derived(palettes[palette].a.name);
	const lo = $derived(axisRange === 'zoomed' ? 30 : 0);
	const hi = $derived(axisRange === 'zoomed' ? 80 : 100);

	type Line = [number, number][];
	type Pour = {
		s: ReturnType<typeof pourer>;
		b: ReturnType<typeof pourer>;
		order: number[];
		n: number;
		redS: number;
		redB: number;
		lineS: Line;
		lineB: Line;
		nextRec: number;
		t0: number;
		stopAt: number;
	};

	let canvas: HTMLCanvasElement | undefined = $state();
	let stopAt = $state(1200),
		running = $state(false),
		v = $state(0),
		pours: Pour[] = [],
		cur = $state.raw<Pour | null>(null),
		raf = 0,
		particles: { x: number; y: number; c: number; t0: number }[] = [];
	const ui = () => v++;
	const kick = () => {
		if (!raf) raf = requestAnimationFrame(frame);
	};

	/** How many marbles should be out after `t` ms: 10 slow ones, then ten times more every 1.6 s. */
	function target(t: number) {
		const one = 300 * speed;
		if (t < 10 * one) return Math.floor(t / one) + 1;
		return Math.floor(10 * Math.pow(10, (t - 10 * one) / (1600 * speed)));
	}

	function newPour(limit: number): Pour {
		const s = pourer('small');
		return {
			s,
			b: pourer('big'),
			order: [],
			n: 0,
			redS: 0,
			redB: 0,
			lineS: [],
			lineB: [],
			nextRec: 1,
			t0: performance.now(),
			stopAt: limit
		};
	}
	function advance(p: Pour, upTo: number, spawn: boolean) {
		upTo = Math.min(upTo, p.stopAt, BIG);
		while (p.n < upTo) {
			p.n++;
			const rb = p.b.next();
			p.redB += rb;
			if (p.n <= SMALL) {
				const rs = p.s.next();
				p.redS += rs;
				p.order.push(rs);
				if (spawn && upTo - p.n < 3) particles.push({ x: 0, y: 0, c: rs, t0: performance.now() });
			}
			if (p.n <= 100 || p.n >= p.nextRec || p.n === upTo || p.n === SMALL) {
				if (p.n <= SMALL) p.lineS.push([p.n, (p.redS / p.n) * 100]);
				p.lineB.push([p.n, (p.redB / p.n) * 100]);
				p.nextRec = Math.max(p.n + 1, p.n * 1.015);
			}
		}
	}

	function start() {
		if (cur && running) return;
		cur = newPour(stopAt);
		pours.push(cur);
		running = true;
		ui();
		kick();
	}
	function finish() {
		if (!cur) return;
		advance(cur, cur.stopAt, false);
		running = false;
		ui();
		kick();
	}
	function keepGoing() {
		if (!cur || cur.n >= BIG) return;
		cur.stopAt = BIG;
		const t = cur.n;
		// resume on the fast part of the curve from where it stopped
		cur.t0 = performance.now() - (10 * 300 + 1600 * Math.log10(Math.max(10, t) / 10)) * speed;
		running = true;
		ui();
		kick();
	}

	// geometry
	const JW = 86,
		JH = 128,
		JT = 6,
		CH_Y = JT + JH + 40,
		CH_H = 210,
		H = CH_Y + CH_H + 30;
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

	function frame(now: number) {
		raf = 0;
		const c = canvas;
		if (!c) return;
		if (cur && running) {
			advance(cur, target(now - cur.t0), true);
			if (cur.n >= cur.stopAt) running = false;
			ui();
		}
		const { g, w } = fit(c, H);
		const colA = tok(c, '--a'),
			colB = tok(c, '--b'),
			ink = tok(c, '--ink'),
			muted = tok(c, '--muted'),
			line = tok(c, '--line'),
			glass = tok(c, '--glass'),
			pin = tok(c, '--pin'),
			mono = tok(c, '--mono'),
			sans = tok(c, '--sans');

		// two jars, drawn the same size
		const xs = w / 2 - JW - 20,
			xb = w / 2 + 20;
		const n = cur?.n ?? 0;
		// small: drains marble by marble (the top of the pile goes first, it's shuffled anyway)
		g.fillStyle = glass;
		jarPath(g, xs, JT, JW, JH);
		g.fill();
		g.strokeStyle = line;
		g.lineWidth = 1.5;
		jarPath(g, xs, JT, JW, JH);
		g.stroke();
		const left = SMALL - Math.min(n, SMALL);
		for (let i = 0; i < left; i++)
			circle(g, xs + pile.pts[i][0], JT + pile.pts[i][1], pile.r, jar[i] ? colA : colB);
		// big: fine grain; the level drops by the share taken out (invisible until very late)
		g.fillStyle = glass;
		jarPath(g, xb, JT, JW, JH);
		g.fill();
		const level = 1 - Math.min(n, BIG) / BIG,
			top = JT + JH * 0.07 + 6 + (JH * 0.93 - 10) * (1 - level);
		g.save();
		g.beginPath();
		g.rect(xb, top, JW, JT + JH - top);
		g.clip();
		const rnd = seeded(9);
		for (let i = 0; i < 9000; i++) {
			g.fillStyle = rnd() < P ? colA : colB;
			g.fillRect(
				xb + 4 + rnd() * (JW - 8),
				JT + JH * 0.07 + 6 + rnd() * (JH * 0.93 - 10),
				0.8,
				0.8
			);
		}
		g.restore();
		g.strokeStyle = line;
		jarPath(g, xb, JT, JW, JH);
		g.stroke();
		g.fillStyle = muted;
		g.font = '12px ' + mono;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		g.fillText(`${fmt(Math.min(n, SMALL))} of 1,000`, xs + JW / 2, JT + JH + 6);
		g.fillText(`${fmt(n)} of 1,000,000`, xb + JW / 2, JT + JH + 6);

		// single marbles popping out of both mouths while it's still slow
		particles = particles.filter((p) => now - p.t0 < 500 * speed);
		for (const p of particles) {
			const q = (now - p.t0) / (500 * speed);
			for (const [x0, col] of [
				[xs + JW / 2, p.c ? colA : colB],
				[xb + JW / 2, Math.random() < P ? colA : colB]
			] as const) {
				circle(g, x0 + q * 18, JT - 4 - Math.sin(Math.PI * q) * 14 + q * q * 30, 3, col, 1 - q);
			}
		}

		// the chart: x is the count on a log scale, y is % so far
		const x0 = 34,
			x1 = w - 10,
			yT = CH_Y,
			yB = CH_Y + CH_H;
		const X = (k: number) => x0 + ((x1 - x0) * Math.log10(Math.max(1, k))) / 6;
		const Y = (p: number) => yB - ((yB - yT) * (Math.max(lo, Math.min(hi, p)) - lo)) / (hi - lo);
		g.fillStyle = muted;
		g.font = '600 11px ' + sans;
		g.textAlign = 'left';
		g.textBaseline = 'bottom';
		g.fillText(`% ${A.toUpperCase()} SO FAR`, 0, yT - 6);
		// the 95% band for the big jar, and the small jar's (which closes at 1,000)
		g.fillStyle = glass;
		g.beginPath();
		for (let e = 0; e <= 6.001; e += 0.05) g.lineTo(X(10 ** e), Y(55 + moe(10 ** e, BIG)));
		for (let e = 6; e >= -0.001; e -= 0.05) g.lineTo(X(10 ** e), Y(55 - moe(10 ** e, BIG)));
		g.fill();
		g.strokeStyle = pin;
		g.setLineDash([2, 3]);
		for (const sgn of [1, -1]) {
			g.beginPath();
			for (let e = 0; e <= 3.001; e += 0.02)
				g.lineTo(X(10 ** e), Y(55 + sgn * moe(Math.round(10 ** e), SMALL)));
			g.stroke();
		}
		g.setLineDash([]);
		// grid
		g.strokeStyle = line;
		g.lineWidth = 1;
		g.fillStyle = muted;
		g.font = '10px ' + mono;
		g.textBaseline = 'top';
		g.textAlign = 'center';
		for (const [k, lbl] of [
			[1, '1'],
			[10, '10'],
			[100, '100'],
			[1000, '1k'],
			[1e4, '10k'],
			[1e5, '100k'],
			[1e6, '1M']
		] as const) {
			g.beginPath();
			g.moveTo(X(k) + 0.5, yT);
			g.lineTo(X(k) + 0.5, yB);
			g.stroke();
			g.fillText(lbl, X(k), yB + 4);
		}
		g.textAlign = 'right';
		g.textBaseline = 'middle';
		for (let p = lo; p <= hi; p += axisRange === 'zoomed' ? 10 : 25)
			g.fillText(p + '%', x0 - 4, Y(p));
		g.fillText('marbles counted →', x1, yB + 22);
		g.strokeStyle = ink;
		g.setLineDash([3, 3]);
		g.beginPath();
		g.moveTo(x0, Y(55) + 0.5);
		g.lineTo(x1, Y(55) + 0.5);
		g.stroke();
		g.setLineDash([]);
		// pours: older ones faint, the current one strong
		const drawLine = (l: Line, col: string, width: number, dash: number[] = []) => {
			if (!l.length) return;
			g.strokeStyle = col;
			g.lineWidth = width;
			g.setLineDash(dash);
			g.beginPath();
			for (const [k, p] of l) g.lineTo(X(k), Y(p));
			g.stroke();
			g.setLineDash([]);
		};
		for (const p of pours) {
			const isCur = p === cur;
			drawLine(p.lineS, isCur ? muted : line, isCur ? 1.5 : 1, [4, 2]);
			drawLine(p.lineB, isCur ? ink : pin, isCur ? 2 : 1);
		}
		if (cur && cur.n > 0) {
			const last = cur.lineB[cur.lineB.length - 1];
			circle(g, X(last[0]), Y(last[1]), 3.5, ink);
		}
		if (running || particles.length) kick();
	}

	const readout = $derived.by(() => {
		void v;
		if (!cur || cur.n === 0) return null;
		const k = cur.n,
			ks = Math.min(k, SMALL);
		return {
			k,
			pctB: (cur.redB / k) * 100,
			pctS: (cur.redS / ks) * 100,
			ofB: pctOf(k, BIG),
			ofS: k >= SMALL ? 'all' : pctOf(k, SMALL),
			moeB: fmtMoe(moe(k, BIG)),
			moeS: fmtMoe(moe(ks, SMALL)),
			done: !running,
			canGoOn: !running && k < BIG
		};
	});

	onMount(() => {
		for (let i = 0; i < startWithPours; i++) {
			cur = newPour(stopAt);
			advance(cur, stopAt, false);
			pours.push(cur);
		}
		ui();
		const ro = new ResizeObserver(kick);
		if (canvas) ro.observe(canvas);
		return () => {
			ro.disconnect();
			cancelAnimationFrame(raf);
		};
	});
	$effect(() => {
		void palette;
		void axisRange;
		kick();
	});
</script>

<div class="widget">
	<p class="lede">
		Two jars, mixed the same way: one holds a thousand marbles, the other a million. Tip them both
		out, counting as you go, and keep an eye on how {A} your count is so far.
	</p>
	<canvas bind:this={canvas} aria-label="Two jars pouring, and a line of the share counted so far"
	></canvas>
	<div class="legend small">
		<span><i class="solid"></i>big jar</span><span><i class="dashed"></i>small jar</span><span
			><i class="band"></i>where 95% of pours stay</span
		>
	</div>
	<div class="row">
		<label class="eyebrow" for="pour-stop">Stop at</label>
		<input
			id="pour-stop"
			type="number"
			min="1"
			max="1000000"
			inputmode="numeric"
			value={stopAt}
			onchange={(e) => (stopAt = clampN(e.currentTarget.value))}
		/>
		{#each [10, 100, 1200, 12000, 1000000] as p (p)}
			<button aria-pressed={stopAt === p} onclick={() => (stopAt = p)}
				>{p === 1000000 ? 'all' : fmt(p)}</button
			>
		{/each}
	</div>
	<div class="row">
		{#if running}
			<button class="primary" onclick={finish}>Skip to {fmt(cur?.stopAt ?? stopAt)}</button>
		{:else}
			<button class="primary" onclick={start}
				>{v >= 0 && pours.length ? 'Pour again' : 'Start pouring'}</button
			>
			{#if readout?.canGoOn}
				<button onclick={keepGoing}>Keep pouring</button>
			{/if}
		{/if}
	</div>
	<div class="tally" aria-live="polite">
		{#if readout}
			<b class="num">{fmt(readout.k)}</b> counted: <b>{readout.pctB.toFixed(1)}% {A}</b> from the
			big jar ({readout.ofB}
			of it), <b>{readout.pctS.toFixed(1)}%</b> from the small one ({readout.ofS} of it).
		{/if}
	</div>
	{#if readout?.done}
		<div class="moe">
			After {fmt(readout.k)} marbles, 95% of pours are within <b>±{readout.moeB} points</b> of the
			true 55% for the big jar, and <b>±{readout.moeS}</b> for the small one{readout.moeS === '0'
				? ' (it’s empty: you counted every marble)'
				: ''}. That ± is what polls call the <strong>margin of error</strong>.
		</div>
	{/if}
</div>

<style>
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
	}
	.legend i {
		display: inline-block;
		width: 18px;
		height: 0;
		vertical-align: middle;
		margin-right: 5px;
	}
	.solid {
		border-top: 2px solid var(--ink);
	}
	.dashed {
		border-top: 2px dashed var(--muted);
	}
	.band {
		height: 10px !important;
		background: var(--glass);
	}
</style>
