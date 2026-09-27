import { chromium } from "playwright-core";
const b = await chromium.launch({ executablePath: "/opt/pw-browsers/chromium" });
for (const [label, net] of [["slow-4G", { latency: 150, downloadThroughput: 1.6e6 / 8, uploadThroughput: 750e3 / 8 }], ["4G", { latency: 60, downloadThroughput: 9e6 / 8, uploadThroughput: 3e6 / 8 }]]) {
  for (const which of ["slim", "full"]) {
    const ctx = await b.newContext(); const p = await ctx.newPage(); const c = await ctx.newCDPSession(p);
    await c.send("Emulation.setCPUThrottlingRate", { rate: 4 });
    await c.send("Network.enable"); await c.send("Network.emulateNetworkConditions", { offline: false, ...net });
    await p.goto("http://localhost:8765/phone/index.html"); await p.waitForFunction(() => (window).run);
    const o = await p.evaluate((w) => (window).run(w), which);
    const ms = o.poll.map(x => x.ms).sort((a, b) => a - b);
    console.log(label, which, "first poll (incl manifest):", o.firstPoll.ms.toFixed(0), "ms", o.firstPoll.kb.toFixed(0), "KB | next polls p50", ms[5].toFixed(0), "ms max", ms[9].toFixed(0), "ms", o.poll[5].kb.toFixed(0), "KB | 100 polls:", o.hundredPolls.ms.toFixed(0), "ms", (o.hundredPolls.kb/1024).toFixed(1), "MB", o.addrGetCold ? `| addr get cold ${o.addrGetCold.ms.toFixed(0)} ms ${o.addrGetCold.kb.toFixed(0)} KB ${JSON.stringify(o.addrGetCold.x)}` : "");
    await ctx.close();
  }
}
await b.close();
