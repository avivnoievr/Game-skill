# 05 — MCP servers & external tools for 3D game production (Research Agent 5)

Date: 2026-10-09. Run was cut short by a spend limit, so some planned threads were not finished (asset
libraries other than Poly Haven/Poly Pizza, Mixamo, audio MCPs, Unreal details). Those are marked
[UNVERIFIED] or [NOT RESEARCHED]. Everything else was read from the repo/docs, or **run in this
container** (Ubuntu 24.04, 4 vCPU, no GPU, Python 3.13.16, Node 22.22, Mesa 25.2.8, Xvfb installed).
Downloads and test files are in `SCRATCH/downloads/5/` and `SCRATCH/tooltest/`.

---

## 1. Executive summary

1. **For a cloud/CI container, plain Bash plus headless Blender beats every Blender MCP.** I ran the official
   `bpy` 5.2.2 wheel from PyPI headless. It built a mesh, exported a GLB, and rendered PNGs with **EEVEE, Workbench
   and Cycles CPU, all without a GPU or display**. No socket, add-on or GUI was needed. The most popular Blender MCP
   (ahujasid `mcp-for-blender`, 30.3k★) **refuses to start in `blender -b`**. Its own add-on prints
   "run Blender with a GUI, or use … xvfb-run".
2. **An official Blender MCP exists.** Blender Lab built it, Anthropic announced it on 2026-04-28, it needs
   Blender ≥ 5.1, and it is GPL-3.0. It has 20 small tools and **can run in background mode**
   (`blender --background file.blend --command blender_mcp`). It is the best MCP choice for desktop work. It
   shares the default port 9876 with ahujasid's add-on, which is a known cause of conflicts.
3. **blender.org is blocked by this container's proxy** (www, download, projects). The official tarball
   can't be fetched here, but `pip install bpy` from PyPI works (about 400 MB wheel, about 1 GB venv). The skill
   should document both install paths.
4. **Headless Godot 4.7.2 works for import, scripted tests and video capture.** `--headless --import` and
   `--headless --script` worked. `--write-movie` worked only under **Xvfb with the Compatibility/OpenGL3
   renderer** (Mesa llvmpipe). Vulkan Forward+ failed (`VK_KHR_surface not found`) and fell back to GL.
5. **Headless Chromium renders WebGL2 here** through ANGLE/SwiftShader. Three.js loaded and rendered the
   Blender GLB, and the screenshot was correct. **FPS numbers from SwiftShader are meaningless** for GPU budgets
   (rAF-capped at about 59).
6. **The glTF toolchain works from npm with no system install:** `@gltf-transform/cli` 4.5.1 (inspect, validate,
   optimize), `gltfpack` 1.3 and `gltf-validator` 2.0.0-dev.3.10. Warning: by default **gltfpack merged my two
   named nodes into one**. Use `-kn -km -ke` when game code references node names.
7. **KTX-Software 4.4.2** (GitHub tarball) works. `ktx create … --encode basis-lz` turned a 1.39 MB PNG into a
   54 KB KTX2. The release notes say "legacy tools will be removed in Release 4.5", so prefer `ktx create`
   over `toktx`.
8. **Engine MCPs only pay off on a desktop with the editor open.** CoplayDev `unity-mcp` (14.8k★, MIT, v10.3.0
   on 2026-10-04) and `hi-godot/godot-ai` (2.9k★, MIT, 46 tools, `editor_screenshot` including the running-game
   framebuffer) are active. Coding-Solo `godot-mcp` (6.0k★) mostly wraps the Godot CLI and its last commit was
   2026-04-16. chongdashu `unreal-mcp` (2.1k★) had its last commit on **2025-04-22, so it is stale**. Unity ships
   an official MCP server in beta (`com.unity.ai.assistant`, Unity 6+).
9. **For web games, Chrome DevTools MCP (Google, Apache-2.0) is the richest verification MCP.** It has
   performance traces, Lighthouse, console with source maps and heap snapshots. Playwright MCP's own README now
   tells coding agents to prefer **Playwright CLI + skills** because MCP schemas and accessibility trees cost
   tokens.
10. **AI 3D generation is a paid, optional tier with real licensing traps.** Free-tier outputs are CC BY 4.0
    (Meshy) or contested (Tripo). Rodin API access needs the $120/mo Business plan. **The Hunyuan3D open-weights
    license excludes the EU, UK and South Korea and forbids using outputs there.** Auto-rigging is reliable for
    humanoids only (Meshy says so explicitly; Tripo offers biped/quadruped/etc. rig types).
11. **The Higgsfield MCP in this environment** gives (a) `generate_3d`, which routes to Meshy, Tripo H3.1,
    Hunyuan3D v3/v3.1 and Meta SAM-3-3D (paid), and (b) "3D Jutsu", which is **hosted headless Blender 5.2 with no
    network, about 5 min per operation, and catalog-only imports (you cannot import your own GLB)**. It suits demo
    scenes but is not a pipeline replacement for local bpy.
12. **Context cost is real.** ahujasid's tool schemas were measured at **6,928 tokens** (issue #347). Chrome
    DevTools MCP has about 57 tools in full mode (`--slim` exists). Install MCPs per task and do not keep all of
    them loaded.

---

## 2. Catalog

★ / last commit are from GitHub search (2026-10-09) and `git log -1` of a depth-1 clone. "Verified" means I
opened the README/source. "Ran" means I executed it in this container.

