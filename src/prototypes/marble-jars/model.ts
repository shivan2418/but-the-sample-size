// PROTOTYPE, throwaway: the marble jars' shared model. Draws are exact (without replacement).

export const P = 0.55;
export const SMALL = 1000;
export const BIG = 1_000_000;

export type Palette = {
	/** The colour being counted ("% red"). */
	a: { name: string; light: string; dark: string };
	b: { name: string; light: string; dark: string };
};

export const palettes = {
	redBlue: {
		a: { name: 'red', light: '#D4463A', dark: '#EE6457' },
		b: { name: 'blue', light: '#2C66CA', dark: '#5B8FEC' }
	},
	neutral: {
		a: { name: 'yellow', light: '#D99A0B', dark: '#F0B63A' },
		b: { name: 'grey', light: '#6B7482', dark: '#8C95A3' }
	}
} satisfies Record<string, Palette>;

export type PaletteKey = keyof typeof palettes;

export const fmt = (n: number) => n.toLocaleString('en-US');

export function shuffle<T>(a: T[]): T[] {
	for (let i = a.length - 1; i > 0; i--) {
		const j = Math.floor(Math.random() * (i + 1));
		[a[i], a[j]] = [a[j], a[i]];
	}
	return a;
}

/** The small jar's 1,000 marbles, shuffled once: 1 = the counted colour. */
export const jar: number[] = shuffle(
	Array.from({ length: SMALL }, (_, i) => (i < SMALL * P ? 1 : 0))
);

export type Draw = { jar: 'small' | 'big'; n: number; red: number; pct: number; picked?: number[] };

export function drawSmall(n: number): Draw {
	n = Math.min(n, SMALL);
	const idx = Array.from({ length: SMALL }, (_, i) => i);
	for (let i = 0; i < n; i++) {
		const j = i + Math.floor(Math.random() * (SMALL - i));
		[idx[i], idx[j]] = [idx[j], idx[i]];
	}
	const picked = idx.slice(0, n);
	let red = 0;
	for (const k of picked) red += jar[k];
	return { jar: 'small', n, red, pct: (red / n) * 100, picked };
}

export function drawBig(n: number): Draw {
	n = Math.min(n, BIG);
	let R = BIG * P,
		T = BIG,
		red = 0;
	for (let i = 0; i < n; i++) {
		if (Math.random() * T < R) {
			R--;
			red++;
		}
		T--;
	}
	return { jar: 'big', n, red, pct: (red / n) * 100 };
}

/** A running draw, one marble at a time, from either jar (used by the pour). */
export function pourer(which: 'small' | 'big') {
	if (which === 'small') {
		const order = shuffle(Array.from({ length: SMALL }, (_, i) => i));
		let k = 0;
		return { size: SMALL, next: () => (k < SMALL ? jar[order[k++]] : -1) };
	}
	let R = BIG * P,
		T = BIG;
	return {
		size: BIG,
		next: () => {
			if (T === 0) return -1;
			const red = Math.random() * T < R ? 1 : 0;
			R -= red;
			T--;
			return red;
		}
	};
}

/** 95% margin of error in points, with the finite-population correction. */
export const moe = (n: number, N: number) =>
	n >= N ? 0 : 1.96 * Math.sqrt(((P * (1 - P)) / n) * ((N - n) / (N - 1))) * 100;

export const fmtMoe = (m: number) => (m === 0 ? '0' : m < 0.1 ? m.toFixed(2) : m.toFixed(1));

export function pctOf(n: number, N: number) {
	const v = (Math.min(n, N) / N) * 100;
	if (v >= 10) return v.toFixed(0) + '%';
	if (v >= 1) return v.toFixed(1) + '%';
	if (v >= 0.01) return v.toFixed(2) + '%';
	return v.toPrecision(1) + '%';
}

export const within = (vals: number[], m: number) =>
	vals.filter((v) => Math.abs(v - P * 100) <= m + 1e-9).length;

export const clampN = (v: unknown) => Math.max(1, Math.min(BIG, Math.round(Number(v) || 1)));

/** A seeded generator so the drawn "grain" of the big jar doesn't flicker between frames. */
export function seeded(seed: number) {
	return () => (seed = (seed * 16807) % 2147483647) / 2147483647;
}

