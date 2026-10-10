# Game-ready 3D models

Contents: 1. The honest ceiling · 2. Choose the source · 3. Brief in numbers · 4. Code-modeling pipeline ·
5. Craft and moving-part contracts · 6. Budgets · 7. Materials, UVs, glTF export · 8. AI-generation pipeline ·
9. Validate and look · 10. Never-list · 11. Blender 4 → 5 API traps

## 1. The honest ceiling (read before promising anything)

- **"The script runs" is not "the model is good".** Benchmarks of LLM-written Blender code show
  that retry loops push executability to nearly 100%, while shape quality barely moves. Even
  successful renders still contain disconnected, floating parts. Your feedback loop must judge the
  *shape*, not the exit code.
- **More viewpoints → better geometry.** Models recover geometry significantly better with
  multi-view and interactive inspection than from a single view. Always review the multi-view
  contact sheet (`render_views.py`), never one screenshot.
- **Primitive assembly has a hard ceiling.** Boxes, cylinders and spheres glued together read as
  "programmer art" however many you add. Quality comes from profiles, lofts, sweeps and revolves,
  detail cut *into* surfaces, bevels sized per part, and calm undetailed areas.
- **Credible from code:**
  - hard-surface props, weapons, furniture, machines and vehicles;
  - architecture and modular kits;
  - rocks and terrain;
  - foliage from growth rules.
- **High-risk for code-only construction:** faces, hands, deforming organic characters, cloth and
  creatures. Prefer suitable authored/licensed sources or an approved generation-and-cleanup route
  when that is the executable option. Primitive assemblies remain placeholders. A procedural source
  may qualify only when its topology, rig, deformation and gameplay-camera motion meet the same
  acceptance criteria; the tool label alone does not establish quality.

## 2. Choose the source (decide per asset, record it in `design/assets.json`)

```
Character / creature / face / hands / cloth?
├─ stylized low-poly fits the art bible → CC0 rigged pack (KayKit, Quaternius, Kenney) → recolor / kitbash   [best]
└─ unique design needed → authored source, or approved generation → planned retopology → rig → motion validation
   (primitive code blockouts remain placeholders; any final route must prove deformation/motion)
Environment kit (walls, floors, dungeon, city) → CC0 kit if the style fits; else code-model on a grid module
Hard-surface prop / weapon / vehicle / machine / furniture → editable parts: procedural construction (§4–5), or a licensed authored source for realism
Rocks → code (subdivide + displace, decimate, vertex-color AO); trees/grass → growth rules or CC0; terrain → heightfield code
Organic prop (statue, food, ornament) → suitable licensed scan/authored source; background generation only under §8's contract
Textures/materials → Poly Haven / ambientCG CC0 PBR sets, or vertex colors / a gradient atlas for stylized looks
```

**One style per game.** Never mix a cartoon CC0 pack with AI-generated realism without a unifying
pass. Unify with a shared palette atlas, the same bevel scale, the same shading model and the same
texel density. Inconsistent assets are the fastest way to look amateur.

Choose controllability and camera quality before transport. Read the [tool matrix](tool-matrix.md) and
only the matching [vehicle](recipes/vehicle.md), [articulated](recipes/articulated.md),
[kit](recipes/modular-kit.md), [character](recipes/character-cc0.md) or
[environment](recipes/environment.md) recipe. A realistic hero can need authored source/human craft;
the procedural route is not a guarantee of production realism.

## 3. Brief in numbers before any vertex

Write `assets/<id>/brief.md`:
- **Purpose:** what it is in the game, camera distance, interactive or static.
- **Dimensions in meters:** source measurements or deliberate design values. Real-world references
  are useful for props; traversal openings/steps/cover use the actual [player/camera metrics](level-design.md).
- **Orientation and pivot:** this project's front convention is −Y in Blender → +Z in glTF.
  The asset root is normally base-center; module/weapon/moving-part pivots follow their functional contract.
- **Budgets:** triangles, materials and texture size, from `design/budgets.json`.
- **Part list (BOM):** each part with the operation that makes it, its parent, and how it joins.
- **Style references:** which art-bible rules apply (palette slots, bevel scale, shading).
- **Views to check:** any special close-ups (hinges, cuts, joints).

## 4. Procedural or authored modeling pipeline

