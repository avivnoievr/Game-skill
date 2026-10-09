#!/usr/bin/env node
// Capture evidence from a running web game (Three.js / R3F / Babylon / PlayCanvas): screenshots with
// objective image metrics and grayscale copies, console + page errors, failed requests, renderer stats
// checked against budgets, game state, a scene-reload leak test, and an optional frame sequence (with
// held/pressed keys) for motion review.
//
// Usage: node capture.mjs --url http://localhost:5173 --out qa/out/<milestone> [options]
//   --viewport 1280x720     page size (default 1280x720)
//   --timeout 30000         max ms to wait for window.__QA__.ready === true (default 30000)
//   --wait-ms 3000          settle time when the page has no __QA__ hook (default 3000)
//   --shots 3               screenshots to take when the page has no __QA__.shots (default 3)
//   --interval-ms 1000      gap between those screenshots (default 1000)
//   --sequence N            also capture N frames for motion review (+ seq_sheet.png)
//   --step-ms 100           time between sequence frames (uses __QA__.advance(ms) when present)
//   --hold KEY              hold a key during the sequence (Playwright key name, e.g. KeyW, ArrowLeft)
//   --press KEY             press a key once at the start of the sequence (e.g. Space)
//   --budgets FILE          design/budgets.json: fail when drawCalls / triangles / textures exceed scene budgets
//   --reloads N             leak test: call __QA__.reload() N times; fail if geometries/textures grow
//   --gpu                   use the machine's GPU instead of SwiftShader (faster; less deterministic)
//   --no-gray               skip the grayscale copy (<shot>_gray.png) written for every named shot
//   --allow-errors          exit 0 even when checks failed
// Requires `playwright` in the game project (npm i -D playwright; npx playwright install chromium).
// CHROMIUM_PATH selects a specific Chromium binary if Playwright's own browser is not installed.
//
// Dev-only hook the game can expose (all members optional except ready):
//   window.__QA__ = {
//     ready: false,                                  // set true (synchronously) after load + first frame
//     stats: () => ({ drawCalls, triangles, geometries, textures, programs }),  // e.g. renderer.info
//     state: () => ({ player: {x, y, z, hp}, ... }), // small JSON game state for invariants
//     shots: { gameplay: async () => {...}, ... },   // named camera/state presets, rendered on call
//     advance: async (ms) => {...},                  // step the fixed-timestep simulation, then render
//     reload: async () => {...},                     // unload + reload the main scene (leak test)
//   }
// Exit code 1 when: page/console errors, failed requests, a blank canvas, budgets exceeded, a leak,
// or a fatal error. Image-metric flags are evidence for the critic, not failures by themselves.
import { createHash } from 'node:crypto';
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
  console.error('usage: node capture.mjs --url URL --out DIR [--sequence N] [--hold KeyW] [--budgets design/budgets.json] [--reloads 5] [--gpu] ...');
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
  : ['--use-gl=angle', '--use-angle=swiftshader-webgl', '--enable-unsafe-swiftshader']; // documented software-WebGL switches
async function launch() {
  if (process.env.CHROMIUM_PATH) return chromium.launch({ args: launchArgs, executablePath: process.env.CHROMIUM_PATH });
  try {
    return await chromium.launch({ args: launchArgs });           // Playwright's own matching browser
  } catch (e) {
    const fallback = '/opt/pw-browsers/chromium';                  // preinstalled in some cloud containers
    if (/Executable doesn't exist/.test(String(e)) && existsSync(fallback)) {
      console.error(`note: Playwright's browser is not installed; using ${fallback}`);
      return chromium.launch({ args: launchArgs, executablePath: fallback });
    }
    throw e;
  }
}
const browser = await launch();
const page = await browser.newPage({ viewport: { width: vw, height: vh } });
const tool = await browser.newPage(); // blank page for image math, isolated from the game

const report = { url: args.url, viewport: [vw, vh], renderer: args.gpu ? 'gpu' : 'swiftshader', consoleErrors: [],
  consoleWarnings: [], pageErrors: [], failedRequests: [], checks: [], hook: false, fps: null, shots: [], sequence: [] };
const fail = (msg) => report.checks.push({ level: 'FAIL', msg });
const warn = (msg) => report.checks.push({ level: 'WARN', msg });
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
const hasHook = (fn) => page.evaluate((f) => typeof window.__QA__?.[f] === 'function', fn);

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
const isBlank = (m) => m.lumaStd < 3 && m.dominantColorShare > 0.97;
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
  const sha1 = createHash('sha1').update(png).digest('hex');
  const grayFile = gray && !args['no-gray'] ? await grayCopy(png, file.replace(/\.png$/, '_gray.png')) : undefined;
  if (isBlank(metrics)) fail(`blank canvas in ${file} (nothing rendered)`);
  return { file, sha1, ...(grayFile ? { grayFile } : {}), metrics, flags: visualFlags(metrics) };
}

