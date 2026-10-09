# Toolchain: what to run for each job

Contents: 1. Principles · 2. Bundled scripts · 3. Essential tools · 4. Optional MCP servers ·
5. Paid 3D generation · 6. Asset sources · 7. Task → tool matrix · 8. Risks

## 1. Principles

- **Scripts first, MCP second.** A headless script is reproducible, diffable, re-runnable and costs no
  context. An MCP server is a live pipe into a GUI app. It is useful when a human watches the viewport
  on a desktop, and it is never required. The most popular Blender MCP refuses to start in background
  mode, so it cannot run in a cloud container at all.
- **The transport is not the skill.** "Blender MCP lets Claude model anything" is false. Asset quality
  comes from the modeling method and the render-and-look loop (`modeling.md`), not from how commands
  reach Blender.
- **Enable MCP servers per phase.** Each server's tool schemas cost context (one Blender MCP measured
  about 7k tokens). Don't keep five loaded "just in case".
- **Measure performance only on real GPUs.** Headless Chromium renders WebGL through SwiftShader. It is
  fine for screenshots and correctness, but its FPS is meaningless. Godot under Xvfb uses llvmpipe,
  with the same caveat.

## 2. Bundled scripts (in `SKILL_DIR/scripts/`)

| Script | Does | Run |
|---|---|---|
| `blender/inspect_model.py` | Game-readiness report: tris, materials, textures, texel density, flipped normals, non-manifold, loose geometry, UVs, negative/unapplied scale, units, pivot, rig/skin limits, actions. Exit 1 on FAIL | `blender -b --factory-startup --python-exit-code 1 -P inspect_model.py -- MODEL --preset web-prop --expect-height 1.0` |
| `blender/render_views.py` | Review renders: front/right/back/left/top (ortho), two 3/4 views, silhouette, wireframe overlay, optional 1.8 m scale figure, pose strip of an action, contact sheet | `blender -b --factory-startup --python-exit-code 1 -P render_views.py -- MODEL --out DIR [--engine workbench\|eevee\|cycles] [--scale-ref] [--anim Walk]` |
| `blender/clip_report.py` | Numeric animation QA per clip: loop-point pops, root speed, implied ground speed for in-place clips, foot-skate ratio. Exit 1 on FAIL | `blender -b --factory-startup --python-exit-code 1 -P clip_report.py -- MODEL [--feet L,R]` |
| `blender/image_metrics.py` | The same objective image metrics as `capture.mjs`, for screenshots from any engine; `--gray` writes grayscale copies. Exit 1 on a blank image | `blender -b --factory-startup --python-exit-code 1 -P image_metrics.py -- shots/*.png --gray` |
| `web/check_gltf.mjs` | Khronos glTF-Validator + budgets (tris, draw calls, materials, texture size, file size) | `node check_gltf.mjs MODEL.glb --max-tris 5000 --max-texture 1024` |
| `web/capture.mjs` | Runs a web game in headless Chromium: screenshots + grayscale copies + image metrics, console/page errors, failed requests, blank-canvas check, renderer stats vs budgets, scene-reload leak test, frame sequence + contact sheet | `node capture.mjs --url http://localhost:5173 --out qa/out/m1 --budgets design/budgets.json --reloads 5 --sequence 8` |

All Blender scripts also run with the PyPI module: `python inspect_model.py MODEL ...`. They accept
`.glb .gltf .fbx .obj .stl .ply .usd* .blend`.

## 3. Essential tools (work in cloud containers and on desktops)

**Blender, headless.** Use one of:
- Installed Blender: `blender -b --factory-startup --python-exit-code 1 -P script.py -- args`.
  `--python-exit-code 1` turns Python exceptions into a failing exit code. It must come **before** `-P`,
  because Blender applies arguments in order. Arguments after `--` go to
  the script.
- When no Blender is installed, or download.blender.org is unreachable: `python3.13 -m venv ~/.venv-blender &&
  ~/.venv-blender/bin/pip install bpy==5.2.2`. Create it outside the game repo. The wheel is about 400 MB and needs Python 3.13. Check the
  wheel tags on PyPI for other versions. Then run `~/.venv-blender/bin/python script.py args`. In the bpy
  module, `import bpy` must come before `import bmesh` or `mathutils`.
- In a bare Linux container, EEVEE and Workbench need Mesa EGL: `apt-get install -y libegl1
  libegl-mesa0 libgl1-mesa-dri`. Cycles CPU works without it. `EGL_BAD_MATCH` lines in the log are
  harmless noise.
- The bpy wheel has no Draco encoder. Export plain glTF, then compress with gltf-transform or gltfpack.

