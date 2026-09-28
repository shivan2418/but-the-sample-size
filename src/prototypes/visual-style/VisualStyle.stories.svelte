<script module lang="ts">
	// PROTOTYPE, throwaway: stories for "Visual style and design language" (#16). Each style is a
	// whole-page mock of the explainer around the accepted marble widget (G · Converge), in light
	// and dark, at 390px and 320px. The copy is shared (content.ts): only the design language differs.
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Newsprint from './Newsprint.svelte';
	import Instrument from './Instrument.svelte';
	import Plain from './Plain.svelte';
	import PlainTw from './PlainTw.svelte';

	const { Story } = defineMeta({
		title: 'Prototypes/visual-style',
		parameters: { layout: 'fullscreen' },
		argTypes: {
			theme: { control: 'inline-radio', options: ['light', 'dark'] },
			speed: { control: { type: 'range', min: 0.25, max: 3, step: 0.25 } }
		},
		args: { theme: 'light', speed: 0.75 }
	});
</script>

<Story name="A · Newsprint · Light" exportName="NewsprintLight" args={{ theme: 'light' }}>
	{#snippet template(args)}
		<Newsprint {...args} />
	{/snippet}
</Story>
<Story name="A · Newsprint · Dark" exportName="NewsprintDark" args={{ theme: 'dark' }}>
	{#snippet template(args)}
		<Newsprint {...args} />
	{/snippet}
</Story>
<Story
	name="A · Newsprint · 320px"
	exportName="NewsprintSmall"
	args={{ theme: 'light' }}
	globals={{ viewport: { value: 'smallPhone', isRotated: false } }}
>
	{#snippet template(args)}
		<Newsprint {...args} />
	{/snippet}
</Story>
<Story name="B · Instrument · Light" exportName="InstrumentLight" args={{ theme: 'light' }}>
	{#snippet template(args)}
		<Instrument {...args} />
	{/snippet}
</Story>
<Story name="B · Instrument · Dark" exportName="InstrumentDark" args={{ theme: 'dark' }}>
	{#snippet template(args)}
		<Instrument {...args} />
	{/snippet}
</Story>
<Story
	name="B · Instrument · 320px"
	exportName="InstrumentSmall"
	args={{ theme: 'light' }}
	globals={{ viewport: { value: 'smallPhone', isRotated: false } }}
>
	{#snippet template(args)}
		<Instrument {...args} />
	{/snippet}
</Story>
<Story name="C · Plain · Light" exportName="PlainLight" args={{ theme: 'light' }}>
	{#snippet template(args)}
		<Plain {...args} />
	{/snippet}
</Story>
<Story name="C · Plain · Dark" exportName="PlainDark" args={{ theme: 'dark' }}>
	{#snippet template(args)}
		<Plain {...args} />
	{/snippet}
</Story>
<Story
	name="C · Plain · 320px"
	exportName="PlainSmall"
	args={{ theme: 'light' }}
	globals={{ viewport: { value: 'smallPhone', isRotated: false } }}
>
	{#snippet template(args)}
		<Plain {...args} />
	{/snippet}
</Story>
<Story
	name="C2 · Plain compact (Tailwind) · Light"
	exportName="PlainTwLight"
	args={{ theme: 'light' }}
>
	{#snippet template(args)}
		<PlainTw {...args} />
	{/snippet}
</Story>
<Story
	name="C2 · Plain compact (Tailwind) · Dark"
	exportName="PlainTwDark"
	args={{ theme: 'dark' }}
>
	{#snippet template(args)}
		<PlainTw {...args} />
	{/snippet}
</Story>
<Story
	name="C2 · Plain compact (Tailwind) · 320px"
	exportName="PlainTwSmall"
	args={{ theme: 'light' }}
	globals={{ viewport: { value: 'smallPhone', isRotated: false } }}
>
	{#snippet template(args)}
		<PlainTw {...args} />
	{/snippet}
</Story>
<Story
	name="C2 · Plain compact (Tailwind) · Tablet"
	exportName="PlainTwTablet"
	args={{ theme: 'light' }}
	globals={{ viewport: { value: 'tablet', isRotated: false } }}
>
	{#snippet template(args)}
		<PlainTw {...args} />
	{/snippet}
</Story>
<Story
	name="C2 · Plain compact (Tailwind) · Desktop"
	exportName="PlainTwDesktop"
	args={{ theme: 'light' }}
	globals={{ viewport: { value: 'desktop', isRotated: false } }}
>
	{#snippet template(args)}
		<PlainTw {...args} />
	{/snippet}
</Story>
