# Asset need → controllable tool → evidence

Choose per asset and record the route in `design/assets.json`. Load only this matrix and the recipe
for the current asset. Blender transport does not determine model quality; semantic parts and evidence do.

## AI-3D decision first

Default to editable Blender construction or a licensed coherent pack for hero props, mechanisms,
vehicles, weapons, sockets and modular pieces. One image-to-3D output is never a finished controllable
asset. The default AI route is **static organic background geometry** with no joint, socket, snapping
grid or gameplay-critical dimensions, a compatible texture style, and approved cost/license.

A deforming character is a separate exception requiring planned retopology, rigging and motion checks;
prefer a rigged pack. If the user explicitly chooses generation for an articulated asset, explain that
segmentation cannot prove hidden mating faces, joint origins or clearances: budget reconstruction and
the same part gates. Verify installed generator parameters; never assume a documented option exists
in an MCP wrapper. No paid job is authorized by this document.

## Selection matrix

| Need | First route / how | Acceptance evidence | Never |
|---|---|---|---|
| Hero hard-surface / moving parts | `gs_build`, [live protocol](blender-live.md) or local CLI; [articulated](recipes/articulated.md) / [vehicle](recipes/vehicle.md) | BOM, required nodes, pivots, sockets, parts sheet, motion sweep | Fuse functional parts or accept a generator blob |
| Grid-snapping structures | [Modular kit](recipes/modular-kit.md), authored against player metrics | Assembled seam/collision test room | Normalize pieces independently or simplify border vertices blindly |
| Character/creature | [One licensed rigged pack](recipes/character-cc0.md); procedural rig only with a usable mesh | Imported clip inventory, deformation/contact/motion evidence | Code-only face as a production character; automatic remesh as finished deformation topology |
| Static organic filler | CC0 scan/pack first; displacement/growth rules; approved generation if suitable | Scale/form/texture-light checks and cleaned export | Use painted shadows as dynamic lighting |
| Materials / flat palettes / trims | [Texturing](texturing.md): matched CC0 PBR, palette/vertex color, bake or shared trim | UV/checker evidence where applicable, in-engine material viewer | Ship procedural Blender nodes as if they were glTF textures |
| Reference sheet | User refs first; orthographic dimensioned views; approved concept generation only if needed | Front/side landmarks align | Treat perspective views or generated labels as dimension truth |
| Vegetation / terrain | [Environment](recipes/environment.md): seeded placement, instancing, editable heightfield | Player route, silhouette/density, near/far transitions | Unique mesh per repeated leaf/rock; image-to-3D terrain layout |
| VFX / decals | Engine-native particles/decals or reusable flipbooks; only where the chosen renderer supports them | Triggered effect with camera/game lighting and overdraw budget | Video clips as interactive VFX; an unsupported renderer feature |
| LOD / delivery | Explicit simplified export copies, engine LOD/instancing; validate before compression | Preserved names/joints/sockets, target-distance silhouette and loader smoke | Promise lower draw calls from a triangle count alone |
| SFX / music / voice | [Audio](audio.md): licensed/user material or controllable synthesis; paid generation only after approval | Event map, human listening, limits/settings, source license | Treat a TTS endpoint as an SFX/music generator |
| HUD / icons / fonts | Load the phase's design references; one icon family, licensed fonts | Readable at play size, interaction captures, attribution | Mix emoji/icon sets or assume a website HUD is game UI |
| Level layout | [Level design](level-design.md): one chosen engine/data/Blender authoring route | Scripted critical path, camera/clearance evidence | Start decorative content before traversal works |

## Non-negotiable delivery boundaries

- Work on owned data/a saved copy; use a script as source. Live writes serialize; validators run separately.
- Join only within one rigid part, on an export copy; keep editable source and all moving nodes.
- Never claim "game-ready" from a successful generation/import/validator alone; inspect engine use.
- Check the license of the **actual downloaded file/pack**; unknown, noncommercial or restrictive terms
  need a project-specific decision. CC0/BY/OFL/vendor licenses are not interchangeable.
- If a download needs the user's login/browser, give the exact asset page, filename and destination
  (`assets/_vendor/<pack>/`), then inspect its license after arrival. Stop repeated blocked fetches.
- Poll a submitted paid job by its ID; do not resubmit after a timeout. No paid/media calls by default.
- Preserve binary sources/deliverables deliberately with an agreed LFS policy. Do not migrate existing
  history or track every disposable QA render merely to satisfy a generic rule.

Basis: original contracts distilled from round-2 reports 02, 04 and 06. Asset budgets and recipes are
project-tunable heuristics, not vendor guarantees. Service model names, prices and free-plan rights must
be checked when used; they are deliberately absent from this runtime matrix.
