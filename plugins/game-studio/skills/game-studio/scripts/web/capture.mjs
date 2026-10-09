#!/usr/bin/env node
// Capture evidence from a running web game (Three.js / R3F / Babylon / PlayCanvas): screenshots with
// objective image metrics, console + page errors, failed requests, renderer stats, game state, a rough
// FPS figure, and an optional frame sequence (with held/pressed keys) for motion review.
//
// Usage: node capture.mjs --url http://localhost:5173 --out qa/captures/<milestone> [options]
//   --viewport 1280x720     page size (default 1280x720)
//   --timeout 20000         max ms to wait for window.__QA__.ready (default 20000)
//   --wait-ms 3000          settle time when the page has no __QA__ hook (default 3000)
//   --shots 3               screenshots to take when the page has no __QA__.shots (default 3)
//   --interval-ms 1000      gap between those screenshots (default 1000)
//   --sequence N            also capture N frames for motion review (+ seq_sheet.png)
//   --step-ms 100           time between sequence frames (uses __QA__.advance(ms) when present)
//   --hold KEY              hold a key during the sequence (Playwright key name, e.g. KeyW, ArrowLeft)
//   --press KEY             press a key once at the start of the sequence (e.g. Space)
//   --gpu                   use the machine's GPU instead of SwiftShader (faster; less deterministic)
//   --no-gray               skip the grayscale copy (<shot>_gray.png) written for every named shot
//   --allow-errors          exit 0 even when console/page errors occurred
// Requires `playwright` in the game project (npm i -D playwright; npx playwright install chromium).
// Set CHROMIUM_PATH to use a specific Chromium binary.
//
// Optional dev-only hook the game can expose to make captures deterministic and informative:
//   window.__QA__ = {
//     ready: true,                                   // set after assets loaded + first frame drawn
//     stats: () => ({ drawCalls, triangles, geometries, textures }),  // e.g. from renderer.info
//     state: () => ({ player: {x, y, z, hp}, enemies: 3, ... }),      // small JSON game state
//     shots: { overview: async () => {...}, player: async () => {...} }, // named camera/state presets
//     advance: async (ms) => {...},                  // step the fixed-timestep simulation
//   }
//
// Image metrics are computed on a 320 px copy of each screenshot. They are evidence, not verdicts:
// low lumaStd (flat contrast), low colorEntropyBits (few colors), high dominantColorShare (one color fills
// the frame), low edgeDensity (little structure) and clipping flags argue against a high visual score.
import { existsSync, mkdirSync, writeFileSync, readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { createRequire } from 'node:module';
import { pathToFileURL } from 'node:url';

// Packages are resolved from the game project (cwd) first, so the script can live in the skill folder.
async function importFromProject(name) {
  try {
    const req = createRequire(resolve(process.cwd(), 'package.json'));
    return await import(pathToFileURL(req.resolve(name)).href);
  } catch {
    return import(name);
  }
}

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, all) => {
  if (a.startsWith('--')) acc.push([a.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : true]);
  return acc;
}, []));
if (!args.url || !args.out) {
  console.error('usage: node capture.mjs --url URL --out DIR [--viewport WxH] [--sequence N] [--hold KeyW] [--gpu] ...');
  process.exit(2);
}
const [vw, vh] = String(args.viewport || '1280x720').split('x').map(Number);
const num = (k, d) => (args[k] === undefined ? d : Number(args[k]));
const outDir = resolve(String(args.out));
mkdirSync(outDir, { recursive: true });

let chromium;
try {
  const pw = await importFromProject('playwright');
  chromium = pw.chromium ?? pw.default?.chromium;
  if (!chromium) throw new Error('no chromium export');
} catch {
  console.error('error: playwright is not installed here. Run: npm i -D playwright && npx playwright install chromium');
  process.exit(2);
}

const launchArgs = args.gpu
  ? ['--ignore-gpu-blocklist', '--enable-gpu-rasterization']
  : ['--use-gl=angle', '--use-angle=swiftshader-webgl', '--enable-unsafe-swiftshader']; // documented Chromium software-WebGL switches