For procedural assets, use `scripts/blender/gs_build.py`: call `gb.begin(id)`, then the helper matching
the form. Raw `bpy.ops` is reserved for a missing operation or measured context need; add a reusable
helper when the operation recurs, rather than extending a context-fragile operator chain. Native
Blender/manual or licensed sources remain valid: preserve editable parts in a working `.blend`,
record source/revision and make the export/validation route reproducible. Do not force a good authored
asset through a code-only rebuild. Follow the [live protocol](blender-live.md) when using a connection.

1. **Blockout at real scale.** Rough volumes only. Run
   `render_views.py --views front,right,q_fr,silhouette --scale-ref` and compare proportions against the
   1.8 m figure and the references. Fix proportions now, because detail never rescues a wrong
   silhouette.
2. **Primary forms, each from the operation that owns it** (§5.1).
3. **Secondary forms:** recesses, panels, openings and joins (§5.2–5.4).
4. **Edges:** bevels, Harden Normals, Weighted Normal (§5.3).
5. **Materials and UVs** (§7).
6. **Game version:**
   - preserve editable semantic source parts; optimize an **export copy**;
   - apply transforms before finalizing joint frames; recheck axes/pivots after changes;
   - join by material only **within one rigid part**; never join independently moving parts,
     sockets or nodes referenced by game code. Measure exported primitives/draw calls;
   - triangulate if normal-mapped;
   - make an LOD by dropping bevel segments if the budget needs it.
7. **Export GLB, then validate and look** (§9). Fix the largest discrepancy first and re-gate.

For procedural assets, save a deterministic, idempotent generator (`assets/<id>/build.py`):
- Re-running it rebuilds its **owned** collection/data via `gb.begin(id)`. Ownership tags, not name
  prefixes, decide what can be removed; preserve user objects and data linked outside the build.
- Seed every random value.
- Print one JSON summary at the end.

A procedural change made live belongs back in the build script. For authored/manual work, the versioned
native `.blend` is source: retain semantic parts, note edits and export settings, and validate its export.
Do not leave the only source in chat history or an unsaved live scene.

Headless call: `blender -b --factory-startup --python-exit-code 1 -P build.py -- --out assets/<id>/`.
- Without `--python-exit-code`, a crashing script still exits 0.
- Without `--factory-startup`, user add-ons change the results.

## 5. Craft rules

### 5.1 Operation by form

| Form | Operation |
|---|---|
| Constant cross-section (beams, rails, trims) | Extrude a profile |
| Changing cross-section (handles, bottles, hulls) | Loft between section rings |
| Axially symmetric (barrels, columns, pots) | Revolve (spin) a profile; weld the poles |
| Pipes, cables, rails along a path | Sweep a profile along a curve |
| Openings (windows, vents, ports) | Build ring topology around the opening (inset), not a boolean on a dense mesh |
| Hollow parts | Solidify with an explicit thickness |

### 5.2 Detail by recess, not glue

- Cut detail into surfaces with `gb.recess` or suitable authored topology. Split sharply folded/concave
  regions rather than assuming a broad even-miter inset is safe. Inspect corners for spikes and
  self-intersections; the helper is not a general self-intersection solver. Glued-on boxes float/z-fight.
- Use greebles at about 1/60 of the object length, clustered and aligned to neighbors.
- **Keep calm areas.** Detail only registers against something undetailed. A model greebled
  everywhere reads as noise.

### 5.3 Edges and normals

- Every manufactured edge gets a bevel. Real objects have no razor edges; edge highlights are what
  make a model read as solid.
- Size bevels to the part, not one global radius:
  - hardware: ~2 mm;
  - panels and slats: ~4 mm;
  - casings and plinths: ~7 mm;
  - frames and machine bodies: ~13 mm;
  - soft upholstered forms: ~45 mm.
  - When unknown, use about 0.5% of the largest dimension.
- **Apply scale before beveling.** On a scaled object, bevels come out uneven ("pillows").
- Game mid-poly: 1–2 bevel segments, Harden Normals, then a **Weighted Normal modifier last**, with
  Keep Sharp on.
- Stack order: Mirror → Booleans → angle-limited Bevel (~30°, Harden Normals) → Weighted Normal →
  (export) Triangulate, keeping custom normals.
- Every wall, groove or step must be wider than 2× the bevel width, or Clamp Overlap shrinks the
  whole object's bevel.
