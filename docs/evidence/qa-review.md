# QA contract fixes — round2 snapshot

Implementation ownership: `plugins/game-studio/skills/game-studio/templates/verify.sh`, `scripts/web/capture.mjs`, `references/qa-protocol.md`, `references/engines/godot.md`, `references/engines/unity.md`, and new `tests/qa/test_verify.mjs` / `tests/web/test_capture.mjs`. No dependency installation or external service calls were needed.

## Changed behavior

- The web verification template requires actual package scripts for lint, layer rules and tests; typechecking requires a typecheck script or tsconfig plus local tsc. Missing checks report BLOCKED and exit non-zero. Full mode requires all project state files, a budgets file and local Vite, and passes --require-qa to capture. Missing tools are never downloaded by npx.
- Gate-mode capture requires ready, stats/state/advance methods and named shots. Hook promises are awaited; synchronous exceptions, rejected promises, invalid return objects and oversize snapshots produce failure evidence.
- Requested budgets require finite nonnegative measured numeric counts; unknown values are not coerced to zero. A limit of zero is checked. Named shots and sequence/action frames both count against declared limits, including shader programs.
- Requested scene reload checks cannot silently skip absent reload/stats implementations or unknown baseline counters. Resource counts must return to baseline. Deterministic sequences in gate mode require advance rather than falling back to wall-clock waits.
- Ordinary timed screenshots continue to work without a QA hook. Their requested budgets still require numeric evidence. Diagnostic --allow-errors prints FAIL when checks fail and cannot be cited as a gate pass.
- Engine references now call native screenshot snippets partial adapters, list the missing seed/step/input/state/reload work, and distinguish motion capture from validated deterministic simulation. The Godot movie example now passes --qa.
- QA protocol defines all-engine missing-evidence/N/A rules and a consistent prototype release policy; prototype skips critic gates while retaining required execution/feature/evidence checks. It explicitly says capture snapshots do not assert project-specific feature invariants and an eight-frame smoke does not meet a sixty-second soak requirement.

## Verification

Current implementation:

1. `node --test --test-isolation=none --test-reporter=spec tests/qa/test_verify.mjs`: **5 passed, 0 failed**, 4.46 s.
2. `node --test --test-isolation=none --test-reporter=spec tests/web/test_capture.mjs`: **14 passed, 0 failed**, 31.83 s. Used preinstalled Playwright and /usr/bin/chromium, with the execution tool's additional network allowance for the localhost fixture only.
3. `node --check scripts/web/capture.mjs` and `bash -n templates/verify.sh`: passed.

Baseline red proof using the unmodified old snapshot:

- Verification subset (empty project, decoy lint key, declared healthy checks): 3 assertions failed. The empty project returned VERIFY PASS; the healthy configured project omitted the declared typecheck entirely.
- Capture subset (throwing stats, zero draw-call budget, budgets without stats): **3 assertions failed** because each baseline run incorrectly printed VERDICT PASS and exited zero. Throwing stats were stored as an error object, zero limits were ignored, and missing stats downgraded to WARN.

Tests exercise subprocesses and an actual headless browser with controlled 2D canvas/QA fixtures. They validate the harness contract, not a real game's GPU performance, animation quality or feature correctness. No full real-game/plugin evaluation or native-engine execution was performed.

This sandbox disallows default stdin pipes and localhost listening. Test subprocesses use ignored stdin. The Node runner used --test-isolation=none to avoid its own worker stdin pipe, and the browser command requested the ordinary additional network allowance. In a normal environment, Node's standard --test invocation works; the isolation flag is a sandbox runner workaround, not a production requirement.

## Integration notes for the parent

- Carry --require-qa into any boot-smoke command presented as a gate.
- Root owns matching prototype acceptance/G7 wording in SKILL.md, orchestration, agents and assets.json.
- Root owns genre/category applicability in the scorecard.
- The existing programmatic model/render findings remain separately owned by the script reviewer.
