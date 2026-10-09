<script lang="ts">
	// PROTOTYPE, throwaway: the marble rung's sample-size control as one slider. The reader drags the
	// target (the thumb) anywhere from what's already counted up to the whole jar, then presses
	// Sample, and marbles come out until the count reaches the target. A second marker under the
	// track shows how many are counted so far. Presets set the target; one below the count is
	// disabled, since marbles can't go back in by moving the target. The jar stands to the right.
	import Jar from './Jar.svelte';

	let {
		jar = 1000,
		share = 0.55,
		presets = [10, 50, 100, 500, 1000],
		scale = 'linear',
		speed = 1
	}: {
		/** How many marbles are in the jar: the slider's maximum. */
		jar?: number;
		/** The share of red marbles in the jar. */
		share?: number;
		presets?: number[];
		/** 'log' spreads the small sizes out, for a jar too big for a straight track. */
		scale?: 'linear' | 'log';
		/** Multiplies the sampling rate. */
		speed?: number;
	} = $props();

	let target = $state(0);
	let counted = $state(0);
	let red = $state(0);
	let running = $state(false);

	const fmt = (n: number) => Math.round(n).toLocaleString('en-US');

	// ---- the track: 0..1000 steps, mapped to marbles on a straight or a log scale ----
	const STEPS = 1000;
	function toPos(v: number) {
		if (scale === 'log') return Math.log10(v + 1) / Math.log10(jar + 1);
		return v / jar;
	}
	function fromStep(s: number) {
		const f = s / STEPS;
		if (scale === 'linear') return Math.round(f * jar);
		const v = Math.pow(10, f * Math.log10(jar + 1)) - 1;
		if (v < 10) return Math.round(v);
		const mag = Math.pow(10, Math.floor(Math.log10(v)) - 1); // two significant figures
		return Math.min(jar, Math.round(v / mag) * mag);
	}

	function setTarget(v: number) {
		target = Math.max(counted, Math.min(jar, v));
	}

	// ---- the jar: every marble, shuffled; the first `jar - counted` are still in it ----
	function fill() {
		const c = new Uint8Array(jar);
		c.fill(1, 0, Math.round(jar * share));
		for (let i = jar - 1; i > 0; i--) {
			const j = Math.floor(Math.random() * (i + 1));
			[c[i], c[j]] = [c[j], c[i]];
		}
		return c;
	}
	let colors = $state.raw(fill());
	let version = $state(0);

	// Take k marbles at random, without replacement: each comes out of a random place in the jar,
	// and the marble on top drops into the gap.
	function take(k: number) {
		let left = jar - counted;
		let got = 0;
		for (let i = 0; i < k && left > 0; i++) {
			const j = Math.floor(Math.random() * left);
			got += colors[j];
			colors[j] = colors[left - 1];
			left--;
		}
		red += got;
		counted = jar - left;
		version++;
	}

	// Sample until the count reaches the target: at least 12 marbles a second, so a small target
	// can be watched one by one, and a big one takes about a second and a half.
	let raf = 0;
	function run() {
		if (running) {
			running = false;
			cancelAnimationFrame(raf);
			return;
		}
		running = true;
		let last = performance.now();
		let due = 0;
		const frame = (now: number) => {
			const rate = Math.max(12, target / 1.5) * speed;
			due += ((now - last) / 1000) * rate;
			last = now;
			const k = Math.min(Math.floor(due), target - counted);
			if (k > 0) {
				take(k);
				due -= k;
			}
			if (counted >= target) {
				running = false;
				return;
			}
			raf = requestAnimationFrame(frame);
		};
		raf = requestAnimationFrame(frame);
	}

	// One marble, straight away: the count goes up by one, and the target with it when they meet.
	function takeOne() {
		if (running || counted >= jar) return;
		take(1);
		target = Math.max(target, counted);
	}

	function putBack() {
		cancelAnimationFrame(raf);
		running = false;
		counted = 0;
		red = 0;
		target = 0;
		colors = fill();
		version++;
	}

	$effect(() => () => cancelAnimationFrame(raf));

	const tPos = $derived(toPos(target));
	const cPos = $derived(toPos(counted));
	const shown = $derived(presets.filter((p) => p <= jar));
	const ticks = $derived(scale === 'log' ? [0, 10, 100, 1000, 10_000, 100_000, 1_000_000] : [0]);
	const pct = (n: number) => {
		const v = (n / jar) * 100;
		return (v >= 1 || v === 0 ? v.toFixed(0) : v >= 0.1 ? v.toFixed(1) : v.toFixed(2)) + '%';
	};
	// keep a label inside the track's ends
	const anchor = (p: number) => (p < 0.08 ? '0' : p > 0.92 ? '-100%' : '-50%');
</script>