const executablePath = process.env.CHROMIUM_PATH || (existsSync('/opt/pw-browsers/chromium') ? '/opt/pw-browsers/chromium' : undefined);
const browser = await chromium.launch({ args: launchArgs, ...(executablePath ? { executablePath } : {}) });
const page = await browser.newPage({ viewport: { width: vw, height: vh } });
const tool = await browser.newPage(); // blank page for image math, isolated from the game

const report = { url: args.url, viewport: [vw, vh], renderer: args.gpu ? 'gpu' : 'swiftshader', consoleErrors: [],
  consoleWarnings: [], pageErrors: [], failedRequests: [], hook: false, fps: null, shots: [], sequence: [] };
page.on('console', (m) => {
  const where = m.location()?.url; // resource-load errors carry the failing URL here
  if (m.type() === 'error') report.consoleErrors.push(where ? `${m.text()} [${where}]` : m.text());
  if (m.type() === 'warning') report.consoleWarnings.push(m.text());
});
page.on('pageerror', (e) => report.pageErrors.push(String(e)));
page.on('requestfailed', (r) => report.failedRequests.push(`${r.url()} (${r.failure()?.errorText})`));
page.on('response', (r) => {
  if (r.status() >= 400) report.failedRequests.push(`${r.url()} (HTTP ${r.status()})`);
});
// A missing favicon and the warnings that screenshots themselves cause are not game errors.
const isNoise = (t) => /favicon\.ico/.test(t) || /GPU stall due to ReadPixels/.test(t);

const frames = (n = 2) => page.evaluate((k) => new Promise((res) => {
  let left = k; const tick = () => (--left <= 0 ? res() : requestAnimationFrame(tick)); requestAnimationFrame(tick);
}), n);
const hookCall = (fn) => page.evaluate((f) => {
  try {
    const v = window.__QA__?.[f] ? window.__QA__[f]() : null;
    const s = v == null ? null : JSON.stringify(v);
    return s && s.length > 4000 ? { truncated: s.slice(0, 4000) } : v;
  } catch (e) { return { error: String(e) }; }
}, fn);

