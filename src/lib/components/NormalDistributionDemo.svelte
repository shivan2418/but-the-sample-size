<script lang="ts">
	import { randomNormal, inchesToFeetInches, mean, standardDeviation } from '$lib/utils/statistics';
	import { fly } from 'svelte/transition';

	// US male height statistics (in inches)
	const TRUE_MEAN = 69.5; // ~5'9.5"
	const TRUE_STD_DEV = 2.8;

	// Histogram configuration
	const MIN_HEIGHT = 60; // 5'0"
	const MAX_HEIGHT = 79; // 6'7"
	const BIN_WIDTH = 1; // 1 inch bins
	const NUM_BINS = (MAX_HEIGHT - MIN_HEIGHT) / BIN_WIDTH;

	// State
	let samples = $state<number[]>([]);
	let fallingPerson = $state<{ height: number; x: number; id: number } | null>(null);
	let isRunning = $state(false);
	let speed = $state(100); // ms between samples
	let sampleIdCounter = $state(0);

	// Derived statistics
	const sampleMean = $derived(mean(samples));
	const sampleStdDev = $derived(standardDeviation(samples));

	// Create histogram bins
	const histogram = $derived.by(() => {
		const bins: number[] = new Array(NUM_BINS).fill(0);
		for (const sample of samples) {
			const binIndex = Math.floor((sample - MIN_HEIGHT) / BIN_WIDTH);
			if (binIndex >= 0 && binIndex < NUM_BINS) {
				bins[binIndex]++;
			}
		}
		return bins;
	});

	const maxBinCount = $derived(Math.max(...histogram, 1));

	// Convert bin index to height value
	function binToHeight(binIndex: number): number {
		return MIN_HEIGHT + binIndex * BIN_WIDTH + BIN_WIDTH / 2;
	}

	// Get x position for a height (as percentage)
	function heightToX(height: number): number {
		return ((height - MIN_HEIGHT) / (MAX_HEIGHT - MIN_HEIGHT)) * 100;
	}

	// Sample one person
	async function sampleOnePerson() {
		const height = randomNormal(TRUE_MEAN, TRUE_STD_DEV);
		const clampedHeight = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT - 0.01, height));
		const x = heightToX(clampedHeight);

		sampleIdCounter++;
		fallingPerson = { height: clampedHeight, x, id: sampleIdCounter };

		// Wait for animation
		await new Promise((r) => setTimeout(r, 400));

		samples = [...samples, clampedHeight];
		fallingPerson = null;
	}

	// Run continuous sampling
	async function startSampling() {
		isRunning = true;
		while (isRunning && samples.length < 1000) {
			await sampleOnePerson();
			await new Promise((r) => setTimeout(r, speed));
		}
		isRunning = false;
	}

	function stopSampling() {
		isRunning = false;
	}

	function reset() {
		isRunning = false;
		samples = [];
		fallingPerson = null;
	}

	// Add many samples at once (for demo)
	function addManySamples(count: number) {
		const newSamples: number[] = [];
		for (let i = 0; i < count; i++) {
			const height = randomNormal(TRUE_MEAN, TRUE_STD_DEV);
			const clampedHeight = Math.max(MIN_HEIGHT, Math.min(MAX_HEIGHT - 0.01, height));
			newSamples.push(clampedHeight);
		}
		samples = [...samples, ...newSamples];
	}
</script>

