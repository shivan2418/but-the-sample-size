// PROTOTYPE, throwaway: the national rung's model. One split of everyone who voted for president in
// 2024 (One US-wide split or per-state proportions?, #23), drawn without replacement, no residents.

export const US = { red: 77_302_580, blue: 75_017_613, other: 2_918_109 };
export const TOTAL = US.red + US.blue + US.other; // 155,238,302
export const P = { red: US.red / TOTAL, blue: US.blue / TOTAL, other: US.other / TOTAL };
export const TRUE_RED = P.red * 100; // 49.80

export const MIN_N = 1000;

/** Sizes the reader has already met, marked on the population slider. */
export const marks = [
	{ N: 1000, label: 'Small jar', long: 'the small jar of marbles' },
	{ N: 645_000, label: 'Charlotte', long: 'Charlotte’s registered voters' },
	{ N: 1_000_000, label: 'Big jar', long: 'the big jar of marbles' },
	{ N: 7_854_102, label: 'North Carolina', long: 'North Carolina’s registered voters' },
	{ N: TOTAL, label: 'US voters', long: 'everyone who voted for president in 2024' }
];

export const fmt = (n: number) => Math.round(n).toLocaleString('en-US');

/** 155,238,302 → "155 million", 7,854,102 → "7.85 million", 645,000 → "645,000". */
export function fmtBig(n: number) {
	if (n >= 1e6) {
		const m = n / 1e6;
		return (
			(m >= 100 ? m.toFixed(0) : m >= 10 ? m.toFixed(1) : m.toFixed(2)).replace(
				/\.0+$|(\.\d*?)0+$/,
				'$1'
			) + ' million'
		);
	}
	return fmt(n);
}

/** Share of everyone that the sample is, readable at any size. */
export function pctOf(n: number, N: number) {
	const v = (Math.min(n, N) / N) * 100;
	if (v >= 10) return v.toFixed(0) + '%';
	if (v >= 1) return v.toFixed(1) + '%';
	if (v >= 0.01) return v.toFixed(2) + '%';
	return v.toPrecision(1) + '%';
}

/** 95% margin of error, in points, for the red candidate's share, with the finite-population correction. */
export const moe = (n: number, N: number, p = P.red) =>
	n >= N ? 0 : 1.96 * Math.sqrt(((p * (1 - p)) / n) * ((N - n) / (N - 1))) * 100;

export const fmtMoe = (m: number) => (m === 0 ? '0' : m < 0.1 ? m.toFixed(2) : m.toFixed(1));

// The population slider is a log scale from 1,000 to 155M, on a 0..1000 track.
const LO = Math.log10(MIN_N),
	HI = Math.log10(TOTAL);
export const toT = (N: number) => ((Math.log10(N) - LO) / (HI - LO)) * 1000;
export function fromT(t: number) {
	const mark = marks.find((m) => Math.abs(toT(m.N) - t) < 14);
	if (mark) return mark.N;
	const N = Math.pow(10, LO + (t / 1000) * (HI - LO));
	const mag = Math.pow(10, Math.floor(Math.log10(N)) - 2); // three significant figures
	return Math.min(TOTAL, Math.max(MIN_N, Math.round(N / mag) * mag));
}
export const markFor = (N: number) => marks.find((m) => m.N === N);

export const clampN = (v: unknown, max = TOTAL) =>
	Math.max(1, Math.min(max, Math.round(Number(v) || 1)));

/** A small seeded generator (mulberry32), so each poll keeps its own random numbers while the
 *  reader drags a control: the dots move only as far as the change really moves them. */
function rng(seed: number) {
	return () => {
		seed |= 0;
		seed = (seed + 0x6d2b79f5) | 0;
		let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
}

export type Poll = { n: number; red: number; blue: number; other: number; pct: number };

/** One poll of n from a population of N with the US split. Exact draws without replacement up to
 *  50,000 asked; past that a normal draw with the same spread (nobody can see the difference). */
export function poll(n: number, N: number, seed: number): Poll {
	n = Math.min(n, N);
	const r = rng(seed);
	let red = 0,
		blue = 0;
	if (n <= 50_000) {
		let R = Math.round(N * P.red),
			B = Math.round(N * P.blue),
			T = N;
		for (let i = 0; i < n; i++) {
			const u = r() * T;
			if (u < R) {
				red++;
				R--;
			} else if (u < R + B) {
				blue++;
				B--;
			}
			T--;
		}
	} else {
		const fpc = (N - n) / Math.max(1, N - 1);
		const z = () => Math.sqrt(-2 * Math.log(1 - r())) * Math.cos(2 * Math.PI * r());
		red = Math.round(n * P.red + z() * Math.sqrt(n * P.red * (1 - P.red) * fpc));
		const rest = n - red,
			q = P.blue / (1 - P.red);
		blue = Math.round(rest * q + z() * Math.sqrt(rest * q * (1 - q) * fpc));
	}
	return { n, red, blue, other: n - red - blue, pct: (red / n) * 100 };
}

export const polls = (n: number, N: number, count: number, batch: number) =>
	Array.from({ length: count }, (_, j) => poll(n, N, batch * 7919 + j * 104729 + 1));

export const misses = (ps: Poll[], m: number) =>
	ps.filter((p) => Math.abs(p.pct - TRUE_RED) > m + 1e-9).length;