- Booleans:
  - Use the `EXACT` solver.
  - Check the vertex count before and after each boolean, and revert if it collapsed.
  - Prefer `bmesh` operations over `bpy.ops.mesh.*` in headless scripts.

### 5.4 Joins (where parts meet)

- Never let unrelated faces sit flush and coplanar, because they z-fight. Choose one:
  - one continuous mesh;
  - a proud part (≥ 0.8 mm);
  - a reveal gap (1.5–6 mm; ≥ 4 mm to read at 2 m);
  - a declared hidden penetration of 5–15 mm.
- A collar, grommet or flange at an intersection reads better than a bare intersection.
- Static joins need declared contact/gaps; unexplained loose pieces read as bugs. Articulated parts
  can deliberately clear their parent. The inspector checks connected islands per rigid group;
  joint metadata does not excuse unexplained loose islands within that group. See §5.6.

### 5.5 Where to spend triangles

- Spend them on silhouette, apertures, edge highlights and contact points, never on hidden flat faces.
- Segments by radius:
  - r ≤ 25 mm: 10–14 segments;
  - r ≤ 100 mm: 16–24;
  - player-adjacent cylinders ≥ 150 mm: 28–48.
- Flat-shaded low-poly styles use far fewer segments by design. Follow the art bible.

### 5.6 Parts that move, pivots, sockets

- One moving rigid part = one named object; origin on its shaft/hinge, not the asset's ground root.
  Wheels/fans spin about the axle; doors hinge at an edge; slide frames define the translation direction.
- Set the pivot before parenting/instancing. Make mesh data single-user before geometry-origin edits
  (`gb.set_origin` copies shared data); preserve world transforms when parenting.
- `gb.set_joint` writes `joint`, Blender-local `axis`, converted `axis_gltf`, `min`/`max`, `units`
  (`m` for slide, `deg` for angular limits). `gb.socket` makes `SOCKET_<name>` empties. Export extras and
  stable names; engine code consumes them explicitly. Extras do not create runtime joints by themselves.
- Separate visual meshes, collision proxies and socket frames. Each moving body gets a proxy only
  where physics needs one; never spend the render-mesh budget on hidden collision geometry.
- Inspect with `--parts 'Wheel_*' --part-pivot center --sockets seat_driver,cam_chase` when applicable.
  Required names/globs are case-sensitive. Socket prefix `SOCKET_` is optional in the argument.
  The center check covers spin joints and explicitly required untagged parts, not hinge/slide/steer
  pivots. Tolerance defaults to max(5 mm, 2% of the largest part extent); this is a tunable heuristic.
- Show the exploded `parts` sheet plus an engine motion sweep through the joint limits. Bbox-center
  tests do not prove hinge placement, axle direction, hidden faces or collision-free motion.

Use [articulated](recipes/articulated.md) and [vehicle](recipes/vehicle.md) contracts for the current asset.

## 6. Budgets (starting points: the project's `design/budgets.json` is the authority)

| Asset class | Triangles (web desktop) | Mobile | Textures |
|---|---|---|---|
| Small prop (cup, book, crate) | 100–1,000 | 100–500 | 512² or atlas |
| Medium prop (barrel, chair, weapon) | 1,000–3,000 | 500–1,500 | 512²–1K |
| Hero prop | 3,000–8,000 | ≤ 3,000 | 1K–2K |
| Character | ≤ 10,000 (head 2–3k, hands ~1k, body 5–6k) | ≤ 6,000 | 1K–2K |
| Building / large kit piece | 2,000–10,000 | ≤ 4,000 | atlas / trim sheet |
| Stylized low-poly (KayKit-class) | a few hundred to a few thousand | same | one gradient atlas, 1024² → 128² fine |

Scene-level budgets:
- Web desktop: ≤ 200–300 draw calls, ≤ 1–2 M triangles in view.
- Mobile web: roughly a third of that.
- Desktop native: a hard-surface hero asset around 15k triangles with one 2K map is normal.

**Texel density:**
- 512 px/m for third-person; 1024 px/m for first-person or hero items; 256–512 px/m for mobile.
- *Consistency matters more than the value.* `inspect_model.py --texel-density 512` reports deviation.

`inspect_model.py --preset web-prop|web-hero-prop|web-character|mobile-*|desktop-*` encodes these
starting points. Pass explicit flags when the project's budgets differ.

