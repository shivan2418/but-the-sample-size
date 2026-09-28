# Drawing every resident's dot on a phone

Research for issue #22, "Drawing every resident's dot on a phone". Researched 2026-09-28, on the map owner's PC, against the real geocoded residents from #10 (7,684,048 with a house point statewide, 641,030 of them in Charlotte), plus live requests to GitHub Pages. Scripts: [`prototypes/dot-rendering/`](../../prototypes/dot-rendering/).

**Question.** A static page on GitHub Pages, with no backend, has to draw one dot per resident on a phone: about 645k for Charlotte and 7.85M for North Carolina. Every dot shows before any poll, coloured by party or race, and the residents a poll draws light up on top. Which of these works: pre-rendered raster tiles, vector tiles in one static archive (PMTiles over HTTP Range), WebGL points straight from zonemapdb blocks, or a mix? Compare bytes, first paint on a mid-range phone, zooming from state to street, fit with SvelteKit + zonemapdb, how lit-up dots go on top, and whether GitHub Pages handles Range requests and the file sizes.

## Answer

- **Charlotte: one flat file of every dot, drawn with WebGL.** All 641,030 dots fit in **1.21 MB gzipped** (3.85 MB unpacked). That's two uint16 coordinates over Charlotte's bounding box (0.5–0.7 m precision, fine at street level) plus one party byte and one race byte, sorted along a Morton curve so gzip can squeeze it. Every resident is drawn at every zoom, from the whole city down to one street, and switching party ↔ race is instant. Lit-up dots are a second, small draw call on top. The file is fetched whole, so it needs no Range requests.
- **North Carolina: a hybrid of raster tiles zoomed out and vector dot tiles zoomed in.** Up to map zoom 12, show pre-rendered raster tiles in which **all 7.68M dots** are painted into pixels. That's about 25 MB per colouring (48 MB for party + race) in ~10,800 files per colouring. The whole-state view on a phone costs **~80 KB**, and a city view 320–430 KB. From map zoom 13, show vector tiles with **every dot kept**, no dropping (59 MB, 36,140 tiles). A street-level view costs 60–280 KB. Poll dots are a small GeoJSON circle layer on top.
- **Use MapLibre GL JS for both rungs** (~0.30 MB gzipped, lazy-loaded). The state rung uses its raster, vector and GeoJSON sources. The Charlotte rung draws its flat file through a MapLibre custom WebGL layer, so both maps share pinch-zoom, panning and styling. No basemap is needed: on white, the dots are the map (C2 · Plain compact).
- **Don't put a PMTiles archive on GitHub Pages.** It doesn't work from a browser. GitHub Pages gzips `.pmtiles` files on the fly (served as `application/octet-stream`) and applies the byte range to the *gzipped* stream. A request for bytes 0–6 returns `1f 8b 08…` (a gzip header), not the `PMTiles` magic. Browsers can't opt out: `Accept-Encoding` is a forbidden request header. Serve tiles as plain `{z}/{x}/{y}` files instead. GitHub Pages does answer Range requests (`206`); only the compression breaks them.
- **Don't draw dots from zonemapdb blocks.** Resident blocks are in random draw order and hold an address id, not a coordinate. Drawing everyone would mean fetching every block: ~23 MB for Charlotte and ~280 MB for the state (from #11's 43 KB per 1,200 residents). zonemapdb stays the poll engine. Each resident record gains its dot's position (Charlotte: an index into the dot file; state: quantized x/y), so a poll's results can light up their dots without any extra fetch.
- **GitHub Pages fits, with room to spare.** The dot data totals about 110 MB (raster 48 + vector 59 + Charlotte 1–4). With zonemapdb's resident data (~180–370 MB, #5/#11) that's well under the 1 GB site limit, and no file comes near git's 100 MiB limit. The real limits are the **10-minute deploy timeout** and the **100 GB/month soft bandwidth** limit (~20,000 heavy visits a month at ~5 MB each). Tiles are built on the owner's PC (local-only data), so ship them as a Release asset (2 GiB per file) that the Pages workflow unpacks, rather than committing 60k tile files to git.

---

## 1. What "every dot" means on a phone

A phone viewport is about 390 × 844 CSS px. On a DPR-3 screen that's ~3M device pixels. At the whole-state view (MapLibre zoom ≈ 5), North Carolina's 8.8° of longitude spans those 390 px, so each device pixel covers ~100 residents. Charlotte's whole-city view (zoom ≈ 9.6) puts about one resident on every device pixel, and more in apartment blocks.

