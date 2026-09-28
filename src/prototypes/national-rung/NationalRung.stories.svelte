<script module lang="ts">
	// PROTOTYPE, throwaway: stories for "How the national rung looks and behaves" (#31). One first
	// draft of the rung, at its clean start and at the starting states worth checking.
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Frame from './Frame.svelte';
	import NationalRung from './NationalRung.svelte';

	const { Story } = defineMeta({
		title: 'Prototypes/national-rung',
		parameters: { layout: 'fullscreen' },
		args: { startN: 1200, startPop: 155_238_302 }
	});
</script>

<Story name="Draft · Clean start" exportName="DraftStart">
	{#snippet template(args)}
		<Frame><NationalRung {...args} /></Frame>
	{/snippet}
</Story>
<Story name="Draft · Charlotte-sized" exportName="DraftCharlotte" args={{ startPop: 645_000 }}>
	{#snippet template(args)}
		<Frame><NationalRung {...args} /></Frame>
	{/snippet}
</Story>
<Story
	name="Draft · Sample a big share"
	exportName="DraftBigShare"
	args={{ startN: 12_000, startPop: 20_000 }}
>
	{#snippet template(args)}
		<Frame><NationalRung {...args} /></Frame>
	{/snippet}
</Story>
<Story
	name="Draft · 320px"
	exportName="DraftSmall"
	globals={{ viewport: { value: 'smallPhone', isRotated: false } }}
>
	{#snippet template(args)}
		<Frame><NationalRung {...args} /></Frame>
	{/snippet}
</Story>
