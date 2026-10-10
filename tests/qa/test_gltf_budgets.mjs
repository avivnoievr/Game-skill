// CLI budget guards against unknown validator evidence; no Khronos dependency installation.
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, existsSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
const root = fileURLToPath(new URL('../../', import.meta.url));
const script = resolve(root, 'plugins/game-studio/skills/game-studio/scripts/web/check_gltf.mjs');
function check(info, args) {
  const folder = mkdtempSync(join(tmpdir(), 'gs-gltf-'));
  try {
    const module = join(folder, 'node_modules/gltf-validator');
    mkdirSync(module, { recursive: true });
    writeFileSync(join(module, 'package.json'), JSON.stringify({ main: 'index.cjs' }));
    writeFileSync(join(module, 'index.cjs'), `exports.validateBytes = async () => (${JSON.stringify({info,issues:{numErrors:0,numWarnings:0,messages:[]}})});`);
    writeFileSync(join(folder, 'model.glb'), 'controlled validator fixture');
    const result = spawnSync(process.execPath, [script, 'model.glb', ...args, '--json', 'report.json'], {
      cwd: folder, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'],
    });
    const report = join(folder, 'report.json');
    result.report = existsSync(report) ? JSON.parse(readFileSync(report, 'utf8')) : null;
    return result;
  } finally { rmSync(folder, { recursive: true, force: true }); }
}
test('unknown required geometry measurement cannot pass', () => {
  const result = check({}, ['--max-tris', '100']);
  assert.equal(result.status, 1, result.stderr);
  assert.equal(result.report?.verdict, 'FAIL', result.stderr);
  assert.ok(result.report.checks.some(c => /measurement is unavailable/.test(c.message)));
});
test('healthy measured counts meet declared limits', () => {
  const result = check({ totalTriangleCount: 12, materialCount: 1, resources: [] }, ['--max-tris', '12', '--max-materials', '1']);
  assert.equal(result.status, 0, result.stderr);
});
test('zero texture limit and absent image dimensions fail', () => {
  for (const image of [{width:16,height:16}, {}]) {
    const result = check({resources:[{pointer:'/images/0',image}]}, ['--max-texture', '0']);
    assert.equal(result.status, 1, result.stderr);
  }
});
test('invalid or missing limits fail', () => {
  for (const args of [['--max-tris'], ['--max-tris', 'NaN'], ['--max-tris', '-1']]) {
    const result = check({totalTriangleCount:12}, args);
    assert.equal(result.status, 1, result.stderr);
  }
});
