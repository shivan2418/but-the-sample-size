<script module lang="ts">
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Rung from './Rung.svelte';

	const { Story } = defineMeta({
		title: 'Page/Rung',
		component: Rung,
		args: { id: 'marbles', title: 'A handful of marbles' }
	});
</script>

<Story name="Placeholder" />

<Story name="With content">
	{#snippet template(args)}
		<Rung {...args}>
			<p>A widget mounts here.</p>
		</Rung>
	{/snippet}
</Story>
