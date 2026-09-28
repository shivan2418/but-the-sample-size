<script lang="ts">
	// PROTOTYPE, throwaway. Variant G, from the map owner's reaction to E (Pour): keep the pour's
	// convergence, drop the technical chart. The jar stands on the right; each marble flies out and
	// lands on the left. Below, the share so far moves after every marble and settles on the truth.
	// Three skippable stages: a jar of 1,000, a jar of 1,000,000, then a million with four colours
	// (two parties, didn't vote, third party). The reader sets any sample size, can read the 95%
	// range for it, and can run 20 counts at once to see which ones miss.
	import { onMount } from 'svelte';
	import {
		circle,
		clampN,
		fit,
		fmt,
		jarPath,
		palettes,
		pctOf,
		seeded,
		shuffle,
		tok,
		type PaletteKey
	} from './model';

	let {
		speed = 1,
		palette = 'redBlue',
		startStage = 0,
		startWith = 0,
		startTarget = 100,
		multiDisplay = 'bars',
		startRuns = false,
		onStep
	}: {
		speed?: number;
		palette?: PaletteKey;
		/** 0: 1,000 marbles, 1: 1,000,000, 2: 1,000,000 in four colours. */
		startStage?: number;
		/** Marbles already counted when the story opens. */
		startWith?: number;
		/** The sample size the reader starts with: the pile is sized for it from the first marble. */
		startTarget?: number;
		/** How the four-colour stage shows the shares: one marker per colour, or stacked bars. */
		multiDisplay?: 'markers' | 'bars';
		/** Open with 20 counts already run. */
		startRuns?: boolean;
		/** Stacked mode (visual-style #16): the widget shows only `startStage`, with no stage tabs,
		 * and Back / Next step call this instead, so the page can scroll to the next stage. */
		onStep?: (dir: -1 | 1) => void;
	} = $props();

	type Cat = { name: string; share: number; col: string };
	const A = $derived(palettes[palette].a.name);
	const B = $derived(palettes[palette].b.name);
	const stages = $derived([
		{
			N: 1000,
			t: 'One jar',
			lede: `This jar holds 1,000 marbles, and 55% of them are ${A}. Take some out and keep count. How close does your count get to 55%?`,
			cats: [
				{ name: A, share: 0.55, col: '--a' },
				{ name: B, share: 0.45, col: '--b' }
			] as Cat[]
		},
		{
			N: 1_000_000,
			t: 'A jar 1,000 times bigger',
			lede: `This jar holds a million marbles, mixed the same way: 55% ${A}. Take out the same number as before. Does a bigger jar need a bigger handful?`,
			cats: [
				{ name: A, share: 0.55, col: '--a' },
				{ name: B, share: 0.45, col: '--b' }
			] as Cat[]
		},
		{
			N: 1_000_000,
			t: 'More than two colours',
			lede: `Real elections have more than two answers. This million-marble jar is 40% ${A}, 35% ${B}, 20% grey for people who didn’t vote and 5% for a third party. Every colour settles at once.`,
			cats: [
				{ name: A, share: 0.4, col: '--a' },
				{ name: B, share: 0.35, col: '--b' },
				{ name: 'didn’t vote', share: 0.2, col: '--grey' },
				{ name: 'third party', share: 0.05, col: '--third' }
			] as Cat[]
		}
	]);

	// Start values only: the story sets them once, the reader changes them after.
	// svelte-ignore state_referenced_locally
	let stage = $state(Math.max(0, Math.min(2, startStage)));
	// svelte-ignore state_referenced_locally
	let target = $state(startTarget);
	const S = $derived(stages[stage]);
	const cats = $derived(S.cats);
	const multi = $derived(cats.length > 2);

	/** 95% margin of error in points for a share `p`, with the finite-population correction. */
	const moeP = (p: number, n: number, N: number) =>
		n >= N ? 0 : 1.96 * Math.sqrt(((p * (1 - p)) / n) * ((N - n) / (N - 1))) * 100;
	const fmtPts = (m: number) => (m === 0 ? '0' : m < 0.1 ? m.toFixed(2) : m.toFixed(1));

	// ---- the small jar's 1,000 marbles, fixed in place in the pile ----
	const JW = 100,
		JH = 160,
		TOP = 34;
	const pile = (() => {
		const iw = JW - 8,
			ih = JH * 0.93 - 8,
			d = Math.sqrt(((iw * ih) / 1000) * (2 / Math.sqrt(3))) * 0.97,
			pts: [number, number][] = [];
		for (let row = 0; pts.length < 1000; row++) {
			const y = JH - 4 - d / 2 - row * d * 0.866,
				off = row % 2 ? d / 2 : 0;
			for (let x = 4 + d / 2 + off; x <= JW - 4 - d / 2 && pts.length < 1000; x += d)
				pts.push([x, y]);
		}
		return { pts, r: d / 2 - 0.3 };
	})();
	const smallJar = shuffle(Array.from({ length: 1000 }, (_, i) => (i < 550 ? 0 : 1)));

	/** One marble at a time from the current stage's jar, exact (without replacement). */
	function source(st: number, N: number, cs: Cat[]) {
		if (st === 0) {
			// the colour is a fair random draw; which marble leaves is the topmost of that colour,
			// so the pile settles lower instead of getting holes (pile slots run bottom to top)
			const stacks = [0, 1].map((c) =>
				Array.from({ length: 1000 }, (_, i) => i).filter((i) => smallJar[i] === c)
			);
			return {
				next: () => {
					const left = stacks[0].length + stacks[1].length;
					if (!left) return null;
					const cat = Math.random() * left < stacks[0].length ? 0 : 1;
					return { cat, m: stacks[cat].pop()! };
				}
			};
		}
		const R = cs.map((c) => Math.round(c.share * N));
		let T = N;
		return {
			next: () => {
				if (T === 0) return null;
				let u = Math.random() * T,
					cat = 0;
				while (u >= R[cat]) u -= R[cat++];
				R[cat]--;
				T--;
				return { cat, m: -1 };
			}
		};
	}
	/** The tally of one whole count of `n`, drawn instantly (for "Run 20"). */
	function sample(st: number, n: number, N: number, cs: Cat[]) {
		const tally = cs.map(() => 0);
		n = Math.min(n, N);
		if (st === 0) {
			const idx = Array.from({ length: 1000 }, (_, i) => i);
			for (let i = 0; i < n; i++) {
				const j = i + Math.floor(Math.random() * (1000 - i));
				[idx[i], idx[j]] = [idx[j], idx[i]];
				tally[smallJar[idx[i]]]++;
			}
			return tally;
		}
		const s = source(st, N, cs);
		for (let i = 0; i < n; i++) tally[s.next()!.cat]++;
		return tally;
	}

	// ---- engine state (plain, mutated per frame; `v` bumps when the DOM text should refresh) ----
	let src = source(0, 1000, []);
	let taken = 0;
	const out = new Uint8Array(1000);
	let landed: number[] = []; // category of each counted marble, in order
	let flying: { cat: number; m: number; t0: number; dur: number; sx: number; sy: number }[] = [];
	let counts: number[] = [0, 0];
	let shown: number[] = [0, 0]; // eased shares for the markers and bars
	let trail: { pct: number; t: number }[] = [];
	let runs: null | { n: number; results: number[][]; t0: number } = null;
	// drawn positions of landed marbles, eased toward their slots so a reflow glides
	const ANIM_MAX = 3000;
	const px = new Float32Array(ANIM_MAX),
		py = new Float32Array(ANIM_MAX),
		pr = new Float32Array(ANIM_MAX);
	let auto = $state(false),
		counted = $state(0),
		v = $state(0),
		tipOpen = $state(false);
	let canvas: HTMLCanvasElement | undefined = $state();
	/** The 20 counts get their own strip under the controls, only while they're shown. */
	let runsCanvas: HTMLCanvasElement | undefined = $state();
	// the put-back: marbles flying home, then the jar refills
	let returning: null | {
		t0: number;
		items: { x: number; y: number; r: number; cat: number }[];
		after?: () => void;
	} = null;
	let returningBigLeft = 0;
	let lastSlot = (i: number): [number, number, number] => [i, 0, 1],
		lastGroup = 1,
		busy = $state(false);
	let runHits: { x: number; y: number; w: number; h: number; j: number }[] = [];
	let byHand = 0, // marbles still to take by hand
		byHandNext = 0;
	let raf = 0,
		runT0 = 0,
		runFrom = 0,
		grain: HTMLCanvasElement | null = null,
		grainKey = '';
	const ui = () => v++;
	const kick = () => {
		if (!raf) raf = requestAnimationFrame(frame);
	};

	/**
	 * The pace: the first 20 marbles one by one, each gap 7% shorter than the last, then ten times
	 * as many every 1.5 s. `elapsed(k)` is when marble k leaves; `due(t)` inverts it.
	 */
	const SLOW = 20;
	const slowGap = (k: number) => 650 * Math.pow(0.93, k) * speed;
	const elapsed = (k: number) => {
		let s = 0;
		for (let i = 0; i < Math.min(k, SLOW); i++) s += slowGap(i);
		return k <= SLOW ? s : s + 1500 * speed * Math.log10(k / SLOW);
	};
	function due(t: number) {
		const slowEnd = elapsed(SLOW);
		if (t < slowEnd) {
			let s = 0,
				k = 0;
			while (k < SLOW && s <= t) s += slowGap(k++);
			return k;
		}
		return Math.floor(SLOW * Math.pow(10, (t - slowEnd) / (1500 * speed)));
	}
	const flight = (k: number) => Math.max(200, 600 * Math.pow(0.97, k)) * speed;

	function launch(now: number, fly: boolean) {
		const d = src.next();
		if (!d) return false;
		taken++;
		if (d.m >= 0) out[d.m] = 1;
		if (fly) {
			// it leaves from where it sat: its slot in the small jar, or the top of a big jar's fill
			const [sx, sy] = d.m >= 0 ? pile.pts[d.m] : bigTop();
			flying.push({ cat: d.cat, m: d.m, t0: now, dur: flight(taken), sx, sy });
		} else land(d.cat, now);
		return true;
	}
	function land(cat: number, now: number) {
		landed.push(cat);
		counts[cat]++;
		counted = landed.length;
		if (!multi) {
			trail.push({ pct: (counts[0] / counted) * 100, t: now });
			if (trail.length > 60) trail.shift();
		}
	}
	const cap = () => Math.min(target, S.N);

	/** Everything counted streams back into the jar, fast; then the count starts clean. */
	function putBack(after?: () => void) {
		auto = false;
		if (!landed.length && !flying.length) {
			reset();
			after?.();
			return;
		}
		const items: { x: number; y: number; r: number; cat: number }[] = [];
		const every = Math.max(1, Math.ceil(landed.length / 400));
		for (let i = 0; i < landed.length; i += every) {
			const [x, y, rr] =
				i < ANIM_MAX && lastGroup === 1 && pr[i]
					? [px[i], py[i], pr[i]]
					: lastSlot(Math.floor(i / lastGroup));
			items.push({ x, y, r: Math.max(1.2, rr), cat: landed[i] });
		}
		const keepOut = out.slice();
		returningBigLeft = bigLeft();
		reset();
		out.set(keepOut); // the jar stays emptied until the marbles are back in
		returning = { t0: performance.now(), items, after };
		busy = true;
		kick();
	}
	function reset() {
		auto = false;
		byHand = 0;
		src = source(stage, S.N, cats);
		taken = 0;
		out.fill(0);
		landed = [];
		flying = [];
		counts = cats.map(() => 0);
		shown = cats.map(() => 0);
		trail = [];
		pr.fill(0);
		counted = 0;
		ui();
		kick();
	}
	function toggleAuto() {
		if (!auto && counted >= cap()) {
			putBack(() => toggleAuto());
			return;
		}
		auto = !auto;
		// resume on the pace curve from where the count stands
		runT0 = performance.now() - elapsed(taken);
		runFrom = taken;
		kick();
	}
	/** By hand: one marble, or ten in quick succession. */
	function takeSome(k: number) {
		auto = false;
		byHand += k;
		byHandNext = Math.max(byHandNext, performance.now());
		kick();
	}
	function goStage(i: number) {
		stage = i;
		returning = null;
		busy = false;
		target = Math.min(target, stages[i].N);
		runs = null;
		tipOpen = false;
		reset();
	}
	function runTwenty() {
		hover = null;
		const n = cap();
		runs = {
			n,
			results: Array.from({ length: 20 }, () => sample(stage, n, S.N, cats)),
			t0: performance.now()
		};
		ui();
		kick();
	}
	const setTarget = (n: number) => {
		target = Math.min(clampN(n), S.N);
		runs = null;
		ui();
		kick();
	};

	// ---- the landing grid ----
	const MAX_CELLS = 12000;
	function gridFor(n: number, w: number, h: number) {
		const group = Math.max(1, Math.ceil(n / MAX_CELLS)),
			cells = Math.ceil(n / group);
		let best = { cols: 1, size: 0 };
		const guess = Math.ceil(Math.sqrt((cells * w) / h));
		for (let cols = Math.max(1, guess - 3); cols <= Math.min(cells, guess + 3); cols++) {
			const size = Math.min(w / cols, h / Math.ceil(cells / cols));
			if (size > best.size) best = { cols, size };
		}
		return { cols: best.cols, size: Math.min(22, best.size), group };
	}

	// A big jar is drawn as BIG_DOTS packed dots, each standing for N / BIG_DOTS marbles. Dots come
	// off the top at the true rate, so the fill drops by exactly the share taken out.
	const BIG_DOTS = 20000;
	const bigPts = (() => {
		const iw = JW - 8,
			ih = JH * 0.93 - 8,
			d = Math.sqrt(((iw * ih) / BIG_DOTS) * (2 / Math.sqrt(3))) * 0.98,
			pts = new Float32Array(BIG_DOTS * 2),
			rnd = seeded(3);
		let k = 0;
		for (let row = 0; k < BIG_DOTS; row++) {
			const y = JH - 4 - d / 2 - row * d * 0.866,
				off = row % 2 ? d / 2 : 0;
			for (let x = 4 + d / 2 + off; x <= JW - 4 - d / 2 && k < BIG_DOTS; x += d, k++) {
				pts[k * 2] = x + (rnd() - 0.5) * d * 0.5;
				pts[k * 2 + 1] = y + (rnd() - 0.5) * d * 0.5;
			}
		}
		return { pts, d };
	})();
	const bigLeft = () => BIG_DOTS - Math.floor((taken * BIG_DOTS) / S.N);
	const bigTop = (): [number, number] => {
		const k = Math.max(0, bigLeft() - 1);
		return [bigPts.pts[k * 2], bigPts.pts[k * 2 + 1]];
	};
	function drawBigJar(cols: string[], shares: number[], left: number) {
		const c = document.createElement('canvas'),
			m = 3;
		c.width = JW * m;
		c.height = JH * m;
		const g = c.getContext('2d')!;
		g.scale(m, m);
		const rnd = seeded(11),
			s = bigPts.d * 0.9;
		for (let i = 0; i < left; i++) {
			let u = rnd(),
				k = 0;
			while (k < shares.length - 1 && u >= shares[k]) u -= shares[k++];
			g.fillStyle = cols[k];
			g.fillRect(bigPts.pts[i * 2] - s / 2, bigPts.pts[i * 2 + 1] - s / 2, s, s);
		}
		return c;
	}

	function cross(g: CanvasRenderingContext2D, x: number, y: number, col: string) {
		g.strokeStyle = col;
		g.lineWidth = 2;
		g.beginPath();
		g.moveTo(x - 3.5, y - 3.5);
		g.lineTo(x + 3.5, y + 3.5);
		g.moveTo(x + 3.5, y - 3.5);
		g.lineTo(x - 3.5, y + 3.5);
		g.stroke();
	}

	/** Hover or tap one of the 20 counts to read it. */
	function pointAt(e: PointerEvent) {
		if (!runs || !runsCanvas) return (hover = null);
		const b = runsCanvas.getBoundingClientRect(),
			x = e.clientX - b.left,
			y = e.clientY - b.top;
		// of the boxes under the pointer, the one whose centre is nearest wins
		const hit = runHits
			.filter((h) => x >= h.x && x <= h.x + h.w && y >= h.y && y <= h.y + h.h)
			.sort(
				(a, b) =>
					Math.hypot(a.x + a.w / 2 - x, a.y + a.h / 2 - y) -
					Math.hypot(b.x + b.w / 2 - x, b.y + b.h / 2 - y)
			)[0];
		if (!hit) return (hover = null);
		const rn = runs.n,
			r = runs.results[hit.j],
			parts = cats.map((k, i) => {
				const pct = (r[i] / rn) * 100,
					off = pct - k.share * 100,
					m = moeP(k.share, rn, S.N);
				return { name: k.name, cnt: r[i], pct, off, miss: Math.abs(off) > m + 1e-9, m };
			});
		hover = { x, y: hit.y, j: hit.j, parts, n: rn };
	}
	type HoverPart = {
		name: string;
		cnt: number;
		pct: number;
		off: number;
		miss: boolean;
		m: number;
	};
	let hover = $state<null | { x: number; y: number; j: number; n: number; parts: HoverPart[] }>(
		null
	);

	function marker(
		g: CanvasRenderingContext2D,
		mx: number,
		y: number,
		col: string,
		label: string,
		ink: string,
		mono: string,
		x0: number,
		x1: number
	) {
		g.beginPath();
		g.moveTo(mx, y - 6);
		g.lineTo(mx - 7, y - 18);
		g.lineTo(mx + 7, y - 18);
		g.closePath();
		g.fillStyle = col;
		g.fill();
		if (label) {
			g.font = '600 13px ' + mono;
			g.textAlign = 'center';
			g.textBaseline = 'bottom';
			g.fillStyle = ink;
			g.fillText(label, Math.max(x0 + 12, Math.min(x1 - 12, mx)), y - 20);
		}
	}

	function frame(now: number) {
		raf = 0;
		const c = canvas;
		if (!c) return;
		if (auto) {
			const want = Math.min(cap(), Math.max(runFrom + 1, due(now - runT0)));
			const n = want - taken;
			// at speed most marbles land straight away; only the last couple each frame fly
			for (let i = 0; i < n; i++) if (!launch(now, i >= n - 2)) break;
			if (taken >= cap()) auto = false;
		}
		while (byHand > 0 && now >= byHandNext) {
			byHand--;
			byHandNext = now + 90 * speed;
			if (!launch(now, true)) byHand = 0;
		}
		while (flying.length > 40) land(flying.shift()!.cat, now);
		while (flying.length && now - flying[0].t0 >= flying[0].dur) land(flying.shift()!.cat, now);

		const colOf = cats.map((k) => tok(c, k.col));
		const ink = tok(c, '--ink'),
			muted = tok(c, '--muted'),
			line = tok(c, '--line'),
			glass = tok(c, '--glass'),
			pin = tok(c, '--pin'),
			surface = tok(c, '--surface'),
			mono = tok(c, '--mono'),
			sans = tok(c, '--sans');

		const bars = multi && multiDisplay === 'bars';
		const LINE_Y = TOP + JH + 56;
		// the 20 counts draw in their own strip under the controls, so nothing is reserved here
		const runsH = multi ? 20 * 8 + 24 : 116;
		const { g, w } = fit(c, LINE_Y + (bars ? 34 : 46));
		let moving = false;

		// ---- the jar, on the right ----
		const jx = w - JW - 4;
		g.fillStyle = glass;
		jarPath(g, jx, TOP, JW, JH);
		g.fill();
		if (stage === 0) {
			for (let m = 0; m < 1000; m++)
				if (!out[m])
					circle(g, jx + pile.pts[m][0], TOP + pile.pts[m][1], pile.r, colOf[smallJar[m]]);
		} else {
			const left = returning ? returningBigLeft : bigLeft(),
				key = stage + colOf.join() + left;
			if (!grain || grainKey !== key) {
				grain = drawBigJar(
					colOf,
					cats.map((k) => k.share),
					left
				);
				grainKey = key;
			}
			g.drawImage(grain, jx, TOP, JW, JH);
		}
		g.strokeStyle = line;
		g.lineWidth = 1.5;
		jarPath(g, jx, TOP, JW, JH);
		g.stroke();
		g.fillStyle = muted;
		g.font = '12px ' + mono;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		g.fillText(`${fmt(S.N - taken)} left`, jx + JW / 2, TOP + JH + 6);

		// ---- where they land, on the left: sized for the planned sample from the start ----
		const lw = jx - 16,
			lh = JH * 0.93,
			ly = TOP + JH * 0.07,
			{ cols, size, group } = gridFor(Math.max(cap(), landed.length + flying.length), lw, lh),
			slot = (i: number): [number, number, number] => [
				2 + ((i % cols) + 0.5) * size,
				ly + lh - (Math.floor(i / cols) + 0.5) * size,
				Math.max(0.6, size / 2 - (size > 4 ? 0.6 : 0.1))
			];
		g.fillStyle = glass;
		g.globalAlpha = 0.5;
		g.beginPath();
		g.roundRect(0, ly - 4, lw + 4, lh + 8, 8);
		g.fill();
		g.globalAlpha = 1;
		const cellsN = Math.ceil(landed.length / group);
		const dot = (x: number, y: number, r: number, col: string) => {
			if (r * 2 < 3) {
				g.fillStyle = col;
				g.fillRect(x - r, y - r, Math.max(1, r * 2), Math.max(1, r * 2));
			} else circle(g, x, y, r, col);
		};
		for (let i = 0; i < cellsN; i++) {
			const [tx, ty, tr] = slot(i),
				col = colOf[landed[i * group]];
			if (i < ANIM_MAX && group === 1) {
				// a new marble appears at its slot; an old one glides there when the grid reflows
				if (pr[i] === 0) [px[i], py[i], pr[i]] = [tx, ty, tr];
				px[i] += (tx - px[i]) * 0.15;
				py[i] += (ty - py[i]) * 0.15;
				pr[i] += (tr - pr[i]) * 0.15;
				if (Math.abs(tx - px[i]) + Math.abs(ty - py[i]) + Math.abs(tr - pr[i]) > 0.15)
					moving = true;
				else [px[i], py[i], pr[i]] = [tx, ty, tr];
				dot(px[i], py[i], pr[i], col);
			} else dot(tx, ty, tr, col);
		}
		if (!landed.length && !flying.length && !returning) {
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
		g.fillText(
			`${fmt(landed.length)} counted${group > 1 ? ` · 1 dot = ${fmt(group)}` : ''}`,
			lw / 2,
			TOP + JH + 6
		);

		lastSlot = slot;
		lastGroup = group;

		// the put-back: every marble races to the mouth in under half a second
		if (returning) {
			const RET = 260 * speed,
				SPREAD = 200 * speed,
				ret = returning,
				len = ret.items.length,
				mx = jx + JW / 2,
				my = TOP - 4;
			let left = 0;
			ret.items.forEach((it, i) => {
				const p = (now - ret.t0 - (SPREAD * i) / len) / RET;
				if (p >= 1) return;
				left++;
				if (p < 0) return dot(it.x, it.y, it.r, colOf[it.cat]);
				const e = p * p;
				circle(
					g,
					it.x + (mx - it.x) * e,
					it.y + (my - it.y) * e - Math.sin(Math.PI * p) * 18,
					it.r * (1 - 0.4 * p),
					colOf[it.cat]
				);
			});
			if (left) moving = true;
			else {
				returning = null;
				out.fill(0);
				busy = false;
				moving = true;
				ret.after?.();
			}
		}

		// marbles in the air: up from where they sat, out of the mouth, then an arc to the left
		flying.forEach((f, j) => {
			const p = Math.min(1, (now - f.t0) / f.dur),
				[tx, ty, tr] = slot(Math.floor((landed.length + j) / group)),
				mx = jx + JW / 2,
				my = TOP - 6,
				r0 = stage === 0 ? pile.r : 1.5,
				r = r0 + (Math.max(tr, 1.5) - r0) * p + (stage === 0 ? 1 : 0.8);
			if (p < 0.3) {
				// rising out of the pile to the mouth
				const q = 1 - Math.pow(1 - p / 0.3, 2);
				circle(
					g,
					jx + f.sx + (mx - jx - f.sx) * q,
					TOP + f.sy + (my - TOP - f.sy) * q,
					r,
					colOf[f.cat]
				);
			} else {
				const q = (p - 0.3) / 0.7;
				circle(
					g,
					mx + (tx - mx) * q,
					my + (ty - my) * q * q - Math.sin(Math.PI * q) * 26,
					r,
					colOf[f.cat]
				);
			}
		});

		// ---- the shares ----
		const x0 = 14,
			x1 = w - 14,
			X = (val: number) => x0 + ((x1 - x0) * val) / 100;
		const n = counted;
		for (let k = 0; k < cats.length; k++) {
			const t = n ? (counts[k] / n) * 100 : cats[k].share * 100;
			shown[k] = n && shown[k] ? shown[k] + (t - shown[k]) * 0.25 : t;
			if (Math.abs(t - shown[k]) < 0.05) shown[k] = t;
			else moving = true;
		}
		const moes = cats.map((k) => moeP(k.share, cap(), S.N));

		if (!bars) {
			// the track, 0% to 100%
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
			if (!multi) {
				// the 95% band around the truth for this sample size, down through the 20 runs
				const tv = cats[0].share * 100,
					m = moes[0];
				g.fillStyle = colOf[0];
				g.globalAlpha = 0.18;
				g.fillRect(X(tv - m), LINE_Y - 9, Math.max(2, X(tv + m) - X(tv - m)), 18);
				g.globalAlpha = 1;
				g.strokeStyle = ink;
				g.lineWidth = 2;
				g.beginPath();
				g.moveTo(X(tv), LINE_Y - 12);
				g.lineTo(X(tv), LINE_Y + 12);
				g.stroke();
				for (const t of trail) {
					const age = (now - t.t) / (2500 * speed);
					if (age >= 1) continue;
					moving = true;
					g.globalAlpha = 0.5 * (1 - age);
					g.fillStyle = ink;
					g.fillRect(X(t.pct) - 1, LINE_Y - 5, 2, 10);
				}
				g.globalAlpha = 1;
				g.fillStyle = ink;
				g.font = '600 11px ' + sans;
				g.textAlign = 'center';
				g.textBaseline = 'top';
				g.fillText(`true ${Math.round(tv)}%`, X(tv), LINE_Y + 30);
				if (n)
					marker(g, X(shown[0]), LINE_Y, colOf[0], `${shown[0].toFixed(0)}%`, ink, mono, x0, x1);
			} else {
				// one true tick and one marker per colour
				cats.forEach((k, i) => {
					g.strokeStyle = colOf[i];
					g.lineWidth = 3;
					g.beginPath();
					g.moveTo(X(k.share * 100), LINE_Y - 3);
					g.lineTo(X(k.share * 100), LINE_Y + 12);
					g.stroke();
					if (n) marker(g, X(shown[i]), LINE_Y, colOf[i], '', ink, mono, x0, x1);
				});
			}
		} else {
			// two stacked bars: the jar's mix, and the count's mix sliding toward it
			const bar = (y: number, shares: number[] | null, label: string) => {
				g.fillStyle = muted;
				g.font = '600 11px ' + sans;
				g.textAlign = 'left';
				g.textBaseline = 'bottom';
				g.fillText(label, x0, y - 3);
				if (!shares) {
					g.fillStyle = line;
					g.fillRect(x0, y, x1 - x0, 16);
					return;
				}
				let acc = 0;
				shares.forEach((s, i) => {
					g.fillStyle = colOf[i];
					g.fillRect(X(acc), y, X(acc + s) - X(acc), 16);
					if (X(acc + s) - X(acc) > 26) {
						g.fillStyle = surface;
						g.font = '600 10px ' + mono;
						g.textAlign = 'center';
						g.textBaseline = 'middle';
						g.fillText(s.toFixed(0) + '%', (X(acc) + X(acc + s)) / 2, y + 8.5);
					}
					acc += s;
				});
			};
			const jarY = LINE_Y - 30,
				cntY = LINE_Y + 12;
			bar(
				jarY,
				cats.map((k) => k.share * 100),
				'In the jar'
			);
			bar(cntY, n ? shown : null, 'Your count');
			// guides at the jar's boundaries, down through the count
			g.strokeStyle = ink;
			g.setLineDash([2, 2]);
			g.lineWidth = 1;
			let acc = 0;
			for (let i = 0; i < cats.length - 1; i++) {
				acc += cats[i].share * 100;
				g.beginPath();
				g.moveTo(Math.round(X(acc)) + 0.5, jarY);
				g.lineTo(Math.round(X(acc)) + 0.5, cntY + 16);
				g.stroke();
			}
			g.setLineDash([]);
		}

		// ---- 20 counts at once, the misses ringed ----
		runHits = [];
		if (runs && runsCanvas) {
			// same width as the main canvas, so X() lines up with the share line above
			const { g } = fit(runsCanvas, runsH + 4),
				runsTop = 0;
			if (!multi) {
				const tv = cats[0].share * 100,
					m = moeP(cats[0].share, runs.n, S.N);
				g.fillStyle = colOf[0];
				g.globalAlpha = 0.18;
				g.fillRect(X(tv - m), runsTop + 12, Math.max(2, X(tv + m) - X(tv - m)), runsH - 16);
				g.globalAlpha = 1;
				g.strokeStyle = ink;
				g.lineWidth = 1;
				g.setLineDash([2, 2]);
				g.beginPath();
				g.moveTo(Math.round(X(tv)) + 0.5, runsTop + 12);
				g.lineTo(Math.round(X(tv)) + 0.5, runsTop + runsH - 4);
				g.stroke();
				g.setLineDash([]);
			} else {
				g.strokeStyle = ink;
				g.setLineDash([2, 2]);
				g.lineWidth = 1;
				let acc = 0;
				for (let i = 0; i < cats.length - 1; i++) {
					acc += cats[i].share * 100;
					g.beginPath();
					g.moveTo(Math.round(X(acc)) + 0.5, runsTop + 12);
					g.lineTo(Math.round(X(acc)) + 0.5, runsTop + runsH);
					g.stroke();
				}
				g.setLineDash([]);
			}
			const shownRuns = Math.min(20, Math.floor((now - runs.t0) / (110 * speed)) + 1);
			if (shownRuns < 20) moving = true;
			const rn = runs.n,
				res = runs.results.slice(0, shownRuns),
				rm = cats.map((k) => moeP(k.share, rn, S.N));
			g.fillStyle = muted;
			g.font = '600 11px ' + sans;
			g.textAlign = 'left';
			g.textBaseline = 'top';
			g.fillText(`20 counts of ${fmt(rn)}`, x0, runsTop);
			if (!multi) {
				// each dot sits at its exact value (rounding could push one across the band's edge) and
				// stacks on any dot it would overlap; the band runs down behind them
				const placed: { x: number; k: number }[] = [],
					missDots: [number, number][] = [];
				res.forEach((r) => {
					const pct = (r[0] / rn) * 100,
						miss = Math.abs(pct - cats[0].share * 100) > rm[0] + 1e-9,
						bx = X(pct),
						k =
							placed.filter((q) => Math.abs(q.x - bx) < 8).reduce((m, q) => Math.max(m, q.k), 0) +
							1,
						y = runsTop + runsH - 12 - (k - 1) * 10;
					placed.push({ x: bx, k });
					runHits.push({ x: bx - 8, y: y - 8, w: 16, h: 16, j: res.indexOf(r) });
					if (!miss) circle(g, bx, y, 3.4, pin, 0.7);
					else missDots.push([bx, y]);
				});
				// misses go on top, so an in-range dot can never cover one
				missDots.forEach(([bx, y]) => {
					// a miss: solid, ringed, and flagged with a cross above the stack
					circle(g, bx, y, 4.6, ink);
					g.strokeStyle = ink;
					g.lineWidth = 2;
					g.beginPath();
					g.arc(bx, y, 8, 0, 7);
					g.stroke();
					cross(g, bx, runsTop + 14, ink);
				});
			} else {
				// one thin bar per count; each colour is judged on its own range, and a share that
				// lands outside it is drawn solid and outlined
				res.forEach((r, j) => {
					const y = runsTop + 16 + j * 8,
						misses = r.map(
							(cnt, i) => Math.abs((cnt / rn) * 100 - cats[i].share * 100) > rm[i] + 1e-9
						),
						anyMiss = misses.some(Boolean);
					runHits.push({ x: x0, y: y - 1, w: x1 - x0 + 14, h: 8, j });
					// rows that got every colour right fade back; a row with a miss stays solid
					let acc = 0;
					g.globalAlpha = anyMiss ? 1 : 0.35;
					r.forEach((cnt, i) => {
						const s = (cnt / rn) * 100;
						g.fillStyle = colOf[i];
						g.fillRect(X(acc), y, X(acc + s) - X(acc), 6);
						acc += s;
					});
					g.globalAlpha = 1;
					acc = 0;
					r.forEach((cnt, i) => {
						const s = (cnt / rn) * 100;
						if (misses[i]) {
							g.strokeStyle = ink;
							g.lineWidth = 2;
							g.strokeRect(X(acc) - 1, y - 1.5, X(acc + s) - X(acc) + 2, 9);
						}
						acc += s;
					});
					if (anyMiss) cross(g, x1 + 7, y + 3, ink);
				});
			}
		}

		if (auto || byHand || flying.length || moving) kick();
		else ui();
	}

	// ---- text ----
	const info = $derived.by(() => {
		void v;
		const n = Math.min(target, S.N),
			moes = cats.map((k) => moeP(k.share, n, S.N)),
			shares = cats.map((_, i) => (counted ? ((counts[i] ?? 0) / counted) * 100 : 0)),
			off = cats.map((k, i) => Math.abs(shares[i] - k.share * 100));
		let runText = '';
		if (runs) {
			const rn = runs.n,
				rm = cats.map((k) => moeP(k.share, rn, S.N));
			// in stage 3 every colour of every count is judged on its own 95% range; with two
			// colours a miss on one is a miss on the other, so only the first is judged
			const judged = multi ? cats.length : 1;
			const misses = runs.results
				.flatMap((r) =>
					r
						.slice(0, judged)
						.map((cnt, i) => Math.abs((cnt / rn) * 100 - cats[i].share * 100) > rm[i] + 1e-9)
				)
				.filter(Boolean).length;
			const total = 20 * cats.length;
			runText =
				rm[0] === 0
					? `Every count of ${fmt(rn)} is the whole jar, so all 20 land exactly on the truth.`
					: !multi
						? `${20 - misses} of 20 landed inside the range, and ${misses === 0 ? 'none' : misses} missed${misses ? ' (ringed)' : ''}. Expect about 1 in 20 to miss.`
						: `20 counts × ${cats.length} colours = ${total} shares. ${total - misses} landed inside their range, and ${misses === 0 ? 'none' : misses} missed${misses ? ' (outlined)' : ''}. Expect about 1 in 20 to miss, so about ${Math.round(total / 20)} here.`;
		}
		return { n, moes, shares, off, runText, whole: n >= S.N };
	});

	onMount(() => {
		reset();
		for (let i = 0; i < Math.min(startWith, cap()); i++) launch(performance.now(), false);
		if (startRuns) runTwenty();
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
		void multiDisplay;
		kick();
	});
</script>

<div class="widget" class:multi>
	{#if !onStep}
		<div class="steps" role="tablist" aria-label="Stages">
			{#each stages as s, i (i)}
				<button
					class="stepbtn"
					class:on={i <= stage}
					role="tab"
					aria-selected={i === stage}
					aria-label="Stage {i + 1}: {s.t}"
					onclick={() => goStage(i)}
				></button>
			{/each}
		</div>
	{/if}
	<div class="eyebrow">Step {stage + 1} of 3</div>
	<h2>{S.t}</h2>
	<p class="lede">{S.lede}</p>
	<div class="canvas-wrap">
		<canvas
			bind:this={canvas}
			aria-label="A jar on the right, the marbles counted so far on the left, and the share of each colour so far against the true mix"
		></canvas>
	</div>
	<div class="tally tally-box" aria-live="polite">
		{#if counted}
			<b class="num">{fmt(counted)}</b> counted:
			{#each cats as k, i (i)}
				<span class="chip" style:--c="var({k.col})"></span><b class="num"
					>{info.shares[i].toFixed(1)}%</b
				>
				{k.name}{i < cats.length - 1 ? ', ' : '.'}
			{/each}
		{:else}
			Nothing counted yet.
		{/if}
	</div>

	<div class="size">
		<div class="row nowrap-row" role="group" aria-label="Sample size">
			<label class="eyebrow" for="conv-n">Sample size</label>
			<input
				id="conv-n"
				type="number"
				min="1"
				max={S.N}
				inputmode="numeric"
				value={target}
				onchange={(e) => setTarget(Number(e.currentTarget.value))}
			/>
			<button
				class="info"
				aria-expanded={tipOpen}
				aria-label="What to expect"
				onclick={() => (tipOpen = !tipOpen)}>i</button
			>
		</div>
		{#if tipOpen}
			<!-- floats over the page, so opening it moves nothing -->
			<div class="tip" role="note">
				<button class="tip-x" aria-label="Close" onclick={() => (tipOpen = false)}>×</button>
				{#if info.whole}
					{fmt(info.n)} is every marble in the jar, so your count will be exactly right, every time.
				{:else if !multi}
					With {fmt(info.n)} marbles, 95% of counts land within
					<b>±{fmtPts(info.moes[0])} points</b>
					of the true {Math.round(cats[0].share * 100)}%. That’s the shaded band on the line.
					Pollsters call it the <strong>margin of error</strong>.
				{:else}
					With {fmt(info.n)} marbles, 95% of counts get each colour within:
					{#each cats as k, i (i)}
						<span class="nowrap"
							><span class="chip" style:--c="var({k.col})"></span>{k.name}
							<b>±{fmtPts(info.moes[i])}</b></span
						>{i < cats.length - 1 ? ', ' : '.'}
					{/each}
					Smaller shares wobble less in points.
				{/if}
			</div>
		{/if}
		<div class="row presets">
			{#each stage === 0 ? [10, 100, 1000] : [10, 100, 1000, 10000] as p (p)}
				<button aria-pressed={target === p} onclick={() => setTarget(p)}>{fmt(p)}</button>
			{/each}
		</div>
		<div class="small">That’s {pctOf(info.n, S.N)} of the jar.</div>
	</div>

	<!-- fixed cells: labels can change (Start, Pause, Again) without moving anything -->
	<div class="controls">
		<div class="group">
			<span class="eyebrow">Count for me</span>
			<button class="primary wide" onclick={toggleAuto} disabled={busy}>
				{auto ? 'Pause' : counted >= info.n ? 'Again' : counted ? 'Keep going' : 'Start'}
			</button>
		</div>
		<div class="group">
			<span class="eyebrow">By hand</span>
			<div class="pair">
				<button onclick={() => takeSome(1)} disabled={auto || busy || counted >= S.N}>Take 1</button
				>
				<button onclick={() => takeSome(10)} disabled={auto || busy || counted >= S.N}
					>Take 10</button
				>
			</div>
		</div>
		<button class="wide" onclick={() => putBack()} disabled={busy || (!counted && !auto)}
			>Put them back</button
		>
		<button class="wide" onclick={runTwenty}>Run 20 counts</button>
	</div>
	{#if info.runText}
		<!-- appears only after "Run 20 counts", under the controls, so nothing above it moves -->
		<div class="canvas-wrap">
			<canvas
				onpointermove={pointAt}
				onpointerdown={pointAt}
				onpointerleave={(e) => e.pointerType === 'mouse' && (hover = null)}
				bind:this={runsCanvas}
				aria-label="Twenty counts of the same size, each at the share it found, with the misses ringed"
			></canvas>
			{#if hover}
				{@const h = hover}
				<div class="count-tip" style:left="{h.x}px" style:top="{h.y}px" role="status">
					<b>Count {h.j + 1}</b> · {fmt(h.n)} marbles
					{#each multi ? h.parts : h.parts.slice(0, 1) as p (p.name)}
						<div class:missed={p.miss}>
							{fmt(p.cnt)}
							{p.name} = <b>{p.pct.toFixed(1)}%</b>,
							{Math.abs(p.off).toFixed(1)} points off{p.miss
								? ` — outside ±${fmtPts(p.m)}: missed`
								: ''}
						</div>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
	<div class="message">
		{#if info.runText}
			<div class="moe">{info.runText}</div>
		{:else if counted >= S.N}
			<div class="moe">You counted every marble, so your count is exactly right.</div>
		{:else if counted >= info.n && counted >= 10}
			<div class="moe">
				After {fmt(counted)} marbles ({pctOf(counted, S.N)} of the jar),
				{#if multi}
					every colour is within <b>{Math.max(...info.off).toFixed(1)} points</b> of the truth.
				{:else}
					your count is <b>{info.off[0].toFixed(1)} points</b> from the truth.
				{/if}
			</div>
		{/if}
	</div>
	<div class="stepnav">
		<button disabled={stage === 0} onclick={() => (onStep ? onStep(-1) : goStage(stage - 1))}
			>Back</button
		>
		<button
			class="primary"
			disabled={stage === 2 && !onStep}
			onclick={() => (onStep ? onStep(1) : goStage(stage + 1))}>Next step</button
		>
	</div>
</div>

<style>
	.steps {
		display: flex;
		gap: 6px;
	}
	.stepbtn {
		flex: 1;
		height: 18px;
		padding: 7px 0;
		border: 0;
		border-radius: 0;
		background: transparent;
		position: relative;
	}
	.stepbtn::after {
		content: '';
		position: absolute;
		left: 0;
		right: 0;
		top: 7px;
		height: 4px;
		border-radius: 2px;
		background: var(--line);
	}
	.stepbtn.on::after {
		background: var(--ink);
	}
	.stepnav {
		display: flex;
		justify-content: space-between;
		gap: 8px;
	}
	.size {
		position: relative;
		display: flex;
		flex-direction: column;
		gap: 8px;
	}
	.nowrap-row {
		flex-wrap: nowrap;
	}
	.tally-box {
		min-height: 4.3em !important;
	}
	.canvas-wrap {
		position: relative;
	}
	.count-tip {
		position: absolute;
		transform: translate(-50%, calc(-100% - 8px));
		max-width: 260px;
		width: max-content;
		background: var(--ink);
		color: var(--surface);
		border-radius: 8px;
		padding: 7px 10px;
		font-size: 13px;
		line-height: 1.4;
		pointer-events: none;
		z-index: 3;
		box-shadow: 0 6px 20px rgb(0 0 0 / 0.25);
	}
	.count-tip .missed {
		font-weight: 600;
		text-decoration: underline;
	}
	.tip {
		position: absolute;
		top: 44px;
		left: 0;
		right: 0;
		z-index: 2;
		box-shadow: 0 6px 20px rgb(0 0 0 / 0.25);
		padding-right: 34px;
	}
	.tip-x {
		position: absolute;
		top: 4px;
		right: 4px;
		width: 28px;
		height: 28px;
		padding: 0;
		background: transparent;
		border: 0;
		color: var(--surface);
		font-size: 18px;
	}
	.controls {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 10px;
		align-items: end;
	}
	.group {
		display: flex;
		flex-direction: column;
		gap: 4px;
		min-width: 0;
	}
	.wide {
		width: 100%;
	}
	.pair {
		display: grid;
		grid-template-columns: 1fr 1fr;
	}
	.pair button:first-child {
		border-radius: 999px 0 0 999px;
		border-right-width: 0;
	}
	.pair button:last-child {
		border-radius: 0 999px 999px 0;
	}
	.message {
		min-height: 6em;
	}
	.info {
		width: 30px;
		height: 30px;
		padding: 0;
		font: italic 600 15px var(--serif);
	}
	.tip {
		background: var(--ink);
		color: var(--surface);
		border-radius: 8px;
		padding: 10px 12px;
		font-size: 14px;
		line-height: 1.45;
	}
	.tip b {
		font-family: var(--mono);
	}
	.chip {
		display: inline-block;
		width: 9px;
		height: 9px;
		border-radius: 50%;
		background: var(--c);
		margin: 0 3px 0 2px;
	}
	.nowrap {
		white-space: nowrap;
	}
</style>
