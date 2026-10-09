# 04 — QA, Rigor & Clean Architecture (Research Agent 4)

Date: 2026-10-09. Scope: verification loops for agent-built 3D games, anti-laziness/rigor patterns, maintainable game architecture, and reusable QA/review skills.

**What was run and what was not.** I did not execute any browser, engine, or test tool. Every command and flag below comes from documentation or source code I read. None of it has been tested in this environment. The only execution was fetching and cloning (git, curl to raw.githubusercontent.com and to platform/code.claude.com, npm registry metadata).

**Access limits I hit.** These hosts were blocked by the proxy or by DNS: arxiv.org, aclanthology.org, iclr.cc, neurips.cc, openreview.net, huggingface.co, semanticscholar, threejs.org, docs.godotengine.org, docs.unity3d.com, playwright.dev, chromium.googlesource.com and gail.wharton.upenn.edu. I worked around this with GitHub mirrors: godot-docs, microsoft/playwright docs, chromium/chromium, and needle-mirror for the Unity packages. I checked academic papers only at abstract level, through search-engine summaries of their primary pages. That is marked [ABSTRACT-LEVEL].

---

## 1. Executive summary

1. **Self-grading fails, so separate grading from generation.** Anthropic's Mar 2026 harness post says agents asked to grade their own work "tend to respond by confidently praising the work—even when… obviously mediocre." The same post says "Out of the box, Claude is a poor QA agent… identify legitimate issues, then talk itself into deciding they weren't a big deal." A separate evaluator, tuned to be skeptical, is "far more tractable than making a generator critical of its own work." [harness-design]
2. **The evidence favours external signals over introspection.** Intrinsic self-correction without external feedback does not reliably improve reasoning and can make it worse (Huang et al., ICLR 2024). Self-correction does work when reliable external feedback exists (Kamoi et al., TACL 2024; CRITIC, ICLR 2024) [ABSTRACT-LEVEL]. For games, the external signals are renders, renderer metrics, console errors and deterministic tests.
3. **"Double-check your work" is the wrong lever on current models.** Anthropic says to remove generic re-check and verification instructions on Opus 5+, because they "cause over-verification" and add cost without quality. What works is grounding claims in tool results. The line "audit each claim against a tool result from this session" "nearly eliminated fabricated status reports". [prompting-opus-5, prompting-fable-5]
4. **Shouting backfires; stated standards with reasons work.** Anthropic's guidance is to dial back "CRITICAL: You MUST…" because newer models overtrigger on it, and to explain *why* a rule exists. Claude Code docs say to use "IMPORTANT" on one line only, since emphasising many lines makes none stand out. Threats and tips had no reliable benchmark effect in Wharton's 2025 test, though that test used non-Claude models. [prompting-best-practices, cc-best-practices, PSR3]
5. **Deterministic gates beat advisory text.** A Claude Code `Stop` hook (command or prompt type) can block "done" until a check passes. It has an 8-continuation cap and a `stop_hook_active` flag. `/goal` is a session-scoped prompt-based Stop hook whose evaluator reads only the transcript, so the evidence must be printed into the conversation. [hooks, goal]
6. **Headless WebGL needs explicit opt-in.** Chromium no longer falls back to SwiftShader automatically. Its documented switches are `--use-gl=angle --use-angle=swiftshader-webgl --enable-unsafe-swiftshader`. Under software rendering, FPS numbers are meaningless, so CI should gate on hardware-independent counts (draw calls, triangles, textures, geometries, programs, errors). Frame time should be measured on a real GPU. [chromium swiftshader.md]
7. **Determinism is required for screenshot QA.** `toHaveScreenshot` waits until two consecutive screenshots match, which never happens with a free-running render loop. three.js's own CI handles this by injecting a deterministic `Math.random`, frozen clocks and controlled `requestAnimationFrame`, then diffing at a 0.1 per-pixel threshold with at most 0.1% of pixels allowed to differ. Copy that approach. [three.js test/e2e, Playwright docs]
8. **Godot `--headless` cannot render.** The RenderingServer docs say headless mode "disables all rendering". Godot screenshots need a real or virtual display and `await RenderingServer.frame_post_draw`. Movie Maker (`--write-movie out.png --fixed-fps N --quit-after F`) gives deterministic, non-real-time frame sequences. [godot-docs]
9. **Vision critique is useful only under strict conditions.** Multimodal judges match humans best on *pairwise* comparison and diverge on absolute scoring (MLLM-as-a-Judge, ICML 2024). Multimodal models struggle to detect game glitches (GlitchBench, CVPR 2024). Use fixed camera shots, side-by-side comparison with references, binary rubric questions, evidence before score, and programmatic invariants for physics and clipping bugs. [ABSTRACT-LEVEL]
10. **Best reusable rigor source: obra/superpowers v6.4.2 (MIT).** It provides verification-before-completion (an "Iron Law" plus a gate function and a rationalization table) and a task reviewer that treats the implementer's report as unverified claims. It also has an evidence-based note on wording: prohibitions *backfire* on output-shape problems and work for discipline problems.
11. **Architecture that stays tidy.** Keep a pure simulation core with no renderer imports, tested in Node with a fixed timestep. A thin render/view layer syncs from the core. Add an asset manifest with explicit `dispose()`, input mapped to actions, and a config single source of truth. Enforce it with machines: strict TypeScript, ESLint `max-lines`, dependency-cruiser layer rules, knip for dead code, size-limit. Keep CLAUDE.md under 200 lines and push the rest into path-scoped `.claude/rules/`.
12. **Negative result.** I found no existing Claude Code skill that runs a WebGL game headlessly, gates on renderer budgets, and runs an independent visual review end to end. The closest are kndoshn/threejs-skill-plugin (manual checklist plus static heuristics), anthropics webapp-testing (generic Playwright; it uses `networkidle`, which Playwright marks DISCOURAGED) and terma's godot-interactive (an MCP bridge). We have to write this part ourselves.

---

## 2. Catalog

