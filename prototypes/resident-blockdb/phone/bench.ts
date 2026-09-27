// PROTOTYPE, wipe me. Browser-side poll benchmark.
import { createClient } from "../../blockdb/packages/blockdb/dist/index.js";
import { schema as full } from "../full/src/blockdb/schema.ts";
import { schema as slim } from "../slim/src/blockdb/schema.ts";
import { schema as addr } from "../addr/src/blockdb/schema.ts";
const N = 10077331;
(window as any).run = async (which: string) => {
  let bytes = 0, files = 0;
  const f = async (u: string, o: any) => { const r = await fetch(u, o); const b = await r.arrayBuffer(); bytes += b.byteLength; files++; return new Response(b); };
  const db = createClient(which === "full" ? full : slim, { basePath: `/${which}/public/blockdb`, manifestCompression: "gzip", fetch: f, maxResults: 200000 }).residents;
  const out: any = {};
  let t = performance.now(); await db.findMany({ where: { draw: { gte: 0 } }, limit: 1200 }); out.firstPoll = { ms: performance.now() - t, kb: bytes / 1024, files };
  const polls = [];
  for (let i = 0; i < 10; i++) { bytes = 0; files = 0; const r = Math.floor(Math.random() * (N - 1200)); t = performance.now();
    await db.findMany({ where: { draw: { gte: r } }, limit: 1200 }); polls.push({ ms: performance.now() - t, kb: bytes / 1024 }); }
  out.poll = polls;
  bytes = 0; files = 0; t = performance.now();
  const r0 = Math.floor(Math.random() * (N - 120000));
  const { records } = await db.findMany({ where: { draw: { gte: r0, lt: r0 + 120000 } }, limit: 120000 });
  out.hundredPolls = { ms: performance.now() - t, kb: bytes / 1024, n: records.length };
  if (which === "slim") {
    const a = createClient(addr, { basePath: `/addr/public/blockdb`, manifestCompression: "gzip", fetch: f }).addresses;
    bytes = 0; files = 0; t = performance.now(); const x = await a.get(123456); out.addrGetCold = { ms: performance.now() - t, kb: bytes / 1024, files, x };
  }
  return out;
};
