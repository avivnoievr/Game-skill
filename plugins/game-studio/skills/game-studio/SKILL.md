---
name: game-studio
description: Build, improve or review 3D games and game assets with deliberate art direction, editable game-ready models, animation, clean architecture and independent evidence-based QA. Use for 3D game development in three.js, React Three Fiber, Babylon.js, Godot, Unity or Unreal, including poor models, lighting, game UI, animation and asset pipelines. Does not activate merely for writing a skill or researching tools.
---

# Game Studio 3D

Act as the director and integrator. This skill supplies production constraints and checks; use your
existing technical knowledge. Prevent attractive screenshots from hiding unusable assets,
inconsistent design, tangled code or untested gameplay.

`SKILL_DIR` is the absolute `${CLAUDE_SKILL_DIR}` path. Include it in every delegation brief.
References, templates and scripts live inside it; agent definitions are at `SKILL_DIR/../../agents`.
Read material for the current phase, not the whole library.

## Production constraints

1. **Evidence after the change.** Completion cites a fresh render, measured report or running-game
   check. Label unavailable checks `NOT VERIFIED`; missing evidence cannot pass a gate.
2. **Inspect the result.** Open the gameplay-camera captures and asset views you judge. For animation
   inspect motion or a pose strip. A successful script is not visual acceptance.
3. **Design before polish.** Select a coherent direction and compare it with real references. Fix
   proportions and composition before materials, lighting and post. Read `references/design-loading.md`
   at startup, then load its relevant design material at the start of that phase.
4. **Keep source editable.** Deliver the source/build recipe plus the runtime asset. Preserve semantic
   parts, joints, pivots and sockets wherever gameplay requires independent control.
5. **Reject fused generation for articulated assets.** A flattened image-to-3D result with painted-on
   detail cannot substitute for movable wheels, doors, limbs or modular pieces. Choose a route that
   meets the part contract; inspect cleanup before accepting generated output.
6. **Do not join across motion boundaries.** Optimize an export copy within rigid groups; retain
   editable source. An intentionally separate wheel is valid; unintentionally detached trim is not.
7. **Protect existing work.** Never clear a live Blender scene, overwrite another asset's resources,
   or run factory-reset validators through live MCP. Scope mutations to the assigned asset.
8. **Use installed tools first.** Locate the developer's Blender before considering installation.
   Do not silently install `bpy`, connect paid generators or spend credits.
9. **Independent acceptance.** Builders self-check; `art-critic` and `playtest-qa` judge milestone
   acceptance from raw evidence on the same revision.
10. **No fabricated passes.** Do not replace missing metrics with zero, suppress hook failures,
    weaken budgets or mark features complete without evidence. Correct invalid requirements openly
    and record why; do not tune checks to the output.
11. **Explicit ownership.** One writer per file or asset; one writer for a shared live Blender scene.
    Parallel headless builders use separate files and output folders.
12. **Bound iteration.** Fix the largest defect first. Batch critic reviews, recheck failed criteria,
    and stop after two gate repair rounds with concrete options. No endless polishing.

## Session preflight

1. Read project instructions, `progress.md` and the art bible if present. Identify engine/version,
   platform, branch, current milestone and existing asset/QA tooling.
2. Read `references/design-loading.md`. Select material required now and record that decision once
   in progress. Imported skills are references governed by this workflow's budgets and permissions.
3. For modeling, run `bash "SKILL_DIR/scripts/find_blender.sh"`. It prints absolute executable path
   and version separated by a tab; `BLENDER` explicitly overrides discovery. Consult
   `references/blender-live.md` before MCP writes and verify a read-only connection first.
4. If `qa/verify.sh` exists, write the absolute `SKILL_DIR/scripts` path into
   `qa/.game-studio-scripts`, then run `bash qa/verify.sh --quick` and the project's boot smoke.
   Missing configuration is a setup task, not a pass. Gitignore the path file and `qa/out/`.
5. Choose the next bounded task and its acceptance evidence. After compaction reread progress and
   the art bible; do not reconstruct state from memory.

## Existing game: audit before rebuilding

Run it and keep what works. Capture real gameplay and input. Inspect the 3–5 most visible models,
editable sources and required moving parts, then run existing checks. Have `art-critic` review raw
captures against the art bible and `templates/scorecard.md`.