| Name | URL | Type | Version / date | License | Verdict | What to borrow |
|---|---|---|---|---|---|---|
| obra/superpowers | github.com/obra/superpowers | skill set / plugin | v6.4.2, commit 2026-09-25 | MIT | 5 | verification-before-completion gate; systematic-debugging (3-failed-fixes → question the architecture); task-reviewer-prompt ("Do Not Trust the Report", "Declined to judge" list, severity calibration); writing-skills "Match the Form to the Failure" plus micro-testing of wording; receiving-code-review (no performative agreement) |
| Anthropic prompting best practices + per-model pages (Opus 5.5, Opus 5, Fable 5) | platform.claude.com/docs/en/build-with-claude/prompt-engineering/… | doc | current 2026 | Anthropic docs | 5 | explain the why; dial back aggressive language; remove generic re-check instructions; ground progress claims; ask reviewers to report everything and filter in a separate pass; anti-test-hardcoding prompt; name specific patterns to avoid |
| Claude Code docs: best-practices, hooks, /goal, sub-agents, memory | code.claude.com/docs/en/… | doc | current | Anthropic docs | 5 | Stop hook gates; /goal conditions; adversarial review subagent; subagent frontmatter (`tools`, `disallowedTools`, `model`, `effort`, `isolation`, `omitClaudeMd`, `maxTurns`); CLAUDE.md under 200 lines; `.claude/rules/` with `paths:` |
| Anthropic Eng: "Harness design for long-running application development" | anthropic.com/engineering/harness-design-long-running-apps | article | 2026-03-24 | © Anthropic | 5 | planner/generator/evaluator; graded criteria with hard thresholds; sprint contracts; few-shot calibration of the evaluator; the evaluator uses Playwright on the live app; cost was solo $9/20 min vs harness $200/6 h |
| Anthropic Eng: "Effective harnesses for long-running agents" | anthropic.com/engineering/effective-harnesses-for-long-running-agents | article | 2025-11-26 | © Anthropic | 4 | feature list in JSON with `passes:false`; init.sh; progress file + git; one feature per session; mandatory end-to-end smoke test at session start |
| anthropics/claude-code plugins: code-review, pr-review-toolkit, ralph-wiggum | github.com/anthropics/claude-code/tree/main/plugins | plugin | cloned 2026-10-09 | "© Anthropic PBC. All rights reserved" — **do not copy text** | 4 | parallel finders → a separate validator subagent per finding → filter; confidence ≥80 threshold; silent-failure-hunter checklist |
| anthropics/skills webapp-testing | github.com/anthropics/skills | skill | 2026-10-09 | Apache-2.0 | 3 | `with_server.py` lifecycle pattern; console capture. Thin and generic; relies on `networkidle` |
| three.js e2e harness (`test/e2e/*.js`) | github.com/mrdoob/three.js (r186) | code | 0.186.0, 2026-10-09 | MIT | 5 | deterministic-injection.js (seeded Math.random, frozen clock, gated rAF); pixel threshold 0.1, max 0.1% differing pixels; 3 progressive retries; exception list |
| Playwright docs (snapshots, clock, params) | github.com/microsoft/playwright/tree/main/docs/src | doc | @playwright/test 1.64.0 (2026-10-07) | Apache-2.0 | 5 | `toHaveScreenshot` semantics; `page.clock` overrides rAF and performance; `networkidle` DISCOURAGED |
| Chromium `docs/gpu/swiftshader.md` | github.com/chromium/chromium (mirror) | doc | main | BSD | 5 | exact SwiftShader flags; the automatic fallback is deprecated |
| pixelmatch | github.com/mapbox/pixelmatch | lib | 8.0.0 (2026-10-06) | ISC | 4 | `threshold` (default 0.1), `includeAA`, `ignoreMask`, `windowSize` |
| stats-gl | github.com/RenaudRohlinger/stats-gl | lib | 4.2.3 (2026-07-10) | MIT | 4 | FPS/CPU/GPU timing for WebGL and WebGPU; ships an llms.txt |
| r3f-perf | github.com/utsuboco/r3f-perf | lib | 7.2.3, **last published 2024-11-08** | MIT | 3 | in-canvas perf HUD; peer `@react-three/fiber >=8`. Possibly stale |
| Spector.js | github.com/BabylonJS/Spector.js | tool | 0.9.33 (2026-09-14) | MIT | 3 | WebGL frame capture for debugging (README not studied in depth) |
| @react-three/test-renderer | pmndrs/react-three-fiber packages/test-renderer | lib | 9.1.1 | MIT | 3 | scene-graph assertions in Node without WebGL |
| R3F docs: pitfalls, scaling-performance | pmndrs/react-three-fiber docs/advanced | doc | master | MIT | 4 | no setState in useFrame; reuse objects; useLoader caching; `frameloop="demand"` + `invalidate` |
| Godot docs (command line, Movie Maker, Performance, RenderingServer, Viewport, best practices, static typing) | github.com/godotengine/godot-docs | doc | master | CC BY 3.0 | 5 | headless limits, Movie Maker, monitors, scene organization, autoload criteria |
| GUT | github.com/bitwes/Gut | test framework | 9.x for Godot 4 (9.7.1 → 4.7) | MIT | 4 | CLI `gut_cmdln.gd`, `-gexit`, JUnit XML |
| gdUnit4 | github.com/godot-gdunit-labs/gdUnit4 | test framework | v6.2.2 (Godot 4.5–4.8dev) | MIT | 4 | scene runner (simulated input), orphan-node detection, flaky retry, CLI, JUnit/HTML, GitHub Action |
| Unity Test Framework / Graphics Test Framework / Performance Testing (docs via needle-mirror) | github.com/needle-mirror/com.unity.test-framework etc. | doc | master | Unity package license [UNVERIFIED] | 3 | `-runTests -batchmode -testPlatform EditMode/PlayMode -testResults`; reference-image graphics tests; profiler-marker perf tests |
| bfollington/terma (code-review, godot-interactive) | github.com/bfollington/terma | skills | 2026-08-30 | **CC-BY-SA-4.0** (share-alike: do not paste text) | 4 | review = "what will this cost the next person"; "Four things that silently lie to you" (stale screenshots and similar) |
| Donchitos/Claude-Code-Game-Studios | github.com/Donchitos/Claude-Code-Game-Studios | subagent set | 2026-10-08 | MIT | 3 | story type → required evidence table; "watch the regression test fail"; gameplay-code rules; path-scoped rules. Heavy: user approval on every file write, 48 agents |
| kndoshn/threejs-skill-plugin | github.com/kndoshn/threejs-skill-plugin | skill | v1.0.0, 2026-01-08 | MIT | 3 | quality-gates.md checklist; `three-doctor.mjs` static heuristics (uncapped DPR, two render loops, mixed color-management APIs, EffectComposer without OutputPass). No automated rendering checks |
| forrestchang/andrej-karpathy-skills | github.com/forrestchang/andrej-karpathy-skills | CLAUDE.md | 2026-04-20 | MIT | 4 | Simplicity First, Surgical Changes, Goal-Driven Execution ("step → verify: check") |
| pmndrs/koota (+ its `skills/koota`) | github.com/pmndrs/koota | ECS lib + skill | 0.6.6 | ISC | 4 | `core/` (pure TS: traits/systems/actions/world) vs `features/` view split |
| Gaffer on Games "Fix Your Timestep!" | gafferongames.com/post/fix_your_timestep/ | article | 2004 (old but canonical) | © author | 5 | accumulator loop, `frameTime` clamp at 0.25 s, interpolation `alpha = accumulator/dt` |
| Game Programming Patterns (game-loop, event-queue, object-pool, state) | github.com/munificent/game-programming-patterns | book source | — | [UNVERIFIED] | 4 | event queues are globals; world state changes before an event is processed; feedback loops |
| brunosimon/my-room-in-3d ("Experience" structure) | github.com/brunosimon/my-room-in-3d | example | 2021 | UNLICENSED | 2 | asset manifest grouping idea only. Stale: singleton, variable delta |
| Tooling docs: ESLint max-lines, TS strict flags, knip, dependency-cruiser, size-limit, ADR templates | eslint/eslint, microsoft/TypeScript-Website, webpro-nl/knip, sverweij/dependency-cruiser, ai/size-limit, joelparkerhenderson/architecture-decision-record | docs | eslint 10.12, knip 6.41, depcruise 18.5, size-limit 14.2 | MIT/ISC | 4 | anti-rot gates (see §3.4) |
| Papers (see §8) | — | research | 2023–2024 | — | — | evidence base for §3.2 |

