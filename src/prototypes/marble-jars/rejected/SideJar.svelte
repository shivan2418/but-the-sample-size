<script lang="ts">
	// PROTOTYPE, throwaway. Variant D rebuilt: tactile to abstract, with the jar upright at the side
	// and marbles taken out sideways into a tray next to it. Timings are about half of round 2's.
	import { onMount } from 'svelte';
	import {
		BIG,
		P,
		SMALL,
		axis as drawAxis,
		circle,
		clampN,
		dots,
		drawBig,
		drawSmall,
		ease,
		fit,
		fmt,
		fmtMoe,
		jar,
		jarPath,
		moe,
		palettes,
		pctOf,
		seeded,
		shuffle,
		tok,
		trueLine,
		within,
		type PaletteKey
	} from '../model';

	let {
		startStep = 0,
		speed = 1,
		axisRange = 'full',
		palette = 'redBlue'
	}: {
		startStep?: number;
		/** Multiplies every duration: 2 = twice as slow. */
		speed?: number;
		axisRange?: 'full' | 'zoomed';
		palette?: PaletteKey;
	} = $props();

	const A = $derived(palettes[palette].a.name);
	const B = $derived(palettes[palette].b.name);

	// ---- geometry (CSS px) ----
	const PAD = 6,
		TOP = 4,
		JW = 120,
		JH = 190,
		COLW = PAD + JW * 1.1 + 12,
		PLOT_Y = TOP + JH + 46,
		LANE = 34,
		LANES = 4,
		H = PLOT_Y + LANES * LANE + 26;
	const B1 = { x: PAD, y: TOP, w: JW, h: JH };
	const S1 = { x: PAD + JW + 4, y: TOP + JH * 0.9, w: JW / 10, h: JH / 10 };

	// the small jar's pile, in world units relative to S1 at full (s = 10) scale
	const pile = (() => {
		const iw = JW - 12,
			ih = JH * 0.93 - 10,
			d = Math.sqrt(((iw * ih) / SMALL) * (2 / Math.sqrt(3))) * 0.97,
			r0 = d / 2,
			pts: [number, number][] = [],
			rnd = seeded(5);
		for (let row = 0; pts.length < SMALL; row++) {
			const y = JH - 5 - r0 - row * d * 0.866,
				off = row % 2 ? d / 2 : 0;
			for (let x = 6 + r0 + off; x <= JW - 6 - r0 && pts.length < SMALL; x += d)
				pts.push([x + (rnd() - 0.5) * 0.8, y + (rnd() - 0.5) * 0.8]);
		}
		return { pts, r: r0 - 0.35 };
	})();
	const rank = (() => {
		const order = Array.from({ length: SMALL }, (_, i) => i).sort(
				(a, b) => jar[b] - jar[a] || a - b
			),
			r = new Array<number>(SMALL);
		order.forEach((m, pos) => (r[m] = pos));
		return r;
	})();

	type Lane = { jar: 'small' | 'big'; n: number; vals: number[]; pending: Record<number, number> };
	type Anim = {
		t0: number;
		dur: number;
		started: boolean;
		start?: () => void;
		step?: (p: number) => void;
		draw?: (g: CanvasRenderingContext2D, p: number) => void;
		done?: () => void;
	};

	// engine state, mutated by animations; `v` bumps whenever the DOM text should refresh
	const st = {
		s: 10,
		sortE: 0,
		lanes: [] as Lane[],
		tray: [] as { c: number; slot: number }[],
		trayN: 10,
		trayA: 1,
		bar: null as null | { n: number; got: number; red: number },
		out: new Uint8Array(SMALL),
		wasOut: new Uint8Array(SMALL),
		refill: 1,
		W: 320
	};
	let step = $state(0),
		busy = $state(false),
		revealed = $state(false),
		n = $state(100),
		tally = $state<null | { jar: 'small' | 'big'; n: number; got: number; red: number }>(null),
		v = $state(0);
	const ui = () => v++;

	let canvas: HTMLCanvasElement | undefined = $state();
	let anims: Anim[] = [],
		raf = 0,
		grain: HTMLCanvasElement | null = null,
		grainKey = '';

	const reduce =
		typeof matchMedia !== 'undefined' && matchMedia('(prefers-reduced-motion: reduce)').matches;
	const k = () => (reduce ? 0.05 : speed);
	const kick = () => {
		if (!raf) raf = requestAnimationFrame(frame);
	};
	const anim = (delay: number, dur: number, a: Omit<Anim, 't0' | 'dur' | 'started'>) => {
		anims.push({
			...a,
			t0: performance.now() + delay * k(),
			dur: Math.max(1, dur * k()),
			started: false
		});
		kick();
	};

	const ax = $derived(
		axisRange === 'zoomed'
			? { lo: 30, hi: 80, bin: 1, ticks: [30, 40, 50, 60, 70, 80] }
			: { lo: 0, hi: 100, bin: 2, ticks: [0, 25, 50, 75, 100] }
	);

	function cam() {
		const kk = (st.s - 1) / 9;
		return { s: st.s, tx: (PAD - 10 * S1.x) * kk, ty: (TOP - 10 * S1.y) * kk };
	}
	const scr = (wx: number, wy: number): [number, number] => {
		const c = cam();
		return [wx * c.s + c.tx, wy * c.s + c.ty];
	};
	const marbleWorld = (i: number): [number, number] => {
		const a = pile.pts[i],
			b = pile.pts[rank[i]],
			e = st.sortE;
		return [S1.x + (a[0] + (b[0] - a[0]) * e) / 10, S1.y + (a[1] + (b[1] - a[1]) * e) / 10];
	};
	const mouth = (which: 'small' | 'big') => {
		const R = which === 'big' ? B1 : S1;
		return scr(R.x + R.w / 2, R.y);
	};
	function trayLayout(count: number) {
		const tx = COLW + 4,
			tw = st.W - PAD - tx,
			ty = TOP + JH * 0.07,
			th = JH * 0.93,
			cols = count <= 10 ? 5 : 10,
			rows = count <= 10 ? 2 : Math.ceil(Math.min(count, 100) / cols),
			size = count <= 10 ? Math.min(30, tw / 5) : Math.min(15, tw / 10, th / 10),
			gx = tx + (tw - cols * size) / 2,
			gy = ty + th - rows * size - 8;
		return {
			tx,
			tw,
			ty,
			th,
			slot: (i: number): [number, number, number] => {
				// fills bottom-up, like marbles settling
				const row = rows - 1 - Math.floor(i / cols);
				return [gx + ((i % cols) + 0.5) * size, gy + (row + 0.5) * size, size / 2 - 1.2];
			}
		};
	}
	const plotX = (x: number) => {
		const x0 = 72,
			x1 = st.W - 14;
		return x0 + ((x1 - x0) * (x - ax.lo)) / (ax.hi - ax.lo);
	};
	const dotR = () => Math.max(1.8, (plotX(ax.lo + ax.bin) - plotX(ax.lo)) / 2 - 0.3);
	const shownLanes = () => st.lanes.slice(-LANES);
	function laneFor(which: 'small' | 'big', size: number) {
		let l = st.lanes.find((l) => l.jar === which && l.n === size);
		if (!l) st.lanes.push((l = { jar: which, n: size, vals: [], pending: {} }));
		return l;
	}
	function dotTarget(l: Lane, value: number) {
		const i = shownLanes().indexOf(l),
			r = dotR(),
			b = Math.round((value - P * 100) / ax.bin);
		const kk =
			l.vals.filter((u) => Math.round((u - P * 100) / ax.bin) === b).length + (l.pending[b] ?? 0);
		l.pending[b] = (l.pending[b] ?? 0) + 1;
		const xv = Math.max(ax.lo, Math.min(ax.hi, P * 100 + b * ax.bin));
		return {
			b,
			xy: [plotX(xv), PLOT_Y + (i + 1) * LANE - 4 - (r + 1 + kk * (2 * r + 0.6))] as [
				number,
				number
			]
		};
	}

	function makeGrain(a: string, b: string) {
		const c = document.createElement('canvas'),
			m = 3;
		c.width = JW * m;
		c.height = JH * m;
		const g = c.getContext('2d')!;
		g.scale(m, m);
		g.beginPath();
		g.roundRect(3, JH * 0.07 + 3, JW - 6, JH * 0.93 - 6, JW * 0.08);
		g.clip();
		const rnd = seeded(9);
		for (let i = 0; i < 70000; i++) {
			g.fillStyle = rnd() < P ? a : b;
			g.fillRect(rnd() * JW, JH * 0.07 + 8 + rnd() * JH * 0.93, 0.55, 0.55);
		}
		return c;
	}

	function frame(now: number) {
		raf = 0;
		const c = canvas;
		if (!c) return;
		const live: [Anim, number][] = [];
		for (const a of anims.slice()) {
			const p = (now - a.t0) / a.dur;
			if (p < 0) continue;
			if (!a.started) {
				a.started = true;
				a.start?.();
			}
			if (p >= 1) {
				a.step?.(1);
				anims.splice(anims.indexOf(a), 1);
				a.done?.();
			} else {
				a.step?.(p);
				if (a.draw) live.push([a, p]);
			}
		}
		const showPlot = step > 0 || st.lanes.length > 0;
		const { g, w, dpr } = fit(c, showPlot ? H : TOP + JH + 26);
		st.W = w;
		const colA = tok(c, '--a'),
			colB = tok(c, '--b'),
			line = tok(c, '--line'),
			glass = tok(c, '--glass'),
			muted = tok(c, '--muted'),
			ink = tok(c, '--ink'),
			mono = tok(c, '--mono'),
			sans = tok(c, '--sans');

		// jars, under the camera
		const cm = cam();
		g.save();
		g.beginPath();
		g.rect(0, 0, COLW, TOP + JH + 2);
		g.clip();
		g.setTransform(dpr * cm.s, 0, 0, dpr * cm.s, dpr * cm.tx, dpr * cm.ty);
		const lw = 1.5 / cm.s;
		if (st.s < 9.99) {
			const key = colA + colB;
			if (!grain || grainKey !== key) {
				grain = makeGrain(colA, colB);
				grainKey = key;
			}
			g.fillStyle = glass;
			jarPath(g, B1.x, B1.y, B1.w, B1.h);
			g.fill();
			g.drawImage(grain, B1.x, B1.y, B1.w, B1.h);
			g.strokeStyle = line;
			g.lineWidth = lw;
			jarPath(g, B1.x, B1.y, B1.w, B1.h);
			g.stroke();
		}
		g.fillStyle = glass;
		jarPath(g, S1.x, S1.y, S1.w, S1.h);
		g.fill();
		g.strokeStyle = line;
		g.lineWidth = lw;
		jarPath(g, S1.x, S1.y, S1.w, S1.h);
		g.stroke();
		for (let i = 0; i < SMALL; i++) {
			if (st.out[i]) continue;
			const [x, y] = marbleWorld(i);
			circle(g, x, y, pile.r / 10, jar[i] ? colA : colB, st.wasOut[i] ? st.refill : 1);
		}
		g.restore();
		g.setTransform(dpr, 0, 0, dpr, 0, 0);

		// jar labels
		g.fillStyle = muted;
		g.font = '12px ' + mono;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		if (st.s > 9.9) g.fillText('1,000 marbles', PAD + JW / 2, TOP + JH + 6);
		else {
			g.globalAlpha = Math.min(1, (9.9 - st.s) / 4);
			g.textAlign = 'left';
			g.fillText('1,000,000', PAD, TOP + JH + 6);
			g.textAlign = 'right';
			g.fillText('1,000 ↑', COLW, TOP + JH + 6);
			g.globalAlpha = 1;
		}

		// tray, to the side
		const T = trayLayout(st.trayN);
		g.fillStyle = glass;
		g.beginPath();
		g.roundRect(T.tx, T.ty, T.tw, T.th, 10);
		g.fill();
		if (st.bar) {
			const bh = T.th - 32,
				bx = T.tx + T.tw / 2 - 12,
				got = Math.max(1, st.bar.got),
				f = st.bar.got / st.bar.n,
				ra = st.bar.red / got;
			g.globalAlpha = st.trayA;
			g.fillStyle = tok(c, '--dim');
			g.fillRect(bx, T.ty + 16, 24, bh);
			g.fillStyle = colA;
			g.fillRect(bx, T.ty + 16 + bh - bh * f * ra, 24, bh * f * ra);
			g.fillStyle = colB;
			g.fillRect(bx, T.ty + 16 + bh - bh * f, 24, bh * f * (1 - ra));
			g.globalAlpha = 1;
		} else
			for (const m of st.tray) {
				const [x, y, r] = T.slot(m.slot);
				circle(g, x, y, r, m.c ? colA : colB, st.trayA);
			}
		if (!st.tray.length && !st.bar && !live.length) {
			g.fillStyle = muted;
			g.font = '12px ' + sans;
			g.textAlign = 'center';
			g.textBaseline = 'middle';
			g.fillText('Your handful', T.tx + T.tw / 2, T.ty + T.th / 2 - 8);
			g.fillText('lands here', T.tx + T.tw / 2, T.ty + T.th / 2 + 8);
		}

		// chart
		if (showPlot) {
			g.fillStyle = muted;
			g.font = '600 11px ' + sans;
			g.textAlign = 'left';
			g.textBaseline = 'top';
			g.fillText(`EACH DOT IS ONE HANDFUL: % ${A.toUpperCase()}`, 0, PLOT_Y - 16);
			if (revealed) trueLine(g, c, plotX, PLOT_Y, PLOT_Y + LANES * LANE, 'true 55%');
			const r = dotR();
			shownLanes().forEach((l, i) => {
				const base = PLOT_Y + (i + 1) * LANE - 4;
				g.fillStyle = muted;
				g.font = '11px ' + mono;
				g.textAlign = 'right';
				g.textBaseline = 'alphabetic';
				const tag = step >= 3 || st.s < 10 ? (l.jar === 'big' ? 'big ' : 'small ') : '';
				g.fillText(tag + (l.n >= 1000 ? l.n / 1000 + 'k' : l.n), 66, base);
				dots(g, l.vals, {
					x: plotX,
					y: base,
					r,
					bin: ax.bin,
					color: ink,
					maxH: LANE - 4,
					lo: ax.lo,
					hi: ax.hi
				});
			});
			drawAxis(g, c, plotX, PLOT_Y + LANES * LANE, ax.ticks);
		}
		for (const [a, p] of live) a.draw!(g, p);
		if (anims.length) kick();
	}

	// ---- actions ----
	function putBack(after?: () => void) {
		anim(0, 150, {
			step: (p) => (st.trayA = 1 - p),
			done: () => {
				st.tray = [];
				st.bar = null;
				st.trayA = 1;
				st.wasOut.set(st.out);
				st.out.fill(0);
				st.refill = 0;
				anim(0, 175, {
					step: (p) => (st.refill = p),
					done: () => {
						st.wasOut.fill(0);
						st.refill = 1;
						after?.();
					}
				});
			}
		});
	}
	function flyMarble(
		delay: number,
		dur: number,
		from: () => [number, number],
		m: [number, number],
		slot: [number, number, number],
		r0: number,
		c: number,
		onStart: () => void,
		onLand: () => void
	) {
		let sx = 0,
			sy = 0;
		const mx = m[0],
			my = m[1] - 14;
		anim(delay, dur, {
			start() {
				[sx, sy] = from();
				onStart();
			},
			draw(g, p) {
				let x, y;
				if (p < 0.35) {
					const e = 1 - Math.pow(1 - p / 0.35, 2);
					x = sx + (mx - sx) * e;
					y = sy + (my - sy) * e;
				} else {
					// out of the mouth and sideways, falling into the tray
					const q = (p - 0.35) / 0.65;
					x = mx + (slot[0] - mx) * q;
					y = my - Math.sin(Math.PI * q) * 10 * (1 - q) + (slot[1] - my) * q * q;
				}
				circle(g, x, y, r0 + (slot[2] - r0) * p, c ? tok(canvas!, '--a') : tok(canvas!, '--b'));
			},
			done: onLand
		});
	}
	function flyDot(
		delay: number,
		dur: number,
		from: [number, number],
		l: Lane,
		value: number,
		onLand?: () => void
	) {
		const { b, xy } = dotTarget(l, value);
		anim(delay, dur, {
			draw(g, p) {
				const e = ease(p);
				circle(
					g,
					from[0] + (xy[0] - from[0]) * e,
					from[1] + (xy[1] - from[1]) * e - Math.sin(Math.PI * p) * 30,
					dotR() + 3 * (1 - p),
					tok(canvas!, '--ink')
				);
			},
			done() {
				l.vals.push(value);
				l.pending[b]--;
				onLand?.();
			}
		});
	}

	function handful(which: 'small' | 'big', size: number, gap: number, dur: number) {
		if (busy) return;
		busy = true;
		const res = which === 'small' ? drawSmall(size) : drawBig(size);
		size = res.n;
		st.trayN = size;
		st.tray = [];
		st.bar = null;
		const T = trayLayout(size);
		const colors =
			which === 'small'
				? res.picked!.map((i) => jar[i])
				: shuffle(Array.from({ length: size }, (_, i) => (i < res.red ? 1 : 0)));
		const t = { jar: which, n: size, got: 0, red: 0 };
		tally = { ...t };
		const finish = () => {
			const l = laneFor(which, size);
			anim(175, 150, { step: (p) => (st.trayA = 1 - p) });
			flyDot(175, 325, [T.tx + T.tw / 2, T.ty + T.th / 2], l, res.pct, () =>
				putBack(() => {
					busy = false;
					ui();
				})
			);
		};
		if (size <= 100) {
			const m = mouth(which);
			colors.forEach((c, j) => {
				const from =
					which === 'small'
						? () => scr(...marbleWorld(res.picked![j]))
						: () =>
								scr(
									B1.x + 8 + Math.random() * (B1.w - 16),
									B1.y + B1.h * 0.3 + Math.random() * B1.h * 0.65
								);
				flyMarble(
					j * gap,
					dur,
					from,
					m,
					T.slot(j),
					(pile.r * st.s) / 10,
					c,
					() => {
						if (which === 'small') st.out[res.picked![j]] = 1;
					},
					() => {
						st.tray.push({ c, slot: j });
						t.got++;
						t.red += c;
						tally = { ...t };
						if (t.got === size) finish();
					}
				);
			});
		} else {
			st.bar = { n: size, got: 0, red: 0 };
			if (which === 'small') for (const i of res.picked!) st.out[i] = 1;
			anim(0, 550, {
				step: (p) => {
					st.bar!.got = Math.round(p * size);
					st.bar!.red = Math.round(p * res.red);
					t.got = st.bar!.got;
					t.red = st.bar!.red;
					tally = { ...t };
				},
				done: finish
			});
		}
	}
	const handfulTimed = (which: 'small' | 'big', size: number) =>
		size <= 10 ? handful(which, size, 85, 325) : handful(which, size, 11, 240);

	function twenty(jars: ('small' | 'big')[], size: number) {
		if (busy) return;
		busy = true;
		tally = null;
		let left = 20 * jars.length;
		jars.forEach((which, j) => {
			const l = laneFor(which, which === 'small' ? Math.min(size, SMALL) : size);
			for (let i = 0; i < 20; i++) {
				const res = which === 'small' ? drawSmall(size) : drawBig(size);
				flyDot((i * jars.length + j) * 35, 300, mouth(which), l, res.pct, () => {
					if (--left === 0) {
						busy = false;
						ui();
					}
				});
			}
		});
	}
	function takeOne() {
		if (busy || st.tray.length >= 10) return;
		busy = true;
		st.trayN = 10;
		const T = trayLayout(10);
		const inJar: number[] = [];
		for (let i = 0; i < SMALL; i++) if (!st.out[i]) inJar.push(i);
		const i = inJar[Math.floor(Math.random() * inJar.length)],
			slot = st.tray.length;
		const t = tally ?? { jar: 'small' as const, n: 10, got: 0, red: 0 };
		flyMarble(
			0,
			600,
			() => scr(...marbleWorld(i)),
			mouth('small'),
			T.slot(slot),
			pile.r,
			jar[i],
			() => (st.out[i] = 1),
			() => {
				st.tray.push({ c: jar[i], slot });
				t.got++;
				t.red += jar[i];
				tally = { ...t };
				busy = false;
			}
		);
	}
	function putThemBack() {
		if (busy) return;
		busy = true;
		putBack(() => {
			tally = null;
			busy = false;
		});
	}
	function sortJar() {
		if (busy) return;
		busy = true;
		const from = st.sortE,
			to = from > 0.5 ? 0 : 1;
		anim(0, 700, {
			step: (p) => (st.sortE = from + (to - from) * ease(p)),
			done: () => {
				if (to === 1) revealed = true;
				busy = false;
				ui();
			}
		});
	}
	function zoom(to: number) {
		busy = true;
		const from = st.s;
		anim(0, 950, {
			step: (p) =>
				(st.s = Math.pow(10, Math.log10(from) + (Math.log10(to) - Math.log10(from)) * ease(p))),
			done: () => (busy = false)
		});
	}
	/** Any step, any time: skipping cancels what's running and starts the step clean. */
	function go(to: number, animate = true) {
		anims = [];
		busy = false;
		step = to;
		st.tray = [];
		st.bar = null;
		st.trayA = 1;
		st.out.fill(0);
		st.wasOut.fill(0);
		st.refill = 1;
		tally = null;
		for (const l of st.lanes) l.pending = {};
		st.sortE = Math.round(st.sortE);
		if (to >= 2) revealed = true;
		const target = to >= 3 ? 1 : 10;
		if (st.s !== target) {
			if (animate) zoom(target);
			else st.s = target;
		}
		ui();
		kick();
	}

	const steps = $derived([
		{
			t: 'One jar',
			body: `This jar holds 1,000 marbles, some ${A} and some ${B}. You can’t tell how many of each by looking. Take one out.`
		},
		{
			t: 'Grab 10 at a time',
			body: `Now grab a handful of 10. Once it’s counted, the handful becomes one dot on the chart: how ${A} it was. Grab a few and see where the dots land.`
		},
		{
			t: 'Grab 100 at a time',
			body: 'Bigger handfuls take longer to count, so this speeds up. Watch the dots for 100 bunch up more tightly than the dots for 10.'
		},
		{
			t: 'A jar 1,000 times bigger',
			body: 'This jar is 10 times as tall, 10 times as wide and 10 times as deep, so it holds 1,000 times as many marbles: a million, mixed the same way. Grab 100 from it.'
		},
		{ t: 'Your turn', body: 'Pick any handful size and grab from either jar.' }
	]);

	const texts = $derived.by(() => {
		void v;
		const lane = (j: string, size: number) =>
			st.lanes.find((x) => x.jar === j && x.n === size)?.vals ?? [];
		let pct = '',
			m = '';
		if (step === 0)
			pct =
				tally && tally.got >= 10
					? 'That’s a handful of 10. Put them back and move on to the next step.'
					: 'One marble is 0.1% of the jar.';
		if (step === 1) {
			pct = 'A handful of 10 is 1% of the jar.';
			const vals = lane('small', 10);
			if (vals.length >= 4)
				m = `Your handfuls of 10 ranged from <b>${Math.min(...vals).toFixed(0)}%</b> to <b>${Math.max(...vals).toFixed(0)}%</b> ${A}.${revealed ? ' The jar is really 55% ' + A + '.' : ' Count the jar to see the real mix.'}`;
		}
		if (step === 2) {
			pct = 'A handful of 100 is 10% of the jar.';
			const vals = lane('small', 100);
			if (vals.length)
				m = `95% of handfuls of 100 land within <b>±${fmtMoe(moe(100, SMALL))} points</b> of the true 55%. Pollsters call that the <strong>margin of error</strong>. <span class="small">${within(vals, moe(100, SMALL))} of your ${vals.length} did.</span>`;
		}
		if (step === 3) {
			pct = 'A handful of 100 is 10% of the small jar and 0.01% of the big one.';
			if (lane('big', 100).length)
				m = `Margin of error for 100: small jar <b>±${fmtMoe(moe(100, SMALL))}</b>, big jar <b>±${fmtMoe(moe(100, BIG))}</b>. A thousand times the marbles, and the handful is almost exactly as good.`;
		}
		if (step === 4) {
			const nS = Math.min(n, SMALL);
			pct = `${fmt(n)} is ${n >= SMALL ? 'all' : pctOf(n, SMALL)} of the small jar and ${pctOf(n, BIG)} of the big one.`;
			m = `Margin of error for ${fmt(n)}: small jar <b>±${fmtMoe(moe(nS, SMALL))}</b>${nS === SMALL ? ' (you counted every marble)' : ''}, big jar <b>±${fmtMoe(moe(n, BIG))}</b>.`;
		}
		return { pct, m };
	});

	onMount(() => {
		go(Math.max(0, Math.min(4, startStep)), false);
		const ro = new ResizeObserver(kick);
		if (canvas) ro.observe(canvas);
		const mq = matchMedia('(prefers-color-scheme: dark)');
		mq.addEventListener('change', kick);
		return () => {
			ro.disconnect();
			mq.removeEventListener('change', kick);
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
	<div class="steps" role="tablist" aria-label="Steps">
		{#each steps as s, i (i)}
			<button
				class="stepbtn"
				class:on={i <= step}
				role="tab"
				aria-selected={i === step}
				aria-label="Step {i + 1}: {s.t}"
				onclick={() => go(i)}
			></button>
		{/each}
	</div>
	<div class="eyebrow">Step {step + 1} of {steps.length}</div>
	<h2>{steps[step].t}</h2>
	<p class="lede">{steps[step].body}</p>
	<canvas
		bind:this={canvas}
		aria-label="A jar of marbles, a tray for the handful beside it, and a chart of every handful"
	></canvas>
	<div class="tally" aria-live="polite">
		{#if tally}
			{tally.got < tally.n ? 'Counting' : 'Handful'} of {fmt(tally.n)}{step >= 3
				? ` from the ${tally.jar} jar`
				: ''}:
			<b class="num">{fmt(tally.got)}</b> counted · <b class="ca">{fmt(tally.red)}</b>
			{A} · <b class="cb">{fmt(tally.got - tally.red)}</b>
			{B}{#if tally.got}
				· <b>{((tally.red / tally.got) * 100).toFixed(0)}% {A}</b>{/if}
		{/if}
	</div>
	<div class="row">
		{#if step === 0}
			<button class="primary" disabled={busy || (tally?.got ?? 0) >= 10} onclick={takeOne}
				>Take out a marble</button
			>
			<button disabled={busy || !tally} onclick={putThemBack}>Put them back</button>
		{:else if step === 1}
			<button class="primary" disabled={busy} onclick={() => handfulTimed('small', 10)}
				>Grab 10</button
			>
			<button disabled={busy} onclick={sortJar}
				>{v >= 0 && st.sortE > 0.5 ? 'Mix them up again' : 'Count the jar'}</button
			>
		{:else if step === 2}
			<button class="primary" disabled={busy} onclick={() => handfulTimed('small', 100)}
				>Grab 100</button
			>
			<button disabled={busy} onclick={() => twenty(['small'], 100)}>Grab 100, twenty times</button>
			<button disabled={busy} onclick={sortJar}
				>{v >= 0 && st.sortE > 0.5 ? 'Mix them up again' : 'Count the jar'}</button
			>
		{:else if step === 3}
			<button class="primary" disabled={busy} onclick={() => handfulTimed('big', 100)}
				>Grab 100 from the big jar</button
			>
			<button disabled={busy} onclick={() => twenty(['small', 'big'], 100)}
				>Twenty from each jar</button
			>
		{:else}
			<div class="row">
				<label class="eyebrow" for="side-n">Handful</label>
				<input
					id="side-n"
					type="number"
					min="1"
					max="1000000"
					inputmode="numeric"
					value={n}
					onchange={(e) => (n = clampN(e.currentTarget.value))}
				/>
				{#each [10, 100, 1000, 12000] as p (p)}
					<button onclick={() => (n = p)}>{fmt(p)}</button>
				{/each}
			</div>
			<button class="primary" disabled={busy} onclick={() => handfulTimed('small', n)}
				>From the small jar</button
			>
			<button disabled={busy} onclick={() => handfulTimed('big', n)}>From the big jar</button>
			<button disabled={busy} onclick={() => twenty(['small', 'big'], n)}>Twenty from each</button>
		{/if}
	</div>
	<div class="small">{texts.pct}</div>
	{#if texts.m}
		<!-- eslint-disable-next-line svelte/no-at-html-tags -- prototype copy built from numbers -->
		<div class="moe">{@html texts.m}</div>
	{/if}
	<div class="stepnav">
		<button disabled={step === 0} onclick={() => go(step - 1)}>Back</button>
		<button class="primary" disabled={step === steps.length - 1} onclick={() => go(step + 1)}
			>Next step</button
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
</style>