try {
  await page.goto(String(args.url), { waitUntil: 'load', timeout: num('timeout', 30000) });
  report.hook = await page.evaluate(() => typeof window.__QA__ === 'object' && window.__QA__ !== null);
  if (report.hook) {
    // Synchronous predicate: Playwright does not await a Promise returned by the predicate.
    await page.waitForFunction(() => window.__QA__?.ready === true, null, { timeout: num('timeout', 30000) })
      .catch(() => { throw new Error(`window.__QA__.ready was not true within ${num('timeout', 30000)} ms`); });
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

  // Budgets: compare the largest renderer counts seen across shots with design/budgets.json → scene.
  if (args.budgets) {
    const scene = JSON.parse(readFileSync(String(args.budgets), 'utf8')).scene || {};
    const seen = (k) => Math.max(0, ...report.shots.map((s) => Number(s.stats?.[k]) || 0));
    if (!report.shots.some((s) => s.stats)) warn('budgets given but the page exposes no __QA__.stats()');
    else {
      if (scene.draw_calls && seen('drawCalls') > scene.draw_calls) fail(`draw calls ${seen('drawCalls')} > budget ${scene.draw_calls}`);
      if (scene.triangles_in_view && seen('triangles') > scene.triangles_in_view) fail(`triangles ${seen('triangles')} > budget ${scene.triangles_in_view}`);
      if (scene.textures_live && seen('textures') > scene.textures_live) fail(`textures ${seen('textures')} > budget ${scene.textures_live}`);
    }
  }

  // Leak test: geometries/textures must return to baseline after N reloads.
  const reloads = num('reloads', 0);
  if (reloads > 0) {
    if (!(await hasHook('reload')) || !(await hasHook('stats'))) warn('leak test skipped: __QA__.reload() or stats() missing');
    else {
      const before = await hookCall('stats');
      for (let i = 0; i < reloads; i++) { await page.evaluate(async () => { await window.__QA__.reload(); }); await frames(2); }
      const after = await hookCall('stats');
      report.leak = { reloads, before, after };
      for (const k of ['geometries', 'textures']) {
        if (Number(after?.[k]) > Number(before?.[k])) fail(`leak: ${k} ${before[k]} -> ${after[k]} after ${reloads} reloads`);
      }
    }
  }

  const seqN = num('sequence', 0);
  if (seqN > 0) {
    const stepMs = num('step-ms', 100);
    const hasAdvance = report.hook && await hasHook('advance');
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
    if (seqN > 1 && new Set(report.sequence.map((s) => s.sha1)).size === 1) {
      warn('all sequence frames are identical: nothing moved, or the capture is stale');
    }
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

const failedChecks = report.checks.filter((c) => c.level === 'FAIL');
const errorCount = report.consoleErrors.length + report.pageErrors.length + report.failedRequests.length
  + failedChecks.length + (report.fatal ? 1 : 0);
console.log(`capture: ${report.shots.length} shots, ${report.sequence.length} sequence frames -> ${outDir}`);
console.log(`hook: ${report.hook ? 'window.__QA__ found' : 'none (timed captures only)'} | fps~${report.fps} (${report.renderer}; not a perf measurement under swiftshader)`);
for (const s of report.shots) {
  const m = s.metrics;
  console.log(`  ${s.name}: lumaStd ${m.lumaStd} entropy ${m.colorEntropyBits} dominant ${m.dominantColorShare} edges ${m.edgeDensity}${s.flags.length ? '  FLAGS: ' + s.flags.join('; ') : ''}`);
}
const last = report.shots.at(-1)?.stats;
if (last) console.log(`stats: ${JSON.stringify(last)}`);
if (report.leak) console.log(`leak test: ${JSON.stringify(report.leak.before)} -> ${JSON.stringify(report.leak.after)}`);
for (const c of report.checks) console.log(`  ${c.level} ${c.msg}`);
for (const t of [...report.pageErrors, ...report.consoleErrors].slice(0, 10)) console.log(`  ERROR ${t}`);
for (const t of report.failedRequests.slice(0, 10)) console.log(`  FAILED REQUEST ${t}`);
if (report.fatal) console.log(`  FATAL ${report.fatal}`);
console.log(`VERDICT: ${errorCount ? 'FAIL' : 'PASS'} (${errorCount} failures, ${report.consoleWarnings.length + report.checks.length - failedChecks.length} warnings)`);
process.exit(errorCount && !args['allow-errors'] ? 1 : 0);
