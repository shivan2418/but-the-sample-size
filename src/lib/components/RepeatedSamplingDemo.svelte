<script lang="ts">
	import { takeMultipleSamples, marginOfError, samplesWithinMOE, createHistogramBins, formatPercent } from '$lib/utils/statistics';
	import { fly, fade } from 'svelte/transition';

	let trueProportion = $state(0.52);
	let sampleSize = $state(1200);
	let numSamples = $state(100);

	let samples = $state<number[]>([]);
	let isRunning = $state(false);

	const moe = $derived(marginOfError(sampleSize, trueProportion));
	const histogramBins = $derived(samples.length > 0 ? createHistogramBins(samples, 20) : []);
	const percentWithinMOE = $derived(samples.length > 0 ? samplesWithinMOE(samples, trueProportion, moe) : 0);
	const maxBinCount = $derived(Math.max(...histogramBins.map((b) => b.count), 1));

	async function runSimulation() {
		isRunning = true;
		samples = [];

		// Run samples in batches for visual effect
		const batchSize = Math.ceil(numSamples / 20);
		for (let i = 0; i < numSamples; i += batchSize) {
			const batch = takeMultipleSamples(trueProportion, sampleSize, Math.min(batchSize, numSamples - i));
			samples = [...samples, ...batch];
			await new Promise((r) => setTimeout(r, 50));
		}

		isRunning = false;
	}

	function reset() {
		samples = [];
	}

	function isWithinMOE(value: number): boolean {
		return Math.abs(value - trueProportion) <= moe;
	}
</script>

<div class="space-y-6">
	<!-- Controls -->
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h3 class="text-lg font-semibold mb-4">Run Many Polls</h3>
		<p class="text-sm text-gray-600 mb-4">
			See what happens when we run hundreds of polls. About 95% should fall within the margin of error.
		</p>

		<div class="grid md:grid-cols-3 gap-4 mb-6">
			<div>
				<label for="rsd-true-prop" class="block text-sm font-medium text-gray-700 mb-2">
					True Support: {formatPercent(trueProportion)}
				</label>
				<input
					id="rsd-true-prop"
					type="range"
					bind:value={trueProportion}
					min="0.3"
					max="0.7"
					step="0.01"
					class="w-full"
				/>
			</div>

			<div>
				<label for="rsd-sample-size" class="block text-sm font-medium text-gray-700 mb-2">
					Sample Size: {sampleSize.toLocaleString()}
				</label>
				<input
					id="rsd-sample-size"
					type="range"
					bind:value={sampleSize}
					min="100"
					max="2000"
					step="100"
					class="w-full"
				/>
			</div>

			<div>
				<label for="rsd-num-samples" class="block text-sm font-medium text-gray-700 mb-2">
					Number of Polls: {numSamples}
				</label>
				<input
					id="rsd-num-samples"
					type="range"
					bind:value={numSamples}
					min="50"
					max="500"
					step="50"
					class="w-full"
				/>
			</div>
		</div>

		<div class="flex gap-3">
			<button
				onclick={runSimulation}
				disabled={isRunning}
				class="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
			>
				{isRunning ? `Running... (${samples.length}/${numSamples})` : 'Run Simulation'}
			</button>
			<button
				onclick={reset}
				disabled={isRunning || samples.length === 0}
				class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 disabled:opacity-50 transition-colors"
			>
				Reset
			</button>
		</div>
	</div>

	<!-- Histogram -->
	{#if samples.length > 0}
		<div transition:fade class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
			<h4 class="font-semibold mb-4">Distribution of Poll Results</h4>

			<div class="relative h-64 flex items-end gap-0.5">
				<!-- MOE band background -->
				<div
					class="absolute inset-0 flex"
					style="left: {((trueProportion - moe - 0.3) / 0.4) * 100}%; width: {(moe * 2 / 0.4) * 100}%"
				>
					<div class="bg-green-100 w-full h-full opacity-50"></div>
				</div>

				<!-- True value line -->
				<div
					class="absolute top-0 bottom-0 w-0.5 bg-green-600 z-10"
					style="left: {((trueProportion - 0.3) / 0.4) * 100}%"
				></div>

				<!-- Histogram bars -->
				{#each histogramBins as bin, i (i)}
					{@const binCenter = (bin.binStart + bin.binEnd) / 2}
					{@const withinMOE = isWithinMOE(binCenter)}
					<div
						class="flex-1 transition-all duration-300 rounded-t"
						class:bg-blue-500={withinMOE}
						class:bg-red-400={!withinMOE}
						style="height: {(bin.count / maxBinCount) * 100}%"
						title="{formatPercent(bin.binStart)} - {formatPercent(bin.binEnd)}: {bin.count} polls"
					></div>
				{/each}
			</div>

			<!-- X-axis labels -->
			<div class="flex justify-between text-xs text-gray-500 mt-2">
				<span>30%</span>
				<span>40%</span>
				<span>50%</span>
				<span>60%</span>
				<span>70%</span>
			</div>

			<!-- Legend -->
			<div class="flex gap-6 mt-4 text-sm">
				<div class="flex items-center gap-2">
					<div class="w-4 h-4 bg-blue-500 rounded"></div>
					<span>Within MOE ({formatPercent(percentWithinMOE)} of polls)</span>
				</div>
				<div class="flex items-center gap-2">
					<div class="w-4 h-4 bg-red-400 rounded"></div>
					<span>Outside MOE</span>
				</div>
				<div class="flex items-center gap-2">
					<div class="w-4 h-0.5 bg-green-600"></div>
					<span>True value ({formatPercent(trueProportion)})</span>
				</div>
			</div>
		</div>

		<!-- Results summary -->
		<div
			transition:fly={{ y: 20 }}
			class="rounded-xl p-6"
			class:bg-green-50={percentWithinMOE >= 0.9}
			class:border-green-200={percentWithinMOE >= 0.9}
			class:bg-amber-50={percentWithinMOE < 0.9}
			class:border-amber-200={percentWithinMOE < 0.9}
		>
			<div class="flex items-center gap-4">
				<div class="text-5xl font-bold" class:text-green-600={percentWithinMOE >= 0.9} class:text-amber-600={percentWithinMOE < 0.9}>
					{formatPercent(percentWithinMOE)}
				</div>
				<div>
					<h4 class="font-semibold" class:text-green-800={percentWithinMOE >= 0.9} class:text-amber-800={percentWithinMOE < 0.9}>
						of polls fell within the margin of error
					</h4>
					<p class="text-sm" class:text-green-700={percentWithinMOE >= 0.9} class:text-amber-700={percentWithinMOE < 0.9}>
						With a 95% confidence level, we expect about 95% of polls to capture the true value.
						{#if percentWithinMOE >= 0.9}
							This is working as expected!
						{:else}
							Random variation means sometimes we'll see slightly different results.
						{/if}
					</p>
				</div>
			</div>
		</div>
	{/if}
</div>
