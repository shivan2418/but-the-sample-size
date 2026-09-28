<script lang="ts">
	// PROTOTYPE, throwaway: the one sentence that gets from "300 million" to the population this rung
	// polls, and the link back to rung 5 instead of simulating people.
	import { TOTAL, fmtBig } from './model';

	// Placeholders, rounded: the source for each is still to be picked.
	const COUNTRY = 340_000_000; // US residents, mid-2024 (Census estimate)
	const CAN_VOTE = 245_000_000; // eligible to vote: citizens 18 and over
</script>

<p>
	About <b>{fmtBig(COUNTRY)}</b> people live in the US. About <b>{fmtBig(CAN_VOTE)}</b> of them
	could vote in 2024, and <b>{fmtBig(TOTAL)}</b> did. A poll of who people voted for is a poll of
	those {fmtBig(TOTAL)}, so that’s the population here.
</p>
<p class="text-[15px] text-muted">
	There are no residents on this rung, only the shares. <a
		class="text-b underline underline-offset-3"
		href="#people-or-percentages">People or percentages</a
	> showed the two give the same polls.
</p>
