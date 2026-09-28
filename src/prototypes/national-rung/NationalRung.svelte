<script lang="ts">
	// PROTOTYPE, throwaway: rung 7, "The whole country", as a first draft in one column. The parts
	// are settled (#23, #29); how the two controls sit together on a phone is the open question in
	// #31, so this is only the plain stacked order to react to.
	import SampleSize from './SampleSize.svelte';
	import PopSlider from './PopSlider.svelte';
	import Polls from './Polls.svelte';
	import Curve from './Curve.svelte';
	import SplitBar from './SplitBar.svelte';
	import Country from './Country.svelte';
	import { TOTAL, fmt, fmtMoe, moe } from './model';

	let { startN = 1200, startPop = TOTAL }: { startN?: number; startPop?: number } = $props();

	// the controls start where the story says, then belong to the reader
	// svelte-ignore state_referenced_locally
	let n = $state(startN);
	// svelte-ignore state_referenced_locally
	let N = $state(startPop);
	const k = $derived(Math.min(n, N));
</script>

<section id="country" class="scroll-mt-4 border-t border-line py-5 lg:py-8">
	<h2 class="mb-3 text-[22px]/tight font-bold lg:mb-4 lg:text-[28px]">
		<a href="#country" class="text-ink no-underline">
			<span class="font-normal text-muted">7 ·</span> The whole country
		</a>
	</h2>

	<div class="flex flex-col gap-4">
		<Country />
		<SplitBar />

		<p>
			Poll this country the way you polled the jars. Then change how many people there are, and
			watch what happens to the polls.
		</p>

		<div class="flex flex-col gap-4 border-t border-dim pt-4">
			<SampleSize {n} {N} onchange={(v) => (n = v)} />
			<PopSlider {N} onchange={(v) => (N = v)} />
		</div>

		<Polls n={k} {N} />

		<div class="flex flex-col gap-2 border-t border-dim pt-4">
			<h3 class="font-bold">What more people buys you</h3>
			<p>
				Going from 1,200 to 12,000 asked costs ten times as much and narrows the range from ±{fmtMoe(
					moe(1200, N)
				)} to ±{fmtMoe(moe(12000, N))} points. Tap the chart to ask that many.
			</p>
			<Curve n={k} {N} onpick={(v) => (n = v)} />
			<p class="text-[15px] text-muted">
				Margin of error against how many you ask{N === TOTAL
					? ''
					: `, for ${fmt(N)} people (dashed: all ${fmt(TOTAL)} US voters)`}.
			</p>
		</div>
	</div>
</section>
