<script lang="ts">
	// PROTOTYPE, throwaway: the whole explainer as it stands, in C2 · Plain compact (#16), put
	// together from the other prototypes so the page can be read top to bottom. The objection is
	// B · Headline (#25), the marbles are G · Converge (#15), Charlotte is the visual-style mock
	// (#20 is open), and the country is the national-rung draft (#31). Rungs with no widget yet are
	// stubs that say what they'll prove.
	import '../visual-style/tw.css';
	import Converge from '../marble-jars/Converge.svelte';
	import DotMap from '../visual-style/DotMap.svelte';
	import NationalRung from '../national-rung/NationalRung.svelte';
	import { nav, objection, marbles, charlotte, resident, stubs } from './content';

	let { speed = 0.75 }: { speed?: number } = $props();

	// The marble stages stack down the page. Back / Next step glide to the neighbouring stage (or
	// on to the Charlotte rung after the last), and jump instead for readers who ask for less motion.
	const stageIds = ['marbles-1', 'marbles-2', 'marbles-3'];
	function glide(from: number, dir: -1 | 1) {
		const id = stageIds[from + dir] ?? 'charlotte';
		const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
		document.getElementById(id)?.scrollIntoView({ behavior: reduce ? 'auto' : 'smooth' });
	}

	const btn =
		'min-h-11 cursor-pointer bg-glass px-3 py-1.5 text-base font-semibold text-ink shadow-[0_2px_0_var(--line)]';
	const btnGo =
		'min-h-11 cursor-pointer bg-go px-3 py-1.5 text-base font-semibold text-white shadow-[0_2px_0_var(--go-edge)]';
	const link = 'text-b underline underline-offset-3';
	const section = 'scroll-mt-4 border-t border-line py-5 lg:py-8';
	const pct = (n: number) => `${n.toFixed(1)}%`;
</script>

