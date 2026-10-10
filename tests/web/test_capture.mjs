import assert from 'node:assert/strict';
import { test, before, after } from 'node:test';
import { createServer } from 'node:http';
import { mkdtempSync, writeFileSync, readFileSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawn } from 'node:child_process';

const capture = process.env.CAPTURE_SCRIPT || fileURLToPath(new URL('../../plugins/game-studio/skills/game-studio/scripts/web/capture.mjs', import.meta.url));
const html = `<!doctype html><body style="margin:0"><canvas width="320" height="200"></canvas><script>
const mode = new URLSearchParams(location.search).get('case');
const c = document.querySelector('canvas'), ctx = c.getContext('2d'); let t = 0;
function draw() { ctx.fillStyle = '#254266'; ctx.fillRect(0,0,320,200); ctx.fillStyle = '#edd26a'; ctx.fillRect(20 + t / 10,30,120,130); }
function stats() { return {drawCalls: mode === 'sequenceBudget' && t > 0 ? 9 : 2, triangles: 100, geometries: 3, textures: 2, programs: 1}; }
draw();
if (mode !== 'noHook') {
 window.__QA__ = {ready:true, stats, state:()=>({timeMs:t}), shots:{gameplay:async()=>draw()},
  advance:async(ms)=>{t+=ms;draw()}, reload:async()=>draw()};
 if (mode === 'missingStats') delete __QA__.stats;
 if (mode === 'throwsStats') __QA__.stats=()=>{throw new Error('stats fixture failed')};
 if (mode === 'throwsState') __QA__.state=async()=>{throw new Error('state fixture failed')};
 if (mode === 'asyncStats') __QA__.stats=async()=>stats();
 if (mode === 'unknownStats') __QA__.stats=()=>({...stats(),drawCalls:'unknown'});
 if (mode === 'unknownLeak') __QA__.stats=()=>({...stats(),geometries:undefined});
 if (mode === 'missingReload') delete __QA__.reload;
 if (mode === 'missingAdvance') delete __QA__.advance;
}
</script>`;
let server, base;
before(async () => {
  server = createServer((_, res) => { res.setHeader('content-type', 'text/html'); res.end(html); });
  await new Promise((resolve, reject) => { server.once('error', reject); server.listen(0, '127.0.0.1', resolve); });
  base = 'http://127.0.0.1:' + server.address().port;
});
after(async () => { await new Promise((resolve) => server.close(resolve)); });
async function run(mode, { budgets, flags = [], requireQa = true } = {}) {
  const dir = mkdtempSync(join(tmpdir(), 'gs-capture-'));
  try {
    const argv = [capture, '--url', base + '/?case=' + mode, '--out', dir, '--timeout', '1000', '--no-gray', '--wait-ms', '0', '--shots', '1', ...flags];
    if (requireQa) argv.push('--require-qa');
    if (budgets) { const p = join(dir, 'budgets.json'); writeFileSync(p, JSON.stringify({scene:budgets})); argv.push('--budgets', p); }
    const env = { ...process.env };
    if (!env.CHROMIUM_PATH && existsSync('/usr/bin/chromium')) env.CHROMIUM_PATH = '/usr/bin/chromium';
    const r = await new Promise((resolve, reject) => {
      const child = spawn(process.execPath, argv, { cwd: dir, env, stdio: ['ignore', 'pipe', 'pipe'] }); let stdout = '', stderr = '';
      child.stdout.on('data', (s) => { stdout += s; }); child.stderr.on('data', (s) => { stderr += s; });
      const timer = setTimeout(() => { child.kill(); reject(new Error('capture subprocess timed out')); }, 15000);
      child.on('error', (e) => { clearTimeout(timer); reject(e); });
      child.on('close', (code) => { clearTimeout(timer); resolve({code,stdout,stderr}); });
    });
    const reportPath = join(dir, 'capture_report.json');
    const report = existsSync(reportPath) ? JSON.parse(readFileSync(reportPath, 'utf8')) : null;
    return {...r,report};
  } finally { rmSync(dir, {recursive:true,force:true}); }
}
function failed(r, message) { assert.equal(r.code, 1, r.stdout + r.stderr); assert.match(r.stdout, message); }
const scene = {draw_calls:4,triangles_in_view:200,textures_live:4,shader_programs:2};

test('healthy async hooks support strict budgets, reloads and deterministic input', async () => {
  const r = await run('asyncStats', {budgets:scene,flags:['--reloads','2','--sequence','3','--step-ms','50','--hold','ArrowUp']});
  assert.equal(r.code,0,r.stdout+r.stderr);
  assert.equal(r.report.sequence[2].state.timeMs,100);
  assert.equal(r.report.sequence[2].deterministic,true);
  assert.equal(r.report.leak.after.geometries,3);
});
test('missing QA hook blocks gate mode', async () => { failed(await run('noHook'), /ready was not true/); });
test('missing stats cannot satisfy requested budgets', async () => { failed(await run('missingStats',{budgets:scene}), /stats.*missing|missing or invalid renderer counts/); });
test('thrown stats are failures rather than zero counts', async () => { failed(await run('throwsStats',{budgets:scene}), /stats fixture failed/); });
test('rejected state hook blocks evidence collection', async () => { failed(await run('throwsState'), /state fixture failed/); });
test('non-numeric renderer counts are unknown rather than zero', async () => { failed(await run('unknownStats',{budgets:scene}), /missing or invalid renderer counts: drawCalls/); });
test('zero budgets are enforced', async () => { failed(await run('healthy',{budgets:{draw_calls:0}}), /drawCalls 2 > budget 0/); });
test('invalid declared budgets fail', async () => { failed(await run('healthy',{budgets:{draw_calls:'4'}}), /invalid budget scene.draw_calls/); });
test('requested reload cannot silently skip missing implementation', async () => { failed(await run('missingReload',{flags:['--reloads','1']}), /requested leak test cannot run/); });
test('missing baseline memory count cannot prove a leak check passed', async () => { failed(await run('unknownLeak',{flags:['--reloads','1']}), /missing or invalid renderer counts: geometries/); });
test('gate sequences cannot fall back to wall-clock waits', async () => { failed(await run('missingAdvance',{flags:['--sequence','2']}), /deterministic sequence needs/); });
test('budgets cover action frames as well as static shots', async () => { failed(await run('sequenceBudget',{budgets:scene,flags:['--sequence','2']}), /drawCalls 9 > budget 4/); });
test('ordinary screenshots remain available without a QA hook', async () => {
  const r = await run('noHook', {requireQa:false});
  assert.equal(r.code,0,r.stdout+r.stderr);
  assert.equal(r.report.hook,false);
});
test('budget evidence cannot silently skip stats in ordinary screenshot mode', async () => {
  failed(await run('noHook', {requireQa:false,budgets:scene}), /missing or invalid renderer counts/);
});
