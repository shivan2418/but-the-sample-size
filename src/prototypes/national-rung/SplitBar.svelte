<script lang="ts">
	// PROTOTYPE, throwaway: the true split as one stacked bar, with the counts under it and where
	// they come from. On this rung nothing is modeled, so the true split is the real result.
	import { US, TOTAL, fmt } from './model';

	const parts = [
		{ key: 'red', name: 'Red candidate', n: US.red, col: 'var(--a)' },
		{ key: 'blue', name: 'Blue candidate', n: US.blue, col: 'var(--b)' },
		{ key: 'other', name: 'Other', n: US.other, col: 'var(--grey)' }
	];
	const pct = (n: number) => ((n / TOTAL) * 100).toFixed(2) + '%';
</script>

<figure class="flex flex-col gap-2">
	<figcaption class="font-bold">Everyone who voted for president in 2024</figcaption>
	<div
		class="flex h-7 w-full"
		role="img"
		aria-label={parts.map((p) => `${p.name} ${pct(p.n)}`).join(', ')}
	>
		{#each parts as p (p.key)}
			<div style:width={pct(p.n)} style:background={p.col}></div>
		{/each}
	</div>
	<table class="w-full text-[15px] tabular-nums">
		<tbody>
			{#each parts as p (p.key)}
				<tr>
					<th scope="row" class="text-left font-normal">
						<span class="mr-1.5 inline-block size-3" style:background={p.col}></span>{p.name}
					</th>
					<td class="text-right">{fmt(p.n)}</td>
					<td class="pl-3 text-right font-bold">{pct(p.n)}</td>
				</tr>
			{/each}
			<tr class="border-t border-line">
				<th scope="row" class="text-left font-normal">All</th>
				<td class="text-right">{fmt(TOTAL)}</td>
				<td class="pl-3 text-right font-bold">100%</td>
			</tr>
		</tbody>
	</table>
	<p class="text-[15px] text-muted">
		Source: Federal Election Commission, <i>Official 2024 Presidential General Election Results</i>.
		“Other” is every candidate but the two main ones.
	</p>
</figure>
