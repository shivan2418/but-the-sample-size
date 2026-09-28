<script lang="ts">
	// PROTOTYPE, throwaway. Style B · Instrument: a tool you work with. Sans throughout with
	// monospaced numbers, a sticky progress bar of the 8 rungs, each rung a panel that says in one
	// plain sentence what it shows, readouts above the map, and solid block controls.
	import Converge from '../marble-jars/Converge.svelte';
	import DotMap from './DotMap.svelte';
	import * as c from './content';

	let { theme = 'light', speed = 0.75 }: { theme?: 'light' | 'dark'; speed?: number } = $props();
	const pct = (n: number) => `${n.toFixed(1)}%`;
	const bars = [
		{ k: 'b', label: 'Blue', poll: c.town.poll.b, real: c.town.real.b },
		{ k: 'a', label: 'Red', poll: c.town.poll.a, real: c.town.real.a },
		{ k: 'grey', label: 'Other', poll: c.town.poll.other, real: c.town.real.other }
	];
</script>

<svelte:head>
	<link
		rel="stylesheet"
		href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap"
	/>
</svelte:head>

<div class="frame" data-theme={theme}>
	<div class="bar" aria-label="Progress">
		{#each c.rungNav as r, i (r.id)}
			<a href="#b-{r.id}" class:on={i <= 1} aria-label={r.short}></a>
		{/each}
		<span class="where num">2/8 Marbles</span>
	</div>

	<main>
		<header>
			<h1>{c.title}</h1>
			<p class="dek">{c.dek}</p>
		</header>

		<section id="b-objection" class="claim">
			<div class="eyebrow">The objection</div>
			<p class="quote">“{c.objection.text}”</p>
			<div class="small">{c.objection.who}. We’ll test it in 7 steps. Skip any of them.</div>
		</section>

		<section id="b-marbles" class="panel">
			<div class="panel-head"><span class="num">02</span> {c.marbles.title}</div>
			<p class="proves">A count gets close to the true mix long before you count everything.</p>
			<p class="body">{c.marbles.intro}</p>
			{#key theme}
				<Converge {speed} startTarget={100} />
			{/key}
		</section>

		<section id="b-town" class="panel">
			<div class="panel-head"><span class="num">03</span> {c.town.title}</div>
			<p class="proves">The same works with real people at real addresses.</p>
			<p class="body">{c.town.intro}</p>
			<div class="widget">
				<div class="readout">
					<div><span class="eyebrow">Asked</span><b class="num">1,200</b></div>
					<div><span class="eyebrow">City</span><b class="num">645,000</b></div>
					<div><span class="eyebrow">Share</span><b class="num">0.19%</b></div>
				</div>
				<div class="map"><DotMap radius={1.4} /></div>
				<div class="card">
					<div class="card-top">
						<b>{c.resident.name}</b><span class="chip-tag">{c.tag}</span>
					</div>
					<table class="kv">
						<tbody>
							<tr><th>Age</th><td>{c.resident.age}</td></tr>
							<tr><th>Address</th><td class="num">{c.resident.address}</td></tr>
							<tr><th>Registered</th><td>{c.resident.registration}</td></tr>
							<tr><th>Voted 2024</th><td>{c.resident.voted2024 ? 'Yes' : 'No'}</td></tr>
							<tr><th>Would vote</th><td class="cb">Blue · modeled</td></tr>
						</tbody>
					</table>
				</div>
				<div class="compare">
					{#each bars as b (b.k)}
						<div class="cmp-row">
							<span class="lbl">{b.label}</span>
							<div class="track">
								<div class="fill" style:width="{b.poll}%" style:background="var(--{b.k})"></div>
								<div class="real" style:left="{b.real}%"></div>
							</div>
							<span class="num val">{pct(b.poll)}</span>
						</div>
					{/each}
					<div class="small">Bar: your poll. Tick: real 2024 result (placeholder).</div>
				</div>
				<div class="seg" role="group" aria-label="Sample size">
					<button>120</button><button aria-pressed="true">1,200</button><button>12,000</button>
				</div>
				<button class="primary">Ask again</button>
			</div>
		</section>

		{#each c.later as r, i (r.id)}
			<section id="b-{r.id}" class="panel stub">
				<div class="panel-head"><span class="num">0{i + 4}</span> {r.title}</div>
				<p class="small">{r.gist}</p>
			</section>
		{/each}

		<section id="b-answer" class="claim done">
			<div class="eyebrow">The answer</div>
			<p class="body">{c.answer.text}</p>
		</section>
		<div class="proto">Prototype, throwaway. Nothing here is final copy or real data.</div>
	</main>
</div>

<style>
	.frame {
		--bg: #eef1f5;
		--surface: #ffffff;
		--ink: #0f1722;
		--muted: #5b6676;
		--line: #d3d9e2;
		--dim: #c9d0da;
		--pin: #8e99a8;
		--glass: #e3e8ef;
		--note: #fff4c7;
		--note-ink: #5c4700;
		--accent: #0f1722;
		--a: #e03c31;
		--b: #1f6feb;
		--grey: #8b95a3;
		--third: #e0a800;
		--serif: 'Inter', system-ui, sans-serif;
		--sans: 'Inter', system-ui, sans-serif;
		--mono: 'JetBrains Mono', ui-monospace, monospace;
		background: var(--bg);
		color: var(--ink);
		font: 16px/1.5 var(--sans);
		min-height: 100vh;
		padding-bottom: 48px;
	}
	.frame[data-theme='dark'] {
		color-scheme: dark;
		--bg: #0b0f15;
		--surface: #121821;
		--ink: #e6ebf2;
		--muted: #8e9aab;
		--line: #243041;
		--dim: #2a3444;
		--pin: #5d6a7c;
		--glass: #151c26;
		--note: #2b2610;
		--note-ink: #ecd98a;
		--accent: #e6ebf2;
		--a: #ff6b5e;
		--b: #5b9bff;
		--grey: #697586;
		--third: #f5c542;
	}
	.frame :global(*) {
		box-sizing: border-box;
	}
	.bar {
		position: sticky;
		top: 0;
		z-index: 5;
		display: flex;
		align-items: center;
		gap: 3px;
		padding: 10px 16px;
		background: var(--surface);
		border-bottom: 1px solid var(--line);
	}
	.bar a {
		flex: 1;
		height: 6px;
		border-radius: 1px;
		background: var(--line);
	}
	.bar a.on {
		background: var(--accent);
	}
	.where {
		font-size: 11px;
		color: var(--muted);
		margin-left: 8px;
		white-space: nowrap;
	}
	main {
		max-width: 36rem;
		margin: 0 auto;
		padding: 0 16px;
		display: flex;
		flex-direction: column;
		gap: 14px;
	}
	header {
		padding: 22px 0 4px;
	}
	h1 {
		font: 700 30px/1.1 var(--sans);
		letter-spacing: -0.02em;
		margin: 0 0 6px;
	}
	.dek {
		color: var(--muted);
		margin: 0;
	}
	.claim {
		background: var(--ink);
		color: var(--surface);
		border-radius: 8px;
		padding: 14px 16px;
	}
	.claim .small,
	.claim .eyebrow {
		color: color-mix(in srgb, var(--surface) 70%, transparent);
	}
	.quote {
		font: 600 20px/1.35 var(--sans);
		margin: 8px 0;
	}
	.panel {
		background: var(--surface);
		border: 1px solid var(--line);
		border-radius: 8px;
		padding: 14px;
		display: flex;
		flex-direction: column;
		gap: 12px;
	}
	.panel-head {
		font: 700 18px var(--sans);
		display: flex;
		gap: 8px;
		align-items: baseline;
	}
	.panel-head .num {
		font: 600 13px var(--mono);
		color: var(--accent);
	}
	.proves {
		font-weight: 600;
		margin: 0;
	}
	.body {
		margin: 0;
	}
	.stub {
		gap: 4px;
	}
	.stub .small {
		margin: 0;
	}
	.proto {
		font: 12px var(--mono);
		background: var(--note);
		color: var(--note-ink);
		padding: 6px 10px;
		border-radius: 4px;
	}

	/* widgets sit flush inside panels */
	.frame :global(.widget) {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}
	.frame :global(canvas) {
		display: block;
		width: 100%;
		background: var(--bg);
		border-radius: 4px;
	}
	.frame :global(button) {
		font: 600 14px var(--sans);
		color: var(--ink);
		background: var(--glass);
		border: 1px solid var(--line);
		border-radius: 6px;
		padding: 10px 14px;
		min-height: 44px;
		cursor: pointer;
	}
	.frame :global(button.primary) {
		background: var(--ink);
		border-color: var(--ink);
		color: var(--surface);
	}
	.frame :global(button[aria-pressed='true']) {
		background: var(--ink);
		border-color: var(--ink);
		color: var(--surface);
	}
	.frame :global(button:disabled) {
		opacity: 0.4;
		cursor: default;
	}
	.frame :global(input[type='number']) {
		font: 600 16px var(--mono);
		width: 9ch;
		padding: 8px;
		border: 1px solid var(--line);
		border-radius: 6px;
		background: var(--bg);
		color: var(--ink);
	}
	.frame :global(.row) {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		align-items: center;
	}
	.frame :global(.eyebrow) {
		font: 600 13px var(--sans);
		color: var(--muted);
	}
	.frame :global(.small) {
		font-size: 13px;
		color: var(--muted);
		line-height: 1.45;
	}
	.frame :global(.num) {
		font-family: var(--mono);
		font-variant-numeric: tabular-nums;
	}
	.frame :global(.tally) {
		font: 14px var(--sans);
		background: var(--bg);
		border-radius: 4px;
		padding: 6px 8px;
		min-height: 1.4em;
	}
	.frame :global(.tally b) {
		font: 600 14px var(--mono);
	}
	.frame :global(.ca) {
		color: var(--a);
	}
	.frame :global(.cb) {
		color: var(--b);
	}
	.frame :global(.moe) {
		font-size: 14px;
		border-left: 3px solid var(--ink);
		padding-left: 10px;
	}
	.frame :global(.moe b) {
		font-family: var(--mono);
	}
	.frame :global(.widget h2) {
		font: 700 17px/1.25 var(--sans);
		margin: 0;
	}
	.frame :global(.lede) {
		font-size: 15px;
		margin: 0;
	}

	/* city rung mock */
	.readout {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 6px;
	}
	.readout div {
		background: var(--bg);
		border-radius: 4px;
		padding: 6px 8px;
		display: flex;
		flex-direction: column;
	}
	.readout b {
		font-size: 17px;
	}
	.map {
		background: var(--bg);
		border-radius: 4px;
		padding: 4px;
	}
	.card {
		border: 1px solid var(--line);
		border-radius: 6px;
		overflow: hidden;
	}
	.card-top {
		display: flex;
		flex-wrap: wrap;
		gap: 6px;
		justify-content: space-between;
		align-items: center;
		padding: 8px 10px;
		background: var(--glass);
	}
	.chip-tag {
		font-size: 12px;
		color: var(--muted);
		border: 1px dashed var(--muted);
		border-radius: 3px;
		padding: 1px 5px;
	}
	.kv {
		width: 100%;
		border-collapse: collapse;
		font-size: 14px;
	}
	.kv th,
	.kv td {
		text-align: left;
		padding: 5px 10px;
		border-top: 1px solid var(--line);
		vertical-align: top;
	}
	.kv th {
		font-weight: 500;
		color: var(--muted);
		width: 7.5em;
	}
	.kv td.num {
		font-size: 12px;
	}
	.compare {
		display: flex;
		flex-direction: column;
		gap: 6px;
	}
	.cmp-row {
		display: grid;
		grid-template-columns: 3.5em 1fr 4em;
		gap: 8px;
		align-items: center;
		font-size: 13px;
	}
	.track {
		position: relative;
		height: 14px;
		background: var(--bg);
		border-radius: 2px;
	}
	.fill {
		height: 100%;
		border-radius: 2px;
	}
	.real {
		position: absolute;
		top: -3px;
		bottom: -3px;
		width: 2px;
		background: var(--ink);
	}
	.val {
		text-align: right;
	}
	.seg {
		display: flex;
	}
	.seg button {
		flex: 1;
		border-radius: 0;
	}
	.seg button:first-child {
		border-radius: 6px 0 0 6px;
	}
	.seg button:last-child {
		border-radius: 0 6px 6px 0;
	}
</style>