---

## 3. Distilled guidance

### 3.1 QA protocol: gates per phase

All gates are invoked from a single `npm run verify` (web) or `qa/verify.sh` (Godot/Unity). Exit code is 0 or non-zero, and the script writes `qa/out/report.json`. The agent may claim a gate passed only by quoting that output. [superpowers verification-before-completion; cc-best-practices "show evidence"]

| Gate | When | Pass condition (blocking) | Tooling |
|---|---|---|---|
| G0 Scaffold | before the first feature | `init.sh` boots the dev server; a QA mode exists (`?qa=1&seed=N`, or Godot `-- --qa`); verify script exists and runs | [effective-harnesses] |
| G1 Static | every change | typecheck 0 errors; lint 0 errors (including max-lines); dependency rules 0 violations; knip 0 unused files/exports; three-doctor-style heuristics clean | tsc, ESLint, dependency-cruiser, knip |
| G2 Logic | every change to simulation code | unit tests green; each new bug-fix test was **seen failing** before the fix | vitest / GUT / gdUnit4 / Unity EditMode [superpowers TDD; CCGS test-standards] |
| G3 Boot smoke | every change | 0 `pageerror`, 0 console errors, 0 failed requests or HTTP ≥400; WebGL context created; `__GAME__.ready` within 30 s; canvas not blank (luminance std-dev > ε); renderer counts within budget | Playwright + SwiftShader flags |
| G4 Scripted playthrough | each feature | input script runs N simulated seconds (e.g. 60 s at a fixed step); invariants hold: player displaced > X, no NaN transforms, never below the floor, objective reachable; `renderer.info.memory` stable after 5 scene reload cycles | game `__GAME__` QA API + Playwright |
| G5 Visual | each visual milestone | the shot list renders; regression diff on frozen shots passes; an independent art reviewer passes rubric thresholds against references | Playwright screenshots + pixelmatch + reviewer subagent |
| G6 Real-GPU perf | milestone (needs a human machine) | p95 frame time ≤ budget on the target device class in a headed browser | stats-gl / in-page frame timer |
| G7 Independent review | before "done" | reviewer subagent verdict PASS on every criterion's hard threshold; a validation pass confirmed each reported finding | §3.3 |