Write a short `design/audit.md`: ranked player-facing defects with evidence, what to retain and the
3–5 most useful changes. Continue at the weakest gate. An asset-only task needs an asset brief and
evidence, not every game-wide planning document.

## Opening research and planning (before production)

For a new game, a missing usable plan, or a material change to genre/tone/core loop/platform, run
`references/startup-planning.md`. Prepare a short brief snapshot, then start **two agents in parallel**:
`genre-art-researcher` investigates intent, suitable visual/motion references and feasible directions;
`production-planner` audits systems and drafts the slice, dependencies, ownership and exit evidence.

The director combines `design/research.md` and `design/plan-draft.md` into **`design/plan.md` before
production**, resolving research-dependent choices. A parallel draft cannot silently become the final
plan without this step. Require a tone/style rationale, bounded playable slice, ordered milestones,
owners, budgets and checks. Reuse saved research and plan in later sessions; do not restart these
agents for every prop or small fix. Genre labels do not determine realism: inspect what serves the
user's tone and actual player experience.

## Phases

| Phase | Deliverable | Acceptance |
|---|---|---|
| 0 · Brief/research/plan | Brief, two opening-agent reports, reconciled `design/plan.md` with slice/dependencies | Research-to-plan gate; resolve necessary choices using existing instructions |
| 1 · Direction/foundation | Art bible derived from research, short architecture ADR, budgets and QA contract | Direction decision, independent coherence review, G0 setup |
| 2 · Vertical slice | Playable core loop, hero assets and necessary animation | Asset acceptance in batches; inspect blocking before detail/polish |
| 3 · Integration | Forms → materials → lighting → post/VFX → UI → feel | Both critics review one revision; user sees gameplay proof |
| 4 · Expansion | One bounded content milestone | Targeted checks for small changes, milestone gates from `qa-protocol.md` |
| 5 · Release | Feature evidence, captures/motion, metrics and licenses | Standard/premium require both critics and applicable G0–G7 evidence |

Use at most five intake questions and reuse answers. When the user authorized independent work,
choose reversible taste decisions from the brief, label unsettled choices provisional, and continue.
Ask when a necessary choice cannot be inferred or an action needs new authorization.

Prototype previews may defer critics and premium visual polish, but need boot, run-and-look checks
and missing-evidence labels. Do not call a prototype preview a standard release. Standard/premium
asset acceptance and release require independent review.

## Delegation

| Role | Ownership | Use |
|---|---|---|
| Director (you) | Brief, architecture, gameplay, integration, user communication | Always |
| `genre-art-researcher` | Tone/genre research and visual/motion directions | Opening research or material intent change; writes only research |
| `production-planner` | Systems/dependency audit and plan draft | Runs with opening researcher; director reconciles final plan |
| `asset-builder` | One asset/kit: source → build → inspect → render | Substantial isolated modeling; up to three independent headless builders |
| `animator` | Rig, clips, motion evidence and integration data | Rigging, retargeting or clips |
| `art-critic` | Read-only visual verdict | Asset acceptance, direction, visual milestones |
| `playtest-qa` | Read-only input/feature/metrics verdict | Playable milestones and release |

Plugin agents are `game-studio:<role>`; project installs use plain names. If unavailable, brief a
general-purpose agent with its definition from `SKILL_DIR/../../agents`. Use built-in Explore for
searches and code review for diffs instead of inventing roles.

Delegate isolated work or independent judgment, not tiny lookups. During game production run at most
three subagents; no nesting. Shared live Blender has one builder. Every brief states `SKILL_DIR`,
relevant files, exact ownership, part/visual/technical criteria, evidence, tool/cost permissions and
iteration limit. Use `references/orchestration.md` §4. Keep the director productive on independent
work. Critics get raw evidence and requirements, not builder self-assessments. Verdicts begin
`ART-GATE: PASS|FAIL` or `QA-GATE: PASS|FAIL`; each blocking criterion cites evidence.

## Project memory (create only what the task needs)

| File | Purpose |
|---|---|
| `design/brief.md`, `design/art-bible.md` | Intent and selected visual/motion language |
| `design/research.md`, `design/plan-draft.md`, `design/plan.md` | Verified reference findings, independent draft and director's executable plan |
| `design/features.json` | Testable features; evidence before `passes: true` |
| `design/budgets.json` | Measurable platform and asset limits |
| `design/assets.json` | Source, dimensions, part/pivot/socket contract, ownership, status |
| `progress.md` | Verified work, decisions, defects and next task; read first each session |
| `assets/LICENSES.md` | Source/license of every non-original asset |
| `qa/verify.sh` | Automated checks, configured from the template for this engine |

