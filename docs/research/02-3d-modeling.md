# 02 — Game-ready 3D modeling with an LLM agent (Research Agent 2)

Date: 2026-10-09. Environment note: only github.com (WebFetch / git clone / raw.githubusercontent), PyPI and the npm
registry were reachable. arXiv, vendor sites (meshy.ai, tripo3d.ai, hyper3d.ai), docs.blender.org, kenney.nl, polyhaven
were all blocked (DNS/403). Everything from those is marked [UNVERIFIED — search-engine summary only].
Downloads: SCRATCH/downloads/2/. Experiments: SCRATCH/tools/, SCRATCH/qa_test/.

---

## 1. Executive summary

1. **"Code runs" ≠ "good model" is now measured.** 3DCodeBench (arXiv 2606.01057, repo gaoypeng/3dcodebench, Apache-2.0):
   error-feedback / Claude Code harness lifts executability to ~0.99–1.00 but shape quality barely moves; failures are
   mostly Blender API mismatches, and *successful* renders still have disconnected/floating parts [repo read; paper
   numbers via search summary, UNVERIFIED].
2. **Richer visual access = better geometry.** 3DHarnessBench (arXiv 2609.06535, Apache-2.0) abstract: all frontier
   models recover geometry significantly better as access goes single-view → multi-view → free camera → full Blender
   interaction. Our skill must give the modeler a multi-view render loop, not one screenshot.
3. **Best existing skill content found:** `scenario-labs/skills` Blender expert family (MIT, Oct 2026; ported from
   edemaistre/blender-expert-skills) — tested on Blender 5.2.1, with `bx_audit.py` (topology metrics) and `bx_review.py`
   (Workbench silhouette/matcap/wire contact sheets). Hard-surface + retopology skills carry measured numbers. Borrow the
   *method*, write our own text.
4. **Best procedural-geometry content (Three.js route):** `scottstts/Threejs-Awesome-Graphics-Agent-Skills` (MIT):
   semantic geometry contract before vertices, bevel-radius bands per part class, segment counts by radius, join rules
   (no flush unrelated faces), coplanar/z-fight + clash audits, fixed-view visual gate.
5. **Primitive assembly has a hard ceiling** (stated by three independent sources: TheLongSilence game repo,
   RobLe3/cc-blender-skill honest README, scottstts). Fix = loft/sweep/revolve profiles + inset-recess detail + bevels +
   detail hierarchy with *calm areas*, not more primitives.
