# Live Blender: handshake, ownership, reproducible builds

Use the developer's installed Blender first. A working live MCP gives iteration feedback; the local
CLI gives isolated build/validation runs. A PyPI `bpy` environment is the fallback when neither exists.
This is an operating contract, not a claim that a connector is available in every client.

## 1. Connect on the machine that runs Blender

| Situation | Route | Verify before modeling |
|---|---|---|
| Blender version supported by Blender Lab (research documents 5.1+) | Official [Blender Lab connector](https://www.blender.org/lab/mcp-server/); follow its current add-on/client installer | Add-on enabled; one read-only object-summary call returns the intended scene |
| Older Blender, or specifically needed `look`/asset-search tools | [ahujasid/mcp-for-blender](https://github.com/ahujasid/mcp-for-blender), one add-on and one client server | Its installed requirements and tool schemas; small handshake completes |
| No working live tools | Local Blender CLI, found with `scripts/find_blender.sh` | Reported executable/version; one separate factory-startup probe |
| Hosted chat/cloud, Blender on the user's desktop | Desktop client runs the local server; otherwise use available cloud CLI | A cloud `localhost` is not the desktop. Installing a desktop connector does not establish cloud access |

Keep only one Blender MCP add-on/server active: the two documented defaults both use port 9876.
Keep its socket on localhost. Do not install a second server to repair a slow first server.

**Client registration:** after installing the matching add-on, register the actual local stdio server.
An official desktop extension may not be imported into Claude Code automatically; locate its installed
executable rather than guessing a macOS/Windows path. For a resolved official executable:

```bash
claude mcp add --scope user blender -- /absolute/path/to/official/blender-mcp
codex mcp add blender -- /absolute/path/to/official/blender-mcp
```

For the alternative server (requires `uvx` and its add-on):

```bash
uvx mcp-for-blender install-addon
codex mcp add --env DISABLE_TELEMETRY=true --env BLENDER_MCP_SAFE_MODE=1 blender -- uvx mcp-for-blender
```

Claude Desktop supports its JSON stdio configuration; use the upstream setup guide for its current UI.
Set the same environment entries there. Restart the client and inspect its loaded tools. Registration
or an "enabled" listing alone is not a successful Blender connection. `uvx blender-mcp` is the
alternative package's legacy name, so it is not a reliable way to select the official connector.

## 2. Read-only preflight

1. Inspect tool availability/schemas. Official tools include scene/object summaries and code execution;
   the alternative includes `get_scene_info` and `look`. Use the tools actually exposed.
2. Run one read-only scene summary. Inspect version, open filepath, dirty state, background status,
   units, mode and bounded object names. Code execution can be used for these reads, without mutation.
3. Read `bpy.app.binary_path` **only when permitted**. The alternative's safe mode blocks this property;
   use `find_blender.sh` instead. Do not disable a guard for discovery.
4. If the connection fails, allow one read-only retry, then use the CLI. On a mutation timeout, follow §4.
5. Before live writes, save a recoverable project copy. Do not overwrite the user's only file. Capture
   unsaved work before changing the scene; preserve unrelated objects and external data.

`gs_build.begin()` chooses reset behavior using `bpy.app.background`. Its live-preservation path is
for an **interactive** Blender process. Do not use it in an MCP-attached background process containing
the user's scene; run the build in a separate disposable CLI process instead.

## 3. One source of truth, one live writer

- For procedural work, save the deterministic build in `assets/<id>/build.py`; use `gs_build` and `gb.begin(id)`.
  The build owns tagged data, not everything whose name resembles `GS_<id>`. Preserve editable source
  parts; joins/decimation belong to an export copy of each rigid part.
- Only one builder writes to this live Blender at a time. Other builders use separate CLI processes.
  Declare the asset ID, owned collection and output paths before executing.
- Extend one semantic part/operation at a time; return part names, dimensions, budgets and errors,
  not a whole-scene dump. Review fixed angles, normally 512 px previews; milestone contact sheets
  must remain legible enough to judge the defects being checked.
- Fold procedural GUI edits back into the script. For authored/manual assets, preserve a versioned
  native `.blend` with editable parts plus export settings; the native file is that asset's source.
- Live execution of the saved script requires permitted file reads/imports. In ahujasid safe mode,
  `open`, `exec`, `sys`, `os` and importing `gs_build` are blocked. Sending the script inline does
  **not** bypass its imports. Send only allowed, self-contained small code; use the CLI for the full
  build/helper when blocked. Never turn safe mode off silently or rewrite the whole library in chat.

## 4. Timeout and validation boundaries

A timed-out mutation may still finish in Blender. Do not resend it: inspect the owned collection and
output files first; resolve the pending call, then rerun an idempotent build if needed. Avoid overlapping
writes. Run heavy renders, bakes and imports outside the live socket.

Export the selected asset with `gb.export_glb`; preserve extras/names. Run **all** inspection/render/
clip/image scripts in separate `blender -b --factory-startup --python-exit-code 1` processes: their
import setup resets the scene. Never paste those entry points into a live user session. Compare the
CLI rebuild's hierarchy/dimensions/budgets with the live export and inspect the actual engine material
viewer; a Blender studio render proves form, not the game's final lighting.

**Evidence/source limits:** original workflow informed by round-2 research report 03. Official install
requirements/tool names above were documented in that research, not live-tested here. The alternative's
README, `server.py` and `safe_mode.py` were re-read on 2026-10-10; CLI registration syntax was checked with
`codex mcp add --help`. Neither client GUI connection was tested. Upstream issue reports do not establish
that every version/OS has a timeout bug. This file copies no upstream implementation or skill text.
