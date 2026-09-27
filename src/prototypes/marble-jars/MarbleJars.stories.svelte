<script module lang="ts">
	// PROTOTYPE, throwaway: stories for "Marble jars in Storybook: D rebuilt, and fresh takes" (#15).
	// Every story takes `palette`, `speed` (and `axisRange` where there's a chart) as controls.
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Frame from './Frame.svelte';
	import SideJar from './SideJar.svelte';
	import Pour from './Pour.svelte';
	import TwentyHands from './TwentyHands.svelte';
	import Converge from './Converge.svelte';

	const { Story } = defineMeta({
		title: 'Prototypes/marble-jars',
		parameters: { layout: 'fullscreen' },
		argTypes: {
			palette: { control: 'inline-radio', options: ['redBlue', 'neutral'] },
			speed: { control: { type: 'range', min: 0.25, max: 3, step: 0.25 } },
			axisRange: { control: 'inline-radio', options: ['full', 'zoomed'] },
			third: { control: 'inline-radio', options: ['yellow', 'purple'] },
			multiDisplay: { control: 'inline-radio', options: ['bars', 'markers'] }
		},
		args: { palette: 'redBlue', speed: 1, axisRange: 'full', third: 'yellow' }
	});

	const intro =
		'Forget people for a moment. Here is a jar of red and blue marbles. You can’t see inside, but you can take some out and count them.';
</script>

{#snippet side(args: Record<string, unknown>)}
	<Frame palette={args.palette as 'redBlue'} {intro}>
		<SideJar {...args} />
	</Frame>
{/snippet}

<Story name="D · 1 One jar" exportName="SideJar1OneJar" args={{ startStep: 0 }} template={side} />
<Story name="D · 2 Grab 10" exportName="SideJar2Grab10" args={{ startStep: 1 }} template={side} />
<Story name="D · 3 Grab 100" exportName="SideJar3Grab100" args={{ startStep: 2 }} template={side} />
<Story
	name="D · 4 Jar 1,000× bigger"
	exportName="SideJar4BigJar"
	args={{ startStep: 3 }}
	template={side}
/>
<Story
	name="D · 5 Your turn"
	exportName="SideJar5YourTurn"
	args={{ startStep: 4 }}
	template={side}
/>

<Story name="E · Pour" exportName="Pour" args={{ startWithPours: 0 }}>
	{#snippet template(args)}
		<Frame palette={args.palette} {intro}>
			<Pour {...args} />
		</Frame>
	{/snippet}
</Story>
<Story name="E · Pour, after 8 pours" exportName="PourAfter8" args={{ startWithPours: 8 }}>
	{#snippet template(args)}
		<Frame palette={args.palette} {intro}>
			<Pour {...args} />
		</Frame>
	{/snippet}
</Story>

<Story name="F · Twenty hands" exportName="TwentyHands" args={{ startSize: 10, startJar: 'small' }}>
	{#snippet template(args)}
		<Frame palette={args.palette} {intro}>
			<TwentyHands {...args} />
		</Frame>
	{/snippet}
</Story>
<Story
	name="F · Twenty hands, lined up"
	exportName="TwentyHandsLinedUp"
	args={{ startSize: 100, startJar: 'big', startSorted: true }}
>
	{#snippet template(args)}
		<Frame palette={args.palette} {intro}>
			<TwentyHands {...args} />
		</Frame>
	{/snippet}
</Story>

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
	name="G · 3 Four colours, markers"
	exportName="Converge3Markers"
	args={{ startStage: 2, startTarget: 1000, multiDisplay: 'markers' }}
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
