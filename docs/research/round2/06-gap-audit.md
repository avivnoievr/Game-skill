# 06 — Gap audit of plugins/game-studio (Round 2, Agent 6)

Scope: every file in `plugins/game-studio/` was read in full (SKILL.md, 8 references + 3 engine files,
9 templates, 4 agents, script docstrings + key code paths). Paths below are relative to
`plugins/game-studio/skills/game-studio/` unless they start with `agents/`. Line numbers are from the
current tree. Severity = impact on final game quality. [judgment] = my opinion; [verified] = source opened.

## 1. Summary

- **The skill tells the agent WHAT good looks like, almost never WITH WHICH CODE.** It names profile/loft/
  revolve/sweep/inset (modeling.md:92-101) but ships no helper for any of them, while admitting API drift is
  the #1 crash cause (modeling.md:279). Every builder writes raw bpy from zero → crashes, style drift between
  parallel builders, and the "primitive soup" fallback the user complains about. **Critical.**
- **Nothing about moving parts, hierarchies, pivots per part, or sockets.** modeling.md:74 even says "join
  parts by material". A vehicle with separate wheels, a door on a hinge, a weapon with a muzzle point have no
  procedure and no validator check. This is the user's exact complaint (fused models). **Critical.**
- **AI image-to-3D is presented as "generate → cleanup" (modeling.md:218-232) with no warning** that the
  output is one fused mesh with baked, mushy texture and no parts/pivots. A live Blender MCP puts
  `generate_3d` one call away [verified: ahujasid README]. **Critical.**
- **The skill is written for a cloud container, the users work on desktops.** No preflight finds the
  installed Blender (macOS/Windows never put it on PATH), so SKILL.md:165 / asset-builder.md:44-45 push the
  agent into a 400 MB `pip install bpy` instead. There is no procedure for using a live Blender MCP, only
  install lines (toolchain.md:92-111). **Critical.**
- **The recommended default style (palette low-poly, art-direction.md:34) has no implementation**: no
  palette-atlas maker, no UV-to-swatch, no vertex-color/AO helper, no bake recipe. **High.**
- **No asset recipes** for vehicle, modular kit, CC0 character, weapon, environment set. **High.**
- **Design-sense skills are never loaded.** No step invokes `frontend-design`/`canvas-design` [verified to
  exist], and the art bible gets "APPROVED" as prose, with no mood board or reference images. **High.**
- **Whole disciplines are missing:** audio (6 passing mentions), level design/greybox metrics, UX/menus/
  onboarding, accessibility beyond colorblind + shake, LODs/collision procedures, binary version control,
  release/export. **High/Medium.**
- **Workflow holes:** web-only verify.sh run every session (SKILL.md:133); assets approved under Blender
  "Standard" studio renders, not the game look; G6 has no tool; style-sheet bevel contradicts per-part rule.
- Negative results: `${CLAUDE_SKILL_DIR}` is a documented substitution (docs/research/01:219), budgets.json
  presets all exist in inspect_model.py, and the ahujasid install command in toolchain.md:97 is current
  [verified]. Those are not gaps.

## 2. Ranked gaps with fixes

### CRITICAL

**C1. No tested bpy helper library.** Evidence: modeling.md:79-86 (write build.py), :92-101 (ops table with no
code), :193-194 (smart_project "works headless using temp_override", but no snippet), :277-294 (API traps);
asset-builder.md:43-52. The three parallel builders (SKILL.md:67) each invent different helpers, so bevel
widths, materials and naming drift apart.
*Fix:* ship `scripts/blender/gs_build.py`, tested headless on Blender 4.2 LTS, 4.5 LTS and 5.x (the version
probe is already in gs_common), plus `templates/build.py` (argparse, seed, `clear_prefix`, `build(out)`,
JSON summary, callable both headless and via a live MCP). Minimum API (each returns an object and fails
loudly):
```
reset_scene(prefix) · profile_extrude(pts2d, depth, axis) · revolve(profile, segments, axis)   # welds poles
loft(rings, close) · sweep(profile, path, twist=0, taper=None) · inset_recess(obj, faces, inset, depth)
cut_opening(obj, profile, depth)  # ring topology, no dense boolean · boolean_safe(obj, cutter, op)  # EXACT + revert
bevel(obj, width_m, segments, angle=30, harden=True) · weighted_normal(obj) · apply_transforms(obj)
set_origin(obj, 'base'|'center'|Vec3) · pivot_empty(name, loc, parent)  # sockets/pivots as glTF nodes
mat_palette(name, hex, rough, metal)  # sockets by name, 4.x/5.x safe · vcol_ao(obj)  # COLOR_0
uv_smart(obj, 66, 0.02) · uv_to_palette_cell(obj, slot, atlas, cell) · bake_to_image(obj, type, size)
join_by_material(objs, keep_separate=[...]) · export_glb(root, path)  # apply, yup, extras
```
Add a one-paragraph rule to modeling.md §4: "Build with `gs_build`; raw `bpy.ops` only when no helper exists,
and then add the helper." [judgment]

