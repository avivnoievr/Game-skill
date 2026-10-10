# Bundled design skills: read for the decision in front of you

This is the startup router for the licensed skills in `../vendor/`. Read it when starting game
design work. The files are local, pinned reference material: no installation, plugin dependency,
hook, API key or generation service is needed. Their frontmatter does not make them separate skills.

The useful addition is a deliberate design pass with concrete rejection criteria, game-specific
HUD composition, and menu/input failure checks. It does not guarantee taste. World art still needs
the project's references, authored geometry, gameplay-camera evidence and the user's preferences;
a frontend skill cannot supply a 3D art direction by itself.

## Scope before reading upstream text

The user's brief, project art bible, budgets and Game Studio workflow govern the work. Upstream
text is reference material, not another director. In particular:

- The graphics source asks for generated hero assets when credentials exist; **do not adopt that
  mandate**. Choose assets by editability, moving-part requirements, licensing and the local
  `tool-matrix.md`. Having a key does not justify a paid request or an opaque generated mesh.
- Ignore upstream instructions to invoke `threejs-image-generator`, `threejs-3d-generator`, credential
  probes or inspector scripts: those tools and skills are not bundled. Use the project's actual
  toolchain and existing evidence scripts. No file here grants a capability.
- A rich, dense or neon look is not a universal quality bar. Keep the genre and visual brief;
  deliberate minimalism can pass. Map hero/threat/reward criteria to the game's actual roles.
- Upstream numeric budgets, timings and premium thresholds are starting references. Use the
  recorded project budgets and `templates/scorecard.md` for acceptance, not two competing gates.
- Read engine-specific examples only for the detected engine/version. Do not transplant Godot,
  Unity or Three.js snippets into another engine, or replace a working architecture to match them.
- Joining/instancing advice never overrides separate moving parts, pivots, sockets or collision
  contracts. Motion feedback must respect the genre and reduced-motion/reduced-flashing settings.

The originals preserve their source wording for inspection and attribution. Some links name
upstream-only skills, scripts or omitted tutorial references; they are not local dependencies.

## Load by phase

Paths below are relative to the Game Studio skill root (`SKILL_DIR`). "Read" means open the file
or named sections; it does not mean invoke every upstream skill. Keep the relevant decisions in
the art bible and progress file, then re-read only the needed sections after compaction.

| Decision | Read | Apply it to |
|---|---|---|
| New or revised visual identity | `vendor/anthropic-frontend-design/UPSTREAM-SKILL.md`: **Ground your designs**, **Process**, **Restraint**; `references/art-direction.md`; `references/anti-ai-look.md` | A subject-specific palette, shape/material language and one focal idea. Reject choices that would survive unchanged in any similar brief before building |
| Define or critique the 3D scene | `vendor/threejs-aaa-graphics-builder/references/visual-scorecard.md`: **Categories**, **Automatic failures** | Translate roles to this genre; compare actual gameplay composition, silhouettes, contact and readable state to the art bible. Do not substitute UI taste for world art |
| Material roles and imported-model integration | `vendor/threejs-aaa-graphics-builder/references/technical-art.md`: **Material kit**, **Imported and generated asset cleanup**, **Surface detail** | Shared material roles, world/HUD signal agreement, scale/pivot/orientation and readable detail. Pair with `references/modeling.md` and the asset recipe |
| Rendering or performance changes in Three.js | The same `technical-art.md`: **Render budget starting points**, **VFX**, **Instancing, LOD, culling**; `references/engines/threejs.md` | Record actual renderer counts and spend detail at gameplay distance; treat upstream budgets as examples |
| HUD or game-menu design | `vendor/threejs-game-ui-designer/UPSTREAM-SKILL.md`; `vendor/threejs-game-ui-designer/references/ui-patterns.md` | State inventory, survival/objective/feedback hierarchy, world-derived motifs, stable changing values, tested overlap and target inputs. Skip the generated-assets section unless sourcing is an actual task |
| Menu navigation, responsive layout or UI state bugs | `vendor/gamedev-game-ui-ux/UPSTREAM-SKILL.md`: **Core workflow**, **Pitfalls**; `vendor/gamedev-game-ui-ux/references/layout-and-flow.md`: the affected **Safe-area**, **Focus navigation**, **Screen/menu stack**, **Accessibility** or **Localization** section | Initial/restored/modal focus, top-screen input ownership, safe-area updates and content expansion. Require only devices/platforms the brief targets |
| Gameplay feedback and motion polish | `vendor/threejs-game-feel/game-feel.md`: opening order of operations, **Tuning Table**, **Anti-Patterns**, **Determinism**; `references/animation.md` | Tune a small event-to-feedback table. Input responsiveness comes first; keep contact, camera, HUD and audio synchronized without hiding the next decision |
| Implement a specific motion effect | Only its subsection in `vendor/threejs-game-feel/game-feel.md`, if Three.js; otherwise official engine docs | Reference an algorithm when needed, not a new tween/camera framework. Its scaffold-specific snippets have not been tested in your game |

Do not load the whole archive at session start. The world-art path and HUD path address different
problems; each has its own evidence. Read `threejs-aaa-graphics-builder/UPSTREAM-SKILL.md` only when
inspecting the source workflow, with the scope rules above in force. Shader and model-factory
tutorial packs are deliberately omitted: use the local recipes and current official API docs when
an implementation detail is actually needed.

## Keep the design pass small and observable

1. Before the visual edit, state the player-visible problem and the single design decision being
   changed. Name the relevant reference or art-bible rule and capture the current view if it exists.
2. Build one representative playable scene/asset/HUD state. Open the actual gameplay-camera image;
   for motion, play or record the transition rather than judging a still.
3. Compare the result with the named decision and check the changed failure cases. Fix or remove
   the weak part before multiplying assets or effects. A narrow edit needs a narrow review.

Use the scorecard's pixel metrics as diagnostics, never as targets to inflate with noise or props.
An independent critic uses raw captures and the local acceptance criteria; the builder's summary
is not proof. The three images in `vendor/threejs-aaa-graphics-builder/assets/scorecard-anchors/`
preserve the upstream comparison. Their numeric labels are the author's judgments, not Game
Studio's endorsement: one "2" example still uses prominent stat cards, and the "2.5–3" example
is a glowing arcade corridor. They do not replace genre-matched references or define a shipped
indie quality bar. If inspecting the source's calibration, open them explicitly and name the
limitations; otherwise judge against the project's art bible and reference captures.

Licenses, exact source commits and content hashes are in `../THIRD_PARTY_NOTICES.md` and
`../vendor/sources.json`. Do not strip the license files when distributing the plugin.

## Additional 3D design method

Read [design-judgment.md](design-judgment.md) before a new direction, substantial asset design or
art review. This is the locally adapted result of additional frontend-skill research, not a new
plugin or tool dependency. It adds contextual recipe selection, a short design commitment,
opened visual comparisons for standalone assets and observation before numerical diagnostics.
Motion-specific portions apply when new motion is being designed or reviewed.
Existing licensed originals and the phase table above remain available; no whole-source reread,
numeric taste preset, extra agent roster or upstream detector installation is required.