Budgets (placeholders: **[OPINION]**, tune per project and with Agent 2's asset budgets): draw calls ≤ 200–300, triangles ≤ 1–2 M, textures ≤ 64 live, shader programs ≤ 40, DPR capped at 2, bundle gzip budget enforced by size-limit, 0 console errors. The DPR cap of 2 matches Bruno Simon's `Math.min(Math.max(devicePixelRatio,1),2)` and kndoshn's "commonly 1 to 2".

### 3.2 Web (Three.js / R3F) verification: approach and key code

**Make the game drivable (the most important design decision).** In QA mode, do not start the rAF loop. Expose a test API so the harness steps the fixed-timestep simulation itself. This mirrors how three.js CI controls rAF and clocks.

```ts
// src/debug/qaApi.ts  (bundled only when import.meta.env.DEV or ?qa=1) — sketch, untested
export function installQaApi(game: Game) {
  (window as any).__GAME__ = {
    ready: false,                       // set true after assets loaded + first render
    frame: 0,
    advance(frames: number) {           // N fixed steps (1/60 s), then one render
      for (let i = 0; i < frames; i++) game.fixedUpdate(1 / 60);
      game.render(); this.frame += frames;
    },
    setShot(name: string) { game.camera.applyShot(SHOTS[name]); },   // fixed camera rig
    input(action: string, down: boolean) { game.input.inject(action, down); },
    metrics() {
      const i = game.renderer.info;   // read after render; autoReset resets counts per render() call
      return { calls: i.render.calls, triangles: i.render.triangles,
               geometries: i.memory.geometries, textures: i.memory.textures,
               programs: i.programs?.length ?? 0, frame: this.frame };
    },
    state() { return game.sim.snapshot(); }   // for invariant assertions
  };
}
```

`WebGLInfo` has `autoReset: true` and `reset()` (read in source). If the frame uses an EffectComposer or several render calls, set `renderer.info.autoReset = false` and call `reset()` once per frame, so the counts cover the whole frame. That last step is my inference.

**Harness** (`qa/capture.ts`; flags verified in Chromium docs, the script itself untested):

```ts
const browser = await chromium.launch({ args: [
  '--use-gl=angle', '--use-angle=swiftshader-webgl', '--enable-unsafe-swiftshader'] });
const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1 });
const errors: string[] = [];
page.on('pageerror', e => errors.push('pageerror: ' + e.message));
page.on('console', m => m.type() === 'error' && errors.push('console: ' + m.text()));
page.on('requestfailed', r => errors.push('requestfailed: ' + r.url()));
page.on('response', r => r.status() >= 400 && errors.push(`http ${r.status()} ${r.url()}`));
await page.goto('http://localhost:5173/?qa=1&seed=1234');          // NOT waitUntil:'networkidle'
await page.waitForFunction(() => (window as any).__GAME__?.ready === true, null, { timeout: 30000 });
for (const s of SHOTS) {
  await page.evaluate(([n, f]) => { const g = (window as any).__GAME__; g.setShot(n); g.advance(f); }, [s.name, s.frames]);
  await page.screenshot({ path: `qa/out/${s.name}.png` });
}
const metrics = await page.evaluate(() => (window as any).__GAME__.metrics());
// write qa/out/report.json {errors, metrics, budgets, pass}; process.exit(pass ? 0 : 1)
```

- **Chromium flags** (from the Chromium doc). As a GL driver: `--use-gl=angle --use-angle=swiftshader`. As the unsafe WebGL fallback: `--use-gl=angle --use-angle=swiftshader-webgl --enable-unsafe-swiftshader`. The doc says the automatic fallback is deprecated, "WebGL context creation will soon fail instead", and that `--enable-unsafe-swiftshader` removes the console warning. If you capture console errors, that warning would otherwise fail G3.
- **Alternative: Playwright `page.clock`.** `install()` overrides `requestAnimationFrame`, `performance`, timers and `Date`, and `runFor(ms)` advances them. It must be installed before any page clock use. Its interaction with `waitForFunction` polling and with three.js `setAnimationLoop` is **[UNVERIFIED]**. Prefer the explicit `advance()` API.
- **Don't use `networkidle`.** Playwright docs label it "**DISCOURAGED** … rely on web assertions to assess readiness instead". Use an app-owned `ready` flag.
- **`toHaveScreenshot` caveat.** It "will wait until two consecutive page screenshots yield the same result", so the canvas must be frozen (QA mode not advancing). `animations:'disabled'` affects only CSS and Web Animations, not the canvas. Baselines must be generated "in the same environment" (OS, browser and headless mode all change rendering). Default `threshold` 0.2; pixelmatch default 0.1. three.js CI uses 0.1 per pixel, at most 0.1% differing pixels, at 800×500 (400×250 × viewScale 2), with 3 progressive retries.
- **Blank-canvas detection.** Compute the luminance std-dev of each screenshot and fail if it is below ε, or if it equals the clear colour. Also hash consecutive shots: identical hashes across a change that should be visible means nothing re-rendered (terma's lie #2, generalised).
- **`preserveDrawingBuffer: true` in QA mode only.** It is needed if you read the canvas with `toDataURL()` or `readPixels` after the frame. Whether `page.screenshot()` captures correctly without it is [UNVERIFIED] (search-sourced only).
- **Logic tests without WebGL.** Put the simulation in `src/core/` with no `three` imports and test it with vitest using a fixed `dt` and a seeded RNG. For R3F scene-graph assertions, use `@react-three/test-renderer` (Node, no WebGL).
- **Performance.** SwiftShader is CPU rendering, so its FPS says nothing about real performance. Gate CI on counts. Measure frame time (stats-gl `trackGPU`, or an in-page p95 of rAF deltas) only in a headed run on a real GPU, and report it as "measured on <device>".
- **Memory leak check.** Load a scene, unload it, load it again, five times, then assert that `info.memory.geometries` and `textures` return to baseline. three.js manual: removing a mesh does **not** dispose its geometry or material; textures, render targets and skeletons each need their own `dispose()`; `ImageBitmap` needs `.close()`.

**Godot 4** (from godot-docs; CI recipe [UNVERIFIED]):
- **Logic tests** can run headless, since no rendering is needed. GUT: `godot -d -s --path "$PWD" addons/gut/gut_cmdln.gd -gdir=res://test -gexit -gjunit_xml_file=res://qa/out/junit.xml` (add `--headless` for CI). gdUnit4 ships a CLI tool, JUnit/HTML output and a GitHub Action. Its scene runner simulates mouse, keyboard and actions, and it detects orphan nodes.
- **Rendering.** `--headless` = `--display-driver headless --audio-driver Dummy`. RenderingServer docs: it "disables all rendering … Most functions … return dummy values". For screenshots, run windowed. In CI, xvfb-run plus a Mesa software GL/Vulkan driver is the likely route [UNVERIFIED]. Viewport doc: capture is "black or outdated if used too early … await RenderingServer.frame_post_draw" first, then `get_viewport().get_texture().get_image().save_png(path)`.
- **Movie Maker**: `godot --path . --write-movie qa/out/frame.png --fixed-fps 30 --resolution 1280x720 --quit-after 300` writes a PNG sequence plus WAV. It is non-real-time, has no dropped frames, and forces `--fixed-fps`. Its doc warns it is "not designed for capturing real-time footage during gameplay". A third-party source reports that `--write-movie` under `--headless` crashes [UNVERIFIED]. Also available: `--fixed-fps <fps>` (disables real-time sync, which is good for determinism), `--time-scale`, `--print-fps`, `--benchmark-file <path>` (JSON), `--gpu-profile`, `--debug-collisions`.
- **Metrics**: `Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)` (excludes culled objects), `RENDER_TOTAL_PRIMITIVES_IN_FRAME`, `RENDER_TOTAL_OBJECTS_IN_FRAME`, `RENDER_VIDEO_MEM_USED`, `RENDER_TEXTURE_MEM_USED`, `OBJECT_ORPHAN_NODE_COUNT`, `TIME_PROCESS`, `TIME_PHYSICS_PROCESS`, `PIPELINE_COMPILATIONS_*`. Write them to JSON from a QA autoload that is active only with a user arg (`OS.get_cmdline_user_args()` [UNVERIFIED this session]).
- **When driving a live game through an MCP bridge** (terma godot-interactive), watch for four failures that look like success:
  1. The screenshot on disk is stale unless a capture is forced.
  2. An occluded window renders nothing, so successive hashes are identical.
  3. Async transitions return a mid-transition frame, so wait for it to settle.
  4. After a restart, the old process's last frame is still on disk.

  Also, `success:true` only means the call was dispatched; check stderr.

**Unity** (Test Framework docs via mirror; editor CLI docs were blocked):
- Tests: `Unity -runTests -batchmode -projectPath <P> -testResults <file.xml> -testPlatform EditMode|PlayMode` (NUnit XML). Filters: `-testFilter`, `-testCategory`, `-assemblyNames`; `-randomOrderSeed`.
- The Graphics Test Framework compares a render against reference images across platforms and graphics APIs. The Performance Testing package measures profiler markers and is a core package from 6000.6.
- Screenshot via `-executeMethod` plus `ScreenCapture`/RenderTexture, and the claim that `-nographics` disables rendering: both [UNVERIFIED].

**Vision critique protocol** (the art-review part of G5):
1. **Fixed shot list.** Six to eight named camera rigs (hero close-up, gameplay view, wide establishing shot, darkest area, action frame, HUD) with a fixed seed and frame count. Rendered identically every time, so iterations are comparable.
2. **Side by side, pairwise.** Compare current vs reference and current vs previous iteration. Swap positions and require a consistent verdict, because position bias is documented (Zheng; Wang). Pairwise judgment aligns with humans better than absolute scores (MLLM-as-a-Judge).
3. **Rubric of binary or anchored questions**, written down before rendering. For example: "Is the silhouette of the player readable against the background at 25% scale? Y/N + crop". Avoid "rate beauty 1–10". Harness post: "'Is this design beautiful?' is hard to answer consistently, but 'does this follow our principles…?' gives Claude something concrete." Its criteria were design quality, originality, craft and functionality, with design and originality weighted higher.
4. **Evidence before score.** Name the region or crop, then give the verdict (Wang et al., MEC). Give the reviewer crop/zoom ability. Opus 5.5 doc: higher resolution and crop or image tools add accuracy on dense inputs.
5. **Image limits.** Opus 5.5 is in the high-resolution tier (long edge 2576 px, 4784 visual tokens). More than 20 images in one request switches to a stricter per-image limit (keep ≤2000 px). Put images before text.
6. **Calibrate** with few-shot examples that include score breakdowns (harness post). Wording steers output: "museum quality" pushed designs toward convergence.
7. **Don't rely on vision for glitches** (clipping, z-fighting, physics). GlitchBench shows multimodal models are weak at this, and the Claude vision docs list spatial reasoning and counting as approximate. Assert those programmatically instead (raycasts, bounding-box overlap, NaN checks).

### 3.3 Reviewer-agent design (genuinely independent)

`agents/qa-reviewer.md`:
- **Frontmatter:** `tools: Read, Grep, Glob, Bash`; `disallowedTools: Edit, Write`; `model: opus`; `effort: high`.
- **Plugin caveat:** plugin subagents ignore `permissionMode`, `mcpServers` and `hooks`.
- **Inputs (files only, never the implementer's session history):**
  - the spec or sprint contract
  - `qa/out/report.json`
  - the shot PNGs and reference images
  - the git range
  - the implementer's report, labelled *unverified claims*
- **Independence:** the reviewer **re-runs `npm run verify` itself** to get fresh evidence. Deterministic and cheap, this defeats stale or fabricated evidence. superpowers tells reviewers not to re-run suites, but that advice is about cost on large test suites. Here the evidence is the product, so re-running is right.
- **Procedure** (from superpowers task-reviewer, harness post, code-review plugin):
  1. Per contract criterion: PASS or FAIL with evidence (file:line, metric, or crop).
  2. Hard thresholds: any criterion below threshold means the sprint fails.
  3. Report *every* finding with severity. Don't pre-filter: Opus 5 doc says "only report high-severity" makes it under-report.
  4. Then a separate validation pass, one cheap subagent per finding, confirms each finding is real (code-review plugin step 5).
  5. Write a "Declined to judge" list so nothing is silently dropped.
  6. A stated rationale never downgrades severity ("Do Not Trust the Report").
- **Anti-leniency wording.** Reason, not threat: "The previous reviewer found real defects and then talked itself into approving. A finding you identified stays a finding; the implementer, not you, argues for exceptions."
- **Anti-over-engineering.** Claude Code docs: "A reviewer prompted to find gaps will usually report some, even when the work is sound." Classify findings as *blocking* (affects a contract criterion or correctness) or *optional*. Only blocking findings re-open the task.
- **Loop limits:**
  - at most 3 fix rounds per task, then escalate (superpowers uses 5 rounds, with a fresh implementer and a stronger model from round 4);
  - Opus 5.5 doc: stop after 2–3 automatic continuations;
  - Stop hook cap is 8 by default.
- **Test the reviewer itself.** Before trusting it, give it a known-bad fixture: a broken build, a blank canvas, an over-budget scene. "A gate you have not watched fail is not a gate" (CCGS).
- **Cost.** The evaluator "is worth the cost when the task sits beyond what the current model does reliably solo" (harness post). Use it per milestone, not per keystroke.
- **Deterministic backstop.** A `Stop` command hook runs `qa/verify.sh --quick`. If it fails, it returns `{"decision":"block","reason":"verify failed: <summary>"}`. Check `stop_hook_active` to avoid infinite blocking.

### 3.4 Rigor rules: which phrasing works (with evidence)

| Use | Instead of | Evidence |
|---|---|---|
| Standard + reason: "Every 'done' claim must quote the verify output from this session, because the developer has been burned by plausible-but-broken builds." | "YOU MUST ALWAYS VERIFY!!!" | explain the why [prompting-best-practices]; dial back CRITICAL/MUST, since newer models overtrigger [same]; "IMPORTANT" on one line only [cc-best-practices] |
| "Before reporting progress, audit each claim against a tool result from this session; if not verified, say so." | "Double-check your work" / "re-verify before responding" | the first "nearly eliminated fabricated status reports" [prompting-fable-5]; generic re-check instructions add cost without quality on Opus 5 [prompting-opus-5] |
| External check + fresh evaluator | "Critique your own output" | self-praise [harness-design]; intrinsic self-correction unreliable [Huang; Kamoi] |
| Report template with REQUIRED evidence slots (command, exit code, metric values, screenshot paths) | prose reminders near the template | structural slot beats prose reminder [superpowers writing-skills] |
| For skipped steps under pressure: bright-line rule + rationalization table + red-flag phrases ("should work", "looks good", "Done!") | soft "consider…" | discipline failures [superpowers writing-skills, verification-before-completion] |
| For wrong-shaped output: positive recipe ("the report is: verdict, evidence table, open issues") | prohibition lists ("don't narrate…") | prohibitions measurably backfired in head-to-head wording tests and trended worse than no guidance [superpowers writing-skills, author's own tests] |
| Name the concrete patterns to avoid | "avoid a generic AI look" | the general instruction "mostly swaps one default for another" [prompting-opus-5-5] |
| "Implement the general logic; if a test seems wrong, tell me rather than working around it" | — | anti-hardcoding prompt [prompting-best-practices]; JSON test lists plus "unacceptable to remove or edit tests" [effective-harnesses] |
| Threats, tips, insults | — | no reliable effect on GPQA/MMLU-Pro across 5 non-Claude models (PSR3, 2025) [ABSTRACT-LEVEL]; persuasion raised GPT-4o-mini compliance with objectionable requests 33%→72% (Meincke 2025). That is not evidence that shouting improves code quality |
| No performative agreement ("You're absolutely right!"); restate the requirement or just fix it | — | [superpowers receiving-code-review]; sycophancy is rewarded by human preference data [Sharma et al.] |
| Debugging: no fix without root cause; after 3 failed fixes, question the architecture | trying fix #4 | [superpowers systematic-debugging] |

**How to get the "scolding" effect the user wants, in a form that works.**
1. A short preamble that states the bar and why: "the last builds looked AI-generated and the models were poor; mediocre is a failing grade".
2. Machine gates that cannot be argued with: hooks and the verify script.
3. A skeptical reviewer that is not the author.
4. A rationalization table quoting the excuses agents actually use.
5. Required evidence slots in every report.
6. Before shipping the skill, micro-test its wording against a no-guidance control: at least 5 reps, read every hit, and treat variance as a metric [superpowers].

### 3.5 Architecture playbook

**Web: TypeScript + Vite + three/R3F.** Structure below is my synthesis of koota's core/view split, R3F docs, three.js manual and Gaffer.

```
src/
  core/          # pure TS simulation: NO 'three'/'react' imports (enforced by dependency-cruiser)
    sim/ systems/ components|traits/ fsm/   rng.ts (seeded)   loop.ts (fixed step)
  render/        # three objects, materials, view-sync from core state; owns dispose()
  assets/        # manifest.ts (single list: id, url, type, group) + registry (load, cache, refcount, dispose)
  scenes/        # Scene interface: enter(), update(), exit() -> must dispose what it created
  input/         # device -> action map; game code reads actions only
  config/        # tunables (speeds, damage, budgets) — the only place numbers live
  ui/  audio/
  debug/         # qaApi, stats-gl, GUI; excluded from prod build
  main.ts
tests/unit (vitest)  tests/e2e (playwright)  qa/ (verify scripts, shots.ts, baselines/, budgets.json)
docs/ARCHITECTURE.md  docs/adr/NNNN-title.md
```

- **Loop.** Accumulator with fixed `dt`, clamp `frameTime` to 0.25 s, render interpolated with `alpha = accumulator/dt` [Gaffer]. Without a clamp and headroom, a slow simulation falls into the "spiral of death".
- **Determinism.** Seeded RNG and fixed `dt` in core make tests and QA shots reproducible.
- **R3F.**
  - Never `setState` in `useFrame` or in fast events; mutate refs and use deltas.
  - Don't re-create objects in loops.
  - Use `useLoader` for caching.
  - Use `frameloop="demand"` with `invalidate()` for scenes that come to rest.
  - Use instancing, and visibility instead of remounting.
- **Lifecycle.** Each scene's `exit()` disposes geometries, materials, textures, render targets and skeletons, removes listeners and stops loops. Verify with the reload-loop memory test (G4). Run one render loop per canvas.
- **Events.** Use a typed event bus only for cross-system notifications, with past-tense names. A central queue "is still a global", the world may have changed by the time an event is processed, and loops are possible [GPP]. Prefer direct calls inside a module.
- **Pools** for frequently spawned objects (projectiles, particles) [GPP object-pool].
- **State machines** with explicit transition tables. All gameplay numbers come from config [CCGS gameplay-code rules].
- **TypeScript.** `strict`, `noUncheckedIndexedAccess` (adds `undefined` to unchecked index access), `exactOptionalPropertyTypes`, `noImplicitOverride`.
- **ESLint.** `max-lines` (default 300; I suggest 300–400 as an error) plus `max-lines-per-function`.
- **Other gates.** knip (unused deps, exports, files), dependency-cruiser (layer rules: `core` must not import `render|ui|three`), size-limit (bundle budget).

**Godot 4** [godot-docs]:
- **Naming.** snake_case files and folders (the PCK virtual filesystem is case-sensitive), PascalCase nodes.
- **Folders.** Third-party code in `addons/`. Group assets near their scenes (`characters/player/…`, `levels/…`). Use `.gdignore` for non-asset folders.
- **Self-contained scenes.** "If at all possible, you should design scenes to have no dependencies". Inject from the parent. Signals respond to behaviour, not start it, and are named in the past tense.
- **Autoloads.** Use one only for a system that "tracks all of its data internally, should be globally accessible, should exist in isolation". Systems that modify other systems' data are regular nodes or scenes. Global state widens the bug-search space to the whole project.
- **Typing.** Static typing everywhere, and enable the extra GDScript warnings. Tests in `test/` with GUT or gdUnit4. Data-driven Resources for config.

**Unity** [mostly UNVERIFIED; docs blocked]:
- ScriptableObjects for config (CCGS example).
- Assembly definitions per layer.
- EditMode tests for pure logic, PlayMode tests for integration.
- Graphics Test Framework for render regressions.

**Preventing rot in an agent-maintained codebase:**
- **CLAUDE.md.** Under 200 lines; each line should prevent a real mistake ("Would removing this cause Claude to make mistakes?"). It holds commands, an architecture map, and gotchas. Move detail into `.claude/rules/*.md` with `paths:` globs, which load only when a matching file is read or edited. Run `/doctor prompt-audit` periodically [memory, cc-best-practices].
- **ADRs.** Use the Nygard template (Title, Status, Context, Decision, Consequences) for every irreversible choice: engine, ECS vs scene graph, physics library, asset pipeline.
- **Refactor gate.** When a file exceeds the line limit, or after 3 failed fixes, plan a split or question the architecture before continuing [superpowers]. Make surgical changes and remove only the orphans your own change created [karpathy].
- **Plans** list exact files and their interfaces first: "files that change together live together", and prefer small focused files [superpowers writing-plans].

---

## 4. Failure modes & anti-patterns (evidence → countermeasure)

1. **Self-praise and lenient self-grading** [harness-design] → separate reviewer, hard thresholds, few-shot calibration.
2. **Reviewer finds issues, then approves anyway; tests superficially** [harness-design] → "a finding stays a finding"; a contract with granular criteria (the harness post's Sprint 3 had 27); probe edge cases.
3. **Declares victory early, or marks a feature done without end-to-end testing** ("unit tests or curl … but would fail to recognize that the feature didn't work end-to-end") [effective-harnesses] → feature list JSON with `passes`; browser-driven e2e is mandatory; boot smoke test at the start of every session.
4. **Fabricated progress reports** [prompting-fable-5] → audit claims against tool results; Stop hook.
5. **Hard-coding to pass tests, editing tests** [prompting-best-practices, effective-harnesses] → anti-hardcoding prompt; tests protected; reviewer checks the diff for test edits.
6. **Silent fallbacks.** Examples: a failed GLTF load shows a placeholder cube, a catch-all swallows a shader error, `?.` hides a missing node [pr-review-toolkit silent-failure-hunter, applied to games] → asset load failure is fatal in QA mode; console errors fail G3.
7. **Blank or black headless canvas.** No SwiftShader opt-in [Chromium]; Godot `--headless` [RenderingServer]; capture before the first draw [Viewport doc] → explicit flags, `ready` flag, `frame_post_draw`, blank detection.
8. **Stale screenshots and false visual confidence** [terma] → hash and frame-counter checks; force a fresh capture.
9. **Flaky waits.** `networkidle` (DISCOURAGED) [Playwright]; Vite's HMR socket may keep the network busy [OPINION] → app-owned readiness signal.
10. **`toHaveScreenshot` never stabilises** on an animating canvas [Playwright] → QA mode freezes the game; diff only frozen shots.
11. **Reporting SwiftShader FPS as performance** → count budgets in CI; frame time only on real hardware, labelled with the device.
12. **GPU memory leaks**: remove() without dispose(); duplicate render loops [three.js manual; three-doctor] → lifecycle contract plus reload-loop test.
13. **Over-verification and over-engineering from reviewers** [prompting-opus-5; cc-best-practices] → blocking vs optional findings; no generic "verify again" instructions.
14. **Bloated instructions get ignored** ("Bloated CLAUDE.md files cause Claude to ignore your actual instructions") [cc-best-practices] → keep it short and use path-scoped rules and skills.
15. **Vision overreach.** Glitch and spatial errors are missed [GlitchBench; vision limits] → programmatic invariants for geometry and physics.
16. **Unattended runs stop early with a summary that announces the next step** [prompting-opus-5-5] → checklist file; harness re-prompts with open items (max 2–3 times).

## 5. Hype vs reality / honest gaps

- **The evaluator loop costs real money.** Solo run: $9 / 20 min. Full harness: $200 / 6 h, and the core play mode worked only in the harness run. Its value shrinks as the model improves; Anthropic removed per-sprint evaluation on Opus 4.6 and kept a single end pass [harness-design]. Scale review depth to risk.
- **Persuasion research is not about quality.** The Meincke (2025) persuasion study measured compliance with objectionable requests on GPT-4o-mini. superpowers cites it to justify "YOU MUST". Transfer to Claude's code quality is unproven. Wharton reportedly published an updated version in May 2026 [UNVERIFIED].
- **Multi-agent debate is not magic.** At an equal number of responses it did not beat self-consistency (Huang et al.) [ABSTRACT-LEVEL]. Value comes from *new information* (renders, tests), not from more opinions.
- **Multimodal judges have biases and hallucinate** (MLLM-as-a-Judge). Don't use absolute 1–10 art scores as a gate without pairwise reference checks.
- **Studio-style agent sets** (CCGS, 48 agents) encode useful rules, but their process requires user approval on every file write, which is heavy for one developer. Borrow the rules, not the ceremony.
- **Tooling staleness.** r3f-perf was last published 2024-11; Bruno Simon's Experience template is from 2021 and unlicensed; Gaffer is from 2004 but its math is timeless.
- **Godot CI rendering** under xvfb/Mesa and **Unity batchmode screenshots** have no verified recipe in this report. A human or the lead must test them once.
- **I could not open these primary pages:** academic papers and playwright.dev, threejs.org, the Godot and Unity documentation sites. I used GitHub mirrors and search summaries instead.

## 6. Recommendations for the skill

1. **Ship a `qa/` kit per engine:**
   - Web: `qa/verify.ts` (G1–G5), `qa/shots.ts`, `qa/budgets.json`, `src/debug/qaApi.ts` template.
   - Godot: `qa/qa_autoload.gd` plus `qa/verify.sh` (GUT/gdUnit4 and windowed capture).
   - Make the scripts verbose, with specific error messages, so the agent can fix issues itself [skill-best-practices "feedback loops"].
2. **Make QA mode a scaffold requirement.** No feature work until G0 passes. Every session starts with the boot smoke test (G3).
3. **Agents:**
   - `qa-reviewer`: read-only, fresh context, runs verify itself, contract plus hard thresholds, validation pass.
   - `art-reviewer`: vision; pairwise against references from the art bible; binary rubric; crops.
   - Implementers never grade their own work.
4. **Install a Stop hook** (command type) that runs a quick verify and blocks on failure. Document `/goal` usage, e.g. "all gates in qa/out/report.json pass; or stop after 20 turns".
5. **Rigor text**:
   - a short "standards and why" preamble;
   - a verification gate with a rationalization table and red flags (our own wording, superpowers-inspired, MIT-compatible);
   - a progress-claim audit line;
   - an anti-hardcoding line;
   - a report template with required evidence fields;
   - no ALL-CAPS walls, no threats, no generic "double-check".
6. **Architecture templates:** the web folder layout plus dependency-cruiser rules, the TS/ESLint config, a CLAUDE.md skeleton under 200 lines with an architecture map, path-scoped rules for `src/core/**` and `src/render/**`, and an ADR template.
7. **Test the skill's wording** with superpowers-style pressure scenarios and a no-guidance control before release.
8. **Leave out** heavy studio ceremony, the r3f-perf dependency (use stats-gl), absolute aesthetic scores as gates, and FPS gates in headless CI.
9. **Licensing:** do not copy text from anthropics/claude-code plugins (all rights reserved) or from terma (CC-BY-SA). Write our own wording and credit them.

## 7. Videos found but not watchable

- **Godotneers on gdUnit4** (youtube.com/watch?v=CreugthdgJ0). The gdUnit4 README says it "demonstrates how to effectively test your game scenes using GDUnit4".
- **GUT VS Code extension tutorial** (youtu.be/pqcA8A52CMs). The GUT README calls it a "Quick tutorial on setup and use".

## 8. Sources

- github.com/obra/superpowers (skills: verification-before-completion, systematic-debugging, test-driven-development, writing-plans, requesting-code-review + code-reviewer.md, receiving-code-review, subagent-driven-development + task-reviewer-prompt.md, writing-skills + persuasion-principles.md)
- platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices ; …/prompting-claude-opus-5-5 ; …/prompting-claude-opus-5 ; …/prompting-claude-fable-5
- platform.claude.com/docs/en/test-and-evaluate/develop-tests ; …/build-with-claude/vision ; …/agents-and-tools/agent-skills/best-practices
- code.claude.com/docs/en/best-practices ; /hooks ; /goal ; /sub-agents ; /memory
- anthropic.com/engineering/harness-design-long-running-apps (2026-03-24) ; anthropic.com/engineering/effective-harnesses-for-long-running-agents (2025-11-26)
- github.com/anthropics/claude-code/tree/main/plugins (code-review, pr-review-toolkit, feature-dev, ralph-wiggum) ; github.com/anthropics/skills (webapp-testing)
- github.com/mrdoob/three.js test/e2e/{README.md,deterministic-injection.js,puppeteer.js}, src/renderers/webgl/WebGLInfo.js, manual/pages/how-to-dispose-of-objects.html
- github.com/microsoft/playwright docs/src/{test-snapshots-js.md, api/class-pageassertions.md, api/params.md, clock.md, api/class-clock.md}
- raw.githubusercontent.com/chromium/chromium/main/docs/gpu/swiftshader.md
- github.com/mapbox/pixelmatch ; github.com/RenaudRohlinger/stats-gl ; github.com/utsuboco/r3f-perf ; github.com/BabylonJS/Spector.js ; pmndrs/react-three-fiber (docs/advanced/pitfalls.mdx, scaling-performance.mdx, packages/test-renderer) ; github.com/pmndrs/koota (skills/koota/references/architecture.md) ; registry.npmjs.org (versions/dates/licenses)
- github.com/godotengine/godot-docs: tutorials/editor/command_line_tutorial.rst, tutorials/animation/creating_movies.rst, classes/class_performance.rst, classes/class_renderingserver.rst, classes/class_viewport.rst, tutorials/export/exporting_for_dedicated_servers.rst, tutorials/best_practices/{project_organization,scene_organization,autoloads_versus_regular_nodes}.rst, tutorials/scripting/gdscript/static_typing.rst
- github.com/bitwes/Gut (README, documentation/docs/Command-Line.md) ; github.com/godot-gdunit-labs/gdUnit4
- github.com/needle-mirror/com.unity.test-framework (Documentation~/reference-command-line.md), com.unity.testframework.graphics, com.unity.test-framework.performance
- github.com/bfollington/terma (plugins/terma/skills/code-review, plugins/tsal/skills/godot-interactive) ; github.com/Donchitos/Claude-Code-Game-Studios (.claude/agents/qa-lead.md, rules/gameplay-code.md, rules/test-standards.md, skills/smoke-check) ; github.com/kndoshn/threejs-skill-plugin ; github.com/forrestchang/andrej-karpathy-skills ; github.com/brunosimon/my-room-in-3d
- gafferongames.com/post/fix_your_timestep/ ; github.com/munificent/game-programming-patterns (book/game-loop, event-queue, object-pool)
- eslint/eslint docs/src/rules/max-lines.md ; microsoft/TypeScript-Website tsconfig-reference (noUncheckedIndexedAccess, exactOptionalPropertyTypes) ; webpro-nl/knip ; sverweij/dependency-cruiser ; ai/size-limit ; joelparkerhenderson/architecture-decision-record (Nygard template)
- Papers, [ABSTRACT-LEVEL], via search results pointing to the primary pages:
  - Huang et al. "Large Language Models Cannot Self-Correct Reasoning Yet" (ICLR 2024, arXiv 2310.01798)
  - Kamoi et al. "When Can LLMs Actually Correct Their Own Mistakes?" (TACL 2024)
  - Gou et al. "CRITIC" (ICLR 2024)
  - Zheng et al. "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (NeurIPS 2023)
  - Wang et al. "Large Language Models are not Fair Evaluators" (ACL 2024)
  - Panickssery et al. "LLM Evaluators Recognize and Favor Their Own Generations" (NeurIPS 2024)
  - Sharma et al. "Towards Understanding Sycophancy in Language Models" (ICLR 2024)
  - Chen et al. "MLLM-as-a-Judge" (ICML 2024)
  - Taesiri et al. "GlitchBench" (CVPR 2024)
  - Meincke et al. "Call Me A Jerk" (Wharton 2025)
  - Meincke, Mollick et al. "Prompting Science Report 3" (arXiv 2508.00614, 2025)
