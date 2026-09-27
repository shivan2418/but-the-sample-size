// PROTOTYPE, wipe me. Random polls within one place, two layouts, through blockdb's runtime.
//   filtered scan: statewide draw order, where { town|county|urban: equals, draw: { gte: r } }
//   place-major:   where { k: { gte: base + r, lt: base + size } }
// Both wrap around to the start of their order when the run from r comes up short.
// Usage: node poll_bench.mjs <blockdb checkout> <data dir>
import { readFile } from "node:fs/promises";

const [BLOCKDB, D] = process.argv.slice(2);
const { createClient } = await import(`${BLOCKDB}/packages/blockdb/dist/index.js`);
const meta = JSON.parse(await readFile(`${D}/places.json`, "utf8"));
const { K, n: N } = meta;
const byName = (kind, name) => meta.places.find((p) => p.kind === kind && p.name === name);

async function client(layout) {
  const { schema } = await import(`${D}/${layout}/src/blockdb/schema.ts`);
  const c = { data: 0, index: 0, files: 0 };
  const fetch = async (url) => {
    const path = new URL(url, "http://x").pathname;
    const b = await readFile(`${D}/${layout}/public${path}`);
    if (!path.includes("manifest")) { c.files++; path.includes("/index/") ? (c.index += b.length) : (c.data += b.length); }
    return new Response(b);
  };
  const db = createClient(schema, { basePath: "/blockdb", manifestCompression: "gzip", fetch, maxResults: 1e6 }).residents;
  return { db, c };
}

// one poll, fresh client (no block cache between polls), manifest not counted
async function poll(layout, place, n) {
  const { db, c } = await client(layout);
  const size = place ? place.size : N;
  n = Math.min(n, size);
  const r = Math.floor(Math.random() * size);
  let where, whereWrap;
  if (layout === "place") {
    const base = place.gid * K;
    where = { k: { gte: base + r, lt: base + size } };
    whereWrap = { k: { gte: base, lt: base + r } };
  } else {
    const f = !place ? {} : place.kind === "town" ? { town: { equals: place.gid } }
      : place.kind === "county" ? { county: { equals: place.gid - meta.places.filter((p) => p.kind === "town").length } }
      : { urban: { equals: place.kind === "urban" } };
    // the draw start is a random point in the statewide order, not in the place
    const rs = Math.floor(Math.random() * N);
    where = { ...f, draw: { gte: rs } };
    whereWrap = { ...f, draw: { lt: rs } };
  }
  const t = performance.now();
  let { records } = await db.findMany({ where, limit: n });
  let rounds = 1;
  if (records.length < n) {
    const more = await db.findMany({ where: whereWrap, limit: n - records.length });
    records = records.concat(more.records);
    rounds++;
  }
  return { n: records.length, files: c.files, dataKB: c.data / 1024, indexKB: c.index / 1024,
    ms: performance.now() - t, dPct: (100 * records.filter((x) => x.vote === "D").length) / records.length };
}

const PLACES = [
  ["state", null],
  ["town", byName("town", "CHARLOTTE")],
  ["town", byName("town", "CHAPEL HILL")],
  ["town", meta.places.filter((p) => p.kind === "town").sort((a, b) => Math.abs(a.size - 12000) - Math.abs(b.size - 12000))[0]],
  ["town", meta.places.filter((p) => p.kind === "town").sort((a, b) => Math.abs(a.size - 3000) - Math.abs(b.size - 3000))[0]],
  ["county", byName("county", "WAKE")],
  ["county", byName("county", "HYDE")],
  ["urban", meta.places.find((p) => p.kind === "urban")],
];
const SIZES = [[1200, 12], [12000, 4], ["full", 1]];
const med = (a) => { const s = [...a].sort((x, y) => x - y); return s[Math.floor(s.length / 2)]; };

console.log("place | size | poll | layout | files | data KB | index KB | ms (local) | D% range (true)");
for (const [kind, place] of PLACES) {
  const size = place ? place.size : N;
  const truth = place ? (100 * place.d) / size : (100 * meta.d) / N;
  for (const [n0, reps] of SIZES) {
    const n = n0 === "full" ? size : n0;
    if (n0 === "full" && (!place || size > 200000)) continue;
    if (n0 !== "full" && n >= size) continue;
    for (const layout of place ? ["state", "place"] : ["state"]) {
      // filtered scans of a full small place read the whole state: run once
      const res = [];
      for (let i = 0; i < (layout === "state" && (n0 === "full" || size < 50000) ? 1 : reps); i++) res.push(await poll(layout, place, n));
      const d = res.map((x) => x.dPct);
      console.log([place ? `${place.name} (${kind})` : "NORTH CAROLINA", size, res[0].n, layout === "state" ? "filtered scan" : "place-major",
        med(res.map((x) => x.files)), med(res.map((x) => x.dataKB)).toFixed(0), med(res.map((x) => x.indexKB)).toFixed(0),
        med(res.map((x) => x.ms)).toFixed(0), `${Math.min(...d).toFixed(1)}-${Math.max(...d).toFixed(1)} (${truth.toFixed(1)})`].join(" | "));
    }
  }
}