| Name | URL | Type | ★ / last commit | License | Verdict 1–5 | What to borrow |
|---|---|---|---|---|---|---|
| bpy (Blender as Python module) | pypi.org/project/bpy | CLI/lib (ran) | 5.2.2 LTS, 2026-09-15 | GPL-3.0 | **5** | Headless model/export/render in CI; `pip install bpy==5.2.2` (needs Py 3.13) |
| Blender CLI (`blender -b -P`) | blender.org | CLI | n/a (download blocked here) | GPL | **5** | Same as above, with full Blender; `--python-exit-code 1` |
| Blender Lab official MCP | projects.blender.org/lab/blender_mcp (source read via fork history) | MCP | v1.0.0 manifest; upstream commit 2026-08-06 (Campbell Barton) | GPL-3.0-or-later | **4** desktop / 3 cloud | Minimal 20-tool design, background `--command blender_mcp`, bundled API/manual RST search |
| ahujasid mcp-for-blender (ex blender-mcp) | github.com/ahujasid/mcp-for-blender | MCP | 30.3k★ / 2026-10-06, v2.1.9, 22 open issues | MIT | **3** | `look` multi-angle/wireframe/xray views; Poly Haven/Poly Pizza/Sketchfab import with licence metadata; safe mode |
| bpy-dev/blender-mcp | github.com/bpy-dev/blender-mcp | MCP (fork of official) | 98★ / 2026-09-11 | GPL-3.0+ | 2 (preview) | `_for_cli` tools that run on saved .blend in subprocess; standalone-bpy backend |
| fnf-blender-mcp (Higgsfield "use Blender") | npm fnf-blender-mcp | MCP | 0.2.2, 2026-09-23 | MIT | 3 | Drives a **background** Blender process (no add-on); 21 `bl_*` tools; bundled MIT skills (`blender-audit-finalize` etc.) |
| Higgsfield MCP: generate_3d / 3D Jutsu | (connected MCP) | MCP (paid) | n/a | proprietary | 3 | Hosted bpy 5.2 with revision guards; read its `/3d-jutsu` guidance (render-then-inspect gates) |
| Coding-Solo/godot-mcp | github.com/Coding-Solo/godot-mcp | MCP | 6.0k★ / 2026-04-16, 73 open issues, v0.1.1 | MIT | 2 | Nothing Bash can't do: launch/run/debug-output/scene ops via CLI |
| hi-godot/godot-ai | github.com/hi-godot/godot-ai | MCP + editor plugin | 2.9k★ / 2026-10-03 | MIT | **4** desktop | `editor_screenshot` (viewport/cinematic/game), `test_run`, GDScript parse-validation |
| CoplayDev/unity-mcp | github.com/CoplayDev/unity-mcp | MCP + Unity pkg | 14.8k★ / 2026-10-08, v10.3.0 | MIT | **4** desktop | 50 tools, tests/profiling/build, tool groups to cut context |
| Unity official Unity MCP (AI Assistant) | docs.unity3d.com/Packages/com.unity.ai.assistant@2.11 | MCP (beta) | 2.11.0-pre.2 | Unity terms | 3 | Relay `~/.unity/relay/relay_linux --mcp`, connection approval |
| IvanMurzak/Unity-MCP | github.com/IvanMurzak/Unity-MCP | MCP | 4.4k★ / 2026-10-04 | (not checked) | [NOT EVALUATED] | — |
| chongdashu/unreal-mcp | github.com/chongdashu/unreal-mcp | MCP | 2.1k★ / **2025-04-22** | (not checked) | 1 (stale) | — |
| ChiR24/Unreal_mcp | github.com/ChiR24/Unreal_mcp | MCP | 910★ / 2026-10-08 | (not checked) | [NOT EVALUATED] | — |
| Epic official MCP plugin (UE 5.8, experimental) | unrealengine.com (403 here) | MCP | — | Epic | [UNVERIFIED: search snippets quoting Epic's State of Unreal 2026 recap] | — |
| Playwright MCP | github.com/microsoft/playwright-mcp | MCP | 0.0.83 / 2026-10-08 | Apache-2.0 | 3 | `--headless --isolated`, `browser_console_messages`, `browser_take_screenshot`; README says prefer CLI+skills |
| Playwright (library) + Chromium headless shell | npm playwright@1 | CLI/lib (ran) | Chromium 156.0.8078.4 | Apache-2.0 | **5** | Scripted screenshot + console capture of WebGL games (tested) |
| Chrome DevTools MCP | github.com/ChromeDevTools/chrome-devtools-mcp | MCP + plugin | 1.10.1 / 2026-10-09 | Apache-2.0 | **4** | `performance_start/stop_trace`, `performance_analyze_insight`, `lighthouse_audit`, `list_console_messages`, heap tools |
| glTF Transform CLI | npm @gltf-transform/cli | CLI (ran) | 4.5.1 | MIT | **5** | `inspect`, `validate`, `optimize`, `dedup/prune/weld/simplify`, `etc1s/uastc/webp` |
| gltfpack (meshoptimizer) | npm gltfpack | CLI (ran) | 1.3.0 | MIT | 4 | `-cc`, `-si`, `-tc`; **use `-kn -km -ke`** |
| Khronos glTF-Validator | npm gltf-validator | lib (ran) | 2.0.0-dev.3.10 | Apache-2.0 | **5** | Errors/warnings JSON; gate on `numErrors==0` |
| KTX-Software | github.com/KhronosGroup/KTX-Software | CLI (ran) | v4.4.2 | Apache-2.0 | 4 | `ktx create --encode basis-lz/uastc`, `ktx info` |
| Godot 4.7.2 editor binary | github.com/godotengine/godot/releases | CLI (ran) | 4.7.2-stable (2026-08-18) | MIT | **5** | `--headless --import`, `--headless --script`, `--write-movie` under Xvfb |
| ffmpeg 6.1.1 / ImageMagick 6.9.12 | apt (preinstalled) | CLI (ran) | — | LGPL/GPL, IM license | **5** | Frames→mp4, `tile` contact sheets, `montage` |
| Meshy API + MCP | docs.meshy.ai/api/ai | API/MCP (paid) | npm @meshy-ai/meshy-mcp-server | (server OSS; outputs per plan) | 3 | Remesh to quad/tri + target polycount; humanoid rig + 3 cr/animation |
| Tripo API v3 / tripo-mcp | developers.tripo3d.com; github VAST-AI-Research/tripo-mcp | API (paid) / MCP alpha | tripo-mcp 210★ | — | 3 API / 1 MCP | P-series low-poly 48–20k faces; multi-species rig types; `spec: mixamo` |
| Hyper3D Rodin | hyper3d.ai/pricing | API (paid) | — | per plan | 2 | API only on Business ($120/mo) |
| Hunyuan3D 2.x open weights | github.com/Tencent-Hunyuan/Hunyuan3D-2.1 | model | — | Tencent Hunyuan 3D Community License | 2 (legal) | Territory excludes EU/UK/KR |
| Poly Haven API | via ahujasid README | asset API | ~2,400 assets | CC0 | **5** | HDRIs/textures/models; free, no key |
| Poly Pizza API | via ahujasid README | asset API | ~10,600 models | ~69% CC-BY | 4 | Free key; **Cloudflare blocks datacenter IPs** |
| Kenney / Quaternius / KayKit / ambientCG / Sketchfab API / Mixamo / ElevenLabs | — | — | — | — | [NOT RESEARCHED: run cut short] | — |

Other Blender MCPs that appeared in search but were **not opened** (no verdict): HoldMyBeer-gg/blenderwright (163★,
"191 tools"), VxASI/blender-mcp-vxai (300★), AIGODLIKE/GenesisCore (141★), dhakalnirajan/blender-open-mcp (119★),
scenario-labs/skills (932★, Scenario MCP + Blender/Unity/Unreal "expert teams"), elithril/blender-kiln (41★, Claude
Code plugin, "runs on both Blender MCP servers"). Agents 1/2 may want to look at the last two.

---

## 3. Distilled guidance

### 3.1 Blender: MCP vs headless Bash (evidence-based)

**Headless experiment (ran):** `SCRATCH/tooltest/bpy_smoke.py` and `bpy_engines.py`
```bash
python3 -m venv .venv-blender && .venv-blender/bin/pip install bpy==5.2.2   # wheel ≈402 MB, cp313 only
.venv-blender/bin/python bpy_smoke.py out/      # build crate+barrel, export GLB, render, save .blend
```
Results on 4 vCPU, no GPU, 480×320:

| Step | Result |
|---|---|
| `bpy.app.version_string`, `bpy.app.background` | `5.2.2 LTS`, `True` |
| GLB export (`bpy.ops.export_scene.gltf`, 170 tris) | OK, 0.06 s, 8.5 KB |
| EEVEE render | OK, **18.3 s** (first run, mostly shader compile); prints `EGL Error 0x3009 EGL_BAD_MATCH` ×3 but image is correct |
| Workbench render | OK, 0.43 s |
| Cycles CPU 16 spp | OK, 1.75 s |
| Draco / meshopt compression in glTF exporter | **Not available in the bpy wheel** (`libbf_intern_draco_bridge.so` missing) → compress afterwards with gltf-transform/gltfpack |
| `RenderSettings.engine` enum listing | Showed only `BLENDER_EEVEE`, yet setting `CYCLES` / `BLENDER_WORKBENCH` worked. Don't trust the enum listing; set it directly |
| Deprecation | `Material.use_nodes` "expected to be removed in Blender 6.0" |

**Comparison:**

| Criterion | Headless Bash (`blender -b -P` / bpy) | ahujasid mcp-for-blender | Blender Lab official MCP |
|---|---|---|---|
| Works in cloud container w/o display | **Yes (tested)** | **No.** Add-on refuses `bpy.app.background`, needs GUI or `xvfb-run -a blender` (addon.py source) | Yes for code/summary tools via `--command blender_mcp`; screenshot/jump tools need UI |
| Reproducibility | Script + seed + pinned version = deterministic, diffable, re-runnable in CI | Stateful live session; history lives in the chat | Stateful (live) |
| Reliability | Process exit code; no socket | Open issue #339: tool calls hang ~4–5 min on Blender 5.1+/5.2 (Windows), unresolved; README: "Sometimes the first command won't go through" | 1.0.x; fewer field reports [UNVERIFIED] |
| Visual check | Render PNG → Read image | `look` tool: viewport/camera/angles/frames, solid/wireframe/xray | `render_thumbnail_to_path`, area/window screenshots |
| Extras | Write your own | Poly Haven / Sketchfab / Poly Pizza search+import, Tripo/Rodin/Hunyuan generation | Bundled API docs + manual full-text search |
| Context cost | 0 schema tokens | ~6.9k tokens of schemas (issue #347) | 20 small tools [token count UNVERIFIED] |

**Rule for the skill:** use headless scripts as the primary path for modeling, export and render QA. Use a
Blender MCP only for interactive desktop sessions where a human is watching the viewport. Never require an MCP.

**Install Blender on Linux non-interactively:**
- PyPI (works here): `pip install bpy==5.2.2`. Requires Python 3.13 (5.1.x and 5.2.x wheels are cp313; 5.0.x
  wheels are cp311). It is GPL-3.0 and published by the Blender Foundation.
- Official tarball: pattern `https://download.blender.org/release/Blender5.2/blender-5.2.2-linux-x64.tar.xz`, then
  `tar xf` and run `./blender -b`. **[UNVERIFIED here: download.blender.org is blocked by this proxy.]** The URL
  pattern is from memory and must be checked.
- apt (Ubuntu 24.04): `apt-cache policy blender` returned nothing in this container (no package lists). Distro
  versions lag upstream. [UNVERIFIED which version.] Snap: [UNVERIFIED].

**Headless script conventions:**
```bash
blender -b --factory-startup -P build_asset.py --python-exit-code 1 -- --out out/ --seed 42
```
(`--python-exit-code` makes Python exceptions fail the process; the args after `--` go to the script. These are
Blender CLI flags I know but did not run here, because only the bpy wheel was available.)

### 3.2 Official Blender Lab MCP: verified facts
Source: the upstream baseline `4309a39` inside `bpy-dev/blender-mcp` git history, authored by Campbell Barton
(Blender core dev). The fork's NOTICE gives the upstream URL `projects.blender.org/lab/blender_mcp`.
- Add-on manifest: `id="mcp"`, `version="1.0.0"`, `maintainer="Blender Lab"`, `blender_version_min="5.1.0"`,
  GPL-3.0-or-later, `network` permission "Runs a local TCP socket server". Default `localhost:9876`.
- Server package `blender-mcp` 1.0.0, deps `mcp[cli]`, `docutils`, `pyyaml`. Data flow is
  `MCP client ⇐stdio⇒ blender-mcp ⇐TCP⇒ add-on`.
- Upstream tools (20): `execute_blender_code`, `get_blendfile_summary_{datablocks,missing_files,of_linked_libraries,path_info,usage_guess}`,
  `get_object_detail_summary`, `get_objects_summary`, `get_python_api_docs`, `search_api_docs`, `search_manual_docs`,
  `get_screenshot_of_area_as_image`, `get_screenshot_of_window_as_image`, `get_screenshot_of_window_as_json`,
  `jump_to_tab_by_name`, `jump_to_tab_by_space_type`, `jump_to_view3d_object_by_name`,
  `jump_to_view3d_object_data_by_name`, `render_thumbnail_to_path`, `render_viewport_to_path`.
- Background mode: `blender --background file.blend --command blender_mcp [--host H --port P]`. "Deferred
  responses are not supported in background mode."
- `weak_sandbox.py`: "this isn't really a sandbox… more of a slap on the wrist". It blocks `sys.exit` and some
  operators.
- The bundled `prompts.yml` contains good rules to borrow: "NEVER assume missing values - inspect the scene
  first"; "set mode/active/selection explicitly"; "flush bmesh changes… forgetting this silently loses all
  edits"; "Return structured data… not print output"; "Blender defaults to meters".
- Anthropic's post (anthropic.com/news/claude-for-creative-work, fetched): "The Blender developers have created
  an MCP connector, which is now officially available for Claude." It also mentions a one-time donation to
  Blender (update dated May 1, 2026).
- Install UI steps (blender.org/lab/mcp-server, the .mcpb bundle): **[UNVERIFIED, blender.org blocked]**.
  From source per the fork README: `uv --directory /abs/path/blender_mcp/mcp run blender-mcp`.

### 3.3 ahujasid mcp-for-blender: setup and facts (README + source, v2.1.9)
```bash
claude mcp add blender uvx mcp-for-blender        # server
uvx mcp-for-blender install-addon                 # copies add-on; then enable "Interface: MCP for Blender"
# recommended env in the MCP entry:
#   DISABLE_TELEMETRY=true  BLENDER_MCP_SAFE_MODE=1   (and --python 3.11 + UV_PYTHON_PREFERENCE=only-managed)
```
- Tools (README): `execute_blender_code`, `look`, `get_scene_info`, `generate_3d`, `search_assets`, `import_asset`,
  `get_addon_status`, `disable_telemetry`, `record_trajectory_feedback`.
- Socket "has no authentication or encryption, so anyone who can reach that port can run Python inside Blender".
- Safe mode blocks file I/O, subprocess, network and persistent handlers. Blocked scripts are returned to the AI.
- Telemetry: an anonymous usage record is sent by default. Content (prompts, code, screenshots) is opt-in. The
  T&C says data "may be used to train AI models". Issue #360 reported that consent was on by default in v1.9.1;
  the current README says opt-in.
- Poly Haven downloads run on Blender's main thread, so the UI freezes. The README suggests 1k/2k resolution.
- Credentials can come from env vars (`BLENDERMCP_SKETCHFAB_API_KEY`, `BLENDERMCP_POLYPIZZA_API_KEY`,
  `BLENDERMCP_HYPER3D_API_KEY`, `BLENDERMCP_HUNYUAN3D_SECRET_ID/KEY`).
- It has bundled guides (`src/blender_mcp/guides/{bpy,materials,retopology,rigging,animation,level-design,scene}.md`),
  which are candidate reading for Agents 2 and 3.

### 3.4 Godot CLI (ran with Godot 4.7.2-stable, official GitHub release zip)
```bash
G=./Godot_v4.7.2-stable_linux.x86_64
$G --headless --path proj --import                          # 8.0 s; imports props.glb → .godot/imported/*.scn
$G --headless --path proj --script res://test_headless.gd   # SceneTree script; quit(code) → process exit code (got 0, ok=true)
mkdir -p frames   # REQUIRED: Godot did not create the dir; first attempt produced nothing
xvfb-run -a -s "-screen 0 1280x720x24" $G --path proj --rendering-driver opengl3 \
   --write-movie "$PWD/frames/f.png" --fixed-fps 30 --quit-after 10      # 10 PNGs + f.wav, 1.3 s
```
- The renderer was "OpenGL API 4.5 Mesa 25.2.8 – Compatibility – llvmpipe". `--resolution 640x360` was
  **ignored** (frames came out 1152×648, the project default). Set `display/window/size/*` in project.godot instead.
- Forward+ under Xvfb gave `Required Vulkan instance extension VK_KHR_surface not found` and then "switching to
  OpenGL 3". Plan on the Compatibility renderer in containers, or install Mesa lavapipe [UNTESTED].
- `--headless` uses the dummy display and rendering driver (per `--help`), so it is fine for tests and import but
  produces no pixels. I infer that `--write-movie` needs Xvfb rather than `--headless` [the headless+movie
  combination was not run].
- Benign noise at exit: `ERROR: n RID allocations … leaked at exit`. Don't treat those lines as failures; gate on
  the exit code and your own assertions.
- `--export-release <preset> <path>` needs `export_presets.cfg` and export templates (not tested; templates are a
  large separate download).
- The metallic barrel rendered **black** in Godot Compatibility and in three.js because there was no environment
  or reflection source. This is a real "looks bad" trap (pass it to Agent 3): metallic PBR needs an
  environment/IBL.

### 3.5 Web game verification (ran)
`SCRATCH/tooltest/npm/shot.mjs`: Playwright headless Chromium, console capture, wait for `window.__done`, then a
screenshot.
```bash
npm i -D playwright@1 three && npx playwright install chromium     # 120 MiB headless shell, worked through proxy
node shot.mjs out.png                                               # no extra flags needed
```
- Console reported `GL_RENDERER ANGLE (Google, Vulkan 1.3.0 (SwiftShader Device (Subzero)…)) webgl2= true`,
  `GLB_MESHES 2`, `FPS 59.1 calls 2 tris 168`. `--enable-unsafe-swiftshader` made no difference with this build.
- Warnings like `GPU stall due to ReadPixels` come from screenshotting. Filter them out of "console must be clean"
  gates.
- Rule: use headless SwiftShader for **correctness and screenshots**. Never use it for FPS or GPU-time budgets.
  Measure performance on real hardware (Chrome DevTools MCP traces on the user's desktop).

**MCP setup (from READMEs):**
```bash
claude mcp add chrome-devtools --scope user npx chrome-devtools-mcp@latest   # add --slim --headless for basics
# or plugin with skills:  /plugin marketplace add ChromeDevTools/chrome-devtools-mcp
#                         /plugin install chrome-devtools-mcp@chrome-devtools-plugins
# privacy: add --no-usage-statistics (on by default; auto-off when CI env set) and --no-performance-crux
claude mcp add playwright npx @playwright/mcp@latest    # flags: --headless --isolated --caps vision
```

### 3.6 glTF / texture pipeline (ran)
```bash
npm i -D @gltf-transform/cli gltfpack gltf-validator
export NO_COLOR=1
npx gltf-transform inspect  m.glb                 # tables: meshes, vertices, materials, textures, sizes
npx gltf-transform validate m.glb                 # Khronos validator; got 0 errors, 2 infos (UNUSED_OBJECT TEXCOORD_0)
npx gltf-transform optimize m.glb m_opt.glb --compress meshopt --texture-compress webp   # 8.53 KB → 4.3 KB
npx gltfpack -i m.glb -o m_pack.glb -cc -kn -km -ke   # -kn/-km/-ke keep named nodes/materials/extras
node validate.mjs m.glb   # validator.validateBytes → {errors,warnings,infos,hints}; gate on errors==0
```
- Observed: plain `gltfpack -cc` produced "2 nodes → 1 nodes, 2 meshes → 1 mesh". Hierarchy and names were lost.
- The validator reported `UNSUPPORTED_EXTENSION` (info) on the gltfpack output because it does not validate meshopt
  extensions. **Run validation on the pre-compression file**, then smoke-test the compressed file in the target
  engine. Engine support for `EXT_meshopt_compression` / `KHR_mesh_quantization` in Godot is [UNVERIFIED]. Three.js
  needs `MeshoptDecoder` set on GLTFLoader.
- Bevelled "crate" (cube) exported as 108 render vertices vs 72 for a 16-segment cylinder. `inspect` gives the
  numbers a QA agent should log per asset.

KTX2 (KTX-Software 4.4.2 tarball from GitHub releases; contains `ktx`, `toktx`, `ktx2check`, `ktxinfo`, `ktxsc`):
```bash
tar xjf KTX-Software-4.4.2-Linux-x86_64.tar.bz2; K=$PWD/KTX-Software-4.4.2-Linux-x86_64
export PATH=$K/bin:$PATH LD_LIBRARY_PATH=$K/lib
ktx create --format R8G8B8_SRGB --assign-tf srgb --encode basis-lz --generate-mipmap albedo.png albedo.ktx2   # 1.39 MB→54 KB
ktx create --format R8G8B8_SRGB --encode uastc --zstd 18 --generate-mipmap in.png out.ktx2                   # →337 KB
ktx info out.ktx2        # "Validation successful"
```
- Trap I observed: with a 16-bit PNG, `ktx create` "defaulting to KHR_DF_TRANSFER_LINEAR". Pass `--assign-tf srgb`
  for colour maps. Normal/ORM maps must be linear (`R8G8B8_UNORM`) and preferably UASTC.
- `gltf-transform etc1s|uastc` require KTX-Software on PATH ("Dependencies: KTX-Software" in its help).

### 3.7 Frame/visual QA utilities (ran)
```bash
ffmpeg -y -framerate 30 -i f%08d.png -c:v libx264 -pix_fmt yuv420p clip.mp4
ffmpeg -y -i clip.mp4 -vf "select='not(mod(n\,3))',scale=320:-1,tile=2x2" -frames:v 1 -fps_mode vfr sheet.png
montage render_*.png -tile 3x1 -geometry +4+4 contact.png      # ImageMagick 6: use montage/convert, NOT `magick`
```
`-label '%f'` printed no labels here [cause unverified, probably fonts]. Annotate with ffmpeg `drawtext` or
Pillow if labels matter.

### 3.8 3D generation services: facts for decisions

| Service | Access for Claude Code | Cost (verified) | Topology / PBR | Rigging / animation | Licence of outputs |
|---|---|---|---|---|---|
| **Meshy** | Official MCP `@meshy-ai/meshy-mcp-server`: `claude mcp add meshy --env MESHY_API_KEY=msy_… -- npx -y @meshy-ai/meshy-mcp-server`; API keys need a **paid** plan | API credits: image→3D 20 (mesh only) / 30 (2K–4K tex) / 35 (8K) on meshy-7.1/6; 5–15 on meshy-6-lite/t2; text→3D preview 20 + refine 10; remesh 5; UV unwrap 5; auto-rig 5; animation 3 per action; convert/resize 1. Failed tasks are not charged. DELETE of an in-progress task now returns 409 and the credits are kept. USD plan prices [UNVERIFIED, meshy.ai unreachable] | Remesh `topology: quad|triangle`, `target_polycount` (default 30,000); `geometry_resolution` 2k/4k (+5) | "only works well with standard humanoid (bipedal) assets"; rig input ≤300k faces | Free: **CC BY 4.0** (attribution); Pro+: private, full commercial; "User owns output" |
| **Tripo** | REST v3 `https://openapi.tripo3d.com/v3`; official `tripo-mcp` is **alpha** and needs the Tripo Blender add-on | Credits frozen at task creation, refunded on fail/cancel; per-task amounts [UNVERIFIED] | P-series low-poly: P2 48–50,000 tri / 48–25,000 quad; standard `smart_low_poly` 500–20,000 tri; `pbr` = base_color/metallic/roughness/normal; `quad:true` forces FBX; smart retopology `mesh/decimate` with `bake` | rig types biped, quadruped, hexapod, octopod, avian, serpentine, aquatic; `spec: mixamo`; retarget presets | Free-tier commercial terms **conflicting across sources [UNVERIFIED]** |
| **Hyper3D Rodin** | API only on Business plan; ahujasid MCP integrates it | Free: pay-per-result, $1.50/credit; Creator $30/mo ($24 yearly), "About 60 models", "Unlimited export and any use"; Business $120/mo ($96 yearly), "Full API access", "High-Poly Quads", 120/240 RPM | Smart Low-Poly, baked normals (Creator+) | [UNVERIFIED] | Paid plans "broader export and usage rights" |
| **Hunyuan3D** | Open weights 2.0/2.1 (local GPU); Tencent Cloud AI3D API (via ahujasid MCP); Higgsfield `hunyuan3d_v3*` | — | Higgsfield v3 params: face_count 40k–1.5M (default 500k); `generate_type: LowPoly` + `polygon_type: quadrilateral` | — | **Open-weights licence: Territory excludes EU, UK, South Korea; "must not use… Output… outside the Territory"; >1M MAU needs a Tencent licence** |
| **Higgsfield `generate_3d`** | Connected here. Models: `sam_3_3d` (Meta), `image_to_3d`/`multi_image_to_3d`/`3d_rigging` (Meshy-backed), `tripo_3d`, `tripo_h3_1_*`, `hunyuan3d_v3*`, `meshy_v6_text_to_3d`, `meshy_v7_image_to_3d`, `meshy_v5_remesh/retexture`; 678-clip animation library | Credits; `get_cost:true` preflights cost (not called) | Meshy-backed: `topology`, `target_polycount` 100–300,000, `pose_mode a-pose|t-pose` | Meshy humanoid rig; tool text: "non-bipeds… may rig poorly" | [UNVERIFIED] |
| **Higgsfield 3D Jutsu** | `scene_builder_3d_*` (hosted Blender 5.2) | `generate_angles`/`generate_video` spend credits; run/query cost [UNVERIFIED] | — | — | [UNVERIFIED] |

3D Jutsu limits (from its `/3d-jutsu` instructions, read via free `get_preset_instructions`): headless bpy 5.2;
about 5 min per operation; code ≤256 KiB; **no network**; models only from the curated catalog ("cannot import a
user's own file"); ≤8 PNG/JPEG/MP4 artifacts per operation; optimistic-concurrency guards (`revision`,
`sceneSequence`); "glTF carries only Sun, Spot and Point lights; Area lights are dropped"; "Procedural shader graphs
do not generally survive glTF". Its rule "A succeeded mutation proves the code ran, not that the scene is right.
Render… look at it…" is a good QA principle to borrow.

### 3.9 Asset sources (only what was verified)
- **Poly Haven:** about 2,400 HDRIs, textures and models, all CC0, no key, no meaningful rate limit. The API ToS asks
  software built on the live API to "make clear where the assets come from" (ahujasid README, linking
  github.com/Poly-Haven/Public-API ToS). Models are best taken from the `.blend` source. Prefer 1k/2k resolution.
- **Poly Pizza:** about 10,600 low-poly GLBs, free API key, **about 69% CC-BY** (credit required), filter
  `licence="CC0"`. `static.poly.pizza` sits behind Cloudflare bot protection that **blocks datacenter/VPN/cloud
  IPs**, so expect failures in cloud sessions.
- Kenney, Quaternius, KayKit, ambientCG, Sketchfab licence filters, Mixamo automation/ToS, ElevenLabs/audio MCPs:
  **[NOT RESEARCHED: run cut short]**. The lead should verify these before writing rules about them. Search only
  surfaced `squall01337/mixamo-llm-mocap` (350★, video→Mixamo-rig via Blender MCP), which I did not open.

---

## 4. Failure modes & anti-patterns (with countermeasures)

| Failure | Evidence | Countermeasure |
|---|---|---|
| Making the pipeline depend on a GUI-only MCP in a cloud session | ahujasid add-on refuses `bpy.app.background` | Default to `blender -b -P`/bpy scripts. Use MCP only when the user is on a desktop |
| Two Blender MCPs fighting for port 9876 | ahujasid issue #339 thread (port conflict with "official BlenderLabs addon") | Install one Blender MCP. If you need both, set a different `--port` |
| Hanging tool calls treated as "Blender is slow" | #339: every call takes about 4–5 min on Blender 5.1+/5.2 | Use a timeout plus a fallback to the headless script path |
| "Code ran, so done" | Higgsfield 3D Jutsu rule; official prompts.yml | Always render from the delivery camera and **look** at the image before claiming done |
| Trusting SwiftShader/llvmpipe FPS | 59 FPS rAF cap under SwiftShader (ran) | Perf budgets are measured only on real GPUs. Headless runs are for correctness |
| Metals render black | Godot Compatibility + three.js renders (ran) | Every scene needs an environment/IBL (HDRI or probe) before material review |
| Compression destroys hierarchy | `gltfpack -cc` merged nodes (ran) | `-kn -km -ke`, or gltf-transform with explicit steps. Validate before compressing |
| Colour textures encoded linear | `ktx create` 16-bit PNG warning (ran) | `--assign-tf srgb` for albedo/emissive. UNORM/linear for normal/ORM |
| Draco expected from Blender export in bpy wheel | missing bridge `.so` (ran) | Compress after export with gltf-transform/gltfpack |
| Godot movie capture silently produces nothing | Output dir missing; `--resolution` ignored (ran) | `mkdir -p` first; set window size in project.godot; check frame count afterwards |
| Shipping free-tier AI assets in a commercial game | Meshy Free = CC BY 4.0; Tripo terms conflicting; Hunyuan territory clause | Record generator, plan and licence per asset in an `ASSET_LICENSES` manifest. Block EU/UK/KR use of Hunyuan open-weights outputs |
| Auto-rigging non-humanoids with Meshy | Meshy docs: humanoid only | Use Tripo `rig_type` for creatures, or rig in Blender by script |
| Burning credits on retries | Meshy: cancel after start keeps credits; Higgsfield: "do not automatically resubmit" on timeout | Preflight cost (`get_cost`), poll by job id, never blind-retry paid calls |
| Context bloat from many MCP servers | ahujasid 6,928-token schemas (#347); Chrome DevTools ~57 tools; Playwright README's own warning | Enable MCPs per phase. Use `--slim` or tool groups. Prefer CLI where equivalent |
| Telemetry or data leakage | ahujasid T&C (training use); Chrome DevTools usage stats on by default; godot-ai telemetry | Set `DISABLE_TELEMETRY=true`, `--no-usage-statistics`, `--no-performance-crux`, `GODOT_AI_DISABLE_TELEMETRY=true` |
| Arbitrary code execution | Every Blender/engine MCP exposes `execute_*`; Blender Lab sandbox is "a slap on the wrist" | Work on copies of .blend files; dedicated output dir; no secrets in the workspace; ahujasid `BLENDER_MCP_SAFE_MODE=1`; keep sockets on localhost |

---

## 5. Hype vs reality / honest gaps

- **"Blender MCP lets Claude model anything."** The MCP is a pipe to `bpy`. Model quality comes from the script and
  the render-review loop (Agents 2/3), not the transport. Both MCP READMEs say the AI writes Blender Python itself.
- **Star counts are not maturity.** ahujasid (30k★) has an unresolved timeout bug on current Blender. The official
  server is younger but authored by Blender core devs, and it is deliberately minimal.
- **Coding-Solo/godot-mcp** (6k★) adds little over `godot --headless` and had its last commit in April 2026.
  **chongdashu/unreal-mcp** (2k★) is abandoned since April 2025.
- **Engine MCPs need a running editor.** That is fine on a desktop but not in a container. godot-ai documents an SSH
  bridge for agents in containers; Unity's relay needs the editor plus connection approval.
- **The Unity official MCP is beta**, needs Unity 6+ and AI Assistant 2.11.0-pre. Whether a subscription is required
  is reported only by secondary sources [UNVERIFIED].
- **The Epic official MCP plugin (UE 5.8, experimental)** is known only from search snippets quoting Epic's recap. The
  page returned 403 [UNVERIFIED].
- **AI-generated meshes**: none of the vendors' docs claim game-ready topology out of the box. All offer
  remesh/retopology as a separate paid step, and rigging is humanoid-first. Treat outputs as raw material that must
  pass the same validation (tri budget, scale, UVs, naming) as anything else.
- **fnf-blender-mcp** README itself says "Windows/Linux native Blender execution has not been verified locally".
- **bpy-dev/blender-mcp** is a self-described "developer preview" fork; its `_for_cli` tools are not in upstream.

---

## 6. Recommendations for the skill

### Tiered toolchain

**Essential (works in cloud and desktop; no MCP):**
1. Headless Blender: `blender -b --factory-startup -P script.py --python-exit-code 1 -- …`, or `pip install bpy==5.2.2`
   (Python 3.13) when blender.org is unreachable.
2. glTF gate: `npx gltf-transform inspect|validate` (Khronos validator, `errors==0`), then
   `optimize`/`gltfpack -kn -km -ke`.
3. Visual QA: render PNG (Workbench for form, EEVEE/Cycles for look), contact sheets with ffmpeg `tile` /
   ImageMagick 6 `montage`, and Claude reads the images.
4. Engine CLI: Godot `--headless --import`, `--headless --script` tests, `xvfb-run … --rendering-driver opengl3
   --write-movie`. For web games, a Playwright script capturing screenshot + console + `pageerror`.

**Recommended:**
- Chrome DevTools MCP (web games: perf traces, Lighthouse, console). Use `--slim --headless` for routine checks and
  full mode on a GPU desktop for perf.
- KTX-Software (`ktx create`) for KTX2/Basis textures.
- Desktop only, one Blender MCP: the **Blender Lab official MCP** (Blender ≥5.1) for inspection/debugging. Use
  ahujasid `mcp-for-blender` only if you need its asset search/import or `look` views, with
  `BLENDER_MCP_SAFE_MODE=1` and `DISABLE_TELEMETRY=true`.
- Desktop engine MCP matching the engine: hi-godot/godot-ai (Godot 4.7+), CoplayDev/unity-mcp or Unity's official
  MCP (Unity 6+).
- Poly Haven (CC0 HDRIs/textures) for lighting/material realism.

**Optional (paid or situational):** Meshy MCP (humanoid characters + rig + animations; Pro+ for commercial
privacy), Tripo API (low-poly P-series, creature rigs), Higgsfield `generate_3d`/3D Jutsu (already connected; check
cost with `get_cost:true` first), Rodin (Business plan), Poly Pizza (CC-BY attribution; blocked from cloud IPs),
Playwright MCP (prefer the CLI/script), fnf-blender-mcp.

**Avoid:** chongdashu/unreal-mcp (stale); Coding-Solo/godot-mcp (redundant with CLI); tripo-mcp (alpha, add-on
dependent); running two Blender MCPs on port 9876; Hunyuan3D open-weights outputs for EU/UK/KR users or >1M MAU
products; free-tier AI assets in commercial builds without licence records; SwiftShader/llvmpipe FPS as perf
evidence. Mixamo scraping: ToS risk [UNVERIFIED, not researched].

### Task → tool matrix

| Task | Cloud / CI container | Desktop with GUI |
|---|---|---|
| Procedural modeling / export GLB | bpy / `blender -b -P` (tested) | same; optionally a Blender MCP for live viewing |
| Inspect an existing .blend | `blender -b file.blend -P inspect.py` | Blender Lab MCP `get_blendfile_summary_*`, `get_objects_summary` |
| Visual check of a model | Render Workbench + EEVEE PNG turntable → contact sheet (tested) | ahujasid `look(mode="angles")` or official screenshots |
| Validate / optimize glTF | gltf-transform + validator + gltfpack (tested) | same |
| Texture compression | KTX-Software `ktx create` (tested) | same |
| Import into Godot + tests | `--headless --import`, `--headless --script` (tested) | godot-ai `test_run`, `editor_screenshot` |
| Gameplay video / frames | Xvfb + `--rendering-driver opengl3 --write-movie` (tested) → ffmpeg | same, or editor MCP screenshots |
| Web game screenshot + console | Playwright script (tested) or Chrome DevTools MCP `--headless` | Chrome DevTools MCP full |
| Web perf budget | not meaningful (SwiftShader) | Chrome DevTools `performance_*` traces, Lighthouse |
| Unity scene/editor work | not practical | CoplayDev unity-mcp / Unity MCP (beta) |
| HDRIs / CC0 textures | Poly Haven API | Poly Haven via ahujasid `search_assets` |
| Low-poly props quickly | own procedural bpy; Poly Pizza likely blocked | Poly Pizza (attribute CC-BY) |
| Humanoid character + rig + clips | Meshy API/MCP or Higgsfield `generate_3d` (paid) | same |
| Creature rig | Tripo `rig_type` (paid) or scripted Blender rig | same |

### What to leave out
- Don't hard-code any one MCP as required, and don't bundle MCP configs that load more than one or two servers at
  once.
- Don't include star counts or prices in the skill text. They change monthly. Point to the vendor's pricing page
  and require a cost preflight.

---

## 7. Videos found but not watchable
- ahujasid README setup/demo videos: youtube.com/watch?v=neoK_WMq92g (Claude Desktop setup), wgWsJshecac (Cursor),
  DqgKuLYUv00 (low-poly dungeon), I29rn92gkC4 (Poly Haven beach), FDZ5fr2QkP (reference image → scene),
  jxbNI5L7AH8 (scene → three.js). The README captions are the only text about them.

---

## 8. Sources
- Research plan: SCRATCH/research/00-research-plan.md
- github.com/ahujasid/mcp-for-blender (README, addon.py, src/blender_mcp/server.py, TERMS_AND_CONDITIONS.md, pyproject.toml); issues #339, #347, #360 and issue list page
- github.com/bpy-dev/blender-mcp (readme.md, NOTICE.md, readme_tools.rst, SECURITY.md; upstream commit 4309a39 files: blender_manifest.toml, prompts.yml, cli.py, weak_sandbox.py, mcp/pyproject.toml)
- anthropic.com/news/claude-for-creative-work
- npm registry: fnf-blender-mcp 0.2.2 (README, UPSTREAM.md, skills/), @gltf-transform/cli 4.5.1, gltfpack 1.3.0, gltf-validator 2.0.0-dev.3.10, playwright 1.x, three 0.180.0
- pypi.org/pypi/bpy/json (versions, wheels, licence)
- github.com/godotengine/godot/releases (4.7.2-stable) and the binary's `--help`
- github.com/KhronosGroup/KTX-Software/releases/latest and expanded_assets/v4.4.2
- github.com/Coding-Solo/godot-mcp, github.com/hi-godot/godot-ai (README, docs/TOOLS.md), github.com/CoplayDev/unity-mcp
- docs.unity3d.com/Packages/com.unity.ai.assistant@2.11/manual/integration/{mcp-overview,unity-mcp-get-started}.html; unity.com/en/blog/unity-ai-mcp-how-to-get-started (dated May 11, 2026, intro only)
- github.com/microsoft/playwright-mcp (README), github.com/ChromeDevTools/chrome-devtools-mcp (README, docs/tool-reference.md, docs/client-configurations.md)
- docs.meshy.ai/api/pricing.md, /en/api/changelog.md, /api/ai.md, /api/remesh.md, /api/rigging.md, /llms-full.txt (licensing table)
- developers.tripo3d.com/en/docs/{billing,introduction,animations-rig,mesh-decimate,generation-image-to-model/p,generation-image-to-model/standard}.md, /llms.txt; github.com/VAST-AI-Research/tripo-mcp README
- hyper3d.ai/pricing (text fetched via curl)
- raw.githubusercontent.com/Tencent-Hunyuan/Hunyuan3D-2.1/main/LICENSE and Hunyuan3D-2/main/LICENSE
- Higgsfield MCP tool descriptions (ToolSearch) and free read-only calls: models_explore(list, 3d), get_preset_instructions(/3d-jutsu, /3d-jutsu/references/composition-modeling, /use-blender, /use-blender/references/installation)
- GitHub repository search results (star counts) for "blender mcp", "godot mcp", "unity mcp", "unreal mcp", "tripo mcp", Tencent-Hunyuan
- Secondary only (not relied on for verified claims): web search snippets about Epic UE 5.8 MCP plugin, Unity MCP subscription requirement, Tripo/Rodin third-party pricing, strayspark.studio blog