<div class="space-y-6">
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h3 class="text-lg font-semibold mb-2">The Normal Distribution Emerges</h3>
		<p class="text-sm text-gray-600 mb-4">
			Watch as we randomly sample men from the US population. Each person's height is random,
			but as we collect more samples, the familiar bell curve emerges.
		</p>

		<!-- Visualization area -->
		<div class="relative bg-gray-50 rounded-lg overflow-hidden" style="height: 350px;">
			<!-- Person icon dropping -->
			{#if fallingPerson}
				<div
					class="absolute z-10 flex flex-col items-center transition-all duration-300"
					style="left: {fallingPerson.x}%; top: 0; transform: translateX(-50%);"
					in:fly={{ y: -50, duration: 300 }}
					out:fly={{ y: 100, duration: 100 }}
				>
					<svg width="24" height="40" viewBox="0 0 24 40" class="text-blue-500">
						<!-- Simple person icon -->
						<circle cx="12" cy="6" r="5" fill="currentColor" />
						<path
							d="M12 12 L12 26 M12 16 L4 22 M12 16 L20 22 M12 26 L6 38 M12 26 L18 38"
							stroke="currentColor"
							stroke-width="2"
							stroke-linecap="round"
							fill="none"
						/>
					</svg>
					<span class="text-xs font-medium text-blue-600 mt-1">
						{inchesToFeetInches(fallingPerson.height)}
					</span>
				</div>
			{/if}

			<!-- Histogram -->
			<div class="absolute bottom-0 left-0 right-0 flex items-end" style="height: 250px; padding: 0 20px;">
				{#each histogram as count, i (i)}
					{@const height = binToHeight(i)}
					{@const isNearMean = Math.abs(height - TRUE_MEAN) < TRUE_STD_DEV}
					{@const isWithin2Std = Math.abs(height - TRUE_MEAN) < 2 * TRUE_STD_DEV}
					<div
						class="flex-1 mx-px transition-all duration-200 rounded-t"
						class:bg-blue-500={isNearMean}
						class:bg-blue-400={!isNearMean && isWithin2Std}
						class:bg-blue-300={!isWithin2Std}
						style="height: {(count / maxBinCount) * 100}%"
						title="{inchesToFeetInches(height)}: {count} people"
					></div>
				{/each}
			</div>

			<!-- X-axis labels -->
			<div class="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500 px-5 pb-1">
				<span>5'0"</span>
				<span>5'4"</span>
				<span>5'9"</span>
				<span>6'2"</span>
				<span>6'7"</span>
			</div>

			<!-- True mean indicator -->
			<div
				class="absolute bottom-0 w-0.5 bg-green-500 opacity-50"
				style="left: {heightToX(TRUE_MEAN)}%; height: 250px; transform: translateX(-50%);"
			></div>
		</div>

		<!-- Controls -->
		<div class="flex flex-wrap gap-3 mt-6">
			{#if !isRunning}
				<button
					onclick={sampleOnePerson}
					disabled={samples.length >= 1000}
					class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
				>
					Sample 1 Person
				</button>
				<button
					onclick={startSampling}
					disabled={samples.length >= 1000}
					class="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
				>
					Start Continuous
				</button>
				<button
					onclick={() => addManySamples(100)}
					disabled={samples.length >= 1000}
					class="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 transition-colors"
				>
					+100 Samples
				</button>
			{:else}
				<button
					onclick={stopSampling}
					class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
				>
					Stop
				</button>
			{/if}
			<button
				onclick={reset}
				class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
			>
				Reset
			</button>

			<div class="flex items-center gap-2 ml-auto">
				<label for="speed-slider" class="text-sm text-gray-600">Speed:</label>
				<input
					id="speed-slider"
					type="range"
					bind:value={speed}
					min="20"
					max="500"
					step="20"
					class="w-24"
				/>
			</div>
		</div>
	</div>

	<!-- Statistics panel -->
	<div class="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
		<h4 class="font-semibold mb-4">Sample Statistics vs True Population</h4>

		<div class="grid grid-cols-2 md:grid-cols-4 gap-4">
			<div class="text-center p-4 bg-gray-50 rounded-lg">
				<div class="text-3xl font-bold text-blue-600">{samples.length}</div>
				<div class="text-sm text-gray-500">Sample Size</div>
			</div>

			<div class="text-center p-4 bg-gray-50 rounded-lg">
				<div class="text-2xl font-bold text-gray-900">
					{samples.length > 0 ? inchesToFeetInches(sampleMean) : '—'}
				</div>
				<div class="text-sm text-gray-500">Sample Mean</div>
				<div class="text-xs text-green-600">True: {inchesToFeetInches(TRUE_MEAN)}</div>
			</div>

			<div class="text-center p-4 bg-gray-50 rounded-lg">
				<div class="text-2xl font-bold text-gray-900">
					{samples.length > 1 ? sampleStdDev.toFixed(2) + '"' : '—'}
				</div>
				<div class="text-sm text-gray-500">Sample Std Dev</div>
				<div class="text-xs text-green-600">True: {TRUE_STD_DEV}"</div>
			</div>

			<div class="text-center p-4 bg-gray-50 rounded-lg">
				<div class="text-2xl font-bold" class:text-green-600={samples.length >= 30} class:text-amber-600={samples.length < 30}>
					{samples.length >= 30 ? 'Yes!' : 'Not yet'}
				</div>
				<div class="text-sm text-gray-500">Bell Curve Visible?</div>
				<div class="text-xs text-gray-400">Need ~30+ samples</div>
			</div>
		</div>

		{#if samples.length >= 30}
			<div class="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
				<p class="text-blue-800 text-sm">
					<strong>The Central Limit Theorem in action!</strong> Even though each individual height is random,
					the distribution of our samples follows a predictable bell curve. The more samples we collect,
					the closer our sample statistics get to the true population values.
				</p>
			</div>
		{/if}
	</div>
</div>
