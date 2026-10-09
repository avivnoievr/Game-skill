# QA protocol: evidence, gates, critics

Contents: 1. Why QA works this way · 2. QA mode (make the game drivable) · 3. Gates G0–G7 ·
4. What counts as evidence · 5. Visual review protocol · 6. Image metrics · 7. Performance and memory ·
8. Asset and animation QA · 9. Deterministic backstops · 10. Test the gates · 11. Report formats

## 1. Why QA works this way

- **Introspection is weak; external signals are strong.** Without outside feedback, a model checking
  its own reasoning often fails to improve it, and can make it worse. With reliable feedback (tests,
  renders, metrics, error logs) it corrects well. For a game, those signals are rendered frames,
  renderer counters, console errors, deterministic tests and asset reports. Every gate below is built
  from them.
- **Builders are lenient judges of their own work.** Anthropic found that agents grading their own
  output "confidently praise the work, even when obviously mediocre". Out of the box, Claude as QA will
  "identify legitimate issues, then talk itself into deciding they weren't a big deal". Hence a
  separate, read-only, skeptical critic with hard thresholds (`orchestration.md` §6).
- **Generic "double-check your work" instructions add cost, not quality** on current models. What
  works: every claim cites a tool result from this session, and anything unverified is labelled
  unverified.
- **Vision is good at taste and bad at glitches.** Multimodal judges are unreliable at spotting
  clipping, z-fighting and physics bugs, and at counting. Assert those programmatically. Use vision
  for composition, readability, palette and style, and judge them side by side against references.

## 2. QA mode: make the game drivable (G0 requirement)

A game that only runs in real time with random seeds cannot be verified reliably. Before feature
work, add a dev-only QA mode:

- It is enabled by `?qa=1&seed=N` for web, a user argument for Godot (`-- --qa`), or a define for Unity.
- In QA mode the game uses a seeded RNG and a fixed timestep, and does not free-run its loop. The
  harness steps it.
- **Web:** expose `window.__QA__`, which `scripts/web/capture.mjs` consumes:

```ts
// src/debug/qa.ts — included only in dev / ?qa=1 builds
window.__QA__ = {
  ready: false,                                 // true after assets loaded AND first frame rendered
  stats: () => ({ drawCalls: renderer.info.render.calls, triangles: renderer.info.render.triangles,
                  geometries: renderer.info.memory.geometries, textures: renderer.info.memory.textures,
                  programs: renderer.info.programs?.length ?? 0 }),
  state: () => game.sim.snapshot(),             // small JSON: positions, hp, score, current state names
  shots: {                                      // fixed camera rigs: identical every run
    gameplay: async () => { cameraRig.apply('gameplay'); game.render(); },
    wide:     async () => { cameraRig.apply('wide'); game.render(); },
    hero:     async () => { cameraRig.apply('hero'); game.render(); },
  },
  advance: async (ms) => { game.stepFixed(ms); game.render(); },   // N fixed steps, then one render
};
```

- With several render passes (EffectComposer), set `renderer.info.autoReset = false` and call
  `renderer.info.reset()` once per frame, so the counts cover the whole frame.
- Asset load failures must be **fatal** in QA mode. A silent placeholder cube is a lie that passes
  every screenshot.
- Godot and Unity equivalents are in `engines/godot.md` and `engines/unity.md`.

## 3. Gates

One entry point runs the automated gates: `qa/verify.sh` (template: `templates/verify.sh`). It exits
non-zero on failure and writes `qa/out/`. A gate counts as passed only when you can quote this
session's output.

| Gate | When | Blocking pass condition | Tools |
|---|---|---|---|
| **G0 Scaffold** | before the first feature | Game boots; QA mode exists; `qa/verify.sh` runs; `design/` state files exist | — |
| **G1 Static** | every change | Typecheck 0 errors; lint 0 errors (incl. `max-lines`); layer rules 0 violations | tsc, ESLint, dependency-cruiser / GDScript warnings |
| **G2 Logic** | every change to simulation code | Unit tests green. A bug fix ships with a test you **saw fail** before the fix | vitest / GUT / gdUnit4 / Unity EditMode |
| **G3 Boot smoke** | every change, start of every session | 0 page errors, 0 console errors, 0 failed requests; `ready` within 30 s; canvas not blank; renderer counts within budget | `capture.mjs` / engine equivalent |
| **G4 Playthrough** | each feature | Scripted input for N simulated seconds keeps invariants true (moved > X, no NaN transforms, never below the floor, objective reachable); after 5 scene reloads, geometry/texture counts return to baseline | `capture.mjs --sequence --hold`, `__QA__.state()` |
| **G5 Visual** | each visual milestone | The shot list renders; `art-critic` passes every scorecard threshold | `capture.mjs`, `render_views.py`, art-critic |
| **G6 Real-GPU perf** | milestones | p95 frame time within budget on the target device class, measured headed on real hardware and labelled with the device | stats-gl / Chrome DevTools trace / Godot monitors |
| **G7 Release review** | before "done" | `art-critic` and `playtest-qa` PASS on the same build revision; every feature in `features.json` has evidence | both critics |