**glTF pipeline** (`npm i -D @gltf-transform/cli gltfpack gltf-validator`):
```bash
npx gltf-transform inspect model.glb          # meshes, vertices, materials, textures, sizes
npx gltf-transform validate model.glb         # Khronos validator; the gate is errors == 0
npx gltf-transform optimize in.glb out.glb --compress meshopt --texture-compress webp
npx gltfpack -i in.glb -o out.glb -cc -kn -km -ke   # -kn/-km/-ke KEEP named nodes/materials/extras
```
- Plain `gltfpack -cc` merges nodes and loses names that game code references.
- Validate **before** compressing. The validator does not decode meshopt and reports it as unsupported.
- Three.js needs `MeshoptDecoder` (and `KTX2Loader` for KTX2) registered on `GLTFLoader`.

**KTX2 textures** (KTX-Software 4.4+, GitHub release tarball). Prefer `ktx create` over the legacy `toktx`:
```bash
ktx create --format R8G8B8_SRGB --assign-tf srgb --encode basis-lz --generate-mipmap albedo.png albedo.ktx2
ktx create --format R8G8B8_UNORM --encode uastc --zstd 18 --generate-mipmap normal.png normal.ktx2
```
- Color maps (albedo, emissive) are sRGB. Data maps (normal, ORM, roughness) are linear and should use UASTC.

**Godot CLI** (4.x):
```bash
godot --headless --path . --import                              # import assets (CI-safe)
godot --headless --path . --script res://tests/run_tests.gd     # quit(code) → process exit code
mkdir -p qa/frames && xvfb-run -a -s "-screen 0 1280x720x24" godot --path . \
  --rendering-driver opengl3 --audio-driver Dummy --write-movie "$PWD/qa/frames/f.png" --fixed-fps 30 --quit-after 120
```
- `--headless` renders no pixels. Movie capture needs Xvfb, plus the Compatibility (OpenGL3) driver in
  containers without Vulkan.
- The output directory must already exist. `--resolution` was ignored in tests, so set the window size
  in `project.godot`.
- `RID allocations leaked at exit` lines are noise. Gate on the exit code and your own assertions.

**Web games:** `npm i -D playwright && npx playwright install chromium`, then `capture.mjs`. Filter
`GPU stall due to ReadPixels` warnings, which screenshots themselves cause.

**Frames and contact sheets:**
```bash
ffmpeg -y -framerate 30 -i qa/frames/f%08d.png -c:v libx264 -pix_fmt yuv420p qa/proof.mp4
ffmpeg -y -i qa/proof.mp4 -vf "select='not(mod(n\,10))',scale=480:-1,tile=4x3" -frames:v 1 -fps_mode vfr qa/sheet.png
montage shot_*.png -tile 3x -geometry +4+4 qa/contact.png    # ImageMagick 6
```

## 4. Optional MCP servers (desktop, per phase)

| Need | Server | Setup |
|---|---|---|
| Live Blender inspection on a desktop | **Blender Lab official MCP** (Blender ≥ 5.1, GPL-3.0). It is minimal: code execution, blend-file summaries, API/manual doc search, screenshots, thumbnail renders. It can run in background mode with `--command blender_mcp` | Follow the install steps on blender.org/lab, or from source: `uv --directory /abs/path/blender_mcp/mcp run blender-mcp` |
| Blender with asset search/import (Poly Haven, Sketchfab, Poly Pizza) and multi-angle `look` | `ahujasid/mcp-for-blender` (MIT). Needs the GUI | `claude mcp add blender uvx mcp-for-blender` then `uvx mcp-for-blender install-addon`. Set `BLENDER_MCP_SAFE_MODE=1` and `DISABLE_TELEMETRY=true` |
| Web perf traces, Lighthouse, console with source maps | **Chrome DevTools MCP** (Apache-2.0) | `claude mcp add chrome-devtools --scope user npx chrome-devtools-mcp@latest`. Add `--slim --headless` for routine checks, and `--no-usage-statistics --no-performance-crux` |
| Godot editor screenshots, test runs, GDScript validation | `hi-godot/godot-ai` (MIT, Godot 4.7+, editor plugin) | Per its README; set `GODOT_AI_DISABLE_TELEMETRY=true` |
| Unity editor control, tests, profiling | `CoplayDev/unity-mcp` (MIT), or Unity's official MCP (beta, Unity 6+, AI Assistant package) | Per their docs. Use tool groups to limit context |
| Engine conventions from the vendor | Unity's official agent plugin (`Unity-Technologies/unity-agent-plugin`) and Epic's `unreal-engine-skills-for-claude-code`, both listed in Anthropic's official plugin marketplace | `/plugin` → browse the official marketplace. Their text is under vendor licenses; use them alongside this skill |

