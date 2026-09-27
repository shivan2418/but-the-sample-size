// PROTOTYPE, wipe me. Runs polls through blockdb's runtime against a built tree, counting fetched bytes.
import { createClient } from "../blockdb/packages/blockdb/dist/index.js";
import { readFile } from "node:fs/promises";
const dir = process.argv[2], n = Number(process.argv[3] ?? 200);
const { schema } = await import(`./${dir}/src/blockdb/schema.ts`);
let bytes = 0, files = 0;
const fetch = async (url) => { const b = await readFile(`${dir}/public${new URL(url, "http://x").pathname}`); bytes += b.length; files++; return new Response(b); };
const db = createClient(schema, { basePath: "/blockdb", manifestCompression: "gzip", fetch }).residents;
const N = 10077331;
await db.findMany({ where: { draw: { gte: 0 } }, limit: 1 });
console.log(`manifest+first: ${files} files ${(bytes/1024).toFixed(0)} KB`);
const res = [];
for (let i = 0; i < n; i++) {
  bytes = 0; files = 0;
  const r = Math.floor(Math.random() * (N - 1200)), t = performance.now();
  const { records } = await db.findMany({ where: { draw: { gte: r } }, limit: 1200 });
  res.push({ files, kb: bytes / 1024, ms: performance.now() - t, n: records.length, d: records.filter(x => x.vote === "D").length });
}
const q = (k, p) => { const s = res.map(x => x[k]).sort((a, b) => a - b); return s[Math.floor(p * (s.length - 1))].toFixed(1); };
console.log(`polls=${n} records=${res[0].n} files p50=${q("files",.5)} max=${q("files",1)} | KB p50=${q("kb",.5)} p95=${q("kb",.95)} max=${q("kb",1)} | ms p50=${q("ms",.5)} p95=${q("ms",.95)}`);
const dem = res.map(x => x.d / x.n * 100); console.log("D% across polls: min", Math.min(...dem).toFixed(1), "max", Math.max(...dem).toFixed(1), "(true 34.6)");
// lookup one resident by pk
bytes = 0; files = 0; const g = await db.get(4242424); console.log("get(draw):", files, "files", (bytes/1024).toFixed(1), "KB", JSON.stringify(g));
