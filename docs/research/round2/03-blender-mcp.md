# 03 — Live Blender MCP playbook (Round-2 Research Agent 3)

Scope: install guide plus operating procedure for a live Blender MCP in the Claude desktop app (Chat and Code tab) and
Claude Code, with Blender installed locally. Builds on docs/research/05-mcp-tools.md §3.1–3.3; it does not repeat them.
All sources were fetched on 2026-10-10. Raw downloads are in SCRATCH/downloads2/3/.

## 1. Summary

- **The official connector is real and simple.** It is the Blender Lab MCP, listed as "Anthropic verified" in the Claude
  directory as `ant.dir.gh.blender.blender-mcp`. In Claude Desktop: **Customize > Connectors > search "Blender" > Add**.
  In Blender: **drag the install link from blender.org/lab/mcp-server into Blender twice** (once for the repository, once
  for the add-on). It needs **Blender 5.1+**. The add-on is mcp-1.0.3 with `blender_version_min=5.1.0`.
  [blender.org, claude.com tutorial, classmethod]
- **Claude Code gotcha (tested by classmethod).** `claude mcp add-from-claude-desktop` does **not** import the connector,
  because the connector is a `.mcpb` desktop extension and not a `claude_desktop_config.json` entry. Register the
  extension's own binary with `claude mcp add` instead. The Code tab of the desktop app reads `claude_desktop_config.json`,
  `~/.claude.json` and `.mcp.json`. Whether it also sees desktop *extensions* is [UNVERIFIED].
