# 02 — Tools and don'ts beyond Blender (Round-2 Agent 2)

Scope: which tool to use for each production job beyond basic Blender modeling, how to use it, and what
never to do. Round-1 facts already in `toolchain.md` / `05-mcp-tools.md` (Meshy/Tripo/Rodin prices, Hunyuan
territory clause, Blender MCPs, glTF/KTX2 pipeline) are not repeated, only referenced.
Evidence tags: [src N] = numbered source in §5. [judgment] = my opinion. [UNVERIFIED] = not confirmed.

## 1. Summary

1. **The user's Higgsfield result is the expected default.** No AI image-to-3D tool gives separate, pivoted,
   named parts by default. The Higgsfield `generate_3d` schema has no part, pivot, scale or delighting
   parameter, and its description says "The mesh reproduces only what is in the source image" [src 1].
2. **Part splitting exists in 2026, but only as a separate, beta, paid or research step:**
   - Tripo `/v3/mesh/segment` (v2 semantic is Beta; the doc's example result consumed 40 credits) [src 4];
   - Meshy T2 `smart-topology`, which promises "natively separated parts" at 100–15,000 faces [src 3];
   - Rodin Gen-2 / BANG, described only in promotional text [src 12];
   - Hunyuan3D-Part (the open release is "a light version") [src 6];
   - PartCrafter (research code, geometry only) [src 5].

   None of them claims pivots, hinges, naming or the hidden surfaces where parts touch.
3. **Baked lighting is a real failure mode that vendors themselves admit.** Meshy ships `remove_lighting`
   ("Removes highlights and shadows from the base color texture") [src 3]. A vendor guide describes double
   shadows under an engine sun [src 13]. Whether Higgsfield passes this flag is unknown [UNVERIFIED].
4. **AI 3D is acceptable only as static, mid-to-far, organic background filler**, or as a blockout or
   reference. It is never acceptable for anything with moving parts, sockets, kit snapping, exact
   dimensions or a stylized hero look (§2.2).
5. **For concept art, use image generation for 2D references only**, then model in Blender against reference
   empties (RNA property names verified [src 9]). The Higgsfield character-sheet workflow has a
   `turnaround / model sheet` composition and a `game-concept` style. Its default style is photoreal
   fashion, so it must be overridden [src 2].
6. **Textures:**
   - Use CC0 Poly Haven and ambientCG, fetched with a scriptable API. Poly Haven's `nor_gl` and `arm` maps
     match glTF conventions [src 14, 15].
   - For flat-color low-poly assets, use `gltf-transform palette` [src 10].
   - Bake procedural materials with `pass_filter={'COLOR'}`. DIRECT/INDIRECT bake light into the albedo
     [src 11].
7. **Rigging:**
   - Claude can drive Rigify (`object.armature_human_metarig_add`, `pose.rigify_generate`; wolf and horse
     metarigs exist) [src 16] and then export only deform bones [src 17].
   - Mixamo and Cascadeur are manual steps for the user. Cascadeur Free forbids commercial use [src 18].
8. **Audio:**
   - Higgsfield's audio tool is speech only. Its own description forbids using it for standalone SFX or
     music [src 1].
   - Use the ElevenLabs SFX API (0.5–30 s, `loop`) [src 19], CC0 packs, or Freesound filtered to CC0/CC BY
     [src 20].
   - Godot's `AudioStreamRandomizer` handles pitch and volume variation [src 21].
9. **UI assets:** game-icons.net is CC BY 3.0 and needs an exact credit line [src 22]. Fonts: check each
   family's license file. Google Fonts is not all OFL [UNVERIFIED this round].
10. **Git LFS on GitHub Free:** 10 GiB of storage and 10 GiB of bandwidth. Every push of a changed file
    counts its full size again, Actions downloads use bandwidth, and files over 100 MiB are blocked
    [src 23, 24].

## 2. Ready-to-use additions for the skill

### 2.1 Production need → tool matrix (paste into toolchain.md §7 or a new `asset-sourcing.md`)

| Need | First choice (how Claude drives it) | Fallback | Cost | Control | License note | Never |
|---|---|---|---|---|---|---|
| Hero prop, anything with moving parts, sockets, modular kit piece | Blender by script or MCP (`modeling.md`), parts as separate named objects with origins at the hinges | CC0 kit (Kenney, Quaternius, KayKit) | free | full | own work | AI image→3D |
| Static organic background filler (rocks, stumps, ruins, far statues) | CC0 first (Poly Haven models). Else, with the user's cost approval, AI image→3D: Meshy `smart-topology`/`meshy-t2` + `remove_lighting:true` + `auto_size:true`, or Tripo P-series. Then `inspect_model.py`, decimate, rescale | Blender sculpt-by-code (displace + decimate) | paid credits | low | per plan; record in LICENSES.md | as a hero asset or for exact sizes |
| Humanoid character | CC0 rigged pack, or Blender-modeled + Rigify by script | AI gen + Meshy/Higgsfield humanoid rig (paid), then planned retopology | free / paid | medium | Meshy free = CC BY | auto-remesh for a deforming hero |
| Creature rig | Rigify animal metarigs (`wolf`, `horse` ship in Rigify) [src 16] | Tripo rig types (paid, round 1) | free | high | — | Mixamo (humanoids only) |
| Animation clips | Keyframes by script (`animation.md`). Mixamo uploaded **by the user** | Cascadeur by the user (Indie licence < US$100k) | free | high | Mixamo: no redistributing raw files [src 25] | scripted Mixamo downloads |
| Mood board / concept | User refs first. Then `generate_image` (`gpt_image_2_5`) after `get_cost:true` and user OK | — | credits | medium | record the prompt and model | treating it as a model input "as is" |
| Ortho turnaround for modeling | Character-sheet workflow: `turnaround / model sheet` + `game-concept` style, 16:9 [src 2]. Crop the views, load them as reference empties (§2.3 P1) | user sketch | credits | medium | — | modeling from a single perspective image |
| Tileable PBR material | Poly Haven API / ambientCG (CC0) at 1k–2k [src 14, 15] | Blender procedural → bake (§2.3 P3) | free | high | CC0, no credit needed | AI tileables without the 3×3 tile + light test |
| Stylized flat-color props | Vertex colors, or a palette/gradient atlas (one material) | `gltf-transform palette` on solid-color materials [src 10] | free | high | — | one material per color |
| Trims / panel detail | Trim sheet baked in Blender from high-poly strips [judgment] | decals | free | high | — | unique 4k textures per prop |
| Decals (dirt, signage, damage) | Engine decals: Godot `Decal` node, Unity URP Decal Projector, three.js `DecalGeometry` [not re-verified this round] | baked into a trim | free | high | — | — |
| Particles / VFX | Engine-native: Godot `GPUParticles3D`, Unity VFX Graph / Particle System, web: `three.quarks` (MIT) [src 26] or a custom Points shader. Flipbooks rendered from Blender | CC0 particle textures | free | high | check the pack license | video-gen clips as VFX [judgment] |
| Terrain | Godot: Terrain3D (MIT) [src 26]; Unity Terrain; web: heightfield mesh by code | Blender heightfield chunks | free | high | — | AI 3D terrain |
| Vegetation scatter | Engine instancing (Godot MultiMesh, Unity Terrain details, three.js InstancedMesh) | Blender Geometry Nodes, baked placement | free | high | — | thousands of unique meshes |
| LOD | Godot import (LODs on by default, `engines/godot.md`); web: `gltf-transform weld` then `simplify` (§2.3 P5) | Blender Decimate modifier by script | free | medium | — | simplify without weld; simplify UV-seamed hero characters blind |
| Lightmaps / AO | Engine bake (Godot LightmapGI, Unity Mixed). Web: bake AO in Blender to a texture or vertex colors | — | free | high | — | baking light into albedo |
| SFX | CC0 packs → Freesound filtered to CC0/CC BY → ElevenLabs SFX API with the user's key (§2.3 P6) | user-recorded Foley | free / paid | medium | Freesound BY-NC is non-commercial | Higgsfield `generate_audio` for SFX |
| Music | User-supplied or licensed/CC0 packs | ElevenLabs music (not researched) | — | — | record it | Higgsfield `sonilo_music` standalone |
| Voice / barks | Higgsfield `generate_audio` (speech) or ElevenLabs TTS, after the user's OK | — | credits | medium | per plan | — |
| Fonts | Google Fonts family, with its license file shipped | — | free | — | OFL: bundle OK, don't sell the font alone | system/default fonts (`anti-ai-look.md`) |
| Icons | game-icons.net (CC BY 3.0, credit) [src 22]; one set only | Kenney UI (CC0, check the pack) | free | — | credit line | mixing icon sets; emoji |
| Version control | Git LFS (§2.3 P7) | — | 10 GiB free | — | — | committing binaries to plain Git |

### 2.2 Decision rule: when AI 3D generation is allowed (paste into modeling.md §8, before step 1)

**Allowed only if every one of these is true:**
- the asset is static: it has no part that moves, opens, rotates or detaches;
- it needs no sockets or attachment points (a held item, a muzzle, a seat, a door hinge);
- it is not a modular kit piece that must snap to a grid;
- it has no exact dimensions that gameplay depends on (doorways, stairs, cover height);
- its shape is irregular or organic (rocks, roots, sculpted ornaments), where Claude's primitive modeling
  is weakest;
- it is seen at mid or far distance, or is a one-off;
- its texture style fits the art bible (generators produce painterly or realistic albedo, not flat palettes);
- the user approved the cost and the license is recorded.

**Never use it for:**
- hero assets in a stylized game;
- characters that will deform, unless planned retopology follows (`modeling.md` §8);
- vehicles, weapons, chests, doors or turrets;
- kit pieces, UI or icons;
- anything the user wants "controllable".

**If the user still wants an AI asset with parts,** state the limits first:
1. Segmentation splits the surface it has. It does not invent the hidden faces where parts touched,
   because the generator never saw them. The `generate_3d` description itself says the mesh "reproduces
   only what is in the source image" [src 1, 4] [judgment on hidden faces].
2. Then use Meshy `model_type:"smart-topology"` + `ai_model:"meshy-t2"`, or Tripo `mesh/segment` v2 with
   `segmentation_granularity`.
3. In Blender: Separate by Loose Parts, then name each part, set its origin at the hinge, parent the parts,
   fill the holes, and re-bake a material per part.
4. Budget it as manual cleanup [judgment].

**Mandatory checks for every AI mesh** (in addition to `inspect_model.py`):
- Render it under two opposite sun directions. Shadows painted into the texture show up as a dark side
  that does not move [src 13].
- Check the scale against the 1.8 m figure. Generators normalize size unless asked otherwise; Meshy has
  `auto_size` with the origin at the bottom [src 3].
- Check `KHR` alpha: TRELLIS.2 exports OPAQUE, and the alpha must be reconnected by hand [src 8].

### 2.3 Short correct-usage procedures

**P1. Reference sheet → Blender reference empties.** This is version-stable; the property names were
verified in `rna_object.cc` [src 9].
```python
import bpy
def ref(path, name, rot, loc, size):        # size = displayed width in metres
    img = bpy.data.images.load(path, check_existing=True)
    e = bpy.data.objects.new(name, None); bpy.context.collection.objects.link(e)
    e.empty_display_type = 'IMAGE'; e.data = img; e.empty_display_size = size
    e.rotation_euler = rot; e.location = loc
    e.empty_image_side = 'FRONT'; e.show_empty_image_only_axis_aligned = True   # shows only in its ortho view
    e.use_empty_image_alpha = True; e.color[3] = 0.5; e.hide_select = True
ref("refs/front.png", "REF_front", (1.5708, 0, 0), (0, 2, 0), 2.0)            # faces -Y (front view)
ref("refs/side.png",  "REF_side",  (1.5708, 0, 1.5708), (-2, 0, 0), 2.0)     # right view
```
- Crop every view of the sheet to the same height first. Check that the eye, belt and knee lines line up
  across views, because turnaround drift is common [src 27, judgment].
- `bpy.ops.image.import_as_mesh_planes(files=[{"name": "front.png"}], directory="refs/", shader='SHADELESS',
  size_mode='ABSOLUTE', height=1.8)` is the alternative when you need a textured plane [src 9].

**P2. CC0 PBR from Poly Haven by script** [src 14]:
1. `curl -s "https://api.polyhaven.com/assets?t=textures&c=wood"` lists assets.
2. `curl -s https://api.polyhaven.com/files/<id>` gives the URLs for each map.
3. Download `Diffuse`, `nor_gl` and `arm` at `2k` (`jpg`).
- Use `nor_gl` (OpenGL, +Y) for glTF, three.js, Godot and Unity, and `nor_dx` only for Unreal
  [knowledge; glTF spec convention].
- `arm` = AO/Rough/Metal in R/G/B, which is the glTF occlusion + metallicRoughness packing. Wire one image to
  both [judgment from channel order].
- Log the asset id in LICENSES.md, even though CC0 needs no credit.

**P3. Bake a procedural material to textures (Cycles, by script)** [src 11; operator args partly from
knowledge]:
1. UV-unwrap the mesh.
2. Add an Image Texture node with a new image (1024² for props) and make it the **active** node in every
   material slot.
3. Set `scene.render.engine='CYCLES'`.
4. Bake the color: `bpy.ops.object.bake(type='DIFFUSE', pass_filter={'COLOR'}, margin=8, use_clear=True)`.
5. Repeat with `type='ROUGHNESS'` and `type='NORMAL'` (high→low: `use_selected_to_active=True`,
   `cage_extrusion`).
6. Save with `img.filepath_raw=...; img.save()`.

- `pass_filter` must not contain `DIRECT` or `INDIRECT` for albedo, or the scene lighting is baked in. The
  enum flags NONE/EMIT/DIRECT/INDIRECT/COLOR/DIFFUSE/GLOSSY/TRANSMISSION were verified in `rna_scene.cc`.
- Bake AO separately (`type='AO'`) into the ORM red channel.

**P4. Rigify by script** [src 16, 17]:
1. Enable the add-on: `bpy.ops.preferences.addon_enable(module="rigify")`. Rigify 0.6.10 is a core add-on
   and needs Blender ≥ 4.0.
2. Add the metarig: `bpy.ops.object.armature_human_metarig_add()`. Animal metarigs (wolf, horse) are in the
   Animals category.
3. Fit the bones to the mesh by script: move the head/tail of each bone to the landmarks measured from the
   mesh bounds. Then render the front and side to check the fit.
4. Generate the rig: select the metarig and call `bpy.ops.pose.rigify_generate()`.
5. Parent the mesh with automatic weights.
6. Export glTF with `export_def_bones=True`. Use `export_hierarchy_flatten_bones=True` only if the engine
   reports non-decomposable bone matrices [src 17].

Mixamo stays a manual upload by the user (already in `animation.md`).

**P5. LOD chain for the web** [src 10]:
```bash
npx gltf-transform weld in.glb tmp.glb
npx gltf-transform simplify tmp.glb lod1.glb --ratio 0.5 --error 0.001     # 50%, max 0.1% error
npx gltf-transform simplify tmp.glb lod2.glb --ratio 0.2 --error 0.01
```
- `--error` is a fraction of the mesh radius. The defaults are `ratio 0`, `error 0.0001`.
- The simplifier stops at the error limit before it reaches the ratio, so check the tris with `inspect`.
- Add `--lock-border true` for meshes whose open edges must stay put.
- Blender alternative: a `Decimate` modifier (COLLAPSE, `ratio`) applied by script, then export.

**P6. SFX with ElevenLabs (the user's own key, after cost OK)** [src 19]:
```bash
curl -s -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" \
  -H "Content-Type: application/json" -o sfx/door_creak_01.mp3 \
  -d '{"text":"old wooden door creak, short, dry, close mic","duration_seconds":1.5,"prompt_influence":0.5}'
```
- `duration_seconds` is 0.5–30. `loop:true` works only on `eleven_text_to_sound_v2`, for ambience beds.
- Generate 3–5 variants per event.
- The free plan requires attribution, per ElevenLabs' SFX pages [search snippet, UNVERIFIED in ToS].

Implementation basics:
- One event plays a randomized pool of clips. Godot: `AudioStreamRandomizer` (`random_pitch` is a scale,
  default 1.0; `random_volume_offset_db`; per-stream `weight`) [src 21].
- Use small pitch ranges for footsteps and impacts, e.g. ±1 semitone [judgment].
- Use 3D players for world sounds (Godot `AudioStreamPlayer3D`, three.js `PositionalAudio`, Unity
  `spatialBlend=1`). UI sounds stay 2D [knowledge].

**P7. Git LFS for a game repo** [src 23, 24]:
```bash
git lfs install
git lfs track "*.blend" "*.glb" "*.fbx" "*.png" "*.jpg" "*.exr" "*.hdr" "*.ktx2" "*.wav" "*.ogg" "*.mp3" "*.psd" "*.ttf" "*.otf"
git add .gitattributes
printf '%s\n' '*.blend1' '*.blend2' '*.blend@' '__pycache__/' '.godot/' '.import/' 'Library/' 'Temp/' 'node_modules/' 'qa/out/' >> .gitignore
```
- Track *before* the first commit of any binary. Migrating later rewrites history
  (`git lfs migrate import`).
- Budget: GitHub Free/Pro gives 10 GiB of storage and 10 GiB of bandwidth. Every push of a changed 200 MB
  `.blend` adds 200 MB again. CI checkouts with LFS use the owner's bandwidth.
- Commit exported `.glb` files and the source `.blend` deliberately, not on every save [judgment].
- Small text-like assets (`.gltf` JSON, `.svg`, `.tres`, `.tscn`) stay in plain Git.

## 3. NEVER-DO list (with reason and evidence)

1. **NEVER use Higgsfield `generate_3d`, or any image-to-3D service, for an asset that needs separate parts,
   pivots, sockets, moving pieces, kit snapping or exact dimensions, and never present its output as
   "controllable".**
   - Reason: the default output is one fused, generator-UV'd mesh. The tool's own description says the mesh
     "reproduces only what is in the source image", and its shared schema has no part, pivot or scale
     parameter [src 1]. Round 1 found the same for TRELLIS.2: "no parts, no pivots, no sockets"
     (`02-3d-modeling.md`).
   - Part splitting is a different, later product: Tripo segment v2 is "Beta", 40 credits in the doc example,
     and returns one GLB [src 4]. Meshy T2 [src 3] and Rodin BANG [src 12] are vendor claims without
     independent tests.
   - Segmentation cannot create the faces hidden where parts touched.
   - The user's experience (fused mesh, mushy texture, no parts) is exactly the documented default.
2. **NEVER accept an AI mesh's base color without a two-light check.**
   - Generators project the photo's shading into the albedo. Meshy needed a dedicated `remove_lighting` flag
     [src 3]. A vendor guide documents shadows "on both sides" under an engine sun [src 13].
   - A texture that looks "mushy" up close is the generator's single projected texture spread over a dense
     mesh, and no parameter makes it crisp [judgment]. Re-texture with your own materials instead.
3. **NEVER use AI 3D for a stylized hero asset or a characteristic silhouette.**
   - It produces realistic/painterly albedo on dense meshes, which clashes with palette- or trim-based art
     bibles and with the anti-AI look goals (`anti-ai-look.md`) [judgment].
4. **NEVER default to local research generators** (PartCrafter, Hunyuan3D-Part, SAM 3D, TRELLIS.2).
   - They need a large NVIDIA GPU (TRELLIS.2 ≥ 24 GB; PartCrafter was tested on H20) [src 5, 8].
   - PartCrafter is trained on Objaverse renders and outputs geometry only. SAM 3D exports Gaussian splats by
     default and splits *objects in a photo*, not parts of an object [src 7]. SAM License applies.
5. **NEVER treat one perspective concept image as an orthographic blueprint.**
   - Turnaround views drift in scale and proportion, and the vendors only *claim* consistency [src 27].
   - Generate a turnaround, crop the views to the same height, check the eye/belt/knee lines, then model.
6. **NEVER bake albedo with lighting passes.** `pass_filter` must be `{'COLOR'}` for base color. DIRECT or
   INDIRECT bake the scene light into the texture [src 11].
7. **NEVER ship an AI-generated "tileable" texture untested.**
   - Vendor docs themselves warn that baked lighting gradients and vignetting break seams, that seam fixing
     is a separate inpainting pass, and that normal maps may be DirectX-convention [src 28].
   - Tile it 3×3 under a moving light before use. Prefer CC0 scanned sets.
8. **NEVER use Higgsfield `generate_audio` for SFX or music.** Its own description: "cannot generate music or
   sound effects for general use", and `sonilo_music`/`mirelo_text_to_audio` "must not be used for
   standalone audio" [src 1].
9. **NEVER ship Freesound CC BY-NC or Sampling+ sounds in a commercial game, and never drop CC BY credits.**
   - Credit format: `"name" by user ( http://freesound.org/s/ID/ ) licensed under CCBY 4.0` [src 20].
   - Keep the per-file license in `assets/LICENSES.md` when downloading, not at ship time.
10. **NEVER use Cascadeur Free for a commercial project.** The EULA forbids it, and Indie requires
    < US$100k revenue [src 18].
11. **NEVER script Mixamo downloads.** There is no API, and no official text found permits automation
    [src 25, UNVERIFIED current ToS]. The user does it by hand.
12. **NEVER commit `.blend`, `.glb`, textures or audio to plain Git, and never commit `*.blend1`.**
    - GitHub warns at 50 MiB and blocks at 100 MiB [src 24].
    - LFS quota is 10 GiB on Free, and each push of a changed file counts its full size again [src 23].
13. **NEVER mix icon sets or use game-icons.net without the credit line** "Icons made by {author}. Available
    on https://game-icons.net" [src 22] (cohesion rule: `art-direction.md`).
14. **NEVER run `gltf-transform simplify` without `weld` first.** The CLI help says split vertices limit the
    simplifier [src 10]. Never trust the target ratio: `--error` can stop it early, so measure the result.

## 4. Gaps and unverified items

- Whether Higgsfield's `generate_3d` sets Meshy's `remove_lighting`, `model_type` or `auto_size` under the
  hood is not documented in the tool schema. `models_explore(get)` was not called this round (budget). Check
  it before any use.
- There is no independent benchmark of part-segmentation quality (Tripo v2, Meshy T2, Rodin BANG, X-Part).
  Every claim is from vendor docs or press. Test on one asset before promising parts to a user.
- WebFetch could not resolve docs.blender.org, elevenlabs.io or freesound.org (curl worked for elevenlabs and
  freesound). Blender facts were verified from the source on GitHub instead.
- The `bake()` arguments other than `pass_filter` are from knowledge, not re-read.
- The YouTube transcript for "Game-Ready Topology with AI? I Compared Best AI Tools" (3hagi51IxeY) failed to
  download, so I have no independent video evidence.
- Unverified this round:
  - the Google Fonts license breakdown (OFL / Apache / UFL);
  - the Kenney audio and particle pack licenses;
  - the Sonniss GDC bundle terms;
  - the current Mixamo ToS;
  - Cascadeur scripting;
  - the ElevenLabs ToS text;
  - the engine decal and VFX class names (from knowledge).
- Rigify game-export quirks (DEF-bone hierarchy in engines) are not verified. Test the export in the target
  engine.

## 5. Sources

1. Higgsfield MCP tool schemas, read via ToolSearch 2026-10-10: `generate_3d`, `generate_image`, `generate_audio` descriptions.
2. Higgsfield `get_workflow_instructions {workflow:"character-sheet"}` (free read): style presets, `turnaround / model sheet` composition, "Do not generate without an explicit ask".
3. Meshy Image-to-3D API: https://docs.meshy.ai/api/image-to-3d.md (`model_type`, `meshy-t2`, `remove_lighting`, `enable_pbr`, `auto_size`, `origin_at`, `target_polycount`).
4. Tripo Mesh Segmentation: https://developers.tripo3d.com/en/docs/mesh-segment.md (v1/v2 Beta, granularity, example `credits_consumed: 40.00`).
5. PartCrafter README + LICENSE (MIT): https://github.com/wgsxm/PartCrafter.
6. Hunyuan3D-Part README: https://github.com/Tencent-Hunyuan/Hunyuan3D-Part (P3-SAM, X-Part, "light version").
7. SAM 3D Objects README: https://github.com/facebookresearch/sam-3d-objects (splat export, SAM License).
8. TRELLIS.2 README: https://github.com/microsoft/TRELLIS.2 (24 GB GPU, decimation_target 1,000,000, OPAQUE export).
9. Blender source: https://github.com/blender/blender/blob/main/scripts/startup/bl_operators/image_as_planes.py and source/blender/makesrna/intern/rna_object.cc (empty image properties, lines ~3458–3530).
10. glTF-Transform CLI: https://github.com/donmccurdy/glTF-Transform/blob/main/packages/cli/src/cli.ts (simplify, palette); packages/functions/src/simplify.ts (defaults).
11. Blender source: source/blender/editors/object/object_bake_api.cc and makesrna/intern/rna_scene.cc (bake pass_filter enum).
12. Rodin/BANG: https://arxiv.org/abs/2507.21493v1; https://help.scenario.com/articles/7603337491-rodin-hyper3d-bang-the-essentials; https://beforesandafters.com/2025/10/02/deemos-launches-rodin-gen-2-a-groundbreaking-generative-ai-for-intuitive-3d-creation/ (search-result level only).
13. Neural4D, "How to solve baked shadows and lighting issues": https://www.neural4d.com/how-tos/how-to-solve-baked-shadows-and-lighting-issues (vendor; search-result level).
14. Poly Haven license https://polyhaven.com/license and API https://api.polyhaven.com/files/rock_wall_08, https://api.polyhaven.com/assets?t=textures&c=wood.
15. ambientCG license: https://ambientcg.com/license (CC0 1.0).
16. Rigify source: https://github.com/blender/blender/tree/main/scripts/addons_core/rigify (ui.py `pose.rigify_generate`; metarig_menu.py `object.armature_<name>_metarig_add`; metarigs/human.py, Animals/wolf.py, Animals/horse.py exist).
17. glTF-Blender-IO: https://github.com/KhronosGroup/glTF-Blender-IO/blob/main/addons/io_scene_gltf2/__init__.py (`export_def_bones`, `export_hierarchy_flatten_bones`).
18. Cascadeur EULA: https://cascadeur.com/help/cascadeur_end_user_agreement (search-result snippet: Free = no commercial use; Indie < US$100k).
19. ElevenLabs Sound Effects API: https://elevenlabs.io/docs/api-reference/text-to-sound-effects/convert.md; licensing snippet: https://elevenlabs.io/sound-effects/commercial.
20. Freesound FAQ: https://freesound.org/help/faq/ (licenses, attribution format).
21. Godot AudioStreamRandomizer class reference: https://github.com/godotengine/godot/blob/master/doc/classes/AudioStreamRandomizer.xml.
22. game-icons.net About: https://game-icons.net/about.html (CC BY 3.0 credit line).
23. GitHub Git LFS billing: https://docs.github.com/en/billing/concepts/product-billing/git-lfs (10 GiB/10 GiB Free; per-push full-size storage; Actions bandwidth).
24. GitHub large files: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github (50 MiB warn, 100 MiB block).
25. Mixamo FAQ (Adobe community repost, 2022): https://community.adobe.com/t5/mixamo-discussions/mixamo-faq-licensing-royalties-ownership-eula-and-tos/m-p/13234775 (search-result level); status: https://app.cinevva.com/guides/free-character-animations-rigging (secondary).
26. Licenses: https://github.com/TokisanGames/Terrain3D/blob/main/LICENSE.txt (MIT); https://github.com/Alchemist0823/three.quarks/blob/master/LICENSE (MIT).
27. Turnaround guides (vendor, search-result level): https://help.scenario.com/en/articles/generate-character-turnarounds/; https://dreamina.capcut.com/resource/gpt-image-2-for-character-turnaround-sheets.
28. AI texture tools (vendor, search-result level): https://www.floyo.ai/workflows/texture-to-pbr-image-to-material-b2nju5t8qfh5; https://sorceress.games/blog/ai-pbr-texture-generator-one-photo-to-game-ready-textures.
- Video found, transcript not obtained: https://www.youtube.com/watch?v=3hagi51IxeY ("Game-Ready Topology with AI? I Compared Best AI Tools").