Rigor levels:
- `prototype` runs G0–G4 and the run-and-look rule.
- `standard` adds G5 at the vertical slice and at release.
- `premium` runs G5 at every milestone and requires G6.

## 4. What counts as evidence

| Claim | Evidence that supports it | Not evidence |
|---|---|---|
| "It builds / tests pass" | Command, exit code and summary line from this session, after the last change | "It should pass"; an earlier run |
| "It runs" | G3 output: 0 errors, `ready`, renderer counts | The dev server started |
| "It looks right" | Screenshots from the gameplay camera that you opened and looked at, compared with the art bible | Code that sets the right values |
| "The model is game-ready" | `inspect_model.py` + `check_gltf.mjs` PASS and a contact sheet you looked at | The export succeeded |
| "The animation is good" | Pose strip or frame sequence you looked at, plus clip lengths and loop check | The clip plays without errors |
| "It's fast enough" | Frame time on real hardware, labelled with the device; renderer counts | SwiftShader / llvmpipe FPS |
| "Fixed" | The failing check now passes; for bugs, the test failed before and passes now | The edit was made |

"A succeeded command proves the code ran, not that the scene is right." Render it, open it, look at it.

**Before reporting progress, audit each claim against a tool result from this session. If something
was not verified, say so explicitly.** This single habit nearly eliminated fabricated status reports
in Anthropic's testing.

## 5. Visual review protocol (G5 and asset acceptance)

1. **Fixed shot list**, defined in the art bible: gameplay camera, wide establishing, hero close-up,
   darkest area, busiest action moment, and UI over gameplay. Use the same seed, frame and camera
   every time, so iterations are comparable.
2. **Pairwise, not absolute.** Judge the current shot next to its reference image and next to the
   previous iteration. Absolute 1–10 beauty scores drift; pairwise judgments track human preference
   better. When comparing two candidates, swap their order and require the same verdict, because
   position bias is documented.
3. **Binary or anchored questions, written before rendering.** Ask "Is the player silhouette readable
   against the background at 25% scale?", not "how good is it?". The scorecard
   (`templates/scorecard.md`) turns the art bible into such questions.
4. **Evidence before verdict.** Name the region (crop it if needed), describe what is there, then
   judge. Zoom into crops for detail. High-resolution input improves accuracy on dense frames.
5. **Image budget.** Contact sheets keep one image per question. Keep single images ≤ 2000 px on the
   long edge, and fewer than 20 images per review turn.
6. **Calibrate with anchors.** The scorecard describes what a 1, 2 and 3 look like for each category.
   Wording steers results: "museum quality" made outputs converge, while concrete criteria don't.
7. **Never use vision alone for glitches.** Interpenetration, z-fighting, falling through floors and
   NaN transforms are checked programmatically (bounds overlap, raycasts, `state()` invariants).

## 6. Image metrics (non-LLM evidence)

`capture.mjs` computes these for each screenshot on a 320 px copy:

| Metric | Meaning | Flag when |
|---|---|---|
| `lumaStd` | Value contrast (0–255 luma standard deviation) | < 30: flat and washed out |
| `colorEntropyBits` | Variety of colors (512-bin histogram) | < 3: very few distinct colors |
| `dominantColorShare` | Share of the most common color bin | > 0.6: one color fills the frame (empty sky, floor or background) |
| `edgeDensity` | Fraction of strong-gradient pixels | < 0.02: little visible structure or detail |
| `clippedHighlights` / `clippedShadows` | Pure white / pure black share | > 0.05 / > 0.15 |

These are heuristics. A flag argues against a high visual score, and the critic must address it
explicitly. A stylized minimal look can legitimately trip one flag. Several flags on gameplay shots
almost always mean "empty, flat, unlit".

