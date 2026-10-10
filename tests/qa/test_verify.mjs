import assert from 'node:assert/strict';
import { test } from 'node:test';
import { mkdtempSync, mkdirSync, copyFileSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { spawnSync } from 'node:child_process';

const template = process.env.VERIFY_TEMPLATE || fileURLToPath(new URL('../../plugins/game-studio/skills/game-studio/templates/verify.sh', import.meta.url));
function verify(packageData, mode = '--quick') {
  const dir = mkdtempSync(join(tmpdir(), 'gs-verify-'));
  try {
    mkdirSync(join(dir, 'qa'));
    copyFileSync(template, join(dir, 'qa/verify.sh'));
    if (packageData !== null) writeFileSync(join(dir, 'package.json'), JSON.stringify(packageData));
    const result = spawnSync('bash', ['qa/verify.sh', mode], { cwd: dir, encoding: 'utf8', timeout: 10000, stdio: ['ignore', 'pipe', 'pipe'] });
    assert.ifError(result.error);
    return result;
  } finally { rmSync(dir, { recursive: true, force: true }); }
}
const checks = Object.fromEntries(['typecheck', 'lint', 'depcheck', 'test'].map((key) => [key, 'node -e "process.exit(0)"']));

test('an empty project cannot pass required checks', () => {
  const r = verify({});
  assert.equal(r.status, 1);
  assert.match(r.stdout, /BLOCKED/);
  assert.match(r.stdout, /VERIFY: FAIL/);
});
test('a key outside package scripts cannot satisfy a missing lint check', () => {
  const { lint, ...scripts } = checks;
  const r = verify({ scripts, metadata: { lint } });
  assert.equal(r.status, 1);
  assert.match(r.stdout, /define a terminating 'lint' check/);
});
test('all declared healthy checks pass', () => {
  const r = verify({ scripts: checks });
  assert.equal(r.status, 0, r.stdout + r.stderr);
  assert.match(r.stdout, /== typecheck/);
  assert.match(r.stdout, /== lint/);
  assert.match(r.stdout, /== layer rules/);
  assert.match(r.stdout, /== unit tests/);
  assert.match(r.stdout, /VERIFY: PASS/);
});
test('a failing declared check blocks completion', () => {
  const r = verify({ scripts: { ...checks, test: 'node -e "process.exit(7)"' } });
  assert.equal(r.status, 1);
  assert.match(r.stdout, /VERIFY: FAIL/);
});
test('full mode requires project state before launching a server', () => {
  const r = verify({ scripts: checks }, 'full');
  assert.equal(r.status, 1);
  assert.match(r.stdout, /missing required state file: design\/budgets.json/);
  assert.match(r.stdout, /missing required state file: design\/research.md/);
  assert.match(r.stdout, /missing required state file: design\/plan.md/);
  assert.match(r.stdout, /BLOCKED: resolve the static\/logic\/scaffold failures/);
});