## 7. Materials, UVs, glTF export

**Materials:**
- Use the Principled BSDF only. Procedural node trees do **not** export to glTF: bake them to
  textures, or use vertex colors or a palette atlas.
- Cheap realism:
  - per-part tonal variation (±10% of the base color);
  - edge wear on convex edges (bake it; Pointiness is Cycles-only);
  - roughness variation.
  - Avoid perfectly uniform values.
- No pure black (< 0.02) or pure white (> 0.95) albedo. Metals are metallic = 1 with a colored base;
  non-metals are metallic = 0. Avoid in-between metallic values except at painted-metal edges.
- **Metals need an environment map** (HDRI/IBL) in the engine, or they render black. Check the look
  render.

**UVs:**
- `bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)` (radians) works headless, using
  `temp_override` plus edit mode.
- Hard edges are UV seams on normal-mapped assets.
- An image-textured material without a UV map exports broken. The inspector FAILs it.
- Before image/trim/bake work, open a checker-material preview for stretching/density and align
  directional grain. Deliberate mirrored/stacked UVs remain valid; lightmap UVs need their own contract.
  Choose the [texturing route](texturing.md); collapsed palette UVs are not a detail/lightmap unwrap.

**glTF conventions:**
- 1 unit = 1 m; glTF is +Y up. This project's authored front convention is +Z after conversion.
- metallicRoughness texture: G = roughness, B = metalness (linear); occlusion in R.
- Base color and emissive are sRGB. Normal maps are tangent-space, OpenGL (+Y up).

**Export:**
```python
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB', use_selection=True,
                          export_apply=True, export_yup=True, export_extras=True)
```
- Vertex colors export as `COLOR_0` when the material uses them.
- Compress afterwards, not in Blender (the PyPI wheel has no Draco):
  - meshopt via gltf-transform, or `gltfpack -cc -kn -km -ke`, is the default for the web;
  - Draco only when raw geometry bytes dominate;
  - KTX2 textures: ETC1S for color, UASTC for normal/ORM.
- Name things: `SM_Crate`, `MAT_Wood`, `T_Crate_BaseColor`. Never ship `Cube.027`. Collision meshes
  follow the engine convention (Godot `-col`/`-colonly` suffixes, Unreal `UCX_`).
- Validate the .blend before export too. The exporter drops loose vertices, so some defects only show
  in the source.

## 8. AI-generation pipeline (when chosen and approved)

**Decide before submitting:** default AI geometry is static organic background content with no moving
parts, sockets, grid-snapping or gameplay-critical dimensions, and a texture style compatible with the
art bible. Prefer CC0/authored assets first. Costs and the actual model/plan's rights must be approved.
Vehicles, mechanisms, controllable hero props and modular pieces use editable construction/parts.

For a deforming character, planned retopology/rigging/motion verification is an explicit exception,
not a one-shot shortcut. If the user chooses a generated articulated source, explain that segmentation
does not recover hidden mating faces or usable pivots; plan reconstruction and the same part gates.
See [tool-matrix.md](tool-matrix.md). Generator success is never final asset acceptance.

1. Make a clean concept image first: single centered subject, plain background, 3/4 view.
   Image-to-3D is more controllable than text-to-3D.
2. Generate with a face cap (10k–50k for game props, lower for low-poly modes). Turn texturing off if
   you will retexture.
3. Import it and run `inspect_model.py`. Generators output normalized sizes, so fix scale, pivot
   (base center) and normals.
4. Remesh or decimate:
   - Static props: Decimate or QuadriFlow are acceptable.
   - Deforming characters: auto-remesh loses the loops around eyes, mouth and joints, so they need
     planned retopology. Flag it to the user.
5. UV-unwrap and bake high → low (normal, AO, base color), build a PBR glTF material, validate, export.
6. Rig last, on the final topology (`animation.md`).
7. Record generator, plan and license in `assets/LICENSES.md` (`toolchain.md` §5).

Test texture lighting under opposite light directions and in the game. Painted shadows, fused parts,
missing backs/inner faces and mushy textures need repair or rejection; detail cannot rescue them.

## 9. Validate and look (every iteration)

Use the resolved local Blender executable from preflight (`blender` below stands for that path).

