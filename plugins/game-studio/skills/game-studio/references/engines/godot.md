# Godot 4 specifics

Contents: 1. Renderer choice · 2. Environment and lighting recipe · 3. Importing assets · 4. QA autoload
(shots + metrics) · 5. Tests and capture commands · 6. Animation · 7. Traps

Check `godot --version` first. Several features below (AgX tonemapping, skeleton modifiers) need 4.4 or
later.

## 1. Renderer choice

| Renderer | Use for |
|---|---|
| Forward+ | Desktop games. Full feature set: SSAO, SDFGI, volumetric fog |
| Mobile | Mobile and lower-end desktop |
| Compatibility (OpenGL) | **Web export** (required for web in Godot 4), very low-end hardware, and headless containers under Xvfb |

Pick it in Project Settings → Rendering → Renderer, and record the choice in an ADR. Feature
availability differs per renderer, so check the art bible's render recipe against it.

## 2. Environment and lighting recipe

A `WorldEnvironment` node with an `Environment` resource holds the whole recipe in one reviewable place.

| Setting | Starting value | Why |
|---|---|---|
| Background | Sky: `ProceduralSkyMaterial` tinted to the palette, or `PanoramaSkyMaterial` with a Poly Haven HDRI | The sky also lights the scene |
| Ambient light source | Sky; energy ~1.0 | Colored fill instead of flat grey |
| Reflected light source | Sky | Metals need something to reflect |
| Tonemap | AgX (4.4+) for most looks; Filmic/ACES for cinematic; Linear only for unlit flat styles | §6 of `art-direction.md` |
| Exposure | 1.0, tuned on gameplay | — |
| Glow | Enabled, blend mode **Soft Light**, HDR threshold ~1.0; only emissives above 1.0 should glow | Additive is usually too strong |
| SSAO (Forward+) | Enabled, intensity conservative (~1) | Strong SSAO distracts in play; it darkens only ambient light |
| Fog | Depth fog with **Aerial Perspective** ~0.5, plus height fog in valleys | Depth through atmosphere, tinted to the sky |
| Adjustments | Color-correction LUT (33³), if the art bible defines a grade | One global grade unifies sources |

`DirectionalLight3D` (sun):
- warm color, energy ~1–2;
- shadows on;
- **Normal Bias** before Bias;
- **Max Distance** as low as the scene allows (quality and performance);
- angular distance ~0.5° for contact-hardening soft shadows (expensive, so use it on few lights).

Static scenes: bake a `LightmapGI` in the editor for the biggest single lighting upgrade. For dynamic
scenes on Forward+, consider SDFGI. Small props get blob shadows (a Decal or a textured quad) rather
than real shadows.

## 3. Importing assets

- glTF 2.0 (`.glb`) is the preferred format. Keep 1 unit = 1 m and Y up, which matches glTF.
- **Node-name import hints** (set them in Blender object names):
  - `-col`: mesh plus generated static collision;
  - `-colonly`: collision only;
  - `-convcol` / `-convcolonly`: convex variants;
  - `-noimp`: skip;
  - `-loop` (or `-cycle`) on animation names makes them loop.
- Use Advanced Import Settings to extract materials (when you need to edit them), set the root type,
  and generate LODs (on by default) and shadow meshes.
- Organize per feature: `characters/player/art/`, `levels/forest/props/` (`architecture.md` §5).

## 4. QA autoload (shots + metrics)

```gdscript
# res://qa/qa.gd: register as autoload "QA". Inert unless started with:  -- --qa [--qa-out=/abs/dir]
extends Node

var enabled := false
var out_dir := "user://qa"

func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	enabled = args.has("--qa")
	if not enabled:
		return
	for a in args:
		if a.begins_with("--qa-out="):
			out_dir = a.trim_prefix("--qa-out=")
	seed(1234)  # global RNG; seed your RandomNumberGenerator instances from config too
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(out_dir))

func capture(shot_name: String) -> void:
	await RenderingServer.frame_post_draw  # earlier captures are black or stale
	var img := get_viewport().get_texture().get_image()
	img.save_png(ProjectSettings.globalize_path("%s/%s.png" % [out_dir, shot_name]))

func metrics() -> Dictionary:
	return {
		"draw_calls": Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME),
		"primitives": Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),
		"objects": Performance.get_monitor(Performance.RENDER_TOTAL_OBJECTS_IN_FRAME),
		"video_mem_bytes": Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED),
		"orphan_nodes": Performance.get_monitor(Performance.OBJECT_ORPHAN_NODE_COUNT),
	}

func write_report(data: Dictionary) -> void:
	var f := FileAccess.open(ProjectSettings.globalize_path("%s/report.json" % out_dir), FileAccess.WRITE)
	f.store_string(JSON.stringify(data, "  "))
```

