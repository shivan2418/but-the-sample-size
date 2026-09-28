<script lang="ts">
	// PROTOTYPE, throwaway. Style C · Plain: legibility over everything, in the spirit of GOV.UK.
	// Large system type (no web fonts), black on white, one column, no cards, no shadows, no
	// decoration. Links are underlined, buttons are big square blocks, the only colour is data.
	import Converge from '../marble-jars/Converge.svelte';
	import DotMap from './DotMap.svelte';
	import * as c from './content';

	let { theme = 'light', speed = 0.75 }: { theme?: 'light' | 'dark'; speed?: number } = $props();
	const pct = (n: number) => `${Math.round(n)}%`;
</script>

<div class="frame" data-theme={theme}>
	<main>
		<h1>{c.title}</h1>
		<p class="lead">{c.dek}</p>

		<details class="contents">
			<summary>Contents</summary>
			<ol>
				{#each c.rungNav as r (r.id)}
					<li><a href="#c-{r.id}">{r.short}</a></li>
				{/each}
			</ol>
		</details>

		<section id="c-objection">
			<p class="said">{c.objection.who}:</p>
			<p class="quote">“{c.objection.text}”</p>
			<p>It’s a fair question. Let’s check it, one step at a time. You can skip any step.</p>
		</section>

		<section id="c-marbles">
			<h2 class="rung"><span class="step">Step 2 of 8</span>{c.marbles.title}</h2>
			<p>{c.marbles.intro}</p>
			{#key theme}
				<Converge {speed} startTarget={100} />
			{/key}
			<p>{c.marbles.outro}</p>
			<a class="skip" href="#c-town">Skip to step 3</a>
		</section>

		<section id="c-town">
			<h2 class="rung"><span class="step">Step 3 of 8</span>{c.town.title}</h2>
			<p>{c.town.intro}</p>
			<div class="widget">
				<DotMap radius={1.5} />
				<p class="small">
					Grey dots: not asked. Coloured dots: the 1,200 you asked, by who they’d vote for.
				</p>

				<div class="resident">
					<p class="tag">{c.tag}</p>
					<p class="name">{c.resident.name}, {c.resident.age}</p>
					<p class="addr">{c.resident.address}</p>
					<dl>
						<div>
							<dt>Registered as</dt>
							<dd>{c.resident.registration}</dd>
						</div>
						<div>
							<dt>Voted in 2024</dt>
							<dd>{c.resident.voted2024 ? 'Yes' : 'No'}</dd>
						</div>
						<div>
							<dt>Would vote</dt>
							<dd><span class="cb">Blue</span> (our guess)</dd>
						</div>
					</dl>
				</div>

				<p class="result">
					You asked <b class="num">1,200</b> people, <b class="num">0.19%</b> of the city.
					<span class="cb">Blue</span> got <b class="num">{pct(c.town.poll.b)}</b>. In the real 2024
					election it got <b class="num">{pct(c.town.real.b)}</b>.
				</p>
				<p class="small">Placeholder numbers.</p>
				<div class="row">
					<button class="primary">Ask 1,200 others</button>
					<button>Ask 20 times</button>
				</div>
			</div>
		</section>

		{#each c.later as r, i (r.id)}
			<section id="c-{r.id}" class="stub">
				<h2 class="rung"><span class="step">Step {i + 4} of 8</span>{r.title}</h2>
				<p>{r.gist}</p>
			</section>
		{/each}

		<section id="c-answer">
			<h2 class="rung"><span class="step">Step 8 of 8</span>{c.answer.title}</h2>
			<p class="quote">{c.answer.text}</p>
		</section>
		<p class="proto">Prototype, throwaway. Nothing here is final copy or real data.</p>
	</main>
</div>

<style>
	.frame {
		--bg: #ffffff;
		--surface: #ffffff;
		--ink: #0b0c0c;
		--muted: #505a5f;
		--line: #b1b4b6;
		--dim: #cfd2d4;
		--pin: #8a8f93;
		--glass: #f3f2f1;
		--focus: #ffdd00;
		--a: #d4351c;
		--b: #1d70b8;
		--grey: #8a8f93;
		--third: #c29600;
		--serif: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
		--sans: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
		--mono: ui-monospace, Menlo, Consolas, monospace;
		background: var(--bg);
		color: var(--ink);
		font: 19px/1.5 var(--sans);
		padding: 0 16px 48px;
		min-height: 100vh;
	}
	.frame[data-theme='dark'] {
		color-scheme: dark;
		--bg: #0e0f10;
		--surface: #0e0f10;
		--ink: #f3f2f1;
		--muted: #a9b0b4;
		--line: #5c6266;
		--dim: #33383b;
		--pin: #767c80;
		--glass: #1c1e20;
		--a: #f0674f;
		--b: #5aa3e8;
		--grey: #767c80;
		--third: #f0c43a;
	}
	.frame :global(*) {
		box-sizing: border-box;
	}
	.frame :global(:focus-visible) {
		outline: 3px solid var(--focus);
		outline-offset: 0;
		box-shadow: 0 0 0 5px var(--ink);
	}
	main {
		max-width: 38rem;
		margin: 0 auto;
	}
	h1 {
		font: 700 36px/1.1 var(--sans);
		margin: 32px 0 12px;
	}
	.lead {
		font-size: 22px;
		margin: 0 0 20px;
	}
	p {
		margin: 0 0 16px;
	}
	a {
		color: var(--b);
		text-decoration-thickness: 1px;
		text-underline-offset: 3px;
	}
	.contents {
		margin-bottom: 8px;
	}
	.contents summary {
		color: var(--b);
		text-decoration: underline;
		text-underline-offset: 3px;
		cursor: pointer;
	}
	.contents ol {
		margin: 8px 0 0;
		padding-left: 1.5em;
	}
	section {
		padding: 24px 0;
		border-top: 1px solid var(--line);
	}
	.said {
		color: var(--muted);
		margin-bottom: 4px;
	}
	.quote {
		font: 700 24px/1.3 var(--sans);
		border-left: 6px solid var(--line);
		padding-left: 14px;
	}
	h2.rung {
		font: 700 27px/1.2 var(--sans);
		margin: 0 0 16px;
	}
	.step {
		display: block;
		font: 400 17px var(--sans);
		color: var(--muted);
		margin-bottom: 4px;
	}
	.skip {
		font-size: 17px;
	}
	.stub p {
		color: var(--muted);
	}
	.proto {
		font-size: 15px;
		color: var(--muted);
		border-top: 1px solid var(--line);
		padding-top: 12px;
	}

	/* the widget sits on the page, no box */
	.frame :global(.widget) {
		display: flex;
		flex-direction: column;
		gap: 14px;
		margin: 8px 0 20px;
	}
	.frame :global(canvas) {
		display: block;
		width: 100%;
	}
	.frame :global(button) {
		font: 600 17px var(--sans);
		color: var(--ink);
		background: var(--glass);
		border: 2px solid transparent;
		border-radius: 0;
		box-shadow: 0 2px 0 var(--line);
		padding: 8px 14px;
		min-height: 44px;
		cursor: pointer;
	}
	.frame :global(button.primary) {
		background: #00703c;
		color: #fff;
		box-shadow: 0 2px 0 #002d18;
	}
	.frame :global(button[aria-pressed='true']) {
		background: var(--ink);
		color: var(--bg);
		box-shadow: none;
	}
	.frame :global(button:disabled) {
		opacity: 0.45;
		cursor: default;
	}
	.frame :global(input[type='number']) {
		font: 600 19px var(--mono);
		width: 9ch;
		padding: 6px 8px;
		border: 2px solid var(--ink);
		border-radius: 0;
		background: var(--bg);
		color: var(--ink);
	}
	.frame :global(.row) {
		display: flex;
		flex-wrap: wrap;
		gap: 10px;
		align-items: center;
	}
	.frame :global(.eyebrow) {
		font: 700 17px var(--sans);
		color: var(--ink);
	}
	.frame :global(.small) {
		font-size: 16px;
		color: var(--muted);
		line-height: 1.45;
		margin: 0;
	}
	.frame :global(.num) {
		font-variant-numeric: tabular-nums;
	}
	.frame :global(.tally) {
		font-size: 17px;
		min-height: 1.4em;
	}
	.frame :global(.ca) {
		color: var(--a);
		font-weight: 700;
	}
	.frame :global(.cb) {
		color: var(--b);
		font-weight: 700;
	}
	.frame :global(.moe) {
		font-size: 19px;
		border-left: 6px solid var(--b);
		padding-left: 14px;
	}
	.frame :global(.widget h2) {
		font: 700 22px/1.25 var(--sans);
		margin: 0;
	}
	.frame :global(.lede) {
		margin: 0;
	}

	/* city rung mock */
	.resident {
		border: 2px solid var(--ink);
		padding: 14px 16px;
	}
	.resident p {
		margin: 0;
	}
	.tag {
		font-size: 16px;
		color: var(--muted);
	}
	.name {
		font-weight: 700;
		font-size: 22px;
	}
	.addr {
		margin-bottom: 10px !important;
	}
	dl {
		margin: 0;
	}
	dl div {
		display: flex;
		flex-wrap: wrap;
		gap: 0 10px;
		padding: 6px 0;
		border-top: 1px solid var(--line);
	}
	dt {
		font-weight: 700;
		min-width: 8em;
	}
	dd {
		margin: 0;
	}
	.result {
		font-size: 21px;
		margin: 0;
	}
</style>
