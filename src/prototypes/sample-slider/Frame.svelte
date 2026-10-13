<script lang="ts">
	// PROTOTYPE, throwaway: the C2 · Plain compact page around the control (#16).
	import '../visual-style/tw.css';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
</script>

<div
	class="plain min-h-screen bg-bg px-4 py-6 font-sans text-[17px]/[1.45] text-ink"
	data-theme="light"
>
	<main class="mx-auto max-w-[40rem]">{@render children()}</main>
</div>
