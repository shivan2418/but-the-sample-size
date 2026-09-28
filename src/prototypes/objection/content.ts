// PROTOTYPE, throwaway: three wordings of the opening objection, the promise under it, and the
// answered version at the end. Every look renders every wording, so look and copy can be judged
// apart. The answered copy never mentions what the reader did on the page: rungs are skippable, so
// the reader may have run nothing.

export type Wording = {
	name: string;
	/** the reader's objection, quoted back */
	objection: string;
	/** who says it: no name, no avatar, no site */
	who: string;
	/** the page's reply, under the objection */
	promise: string;
	/** the answer at the end, under the same objection */
	answer: string;
	/** the follow-up question, linking back to the city-only rung */
	why: string;
};

export const wordings: Wording[] = [
	{
		name: '1 · The ticket’s draft',
		objection: '1,200 people out of 300 million? That’s 0.0004%. How can that mean anything?',
		who: 'A comment under every poll',
		promise: 'By the end, you’ll have run the polls yourself.',
		answer: '1,200 is enough, if it’s random.',
		why: 'So why are polls sometimes wrong?'
	},
	{
		name: '4 · Map owner’s pick',
		objection: '1,200 people out of 300 million? That’s 0.0004%. How can that mean anything?',
		who: 'A comment under every poll',
		promise: '1,200 is probably enough. Let me explain why.',
		answer: '1,200 is enough, if it’s random.',
		why: 'So why are polls sometimes wrong?'
	},
	{
		name: '2 · Plain speech',
		objection:
			'They asked 1,200 people. There are 300 million of us. How is that supposed to mean anything?',
		who: 'Someone in the comments, every election',
		promise:
			'It’s a fair question, and you don’t have to take anyone’s word for the answer. Below, you run the polls yourself: first on marbles, then on every registered voter in North Carolina.',
		answer:
			'How close a poll gets depends on how many people you ask, not on how many people there are. That holds as long as the people you ask are picked at random.',
		why: 'Then why do polls miss? Usually because the sample wasn’t random.'
	},
	{
		name: '3 · Flat claim',
		objection: 'A poll of 1,200 people can’t tell you what 300 million think.',
		who: 'A common reply to any poll',
		promise: 'Let’s test that. You pick how many to ask, and you count the answers yourself.',
		answer:
			'It can, to within about 3 points either way, as long as the 1,200 are picked at random. Asking more narrows that. Asking more of the wrong people doesn’t.',
		why: 'Why polls still miss'
	}
];
