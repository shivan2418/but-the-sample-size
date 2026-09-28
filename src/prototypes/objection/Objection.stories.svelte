<script module lang="ts">
	// PROTOTYPE, throwaway: stories for "Wording and look of the opening objection" (#25). Four looks,
	// each opening and answered, at phone width. `wording` switches between the three drafts of the
	// copy in content.ts, so any look can be read with any wording.
	import { defineMeta } from '@storybook/addon-svelte-csf';
	import Objection from './Objection.svelte';
	import { wordings } from './content';

	const { Story } = defineMeta({
		title: 'Prototypes/objection',
		component: Objection,
		parameters: { layout: 'fullscreen' },
		argTypes: {
			wording: {
				control: 'inline-radio',
				options: wordings.map((_, i) => i),
				labels: Object.fromEntries(wordings.map((w, i) => [i, w.name]))
			},
			look: { control: 'inline-radio', options: ['quote', 'headline', 'comment', 'thread'] },
			state: { control: 'inline-radio', options: ['opening', 'answered'] }
		},
		args: { wording: 0 }
	});
</script>

<Story name="A · Quote · Opening" args={{ look: 'quote', state: 'opening' }} />
<Story name="A · Quote · Answered" args={{ look: 'quote', state: 'answered' }} />
<Story name="B · Headline · Opening" args={{ look: 'headline', state: 'opening' }} />
<Story name="B · Headline · Answered" args={{ look: 'headline', state: 'answered' }} />
<Story name="C · Comment · Opening" args={{ look: 'comment', state: 'opening' }} />
<Story name="C · Comment · Answered" args={{ look: 'comment', state: 'answered' }} />
<Story name="D · Thread · Opening" args={{ look: 'thread', state: 'opening' }} />
<Story name="D · Thread · Answered" args={{ look: 'thread', state: 'answered' }} />
<Story
	name="D · Thread · Opening · Desktop"
	args={{ look: 'thread', state: 'opening' }}
	globals={{ viewport: { value: 'desktop', isRotated: false } }}
/>