<!-- each rung heading is its own anchor link (#28) -->
{#snippet heading(id: string, n: number, title: string)}
	<h2 class="mb-3 text-[22px]/tight font-bold lg:mb-4 lg:text-[28px]">
		<a href="#{id}" class="text-ink no-underline">
			<span class="font-normal text-muted">{n} ·</span>
			{title}
		</a>
	</h2>
{/snippet}

{#snippet next(id: string, text: string)}
	<p class="mt-3"><a class="{link} text-base" href="#{id}">{text}</a></p>
{/snippet}

<div
	class="plain min-h-screen bg-bg px-4 pb-10 font-sans text-[17px]/[1.45] text-ink lg:px-8 lg:text-[19px]/normal"
	data-theme="light"
>
	<div class="mx-auto lg:grid lg:max-w-5xl lg:grid-cols-[11rem_minmax(0,40rem)] lg:gap-12">
		<aside class="hidden lg:block">
			<nav aria-label="Steps" class="sticky top-8 pt-10 text-base">
				<p class="mb-2 font-bold">Contents</p>
				<ol class="flex flex-col gap-1.5">
					{#each nav as r, i (r.id)}
						<li>
							<span class="text-muted">{i + 1}</span>
							<a class={link} href="#{r.id}">{r.short}</a>
						</li>
					{/each}
				</ol>
			</nav>
		</aside>

		<main class="mx-auto max-w-[40rem] lg:mx-0">
			<!-- 1 · The objection, as the page's headline (B · Headline, #25) -->
			<section id="objection" class="scroll-mt-4 pb-4">
				<p class="mt-6 text-base font-bold text-muted lg:mt-10">But the sample size…</p>
				<h1 class="mt-1 mb-3 text-[28px]/tight font-bold lg:text-5xl/tight">
					“{objection.text}”
				</h1>
				<p class="mb-1 text-[15px] text-muted">{objection.who}</p>
				<p class="mb-3 text-[19px]/snug lg:text-2xl/snug">{objection.promise}</p>
				<p class="text-base">You can skip any step.</p>
				<details class="mt-3 lg:hidden">
					<summary class="{link} cursor-pointer">Contents</summary>
					<ol class="mt-1 grid list-decimal grid-cols-2 gap-x-4 pl-6">
						{#each nav as r (r.id)}
							<li><a class={link} href="#{r.id}">{r.short}</a></li>
						{/each}
					</ol>
				</details>
			</section>

			<!-- 2 · Marbles (G · Converge, #15), stages stacked (#16) -->
			<section id="marbles" class={section}>
				{@render heading('marbles', 2, marbles.title)}
				<p class="mb-3">{marbles.intro}</p>
				{#each stageIds as id, i (id)}
					<div {id} class="conv scroll-mt-4 {i ? 'mt-5 border-t border-dim pt-5' : ''} mb-3">
						<Converge
							{speed}
							startStage={i}
							startTarget={i ? 1000 : 100}
							onStep={(dir) => glide(i, dir)}
						/>
					</div>
				{/each}
				<p>{marbles.outro}</p>
				{@render next('charlotte', 'Skip to step 3')}
			</section>

			<!-- 3 · Charlotte: the visual-style mock until #20 settles the widget -->
			<section id="charlotte" class={section}>
				{@render heading('charlotte', 3, charlotte.title)}
				<p class="mb-2">{charlotte.intro}</p>
				<p class="mb-2">{charlotte.voters}</p>
				<p class="mb-3">{charlotte.candidates}</p>
				<div class="flex flex-col gap-3 md:grid md:grid-cols-2 md:gap-6 lg:-mr-24">
					<div>
						<DotMap radius={1.5} viewBox="0 10 100 80" />
						<p class="text-[15px]/snug text-muted">
							Grey: not asked. Coloured: the voters you asked, by who they’d vote for.
						</p>
					</div>
					<div class="flex flex-col gap-3">
						<div class="border-2 border-ink px-3 py-2.5">
							<p class="text-[15px] text-muted">Invented resident · real address</p>
							<p class="text-xl font-bold">{resident.name}, {resident.age}</p>
							<p class="mb-2">{resident.address}</p>
							<dl class="grid grid-cols-[auto_1fr] gap-x-4 border-t border-line pt-1.5">
								<dt class="font-bold">Registered</dt>
								<dd>{resident.registration}</dd>
								<dt class="font-bold">Voted 2024</dt>
								<dd>Yes</dd>
								<dt class="font-bold">Would vote</dt>
								<dd><b class="text-b">Blue</b> (our guess)</dd>
							</dl>
						</div>
						<p class="text-[19px]/snug lg:text-xl/snug">
							You asked until <b class="tabular-nums">1,200</b> voters had answered (<b>0.19%</b>
							of the city). <b class="text-b">Blue</b> got <b>{pct(charlotte.poll.b)}</b>. In the
							real 2024 election it got <b>{pct(charlotte.real.b)}</b>.
						</p>
						<p class="text-[15px] text-muted">
							You met {charlotte.asked.toLocaleString('en-US')} people to get there; the {(
								charlotte.asked - 1200
							).toLocaleString('en-US')} who didn’t vote weren’t counted. Placeholder numbers.
						</p>
						<div class="flex flex-wrap gap-2.5">
							<button class={btnGo}>Ask 1,200 others</button>
							<button class={btn}>Ask 20 times</button>
						</div>
					</div>
				</div>
			</section>

			<!-- 4–6 · stubs: no widget designed yet -->
			{#each stubs as r (r.id)}
				<section id={r.id} class={section}>
					{@render heading(r.id, r.n, r.title)}
					<p class="mb-2">{r.claim}</p>
					<p
						class="border-2 border-dashed border-line px-3 py-6 text-center text-[15px] text-muted"
					>
						{r.widget}
					</p>
				</section>
			{/each}

			<!-- 7 · The whole country (#31 draft) -->
			<NationalRung />

			<!-- 8 · The objection answered (B · Headline, #25) -->
			<section id="answer" class={section}>
				{@render heading('answer', 8, 'Back to the objection')}
				<p class="mb-3 text-muted">“{objection.text}”</p>
				<p class="text-[26px]/tight font-bold lg:text-4xl/tight">{objection.answer}</p>
				<p class="mt-3">
					<a class={link} href="#city-only">{objection.why}</a> (step 4)
				</p>
			</section>

			<p class="border-t border-line pt-3 text-[15px] text-muted">
				Prototype, throwaway. Nothing here is final copy, and the Charlotte numbers are
				placeholders.
			</p>
		</main>
	</div>
</div>
