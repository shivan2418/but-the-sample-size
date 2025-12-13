<script lang="ts">
	import { Chart, Svg, Axis, Spline, Highlight, Points, Tooltip } from 'layerchart';
	import { scaleLinear } from 'd3-scale';
	import { generateMOECurveData, marginOfError, formatMOE } from '$lib/utils/statistics';

	let sampleSize = $state(1200);

	// Generate the curve data
	const curveData = generateMOECurveData(50, 5000, 100);

	// Current sample size point
	const currentMOE = $derived(marginOfError(sampleSize) * 100);

	// Notable sample sizes to mark
	const notableSizes = [
		{ n: 400, label: '400', moe: marginOfError(400) * 100 },
		{ n: 1000, label: '1,000', moe: marginOfError(1000) * 100 },
		{ n: 1200, label: '1,200 (typical poll)', moe: marginOfError(1200) * 100 },
		{ n: 2000, label: '2,000', moe: marginOfError(2000) * 100 }
	];
</script>

<div class="space-y-6">
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h3 class="text-lg font-semibold mb-4">Margin of Error vs Sample Size</h3>
		<p class="text-sm text-gray-600 mb-4">
			The margin of error follows the formula MOE = 1/√n. Notice how it drops sharply at first,
			then flattens out — meaning bigger samples have diminishing returns.
		</p>

		<div class="h-80 w-full">
			<Chart
				data={curveData}
				x="n"
				y="moe"
				xScale={scaleLinear()}
				yScale={scaleLinear()}
				padding={{ top: 20, right: 20, bottom: 40, left: 50 }}
			>
				<Svg>
					<Axis placement="left" label="Margin of Error (%)" grid />
					<Axis placement="bottom" label="Sample Size" />
					<Spline class="stroke-blue-500 stroke-2 fill-none" />
				</Svg>
			</Chart>
		</div>

		<!-- Slider control -->
		<div class="mt-6">
			<label for="moe-sample-size" class="block text-sm font-medium text-gray-700 mb-2">
				Sample Size: {sampleSize.toLocaleString()} → MOE: {formatMOE(currentMOE / 100)}
			</label>
			<input
				id="moe-sample-size"
				type="range"
				bind:value={sampleSize}
				min="50"
				max="5000"
				step="50"
				class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
			/>
		</div>
	</div>

	<!-- Notable sample sizes -->
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h4 class="font-semibold mb-4">Common Sample Sizes</h4>
		<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
			{#each notableSizes as item (item.n)}
				<button
					onclick={() => (sampleSize = item.n)}
					class="p-4 rounded-lg border-2 text-left transition-colors"
					class:border-blue-500={sampleSize === item.n}
					class:bg-blue-50={sampleSize === item.n}
					class:border-gray-200={sampleSize !== item.n}
					class:hover:border-gray-300={sampleSize !== item.n}
				>
					<div class="text-2xl font-bold text-gray-900">{item.label}</div>
					<div class="text-sm text-gray-500">MOE: ±{item.moe.toFixed(1)}%</div>
				</button>
			{/each}
		</div>
	</div>

	<!-- Key insight -->
	<div class="bg-amber-50 border border-amber-200 rounded-xl p-6">
		<h4 class="font-semibold text-amber-800 mb-2">The Diminishing Returns</h4>
		<p class="text-amber-700">
			Going from 100 to 1,000 samples cuts the margin of error from ±10% to ±3.1%.
			But going from 1,000 to 10,000 only improves it from ±3.1% to ±1%.
			This is why pollsters typically stop at 1,000-2,000 — the extra precision isn't worth the cost.
		</p>
	</div>
</div>
