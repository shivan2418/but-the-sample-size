<script lang="ts">
	import type { Snippet } from 'svelte';

	let { id, title, children }: { id: string; title: string; children?: Snippet } = $props();
</script>

<section {id} aria-labelledby="{id}-title">
	<h2 id="{id}-title">{title}</h2>
	{#if children}
		{@render children()}
	{:else}
		<p class="placeholder">This rung isn't built yet.</p>
	{/if}
</section>

<style>
	section {
		padding-block: 3rem;
		scroll-margin-top: 1rem;
	}

	.placeholder {
		color: #666;
		font-style: italic;
	}
</style>