async function imageMetrics(png) {
  return tool.evaluate(async (b64) => {
    const im = new Image(); im.src = 'data:image/png;base64,' + b64; await im.decode();
    const W = 320; const H = Math.max(3, Math.round((im.height * W) / im.width));
    const c = document.createElement('canvas'); c.width = W; c.height = H;
    const ctx = c.getContext('2d', { willReadFrequently: true }); ctx.drawImage(im, 0, 0, W, H);
    const d = ctx.getImageData(0, 0, W, H).data; const n = W * H; const lum = new Float32Array(n);
    const hist = new Map(); let sum = 0; let sum2 = 0; let sat = 0; let lo = 0; let hi = 0;
    for (let i = 0; i < n; i++) {
      const r = d[i * 4]; const g = d[i * 4 + 1]; const b = d[i * 4 + 2];
      const L = 0.2126 * r + 0.7152 * g + 0.0722 * b; lum[i] = L; sum += L; sum2 += L * L;
      const mx = Math.max(r, g, b); const mn = Math.min(r, g, b); sat += mx ? (mx - mn) / mx : 0;
      if (L < 5) lo++; if (L > 250) hi++;
      const key = ((r >> 5) << 6) | ((g >> 5) << 3) | (b >> 5); hist.set(key, (hist.get(key) || 0) + 1);
    }
    let entropy = 0; let top = 0;
    for (const v of hist.values()) { const p = v / n; entropy -= p * Math.log2(p); top = Math.max(top, v); }
    let edges = 0;
    for (let y = 1; y < H - 1; y++) for (let x = 1; x < W - 1; x++) {
      const i = y * W + x;
      const gx = lum[i - W + 1] + 2 * lum[i + 1] + lum[i + W + 1] - lum[i - W - 1] - 2 * lum[i - 1] - lum[i + W - 1];
      const gy = lum[i + W - 1] + 2 * lum[i + W] + lum[i + W + 1] - lum[i - W - 1] - 2 * lum[i - W] - lum[i - W + 1];
      if (Math.hypot(gx, gy) > 96) edges++;
    }
    const mean = sum / n;
    return { lumaMean: +mean.toFixed(1), lumaStd: +Math.sqrt(Math.max(0, sum2 / n - mean * mean)).toFixed(1),
      colorEntropyBits: +entropy.toFixed(2), dominantColorShare: +(top / n).toFixed(3),
      edgeDensity: +(edges / ((W - 2) * (H - 2))).toFixed(4), saturationMean: +(sat / n).toFixed(3),
      clippedShadows: +(lo / n).toFixed(3), clippedHighlights: +(hi / n).toFixed(3) };
  }, png.toString('base64'));
}
function visualFlags(m) {
  const f = [];
  if (m.lumaStd < 30) f.push('low contrast (lumaStd < 30)');
  if (m.colorEntropyBits < 3) f.push('very few distinct colors (entropy < 3 bits)');
  if (m.dominantColorShare > 0.6) f.push('one color fills >60% of the frame');
  if (m.edgeDensity < 0.02) f.push('little visible structure (edgeDensity < 0.02)');
  if (m.clippedHighlights > 0.05) f.push('blown highlights (>5% pure white)');
  if (m.clippedShadows > 0.15) f.push('crushed shadows (>15% pure black)');
  return f;
}
async function grayCopy(png, file) {  // value-structure check: does the scene still read without hue?
  const url = await tool.evaluate(async (b64) => {
    const im = new Image(); im.src = 'data:image/png;base64,' + b64; await im.decode();
    const c = document.createElement('canvas'); c.width = im.width; c.height = im.height;
    const ctx = c.getContext('2d', { willReadFrequently: true }); ctx.drawImage(im, 0, 0);
    const img = ctx.getImageData(0, 0, c.width, c.height); const d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      const L = 0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]; d[i] = d[i + 1] = d[i + 2] = L;
    }
    ctx.putImageData(img, 0, 0); return c.toDataURL('image/png');
  }, png.toString('base64'));
  writeFileSync(file, Buffer.from(url.split(',')[1], 'base64'));
  return file;
}
async function shoot(file, gray = false) {
  const png = await page.screenshot({ path: file });
  const metrics = await imageMetrics(png);
  const grayFile = gray && !args['no-gray'] ? await grayCopy(png, file.replace(/\.png$/, '_gray.png')) : undefined;
  return { file, ...(grayFile ? { grayFile } : {}), metrics, flags: visualFlags(metrics) };
}

