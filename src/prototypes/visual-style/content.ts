// PROTOTYPE, throwaway: the copy and mock data every style shares, so the styles differ only in
// design language. Nothing here is final copy, and the town numbers are placeholders, not real data.
import { seeded } from '../marble-jars/model';

export const objection = {
	who: 'A comment you’ve probably seen',
	text: '1,200 people out of 300 million? That’s 0.0004%. How can that mean anything?'
};

export const title = 'But the sample size…';
export const dek = 'Why a random poll of about 1,200 people can describe a whole country.';

export const marbles = {
	title: 'A handful of marbles',
	intro:
		'Forget people for a moment. Here is a jar of red and blue marbles. You can’t see inside, but you can take some out and count them.',
	outro:
		'Next, we swap the marbles for people: every registered voter in a real North Carolina city.'
};

export const town = {
	title: 'A city',
	intro:
		'This is Charlotte. Every dot is one of its 645,000 registered voters, at their real address. Ask 1,200 of them, picked at random, who they’d vote for.',
	sample: 1200,
	population: 645_000,
	// placeholders: the real numbers come from the resident build
	poll: { a: 34.1, b: 63.2, other: 2.7 },
	real: { a: 32.8, b: 64.9, other: 2.3 }
};

export type Resident = {
	name: string;
	age: number;
	address: string;
	registration: string;
	voted2024: boolean;
	choice: 'a' | 'b' | 'none';
};

export const resident: Resident = {
	name: 'Dana Whitfield',
	age: 41,
	address: '123 Placeholder Ave, Charlotte, NC 28205',
	registration: 'Unaffiliated',
	voted2024: true,
	choice: 'b'
};

export const tag = 'Invented resident · real address';

export const later = [
	{
		id: 'city-only',
		title: 'Only asking the city',
		gist: 'What goes wrong when the sample isn’t random.'
	},
	{ id: 'north-carolina', title: 'North Carolina', gist: '7.85 million voters, the same 1,200.' },
	{
		id: 'people-or-percentages',
		title: 'People or percentages',
		gist: 'Simulating people and simulating shares give the same answer.'
	},
	{ id: 'country', title: 'The whole country', gist: '300 million, still 1,200.' }
];

export const answer = {
	title: 'Back to the objection',
	text: 'How close a poll gets depends on how many you ask, not on how many there are, as long as the people you ask are picked at random.'
};

export const rungNav = [
	{ id: 'objection', short: 'Objection' },
	{ id: 'marbles', short: 'Marbles' },
	{ id: 'town', short: 'City' },
	{ id: 'city-only', short: 'Bias' },
	{ id: 'north-carolina', short: 'State' },
	{ id: 'people-or-percentages', short: 'Shares' },
	{ id: 'country', short: 'Country' },
	{ id: 'answer', short: 'Answer' }
];

/** Fake dots for the city map: clustered neighbourhoods, some polled. 0..1 coordinates. */
export type Dot = { x: number; y: number; polled: boolean; choice: 'a' | 'b' | 'none' };

export function cityDots(count = 900, seed = 7): Dot[] {
	const r = seeded(seed);
	const hoods = Array.from({ length: 9 }, () => ({
		x: 0.12 + r() * 0.76,
		y: 0.12 + r() * 0.76,
		s: 0.05 + r() * 0.1,
		lean: r()
	}));
	return Array.from({ length: count }, () => {
		const h = hoods[Math.floor(r() * hoods.length)];
		const a = r() * Math.PI * 2;
		const d = Math.sqrt(r()) * h.s;
		const v = r();
		const choice = v < 0.18 ? 'none' : v < 0.18 + 0.82 * (0.2 + h.lean * 0.3) ? 'a' : 'b';
		return {
			x: Math.min(0.98, Math.max(0.02, h.x + Math.cos(a) * d)),
			y: Math.min(0.98, Math.max(0.02, h.y + Math.sin(a) * d)),
			polled: r() < 0.09,
			choice
		};
	});
}
