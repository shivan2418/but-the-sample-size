<script lang="ts">
	// PROTOTYPE, throwaway. Style C2 · Plain compact, in Tailwind v4: C · Plain (the map owner's pick)
	// with tighter spacing, and a desktop layout. Mobile first: one column, 17px body. From `lg`
	// (1024px) a sticky contents list sits beside a 40rem reading column, body steps up to 19px, and
	// the city rung puts the map beside the resident card and the result.
	import './tw.css';
	import Converge from '../marble-jars/Converge.svelte';
	import DotMap from './DotMap.svelte';
	import * as c from './content';

	let { theme = 'light', speed = 0.75 }: { theme?: 'light' | 'dark'; speed?: number } = $props();
	const pct = (n: number) => `${Math.round(n)}%`;

	// The marble stages stack down the page. Back / Next step glide to the neighbouring stage (or
	// on to the city rung after the last), and jump instead for readers who ask for less motion.
	const stageIds = ['t-marbles-1', 't-marbles-2', 't-marbles-3'];
	function glide(from: number, dir: -1 | 1) {
		const id = stageIds[from + dir] ?? 't-town';
		const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
		document.getElementById(id)?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
	}

	const btn =
		'min-h-11 cursor-pointer bg-glass px-3 py-1.5 text-base font-semibold text-ink shadow-[0_2px_0_var(--line)]';
	const btnGo =
		'min-h-11 cursor-pointer bg-go px-3 py-1.5 text-base font-semibold text-white shadow-[0_2px_0_var(--go-edge)]';
	const link = 'text-b underline underline-offset-3';
	const section = 'scroll-mt-4 border-t border-line py-5 lg:py-8';
</script>

{#snippet heading(n: number, title: string)}
	<h2 class="mb-3 text-[22px]/tight font-bold lg:mb-4 lg:text-[28px]">
		<span class="font-normal text-muted">{n} ·</span>
		{title}
	</h2>
{/snippet}

<div
	class="plain min-h-screen bg-bg px-4 pb-10 font-sans text-[17px]/[1.45] text-ink lg:px-8 lg:text-[19px]/normal"
	data-theme={theme}
>
	<div class="mx-auto lg:grid lg:max-w-5xl lg:grid-cols-[11rem_minmax(0,40rem)] lg:gap-12">
		<aside class="hidden lg:block">
			<nav aria-label="Rungs" class="sticky top-8 pt-10 text-base">
				<p class="mb-2 font-bold">Contents</p>
				<ol class="flex flex-col gap-1.5">
					{#each c.rungNav as r, i (r.id)}
						<li class={i === 1 ? 'font-bold' : ''}>
							<span class="text-muted">{i + 1}</span>
							<a class={link} href="#t-{r.id}">{r.short}</a>
						</li>
					{/each}
				</ol>
			</nav>
		</aside>

		<main class="mx-auto max-w-[40rem] lg:mx-0">
			<h1 class="mt-6 mb-2 text-[30px]/tight font-bold lg:mt-10 lg:text-5xl/tight">{c.title}</h1>
			<p class="mb-3 text-[19px]/snug lg:text-2xl/snug">{c.dek}</p>

			<details class="mb-4 lg:hidden">
				<summary class="{link} cursor-pointer">Contents</summary>
				<ol class="mt-1 grid list-decimal grid-cols-2 gap-x-4 pl-6">
					{#each c.rungNav as r (r.id)}
						<li><a class={link} href="#t-{r.id}">{r.short}</a></li>
					{/each}
				</ol>
			</details>

			<section id="t-objection" class={section}>
				<p class="mb-1 border-l-[5px] border-line pl-3 text-xl/snug font-bold lg:text-2xl/snug">
					“{c.objection.text}”
				</p>
				<p class="mb-3 pl-4 text-[15px] text-muted">{c.objection.who}</p>
				<p>It’s a fair question. Let’s check it, one step at a time. You can skip any step.</p>
			</section>

			<section id="t-marbles" class={section}>
				{@render heading(2, c.marbles.title)}
				<p class="mb-3">{c.marbles.intro}</p>
				{#each stageIds as id, i (id)}
					<div {id} class="conv scroll-mt-4 {i ? 'mt-5 border-t border-dim pt-5' : ''} mb-3">
						{#key theme}
							<Converge
								{speed}
								startStage={i}
								startTarget={i ? 1000 : 100}
								onStep={(dir) => glide(i, dir)}
							/>
						{/key}
					</div>
				{/each}
				<p class="mb-2">{c.marbles.outro}</p>
				<a class="{link} text-base" href="#t-town">Skip to step 3</a>
			</section>

			<section id="t-town" class={section}>
				{@render heading(3, c.town.title)}
				<p class="mb-3">{c.town.intro}</p>
				<div class="flex flex-col gap-3 md:grid md:grid-cols-2 md:gap-6 lg:-mr-24">
					<div>
						<DotMap radius={1.5} viewBox="0 10 100 80" />
						<p class="text-[15px]/snug text-muted">
							Grey: not asked. Coloured: the 1,200 you asked, by who they’d vote for.
						</p>
					</div>
					<div class="flex flex-col gap-3">
						<div class="border-2 border-ink px-3 py-2.5">
							<p class="text-[15px] text-muted">{c.tag}</p>
							<p class="text-xl font-bold">{c.resident.name}, {c.resident.age}</p>
							<p class="mb-2">{c.resident.address}</p>
							<dl class="grid grid-cols-[auto_1fr] gap-x-4 border-t border-line pt-1.5">
								<dt class="font-bold">Registered</dt>
								<dd>{c.resident.registration}</dd>
								<dt class="font-bold">Voted 2024</dt>
								<dd>{c.resident.voted2024 ? 'Yes' : 'No'}</dd>
								<dt class="font-bold">Would vote</dt>
								<dd><b class="text-b">Blue</b> (our guess)</dd>
							</dl>
						</div>
						<p class="text-[19px]/snug lg:text-xl/snug">
							You asked <b class="tabular-nums">1,200</b> people, <b>0.19%</b> of the city.
							<b class="text-b">Blue</b> got <b>{pct(c.town.poll.b)}</b>. In the real 2024 election
							it got <b>{pct(c.town.real.b)}</b>.
						</p>
						<p class="text-[15px] text-muted">Placeholder numbers.</p>
						<div class="flex flex-wrap gap-2.5">
							<button class={btnGo}>Ask 1,200 others</button>
							<button class={btn}>Ask 20 times</button>
						</div>
					</div>
				</div>
			</section>

			{#each c.later as r, i (r.id)}
				<section id="t-{r.id}" class="{section} py-4">
					{@render heading(i + 4, r.title)}
					<p class="text-muted">{r.gist}</p>
				</section>
			{/each}

			<section id="t-answer" class={section}>
				{@render heading(8, c.answer.title)}
				<p class="border-l-[5px] border-line pl-3 text-xl/snug font-bold lg:text-2xl/snug">
					{c.answer.text}
				</p>
			</section>
			<p class="border-t border-line pt-3 text-[15px] text-muted">
				Prototype, throwaway. Nothing here is final copy or real data.
			</p>
		</main>
	</div>
</div>