So "every dot visible" can only be literal from about city zoom inward. Zoomed out, the honest version is that **every resident contributes to the pixels**: each pixel is coloured by the mix of the dots under it and gets darker the more of them there are. That's the look of the Weldon Cooper Center's [Racial Dot Map](https://demographics.coopercenter.org/racial-dot-map) (308,745,538 dots, one per person). Pre-rendered raster tiles can do this. Vector tiles can't. Vector tiles have to *drop* dots at low zoom to stay small (tippecanoe's default drop rate is 2.5× per zoom below the base zoom), so the reader would see a sample. For a page arguing that samples work, "these dots are a sample" at the state view would be confusing.

## 2. Options measured

All sizes come from the real residents (`residents_geo.parquet` from #10). The ~2% without a local point are excluded here, so the final build (99.6% with a dot, #10) will be about 2% larger. "Viewport" means the tiles covering one 390 × 844 CSS px phone screen, centred on uptown Charlotte, downtown Raleigh, rural Sampson County, or the state.

### A. One flat binary of every dot ([`02_raw_sizes.py`](../../prototypes/dot-rendering/02_raw_sizes.py))

| layout | Charlotte (641,030) | North Carolina (7,684,048) |
|---|---|---|
| float32 lon/lat + 2 bytes, unsorted, gzip | 3.7 MB | 44.0 MB |
| uint32 Mercator x/y + 2 bytes, Morton-sorted, gzip | 1.3 MB | 19.7 MB |
| **uint16 x/y over the bounding box + 2 bytes, Morton-sorted, gzip** | **1.21 MB** (0.5–0.7 m precision) | 14.9 MB (but 12 × 5 m precision) |
| unpacked, in GPU memory (uint16 layout) | 3.85 MB | 46.1 MB |

Spatial sorting is what makes this small. It cuts gzip size about 3× compared with random order. Of Charlotte's 1.21 MB, the coordinates are 0.91 MB, party 148 KB and race 154 KB. The race column could load later.

Charlotte fits comfortably. The state doesn't: 15–20 MB before the first dot, and 7.7M points redrawn every frame on a phone GPU. deck.gl's own guidance is that a basic point layer stays at 60 fps "up to about 1M (one million) data items" on a 2015 MacBook Pro ([deck.gl performance](https://deck.gl/docs/developer-guide/performance)). A phone is weaker than that, and 7.7M is 7.7× the number.

### B. Vector tiles ([`03_tippecanoe.sh`](../../prototypes/dot-rendering/03_tippecanoe.sh), [`04_vector_sizes.py`](../../prototypes/dot-rendering/04_vector_sizes.py))

Built with tippecanoe 2.82.0 ([felt/tippecanoe](https://github.com/felt/tippecanoe)), one point per resident with `p` and `r` attributes, gzip-compressed MVT tiles.

| tile set | total | tiles | Charlotte viewport | Raleigh viewport |
|---|---|---|---|---|
| **Statewide, z5–14, `--drop-densest-as-needed`** (dots dropped below z14) | 58.4 MB | 39,138 | z5 11 KB · z9 112 KB · z11 259 KB · z13 151 KB | z5 11 KB · z9 116 KB · z12 198 KB |
| **Statewide, every dot at z12–14** (`-B12 --no-feature-limit --no-tile-size-limit`) | 85.6 MB | 38,309 | z12 858 KB · z13 276 KB · z14 61 KB | z12 781 KB · z13 110 KB · z14 73 KB |
| &nbsp;&nbsp;of which z12 / z13 / z14 | 26.3 / 28.2 / 31.2 MB | 2,169 / 7,907 / 28,233 | max tile 231 / 67 / 24 KB | |
| Charlotte only, z8–14, base zoom 14 | 4.0 MB | 380 | z10 83 KB · z12 216 KB | |

With every dot kept, z12 is too heavy (858 KB for one Charlotte screen, tiles up to 231 KB). From z13 it's cheap. With dropping, low zooms are cheap but show a thinned sample (section 1). Vector tiles are the right tool from map zoom 13 in: they're crisp at any zoom (MapLibre overzooms z14 to street level), and a colour switch is only a paint-property change with no new download.

### C. Pre-rendered raster tiles ([`05_raster.py`](../../prototypes/dot-rendering/05_raster.py), [`06_raster_view.py`](../../prototypes/dot-rendering/06_raster_view.py))

Every one of the 7.68M dots is painted into 512 × 512 px tiles shown at 256 CSS px (sharp on 2× screens). Each pixel's colour is the mean of its dots' colours, and it gets more opaque the more dots it holds, composited on white. The party palette is DEM blue, REP red, unaffiliated grey and others yellow. Encoder: after trying WebP lossy (q80, q50), WebP lossless, PNG and 64-colour PNG on sample tiles ([`05b_encoders.py`](../../prototypes/dot-rendering/05b_encoders.py)), **WebP lossless after a 64-colour quantize** was smallest or near-smallest at every zoom (Charlotte z11: 60 KB vs 114 KB for WebP q80 and 111 KB for PNG).

Party colouring, whole state:

| raster z (shown at map zoom) | tiles | total | median tile | max tile |
|---|---|---|---|---|
| 5 (4) | 2 | 0.02 MB | 12 KB | 13 KB |
| 6 (5) | 2 | 0.08 MB | 39 KB | 48 KB |
| 7 (6) | 6 | 0.24 MB | 22 KB | 111 KB |
| 8 (7) | 16 | 0.61 MB | 29 KB | 101 KB |
| 9 (8) | 47 | 1.37 MB | 27 KB | 82 KB |
| 10 (9) | 161 | 2.72 MB | 13 KB | 77 KB |
| 11 (10) | 582 | 4.55 MB | 5 KB | 64 KB |
| 12 (11) | 2,154 | 6.66 MB | 1.5 KB | 35 KB |
| 13 (12) | 7,866 | 9.07 MB | 0.6 KB | 14 KB |
| **total** | **10,836** | **25.3 MB** | | |

Race tiles run 10–15% smaller at z5–11 (measured). Both colourings together come to about 48 MB.

Bytes for one phone screen (party):

| map zoom | whole state | Charlotte | Raleigh | rural Sampson |
|---|---|---|---|---|
| 5 (state) | **79 KB** | 79 KB | 79 KB | 79 KB |
| 7 | 455 KB | 380 KB | 303 KB | 355 KB |
| 9 (city) | 193 KB | **320 KB** | 420 KB | 181 KB |
| 10 | 97 KB | 339 KB | 401 KB | 50 KB |
| 12 | 16 KB | 140 KB | 99 KB | 11 KB |

The worst screen anywhere is ~450 KB. Raster tiles stop being attractive past zoom 12: file counts roughly quadruple per zoom (z15 alone would be ~100k files per colouring), dots blur when overzoomed, and every colour switch re-downloads the screen.

### D. WebGL points straight from zonemapdb blocks

Rejected. zonemapdb fetches whole blocks and filters them ([zonemapdb README](https://github.com/shivan2418/zonemapdb)). The resident collections are sorted by random draw number (#5, #11), so no block covers a place on the map. Every screen would need every block: ~23 MB for Charlotte and ~280 MB statewide, at #11's 43 KB per 1,200 residents. And the blocks hold an `addr` id, not coordinates. A zonemapdb collection sorted by a spatial key would amount to rebuilding a tile pyramid by hand. zonemapdb is the right tool for polls, and the dot map needs a spatial file layout instead.

### E. Hybrids

| | state first paint | city view | street view | every resident shown? | colour switch |
|---|---|---|---|---|---|
| raster only | 79 KB | 320–420 KB | ~100k+ files per zoom, blurry | yes (in pixels) | re-download |
| vector only, with dropping | 11 KB | 112–260 KB | 60–150 KB | **no**, sampled below z14 | instant |
| **raster ≤ z12, vector (every dot) ≥ z13** | **79 KB** | **320–420 KB** | **60–280 KB** | **yes** | re-download zoomed out, instant zoomed in |
| flat binary (Charlotte only) | — | 1.21 MB once, then nothing | nothing more | yes, literally | instant |

For Charlotte, the flat binary is simplest. It draws every resident literally, and the lit-up link is just an index. It costs more up front than a raster screen (1.21 MB vs ~330 KB). If first paint matters more, show the state raster tiles for Charlotte while the binary loads, then swap. They're already built, so the swap costs nothing extra.

## 3. First paint on a mid-range phone

No real phone was available for this study, so these are transfer estimates on Lighthouse's default mobile profile ("Slow 4G": 150 ms latency, 1.6 Mbps down, 4× CPU slowdown; "roughly the bottom 25% of 4G connections" — [Lighthouse throttling docs](https://github.com/GoogleChrome/lighthouse/blob/main/docs/throttling.md)). At 1.6 Mbps, 1 MB takes ~5 s.

| what | bytes | Slow 4G | at 10 Mbps |
|---|---|---|---|
| MapLibre GL JS 6.11.2 (`maplibre-gl.mjs` + `maplibre-gl-shared.mjs`, gzipped) | ~0.30 MB | ~1.5 s | ~0.25 s |
| State view, raster | 79 KB | ~0.5 s | ~0.2 s |
| Charlotte view, raster (fallback while the binary loads) | ~330 KB | ~1.8 s | ~0.4 s |
| Charlotte, all dots (flat binary) | 1.21 MB | ~6 s | ~1 s |
| Street view, vector z13–14 | 60–280 KB | 0.5–1.5 s | < 0.4 s |
| *(rejected)* North Carolina flat binary | ~15 MB | ~75 s | ~12 s |
| *(rejected)* vector every dot at z12, Charlotte screen | 858 KB | ~4.4 s | ~0.8 s |

Two things keep this acceptable. First, the map is lazy-loaded (per #2's stack notes), so MapLibre and the Charlotte binary can prefetch while the reader is still on the marble rung. Second, the heavy Charlotte file loads once and costs nothing afterwards: zooming, panning, recolouring and every poll reuse it.

GPU cost still needs checking on a real mid-range phone before the widget is built. 641k points is below deck.gl's ~1M guideline for a 2015 laptop, and the unpacked buffer is only 3.85 MB. Still, a phone's fill rate is the risk. Draw 1–3 device-px quads, not circles with outlines, zoomed out.

## 4. Fit with SvelteKit + zonemapdb

- **One map library, lazy-loaded.** MapLibre GL JS (BSD-3) can load inside a Svelte component with a dynamic `import()` in `onMount`, which suits SvelteKit's static adapter (no SSR of the map). Sources for the state rung:
  - raster source, `tiles: [".../raster/party/{z}/{x}/{y}.webp"]`, `tileSize: 256` (the style spec default is 512, so it must be set), `maxzoom: 13`, the layer shown up to zoom 13;
  - vector source for the dot tiles, the layer shown from zoom 13, `circle-color` driven by `p` or `r`;
  - GeoJSON source for poll dots.
  ([MapLibre sources](https://maplibre.org/maplibre-style-spec/sources/)).
- **Charlotte's flat file** goes in through a custom layer, which "render[s] directly into the map's GL context using the map's camera" ([CustomLayerInterface](https://maplibre.org/maplibre-gl-js/docs/API/interfaces/CustomLayerInterface/)). Pinch-zoom and panning come from MapLibre, and the layer is ~150 lines of WebGL: one instanced quad per dot, colour looked up from the party or race byte through a small palette uniform.
- **The link to polls.** Build the dots and the zonemapdb residents from the same table, and give each resident record its dot:
  - Charlotte: `d`, the dot's index in the Morton-sorted file (fits in 20 bits);
  - statewide: `x`, `y` as integers in the same quantization as the tiles.

  A poll's results then carry everything needed to light them up, with no extra fetch. That's about 6–8 more gzipped bytes per resident, or ~10 KB for a 1,200 poll.
- **Apartments (#10).** Bake the sunflower spread into the dot coordinates at build time, in the flat file, the tiles *and* the resident's `d`/`x`/`y`. A lit-up dot then lands exactly on its base dot. The real building point stays in the address data.
- **Build.** The tiles need the geocoded residents, which live only on the owner's PC (#2's local-only rule). The raster pass took ~5 min for one colouring at z5–13 and tippecanoe ~1 min. The output (~110 MB, ~60k files) is too churny for git. Upload it as a GitHub Release asset ("Each file included in a release must be under 2 GiB" — [About releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)) and have the Pages workflow download and unpack it into the build before `upload-pages-artifact`.

## 5. Drawing lit-up poll dots over the base layer

- **State rung (MapLibre).** A GeoJSON source holds only the poll's residents (1,200–12,000 points). Its `circle` layer sits above both base layers: larger radius, fully opaque, a 1 px dark stroke, filled with the party or race colour. `setData` replaces the set for a new poll. `updateData` patches it when draws are animated one by one; it needs feature ids and is the documented faster path "for sources with lots of features" ([GeoJSONSource](https://maplibre.org/maplibre-gl-js/docs/API/classes/GeoJSONSource/)). While a poll is shown, dim the base (`raster-opacity` and `circle-opacity` around 0.35) so lit dots stand out even over dense raster pixels. Layer order guarantees they're on top. No feature-state is needed on the base tiles.
- **Charlotte (custom layer).** Draw the base buffer, then a second draw call over a small index buffer of the poll's `d` values: bigger, with an outline. Updating a poll means rewriting a few thousand indices (`bufferSubData`), so draws can animate one per frame. Drawing lit dots in a separate pass keeps them on top, whatever their place in the spatial sort.
- **Watching draws happen.** Both paths add dots in draw order, so the "watch the draw" animation is the same code: push the next n residents from zonemapdb's contiguous range.

## 6. GitHub Pages: Range requests, compression and size limits

Tested live on 2026-09-28 ([`07_ghpages_check.sh`](../../prototypes/dot-rendering/07_ghpages_check.sh)):

| request | status | Content-Encoding | what comes back |
|---|---|---|---|
| `.pmtiles` (application/octet-stream), Range 0–6, `Accept-Encoding: identity` | 206 | — | `PMTiles` (correct) |
| same, with a browser's `Accept-Encoding: gzip, deflate, br, zstd` | 206 | gzip | `1f 8b 08 00…`: bytes 0–6 of the **gzipped** file; `Content-Range` total 9,138,901 vs 9,202,547 real |
| `.gz` (application/gzip), Range, gzip accepted | 206 | — | the file's own bytes (not recompressed) |
| `.png` (image/png), Range, gzip accepted | 206 | — | the file's own bytes |
| `.js`, `Accept-Encoding: br, zstd` only | 200 | — | uncompressed: Pages serves gzip, never brotli |

- **Range works, but not on files GitHub compresses.** PMTiles readers need exact byte ranges ("PMTiles readers use HTTP Range Requests to fetch only the relevant tile or metadata" — [PMTiles docs](https://docs.protomaps.com/pmtiles/)). Pages compresses `application/octet-stream` (mime-db marks it compressible) and ranges the compressed stream. A browser always sends `Accept-Encoding: gzip`, and page code can't change that: it's a forbidden request header ([Fetch standard](https://fetch.spec.whatwg.org/#forbidden-request-header)). The same behaviour broke sql.js-httpvfs on Pages in 2025 ([community discussion #162857](https://github.com/orgs/community/discussions/162857), no GitHub staff reply). Protomaps' own hosting page only says Pages "supports repositories up to 1 GB" ([cloud storage](https://docs.protomaps.com/pmtiles/cloud-storage)), which misses this. Renaming the archive to an extension Pages doesn't compress (`.png`, `.zip`) would work today, but it's undocumented and could break the day GitHub changes its CDN rules.
- **Plain tile directories avoid the problem, and they're how zonemapdb works too.** `.webp` isn't recompressed. For vector tiles:
  - Store them pre-gzipped as `{z}/{x}/{y}.pbf.gz`. Pages serves `.gz` untouched, so disk use equals transfer: 59 MB instead of 283 MB uncompressed for z13–14.
  - Gunzip them in the browser through `maplibregl.addProtocol` ("A tile is an `ArrayBuffer`, for example a non-compressed pbf vector tile" — [addProtocol](https://maplibre.org/maplibre-gl-js/docs/API/functions/addProtocol/)) with `DecompressionStream('gzip')`, Baseline since May 2023 ([MDN](https://developer.mozilla.org/en-US/docs/Web/API/DecompressionStream)).

  The Charlotte file can be pre-gzipped the same way, or served as `.bin` and left to Pages' on-the-fly gzip. That's fine for a whole-file fetch.
- **Limits** ([GitHub Pages limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits); [upload-pages-artifact](https://github.com/actions/upload-pages-artifact); [large files](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)):
  - "Published GitHub Pages sites may be no larger than 1 GB." Dots ~110 MB + zonemapdb data ~180–370 MB: fits.
  - Deployments "timeout if they take longer than 10 minutes". ~60k tile files + ~16k zonemapdb blocks in one artifact needs a timing check on the first deploy. It's the most likely limit to bite.
  - "A *soft* bandwidth limit of 100 GB per month." A heavy visit (state + Charlotte + some zooming) is ~3–5 MB, so ~20–30k visits a month. If the page goes viral, move the tiles behind a CDN (e.g. Cloudflare R2, where PMTiles would also work).
  - Git blocks files over 100 MiB. No single file here comes close; the largest tile is 231 KB.
  - Artifacts can't contain symbolic or hard links. The tile tree is plain files.

## 7. What's left for the widget ticket

- Check on a real mid-range Android phone that 641k instanced quads pan at an acceptable frame rate. The fallback is the hybrid tiles for Charlotte too.
- Palette. The party and race colours used here are placeholders; the widget ticket picks accessible ones. Raster tiles bake the palette in, so a palette change means a rebuild (~10 min).
- The raster/vector handover at zoom 12 → 13. Match the raster dot size at z13 to the vector circle radius so the switch doesn't jump.
