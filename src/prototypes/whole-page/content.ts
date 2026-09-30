// PROTOTYPE, throwaway: the page's copy as far as it's decided. The objection's wording is the map
// owner's pick (#25); the claims for the stub rungs come from the rung list (#6). The Charlotte
// numbers are placeholders until the resident build.

export const nav = [
	{ id: 'objection', short: 'Objection' },
	{ id: 'marbles', short: 'Marbles' },
	{ id: 'charlotte', short: 'Charlotte' },
	{ id: 'city-only', short: 'Only the city' },
	{ id: 'north-carolina', short: 'North Carolina' },
	{ id: 'people-or-percentages', short: 'People or shares' },
	{ id: 'country', short: 'The country' },
	{ id: 'answer', short: 'The answer' }
];

export const objection = {
	text: '1,200 people out of 300 million? That’s 0.0004%. How can that mean anything?',
	who: 'A comment under every poll',
	promise: '1,200 is probably enough. Let me explain why.',
	answer: '1,200 is enough, if it’s random.',
	why: 'So why are polls sometimes wrong?'
};

export const marbles = {
	title: 'A handful of marbles',
	intro:
		'Forget people for a moment. Here is a jar of red and blue marbles. You can’t see inside, but you can take some out and count them.',
	outro:
		'Next, we swap the marbles for people: every registered voter in a real North Carolina city.'
};

export const charlotte = {
	title: 'A North Carolina city',
	intro:
		'This is Charlotte. Every dot is one of its 645,000 registered voters, at their real address. Ask 1,200 of them, picked at random, who they’d vote for.',
	voters:
		'We use registered voters, not everyone who lives here: North Carolina has about 11 million people and 7.85 million registered voters. Their names are invented; their party, race, age and whether they voted in 2024 come from the public voter record at that address. Who they’d vote for is our estimate.',
	candidates:
		'The red candidate is the Republican and the blue candidate the Democrat, here and on every step after.',
	asked: 1650,
	// placeholders: the real numbers come from the resident build
	poll: { a: 34.1, b: 63.2 },
	real: { a: 32.8, b: 64.9 }
};

export const resident = {
	name: 'Dana Whitfield',
	age: 41,
	address: '123 Placeholder Ave, Charlotte, NC 28205',
	registration: 'Unaffiliated'
};

export const stubs = [
	{
		id: 'city-only',
		n: 4,
		title: 'Only asking the city',
		claim:
			'All of this holds only if the poll is random. Ask only Charlotte about all of North Carolina and you’re confidently wrong, and asking more people doesn’t help.',
		widget: 'Widget not designed yet (#21).'
	},
	{
		id: 'north-carolina',
		n: 5,
		title: 'North Carolina',
		claim:
			'Scale up to North Carolina’s 7.85 million registered voters, and a random poll of 1,200 is as close as it was in Charlotte.',
		widget: 'Widget not designed yet.'
	},
	{
		id: 'people-or-percentages',
		n: 6,
		title: 'People or percentages',
		claim:
			'Drawing only the percentages gives the same spread of polls as drawing actual people, so from here on we can drop the people.',
		widget: 'Widget not designed yet.'
	}
];
