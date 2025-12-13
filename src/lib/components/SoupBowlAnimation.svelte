<script lang="ts">
	import { Spring } from 'svelte/motion';
	import { fade, fly } from 'svelte/transition';

	let { potSize = 'small' }: { potSize?: 'small' | 'large' } = $props();

	let showSpoon = $state(false);
	let isTasting = $state(false);
	let showResult = $state(false);

	const spoonX = new Spring(150, { stiffness: 0.1, damping: 0.5 });
	const spoonY = new Spring(20, { stiffness: 0.1, damping: 0.5 });

	// Seed for consistent random generation per potSize
	let seed = $state(1);

	// Seeded random for reproducible particles
	function seededRandom(s: number): number {
		const x = Math.sin(s) * 10000;
		return x - Math.floor(x);
	}

	// Generate random particle positions for the soup
	const particlePositions = $derived.by(() => {
		const count = potSize === 'large' ? 80 : 40;
		const particles: Array<{ id: number; x: number; y: number; color: string }> = [];
		for (let i = 0; i < count; i++) {
			const s = seed + i;
			const angle = seededRandom(s) * Math.PI * 2;
			const radiusX = 60 + seededRandom(s + 1) * 50;
			const radiusY = 20 + seededRandom(s + 2) * 15;
			particles.push({
				id: i,
				x: 150 + Math.cos(angle) * radiusX * seededRandom(s + 3),
				y: 85 + Math.sin(angle) * radiusY * seededRandom(s + 4),
				color: seededRandom(s + 5) > 0.3 ? '#ff6b6b' : '#ffd93d'
			});
		}
		return particles;
	});

	async function animateTaste() {
		showSpoon = true;
		showResult = false;

		// Move spoon down into soup
		await new Promise((r) => setTimeout(r, 300));
		spoonY.set(70);

		await new Promise((r) => setTimeout(r, 800));
		isTasting = true;

		// Move spoon up
		await new Promise((r) => setTimeout(r, 500));
		spoonY.set(20);

		await new Promise((r) => setTimeout(r, 600));
		showResult = true;
	}

	function reset() {
		showSpoon = false;
		isTasting = false;
		showResult = false;
		spoonY.set(20, { instant: true });
	}
</script>

<div class="flex flex-col items-center gap-4">
	<div class="text-center mb-2">
		<span class="text-sm text-gray-500">
			{potSize === 'large' ? '1000 gallon pot' : '1 gallon pot'}
		</span>
	</div>

	<svg viewBox="0 0 300 180" class="w-full max-w-xs">
		<!-- Pot -->
		<ellipse cx="150" cy="130" rx="120" ry="30" fill="#4a4a4a" />
		<rect x="30" y="70" width="240" height="60" fill="#5a5a5a" rx="5" />
		<ellipse cx="150" cy="70" rx="120" ry="30" fill="#6a6a6a" />

		<!-- Soup surface -->
		<ellipse cx="150" cy="85" rx="110" ry="25" fill="#f97316" />

		<!-- Particles (spices) -->
		{#each particlePositions as particle (particle.id)}
			<circle cx={particle.x} cy={particle.y} r="3" fill={particle.color} opacity="0.8" />
		{/each}

		<!-- Spoon -->
		{#if showSpoon}
			<g transform="translate({spoonX.current}, {spoonY.current})" transition:fade>
				<!-- Spoon handle -->
				<rect x="-3" y="-50" width="6" height="60" fill="#c0c0c0" rx="2" />
				<!-- Spoon bowl -->
				<ellipse cx="0" cy="15" rx="15" ry="8" fill="#d0d0d0" />
				{#if isTasting}
					<!-- Soup in spoon -->
					<ellipse cx="0" cy="14" rx="12" ry="6" fill="#f97316" />
					<!-- A few particles in the spoon -->
					<circle cx="-4" cy="13" r="2" fill="#ff6b6b" />
					<circle cx="3" cy="15" r="2" fill="#ffd93d" />
					<circle cx="0" cy="12" r="2" fill="#ff6b6b" />
				{/if}
			</g>
		{/if}
	</svg>

	<div class="flex gap-2">
		<button
			onclick={animateTaste}
			disabled={showSpoon && !showResult}
			class="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
		>
			Taste the soup
		</button>
		{#if showResult}
			<button onclick={reset} class="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600">
				Reset
			</button>
		{/if}
	</div>

	{#if showResult}
		<div transition:fly={{ y: 20 }} class="text-center p-4 bg-green-100 rounded-lg max-w-xs">
			<p class="text-green-800 font-medium">Just right!</p>
			<p class="text-green-700 text-sm mt-1">
				One spoonful tells you about the whole pot, whether it's 1 gallon or 1000 gallons.
			</p>
		</div>
	{/if}
</div>