**C2. No hierarchy, moving-part, pivot or socket rules.** Evidence: modeling.md:55-56 (one pivot rule for the
whole asset), :72-76 ("join parts by material"), :213 (naming only); inspect_model.py has no node or per-part
pivot checks (it reports per mesh only; grep shows no hierarchy/socket logic). render_views renders the asset
as one block.
*Fix:* add modeling.md §5.6 "Parts that move":
- Anything that rotates, opens, detaches, is swapped or is animated by code stays a **separate node**. Its
  origin sits on the joint (wheel center, hinge line, trigger axle), with the local axis = rotation axis.
- Sockets/attachment points are empties named `SOCKET_<name>` (muzzle, grip, hand_R, exhaust, seat). They
  export as glTF nodes, and game code finds them by name, so pack with `gltfpack -kn` (toolchain.md:56 already
  warns about this).
- `join_by_material` only within one rigid part.
- Extend `inspect_model.py`: `--expect-nodes wheel_FL,wheel_FR,...`, `--node-pivot wheel_*=bbox-center`,
  `--sockets SOCKET_muzzle`. Make it FAIL if a listed node is missing or merged. Add an `--explode` view to
  render_views that offsets child nodes so the critic can see the parts.

**C3. AI generation has no "never" rules for its known failure.** Evidence: modeling.md:218-232 (pipeline
assumes cleanup fixes it), toolchain.md:113-127 (Higgsfield listed as a route); round-1 already found
"single-mesh without parts/pivots" (docs/research/02-3d-modeling.md:262). The ahujasid MCP exposes
`generate_3d`, "Premium generators are preferred automatically" [verified README §Capabilities].
*Fix:* insert at the top of modeling.md §8:
> Image/text-to-3D returns ONE fused, dense, triangulated mesh. Its texture has the lighting baked in and
> does not follow the palette, and it has no parts, pivots or sockets. Use it only for single-piece, static,
> organic props (rock, statue, food, sculpted ornament) or as a sculpt/reference base. Never use it for
> vehicles, doors, weapons, modular kits, characters with gear, or anything in §5.6. Always retexture to the
> palette (or rebake from the generated high-poly onto your own low-poly). The asset goes through the same
> gates, and the user approves the cost first.
Add the same to anti-ai-look.md §4 (process tells): "One-shot AI mesh shipped as is".