6. **Code-only modeling is credible for:** props, weapons, hard-surface, architecture/modular kits, vehicles, rocks,
   foliage via growth grammars. **Not credible for:** faces, hands, organic characters (cc-blender-skill: "sphere + nose
   + ears reads as abstract avatar"; img2threejs marks its character demos "placeholder"). Route characters to a CC0
   pack or AI generation + cleanup.
7. **AI generation output is not game-ready raw.** TRELLIS.2 (MIT, 24 GB+ GPU) default GLB export: decimation target
   1,000,000 faces, 4096 textures. Hunyuan3D 2.1 needs 29 GB VRAM for shape+texture and its license *excludes EU, UK,
   South Korea*. SF3D/SPAR3D: Stability Community License (<$1M revenue). Commercial services need remesh/decimate,
   re-UV/bake, pivot/scale fix every time.
8. **Cohesive CC0 packs are often the honest best answer** (KayKit, Kenney, Quaternius, Poly Haven): KayKit packs are
   CC0, modular, single 1024² gradient atlas downsamplable to 128² (README verified).
9. **Validation must be numeric AND visual** — a real case: an interference gate passed a ladder whose rungs floated
   (kai-chop/blender-industrial-kit). img2threejs: silhouette IoU "scored a deleted face identically to a finished one".
10. **Our experiment:** a ~330-line headless validator (bpy wheel) ran on Blender **5.2.2**; Workbench contact-sheet
    rendering worked on a GPU-less Linux container (EGL warnings, PNGs written). It caught planted defects (loose verts,
    flipped winding, no UVs, unapplied scale, below-ground pivot, floating part, size mismatch). Two traps found:
    **re-imported GLBs must be imported with vertex merging** or every UV seam reads as an open boundary; and
    `bm.verts[::step]` slicing fails on 4.5 (works on 5.2).
11. **Blender 5.x API drift is the #1 crash cause** (3DCodeBench failure taxonomy): `BLENDER_EEVEE_NEXT`, `use_auto_smooth`,
    `Action.fcurves`, `Scene.node_tree`, Principled socket renames. Ship a version-delta cheat sheet + `bpy.app.version` check.
12. **Web export:** meshopt > Draco for most web scenes (faster decode, compresses animation); KTX2 for VRAM; merge by
    material to cut draw calls (78 → ~11 draws in one game; 4,460 → 1,288 calls / p50 32.6 → 16.7 ms in another).

---

## 2. Catalog

| Name | URL | Type | Stars / last update | License | Verdict | What to borrow |
|---|---|---|---|---|---|---|
| scenario-labs/skills — Blender expert family (13 skills) | github.com/scenario-labs/skills/tree/main/skills/dcc/blender | skill set + bpy toolkits | commit 2026-10-04 | MIT | **5** | Expert loop (brief→stage→gate→fix), `bx_audit` metrics, `bx_review` contact sheets, hard-surface stack order & numbers, retopo game budgets, "what an agent reaches" honesty tables |
| scenario-labs `scenario-3d` | same repo `skills/scenario-3d` | skill (vendor MCP) | 2026-10 | MIT | 3 | Staged AI-gen chain: concept image → img-to-3D (texture off) → UV unwrap → retexture → rig last; faceBudget 10k–50k for games; check scale/pivot/normals between steps |
| scottstts/Threejs-Awesome-Graphics-Agent-Skills | github.com/scottstts/Threejs-Awesome-Graphics-Agent-Skills | skill set (24) | 2026-09-22 | MIT | **5** | `geometry-craft-workflow.md`, `geometry-quality-gates.md`, procedural architecture/vegetation contracts |
| LumosLab-Innovation/3D-lab-skills | github.com/LumosLab-Innovation/3D-lab-skills | skill set | 2 stars, 2026-09-14 | GPL-3.0 (adapts scottstts) | 2 | Nothing beyond upstream; avoid GPL text |
| czlonkowski/blender-web-3d-skill | github.com/czlonkowski/blender-web-3d-skill | plugin/skill | 3 stars, 2026-09-23 | MIT | 4 | Managed idempotent edit scripts, raw-GLB→gltf-transform pipeline + traps, draw-call consolidation, BVH orphan sweep |
| achimala/TheLongSilence `.claude/skills/blender-hardsurface` | github.com/achimala/TheLongSilence | skill inside a real game | 2026-09-03 | MIT | 4 | Loft/recess/detail-hierarchy method, bbox-derived camera, `apply scale before bevel`, join-by-material |
| kai-chop/blender-industrial-kit | github.com/kai-chop/blender-industrial-kit | skill + 3 agents + docs | 1 star, 2026-10-07 | MIT | 4 | Never-list (18 items), requirement register, engineering sheet (PARAMS/datums/BOM), two-axis verification, 5 renders incl. human-scale figure |
| RobLe3/cc-blender-skill | github.com/RobLe3/cc-blender-skill | plugin, 30 skills | 86 stars, 2026-05/10 | MIT | 3 | Honest failure renders; real-world dimension table; world reset; axis/orientation lessons. Render-oriented, not game-oriented; some export claims wrong (see §5) |
| CheshireJCat/create-3d-model-skill | github.com/CheshireJCat/create-3d-model-skill | repackage of RobLe3 | 2026-07 | MIT | 1 | Derivative — skip |
| img2threejs/img2threejs | github.com/img2threejs/img2threejs | skill + Python gates | 17.8k stars, 2026-10-08 | Apache-2.0 (sponsored by Tripo, Hyper3D) | 4 | Pass order blockout→structural→form→material→surface→lighting→interaction→optimization; geometric gates *before* rendering; detail inventory; chirality check; attachment declarations; one side-by-side sheet per review |
| gaoypeng/3dcodebench | github.com/gaoypeng/3dcodebench | benchmark | 2026-06-01 | Apache-2.0 | 4 (evidence) | `blender_5_api_reference.txt` (tested API drift list), failure taxonomy, visual-critique prompt with priority order |
| llada60/3DHarnessBench | github.com/llada60/3DHarnessBench | benchmark | 2026-09-26 | Apache-2.0 | 4 (evidence) | Correction priority order; "don't stop at rough approximation"; multi-view inspection list |
| threedle/ll3m (LL3M) | github.com/threedle/ll3m | client of multi-agent Blender system | 554 stars | Demo license, **non-commercial**, outputs CC-BY | 2 | Concept only (plan/retrieve/write/debug/critique + 5-view renders); server discontinued (Sonnet 3.7 retired) |
| ahujasid/blender-mcp | github.com/ahujasid/blender-mcp | MCP | 2026-10-06 | MIT | n/a (Agent 5) | — |
| microsoft/TRELLIS.2 | github.com/microsoft/TRELLIS.2 | open image-to-3D (4B) | — | MIT (deps nvdiffrast/nvdiffrec own licenses) | 3 | Local gen if 24 GB GPU; open surfaces; must decimate |
| Tencent-Hunyuan/Hunyuan3D-2.1 | github.com/Tencent-Hunyuan/Hunyuan3D-2.1 | open image-to-3D + PBR paint | 4.1k stars | Tencent Hunyuan Community License (not EU/UK/KR; >1M MAU needs license) | 2 | Avoid for EU/UK users |
| Stability-AI/stable-fast-3d, stable-point-aware-3d | github.com/Stability-AI/... | fast image-to-3D, UV-unwrapped, remesh option | — | Stability Community License (<$1M revenue, attribution) | 3 | Fast low-cost props; built-in UV unwrap, `--remesh_option quad/triangle`, target vertex count |
| VAST-AI-Research/TripoSG | github.com/VAST-AI-Research/TripoSG | open image-to-shape (no texture) | 1.8k | MIT | 3 | `--faces 5000` face cap; 8 GB VRAM |
| KayKit packs | github.com/KayKit-Game-Assets/* | CC0 asset packs | — | CC0 (LICENSE.txt read) | 5 for stylized low-poly | Modular kits + single gradient atlas |
| Kenney starter kits | github.com/KenneyNL/Starter-Kit-3D-Platformer etc. | code MIT, assets CC0 | 1.2k+ | MIT / CC0 | 5 | CC0 low-poly kits |
| Meshy / Tripo / Rodin | (vendor sites blocked) | paid services | — | see §3.6 | 3 | [UNVERIFIED] |

Negative results: no existing skill covers *game-ready* modeling end-to-end with platform budgets, LODs, collision
naming and glTF validation; most "Blender skills" (majiayu000 registry, major-ai-skills, TerminalSkills) are thin API
summaries — not opened in depth after sampling search listings. LL3M paper text and BlenderGym results unreadable (arXiv blocked).

---

## 3. Distilled guidance

### 3.1 Sourcing decision tree (opinion built from §2 evidence)

```
Asset needed
├─ Character / creature / face / hands / cloth?
│   ├─ stylized low-poly ok → CC0 rigged pack (KayKit, Quaternius, Kenney) → recolor/kitbash   [best]
│   └─ unique design → concept image → AI gen (quad/low-poly mode) → retopo/decimate → UV/bake → rig → validate
│      Code-only: NO (only a blockout/placeholder; say so to the user)
├─ Environment kit (walls, floors, dungeon, city, modular) → CC0 kit if style fits; else code (bmesh/GN) on a grid
├─ Hard-surface prop / weapon / vehicle / machine / furniture → code modeling (profiles + bevels + recess), Blender
├─ Natural: rocks → code (subdivided/displaced, decimated, vertex-color AO); trees/grass → growth grammar
│   (species table) or CC0; terrain → heightfield code
├─ Hero organic prop with complex surface (statue, food, sculpted ornament) → AI gen + cleanup, or CC0 scan (Poly Haven)
└─ Textures/materials → Poly Haven / ambientCG CC0 PBR, or vertex colors / gradient atlas for stylized
Rule: ONE art-style per game. Never mix a CC0 pack style with AI-gen realism without a unifying pass
(shared palette atlas, same bevel scale, same shading model).
```

### 3.2 Code-modeling pipeline (Blender headless; works for Three.js with equivalent ops)

0. **Brief in numbers before any vertex** [scenario expert loop; kai-chop engineering sheet; scottstts contract]:
   purpose (game/platform), tri budget, texture budget, style, real-world size (metres), axis frame, pivot, part list
   (BOM) with parent and process ("extrusion", "casting"), joins (contact / reveal / proud / penetration), views to check.
1. **Real dimensions from a table**, never guessed (cc-blender-skill v0.6 sword went "thin pole" until dimensions + broad-axis orientation fixed).
2. **Blockout** at real scale; render silhouette sheet; check proportions next to a 1.7–1.8 m human-scale box
   [kai-chop `view_scale` figure; scenario hard-surface step 1].
3. **Primary forms by the operation that owns them** [scottstts table]: constant section → extrude/prism; changing
   section → loft over rings; axial → revolve (weld poles); rails/pipes → sweep; openings → direct ring topology
   (frame with inner/outer rings) before booleans; hollow → solidify with explicit thickness.
4. **Detail by recess, not glue** [TheLongSilence]: `bmesh.ops.inset_region` + translate along `-normal`; greebles at
   ~1/60 of object length, clustered; leave calm areas ("detail only registers against something undetailed").
5. **Edges**: every manufactured edge gets a bevel sized to the part, not one global radius [scottstts bands:
   hardware 2 mm, panel/slat 4 mm, carcass/plinth 7 mm, frame/machine body 13 mm, soft upholstered 45 mm]. Game mid-poly:
   bevel 1–2 segments + Harden Normals + Weighted Normal (keep sharp) [scenario]. Apply scale BEFORE bevel (scaled object
   = "pillows") [TheLongSilence, scenario].
6. **Stack order** [scenario, verified 5.2.1]: Mirror(late, above WN) … Boolean cuts → angle-limited micro Bevel
   (30°, Harden Normals, Miter Outer Arc) → Weighted Normal last → (game) Triangulate keeping custom normals.
   Booleans: solver `EXACT` default; `FLOAT` only to diagnose (scenario) — but 3DCodeBench reports EXACT DIFFERENCE
   destroying *voxel-remeshed* meshes: check vertex count before/after every boolean and revert if < 50 %.
7. **Segment budget by radius** [scottstts]: r ≤ 25 mm → 10–14 segs; ≤ 100 mm → 16–24; ≥ 150 mm player-adjacent → 28–48.
   Spend tris on silhouette, apertures, edge highlights, contact points — not hidden flat faces.
8. **Joins**: forbid flush unrelated faces (z-fight). Choose: one continuous mesh / declared penetration / proud part
   ≥ 0.8 mm / reveal 1.5–6 mm (≥ 4 mm to read at 2 m) [scottstts]. Hidden overlap 5–15 mm at static joins is acceptable
   for props (cc-blender-skill) — a collar/grommet at intersections reads better [scenario/du Mont].
9. **Materials**: Principled BSDF only for glTF; procedural nodes do NOT export — bake to textures or use vertex
   colors/gradient atlas [czlonkowski, TheLongSilence]. Cheap realism: per-part tonal variation (Voronoi 0.9–1.1 ×
   base), edge wear on convex edges (Pointiness is Cycles-only → bake it) [TheLongSilence].
10. **UV**: `bpy.ops.uv.smart_project(angle_limit≈66°, island_margin 0.02)` worked headless in our test (with
    `temp_override` + edit mode). Every hard edge = UV seam for normal-mapped assets [scenario retopo]. Image-textured
    material with no UV layer exports broken UVs [czlonkowski].
11. **Game version**: join by material (one object ≈ one draw per material) [TheLongSilence 78→~11 draws]; origin at
    base-centre (ground contact z = 0) for props; triangulate deterministically if normal-mapped; LOD by dropping every
    second bevel segment (Ryuu: 7,266 → 4,166 tris on a panel) [scenario].
12. **Gate** (§3.5) → fix → re-gate. Never report done without opening the renders.

Managed-script pattern [czlonkowski]: copy-forward versioned .blend, idempotent script with a version marker,
tag created objects `obj["managed"]=True`, remove-then-rebuild by name prefix, print one JSON report.

### 3.3 AI-generation pipeline (when chosen)

1. Generate a **clean concept image** first (single centered subject, plain background, orthographic-ish 3/4) —
   scenario-3d: image-to-3D is more controllable than text-to-3D.
2. Generate geometry with face cap (10k–50k game props [scenario-3d]; TripoSG `--faces 5000`; SF3D/SPAR3D
   `--remesh_option quad|triangle` + target count). Texture off if you will re-texture.
3. Import into Blender → audit (`bx_audit`-style) → fix normals/scale/pivot (generators output unit-normalized
   size; Tripo-style `autoSize` puts metres in node scale [scenario-3d]).
4. Remesh/decimate: static props → QuadriFlow or Decimate is acceptable; deforming characters → auto-remesh lacks
   loops around eyes/mouth/joints (scenario sheep test: QuadriFlow 0 eye/mouth rings, torn ear) → manual/planned retopo.
5. UV unwrap + bake high→low (normal, AO, base color) → PBR glTF material → validate → export.
6. Rig last, on shipping topology.

### 3.4 Numeric budgets (sourced where marked; [H] = heuristic/opinion, not from a primary source)

| Item | Value | Source |
|---|---|---|
| Hard-surface game asset | 15k tris, one 2K map, animated/breakable parts separate | Augusto BCON23 via scenario hard-surface |
| Game character | < 10k tris; head 2–3k, both hands ~1k, body 5–6k | scenario retopology (SpeedChar) |
| AI-gen game-ready prop | 10k–50k faces cap | scenario-3d |
| Stylized low-poly prop (KayKit-class) | few hundred–few thousand tris, 1 gradient atlas 1024² (→128² ok) | KayKit README (atlas); tri range [H] |
| Web scene reference | demo: 25 objects, ~33k tris, 69 draw calls, 332 KB GLB | czlonkowski |
| Draw calls, WebGL | desktop 2,000–5,000; mobile browser 200–500 | [UNVERIFIED blog via search] |
| Texel density | 512 px/m third-person; 1024 px/m first-person/hero; 256–512 mobile | [UNVERIFIED — Polycount forum/blogs via search; consistency matters more than value] |
| Texture sizes [H] | props 512–1K, hero 2K, mobile ≤1K; power-of-two (glTF-Validator warns on NPOT) | validator README (NPOT); sizes [H] |
| Units / axes | 1 unit = 1 m; glTF +Y up, asset front faces +Z, right-handed | glTF 2.0 spec §Coordinate System |
| Bevel widths | see §3.2 bands; micro bevel ≈ 0.5 % of largest dimension when unknown | scottstts; scenario |
| Features vs bevel | every wall/groove/step > 2× micro-bevel width or Clamp Overlap shrinks the whole object's bevel | scenario [verified 5.2.1] |
| Join floors | proud ≥ 0.8 mm; reveal 1.5–6 mm; gap readable at 2 m ≥ 4 mm | scottstts |
| Floating tolerance | island touching nothing within 2 mm = defect unless declared | our validator [H] |

### 3.5 PBR / glTF / export rules (primary: glTF spec, Blender glTF-IO docs, gltfpack & glTF-Transform READMEs)

- metallicRoughness texture: **G = roughness, B = metalness**, linear; occlusion in **R**; base color & emissive sRGB;
  normal maps tangent-space **+Y up (OpenGL)**; tangents default to MikkTSpace if absent. `COLOR_0` multiplies base color.
- Blender exporter: `bpy.ops.export_scene.gltf(filepath, export_format='GLB', use_selection=True, export_apply=True,
  export_yup=True)` (+ `export_gpu_instances=True` for linked duplicates). Vertex colors export as `COLOR_0` only when
  used in the material by default ("Use Vertex Color: Material"). AO needs a `glTF Material Output` group node.
  Blender 5.x also offers native meshopt (`EXT_`/`KHR_meshopt_compression`).
- Compression: **meshopt** (gltfpack `-cc`, or `gltf-transform meshopt`) default for web; Draco only when raw geometry
  bytes dominate (static scans) [czlonkowski]. gltfpack does **not** read Draco input; npm gltfpack lacks texture
  compression — use native binary for `-tc` (KTX2/Basis) [gltfpack README]. KTX2: ETC1S color, UASTC normals/ORM
  (`gltf-transform uastc --slots "{normalTexture,occlusionTexture,metallicRoughnessTexture}"`, `gltf-transform etc1s`).
- gltfpack keeps names only with `-kn` (nodes) / `-km` (materials); gltf-transform `flatten()` kills JS-driven pivots,
  `palette()` merges materials, `instance()` is skipped when the file has animation [czlonkowski].
- Validate: `gltf_validator model.glb` (non-zero exit on errors; NPOT warnings) — npm `gltf-validator` latest
  2.0.0-dev.3.10 (2024-10-22); `gltf-transform inspect/validate`; gltf-transform 4.5.1 (2026-09-28), gltfpack 1.3.0
  (2026-09-25) per npm registry. **Installed in SCRATCH/tools/node but NOT run** (stopped for cost).
- Collision/naming: engine-specific suffixes (Godot `-col`/`-colonly`, Unreal `UCX_`) [UNVERIFIED — docs not fetched].
  Naming prefixes `SM_` (static mesh), `MAT_`, `T_` [H]; never ship `Cube.027`.

### 3.6 AI service facts (all [UNVERIFIED — vendor pages blocked; search summaries, sources conflict])

- Meshy: free 100 credits/month; free-plan outputs CC BY 4.0 (public, attribution); paid = private + commercial;
  Meshy 6 ~20 credits/gen; remesh/rig 0 credits. An independent test reported ~3M-poly raw output → 100k quads / 30k tris after its remesh, losing detail.
- Tripo: free tier **not** for commercial use; Pro ~$19.9/mo; quad/triangle modes, "Smart Low Poly".
- Rodin (Hyper3D): credits charged on download; quad default (18k/50k tiers); API quad 1k–200k faces.
- Hunyuan 3.0/3.1 hosted only (no confirmed open weights); open 2.1 has the territory exclusion above (verified).

### 3.7 Validation — key bpy calls (tested on bpy 5.2.2; partially on 4.5.14)

```python
dg = bpy.context.evaluated_depsgraph_get(); eo = obj.evaluated_get(dg); me = eo.to_mesh()
bm = bmesh.new(); bm.from_mesh(me); eo.to_mesh_clear(); bm.transform(obj.matrix_world)  # world metres
tris = sum(len(f.verts)-2 for f in bm.faces)
non_manifold = sum(1 for e in bm.edges if not e.is_manifold and not e.is_boundary)
boundary = sum(1 for e in bm.edges if e.is_boundary); loose_v = sum(1 for v in bm.verts if not v.link_edges)
loose_e = sum(1 for e in bm.edges if not e.link_faces); zero = sum(1 for f in bm.faces if f.calc_area() < 1e-10)
ngons = sum(1 for f in bm.faces if len(f.verts) > 4)
flipped = sum(1 for e in bm.edges if len(e.link_faces)==2 and e.link_loops[0].vert == e.link_loops[1].vert)
# inward normals: closed mesh with signed volume < 0 (sum v0·(vi×vi+1)/6)
# islands: union-find over edges; floating = island with no BVHTree.overlap / find_nearest(co, 0.002) to others
# transforms: obj.scale != 1, obj.matrix_world.determinant() < 0 (negative scale flips normals)
# UV: me.uv_layers empty → fail; rasterize loop_triangles UVs on a grid to estimate overlap & out-of-0..1
# size/pivot: world bbox from eo.bound_box; lowest z ≈ 0 for ground props; dims vs expected ±20 %
```
Review sheet (approach of scenario `bx_review.py`, re-implemented by us): Workbench engine; modes silhouette
(`shading.light='FLAT'`, black on white), matcap (`studio_light='clay_studio.exr'`), normal check
(`check_normal+y.exr` + backface culling so flipped faces show as holes), material/studio; views front/right/back
(ortho) + 3/4 (50 mm persp) + top; camera distance from bbox; tile PNGs with numpy into one sheet the agent opens.
Headless run: `blender -b --factory-startup --python-exit-code 1 -P validate.py -- args` (without
`--python-exit-code` a failing script exits 0; without `--factory-startup` user add-ons load) [scenario expert].

---

## 4. Failure modes & anti-patterns (evidence → countermeasure)

| Failure | Evidence | Countermeasure |
|---|---|---|
| Primitive soup (box+cylinder+sphere) | TheLongSilence "hard ceiling"; cc-blender chair "6 rectangles… printed plastic wrap", final "still an ugly designed chair"; scottstts | Profile/loft/revolve/sweep owners; recess detail; big→medium→small; reject in visual gate "primitive-assembled" |
| Floating / disconnected parts | 3DCodeBench abstract; kai-chop ladder rungs; czlonkowski "floating greebles read as bugs" | Declared joins per part; BVH island contact check; side-ortho render |
| Interpenetration / z-fight | scottstts coplanar audit; kai-chop never-list #1–2 | Proud/reveal offsets; coplanar audit after merging by material |
| No bevels → cheap CG | kai-chop never-list #6; scenario "every hard edge catches light" | Bevel bands per part, Harden Normals + WN |
| Wrong proportions / scale | cc-blender sword attempts 4–6 | Dimension table + human-scale figure render + `--expect-size` gate |
| Wrong orientation (thin axis to camera) | cc-blender sword "thin pole" | Contract states axis frame; glTF front = +Z |
| Wrong pivot / below ground | our bad crate z = −0.3 m | Origin at base centre; gate lowest z |
| Unapplied scale → uneven bevels / export surprises | TheLongSilence "pillows"; scenario rubric #1 | `transform_apply(scale=True)` before modifiers; gate scale = 1 |
| Broken normals (flipped, smoothed hard edges, smear) | scenario triage table; czlonkowski "mirrored cubes have inward normals" | `bmesh.ops.recalc_face_normals`; WN last; normal-matcap + backface-cull render |
| Flat untextured materials | cc-blender "materials look flat" | Tonal variation, edge wear baked, roughness variation; or palette atlas |
| Over-detail / noise | TheLongSilence "greebled every face read as noise" | Calm zones; detail clusters aligned to neighbours |
| Inconsistent style across assets | [H] | Single style sheet: palette atlas, bevel scale, shading model, texel density |
| API-drift crashes | 3DCodeBench taxonomy (B5-API, BMSH, CTX) | Version check + 4→5 delta sheet; prefer `bmesh.ops` / data API over `bpy.ops.mesh.*` headless; `temp_override` |
| Self-verification / exit-0-as-proof | kai-chop never-list #13–17 | Independent validator script; render opened; "unverified (reason)" labels |
| Single-view confidence | kai-chop #14; 3DHarnessBench | ≥ 5 views + close-ups of every join/cut |
| Regression from "fix" passes | 3DCodeBench critique prompt is deliberately biased to NEEDS_FIX: NO because rewrites break working code | Keep last-good version; compare sheets before/after; fix one largest discrepancy per iteration |

Correction priority (3DHarnessBench / 3DCodeBench, merged): missing/extra parts → global proportions → part
position/rotation/scale → attachment/floating → silhouette → distinctive local shape → minor detail. Don't start
texturing while any of the first five fail.

---

## 5. Hype vs. reality / honest gaps

- **Code-only characters**: not production quality from any source examined; img2threejs's own character demos are
  flagged "placeholder". Scenario: headless sculpting reaches "concept quality"; agent retopo reaches near-expert numbers
  but nose/upper-lip needs a human pass.
- **"Validated" skills ≠ game-ready**: cc-blender-skill is render-oriented (SubSurf level 2 everywhere, hero lighting);
  its export notes are wrong/stale ("glTF hard cap 15 MB", "no KTX2/Draco", "PNG max 1024") — do not copy.
- **AI generation**: raw output is dense, UV'd by the generator, single-mesh without parts/pivots (TRELLIS.2: "no
  parts, no pivots, no sockets" per img2threejs research note). Licenses vary wildly (Hunyuan territory exclusion,
  Stability revenue cap, Meshy free = CC BY public, Tripo free = non-commercial [UNVERIFIED]).
- **Benchmarks**: executability is solved by retry loops; geometric fidelity is not. Visual critique helps only with
  multi-view, same-angle comparison and a conservative stop rule.
- **LL3M**: interesting multi-agent design but server is gone and license is non-commercial; nothing reusable.
- **Our validator** is a prototype: floating-island logic flags *both* islands when only two exist (needs a contact-graph
  "largest component" rule); UV overlap is a coarse raster estimate; no self-intersection or texel-density check yet.

---

## 6. Recommendations for the skill

1. **Modeler subagent contract**: must emit (a) a written asset brief (purpose, budget, size, frame, pivot, BOM,
   joins, style ref), (b) a deterministic, re-runnable generator script (managed-script pattern), (c) validator JSON,
   (d) review sheet PNG that it *opened*, (e) "not verified" list. No "done" without all five.
2. **Ship our own `validate_model.py`** (start from SCRATCH/tools/validate_model.py, fix the two bugs below) + a
   `render_sheet` and a `gltf_check.sh` (`gltf_validator`, `gltf-transform inspect`, optional `gltfpack -cc -kn -km`).
   Separate QA agent runs it independently (no generator self-grading).
3. **Routing table** from §3.1 in SKILL.md; characters default to CC0 packs/AI-gen, with an explicit honesty
   statement to the user.
4. **References to write** (our text, credit sources): procedural-modeling craft (§3.2 bands/segments/joins/stack
   order), Blender 4→5 API deltas (from 3DCodeBench list + scenario 5.2 deltas), budgets table (§3.4, heuristics
   labelled), glTF/PBR/export rules (§3.5), never-list + correction priority (§4), asset-source licenses (§3.6, flagged).
5. **Style consistency**: a per-project style sheet file (palette atlas or PBR set, bevel scale, texel density,
   tri ranges per class) every asset is checked against.
6. Leave out: LL3M, cc-blender export advice, GPL text from LumosLab, any vendor price as fact.

---

## 7. Experiments run (exact)

- `uv venv -p python3.11 venv45 && uv pip install bpy==4.5.14 pillow`; `uv venv -p python3.13 venv52 && uv pip install
  bpy==5.2.2 pillow` — both import fine (`4.5.14 LTS`, `5.2.2 LTS`). PyPI bpy wheels: 4.x = cp311, 5.x = cp313,
  manylinux x86_64. **This gives an agent a pip-installable headless Blender without the GUI binary.**
- `build_test_assets.py` (bmesh `create_cube`, Bevel + WeightedNormal, `smart_project` via `temp_override`, glTF
  export Y-up/apply) ran on **both 4.5.14 and 5.2.2**. Material creation guarded: `if m.node_tree is None: m.use_nodes=True`
  (5.x: `use_nodes` deprecated). Good crate: 196 tris, 0.608×0.608×0.600 m.
- `validate_model.py` on 5.2.2: good crate → 0 problems (boundary-edge warnings were import artifacts, see below);
  bad crate .blend → detected `2 loose_verts`, `4 inconsistent_winding_edges` (one flipped face), `no UV map` ×2,
  `unapplied scale [0.6,0.6,0.6]`, `lowest point z=-0.3000 m`, floating islands, size mismatch (bbox inflated by
  loose verts). Bad crate .glb → loose verts and flipped face were *not* visible (exporter drops loose points;
  importer split all verts) — **validate the .blend before export, and import GLBs with
  `bpy.ops.import_scene.gltf(filepath=..., merge_vertices=True)`** (option exists per Blender glTF docs; not re-tested).
- **Workbench rendering headless on a GPU-less Linux container worked in 5.2.2** (prints `EGL Error 0x3009` ×3 but all
  20 PNGs + sheet written). Sheet image not visually inspected. Fallback to Cycles CPU coded but not exercised.
- On 4.5.14 the validator crashed: `TypeError: slice indices must be integers…` at `b.verts[::step]` — BMVertSeq
  step-slicing unsupported in 4.5; use `list(bm.verts)[::step]`. Rendering on 4.5 therefore untested.
- npm installed `@gltf-transform/cli@4.5.1`, `gltf-validator@2.0.0-dev.3.10`, `gltfpack@1.3.0` — not executed.

---

## 8. Sources (all opened unless marked)

Skills/repos: github.com/scenario-labs/skills (skills/dcc/blender/*, skills/scenario-3d); github.com/scottstts/Threejs-Awesome-Graphics-Agent-Skills;
github.com/LumosLab-Innovation/3D-lab-skills; github.com/czlonkowski/blender-web-3d-skill; github.com/achimala/TheLongSilence;
github.com/kai-chop/blender-industrial-kit; github.com/RobLe3/cc-blender-skill; github.com/CheshireJCat/create-3d-model-skill;
github.com/img2threejs/img2threejs (README, docs/ARCHITECTURE.md, docs/RESEARCH_TRELLIS2_TO_IMG2THREEJS.md);
github.com/gaoypeng/3dcodebench (prompts/, metrics/failure_taxonomy.py); github.com/llada60/3DHarnessBench;
github.com/threedle/ll3m; github.com/ahujasid/blender-mcp; github.com/MAX-786/claude-3d-harness, github.com/XliuXjianX/blender-production-skills (listed only).
Generators: github.com/microsoft/TRELLIS.2; Tencent-Hunyuan/Hunyuan3D-2.1 and -2 (README+LICENSE); Stability-AI/stable-fast-3d,
stable-point-aware-3d; VAST-AI-Research/TripoSG; stepfun-ai/Step1X-3D (Apache-2.0, README not analysed); wgsxm/PartCrafter (MIT, not analysed).
Assets: github.com/KayKit-Game-Assets/KayKit-Dungeon-Remastered-1.0; KenneyNL/Starter-Kit-3D-Platformer.
Standards: KhronosGroup/glTF specification/2.0/Specification.adoc; KhronosGroup/glTF-Blender-IO docs/blender_docs/scene_gltf2.rst;
zeux/meshoptimizer gltf/README.md; KhronosGroup/glTF-Validator README; donmccurdy/glTF-Transform packages/cli/README; npm registry metadata; PyPI bpy.
Search summaries only [UNVERIFIED]: arxiv.org/abs/2606.01057, 2609.06535, 2508.08228, 2504.01786; docs.meshy.ai/en/webapp/pricing;
costbench.com (Tripo, Rodin); dupple.com/reviews/rodin-ai; ufo3d.com AI tools test; help.scenario.com Hunyuan; quaternius.itch.io;
docs.polyhaven.com/en/faq; sketchfab.com license-filter blog; polycount.com texel-density threads; abratabia.com draw-call guide.
Videos: none watched (YouTube blocked); scenario skills cite timestamps from Gambrell, du Mont, Ryuu, Augusto (BCON23), rileyb3d,
PzThree, Lampel, Kaspar (BCON22) — content known only via those notes.
