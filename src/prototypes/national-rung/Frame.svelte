<script lang="ts">
	// PROTOTYPE, throwaway: the C2 · Plain compact page around the rung (#16), so it's judged in
	// context: the end of rung 6 above it and the answer below.
	import '../visual-style/tw.css';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div
	class="plain min-h-screen bg-bg px-4 pb-10 font-sans text-[17px]/[1.45] text-ink lg:px-8 lg:text-[19px]/normal"
	data-theme="light"
>
	<main class="mx-auto max-w-[40rem]">
		<section id="people-or-percentages" class="border-t border-line py-4">
			<h2 class="mb-3 text-[22px]/tight font-bold">
				<span class="font-normal text-muted">6 ·</span> People or percentages
			</h2>
			<p class="text-muted">Simulating people and simulating shares give the same answer.</p>
		</section>
		{@render children()}
		<section class="border-t border-line py-4">
			<h2 class="mb-3 text-[22px]/tight font-bold">
				<span class="font-normal text-muted">8 ·</span> Back to the objection
			</h2>
			<p class="border-l-[5px] border-line pl-3 text-xl/snug font-bold">
				1,200 is enough, if it’s random.
			</p>
		</section>
		<p class="border-t border-line pt-3 text-[15px] text-muted">
			Prototype, throwaway. Nothing here is final copy.
		</p>
	</main>
</div>
