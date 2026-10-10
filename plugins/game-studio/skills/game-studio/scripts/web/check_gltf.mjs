#!/usr/bin/env node
// Validate a .glb/.gltf with the Khronos glTF-Validator and check it against budgets.
//
// Usage: node check_gltf.mjs MODEL.glb [--max-tris N] [--max-draw-calls N] [--max-materials N]
//                            [--max-texture PX] [--max-size-mb N] [--json report.json]
// Requires: npm i -D gltf-validator
// Exit codes: 0 = pass, 1 = validation errors or budget exceeded, 2 = usage/load error.
import { readFileSync, existsSync, writeFileSync, statSync } from 'node:fs';
import { dirname, resolve, basename } from 'node:path';
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

const argv = process.argv.slice(2);
const file = argv.find((a) => !a.startsWith('--') && !argv[argv.indexOf(a) - 1]?.startsWith('--'));
const opt = (k) => { const i = argv.indexOf(`--${k}`); return i >= 0 ? argv[i + 1] : undefined; };
if (!file || !existsSync(file)) {
  console.error('usage: node check_gltf.mjs MODEL.glb [--max-tris N] [--max-draw-calls N] [--max-materials N] [--max-texture PX] [--max-size-mb N] [--json out.json]');
  process.exit(2);
}

let validator;
try {
  const mod = await importFromProject('gltf-validator');
  validator = mod.default ?? mod;
} catch {
  console.error('error: gltf-validator is not installed here. Run: npm i -D gltf-validator');
  process.exit(2);
}

const path = resolve(file);
const report = await validator.validateBytes(new Uint8Array(readFileSync(path)), {
  uri: basename(path),
  maxIssues: 200,
  externalResourceFunction: (uri) => new Promise((ok, fail) => {
    const p = resolve(dirname(path), decodeURIComponent(uri));
    try { ok(new Uint8Array(readFileSync(p))); } catch (e) { fail(`missing external resource: ${uri}`); }
  }),
});

const info = report.info || {};
const issues = report.issues || {};
const checks = [];
const add = (level, check, message) => checks.push({ level, check, message });

if (issues.numErrors) add('FAIL', 'validator', `${issues.numErrors} errors`);
if (issues.numWarnings) add('WARN', 'validator', `${issues.numWarnings} warnings`);
for (const m of (issues.messages || []).filter((m) => m.severity <= 1).slice(0, 15)) {
  add(m.severity === 0 ? 'FAIL' : 'WARN', 'validator', `${m.code}: ${m.message} (${m.pointer || ''})`);
}

const limit = (k) => {
  if (!argv.includes(`--${k}`)) return undefined;
  const raw = opt(k);
  const value = Number(raw);
  if (raw === undefined || raw === '' || raw.startsWith('--') || !Number.isFinite(value) || value < 0) {
    add('FAIL', 'budget', `${k} requires a finite nonnegative limit`);
    return undefined;
  }
  return value;
};
const budget = (k, actual, label) => {
  const lim = limit(k);
  if (lim === undefined) return;
  if (typeof actual !== 'number' || !Number.isFinite(actual) || actual < 0) {
    add('FAIL', 'budget', `${label} measurement is unavailable; cannot verify budget ${lim}`);
    return;
  }
  add(actual <= lim ? 'PASS' : 'FAIL', 'budget', `${label} ${actual} / budget ${lim}`);
};
budget('max-tris', info.totalTriangleCount, 'triangles');
budget('max-draw-calls', info.drawCallCount, 'draw calls');
budget('max-materials', info.materialCount, 'materials');
const sizeMb = statSync(path).size / 1048576;
budget('max-size-mb', sizeMb, 'file size MB');

const images = (info.resources || []).filter((r) => r.image);
const maxTex = limit('max-texture');
for (const r of images) {
  const { width, height } = r.image;
  const pot = (v) => v > 0 && (v & (v - 1)) === 0;
  const measured = Number.isFinite(width) && width > 0 && Number.isFinite(height) && height > 0;
  if (maxTex !== undefined && !measured) add('FAIL', 'budget', `texture ${r.pointer} dimensions unavailable; cannot verify ${maxTex}px`);
  else if (maxTex !== undefined && Math.max(width, height) > maxTex) add('FAIL', 'budget', `texture ${r.pointer} ${width}x${height} exceeds ${maxTex}px`);
  if (!pot(width) || !pot(height)) add('WARN', 'texture', `texture ${r.pointer} ${width}x${height} is not power-of-two`);
}
if ((info.maxInfluences || 0) > 4) add('WARN', 'skinning', `up to ${info.maxInfluences} joint influences per vertex (engines commonly use 4)`);

const ext = info.extensionsUsed || [];
const compressed = ext.some((e) => ['EXT_meshopt_compression', 'KHR_draco_mesh_compression'].includes(e));
const ktx = ext.includes('KHR_texture_basisu');
if (sizeMb > 5 && !compressed) add('WARN', 'delivery', `${sizeMb.toFixed(1)} MB without mesh compression (consider meshopt via gltf-transform/gltfpack)`);
if (images.length && !ktx && sizeMb > 5) add('INFO', 'delivery', 'textures are not KTX2; GPU memory = width*height*4 bytes each (+33% mips)');

const fails = checks.filter((c) => c.level === 'FAIL').length;
const warns = checks.filter((c) => c.level === 'WARN').length;
const summary = {
  file: path, sizeMb: Number(sizeMb.toFixed(2)), triangles: info.totalTriangleCount, vertices: info.totalVertexCount,
  drawCalls: info.drawCallCount, materials: info.materialCount, animations: info.animationCount, skins: !!info.hasSkins,
  morphTargets: !!info.hasMorphTargets, maxUVs: info.maxUVs, maxInfluences: info.maxInfluences, extensions: ext,
  textures: images.map((r) => ({ pointer: r.pointer, mime: r.mimeType, size: [r.image.width, r.image.height] })),
};
console.log(`\n== check_gltf: ${basename(path)} ==`);
console.log(`triangles ${summary.triangles} | vertices ${summary.vertices} | draw calls ${summary.drawCalls} | materials ${summary.materials} | animations ${summary.animations} | ${summary.sizeMb} MB`);
if (ext.length) console.log(`extensions: ${ext.join(', ')}`);
for (const c of checks) console.log(`  ${c.level.padEnd(4)} ${c.check}: ${c.message}`);
const verdict = fails ? 'FAIL' : warns ? 'WARN' : 'PASS';
console.log(`VERDICT: ${verdict} (${fails} fail, ${warns} warn)`);
if (opt('json')) writeFileSync(opt('json'), JSON.stringify({ summary, checks, verdict, validator: issues }, null, 2));
process.exit(fails ? 1 : 0);
