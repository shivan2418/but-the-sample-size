<script lang="ts">
	// PROTOTYPE, throwaway: shows the whole-page prototype on the dev server for feedback. Only on
	// prototype/whole-page; it breaks the rule that nothing imports from src/prototypes, so it never
	// merges.
	import Page from '../../prototypes/whole-page/Page.svelte';
</script>

<svelte:head><title>But the sample size… (prototype)</title></svelte:head>

<Page />
