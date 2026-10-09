<script module lang="ts">
	// PROTOTYPE, throwaway: the sample-size slider for the marble jars, one story per jar.
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Frame from './Frame.svelte';
	import SampleSlider from './SampleSlider.svelte';

	const { Story } = defineMeta({
		title: 'Prototypes/sample-slider',
		parameters: { layout: 'fullscreen' },
		argTypes: {
			scale: { control: 'inline-radio', options: ['linear', 'log'] },
			speed: { control: { type: 'range', min: 0.25, max: 3, step: 0.25 } }
		},
		args: { speed: 1 }
	});
</script>

<Story name="Jar of 1,000" exportName="SmallJar" args={{ jar: 1000, scale: 'linear' }}>
	{#snippet template(args)}
		<Frame><SampleSlider {...args} /></Frame>
	{/snippet}
</Story>
<Story
	name="Jar of a million, log track"
	exportName="BigJarLog"
	args={{ jar: 1_000_000, scale: 'log', presets: [10, 100, 1000, 10_000, 100_000] }}
>
	{#snippet template(args)}
		<Frame><SampleSlider {...args} /></Frame>
	{/snippet}
</Story>
<Story
	name="Jar of a million, straight track"
	exportName="BigJarLinear"
	args={{ jar: 1_000_000, scale: 'linear', presets: [10, 100, 1000, 10_000, 100_000] }}
>
	{#snippet template(args)}
		<Frame><SampleSlider {...args} /></Frame>
	{/snippet}
</Story>
