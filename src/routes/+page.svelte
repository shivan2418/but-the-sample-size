<script lang="ts">
	import SoupBowlAnimation from '$lib/components/SoupBowlAnimation.svelte';
	import NormalDistributionDemo from '$lib/components/NormalDistributionDemo.svelte';
	import SamplingSimulator from '$lib/components/SamplingSimulator.svelte';
	import MarginOfErrorChart from '$lib/components/MarginOfErrorChart.svelte';
	import RepeatedSamplingDemo from '$lib/components/RepeatedSamplingDemo.svelte';
	import SampleSizeCalculator from '$lib/components/SampleSizeCalculator.svelte';
</script>

<svelte:head>
	<title>Sample Size Explainer | Why 1,200 People Can Represent 320 Million</title>
	<meta
		name="description"
		content="Interactive demonstrations explaining why sample size, not population size, determines polling accuracy."
	/>
</svelte:head>

<div class="min-h-screen bg-gray-50">
	<!-- Hero Section -->
	<section class="bg-gradient-to-br from-indigo-600 to-purple-700 text-white py-16 px-4">
		<div class="max-w-4xl mx-auto text-center">
			<h1 class="text-4xl md:text-5xl font-bold mb-6">
				"How Can 1,200 People Represent 320 Million?"
			</h1>
			<p class="text-xl md:text-2xl text-indigo-100 mb-8">
				You've seen a poll with only 1,200 respondents and wondered how that could possibly be accurate.
				<br class="hidden md:block" />
				Let's explore why it actually works.
			</p>
			<div class="inline-block bg-white/10 backdrop-blur rounded-xl px-6 py-4">
				<p class="text-lg">
					<span class="font-semibold">The surprising truth:</span> Population size barely matters.
					<br />
					A sample of 1,200 from a town of 10,000 is just as accurate as 1,200 from 320 million.
				</p>
			</div>
		</div>
	</section>

	<div class="max-w-5xl mx-auto px-4 py-12 space-y-20">
		<!-- Section 1: The Soup Analogy -->
		<section>
			<div class="text-center mb-8">
				<span class="inline-block px-3 py-1 bg-orange-100 text-orange-700 rounded-full text-sm font-medium mb-4">
					The Intuition
				</span>
				<h2 class="text-3xl font-bold text-gray-900 mb-4">The Soup Bowl Analogy</h2>
				<p class="text-lg text-gray-600 max-w-2xl mx-auto">
					Imagine you're tasting soup to check if it's properly seasoned.
					Do you need to taste the whole pot? Of course not — just one well-stirred spoonful tells you everything.
				</p>
			</div>

			<div class="grid md:grid-cols-2 gap-8 items-center">
				<SoupBowlAnimation potSize="small" />
				<SoupBowlAnimation potSize="large" />
			</div>

			<div class="mt-8 bg-orange-50 border border-orange-200 rounded-xl p-6 text-center">
				<p class="text-orange-800">
					<strong>The key insight:</strong> Whether the pot holds 1 gallon or 1,000 gallons,
					a single well-mixed spoonful gives you the same information about the seasoning.
					The same principle applies to statistical sampling.
				</p>
			</div>
		</section>

		<!-- Section 2: Normal Distribution Demo -->
		<section>
			<div class="text-center mb-8">
				<span class="inline-block px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full text-sm font-medium mb-4">
					Watch It Happen
				</span>
				<h2 class="text-3xl font-bold text-gray-900 mb-4">The Bell Curve Emerges</h2>
				<p class="text-lg text-gray-600 max-w-2xl mx-auto">
					Let's randomly sample men from the US and measure their heights.
					Each individual is random, but watch how a pattern emerges as the samples accumulate.
				</p>
			</div>

			<NormalDistributionDemo />
		</section>

		<!-- Section 3: Interactive Sampling Simulator -->
		<section>
			<div class="text-center mb-8">
				<span class="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium mb-4">
					See It In Action
				</span>
				<h2 class="text-3xl font-bold text-gray-900 mb-4">The Sampling Simulator</h2>
				<p class="text-lg text-gray-600 max-w-2xl mx-auto">
					Take samples from both a small town and the entire United States.
					Notice how the results are remarkably similar with the same sample size.
				</p>
			</div>

			<SamplingSimulator />
		</section>

		<!-- Section 3: Margin of Error Explained -->
		<section>
			<div class="text-center mb-8">
				<span class="inline-block px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm font-medium mb-4">
					The Math
				</span>
				<h2 class="text-3xl font-bold text-gray-900 mb-4">Understanding Margin of Error</h2>
				<p class="text-lg text-gray-600 max-w-2xl mx-auto">
					The margin of error follows a simple formula: MOE = 1/√n.
					This means doubling precision requires quadrupling the sample size.
				</p>
			</div>

			<MarginOfErrorChart />
		</section>

		<!-- Section 4: Repeated Sampling Demo -->
		<section>
			<div class="text-center mb-8">
				<span class="inline-block px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-medium mb-4">
					The Evidence
				</span>
				<h2 class="text-3xl font-bold text-gray-900 mb-4">What Happens Over Many Polls?</h2>
				<p class="text-lg text-gray-600 max-w-2xl mx-auto">
					If we ran hundreds of polls, about 95% would capture the true value within their margin of error.
					This is what "95% confidence" actually means.
				</p>
			</div>

			<RepeatedSamplingDemo />
		</section>

		<!-- Section 5: Calculator & Takeaways -->
		<section>
			<div class="text-center mb-8">
				<span class="inline-block px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-medium mb-4">
					Tools
				</span>
				<h2 class="text-3xl font-bold text-gray-900 mb-4">Sample Size Calculator</h2>
				<p class="text-lg text-gray-600 max-w-2xl mx-auto">
					How many people do you actually need to survey?
					The answer might surprise you — and it has nothing to do with population size.
				</p>
			</div>

			<SampleSizeCalculator />
		</section>

		<!-- Real-World Examples -->
		<section class="bg-white rounded-2xl p-8 shadow-sm border border-gray-200">
			<h2 class="text-2xl font-bold text-gray-900 mb-6 text-center">Real-World Examples</h2>

			<div class="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
				<div class="text-center p-4">
					<div class="text-4xl font-bold text-blue-600 mb-2">~1,200</div>
					<div class="font-medium text-gray-900">Typical Election Poll</div>
					<div class="text-sm text-gray-500">Gallup, Pew Research</div>
					<div class="text-xs text-gray-400 mt-1">MOE: ±2.8%</div>
				</div>

				<div class="text-center p-4">
					<div class="text-4xl font-bold text-green-600 mb-2">~40,000</div>
					<div class="font-medium text-gray-900">Nielsen TV Ratings</div>
					<div class="text-sm text-gray-500">For all US television</div>
					<div class="text-xs text-gray-400 mt-1">MOE: ±0.5%</div>
				</div>

				<div class="text-center p-4">
					<div class="text-4xl font-bold text-purple-600 mb-2">~100,000</div>
					<div class="font-medium text-gray-900">Exit Polls</div>
					<div class="text-sm text-gray-500">Major elections</div>
					<div class="text-xs text-gray-400 mt-1">MOE: ±0.3%</div>
				</div>

				<div class="text-center p-4">
					<div class="text-4xl font-bold text-orange-600 mb-2">~60,000</div>
					<div class="font-medium text-gray-900">Consumer Confidence</div>
					<div class="text-sm text-gray-500">Monthly surveys</div>
					<div class="text-xs text-gray-400 mt-1">MOE: ±0.4%</div>
				</div>
			</div>
		</section>

		<!-- Final Takeaways -->
		<section class="bg-gradient-to-br from-gray-900 to-gray-800 text-white rounded-2xl p-8">
			<h2 class="text-2xl font-bold mb-6 text-center">Key Takeaways</h2>

			<div class="grid md:grid-cols-3 gap-6">
				<div class="bg-white/10 rounded-xl p-6">
					<div class="text-3xl mb-3">1</div>
					<h3 class="font-semibold mb-2">Sample Size Matters</h3>
					<p class="text-gray-300 text-sm">
						The margin of error depends on how many people you survey, not how many exist in the population.
					</p>
				</div>

				<div class="bg-white/10 rounded-xl p-6">
					<div class="text-3xl mb-3">2</div>
					<h3 class="font-semibold mb-2">Population Size Doesn't</h3>
					<p class="text-gray-300 text-sm">
						1,200 people from a town of 10,000 is just as reliable as 1,200 from a country of 320 million.
					</p>
				</div>

				<div class="bg-white/10 rounded-xl p-6">
					<div class="text-3xl mb-3">3</div>
					<h3 class="font-semibold mb-2">Diminishing Returns</h3>
					<p class="text-gray-300 text-sm">
						Going from 1,000 to 2,000 respondents only improves MOE from ±3.1% to ±2.2%. Often not worth the cost.
					</p>
				</div>
			</div>
		</section>

		<!-- Footer -->
		<footer class="text-center text-gray-500 text-sm py-8">
			<p>
				Built to help people understand statistical sampling.
				<br />
				The next time you see "1,200 respondents," you'll know why that's enough.
			</p>
		</footer>
	</div>
</div>