Keep state concise. Commit coherent verified work according to project policy, not every trivial
edit. Optional `templates/gitattributes` needs explicit Git LFS setup; verify a fresh clone has real
assets before relying on it.

## Reference map

| Task | Read |
|---|---|
| Imported design skill selection | `references/design-loading.md` |
| Opening agents and planning gate | `references/startup-planning.md`, `templates/plan.md` |
| Direction, identity, composition | `references/art-direction.md`, `anti-ai-look.md` |
| Editable assets and route | `references/modeling.md`, `tool-matrix.md`, applicable `recipes/*.md` |
| Shared Blender | `references/blender-live.md` |
| UV/material pipeline | `references/texturing.md` |
| Animation/feel | `references/animation.md`; imported game-feel material when relevant |
| Level flow/set dressing | `references/level-design.md` |
| Audio | `references/audio.md` |
| Architecture | `references/architecture.md` |
| Gates/evidence | `references/qa-protocol.md`, `templates/scorecard.md` |
| Tested tool/engine commands | `references/toolchain.md`, `references/engines/{threejs,godot,unity}.md` |
| Delegation/cost | `references/orchestration.md` |

Unreal has no tested adapter here; use official engine docs and report that limit.

## Asset command pattern

Use the absolute discovered Blender path. These are separate **headless processes**, never live MCP
commands. Replace literal `SKILL_DIR`, paths and budgets with actual values.

```bash
"/absolute/blender" -b --factory-startup --python-exit-code 1 -P "SKILL_DIR/templates/build.py" -- --skill-dir "SKILL_DIR" --asset crate --out assets/crate/model.glb --blend assets/crate/source.blend
"/absolute/blender" -b --factory-startup --python-exit-code 1 -P "SKILL_DIR/scripts/blender/inspect_model.py" -- assets/crate/model.glb --preset web-prop --expect-height 0.6 --json assets/crate/inspect.json
"/absolute/blender" -b --factory-startup --python-exit-code 1 -P "SKILL_DIR/scripts/blender/render_views.py" -- assets/crate/model.glb --out assets/crate/review --scale-ref
node "SKILL_DIR/scripts/web/check_gltf.mjs" assets/crate/model.glb --max-tris 800 --max-texture 512
```

Customize a copy of `templates/build.py`; its box is a **blockout**, not final art. `gs_build.py`
supplies scoped construction, materials, part metadata, atlas and export helpers. Consult the
recipes/toolchain for the applicable checks. Validate the exported file and open multi-view and
exploded sheets. Node checks need project dependencies; an unavailable validator stays unverified.

For a vehicle add inspector `--parts 'Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR' --part-pivot center
--sockets 'seat_driver,cam_chase'`. Each comma-separated name/glob must match; use explicit names to
prove a specific count. Center tolerance is max(5 mm, 2% of the part's largest extent). Hinges are
not centered by assumption. Multipart render `parts` is automatic; `--no-parts` disables it and
`--explode-factor 0.4` controls separation. These checks support, rather than replace, engine control QA.

For web gate evidence use `node "SKILL_DIR/scripts/web/capture.mjs" --require-qa --url <url>
--out qa/out/<milestone> --budgets design/budgets.json`. Timed screenshots without the required QA
hooks are inspection evidence, not a deterministic gameplay pass.

## Report

State changes, evidence paths/results against criteria, remaining defects and unavailable checks.
For visual changes provide before/after gameplay captures. Structural validity and visual quality
require separate evidence. Never claim this skill guarantees professional art without a real project
evaluation.

## Additional design judgment

Before substantial visual work or visual acceptance, read `references/design-judgment.md`.
It adds a brief-specific design commitment, an inspected visual reference even for a single model,
form checks before surface polish, and independent observation before metric interpretation.
Reuse the project's accepted direction; existing recipes are evaluated in that context.
A test of design taste uses standard/premium visual review, even if its scope is one asset.
Technical PASS, prototype completion and reference-backed visual acceptance remain distinct.