The same JSON records a blank-canvas signature:
- A very low `lumaStd`, plus a dominant share near 1, means nothing rendered.
- Identical hashes on consecutive shots after a change that should be visible mean the capture is
  stale.

## 7. Performance and memory

- **Headless numbers are not performance.** SwiftShader and llvmpipe are CPU renderers capped near
  60 FPS. In CI, gate on hardware-independent counts: draw calls, triangles, geometries, textures,
  shader programs and errors.
- **Measure frame time on a real GPU** (G6). Use a headed browser with stats-gl or a Chrome DevTools
  performance trace, or Godot's `--print-fps` and Performance monitors. Report p95 frame time, not
  average FPS, with the device named.
- Starting budgets live in `design/budgets.json`, set by the director from `modeling.md` §6. Typical
  web desktop targets:
  - ≤ 200–300 draw calls;
  - ≤ 1–2 M triangles in view;
  - device pixel ratio capped at 2;
  - 0 console errors.

  Mobile targets are roughly a third of that.
- **Leak test (G4):** load and unload a scene 5 times, and assert that `info.memory.geometries` and
  `textures` return to baseline. In three.js, removing a mesh does not dispose its geometry, material
  or textures, and render targets and skeletons need explicit `dispose()`.

## 8. Asset and animation QA

Every asset delivered by `asset-builder` arrives with:
1. `inspect_model.py` output, with a budget preset or explicit numbers and the expected height or
   dimensions, at verdict PASS or justified WARN.
2. `check_gltf.mjs` output for the exported GLB, with 0 validator errors.
3. `render_views.py` contact sheet: ortho views for proportions, 3/4 views for form, silhouette and
   wireframe. Add `--scale-ref` for anything that relates to a human.
4. The look render (`--engine eevee` or `cycles`), if materials matter.

Animation QA:
- Run `render_views.py --anim <clip>` for each clip to get a pose strip.
- Use `capture.mjs --sequence` for in-game motion.
- Check the strip against `animation.md` §7: contact poses, arcs, no foot sliding, no popping, loop
  closure (the first and last pose match), no bind-pose leaks.

## 9. Deterministic backstops (optional)

For long autonomous runs, block "done" mechanically with a project-level Stop hook. Put this in the
game repo's `.claude/settings.json`, not in the plugin, so it only runs where it belongs:

```json
{ "hooks": { "Stop": [ { "hooks": [ { "type": "command", "command": "bash qa/stop-gate.sh", "timeout": 300 } ] } ] } }
```

```bash
#!/usr/bin/env bash
# qa/stop-gate.sh: exit 2 blocks the stop and shows stderr to Claude
input=$(cat)
echo "$input" | grep -q '"stop_hook_active": *true' && exit 0   # never block twice in a row
[ -f qa/verify.sh ] || exit 0
if ! out=$(bash qa/verify.sh --quick 2>&1); then
  printf 'Quick verify failed. Fix it before finishing:\n%s\n' "$(echo "$out" | tail -40)" >&2
  exit 2
fi
```

Keep `--quick` fast (typecheck, lint, unit tests). The full G3–G5 run belongs at milestones.

## 10. Test the gates themselves

A gate you have never seen fail is not a gate. When setting up QA, feed each check a known-bad input
once:
- a blank canvas (comment out the render call) → G3 must fail;
- a model with a flipped face → `inspect_model.py` must FAIL;
- an over-budget scene → the budget check must fail.

Record that it failed in `progress.md`.

## 11. Report formats

**Builder or director progress report:**
```
STATUS: DONE | BLOCKED | NEEDS-DECISION
Changed: <files>
Verified: <command> → <exit code / summary line> ; <screenshot path> (looked at: <what it shows>)
Not verified: <anything not run, and why>
Numbers: tris <n>/<budget>, draw calls <n>, errors <n>
Open risks: <...>
```

**Critic verdict** (`art-critic`, `playtest-qa`):
```
ART-GATE: FAIL                       (or QA-GATE: PASS)
Build/revision: <git sha or capture dir>
Scores: <criterion>: <score>/<threshold> — evidence: <path or crop>   (one line per criterion)
Blocking defects (ranked): 1. <defect> — where — why it fails <rule> — concrete fix
Optional: <non-blocking notes>
Declined to judge: <what could not be assessed, and why>
```
