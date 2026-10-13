<script lang="ts">
	// PROTOTYPE, throwaway: the jar beside the slider, draining as marbles come out. A small jar
	// draws every marble, stacked from the bottom; a taken marble's place is filled by the one on
	// top, so the level drops by one. A jar too big to draw marble by marble is a speckle of red and
	// blue that drains at the true rate, so a few thousand barely dent a million.

	let {
		colors,
		left,
		version = 0
	}: {
		/** The jar's marbles, 1 for red and 0 for blue. Only the first `left` are still in it. */
		colors: Uint8Array;
		left: number;
		/** Bumped by the parent whenever `colors` changes in place, so the jar redraws. */
		version?: number;
	} = $props();

	const W = 96;
	const H = 190;
	const LID = 10; // the lid's height
	const PAD = 5; // glass thickness, inside the outline
	const MAX_DRAWN = 5000; // above this, the jar is drawn as a speckle

	let canvas: HTMLCanvasElement;
	let speckle: HTMLCanvasElement | null = null;

	function draw() {
		const n = colors.length;
		const dpr = window.devicePixelRatio || 1;
		canvas.width = W * dpr;
		canvas.height = H * dpr;
		const g = canvas.getContext('2d')!;
		g.scale(dpr, dpr);
		const css = getComputedStyle(canvas);
		const v = (name: string) => css.getPropertyValue(name).trim();
		const [cRed, cBlue, line, glass] = [v('--a'), v('--b'), v('--line'), v('--glass')];

		// the inside of the jar
		const x0 = PAD + 2,
			y0 = LID + PAD + 2,
			iw = W - 2 * x0,
			ih = H - y0 - PAD - 2;

		// lid and glass
		g.fillStyle = glass;
		g.strokeStyle = line;
		g.lineWidth = 2;
		g.beginPath();
		g.roundRect(W * 0.3, 1, W * 0.4, LID, 2);
		g.fill();
		g.stroke();
		g.beginPath();
		g.roundRect(1, LID, W - 2, H - LID - 1, 8);
		g.fill();
		g.stroke();

		g.save();
		g.beginPath();
		g.roundRect(x0, y0, iw, ih, 5);
		g.clip();

		if (n <= MAX_DRAWN) {
			// marbles in a grid, as big as the jar allows
			let d = Math.sqrt((iw * ih) / n);
			let cols = Math.floor(iw / d);
			while (cols * Math.floor(ih / d) < n) {
				d *= 0.98;
				cols = Math.floor(iw / d);
			}
			const off = (iw - cols * d) / 2;
			const r = Math.max(0.6, d / 2 - 0.4);
			for (let i = 0; i < left; i++) {
				const row = Math.floor(i / cols),
					col = i % cols;
				g.fillStyle = colors[i] ? cRed : cBlue;
				g.beginPath();
				g.arc(x0 + off + col * d + d / 2, y0 + ih - row * d - d / 2, r, 0, Math.PI * 2);
				g.fill();
			}
		} else {
			// a speckle in the jar's own mix, cut at the level of what's left
			if (!speckle) {
				speckle = document.createElement('canvas');
				speckle.width = Math.ceil(iw * dpr);
				speckle.height = Math.ceil(ih * dpr);
				const s = speckle.getContext('2d')!;
				const img = s.createImageData(speckle.width, speckle.height);
				const share = colors.reduce((a, c) => a + c, 0) / n;
				const rgb = (c: string) => {
					s.fillStyle = c;
					const hex = s.fillStyle.slice(1);
					return [0, 2, 4].map((k) => parseInt(hex.slice(k, k + 2), 16));
				};
				const [red, blue] = [rgb(cRed), rgb(cBlue)];
				for (let p = 0; p < img.data.length; p += 4) {
					const c = Math.random() < share ? red : blue;
					img.data.set([c[0], c[1], c[2], 255], p);
				}
				s.putImageData(img, 0, 0);
			}
			const h = (left / n) * ih;
			g.drawImage(
				speckle,
				0,
				speckle.height * (1 - left / n),
				speckle.width,
				speckle.height * (left / n),
				x0,
				y0 + ih - h,
				iw,
				h
			);
		}
		g.restore();
	}

	$effect(() => {
		void version;
		void left;
		void colors;
		draw();
	});
</script>

<figure class="flex shrink-0 flex-col items-center gap-1">
	<canvas bind:this={canvas} style:width="{W}px" style:height="{H}px" aria-hidden="true"></canvas>
	<figcaption class="font-mono text-[12px] text-muted tabular-nums">
		{left.toLocaleString('en-US')} left in the jar
	</figcaption>
</figure>