**C4. Desktop environment and live Blender MCP are not supported.** Evidence: toolchain.md:8-11 ("Scripts
first, MCP second… never required"), :148-162 (matrix framed as cloud vs. desktop), SKILL.md:152-167 and
asset-builder.md:44-45 (assume `blender` on PATH, else pip bpy). On macOS the binary is inside the .app; on
Windows it lives under Program Files and is not on PATH by default [judgment: installer defaults]. There is
no rule for the live MCP: when to use `execute_blender_code`/`look`/`get_scene_info`, how to keep build.py
the source of truth, or what to do when the user edits in the GUI.
Contradiction: toolchain.md:97 recommends `BLENDER_MCP_SAFE_MODE=1`, but safe mode blocks "reading or writing
files directly" [verified README:397]. That blocks running `build.py` from disk through the MCP.
*Fix:* add the "Session preflight" and "Live Blender protocol" in §3 (A, B) to SKILL.md (5 lines + a pointer)
and to toolchain.md.

### HIGH

**H1. Texturing and UVs are rules without procedures.** Evidence: modeling.md:179-196 (one UV call, "bake it"
with no bake steps), art-direction.md:34 (palette atlas recommended), :181 (edge wear), assets.json:9
(`palette` path but no tool makes the atlas). Also missing: trim sheets for kits, Poly Haven PBR application,
UV2 for baked lightmaps (godot.md:209 and unity.md:355 recommend lightmaps without mentioning UV2).
*Fix:* add `scripts/blender/palette_atlas.py`, which turns the art-bible hex list into an N×N PNG (each cell
padded by 2+ px to survive mip filtering), plus the `uv_to_palette_cell` and `vcol_ao` helpers (C1). Add
modeling.md §7.1 "Texturing routes" with one recipe each:
(a) palette atlas or vertex colors (default stylized);
(b) trim sheet for kits (horizontal strips, UV-snap faces to strips, uniform texel density);
(c) Poly Haven PBR: `https://api.polyhaven.com/files/<id>` lists the maps [verified]. Use `nor_gl` (OpenGL,
    which is what glTF needs) and `arm` (AO/Rough/Metal packed in R/G/B, which matches glTF's
    occlusion-R / roughness-G / metal-B), 1k–2k. UVs come from a cube or box projection at the texel density;
(d) bake procedural → image (Cycles CPU, `bake_type` DIFFUSE color-only / ROUGHNESS / NORMAL; the active
    Image Texture node is the target);
(e) lightmap UV2 when the engine bakes GI.

**H2. No recipes per asset type.** Evidence: modeling.md:33-43 routes by type but stops there. *Fix:* add
`references/recipes/{vehicle,modular-kit,character-cc0,weapon,environment-set}.md`, each ≤ 40 lines, loaded
only for that asset type so builders don't pay for all of them. Drafts are in §3 D.

**H3. Design-sense skills and visual references are missing at the start.** Evidence: SKILL.md:81-107 (no
skill invocation anywhere); art-direction.md:19-20 (directions = text + swatches); art-critic.md:63-65
(approves an art bible from prose alone); brief.md:12 asks for references as text. Anthropic's `frontend-design`
("distinctive, intentional visual design… choices that don't read as templated defaults") and `canvas-design`
exist [verified: anthropics/skills, claude-plugins-official].
*Fix:* see §3 C.

**H4. Level design, greybox and player metrics are absent.** Evidence: SKILL.md:104 and orchestration.md:99 say
"greybox core loop" with no guidance. modeling.md:53 uses real-world sizes (door 0.9 × 2.1 m), while the
art-bible template:52 example says "doors 1.4× player height", a contradiction for anything the player walks
through. There is no route for authoring levels: Blender-authored layout with empties + glTF extras, the
engine editor, or level data JSON. *Fix:* see §3 E, plus an ADR choice "level authoring route" in
architecture.md §7.

**H5. Audio is missing.** Evidence: the only mentions are animation.md:49 ("chime") and :84 ("bass in impact
sounds"), and architecture.md:33 (an `audio/` folder). Godot QA runs `--audio-driver Dummy`
(toolchain.md:74), and nothing checks sound. The scorecard (templates/scorecard.md:18-29) has no audio
category. *Fix:* add `references/audio.md` (§3 F), an art-bible "§10b Sound language", and a scorecard/QA line:
"every juice event in animation.md §3 has a sound; volume sliders exist; web audio unlocks on the first
gesture".

**H6. Getting third-party assets stalls the agent, and the license rule is too weak.** Evidence: toolchain.md:133-143
names Kenney/Quaternius/KayKit/Mixamo with no URLs and no hand-off ("use it manually"). Poly Pizza blocks
datacenter IPs. toolchain.md:169 only requires *recording* a license, not checking it is allowed.
*Fix:* (1) Procedure: "If a download needs a browser, login or itch.io, return NEEDS-DECISION / ask the user:
exact page URL, which file, and the folder to unzip into (`assets/_vendor/<pack>/`). Then verify the LICENSE
file inside the pack before use." (2) License allow/deny list (§4, item 5). (3) A Mixamo click-path for the
user (upload FBX/OBJ → auto-rig → download "FBX Binary, Without Skin, In Place" for each clip)
[UNVERIFIED wording of the Mixamo UI].

**H7. Assets are approved under the wrong look.** Evidence: render_views.py:102 and :215 force the `Standard`
view transform with studio lights. The game uses Neutral/AgX plus the art-bible recipe (threejs.md:16,
godot.md:195), and asset acceptance happens before integration (SKILL.md:104). Palette and roughness choices
that pass in Blender can fail in the game.
*Fix:* add an engine "asset viewer" shot: `?qa=1&viewer=<asset_id>` (web) or `res://qa/viewer.tscn` (Godot).
It loads one GLB into the art-bible lighting, with turntable shots at 0/90/180/270°. The material criterion of
asset acceptance (scorecard.md:66) uses that shot; Blender renders stay the evidence for form.

**H8. The QA entry point exists only for web.** Evidence: templates/verify.sh:2 ("web (Vite + TypeScript)"),
SKILL.md:131-134 (every session runs it), qa-protocol.md:262. Godot and Unity projects get no template, and
bash plus `xvfb-run` don't exist on Windows. *Fix:* `templates/verify-godot.sh` (import → GUT → shots.tscn →
image_metrics) and `verify-unity.sh`. On Windows, document Git Bash/WSL or a `verify.ps1`.

**H9. Game UX and accessibility are thin.** Evidence: features.json:8-31 (only boot and one verb);
accessibility = colorblind backups (art-direction.md:52) + reduce shake (animation.md:65); no menus, pause,
settings, onboarding or restart loop. *Fix:* template features F03–F08: title → play in ≤ 2 inputs; pause/resume; settings (volume per bus,
sensitivity, invert Y, FOV slider, reduce shake/flash, text size, remap or hold↔toggle); verbs taught in a
safe space within 60 s; death → retry ≤ 3 s; a save/progress rule. [judgment]

### MEDIUM

**M1. Collision: naming only.** Evidence: modeling.md:213-214, godot.md:216-221, unity.md:366-367. three.js has
no import convention and there is no physics-library guidance. *Fix:* build.py emits simple proxies (boxes,
convex hulls ≤ 32 verts) named `<part>-colonly` (Godot) or `UCX_<part>` (Unreal). For three.js, export them
as hidden nodes and build Rapier colliders by name [judgment]. Moving parts get their own proxies.

**M2. LOD is one line** (modeling.md:76). *Fix:* a table per engine. Godot generates mesh LODs on import
(godot.md:222, already noted). Unity LODGroup names `_LOD0/_LOD1` [UNVERIFIED exact auto-detect rule]. three.js
uses `THREE.LOD` with distances, or `gltfpack -si 0.5` for a simplified copy [UNVERIFIED flag semantics].
Rule: LOD only for assets whose screen size changes a lot. Inspect each LOD.

**M3. No version control for binaries.** Evidence: SKILL.md:40-41 (commit after every verified step); the
pipeline creates .blend, .glb, PNG renders, KTX2 and audio. *Fix:* a `templates/gitattributes` with LFS for
`*.blend *.glb *.fbx *.psd *.wav *.ogg *.ktx2 *.png *.jpg *.exr *.hdr`, plus a gitignore for `*.blend1`,
`assets/*/review/` and `qa/out/`. Commit build.py plus the final GLB; regenerate renders. Check `git lfs` is
installed in the preflight, or warn when a commit adds more than 10 MB.

**M4. G6 real-GPU performance has no tool.** Evidence: qa-protocol.md:274 names stats-gl / DevTools.
capture.mjs has `--gpu` (line 19) but no frame-time measurement. On a desktop this gate is measurable.
*Fix:* add `--frametimes N` to capture.mjs (headed, `--gpu`): sample rAF deltas for N frames during
`--hold`, report p50/p95/p99 and the GPU string (`WEBGL_debug_renderer_info`), and check them against
`budgets.json frame.p95_frame_ms`.

**M5. The style sheet contradicts the bevel rule.** assets.json:10 has a single `bevel_scale_mm: 4`;
modeling.md:115-121 says "Size bevels to the part, not one global radius". *Fix:* replace it with
`bevel_mm_by_part: {hardware:2, panel:4, casing:7, frame:13, soft:45}`.

**M6. VFX, toon, outlines, foliage wind and water are named but not implemented.** Evidence: art-direction.md:35,
:126; animation.md:51-53 (particles, dust puff). *Fix:* engine snippets in engines/*.md: one outline method (inverted hull or post), toon ramp material, pooled
billboard particles with a 4×4 flipbook, vertex-shader wind sway weighted by vertex color R.

**M7. No release or export procedure.** Evidence: SKILL.md:107 (evidence pack only). *Fix:* release
checklist: production build with the QA hook stripped (grep bundle for `__QA__`); base path for itch.io/subfolder; compressed assets; download size vs.
`budgets.delivery`; Godot export templates; one fresh-machine boot test.

**M8. MCP install for the Claude desktop app is incomplete.** Evidence: toolchain.md:96. The Blender Lab page
offers an `.mcpb` bundle for newer clients and says the server runs LLM code "without any guards… use a
virtual machine" [verified blender.org/lab/mcp-server]. *Fix:* mention `.mcpb` as the desktop install path,
copy the safety line, and map the MCP tools to tasks (§3 B).

**M9. No reference-match metric.** Vision is weak at proportions (qa-protocol.md:222-224). *Fix (optional):*
`compare_ref.py`, the IoU between the rendered front/side silhouette and a reference mask. Flag below 0.85
[judgment threshold].

### LOW

- **L1.** Budget numbers disagree: modeling.md:158 puts a small mobile prop at 100–500 tris, while inspect_model.py:44
  `mobile-prop` allows 1500. There is no `mobile-prop-medium`.
- **L2.** Repeated text costs tokens and drifts: UI timings appear in art-direction.md:211-218 and animation.md:38-40;
  the lighting recipe appears in art-direction §5 and in all three engine files; budgets appear in four places.
  Keep one source and point to it.
- **L3.** `--scale-ref` gives only a 1.8 m human. Add a 2.1 m door, or a car for vehicles and buildings.
- **L4.** SKILL.md:150: no Unreal guide; intake should warn. **L5.** Every builder reads all of modeling.md
  (asset-builder.md:27); keep recipes in separate files (H2) so it does not pass 400 lines.

## 3. Ready-to-paste additions

**A. Session preflight (SKILL.md "Every session", before step 3; desktop-first)** [judgment; paths are installer defaults]
```
0. Preflight (once per session, ≤ 5 calls; write results to qa/.game-studio-env):
   - Blender: `command -v blender`; else macOS /Applications/Blender.app/Contents/MacOS/Blender;
     Windows newest "C:\Program Files\Blender Foundation\Blender */blender.exe"; Linux ~/blender-*/blender,
     /snap/bin/blender. Probe: <bin> -b --factory-startup --python-expr "import bpy;print(bpy.app.version_string)".
     Use the user's Blender. pip bpy is only for machines with no Blender at all.
   - Live MCP: are tools like execute_blender_code / look / get_scene_info (or the Blender Lab server) loaded?
     yes → "Live Blender protocol"; no → headless only. Don't ask for an MCP install unless headless is blocked.
   - Engine + version; git-lfs present; GPU present (desktop → G6 is measurable: capture.mjs --gpu).
   - Windows: run qa/*.sh through Git Bash or WSL.
```
**B. Live Blender protocol (toolchain.md §4.1)** [sources: ahujasid README §Capabilities, :397, :792; blender.org/lab]
1. `build.py` stays the source of truth. Run it live with `execute_blender_code`:
   `import sys, importlib; sys.path.insert(0, "<abs dir>"); import build; importlib.reload(build);
   build.build("<abs out>")`. With `BLENDER_MCP_SAFE_MODE=1` file reads are blocked, so either send the
   script text inline or leave safe mode off on a trusted machine and say so.
2. Iterate with `get_scene_info` (names, transforms, origins, materials; cheap, no image). Use `look`
   (angles, solid/material) to eyeball. Gate evidence is still `render_views.py` headless: the same framing
   every time, so critics can compare.
3. Save or copy the .blend before every run (the README warns: "ALWAYS save your work").
4. The user may edit in the GUI. Read the change back with `get_scene_info` and port it into build.py before
   continuing; never leave state that only exists in the live scene.
5. `search_assets`/`import_asset`: Poly Haven only, CC0, 1k–2k (the README warns about Blender freezing
   during larger downloads). Sketchfab or Poly Pizza only after a license check. `generate_3d` falls under
   modeling.md §8 rules plus cost approval.
6. If a call has no result after ~60 s, stop and use the headless script. Never run two Blender MCPs at once.

**C. Design-sense start (SKILL.md Phase 1, first bullet)** [verified skills exist; procedure is judgment]
- If a `frontend-design` skill is listed, invoke it before writing art-bible §11 and before any HUD or menu
  code. Its job is to stop templated UI.
- If `canvas-design` is listed, use it to make a one-page PNG board per direction (palette swatches, value
  strip, 3–6 references, a silhouette row). The user picks from images, not prose.
- Build a reference board: 6–12 images (from the user, or from the web with URLs in `design/refs/README.md`;
  never shipped). Every hero asset gets a front and side reference with a dimension line.
- art-critic reviews the art bible together with the boards (art-critic.md §8).

**D. Asset recipes (references/recipes/*.md)** [dimensions: real-world typical values; budgets from modeling.md §6; rest judgment]
- *Vehicle.* Root empty `VH_<id>` (origin on the ground, centered between axles). `body` lofted from 4–6
  side-profile sections, wheel wells cut in (≥ 3 cm clearance). `wheel_FL/FR/RL/RR`: revolved tire profile
  (16–24 segments web) + inset rim, origin at wheel center, local X = axle. `steer_FL/FR` empties parent the
  front wheels; `door_L/R` origin on the hinge line; sockets `SOCKET_seat/exhaust/light_*`; collision
  `body-convcolonly`. Compact car ≈ 4.2–4.6 × 1.8 × 1.45 m, wheel Ø 0.6–0.7 m, wheelbase ≈ 2.6 m. Never join
  wheels to the body; validate with `--expect-nodes wheel_FL,wheel_FR,wheel_RL,wheel_RR`.
- *Modular kit.* Grid 2 m (interiors) or 4 m (exteriors); walls 3 m high (4 m for third-person), 0.2–0.3 m
  thick; pivot at the module corner on the floor; vertices snapped to 1 mm. Pieces: wall, wall_door (opening
  ≥ 1.2 × 2.4 m for a third-person camera), wall_window, corner_in/out, floor, floor_edge, stairs, pillar,
  roof, trim. One trim sheet or palette atlas per kit. Gate: an L-shaped test room rendered top + 3/4: no
  gaps, no z-fighting, uniform texel density.
- *Character from a CC0 pack.* One pack family for the whole cast; check the LICENSE inside it; the user
  downloads into `assets/_vendor/`. Run `inspect_model` + `clip_report` and list clips against the design.
  Normalize to the art-bible height; recolor by swapping the atlas texture; weapons attach to `hand_R` in the
  engine; retarget only within the same skeleton.
- *Weapon.* Origin at the grip (where the hand closes); declare the axis frame (blade/barrel along forward).
  Sockets `SOCKET_muzzle`, `SOCKET_offhand`; magazine or other animated part = its own node. Blade 0.7–0.9 m;
  first-person = hero budget and 1024 px/m.
- *Environment set.* Rocks: 3–5 bases (subdivided icosphere + seeded noise displacement, decimated, vertex
  AO). Trees: trunk swept along a seeded curve with taper (r 0.15–0.4 m), 2–3 levels of branch recursion,
  canopy of 3–7 displaced low-subdivision blobs with a palette gradient, 300–1,500 tris (web). Ground:
  heightfield + vertex-color splat. Placement: seeded Poisson-disk scatter; variants instanced, never merged.

**E. Level and greybox metrics (references/level-design.md)** [judgment: common third-person practice; tune in greybox]
- Player capsule 1.8 m, radius 0.3–0.4 m. Corridors ≥ 2.5–3 m (third-person) / ≥ 1.5–2 m (first-person);
  ceilings ≥ 3 m (third-person); doors ≥ 1.2 × 2.4 m. Step ≤ 0.3–0.35 m; walkable slope ≤ 40–45°.
- Jump apex lives in config. Ledges below apex − 0.2 m are jumpable, above apex + 0.3 m clearly not; no
  ambiguous heights between. Cover: low 1.0 m, high ≥ 1.8 m.
- Greybox: one grey material with a 1 m checker so scale reads. No final art until the scripted critical-path
  run passes and the loop is fun at greybox. A landmark is visible from the start; a rest beat every 30–60 s.
- "Gameplay metrics override real-world dimensions for anything the player traverses" (resolves the
  modeling.md:53 vs. art-bible.md:52 conflict).

**F. Audio minimum (references/audio.md)** [judgment unless marked]
- Sources: Kenney audio packs (CC0), freesound.org filtered to CC0, jsfxr/sfxr for generated SFX; each in
  LICENSES.md. Buses master/music/sfx/ui with settings sliders. 3–5 variants and ±5–10% pitch on repeated
  sounds (seeded in QA). Spatial: three.js `PositionalAudio`, Godot `AudioStreamPlayer3D`. Web: resume the
  `AudioContext` on the first user gesture (autoplay policy). Music ducks under big events; nothing clips.
- QA: every juice event (animation.md §3) maps to a sound id; captures run with audio enabled where possible.

## 4. "Never do" list (to add; each closes a gap above)

1. Never use one-shot image/text-to-3D for anything with moving, separable or swappable parts. The output is one
   fused mesh with no pivots (docs/research/02:262; the user's Higgsfield result).
2. Never keep a generator's texture as final. It has baked lighting, is mushy and is off-palette. Retexture or rebake.
3. Never call `generate_3d` (live Blender MCP or Higgsfield) without a cost preflight and the user's OK
   (the ahujasid MCP prefers premium generators automatically).
4. Never join moving parts into one mesh, and never put a moving part's pivot anywhere except its joint (C2).
5. Never import an asset whose license is not on the allow-list. Allowed: CC0; CC-BY with attribution text
   recorded; purchased with the license file kept; user-made. Denied: CC-BY-NC in a commercial game; ND if
   modified; "editorial"; unknown; ripped game assets; AI likenesses of trademarked characters.
6. Never leave a change that exists only in the live Blender scene. build.py is the source of truth (C4/B).
7. Never accept materials from Blender's Standard/studio render alone. Accept them in the engine viewer under
   the art-bible look (H7).
8. Never size traversable spaces from real-world dimensions alone. Use the gameplay metrics (§3 E).
9. Never mix characters from different packs, or code-built heroes with pack heroes, in one cast.
10. Never commit .blend, .glb or audio binaries without LFS, and never commit regenerable review renders (M3).
11. Never ship a silent game, or one with placeholder bleeps, without logging it in progress.md as a known defect.
12. Never install `pip bpy` on a machine that already has Blender. Find the binary first (A).

## 5. Gaps I could not close / unverified

- Exact Windows/macOS Blender paths are installer defaults [judgment], not tested on those OSes here.
- Unity LOD auto-naming and the semantics of the `gltfpack -si` flag are [UNVERIFIED].
- Mixamo UI wording is [UNVERIFIED]. Unity CharacterController defaults could not be read: the docs page
  loaded but the value was not in the extracted text.
- Godot's handling of glTF `COLOR_0` as albedo on import was not checked [UNVERIFIED]. Verify it before
  recommending vertex colors for Godot.
- The level metrics, audio numbers and recipe numbers are practitioner heuristics [judgment]. Treat them as
  greybox starting points, not facts.
- I did not run the bundled scripts. The audit is of text and code, not behavior.

## 6. Sources (opened this session)

- Plugin files: all files under /home/user/Game-skill/plugins/game-studio/ (line refs above).
- Round-1: /home/user/Game-skill/docs/research/02-3d-modeling.md:257-293; 05-mcp-tools.md:1-60; 01-ecosystem-orchestration.md:219.
- ahujasid MCP README: https://raw.githubusercontent.com/ahujasid/blender-mcp/main/README.md (lines 7-8, 38-41, 105, 126,
  632-642 tool list, 357/397 safe mode, 777-778 Poly Haven freeze / Poly Pizza Cloudflare, 792, 810).
- Blender Lab MCP page: https://www.blender.org/lab/mcp-server/ (Blender 5.1, add-on + server, .mcpb bundle, "without any guards").
- Anthropic skills: https://raw.githubusercontent.com/anthropics/skills/main/skills/{frontend-design,canvas-design,algorithmic-art,theme-factory}/SKILL.md (HTTP 200);
  https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/plugins/frontend-design/skills/frontend-design/SKILL.md (200).
- Poly Haven API: https://api.polyhaven.com/files/rocky_terrain_02 (keys incl. nor_gl, arm, gltf); https://api.polyhaven.com/assets?type=hdris (997 HDRIs).
