<script lang="ts">
	import { requiredSampleSize, marginOfError, finitePopulationCorrection, formatMOE } from '$lib/utils/statistics';

	let targetMOE = $state(3); // percentage
	let confidenceLevel = $state(0.95);
	let showFPC = $state(false);
	let populationSize = $state(320_000_000);

	const calculatedSampleSize = $derived(requiredSampleSize(targetMOE / 100, 0.5, confidenceLevel));
	const actualMOE = $derived(marginOfError(calculatedSampleSize, 0.5, confidenceLevel) * 100);

	// FPC calculation
	const fpc = $derived(finitePopulationCorrection(populationSize, calculatedSampleSize));
	const adjustedMOE = $derived(actualMOE * fpc);

	const confidenceLevels = [
		{ value: 0.9, label: '90%', z: '1.645' },
		{ value: 0.95, label: '95%', z: '1.96' },
		{ value: 0.99, label: '99%', z: '2.576' }
	];
</script>

<div class="space-y-6">
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h3 class="text-lg font-semibold mb-4">Sample Size Calculator</h3>
		<p class="text-sm text-gray-600 mb-6">
			Find out how many people you need to survey to achieve your desired margin of error.
		</p>

		<div class="grid md:grid-cols-2 gap-8">
			<!-- Inputs -->
			<div class="space-y-6">
				<div>
					<label for="target-moe" class="block text-sm font-medium text-gray-700 mb-2">
						Desired Margin of Error: ±{targetMOE}%
					</label>
					<input
						id="target-moe"
						type="range"
						bind:value={targetMOE}
						min="0.5"
						max="10"
						step="0.5"
						class="w-full"
					/>
					<div class="flex justify-between text-xs text-gray-400 mt-1">
						<span>±0.5% (very precise)</span>
						<span>±10% (rough estimate)</span>
					</div>
				</div>

				<div>
					<span class="block text-sm font-medium text-gray-700 mb-2">Confidence Level</span>
					<div class="flex gap-2" role="group" aria-label="Confidence level selection">
						{#each confidenceLevels as level (level.value)}
							<button
								onclick={() => (confidenceLevel = level.value)}
								class="flex-1 py-2 px-4 rounded-lg border-2 text-sm font-medium transition-colors"
								class:border-blue-500={confidenceLevel === level.value}
								class:bg-blue-50={confidenceLevel === level.value}
								class:text-blue-700={confidenceLevel === level.value}
								class:border-gray-200={confidenceLevel !== level.value}
								class:hover:border-gray-300={confidenceLevel !== level.value}
							>
								{level.label}
							</button>
						{/each}
					</div>
				</div>
			</div>

			<!-- Result -->
			<div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6">
				<div class="text-center">
					<p class="text-sm text-gray-600 mb-2">Required Sample Size</p>
					<p class="text-5xl font-bold text-blue-600">{calculatedSampleSize.toLocaleString()}</p>
					<p class="text-sm text-gray-500 mt-2">
						Actual MOE: {formatMOE(actualMOE / 100)}
					</p>
				</div>
			</div>
		</div>
	</div>

	<!-- Formula reveal -->
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h4 class="font-semibold mb-4">The Formula</h4>
		<div class="bg-gray-50 rounded-lg p-4 font-mono text-center text-lg">
			n = (z² × p × (1-p)) / MOE²
		</div>
		<p class="text-sm text-gray-600 mt-4">
			Where <strong>z</strong> is the z-score for your confidence level ({confidenceLevels.find(l => l.value === confidenceLevel)?.z}),
			<strong>p</strong> is the expected proportion (0.5 for maximum variance),
			and <strong>MOE</strong> is your desired margin of error.
		</p>
		<p class="text-sm text-gray-600 mt-2 font-medium">
			Notice: <span class="text-blue-600">Population size doesn't appear in this formula!</span>
		</p>
	</div>

	<!-- FPC section -->
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<div class="flex items-center justify-between mb-4">
			<h4 class="font-semibold">Finite Population Correction (Advanced)</h4>
			<button
				onclick={() => (showFPC = !showFPC)}
				class="text-sm text-blue-600 hover:text-blue-700"
			>
				{showFPC ? 'Hide' : 'Show'} details
			</button>
		</div>

		{#if showFPC}
			<div class="space-y-4">
				<p class="text-sm text-gray-600">
					The finite population correction (FPC) only matters when you're sampling a large fraction
					of the total population (more than 5%). For national polls, it's negligible.
				</p>

				<div>
					<label for="pop-size" class="block text-sm font-medium text-gray-700 mb-2">
						Population Size: {populationSize.toLocaleString()}
					</label>
					<input
						id="pop-size"
						type="range"
						bind:value={populationSize}
						min="1000"
						max="400000000"
						step="1000"
						class="w-full"
					/>
				</div>

				<div class="grid grid-cols-3 gap-4 text-center">
					<div class="bg-gray-50 rounded-lg p-4">
						<p class="text-xs text-gray-500">Sampling Fraction</p>
						<p class="text-lg font-semibold">
							{((calculatedSampleSize / populationSize) * 100).toFixed(4)}%
						</p>
					</div>
					<div class="bg-gray-50 rounded-lg p-4">
						<p class="text-xs text-gray-500">FPC Factor</p>
						<p class="text-lg font-semibold">{fpc.toFixed(4)}</p>
					</div>
					<div class="bg-gray-50 rounded-lg p-4">
						<p class="text-xs text-gray-500">Adjusted MOE</p>
						<p class="text-lg font-semibold">{formatMOE(adjustedMOE / 100)}</p>
					</div>
				</div>

				<p class="text-sm text-gray-500 italic">
					{#if calculatedSampleSize / populationSize <= 0.05}
						The sampling fraction is below 5%, so FPC makes essentially no difference.
					{:else}
						The sampling fraction is above 5%, so FPC slightly improves your margin of error.
					{/if}
				</p>
			</div>
		{/if}
	</div>
</div>