<div class="flex flex-col gap-3">
	<div class="flex items-start gap-4">
		<div class="flex min-w-0 flex-1 flex-col gap-3">
			<div class="flex flex-col gap-1">
				<label for="target" class="font-bold">How many marbles to take</label>

				<!-- the track: the native range input sits on top for dragging and the keyboard; the fills,
		     the counted marker and the labels are drawn under it -->
				<div class="track relative h-[76px]" style:--t={tPos} style:--c={cPos}>
					<span
						class="pointer-events-none absolute top-0 text-[15px]/none font-bold whitespace-nowrap tabular-nums"
						style:left="calc(var(--t) * (100% - 20px) + 10px)"
						style:translate="{anchor(tPos)} 0">Target {fmt(target)}</span
					>
					<div class="absolute inset-x-[10px] top-[31px] h-2.5 bg-dim">
						<!-- counted so far -->
						<div class="absolute inset-y-0 left-0 bg-ink" style:width="calc(var(--c) * 100%)"></div>
						<!-- still to take -->
						<div
							class="absolute inset-y-0 bg-line"
							style:left="calc(var(--c) * 100%)"
							style:width="calc((var(--t) - var(--c)) * 100%)"
						></div>
					</div>
					<!-- the counted marker, under the track -->
					<div
						class="pointer-events-none absolute top-[44px] flex flex-col items-center"
						style:left="calc(var(--c) * (100% - 20px) + 10px)"
						style:translate="-50% 0"
					>
						<span class="h-0 w-0 border-x-[6px] border-b-[8px] border-x-transparent border-b-ink"
						></span>
					</div>
					<span
						class="pointer-events-none absolute top-[56px] text-[15px]/none whitespace-nowrap text-muted tabular-nums"
						style:left="calc(var(--c) * (100% - 20px) + 10px)"
						style:translate="{anchor(cPos)} 0">Counted {fmt(counted)}</span
					>
					<input
						id="target"
						type="range"
						min="0"
						max={STEPS}
						step="1"
						value={Math.round(tPos * STEPS)}
						oninput={(e) => {
							setTarget(fromStep(Number(e.currentTarget.value)));
							e.currentTarget.value = String(Math.round(toPos(target) * STEPS));
						}}
						aria-valuetext="Target {fmt(target)} marbles, {fmt(counted)} counted"
						class="absolute inset-x-0 top-[20px] h-8 w-full cursor-pointer appearance-none bg-transparent"
					/>
				</div>
				{#if scale === 'log'}
					<div class="relative mx-[10px] h-4 text-[12px]/none text-muted" aria-hidden="true">
						{#each ticks.filter((t) => t <= jar) as t (t)}
							<span
								class="absolute font-mono"
								style:left="{toPos(t) * 100}%"
								style:translate={t === 0 ? '0' : t === jar ? '-100% 0' : '-50% 0'}
								>{t >= 1e6 ? t / 1e6 + 'M' : t >= 1000 ? t / 1000 + 'k' : t}</span
							>
						{/each}
					</div>
				{:else}
					<div
						class="mx-[10px] flex justify-between font-mono text-[12px] text-muted"
						aria-hidden="true"
					>
						<span>0</span><span>{fmt(jar)}</span>
					</div>
				{/if}
			</div>

			<div class="flex flex-wrap gap-1.5" role="group" aria-label="Set the target">
				{#each shown as p (p)}
					<button
						class="min-h-11 cursor-pointer bg-glass px-3 font-semibold tabular-nums shadow-[0_2px_0_var(--line)] disabled:cursor-default disabled:opacity-40 aria-pressed:bg-ink aria-pressed:text-bg aria-pressed:shadow-none"
						aria-pressed={target === p}
						disabled={counted > p}
						onclick={() => setTarget(p)}>{fmt(p)}</button
					>
				{/each}
			</div>
		</div>
		<Jar {colors} left={jar - counted} {version} />
	</div>

	<div class="flex flex-wrap gap-2.5">
		<button
			class="min-h-11 min-w-[9rem] cursor-pointer bg-go px-4 font-semibold text-white shadow-[0_2px_0_var(--go-edge)] disabled:cursor-default disabled:opacity-45"
			disabled={!running && counted >= target}
			onclick={run}>{running ? 'Pause' : counted ? 'Keep sampling' : 'Sample'}</button
		>
		<button
			class="min-h-11 cursor-pointer bg-glass px-3 font-semibold shadow-[0_2px_0_var(--line)] disabled:cursor-default disabled:opacity-45"
			disabled={running || counted >= jar}
			onclick={takeOne}>Take 1</button
		>
		<button
			class="min-h-11 cursor-pointer bg-glass px-3 font-semibold shadow-[0_2px_0_var(--line)] disabled:cursor-default disabled:opacity-45"
			disabled={!counted && !target}
			onclick={putBack}>Put them back</button
		>
	</div>

	<p class="tabular-nums" aria-live="polite">
		{#if counted}
			<b>{fmt(counted)}</b> counted ({pct(counted)} of the jar):
			<b class="text-a">{fmt(red)} red</b>, <b class="text-b">{fmt(counted - red)} blue</b>. That’s
			<b>{((red / counted) * 100).toFixed(1)}% red</b>.
		{:else}
			Nothing counted yet. Drag the slider or pick a number, then press Sample.
		{/if}
	</p>
</div>

<style>
	/* the thumb is the target: a 20px ring in ink, while the input's full 32px height still catches
	   the finger. The track is drawn underneath, so the input's own track is invisible. */
	input[type='range']::-webkit-slider-runnable-track {
		background: transparent;
		height: 2rem;
	}
	input[type='range']::-moz-range-track {
		background: transparent;
	}
	input[type='range']::-webkit-slider-thumb {
		appearance: none;
		box-sizing: border-box;
		width: 20px;
		height: 20px;
		margin-top: 6px;
		background: var(--bg);
		border: 2px solid var(--ink);
		border-radius: 50%;
	}
	input[type='range']::-moz-range-thumb {
		box-sizing: border-box;
		width: 20px;
		height: 20px;
		background: var(--bg);
		border: 2px solid var(--ink);
		border-radius: 50%;
	}
</style>
