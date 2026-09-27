/**
 * The explainer's rungs in page order, as decided in "Draft the list of rungs" (#6).
 * `id` is the section's anchor (`#marbles`); titles are placeholders until the copy is written.
 */
export const rungs = [
	{ id: 'objection', title: '1,200 people out of 300 million?' },
	{ id: 'marbles', title: 'A handful of marbles' },
	{ id: 'town', title: 'A town' },
	{ id: 'city-only', title: 'Only asking the city' },
	{ id: 'north-carolina', title: 'North Carolina' },
	{ id: 'people-or-percentages', title: 'People or percentages' },
	{ id: 'country', title: 'The whole country' },
	{ id: 'answer', title: 'Back to the objection' }
] as const satisfies readonly { id: string; title: string }[];

export type RungId = (typeof rungs)[number]['id'];
