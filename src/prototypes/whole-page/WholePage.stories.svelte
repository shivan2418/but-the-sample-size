<script module lang="ts">
	// PROTOTYPE, throwaway: the whole page as it stands, at phone, small-phone and desktop width.
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Page from './Page.svelte';

	const { Story } = defineMeta({
		title: 'Prototypes/whole-page',
		parameters: { layout: 'fullscreen' },
		argTypes: { speed: { control: { type: 'range', min: 0.25, max: 3, step: 0.25 } } },
		args: { speed: 0.75 }
	});
</script>

<Story name="Phone" exportName="Phone">
	{#snippet template(args)}
		<Page {...args} />
	{/snippet}
</Story>
<Story
	name="320px"
	exportName="Small"
	globals={{ viewport: { value: 'smallPhone', isRotated: false } }}
>
	{#snippet template(args)}
		<Page {...args} />
	{/snippet}
</Story>
<Story
	name="Desktop"
	exportName="Desktop"
	globals={{ viewport: { value: 'desktop', isRotated: false } }}
>
	{#snippet template(args)}
		<Page {...args} />
	{/snippet}
</Story>
