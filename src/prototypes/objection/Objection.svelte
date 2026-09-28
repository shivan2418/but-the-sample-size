<script lang="ts">
	// PROTOTYPE, throwaway: the objection that opens the page (rung 1 in the C2 numbering) and the
	// same objection answered at the end (rung 8), in four looks. Each look is set in a slice of the
	// C2 · Plain compact page around it, so it's judged in place: the masthead and the start of the
	// marble rung for the opening, the end of the country rung for the answer.
	import '../visual-style/tw.css';
	import { wordings } from './content';

	export type Look = 'quote' | 'headline' | 'comment' | 'thread';

	let {
		look = 'quote',
		state = 'opening',
		wording = 0
	}: { look?: Look; state?: 'opening' | 'answered'; wording?: number } = $props();

	const w = $derived(wordings[wording] ?? wordings[0]);
	const link = 'text-b underline underline-offset-3';
	const section = 'scroll-mt-4 border-t border-line py-5 lg:py-8';
	const title = 'But the sample size…';
	const dek = 'Why a random poll of about 1,200 people can describe a whole country.';
	const skip = 'You can skip any step.';
</script>

{#snippet heading(n: number, text: string)}
	<h2 class="mb-3 text-[22px]/tight font-bold lg:mb-4 lg:text-[28px]">
		<span class="font-normal text-muted">{n} ·</span>
		{text}
	</h2>
{/snippet}

{#snippet whyLink()}
	<p class="mt-3"><a class={link} href="#t-city-only">{w.why}</a> (step 4)</p>
{/snippet}

<!-- A · Quote: the C2 page as it stands. The objection is a bold pull quote on a grey rule. -->
{#snippet quote()}
	<p class="mb-1 border-l-[5px] border-line pl-3 text-xl/snug font-bold lg:text-2xl/snug">
		“{w.objection}”
	</p>
	<p class="mb-3 pl-4 text-[15px] text-muted">{w.who}</p>
	{#if state === 'opening'}
		<p>{w.promise} {skip}</p>
	{:else}
		<p class="text-xl/snug font-bold lg:text-2xl/snug">{w.answer}</p>
		{@render whyLink()}
	{/if}
{/snippet}

<!-- B · Headline: no card at all. The objection is the page's headline, the promise its dek. -->
{#snippet headline()}
	{#if state === 'opening'}
		<p class="mt-6 text-base font-bold text-muted lg:mt-10">{title}</p>
		<h1 class="mt-1 mb-3 text-[28px]/tight font-bold lg:text-5xl/tight">“{w.objection}”</h1>
		<p class="mb-1 text-[15px] text-muted">{w.who}</p>
		<p class="mb-5 text-[19px]/snug lg:text-2xl/snug">{w.promise} {skip}</p>
	{:else}
		<p class="mb-3 text-muted">“{w.objection}”</p>
		<p class="text-[26px]/tight font-bold lg:text-4xl/tight">{w.answer}</p>
		{@render whyLink()}
	{/if}
{/snippet}

<!-- C · Comment: a plain outlined box holding the comment. No avatar, handle, likes or site. -->
{#snippet comment()}
	<figure class="mb-3 border border-line px-3 py-2.5">
		<figcaption class="mb-1 text-[15px] text-muted">{w.who}</figcaption>
		<blockquote class="text-lg/snug">{w.objection}</blockquote>
	</figure>
	{#if state === 'opening'}
		<p>{w.promise} {skip}</p>
	{:else}
		<p class="text-xl/snug font-bold lg:text-2xl/snug">{w.answer}</p>
		{@render whyLink()}
	{/if}
{/snippet}

<!-- D · Thread: the page replies under the comment, indented on a thin line, as a thread does. -->
{#snippet thread()}
	<p class="mb-1 text-[15px] text-muted">{w.who}</p>
	<p class="text-xl/snug font-bold lg:text-2xl/snug">{w.objection}</p>
	<div class="mt-3 ml-1 border-l-2 border-line pl-4">
		{#if state === 'opening'}
			<p>{w.promise}</p>
			<p class="mt-2 text-muted">{skip}</p>
		{:else}
			<p class="text-xl/snug font-bold lg:text-2xl/snug">{w.answer}</p>
			{@render whyLink()}
		{/if}
	</div>
{/snippet}

{#snippet body()}
	{#if look === 'quote'}{@render quote()}
	{:else if look === 'headline'}{@render headline()}
	{:else if look === 'comment'}{@render comment()}
	{:else}{@render thread()}{/if}
{/snippet}

<div
	class="plain min-h-screen bg-bg px-4 pb-10 font-sans text-[17px]/[1.45] text-ink lg:px-8 lg:text-[19px]/normal"
>
	<main class="mx-auto max-w-[40rem]">
		{#if state === 'opening'}
			{#if look === 'headline'}
				<section id="t-objection">{@render body()}</section>
			{:else}
				<h1 class="mt-6 mb-2 text-[30px]/tight font-bold lg:mt-10 lg:text-5xl/tight">{title}</h1>
				<p class="mb-4 text-[19px]/snug lg:text-2xl/snug">{dek}</p>
				<section id="t-objection" class={section}>{@render body()}</section>
			{/if}
			<section id="t-marbles" class={section}>
				{@render heading(2, 'A handful of marbles')}
				<p class="mb-3">
					Forget people for a moment. Here is a jar of red and blue marbles. You can’t see inside,
					but you can take some out and count them.
				</p>
				<div class="grid aspect-[4/3] place-items-center bg-glass text-muted">marble widget</div>
			</section>
		{:else}
			<section id="t-country" class="{section} pt-8">
				{@render heading(7, 'The whole country')}
				<p class="text-muted">
					…the same 1,200, and the spread of polls barely moves as the population grows to 155
					million.
				</p>
			</section>
			<section id="t-answer" class={section}>
				{@render heading(8, 'Back to the objection')}
				{@render body()}
			</section>
			<p class="border-t border-line pt-3 text-[15px] text-muted">
				Prototype, throwaway. Nothing here is final copy.
			</p>
		{/if}
	</main>
</div>
