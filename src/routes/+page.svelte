<script lang="ts">
	import Rung from '$lib/components/Rung.svelte';
	import { rungs } from '$lib/rungs';
</script>

<svelte:head>
	<title>But the sample size…</title>
	<meta
		name="description"
		content="Why a random poll of about 1,200 people can describe a country of 300 million."
	/>
</svelte:head>

<main>
	<header>
		<h1>But the sample size…</h1>
		<nav aria-label="Rungs">
			<ol>
				{#each rungs as rung (rung.id)}
					<li><a href="#{rung.id}">{rung.title}</a></li>
				{/each}
			</ol>
		</nav>
	</header>

	{#each rungs as rung (rung.id)}
		<Rung id={rung.id} title={rung.title} />
	{/each}
</main>

<style>
	main {
		max-width: 40rem;
		margin-inline: auto;
		padding-inline: 1rem;
	}
</style>
