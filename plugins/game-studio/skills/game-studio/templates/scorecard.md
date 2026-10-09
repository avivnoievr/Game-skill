# Visual scorecard (used by art-critic)

Score each category 0–3 against the anchors, citing an evidence path for every score. The anchors are
deliberately concrete so scores mean the same thing every time. Category structure adapted, with
credit, from majidmanzarpour/threejs-game-skills (MIT).

## Anchors (all categories)

| Score | Meaning |
|---|---|
| 0 | Missing or broken |
| 1 | Placeholder or default: primitives, default materials and lights, generic UI, nothing chosen |
| 2 | Authored and intentional: follows the art bible, coherent, minor issues only. **This is the "doesn't look AI-made" bar** |
| 3 | Distinctive and polished: would hold up next to a shipped indie game in the same genre |

## Categories

| # | Category | 1 looks like | 2 looks like | 3 looks like | Binary checks (all must be yes for ≥ 2) |
|---|---|---|---|---|---|
| 1 | Art direction | Generic; could be any game | The art bible is visibly applied | One bold element defines the game's identity | Palette roles respected? The one bold element visible? No banned default without an art-bible reason? |
| 2 | Hero / player | Capsule or primitive assembly | Authored model, readable silhouette, animated | Character with personality in form and motion | Recognizable in the silhouette shot? Stands out in the grayscale shot? |
| 3 | Threats / obstacles | Recolored primitives | Distinct authored shapes per type | Telegraphs and shapes teach the player | Each type nameable by shape alone? Threat color semantic consistent? |
| 4 | Rewards / interactables | Floating cubes or spheres | Authored, readable, semantically colored | Inviting; feedback on interaction | Distinguishable from threats in grayscale? |
| 5 | World / environment | Flat ground plus scattered primitives; empty | Layered, set-dressed with purpose, grounded | Landmarks, storytelling, a sense of place | Nothing floating? No perfect grids? Rest areas exist? |
| 6 | Materials | Default grey or flat unlit colors | Palette materials with variation; metals reflect | Material contrast tells the story (wear, use) | No pure-black albedo? IBL present wherever metals exist? |
| 7 | Lighting / render | Default lights, no tone mapping | Designed key/fill/IBL, grounding, chosen tone mapper | Light guides the eye; mood per state | Shadows colored, not black? Post-off shot still reads? |
| 8 | VFX / motion | None, or linear tweens | Eased motion, juice tiers, clean transitions | Game feel is a selling point | Motion evidence exists (sequence/strip)? Shake decays? No foot sliding? |
| 9 | UI / HUD | Web-app look (cards, pills, gradients, emoji) | Game-specific paradigm, hierarchy, one icon set | UI feels part of the world | No §2 UI tells from anti-ai-look.md? Text never clipped? HUD clear of the play path? |
| 10 | Performance evidence | No numbers | Renderer counts within budget; 0 errors | Real-GPU frame time within budget | Counts reported? Budget respected? |

## Thresholds by rigor level

- **prototype:** no visual gate. Automatic failures are still reported.
- **standard:** every category ≥ 2, and no automatic failure.
- **premium:** every category ≥ 2, average ≥ 2.3, no automatic failure, and real-GPU frame time
  measured (G6).

A category scored below the threshold fails the gate, whatever the average. Never round up.

## Automatic failures (any one fails the gate)

- An active gameplay shot dominated by placeholders, or empty.
- The hero is a primitive assembly or "primitive plus glow".
- Gameplay roles can't be told apart in the silhouette or grayscale shots.
- The HUD is mostly stat cards or other web-app UI.
- Fog, darkness or bloom stands in for geometry.
- UI overlaps the play path, or text is clipped.
- Metals render black (no environment map).
- Floating objects in the gameplay or hero shots.
- No evidence from real input (only staged or title-screen shots).
- No renderer diagnostics (draw calls, triangles, errors).

## Advisory image metrics (from capture.mjs or image_metrics.py)

Several flags on gameplay shots argue against scores of 2 or more. The critic must address each flag
in writing. "Do not add noise just to raise metrics": metrics are evidence, not targets.

## Asset acceptance (single asset, from render_views.py output)

| Criterion | ≥ 2 means |
|---|---|
| Silhouette | Reads as *this* object in the black-on-white view |
| Proportions and scale | Matches the brief's dimensions; sensible next to the 1.8 m figure |
| Form quality | No primitive soup; bevels sized per part; detail recessed; calm areas present |
| Joins | Every part attached (no floating warning), no z-fighting seams |
| Materials | Palette roles, tonal or roughness variation, correct metalness |
| Style match | Same bevel scale, shading and texel density as the style sheet and accepted assets |
| Technical | `inspect_model.py` PASS (or a WARN explained in the asset report), `check_gltf.mjs` 0 errors, within budget |

To pass: every criterion ≥ 2, with a technical PASS.
