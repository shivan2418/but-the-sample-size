<script lang="ts">
	import { takeSample, marginOfError, formatPercent, formatMOE } from '$lib/utils/statistics';
	import { fly, fade } from 'svelte/transition';
	import { Spring } from 'svelte/motion';

	let trueProportion = $state(0.52);
	let sampleSize = $state(1200);

	// Two populations to compare
	const populations = [
		{ id: 'small', name: 'Small Town', size: 10_000 },
		{ id: 'large', name: 'United States', size: 320_000_000 }
	];

	// Sample results for each population
	let sampleResults = $state<Array<{ population: string; samples: number[] }>>([
		{ population: 'Small Town', samples: [] },
		{ population: 'United States', samples: [] }
	]);

	let isAnimating = $state(false);

	const moe = $derived(marginOfError(sampleSize, trueProportion));

	// Animated display values - initialized with a fixed starting value
	const animatedSample1 = new Spring(0.52);
	const animatedSample2 = new Spring(0.52);

	async function takeSamples() {
		isAnimating = true;

		// Take samples from both populations
		const sample1 = takeSample(trueProportion, sampleSize);
		const sample2 = takeSample(trueProportion, sampleSize);

		// Animate to the new values
		animatedSample1.set(sample1);
		animatedSample2.set(sample2);

		// Add to history
		sampleResults = [
			{
				population: 'Small Town',
				samples: [...sampleResults[0].samples.slice(-9), sample1]
			},
			{
				population: 'United States',
				samples: [...sampleResults[1].samples.slice(-9), sample2]
			}
		];

		await new Promise((r) => setTimeout(r, 500));
		isAnimating = false;
	}

	function clearHistory() {
		sampleResults = [
			{ population: 'Small Town', samples: [] },
			{ population: 'United States', samples: [] }
		];
		animatedSample1.set(trueProportion, { instant: true });
		animatedSample2.set(trueProportion, { instant: true });
	}

	function isWithinMOE(sample: number): boolean {
		return Math.abs(sample - trueProportion) <= moe;
	}
</script>

<div class="space-y-6">
	<!-- Controls -->
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h3 class="text-lg font-semibold mb-4">Set the Parameters</h3>

		<div class="grid md:grid-cols-2 gap-6">
			<div>
				<label for="true-proportion" class="block text-sm font-medium text-gray-700 mb-2">
					True Population Support: {formatPercent(trueProportion)}
				</label>
				<input
					id="true-proportion"
					type="range"
					bind:value={trueProportion}
					min="0.3"
					max="0.7"
					step="0.01"
					class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
				/>
				<p class="text-xs text-gray-500 mt-1">
					The actual percentage of people who support the candidate
				</p>
			</div>

			<div>
				<label for="sample-size" class="block text-sm font-medium text-gray-700 mb-2">
					Sample Size: {sampleSize.toLocaleString()}
				</label>
				<input
					id="sample-size"
					type="range"
					bind:value={sampleSize}
					min="100"
					max="5000"
					step="100"
					class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
				/>
				<p class="text-xs text-gray-500 mt-1">
					Margin of error: {formatMOE(moe)} (at 95% confidence)
				</p>
			</div>
		</div>

		<div class="flex gap-3 mt-6">
			<button
				onclick={takeSamples}
				disabled={isAnimating}
				class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
			>
				{isAnimating ? 'Sampling...' : 'Take Sample'}
			</button>
			<button
				onclick={clearHistory}
				class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
			>
				Clear History
			</button>
		</div>
	</div>

	<!-- Side-by-side comparison -->
	<div class="grid md:grid-cols-2 gap-6">
		{#each populations as pop, i (pop.id)}
			{@const animated = i === 0 ? animatedSample1 : animatedSample2}
			{@const samples = sampleResults[i].samples}
			{@const latestSample = samples[samples.length - 1]}

			<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
				<div class="text-center mb-4">
					<h4 class="font-semibold text-lg">{pop.name}</h4>
					<p class="text-sm text-gray-500">
						Population: {pop.size.toLocaleString()}
					</p>
				</div>

				<!-- Current result display -->
				<div class="relative h-32 bg-gray-50 rounded-lg mb-4 overflow-hidden">
					<!-- True value marker -->
					<div
						class="absolute top-0 bottom-0 w-0.5 bg-green-500"
						style="left: {trueProportion * 100}%"
					>
						<div class="absolute -top-1 left-1/2 -translate-x-1/2 text-xs text-green-600 whitespace-nowrap">
							True: {formatPercent(trueProportion)}
						</div>
					</div>

					<!-- Margin of error band -->
					<div
						class="absolute top-8 bottom-8 bg-green-100 opacity-50"
						style="left: {(trueProportion - moe) * 100}%; width: {moe * 200}%"
					></div>

					<!-- Sample result marker -->
					{#if latestSample !== undefined}
						<div
							class="absolute top-8 bottom-8 w-1 transition-all duration-500"
							class:bg-blue-500={isWithinMOE(latestSample)}
							class:bg-red-500={!isWithinMOE(latestSample)}
							style="left: {animated.current * 100}%"
						>
							<div
								class="absolute top-full mt-1 left-1/2 -translate-x-1/2 text-xs whitespace-nowrap font-medium"
								class:text-blue-600={isWithinMOE(latestSample)}
								class:text-red-600={!isWithinMOE(latestSample)}
							>
								{formatPercent(latestSample)}
							</div>
						</div>
					{:else}
						<div class="flex items-center justify-center h-full text-gray-400 text-sm">
							Click "Take Sample" to begin
						</div>
					{/if}
				</div>

				<!-- Sample history -->
				{#if samples.length > 0}
					<div class="space-y-2">
						<p class="text-xs text-gray-500 font-medium">Recent samples:</p>
						<div class="flex flex-wrap gap-2">
							{#each samples as sample, j (j)}
								<span
									class="text-xs px-2 py-1 rounded"
									class:bg-blue-100={isWithinMOE(sample)}
									class:text-blue-700={isWithinMOE(sample)}
									class:bg-red-100={!isWithinMOE(sample)}
									class:text-red-700={!isWithinMOE(sample)}
									transition:fly={{ y: -10 }}
								>
									{formatPercent(sample)}
								</span>
							{/each}
						</div>
						<p class="text-xs text-gray-500">
							{samples.filter(isWithinMOE).length} of {samples.length} within margin of error
						</p>
					</div>
				{/if}
			</div>
		{/each}
	</div>

	<!-- Key insight -->
	{#if sampleResults[0].samples.length >= 3}
		<div transition:fade class="bg-blue-50 border border-blue-200 rounded-xl p-6">
			<h4 class="font-semibold text-blue-800 mb-2">Notice something?</h4>
			<p class="text-blue-700">
				Both populations give <strong>nearly identical results</strong> with the same sample size!
				The small town (10,000 people) and the entire US (320 million) produce estimates with the
				same margin of error. This is because the margin of error depends on <strong>sample size</strong>,
				not population size.
			</p>
		</div>
	{/if}
</div>