```bash
blender -b --factory-startup --python-exit-code 1 -P "$SKILL_DIR/scripts/blender/inspect_model.py" -- \
  assets/<id>/<id>.glb --preset web-prop --expect-height 0.9 --json assets/<id>/inspect.json
blender -b --factory-startup --python-exit-code 1 -P "$SKILL_DIR/scripts/blender/render_views.py" -- \
  assets/<id>/<id>.glb --out assets/<id>/review --scale-ref            # form: workbench (fast)
blender -b --factory-startup --python-exit-code 1 -P "$SKILL_DIR/scripts/blender/render_views.py" -- \
  assets/<id>/<id>.glb --out assets/<id>/look --engine eevee --views q_fl,q_fr   # materials
node "$SKILL_DIR/scripts/web/check_gltf.mjs" assets/<id>/<id>.glb --max-tris 3000 --max-texture 1024
```

**Open `contact_sheet.png` and look.** Correct problems in this priority order, and don't start on
materials while any of the first five fail:
1. missing or extra parts;
2. overall proportions (compare with the scale figure and the references);
3. part position, rotation and scale;
4. attachment: floating or intersecting parts;
5. silhouette readability (the black-on-white view; it must read at a glance);
6. the distinctive local shapes that make it *this* object;
7. minor detail.

Separate CLI processes run the scripts even when building live. For multi-part assets, include the
exploded `parts` view and required-name/pivot/socket checks. Material acceptance uses the actual
engine asset viewer under the art-bible lighting; Blender renders remain form evidence.

Fix one major discrepancy per iteration. Keep the last good version so a "fix" that breaks something
can be reverted. Compare the before/after sheets.

## 10. Never-list (each one has made AI-built models look bad)

| Never | Instead |
|---|---|
| Primitive soup: boxes, cylinders and spheres stacked | Profile / loft / revolve / sweep, recessed detail |
| Unexplained floating pieces inside a rigid group | Declared joins/gaps; per-group inspection; joint sweep for articulated separation |
| Coplanar overlapping faces (z-fighting) | Proud / reveal / continuous mesh (§5.4) |
| Razor edges with no bevels | Bevels sized per part + Weighted Normal |
| Guessed proportions | A dimension table and the 1.8 m scale figure render |
| Thin axis toward the camera (sword seen edge-on) | Declare the axis frame in the brief |
| Guessed pivot | Asset root base-center; moving-part pivot on its declared joint |
| Unapplied or negative scale | Apply transforms; the inspector FAILs negative scale |
| Flipped normals | `bmesh.ops.recalc_face_normals`; the inspector FAILs them |
| One flat color per part, no variation | Tonal variation, edge wear, roughness variation, or a palette atlas |
| Detail everywhere | Calm areas; clustered detail |
| Assets in different styles side by side | One style sheet: palette, bevel scale, shading, texel density |
| Exit code 0 as proof | Validator JSON + a contact sheet you opened |

## 11. Blender 4 → 5 API traps

API drift is the #1 crash cause in LLM-written Blender code. Check `bpy.app.version` and read the
installed version's API when in doubt.
- EEVEE's engine id is `BLENDER_EEVEE_NEXT` in 4.2–4.5 and `BLENDER_EEVEE` in 5.x.
- `mesh.use_auto_smooth` was removed in 4.1. Use the "Smooth by Angle" modifier or
  `bpy.ops.object.shade_auto_smooth()`.
- Principled BSDF sockets were renamed in 4.0: `Subsurface Weight`, `Specular IOR Level`,
  `Emission Color`, `Transmission Weight`, `Coat Weight`, `Sheen Weight`. Look sockets up by name and
  fail loudly if one is missing.
- Actions are slotted since 4.4 and `Action.fcurves` is gone in 5.0. Access curves through the
  action's layers/strips/channelbags, or keyframe with `keyframe_insert`.
- `Material.use_nodes` is deprecated in 5.x, where materials always have a node tree. Guard with
  `if mat.node_tree is None: mat.use_nodes = True`.
- In the PyPI `bpy` module, `import bpy` must come before `bmesh` and `mathutils`.
- `BMVertSeq` step-slicing (`bm.verts[::2]`) fails on 4.5. Use `list(bm.verts)[::2]`.
- `bpy.ops` in background mode needs a context. Use `with bpy.context.temp_override(...)`, or prefer
  the data API and `bmesh.ops`.
