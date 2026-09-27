import { describe, expect, it } from 'vitest';
import { rungs } from './rungs';

describe('rungs', () => {
	it('opens with the objection and closes by answering it', () => {
		expect(rungs[0].id).toBe('objection');
		expect(rungs.at(-1)?.id).toBe('answer');
	});

	it('has unique anchors that are valid URL fragments', () => {
		const ids = rungs.map((r) => r.id);
		expect(new Set(ids).size).toBe(ids.length);
		for (const id of ids) expect(id).toMatch(/^[a-z]+(-[a-z]+)*$/);
	});
});