export const ease = (p: number) => (p < 0.5 ? 2 * p * p : 1 - Math.pow(-2 * p + 2, 2) / 2);

/** Reads a CSS custom property from an element (the frame sets them). */
export const tok = (el: Element, name: string) =>
	getComputedStyle(el).getPropertyValue(name).trim();

/** Sizes a canvas for the device pixel ratio and returns a context in CSS pixels. */
export function fit(c: HTMLCanvasElement, h: number) {
	const dpr = window.devicePixelRatio || 1,
		w = c.clientWidth || 320;
	if (c.width !== Math.round(w * dpr) || c.height !== Math.round(h * dpr)) {
		c.width = Math.round(w * dpr);
		c.height = Math.round(h * dpr);
		c.style.height = h + 'px';
	}
	const g = c.getContext('2d')!;
	g.setTransform(dpr, 0, 0, dpr, 0, 0);
	g.clearRect(0, 0, w, h);
	return { g, w, h, dpr };
}

export function circle(
	g: CanvasRenderingContext2D,
	x: number,
	y: number,
	r: number,
	col: string,
	alpha = 1
) {
	g.globalAlpha = alpha;
	g.beginPath();
	g.arc(x, y, Math.max(0.4, r), 0, 7);
	g.fillStyle = col;
	g.fill();
	g.globalAlpha = 1;
}

export function jarPath(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number) {
	g.beginPath();
	g.roundRect(x + w * 0.28, y, w * 0.44, h * 0.07, w * 0.02);
	g.roundRect(x, y + h * 0.07, w, h * 0.93, w * 0.08);
}

/** Stacks one dot per value in bins around the true split; returns nothing, draws in place. */
export function dots(
	g: CanvasRenderingContext2D,
	vals: number[],
	o: {
		x: (v: number) => number;
		y: number;
		r: number;
		bin: number;
		color: string;
		maxH: number;
		lo?: number;
		hi?: number;
	}
) {
	const lo = o.lo ?? 0,
		hi = o.hi ?? 100;
	const bins = vals.map((v) => Math.round((v - P * 100) / o.bin));
	const counts: Record<number, number> = {};
	let max = 0;
	for (const b of bins) max = Math.max(max, (counts[b] = (counts[b] ?? 0) + 1));
	const step = Math.min(2 * o.r + 0.6, max > 0 ? (o.maxH - o.r) / max : 99);
	const seen: Record<number, number> = {};
	for (const b of bins) {
		const k = (seen[b] = (seen[b] ?? 0) + 1);
		const cx = o.x(Math.max(lo, Math.min(hi, P * 100 + b * o.bin)));
		circle(g, cx, o.y - (o.r + 1 + (k - 1) * step), o.r, o.color);
	}
}

export function axis(
	g: CanvasRenderingContext2D,
	el: Element,
	x: (v: number) => number,
	y: number,
	ticks: number[]
) {
	g.strokeStyle = tok(el, '--line');
	g.lineWidth = 1;
	g.beginPath();
	g.moveTo(x(ticks[0]), y + 0.5);
	g.lineTo(x(ticks[ticks.length - 1]), y + 0.5);
	g.stroke();
	g.fillStyle = tok(el, '--muted');
	g.font = '11px ' + tok(el, '--mono');
	g.textAlign = 'center';
	g.textBaseline = 'top';
	for (const t of ticks) {
		g.fillRect(x(t), y, 1, 4);
		g.fillText(t + '%', x(t), y + 6);
	}
}

export function trueLine(
	g: CanvasRenderingContext2D,
	el: Element,
	x: (v: number) => number,
	y0: number,
	y1: number,
	label = ''
) {
	const X = Math.round(x(P * 100)) + 0.5;
	g.strokeStyle = tok(el, '--ink');
	g.setLineDash([3, 3]);
	g.lineWidth = 1;
	g.beginPath();
	g.moveTo(X, y0);
	g.lineTo(X, y1);
	g.stroke();
	g.setLineDash([]);
	if (label) {
		g.fillStyle = tok(el, '--ink');
		g.font = '500 11px ' + tok(el, '--sans');
		g.textAlign = 'left';
		g.textBaseline = 'top';
		g.fillText(label, X + 4, y0);
	}
}
