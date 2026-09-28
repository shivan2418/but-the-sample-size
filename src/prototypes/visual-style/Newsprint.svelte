<script lang="ts">
	// PROTOTYPE, throwaway. Style A · Newsprint: an editorial essay. Serif body on warm paper,
	// hairline rules, small-caps kickers, widgets set as numbered figures with captions, square
	// outlined controls. Reads like a long-form piece in a newspaper's graphics desk.
	import Converge from '../marble-jars/Converge.svelte';
	import DotMap from './DotMap.svelte';
	import * as c from './content';

	let { theme = 'light', speed = 0.75 }: { theme?: 'light' | 'dark'; speed?: number } = $props();
	const pct = (n: number) => `${n.toFixed(1)}%`;
</script>

<svelte:head>
	<link
		rel="stylesheet"
		href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=Public+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400;500&display=swap"
	/>
</svelte:head>

<div class="frame" data-theme={theme}>
	<article>
		<header class="mast">
			<div class="kicker">An explainer · 8 steps · about 10 minutes</div>
			<h1>{c.title}</h1>
			<p class="dek">{c.dek}</p>
			<nav aria-label="Rungs">
				<ol>
					{#each c.rungNav as r, i (r.id)}
						<li><a href="#a-{r.id}"><span class="n">{i + 1}</span> {r.short}</a></li>
					{/each}
				</ol>
			</nav>
		</header>

		<section id="a-objection">
			<blockquote>
				<p>“{c.objection.text}”</p>
				<footer>{c.objection.who}</footer>
			</blockquote>
			<p class="body">
				It’s a fair question. The answer fits in one sentence, but it’s more convincing if you check
				it yourself. So let’s check it.
			</p>
		</section>

		<section id="a-marbles">
			<div class="rung-kicker">Step 2</div>
			<h2 class="rung">{c.marbles.title}</h2>
			<p class="body">{c.marbles.intro}</p>
			<figure>
				{#key theme}
					<Converge {speed} startTarget={100} />
				{/key}
				<figcaption>
					<b>Figure 1.</b> Take marbles out one at a time or let it count for you.
				</figcaption>
			</figure>
			<p class="body">{c.marbles.outro}</p>
		</section>

		<section id="a-town">
			<div class="rung-kicker">Step 3</div>
			<h2 class="rung">{c.town.title}</h2>
			<p class="body">{c.town.intro}</p>
			<figure>
				<div class="widget">
					<DotMap />
					<div class="legend small">
						<span><i style:background="var(--a)"></i>red</span>
						<span><i style:background="var(--b)"></i>blue</span>
						<span><i style:background="var(--grey)"></i>wouldn’t vote</span>
						<span><i style:background="var(--dim)"></i>not asked</span>
					</div>
					<div class="card">
						<div class="tag">{c.tag}</div>
						<div class="name">{c.resident.name}, {c.resident.age}</div>
						<div class="addr num">{c.resident.address}</div>
						<dl>
							<dt>Registered</dt>
							<dd>{c.resident.registration}</dd>
							<dt>Voted in 2024</dt>
							<dd>{c.resident.voted2024 ? 'Yes' : 'No'}</dd>
							<dt>Would vote</dt>
							<dd class="cb">blue <span class="small">(modeled)</span></dd>
						</dl>
					</div>
					<table>
						<thead>
							<tr><th></th><th class="cb">Blue</th><th class="ca">Red</th><th>Other</th></tr>
						</thead>
						<tbody>
							<tr>
								<th>Your poll of 1,200</th>
								<td class="num">{pct(c.town.poll.b)}</td>
								<td class="num">{pct(c.town.poll.a)}</td>
								<td class="num">{pct(c.town.poll.other)}</td>
							</tr>
							<tr>
								<th>Real 2024 result</th>
								<td class="num">{pct(c.town.real.b)}</td>
								<td class="num">{pct(c.town.real.a)}</td>
								<td class="num">{pct(c.town.real.other)}</td>
							</tr>
						</tbody>
					</table>
					<div class="row">
						<button class="primary">Ask 1,200 more</button>
						<button>Ask 20 times</button>
					</div>
				</div>
				<figcaption>
					<b>Figure 2.</b> Placeholder numbers. You asked 0.19% of the city.
				</figcaption>
			</figure>
		</section>

		{#each c.later as r, i (r.id)}
			<section id="a-{r.id}" class="stub">
				<div class="rung-kicker">Step {i + 4}</div>
				<h2 class="rung">{r.title}</h2>
				<p class="body muted">{r.gist}</p>
			</section>
		{/each}

		<section id="a-answer">
			<div class="rung-kicker">Step 8</div>
			<h2 class="rung">{c.answer.title}</h2>
			<p class="body drop">{c.answer.text}</p>
		</section>
		<div class="proto">Prototype, throwaway. Nothing here is final copy or real data.</div>
	</article>
</div>

<style>
	.frame {
		--bg: #f6f2e9;
		--surface: #fbf9f4;
		--ink: #1f1b16;
		--muted: #6b6257;
		--line: #d9d1c3;
		--dim: #d4cbbb;
		--pin: #a39886;
		--glass: #ebe4d6;
		--note: #efe6cf;
		--note-ink: #5a4a26;
		--a: #b8382c;
		--b: #2d5a9a;
		--grey: #9b9384;
		--third: #c8960c;
		--serif: 'Newsreader', Georgia, serif;
		--sans: 'Public Sans', system-ui, sans-serif;
		--mono: 'IBM Plex Mono', ui-monospace, monospace;
		background: var(--bg);
		color: var(--ink);
		font: 18px/1.6 var(--serif);
		padding: 0 18px 56px;
		min-height: 100vh;
	}
	.frame[data-theme='dark'] {
		color-scheme: dark;
		--bg: #1a1814;
		--surface: #211e19;
		--ink: #ece5d8;
		--muted: #a59b8b;
		--line: #3a352d;
		--dim: #3d382f;
		--pin: #7b7263;
		--glass: #2a2620;
		--note: #2f2a1c;
		--note-ink: #e0cf9c;
		--a: #e0685b;
		--b: #7a9fd8;
		--grey: #7d7567;
		--third: #e6b93d;
	}
	.frame :global(*) {
		box-sizing: border-box;
	}
	article {
		max-width: 34rem;
		margin: 0 auto;
	}
	.mast {
		padding: 28px 0 20px;
		border-bottom: 3px double var(--ink);
	}
	.kicker,
	.rung-kicker {
		font: 600 14px var(--sans);
		color: var(--muted);
	}
	h1 {
		font: 600 40px/1.05 var(--serif);
		letter-spacing: -0.01em;
		margin: 10px 0 8px;
	}
	.dek {
		font: italic 20px/1.4 var(--serif);
		color: var(--muted);
		margin: 0 0 16px;
	}
	nav ol {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
		font: 14px var(--sans);
	}
	nav a {
		color: var(--ink);
		text-decoration: none;
		border-bottom: 1px solid var(--line);
	}
	nav .n {
		font: 500 12px var(--mono);
		color: var(--muted);
	}
	section {
		padding: 28px 0;
		border-bottom: 1px solid var(--line);
	}
	blockquote {
		margin: 0 0 18px;
		padding: 0;
		font: italic 24px/1.35 var(--serif);
	}
	blockquote p {
		margin: 0;
	}
	blockquote footer {
		font: 13px var(--sans);
		color: var(--muted);
		margin-top: 8px;
	}
	blockquote footer::before {
		content: '— ';
	}
	h2.rung {
		font: 600 28px/1.15 var(--serif);
		margin: 6px 0 12px;
	}
	.body {
		margin: 0 0 16px;
	}
	.muted {
		color: var(--muted);
	}
	.drop::first-letter {
		float: left;
		font: 600 52px/0.9 var(--serif);
		padding: 4px 6px 0 0;
	}
	figure {
		margin: 20px 0;
	}
	figcaption {
		font: 13px/1.45 var(--sans);
		color: var(--muted);
		margin-top: 8px;
	}
	.stub {
		padding: 18px 0;
	}
	.proto {
		margin-top: 24px;
		font: 12px var(--sans);
		color: var(--note-ink);
		background: var(--note);
		padding: 6px 10px;
	}

	/* the widget itself: a figure between two rules, no card */
	.frame :global(.widget) {
		border-top: 2px solid var(--ink);
		border-bottom: 1px solid var(--ink);
		padding: 14px 0;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}
	.frame :global(canvas) {
		display: block;
		width: 100%;
	}
	.frame :global(button) {
		font: 600 14px var(--sans);
		color: var(--ink);
		background: transparent;
		border: 1px solid var(--ink);
		border-radius: 2px;
		padding: 9px 14px;
		min-height: 40px;
		cursor: pointer;
	}
	.frame :global(button.primary),
	.frame :global(button[aria-pressed='true']) {
		background: var(--ink);
		color: var(--bg);
	}
	.frame :global(button:disabled) {
		opacity: 0.35;
		cursor: default;
	}
	.frame :global(input[type='number']) {
		font: 500 16px var(--mono);
		width: 9ch;
		padding: 6px 8px;
		border: 0;
		border-bottom: 2px solid var(--ink);
		background: transparent;
		color: var(--ink);
	}
	.frame :global(.row) {
		display: flex;
		flex-wrap: wrap;
		gap: 8px;
		align-items: center;
	}
	.frame :global(.eyebrow) {
		font: 600 13px var(--sans);
		color: var(--muted);
	}
	.frame :global(.small) {
		font: 13px/1.45 var(--sans);
		color: var(--muted);
	}
	.frame :global(.num) {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
	}
	.frame :global(.tally) {
		font: 15px var(--sans);
		min-height: 1.4em;
	}
	.frame :global(.tally b) {
		font: 500 15px var(--mono);
	}
	.frame :global(.ca) {
		color: var(--a);
	}
	.frame :global(.cb) {
		color: var(--b);
	}
	.frame :global(.moe) {
		font: italic 16px/1.5 var(--serif);
		border-left: 2px solid var(--ink);
		padding-left: 12px;
	}
	.frame :global(.moe b) {
		font: 500 15px var(--mono);
		font-style: normal;
	}
	.frame :global(.widget h2) {
		font: 600 20px/1.25 var(--serif);
		margin: 0;
	}
	.frame :global(.lede) {
		font: 17px/1.55 var(--serif);
		margin: 0;
	}

	/* city rung mock */
	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 4px 14px;
	}
	.legend i {
		display: inline-block;
		width: 9px;
		height: 9px;
		border-radius: 50%;
		margin-right: 5px;
	}
	.card {
		background: var(--surface);
		border: 1px solid var(--line);
		padding: 12px 14px;
		font: 15px var(--sans);
	}
	.tag {
		display: inline-block;
		font: 13px var(--sans);
		border: 1px solid var(--muted);
		color: var(--muted);
		padding: 1px 6px;
		margin-bottom: 8px;
	}
	.name {
		font: 600 20px var(--serif);
	}
	.addr {
		font-size: 13px;
		color: var(--muted);
		margin-bottom: 8px;
	}
	dl {
		display: grid;
		grid-template-columns: auto 1fr;
		gap: 2px 14px;
		margin: 0;
	}
	dt {
		color: var(--muted);
	}
	dd {
		margin: 0;
	}
	table {
		width: 100%;
		border-collapse: collapse;
		font: 14px var(--sans);
	}
	th,
	td {
		text-align: right;
		padding: 6px 4px;
		border-bottom: 1px solid var(--line);
	}
	tbody th {
		text-align: left;
		font-weight: 400;
	}
	thead th {
		font-weight: 600;
		border-bottom: 1px solid var(--ink);
	}
</style>