```gdscript
# res://qa/shots.gd: attach to the root of res://qa/shots.tscn, which instances the level and
# has one Camera3D per verification shot (gameplay, wide, hero, darkest, ...).
extends Node
@export var shot_cameras: Array[NodePath] = []

func _ready() -> void:
	for i in 10:
		await get_tree().process_frame  # let the level settle
	var report := {"shots": []}
	for path in shot_cameras:
		var cam := get_node(path) as Camera3D
		cam.make_current()
		await get_tree().process_frame
		await QA.capture(cam.name)
		report.shots.append({"name": cam.name, "metrics": QA.metrics()})
	QA.write_report(report)
	get_tree().quit(0)
```

## 5. Tests and capture commands

```bash
godot --headless --path . --import                                          # import assets (CI-safe)
godot --headless --path . -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit # GUT tests (or the gdUnit4 CLI)
# Shots need a display: a real one, or Xvfb with the OpenGL3 (Compatibility) driver in containers
xvfb-run -a -s "-screen 0 1280x720x24" godot --path . --rendering-driver opengl3 --audio-driver Dummy \
  res://qa/shots.tscn -- --qa --qa-out="$PWD/qa/out/shots"
# Motion sequence (non-real-time, deterministic): Movie Maker
mkdir -p qa/out/frames && xvfb-run -a godot --path . --rendering-driver opengl3 --audio-driver Dummy \
  --write-movie "$PWD/qa/out/frames/f.png" --fixed-fps 30 --quit-after 150 res://levels/test_level.tscn
```

- `--headless` disables rendering entirely, so use it for tests and import only.
- `--write-movie` needs an existing output folder.
- In tests, the window size came from `project.godot`, not from `--resolution`.
- Turn frames into a contact sheet with `toolchain.md` §3 (ffmpeg `tile`).
- `RID allocations leaked at exit` lines are noise. Gate on the exit code and the report.

## 6. Animation

- `AnimationTree` with a StateMachine root:
  - Transitions use Xfade Time with a non-linear curve.
  - Use BlendSpace1D/2D for locomotion and OneShot with filters for upper-body actions.
  - Advance Expressions read gameplay state.
- Godot 4.4+ skeleton modifiers: `SpringBoneSimulator3D` (secondary motion), `LookAtModifier3D`,
  `RetargetModifier3D`. Godot 4.6+ adds `TwoBoneIK3D`. `SkeletonIK3D` is deprecated.
- Hitstop with `Engine.time_scale`: timers that must keep running use `ignore_time_scale`, and tweens
  set `set_ignore_time_scale(true)`.
- `Tween`:
  - `create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)` for pops;
  - `TRANS_SINE` + `EASE_IN_OUT` for camera moves.

## 7. Traps

- Web export requires the Compatibility renderer. Effects designed on Forward+ (SSAO, SDFGI, volumetric
  fog) won't exist there, so design the web look on Compatibility from the start.
- Metallic materials without a sky or reflection probe render dark. Check `reflected_light_source`.
- Physics belongs in `_physics_process` (fixed rate), visuals in `_process`. Mixing them causes jitter.
- Movement in `_process` without `delta` is frame-rate dependent.
- Autoload sprawl: every autoload widens the global state. Keep to the few that pass the test in
  `architecture.md` §5.
- Case sensitivity: exported packs are case-sensitive, while the editor on Windows/macOS may not be.
  Use snake_case paths everywhere.