try {
  await page.goto(String(args.url), { waitUntil: 'load', timeout: num('timeout', 20000) });
  report.hook = await page.evaluate(() => typeof window.__QA__ === 'object' && window.__QA__ !== null);
  if (report.hook) {
    await page.waitForFunction(async () => (await window.__QA__.ready) === true, null, { timeout: num('timeout', 20000) });
  } else {
    await page.waitForTimeout(num('wait-ms', 3000));
  }
  await frames(3);

  // Rough FPS over 2 s. Under SwiftShader this is CPU rendering capped near 60: compare builds, never budgets.
  report.fps = await page.evaluate(() => new Promise((res) => {
    let n = 0; const t0 = performance.now();
    const tick = () => { n++; if (performance.now() - t0 < 2000) requestAnimationFrame(tick); else res(Math.round(n / ((performance.now() - t0) / 1000))); };
    requestAnimationFrame(tick);
  }));

  const shotNames = report.hook ? await page.evaluate(() => Object.keys(window.__QA__.shots || {})) : [];
  if (shotNames.length) {
    for (const name of shotNames) {
      await page.evaluate(async (n) => { await window.__QA__.shots[n](); }, name);
      await frames(3);
      const s = await shoot(join(outDir, `shot_${name}.png`), true);
      report.shots.push({ name, ...s, stats: await hookCall('stats'), state: await hookCall('state') });
    }
  } else {
    for (let i = 0; i < num('shots', 3); i++) {
      if (i) await page.waitForTimeout(num('interval-ms', 1000));
      const s = await shoot(join(outDir, `shot_${String(i).padStart(2, '0')}.png`), true);
      report.shots.push({ name: `t${i}`, ...s, stats: await hookCall('stats'), state: await hookCall('state') });
    }
  }

  const seqN = num('sequence', 0);
  if (seqN > 0) {
    const stepMs = num('step-ms', 100);
    const hasAdvance = report.hook && await page.evaluate(() => typeof window.__QA__.advance === 'function');
    await page.mouse.click(vw / 2, vh / 2); // focus the canvas so keyboard input reaches the game
    if (args.hold) await page.keyboard.down(String(args.hold));
    if (args.press) await page.keyboard.press(String(args.press));
    for (let i = 0; i < seqN; i++) {
      if (i) {
        if (hasAdvance) await page.evaluate(async (ms) => { await window.__QA__.advance(ms); }, stepMs);
        else await page.waitForTimeout(stepMs);
        await frames(1);
      }
      const s = await shoot(join(outDir, `seq_${String(i).padStart(2, '0')}.png`));
      report.sequence.push({ index: i, ...s, deterministic: hasAdvance, state: await hookCall('state') });
    }
    if (args.hold) await page.keyboard.up(String(args.hold));
    // Contact sheet composed in the browser (no image libraries needed), frames numbered.
    const imgs = report.sequence.map((s) => readFileSync(s.file).toString('base64'));
    const cols = Math.min(4, imgs.length);
    const sheet = await tool.evaluate(async ({ imgs, cols, w, h }) => {
      const cw = Math.round(w / 2); const ch = Math.round(h / 2);
      const c = document.createElement('canvas'); c.width = cw * cols; c.height = ch * Math.ceil(imgs.length / cols);
      const ctx = c.getContext('2d');
      for (let i = 0; i < imgs.length; i++) {
        const im = new Image(); im.src = 'data:image/png;base64,' + imgs[i]; await im.decode();
        const x = (i % cols) * cw; const y = Math.floor(i / cols) * ch;
        ctx.drawImage(im, x, y, cw, ch);
        ctx.fillStyle = '#000a'; ctx.fillRect(x, y, 34, 18);
        ctx.fillStyle = '#fff'; ctx.font = '12px monospace'; ctx.fillText(String(i), x + 6, y + 13);
      }
      return c.toDataURL('image/png');
    }, { imgs, cols, w: vw, h: vh });
    const sheetFile = join(outDir, 'seq_sheet.png');
    writeFileSync(sheetFile, Buffer.from(sheet.split(',')[1], 'base64'));
    report.sequenceSheet = sheetFile;
  }
} catch (e) {
  report.fatal = String(e);
} finally {
  await browser.close();
}

report.consoleErrors = report.consoleErrors.filter((t) => !isNoise(t));
report.consoleWarnings = report.consoleWarnings.filter((t) => !isNoise(t));
report.failedRequests = report.failedRequests.filter((t) => !isNoise(t));
writeFileSync(join(outDir, 'capture_report.json'), JSON.stringify(report, null, 2));

const errorCount = report.consoleErrors.length + report.pageErrors.length + report.failedRequests.length + (report.fatal ? 1 : 0);
console.log(`capture: ${report.shots.length} shots, ${report.sequence.length} sequence frames -> ${outDir}`);
console.log(`hook: ${report.hook ? 'window.__QA__ found' : 'none (timed captures only)'} | fps~${report.fps} (${report.renderer}; not a perf measurement under swiftshader)`);
for (const s of report.shots) {
  const m = s.metrics;
  console.log(`  ${s.name}: lumaStd ${m.lumaStd} entropy ${m.colorEntropyBits} dominant ${m.dominantColorShare} edges ${m.edgeDensity}${s.flags.length ? '  FLAGS: ' + s.flags.join('; ') : ''}`);
}
const last = report.shots.at(-1)?.stats;
if (last) console.log(`stats: ${JSON.stringify(last)}`);
for (const t of [...report.pageErrors, ...report.consoleErrors].slice(0, 10)) console.log(`  ERROR ${t}`);
for (const t of report.failedRequests.slice(0, 10)) console.log(`  FAILED REQUEST ${t}`);
if (report.fatal) console.log(`  FATAL ${report.fatal}`);
console.log(`VERDICT: ${errorCount ? 'FAIL' : 'PASS'} (${errorCount} errors, ${report.consoleWarnings.length} warnings)`);
process.exit(errorCount && !args['allow-errors'] ? 1 : 0);
