# Game Studio 3D

A Claude Code plugin for deliberate 3D game production: editable assets, coherent art direction,
animation, clean architecture and independent quality checks. It supplies a workflow and executable
evidence tools for a capable model; it does not promise professional art from prompting alone.

- **Editable game assets:** semantic parts, joints, pivots, sockets and collision contracts. Moving
  parts stay separate; source files/build recipes survive export optimization.
- **Design material loaded by phase:** five selected components from three upstream repositories,
  pinned with licenses and hashes. The short startup router selects what the current task needs.
- **Research before production:** opening genre/art researcher and production planner produce
  separate reports; the director reconciles them into an executable slice/milestone plan.
- **Installed Blender first:** executable discovery, optional constrained live workflow and separate
  headless inspection/rendering. No automatic installation or paid generation.
- **Useful specialists:** two opening roles, asset builder, animator, art critic and playtest QA. Up to
  three independent production agents; one writer in a shared live Blender scene.
- **Evidence that can fail:** part/pivot/socket checks, exploded views, animation seam reports,
  browser input/counters and verification gates. Missing measurements cannot become a passing zero.

The complete Hebrew explanation and exact integration inventory are in
[docs/SUMMARY.he.md](docs/SUMMARY.he.md). Activation prompts are in [PROMPT.md](PROMPT.md).
Current continuation state is in [docs/HANDOFF.md](docs/HANDOFF.md).

## Install in a game project

For a cloud session, keep the installed files in the game repository so the next session sees them:

```bash
git clone https://github.com/avivnoievr/Game-skill
bash Game-skill/install.sh /path/to/your-game
```

Commit the resulting `.claude/skills/game-studio` and `.claude/agents` according to your project's
branch policy. Windows PowerShell: `.\install.ps1 -Target C:\path\to\your-game`.
Upgrades preserve the previous skill and same-name agents under `.claude/game-studio-backups/`.

Where Claude Code supports marketplace plugins:

```text
/plugin marketplace add avivnoievr/Game-skill
/plugin install game-studio@game-skill
```

The default branch is `claude/3d-game-dev-skills-system-13c0pn`; it can be pinned with
`/plugin marketplace add avivnoievr/Game-skill#claude/3d-game-dev-skills-system-13c0pn`.
Invoke `/game-studio:game-studio` for a plugin or `/game-studio` for a project copy. Open a new session
after installation and use the matching prompt. Optional machine-only install: `bash install.sh --user`.

## Tool requirements

| Tool | Purpose | Policy |
|---|---|---|
| Existing Blender 4.2+ executable | Asset build, import, checks and renders | `scripts/find_blender.sh`; `BLENDER` overrides its location. Actually tested here on 4.3.2 |
| Node 18+ and project `playwright` | Browser game capture/input | Use existing tools; install dependencies only within the authorized setup scope |
| Project `gltf-validator` | Khronos GLB validation | `check_gltf.mjs`; missing dependency remains unverified |
| Godot / Unity / other engine | Runtime import and gameplay evidence | Use installed project version. Native capture recipes are partial adapters, not complete QA systems |
| Optional MCP, optimization, ffmpeg | Live access or specific pipeline work | Route by actual capability; none is a mandatory plugin dependency |

`pip install bpy` is an explicit fallback requiring compatible Python/Blender versions, not the
default when Blender is already installed. This repository does not install Blender, run a paid
generator or grant access to a developer's desktop. Live MCP compatibility and sandbox limits must
be checked in that developer's actual environment.

## Contents

```text
plugins/game-studio/
  .claude-plugin/plugin.json          plugin version 1.1.0
  agents/                            genre-art-researcher, production-planner, asset-builder,
                                     animator, art-critic, playtest-qa
  THIRD_PARTY_NOTICES.md              bundled licenses/source inventory
  skills/game-studio/
    SKILL.md                         lean orchestrator and production contracts
    references/                      design, tools, live Blender, asset recipes, QA, engine adapters
    vendor/                          pinned reference selections, original licenses, sources.json
    templates/                       brief, art bible, assets/budgets/features, scorecard, build, verify
    scripts/blender/                  gs_build, inspector, multiview/exploded renderer, clip/image reports
    scripts/web/                      capture and GLB validator
tests/                               executable regression fixtures
docs/                                research, Hebrew report, handoff and validation evidence
```

## Validation and limits

See [docs/VALIDATION.md](docs/VALIDATION.md) for reproducible commands and actual results from this
continuation. Fixtures exercise clean and intentionally broken cases rather than checking syntax
alone. The stylized car is a structural regression fixture; the independent prop pilot checks that
another agent can use the workflow. Neither is proof of a polished finished game.

The current environment has Blender 4.3.2 and software rendering. No actual developer GUI/MCP session,
Unity, paid generation or broad real-game quality evaluation is claimed. Prior handoff reports
contain additional historical test claims; results not reproduced here remain historical reports.
Automated critics and image metrics support review but cannot establish taste by themselves.

## License and attribution

Original work is MIT ([LICENSE](LICENSE)). Bundled reference files retain MIT or Apache-2.0 terms,
including applicable NOTICE files; see [THIRD_PARTY_NOTICES](plugins/game-studio/THIRD_PARTY_NOTICES.md)
and [docs/CREDITS.md](docs/CREDITS.md). The imported scorecard example ratings are their author's
judgments, not the project's adopted visual quality target.

## Additional design judgment (2026-10-10)

An additive supplement to 1.1.0 preserves the prior files and bundled design references:
[design-judgment.md](plugins/game-studio/skills/game-studio/references/design-judgment.md).
It adds project-specific recipe selection, inspected visual comparisons for standalone assets,
form checkpoints and visual observation before metric interpretation. A model-design test uses
standard/premium art review; prototype or technical completion does not certify design taste.
The [research record](docs/research/round2/10-design-judgment-additions.md) identifies four further
skill sources, selected adaptations and licenses. Their runtime/CLI packages are not dependencies.
This supplement is identified by its Git commit; the package version remains 1.1.0.

## Development and publication policy

This repository remains the source of every update and regression comparison. The planned
`avivnoievr/game-studio-3d` repository is a publication channel for versions the owner tests
and explicitly approves. It does not receive automatic updates.

The package metadata now identifies candidate **1.1.1**. Earlier 1.1.0 descriptions and
validation counts above remain historical. Publication templates live in `distribution/`;
`tools/prepare_distribution.py` exports a specific committed SHA into a new local folder,
retaining tests, licenses and a content manifest. Preparing a candidate does not publish it.
See [the Hebrew release process](docs/RELEASE-PROCESS.he.md). Development continues here.
