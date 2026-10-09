# Game Studio 3D: a Claude Code plugin for high-quality 3D games

Claude can write a game that runs. Left to its defaults, though, the result looks AI-made: primitive-soup
models, grey three-point lighting, glow on everything, a web-app HUD, and "done" claims that don't
survive playing it. This plugin changes the *process*:

- An **art bible** with real numbers, written before building, after a "would I do this for any
  game?" check that weeds out defaults.
- **Game-ready 3D models** through a sourcing decision tree, modeling craft rules and budgets, with
  headless validation and multi-view renders the agent must actually look at.
- **Animation and game feel** grounded in principles and concrete values, checked with motion
  evidence rather than still frames.
- **A clean architecture**: pure simulation core, fixed timestep, explicit lifecycle and machine-enforced
  rules.
- **Evidence-based QA**: a QA mode in the game, gates G0–G7, objective image metrics, and two
  independent, read-only critic agents with hard thresholds.
- **A small team of specialist subagents** used only where they pay off: `asset-builder` (up to 3 in
  parallel), `animator`, `art-critic` and `playtest-qa`.

It works with three.js / React Three Fiber, Godot 4 and Unity, plus Blender for assets. A full
explanation in Hebrew is in [`docs/SUMMARY.he.md`](docs/SUMMARY.he.md).

## What's inside

```
.claude-plugin/marketplace.json        marketplace (this repo)
plugins/game-studio/
  .claude-plugin/plugin.json
  agents/                               asset-builder · animator · art-critic · playtest-qa
  skills/game-studio/
    SKILL.md                            the orchestrating skill (standards, roles, phases, gates)
    references/                         orchestration · art-direction · anti-ai-look · modeling · animation
                                        architecture · qa-protocol · toolchain · engines/{threejs,godot,unity}
    templates/                          brief · art-bible · scorecard · features.json · budgets.json
                                        assets.json · progress · LICENSES · verify.sh
    scripts/blender/                    inspect_model.py · render_views.py · clip_report.py · image_metrics.py
                                        (headless Blender or `pip install bpy`)
    scripts/web/                        capture.mjs (Playwright) · check_gltf.mjs (Khronos validator)
PROMPT.md                               activation prompts (English + Hebrew)
install.sh / install.ps1                copy the skill + agents into a project (no plugin system needed)
docs/                                   Hebrew summary, credits, the five research reports
```

## Install

Pick one of three ways.

**1. As a plugin (Claude Code CLI or desktop).**
```text
/plugin marketplace add avivnoievr/Game-skill
/plugin install game-studio@game-skill
```
- The branch `claude/3d-game-dev-skills-system-13c0pn` is currently the repository's default branch.
  If you change the default branch later, pin this one with
  `/plugin marketplace add avivnoievr/Game-skill#claude/3d-game-dev-skills-system-13c0pn`.
- Skill: `/game-studio:game-studio`. Agents: `game-studio:asset-builder`, and so on.

**2. Into the game repository (works in cloud sessions, which don't load marketplace plugins):**
```bash
git clone https://github.com/avivnoievr/Game-skill && bash Game-skill/install.sh /path/to/your-game
cd /path/to/your-game && git add .claude && git commit -m "Add game-studio skill and agents"
```
On Windows: `.\install.ps1 -Target C:\path\to\your-game`.

**3. For your user only (this machine):** `bash install.sh --user`.

Then open a new Claude Code session in the game project and paste a prompt from [`PROMPT.md`](PROMPT.md).

## Requirements (in the game project or environment)

| Tool | Needed for | Install |
|---|---|---|
| Blender 4.2+ **or** the `bpy` module | Asset inspection and renders | blender.org, or `pip install bpy` (Python 3.13). On bare Linux also `apt-get install libegl1 libegl-mesa0 libgl1-mesa-dri` |
| Node 18+ with `playwright` | Web-game captures | `npm i -D playwright && npx playwright install chromium` |
| `gltf-validator` | glTF validation | `npm i -D gltf-validator` |
| Optional | Optimization, KTX2, video | `@gltf-transform/cli`, `gltfpack`, KTX-Software, ffmpeg |
| Optional MCP servers | Desktop-only live tools | See `references/toolchain.md`. **None is required** |

## What was tested while building this (Linux container, no GPU)

- `inspect_model.py` on Blender 5.2.2 (PyPI `bpy`):
  - catches flipped normals, mirrored scale, missing materials, unit errors, budget overruns and
    floating parts;
  - passes a clean model;
  - also run on Khronos sample models (DamagedHelmet, Fox).
- `render_views.py`:
  - Workbench, EEVEE and Cycles renders;
  - ortho, 3/4, silhouette and wireframe views, contact sheets;
  - animation pose strips (Fox `Run`, distinct poses verified);
  - the scale figure.
- `capture.mjs`:
  - WebGL screenshots via SwiftShader;
  - console/page error capture;
  - the `__QA__` hook (shots, stats, state, deterministic `advance`);
  - held-key sequences, grayscale copies, image metrics.
- `capture.mjs`, in both directions:
  - it waits for a late `ready`;
  - it fails when the game is never ready, the canvas is blank, counts are over budget, or a scene
    reload leaks geometry;
  - it passes a healthy game.
- `clip_report.py`: passes the Fox clips; FAILs a clip with a deliberate pop at the loop point.
- `image_metrics.py`: run on Godot, web and Blender images (grayscale copies written).
- `check_gltf.mjs`: Khronos validator and budget checks.
- `templates/verify.sh`: a minimal Vite + TypeScript + three r186 game, in both its pass and fail paths.
- The three.js reference snippets typecheck against three r186 under strict TypeScript.
- The Godot QA autoload in `engines/godot.md` ran in Godot 4.7.2 (shots and a metrics report).
- `claude plugin validate --strict` passes for the plugin and the marketplace.
- An independent review agent checked everything. It found 7 blocking and 15 optional issues,
  including a real bug where `capture.mjs` did not wait for `ready`. All were fixed and re-tested.

**Not tested here:** Unity snippets (no Unity available), `install.ps1` (no PowerShell), and the paid
3D-generation services and MCP servers (documented from their docs; not run). The plugin's effect on
real game quality has not been measured with `claude plugin eval` yet.

## Honest limitations

- No skill makes code-only modeling produce good **characters**. The plugin routes characters to CC0
  rigged packs or AI generation plus cleanup, and says so.
- Taste needs a human. The plugin asks you at the decisions that matter (art direction, vertical slice).
- Independent critics are the same model with a fresh context and a strict rubric. That's much better
  than self-review, but it is not a human art director. Objective metrics and scripts back them up.
- Multi-agent work costs tokens. The plugin keeps the team small and runs gates at milestones only.

## Credits and license

MIT; see `LICENSE`. This plugin is original text informed by many sources: Anthropic's documentation
and skills, threejs-game-skills, superpowers, Claude-Code-Game-Studios, godogen, scenario-labs, scottstts
and others. Full attribution is in [`docs/CREDITS.md`](docs/CREDITS.md).
