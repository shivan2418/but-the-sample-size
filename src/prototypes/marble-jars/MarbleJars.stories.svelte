<script module lang="ts">
	// PROTOTYPE, throwaway: stories for "Marble jars in Storybook: D rebuilt, and fresh takes" (#15).
	// G · Converge is the accepted widget. Variants the map owner didn’t take are on prototype/marble-jars-storybook.
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Frame from './Frame.svelte';
	import Converge from './Converge.svelte';

	const { Story } = defineMeta({
		title: 'Prototypes/marble-jars',
		parameters: { layout: 'fullscreen' },
		argTypes: {
			palette: { control: 'inline-radio', options: ['redBlue', 'neutral'] },
			speed: { control: { type: 'range', min: 0.25, max: 3, step: 0.25 } },
			third: { control: 'inline-radio', options: ['yellow', 'purple'] }
		},
		args: { palette: 'redBlue', speed: 0.75, third: 'yellow' }
	});

	const intro =
		'Forget people for a moment. Here is a jar of red and blue marbles. You can’t see inside, but you can take some out and count them.';
</script>

<Story name="G · 1 One jar" exportName="Converge1OneJar" args={{ startStage: 0, startTarget: 100 }}>
	{#snippet template(args)}
		<Frame palette={args.palette} third={args.third} {intro}>
			<Converge {...args} />
		</Frame>
	{/snippet}
</Story>
<Story
	name="G · 1 One jar, 20 counts"
	exportName="Converge1Runs"
	args={{ startStage: 0, startTarget: 100, startRuns: true }}
>
	{#snippet template(args)}
		<Frame palette={args.palette} third={args.third} {intro}>
			<Converge {...args} />
		</Frame>
	{/snippet}
</Story>
<Story
	name="G · 2 Jar of a million"
	exportName="Converge2BigJar"
	args={{ startStage: 1, startTarget: 1000 }}
>
	{#snippet template(args)}
		<Frame palette={args.palette} third={args.third} {intro}>
			<Converge {...args} />
		</Frame>
	{/snippet}
</Story>
<Story
	name="G · 3 Four colours, bars"
	exportName="Converge3Bars"
	args={{ startStage: 2, startTarget: 1000, multiDisplay: 'bars' }}
>
	{#snippet template(args)}
		<Frame palette={args.palette} third={args.third} {intro}>
			<Converge {...args} />
		</Frame>
	{/snippet}
</Story>
<Story
	name="G · 3 Four colours, 20 counts"
	exportName="Converge3Runs"
	args={{ startStage: 2, startTarget: 1000, startRuns: true }}
>
	{#snippet template(args)}
		<Frame palette={args.palette} third={args.third} {intro}>
			<Converge {...args} />
		</Frame>
	{/snippet}
</Story>