Rules:
- Run only one Blender MCP at a time, because both default to port 9876.
- If a Blender MCP call hangs, don't wait it out. One server has an open bug with 4–5 minute hangs on
  Blender 5.1+. Time out and fall back to the headless script.

**Avoid:**
- `chongdashu/unreal-mcp` (abandoned since April 2025).
- `Coding-Solo/godot-mcp` (adds little over the Godot CLI).
- Running two Blender MCPs at once.

## 5. Paid 3D generation (optional, with cost and license discipline)

Image-to-3D services produce raw material, not game-ready assets. None of them claims game-ready
topology out of the box. Remesh, retopology and rigging are separate (often paid) steps, and rigging is
reliable for humanoids first. Every generated asset goes through the same gates as everything else
(`modeling.md`).

| Service | Use it for | Watch out for |
|---|---|---|
| Meshy (official MCP `@meshy-ai/meshy-mcp-server`, paid API key) | Characters and props, remesh with `target_polycount`, humanoid auto-rig and animation clips | Free-tier outputs are CC BY 4.0, so attribution is required. Auto-rig works only for standard bipeds |
| Tripo (REST API v3) | Low-poly "P" models with face-count control; rig types for quadrupeds, birds and other creatures; `spec: mixamo` | Free-tier commercial terms are unclear, so check before shipping. The MCP is alpha |
| Hyper3D Rodin | High-quality props | API only on the business plan |
| Hunyuan3D open weights | Local generation on your GPU | The license territory **excludes the EU, UK and South Korea**, and over 1M MAU needs a separate license |
| Higgsfield MCP `generate_3d` (if connected) | Routes to Meshy/Tripo/Hunyuan/SAM-3D models | Spends credits. Preflight with `get_cost: true`. Its hosted "3D Jutsu" Blender cannot import your own files and has no network |

Always:
- Preflight the cost, and get the user's OK before spending.
- Never blind-retry a paid job. Poll it by job id.
- Record generator, plan and license for every asset in `assets/LICENSES.md`.

## 6. Asset sources

- **Poly Haven** (CC0): HDRIs, PBR textures, some models. Free, no key. The best single upgrade for
  lighting is an HDRI environment. Use 1k–2k resolutions.
- **Poly Pizza** (low-poly GLBs): about 69% CC-BY, which requires credit. Filter to CC0 when possible. It
  blocks datacenter IPs, so expect failures from cloud sessions.
- **Kenney, Quaternius, KayKit, ambientCG:** popular stylistically consistent packs, widely published as
  CC0. Check the license file in each pack before use.
- **Sketchfab:** filter by downloadable license and record it.
- **Mixamo:** a free humanoid auto-rigger and animation library, but there is no official API.
  Automating it carries terms-of-service risk, so use it manually.

Record every third-party asset (source URL, author, license) in `assets/LICENSES.md` when it enters
the project.

## 7. Task → tool matrix

| Task | Cloud / CI container | Desktop |
|---|---|---|
| Procedural model, export GLB | bpy / `blender -b -P` | same; optionally a Blender MCP to watch |
| Inspect an asset | `inspect_model.py` + `check_gltf.mjs` | same, or Blender Lab MCP summaries |
| Look at an asset | `render_views.py` → contact sheet → Read the PNG | same, or MCP screenshots |
| Optimize for delivery | gltf-transform / gltfpack `-kn -km -ke`, `ktx create` | same |
| Godot import + tests | `--headless --import`, `--headless --script` | godot-ai `test_run` |
| Gameplay frames / proof video | Xvfb + `--write-movie` (Godot); `capture.mjs --sequence` (web) | same, or editor screenshots |
| Web screenshots + console | `capture.mjs` | Chrome DevTools MCP |
| Web performance budget | not measurable (SwiftShader) | Chrome DevTools performance trace on a real GPU |
| Unity scene/editor work | not practical | unity-mcp / Unity MCP |
| Humanoid character + rig + clips | Meshy / Higgsfield (paid), or a CC0 rigged pack | same, plus Mixamo by hand |
| Creature rig | Tripo `rig_type` (paid) or a scripted Blender rig | same |

## 8. Risks

- **Arbitrary code execution:** every Blender and engine MCP exposes "run code". Work on copies of
  `.blend` files, keep secrets out of the workspace, and keep sockets on localhost.
- **Telemetry:** several servers send usage data by default. Turn it off with the flags above.
- **Licenses:** never ship an asset whose license you did not record.
- **Stale knowledge:** read the installed version before using version-sensitive APIs, e.g.
  `node_modules/three/package.json`, `godot --version`, `bpy.app.version_string`.