- **Recommended default: the official Blender Lab connector** [judgment]. Reasons:
  1. ahujasid has an **open, unresolved bug (#339)**: every call takes 4–5 min on Windows with Blender 5.1/5.2, which is
     beyond Claude Desktop's limit of about 4 min. Blender 4.5 and 5.0 work.
  2. The official one is one-click and comes from the Blender developers.
  3. It sends no telemetry.
  4. It has API and manual doc search, which cuts down on bpy hallucination.

  Use ahujasid only on Blender ≤ 5.0, or when its `look` multi-angle tool or asset import is worth that risk.
- **Never run both.** Both default to **port 9876**. In #339 the two add-ons were "competing for the same port", and
  uninstalling one fixed it. Both add-ons run *inside the same Blender process*, so "only one PID listens on 9876" does
  **not** rule out a clash [judgment]. Their port environment variables also differ: official `BLENDER_MCP_PORT`,
  ahujasid `BLENDER_PORT`.
- **Every step can run late.** The official server's socket timeout is 300 s and ahujasid's is 180 s. Claude Code
  stdio servers default to an idle timeout of about 30 min, and a call that runs past 2 min moves to the background.
  When a call is cancelled, it **can still execute in Blender later** (#339: a result came back about a minute after the
  client cancelled). So build steps must be idempotent, and the agent must inspect the scene before any retry.
- **The context cost of a live session is the real limit.** In a documented 2-hour connector session (Theoretically
  Media), about 60% of a Max-5x session budget was used. Output degraded: the camera changed, magenta textures appeared,
  Claude "congratulating itself", with clipping and wrong scale throughout. Countermeasures:
  - Keep state on disk: the build script, versioned .blend files and notes.
  - Use small images (max_size 512).
  - Use contact sheets instead of many screenshots.
  - Start fresh sessions.
- **ahujasid's bundled guides are switched off** in its current server ("switched off while evals measure what the model
  does without them"), so `get_guide` is not callable. Their best rules are distilled in §2.4.
- **Validation must run outside the live session.** The skill's headless scripts call `read_factory_settings`
  (`gs_common.py:42`), which would wipe the user's scene. Export a GLB from the live session, then run the scripts in a
  **separate** `blender -b --factory-startup` process.
- **Ask the live Blender for its own binary path** with `bpy.app.binary_path`. This is the most reliable way to find the
  CLI executable, and it guarantees the same version. Fall back to OS default paths (§2.6).
- **Name trap:** `uvx blender-mcp` on PyPI runs **ahujasid's** server (the old name), not the official one, even though
  the official package's entry point is also called `blender-mcp`.

## 2. Ready-to-use additions for the skill

### 2.1 Install guide: official Blender Lab connector (DEFAULT)

Requirements: Blender **5.1 or newer** [blender.org; the manifest and download link say `blender_version_min=5.1.0`]. The
Anthropic tutorial says "4.2 or later", which contradicts the add-on's own manifest, so trust 5.1. Claude Desktop works
on any plan, including Free. The connector does not work on claude.ai in a browser [claude.com tutorial FAQ].

1. **Claude Desktop:** Customize > Connectors → search **Blender** → **Add** [claude.com tutorial]. An older UI path,
   Settings > Connectors, appeared under "Anthropic & Partners" in classmethod's test.
2. **Blender add-on:** open https://www.blender.org/lab/mcp-server/ beside Blender and **drag the install link into the
   Blender window**. The first drop adds the Blender Lab extension repository (allow it). The **second drop** installs the
   add-on. Alternative: download the zip and use *Install from Disk* (no update notifications) [blender.org].
3. **Start it:** Edit > Preferences > Add-ons > **MCP** → shows Host `localhost`, Port `9876`, **Auto Start**, and
   "Server is running" [classmethod]. The tutorial says to start the connection from inside Blender each session.
4. **Smoke test, read-only:** "List the objects in the current scene". A default file returns Camera, Cube and Light
   [classmethod].
5. **Claude Code CLI, or a project `.mcp.json`:** the connector's files live in the Claude Extensions folder.
   macOS (tested): `~/Library/Application Support/Claude/Claude Extensions/ant.dir.gh.blender.blender-mcp/.venv/bin/blender-mcp`.
   ```bash
   claude mcp add --scope user blender -- "$HOME/Library/Application Support/Claude/Claude Extensions/ant.dir.gh.blender.blender-mcp/.venv/bin/blender-mcp"
   claude mcp list      # expect: blender ✓ Connected
   ```
   Windows equivalent, probably `%APPDATA%\Claude\Claude Extensions\ant.dir.gh.blender.blender-mcp\.venv\Scripts\blender-mcp.exe`,
   is **[UNVERIFIED]**. Check that the folder exists before using it. From source:
   `uv --directory /abs/blender_mcp/mcp run blender-mcp` (round 1). **Do not** use `uvx blender-mcp`, which installs
   ahujasid's server.
6. **Optional timeout in `.mcp.json`:** `"timeout": 120000` per server. This is a hard wall-clock limit per call. Values
   below 1000 are ignored. Global variable: `MCP_TOOL_TIMEOUT`. The idle timeout is `CLAUDE_CODE_MCP_TOOL_IDLE_TIMEOUT`
   [code.claude.com/docs/en/mcp].

Tools: see round 1 §3.2 for the 20 upstream tools. The developer fork (bpy-dev) adds `*_for_cli` variants and
`get_runtime_python_api_docs`; whether upstream 1.0.3 has these too is [UNVERIFIED]. Upstream has **no** multi-angle
`look`, **no** asset import and **no** export tool. Instead:
- For images: `render_thumbnail_to_path` / `render_viewport_to_path`, then Read the PNG, or
  `get_screenshot_of_area_as_image`.
- For export: `bpy.ops.export_scene.gltf` via `execute_blender_code`.

Its sandbox (`weak_sandbox.py`) blocked `bpy.ops.wm.read_factory_settings` in a hands-on test [classmethod]. Nothing else
is guarded: "will execute LLM generated code in Blender without any guards ... recommended to use a virtual machine, or a
system without access to sensitive information" [blender.org].

### 2.2 Install guide: ahujasid mcp-for-blender (ALTERNATIVE; only one at a time)

Use it when the user is on Blender ≤ 5.0 (3.0+ supported), or explicitly wants `look`, Poly Haven, Sketchfab or Poly Pizza.
Avoid it on Blender 5.1/5.2 under Windows until #339 is closed.

- One-command setup (lead-verified): `uvx mcp-for-blender setup`, or install.sh / install.ps1. This writes Claude Desktop
  and Claude Code configs, then installs and enables the add-on. Afterwards **fully quit the app**; on Windows that means
  quitting from the system tray [README].
- Recommended env:
  - `DISABLE_TELEMETRY=true` (turns off even the anonymous usage record)
  - `BLENDER_MCP_SAFE_MODE=1`
  - args `--python 3.11` plus `UV_PYTHON_PREFERENCE=only-managed` (avoids conda/pyenv conflicts)
  - On Windows GUI apps, use the full `uvx.exe` path or `"command":"cmd","args":["/c","uvx","mcp-for-blender"]` to avoid
    `spawn uvx ENOENT` [README].
- Decline the "one-time opt-in prompt" for content telemetry that some clients show. Opted-in data "may be used ... to
  train AI models" [README].
- Every tool has a `user_prompt` field that is meant to hold the user's words verbatim and is captured for trajectory and
  telemetry. With telemetry off this is harmless. Never put secrets in it.
- Safe mode allows only bpy, bmesh, mathutils and pure stdlib. It blocks eval/exec/open, os/subprocess/network,
  handlers/timers/drivers, class/property registration, and external .blend loading. **Rendering, saving and
  import/export operators are allowed** [server.py]. Consequence: in safe mode you cannot `exec(open(build.py))`. Send the
  file's text as the `code` argument instead.
- Before installing, check for leftovers of the other server: Preferences > Add-ons, search "MCP". Keep exactly one MCP
  add-on enabled.

### 2.3 Session bootstrap (agent procedure, every session)

1. **Detect.** `ToolSearch "blender"`, then classify:
   - **Official** if `get_objects_summary` / `search_api_docs` / `render_thumbnail_to_path` exist.
   - **ahujasid** if `look` / `get_scene_info` / `get_addon_status` exist.
   - **Neither:** use the headless CLI path (§2.6). Don't ask the user to install anything mid-task. Offer it once.
   - **Both:** stop and tell the user to disable one (port 9876).
2. **Handshake with one read-only call** (`get_objects_summary`, or `get_addon_status` + `get_scene_info`). If the first
   call fails, retry once: "Sometimes the first command won't go through" [ahujasid README]. If the second also fails or
   takes over 60 s, switch to headless and say why.
3. **Read the environment in a single `execute_blender_code` call** that returns a dict:
   `bpy.app.version_string`, `bpy.app.binary_path`, `bpy.data.filepath`, `bpy.data.is_dirty`,
   `scene.unit_settings.system/scale_length`, `scene.render.engine`, object count, mode.
   - Keep `binary_path` for the CLI checks (§2.6).
   - If the version is ≥ 5.1 and the server is ahujasid on Windows, warn about #339.
4. **Protect the user's file.**
   - If `is_dirty`, ask the user to save first.
   - Then `bpy.ops.wm.save_as_mainfile(filepath="<project>/art/blend/<asset>_work.blend")` so the session continues on a
     project copy and the original is never written.
   - For a new asset, start from a new file saved into the project.
   - Never call `read_factory_settings` / `read_homefile` in the live session.
5. **Inspect before acting.** Walk the collections and objects, then read details progressively. Don't dump the scene.
   Official rules: "NEVER assume missing values - inspect the scene first", "Do not destructively modify objects without
   confirmation", "Respect existing structure and naming conventions" [prompts.yml].

### 2.4 Build loop (live)

**Source of truth = a build script on disk:** `art/src/<asset>/build_<asset>.py`. The live session only executes it.

1. **Write a brief first** [Nik Bear Brown course, 05:00–05:15]:
   - size in metres (justified against the player, a door or a tile)
   - origin (bottom-centre for floor props)
   - triangle budget
   - materials
   - 3 predicted failures, each with the check that catches it
2. **Script structure (idempotent):**
   - The script owns one collection `GS_<asset>`. On each run it deletes that collection's objects and orphan data it
     created, then rebuilds. It never touches anything else.
   - It **returns a compact dict** (per-part name, dims, tris, materials). Official rule: "Return compact structured
     results ... avoid scene dumps and print output" [prompts.yml].
   - Parameters (seed, sizes) go at the top.
3. **Step size:** one part or one logical operation per `execute_blender_code` call. Grow the script by appending
   functions, and re-run the whole script when cheap. Aim for calls under ~150 lines that finish in a few seconds
   [judgment]. Rationale: "Complex operations might need to be broken down into smaller steps", and for timeouts,
   "breaking them into smaller steps" [ahujasid README]. The ahujasid tool description says: "Work in small steps and
   print what you need to know" [server.py].
4. **After each step, read numbers before looking at pictures:** location, size (world bbox), ground contact, rotation,
   scale, tris.
   - With ahujasid, use `get_scene_info(fields=["size","ground","topology"], query=...)`.
   - Mind the triangle traps. Default primitives in Blender 5.1 are cube 12, cylinder 124, **UV sphere 960** tris;
     12×6 segments gives 120 [Nik Bear Brown, 01:30–01:50].
   - Note that the official site's own example LLM analysis missed a Solidify modifier, so evaluate modifiers
     (depsgraph) when counting [blender.org].
5. **Look from fixed angles every step, small:**
   - **ahujasid:** `look(mode="angles", target=["GS_<asset>"], views=["front","right","top","three_quarter"],
     max_size=512)`. For materials, use `shading="material"` (solid shading shows only the viewport colour). For
     topology, use `wireframe`. For rigs, use `xray`.
   - **Official:** keep a review camera `GS_ReviewCam` at a fixed transform. Call `render_thumbnail_to_path("<project>/
     review/<asset>/step_NN.png")`, then Read it.
   - **Both:** every 3–5 steps, or at milestones, export GLB and run `render_views.py` headless (§2.5) for the
     9-view contact sheet. One image replaces many screenshots.
6. **Version saves.** At milestones use `bpy.ops.wm.save_as_mainfile(filepath=".../<asset>_v003.blend", copy=True)`,
   which saves a copy and keeps the working file open. Commit the build script with the same version number.
7. **Change only what was asked.** Don't move the camera, swap textures or "improve" unrequested parts. The documented
   session drifted on cup handle, camera and exposure because Claude changed unrequested things [Theoretically Media,
   03:55–05:50].
8. **Retry discipline.** On timeout or cancel, **do not resend**. First inspect: did the step run? Was there a duplicate
   `.001` object? The old call may still complete later [#339]. Then re-run the idempotent script, not a delta.
9. **Long or heavy operations go to the CLI, not the live socket:**
   - final renders and bakes
   - QuadriFlow/voxel remesh of dense meshes
   - big imports and batch exports

   Run them with `blender -b <saved copy>.blend -P job.py` [judgment, consistent with ahujasid "Timeout errors"
   advice and the note.com guide's split of MCP for building vs CLI for rendering; the note.com guide was not opened
   in full].
10. **Context hygiene.**
    - Default `max_size` 512. Each image stays in context; a 768-px image costs roughly 800 tokens [judgment, standard
      vision-token estimate].
    - Use one contact sheet per milestone.
    - When the session gets long, write a `NOTES.md` handoff (state, next step, open issues) and continue in a fresh
      session from the script and the .blend.

**bpy rules worth pasting** (from ahujasid guides `bpy.md`/`materials.md`/`scene.md`/`retopology.md`/`rigging.md`/
`animation.md`/`level-design.md`, MIT, and the official `prompts.yml`, GPL — paraphrase, don't copy verbatim):

- **Version-proofing**
  - Find nodes by `type`, never by name (names are localized). Example:
    `next(n for n in nodes if n.type=="BSDF_PRINCIPLED")`.
  - Resolve renamed sockets defensively: `inputs.get("Emission Color") or inputs.get("Emission")` (4.0 renames).
  - Never hardcode enums; read `bl_rna.properties[...].enum_items`.
  - The render engine under-reports. Assign it in `try/except TypeError` (the error lists valid values). EEVEE is
    `BLENDER_EEVEE_NEXT` in 4.2–4.x and `BLENDER_EEVEE` otherwise.
  - 5.0 removed `Action.fcurves`. Use `obj.keyframe_insert(...)` and
    `anim_utils.action_get_channelbag_for_slot(...)` on 4.4+.
  - In 5.0+ `material.use_nodes` is always on.
- **Context**
  - Code runs from a timer, not a UI area. Viewport operators need
    `bpy.context.temp_override(area=..., region=..., active_object=..., selected_objects=[...])`.
  - Set mode, active and selection explicitly before each operator, and re-set them between operators on different
    objects.
  - Return to OBJECT mode in `finally`.
  - Edit-mode geometry goes through bmesh, and you must flush it back ("forgetting this silently loses all edits").
  - Update the depsgraph before reading computed values.
- **Naming:** Names auto-suffix `.001`, so capture references at creation and never look up an assumed name. Name
  everything. Use one collection per logical group.
- **Scale:** Units are metres. Reference sizes: door 2.1 m, table 0.75 m, person 1.7 m. Apply scale and rotation
  before modifiers that depend on it, rigging and export. Use `obj.copy()` (linked data) for repeats. Shared mesh
  data: check the user count and make it single-user before editing. Check the rotation mode before writing rotation;
  writing the wrong property "is silently ignored".
- **Materials:** Colours live on node inputs; `diffuse_color` affects only the solid viewport. Keep base colour
  between 0.02 and 0.9. Roughness/metal/normal images must be `Non-Color`. Scripted meshes need UVs. Add a little
  noise into roughness so it looks less CG. Check with `shading="material"`/`"rendered"`.
- **Imports and generated meshes:** They arrive at arbitrary scale, rotation and origin. Size them from the world
  bounding box, drop them to the ground (`location.z -= min_z`), and face them correctly (generators face ±Y). Check
  for intersections. Don't mix low-poly and photoscan styles in one frame.
- **Retopology and budgets**
  - Work on a copy and keep the original as the bake source.
  - Diagnose with the topology fields, then clean up (remove_doubles, dissolve_degenerate, delete loose, recalc
    normals).
  - Decimate for static props. Voxel remesh then QuadriFlow for deforming meshes. Shrinkwrap restores the silhouette.
  - Bake normals in Cycles with selected-to-active, cage extrusion about 1–2% of object size.
  - Budgets: hero character 15–50k tris, prop 500–5k, background 50–500.
- **Rigging:** Applied transforms, at the origin, facing −Y, merged vertices. Use Rigify for humanoids. Parent rigid
  parts to bones for mechanical rigs (no skinning). If heat weighting fails: merge and clean first, or skin a voxel-
  remeshed copy and Data-Transfer the weights, or scale ×10, skin, then scale back. Verify by posing elbows, knees and
  hips, then reset.
- **Animation:** Check motion with frame strips (`look(mode="frames")`): popping, foot sliding, loop seam. Loops: make
  the first and last key identical and add a Cycles modifier. Name actions `Character_Walk` (engines import actions by
  name).
- **Level design:** Player capsule 1.8×0.6 m, doors 1.2–1.5 m wide × 2.4–3 m tall, corridors 3–4 m, step 0.2/0.3 m, 1
  m grid with 2/4 m modules. Keep a `PlayerScale` capsule in the scene. Engine collision naming: Godot
  `-col`/`-colonly`, Unreal `UCX_`. Read each exporter's operator arguments before use, because they change between
  versions.

### 2.5 Export + validation (always a separate process)

1. Export from the live session with `bpy.ops.export_scene.gltf(filepath=".../<asset>.glb", export_format="GLB",
   use_selection=True, ...)`.
   - First read the operator's RNA properties; they change between versions [level-design.md].
   - ahujasid v2.1.9 removed its `export_scene` tool. The official server never had one [Nik Bear Brown, 08:10–09:20].
2. In Bash, run each skill script in a **new** Blender process:
   `"$BLENDER" -b --factory-startup --python-exit-code 1 -P "$SKILL_DIR/scripts/blender/inspect_model.py" -- out.glb`,
   and likewise for `render_views.py`.
   - `--factory-startup` keeps user add-ons (including any MCP add-on with auto-start) from loading, so the
     validation process cannot grab port 9876 [judgment].
   - `--python-exit-code 1` is needed because without it "Blender exits with zero, even when the script raises an
     error" [Nik Bear Brown, 07:10–07:20].
3. **Reproducibility check:** run `build_<asset>.py` headless from an empty file
   (`-b --factory-startup -P build.py -- --export out_ci.glb`) and compare tris and bbox with the live export. A
   difference means hand edits or unscripted live state. Fold them into the script or record them in NOTES.md
   [judgment].
4. Read the checks you wrote: "A check can prove less than it claims". In one recorded case a floor check hit the
   object's own collider [Nik Bear Brown, 10:10–10:20]. Don't move a node to hide a bad origin.

### 2.6 Blender CLI on users' machines

| OS | Where | Discover |
|---|---|---|
| Any (best) | Ask the live session: `bpy.app.binary_path` | Same build as the open GUI |
| Windows | Manual: `C:\Program Files\Blender Foundation\Blender\blender.exe` [docs.blender.org]. Current installers usually use a versioned folder `...\Blender X.Y\blender.exe` [UNVERIFIED]. Steam: `...\Steam\steamapps\common\Blender\blender.exe` [UNVERIFIED]. Portable zip: anywhere | PowerShell: `Get-ChildItem 'C:\Program Files\Blender Foundation' -Recurse -Filter blender.exe \| Sort-Object FullName -Descending`; `where.exe blender` |
| macOS | `/Applications/Blender.app/Contents/MacOS/Blender` [docs.blender.org]; also `~/Applications/...` | `mdfind "kMDItemCFBundleIdentifier == 'org.blenderfoundation.blender'"` [UNVERIFIED id] |
| Linux | `blender` on PATH (distro/snap) or `<dir>/blender` from the tarball [docs.blender.org] | `command -v blender` |

- Use `blender.exe`, not `blender-launcher.exe`. The launcher does not attach to the console, so you would get no output
  [UNVERIFIED].
- Claude Code on native Windows uses **Git Bash** for its Bash tool when Git for Windows is installed, and the
  **PowerShell tool** otherwise. The PowerShell tool is also available alongside Bash by default for claude.ai accounts.
  `CLAUDE_CODE_GIT_BASH_PATH` fixes a Git Bash that can't be found [code.claude.com/docs/en/setup].
- Quoting:
  - Git Bash: `"/c/Program Files/Blender Foundation/Blender 5.1/blender.exe" -b ...`
  - PowerShell: `& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b ...` (the call operator `&` is
    needed for a quoted path).
  - Pass file arguments as `C:/Users/me/proj/out.glb` (forward slashes) [judgment: works in both shells and in Python].
  - Whether Windows PowerShell 5.1 passes `--` through to native programs unchanged is [UNVERIFIED]. Hence the smoke
    test below.
- **Smoke test, once per machine:**
  `"$BLENDER" -b --factory-startup --python-expr "import sys,bpy;print(bpy.app.version_string, sys.argv[sys.argv.index('--')+1:])" -- a b`
  It must print the version and `['a', 'b']`. This confirms the executable, the version and argument passing in one
  call.
- **Version match:** prefer the same major.minor as the live session. bpy APIs changed in 4.0, 4.2, 4.4 and 5.0
  [bpy.md].

## 3. Never do

| Never | Why / evidence |
|---|---|
| Run the official and ahujasid add-ons/servers at the same time | Both use port 9876; #339 had "competing for the same port". The same Blender PID hosts both, so a PID check proves nothing |
| Use `uvx blender-mcp` expecting the official server | That PyPI name runs ahujasid's server [ahujasid README Quickstart note] |
| Use ahujasid on Windows with Blender 5.1/5.2 and wait it out | #339 is open: 4–5 min per call, beyond the client timeout. Switch to the official connector or headless |
| Run the skill's validation scripts inside the live session | `gs_common.py` calls `read_factory_settings`, which wipes the user's scene (the official sandbox blocks it, ahujasid doesn't) |
| Resend a step after a timeout without inspecting | A cancelled call can still execute later [#339], which gives duplicate `.001` objects |
| Build an asset only through chat history | Not reproducible or diffable. The course rule is to "Copy every execute Blender code body into a script ... Otherwise, Git won't show how the asset was built" |
| Work on the user's only copy | No undo across MCP. "ALWAYS save your work before using it" [ahujasid]; "without any guards" [blender.org] |
| Long sessions with full-size screenshots | Documented session: about 60% of a 5x plan in 2 h, then degraded output and false "done" [Theoretically Media 05:50–06:45] |
| Declare done from code success or numbers alone | Clipping, a "thimble-sized" cup and overexposure all passed silently. Look at fixed angles and check bbox against the brief |
| Leave asset downloads or generators enabled by default | Poly Haven downloads freeze Blender's main thread [README]. Generators may cost credits. A course required them off [Nik Bear Brown 02:40–02:55] |
| Opt into ahujasid content telemetry | Opted-in prompts, code and screenshots "may be used ... to train AI models" [README] |
| Open untrusted .blend files while the MCP socket is up | The socket has no authentication. Turn the add-on off when idle [Nik Bear Brown 06:30–06:55; README] |

## 4. Gaps and unverified items

- projects.blender.org returns 403 to this proxy, so the official **wiki/Setup**, the **release notes for 1.0.1–1.0.3**
  and the upstream tool list for 1.0.3 were not read. The tool list comes from round 1 (upstream commit 4309a39) and the
  bpy-dev fork's readme_tools.rst.
- The Windows path of the connector's extension folder, and whether the **Code tab** sees desktop *extensions* (versus
  `claude_desktop_config.json` servers), are not verified.
- Claude Desktop's own MCP tool timeout ("~4 minutes") comes only from #339 reports. There is no official documentation
  for it.
- GitHub issues API and HTML pages are blocked for this session. Only #339 was read (via WebFetch). Other ahujasid
  issues (#260 Mac timeouts, #155) were seen only as search snippets.
- No Reddit or HN threads were found. The Aidan Stanik "Can Claude Animate Characters in Blender?" transcript failed to
  download. The note.com (Japanese) and strayspark troubleshooting pages were seen only as search snippets.
- The mcp.directory guide was **not used for facts**: it wrongly claims Blender 3.0+/4.5 support and an ahujasid-style
  sidebar for the official connector.
- Windows installer folder naming, Steam/Store paths, `blender-launcher.exe` behaviour, and PowerShell `--` passing are
  all [UNVERIFIED]. The smoke test in §2.6 settles them on each machine.

## 5. Sources

- blender.org/lab/mcp-server (requirements, drag-twice install, warning, mcp-1.0.3.zip) · claude.com/connectors/blender
  (Anthropic verified, id) · claude.com/resources/tutorials/using-the-blender-connector-in-claude (steps, FAQ)
- dev.classmethod.jp/en/articles/claude-blender-connector-desktop-and-code/ (hands-on, Claude Code registration, sandbox)
- mcp.directory/blog/claude-blender-connector-guide (low reliability; only "don't run both" used)
- raw.githubusercontent.com/bpy-dev/blender-mcp/main/{mcp/blmcp/data/prompts.yml, mcp/blmcp/tools_helpers/connection.py,
  readme_tools.rst}
- raw.githubusercontent.com/ahujasid/mcp-for-blender/main/{README.md, src/blender_mcp/server.py,
  src/blender_mcp/guides/*.md}
- github.com/ahujasid/mcp-for-blender/issues/339 (WebFetch) · code.claude.com/docs/en/{mcp,desktop,setup}.md
- docs.blender.org/manual/en/latest/advanced/command_line/launch/{windows,macos,linux}.html
- youtube.com/watch?v=6YO6y_2SSro (Theoretically Media) 01:39–01:52 setup; 02:32–06:20 failures; 06:36–06:47 cost
- youtube.com/watch?v=i-2NlEHaGjI (Nik Bear Brown) 01:30 tris; 05:10–06:55 setup/safety; 07:30–08:10 plan→per-object
  calls; 08:10 tool drift; 08:40 save code; 09:30–10:40 headless checks
