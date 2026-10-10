# Environment set: a repeatable family and readable layout

Define near/mid/far use, camera, palette/materials, scale bands, variation seed, collision/nav needs,
density and screen-space/instance budgets. Use [level design](../level-design.md) for the route and
[texturing](../texturing.md) for a shared material family.

| Family | Route | Check before scattering |
|---|---|---|
| Rocks/static organic forms | Few seeded profile/displacement variants or coherent licensed pack | Silhouette, grounded placement, no baked light in albedo |
| Trees/vegetation | Tapered sweeps/growth grammar or pack; shared geometry/materials | Trunk/canopy shape, alpha/overdraw, root contact, wind if used |
| Ground/terrain | Editable heightfield/chunks and deliberate landmarks | Border/collision continuity, slope/traversal, texture scale |
| Architectural set dressing | Authored purpose-driven clusters using kit/prop recipes | Rest areas, distinctive local shapes, joins and player clearance |

Build a small family first, with calm shapes and shared style. Use seeded, rule-based placement and
engine instancing; keep landmarks/collision blockers explicit. Do not merge an entire environment
into one mesh or create unique geometry per repeated grass blade merely to avoid a placement system.
Bake Blender procedural placement only when the engine import route needs it, preserving source rules.

**Gate:** a representative scene patch with the player/camera, not just asset turntables. Check near/
far silhouette, repeated-pattern tells, color/value read hierarchy, density/rest areas, collision/nav and
LOD transitions. Measure actual draw/triangle/texture/overdraw effects; a shared palette is not a
performance guarantee. Walk the critical path and compare fixed shots with the art bible.

Keep a scatter seed and manifest, export names and independent collision proxies. Change density,
geometry or lighting one cause at a time. Distant filler generation follows the [tool matrix](../tool-matrix.md)
and never substitutes for editable level layout or controllable hero assets.

Basis: original recipe from round-2 reports 02/06; no algorithm or fixed polycount guarantees finished
environment art. Calibrate variation, density and performance on this project's actual gameplay camera.
