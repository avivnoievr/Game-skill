# Game Studio 3D

A Claude Code skill and plugin for editable 3D assets, deliberate art direction,
animation, game architecture and evidence-based quality checks.

**Version {{VERSION}} is offered for testing and feedback.** The workflow and several tools
have been checked; professional visual quality and a complete game made with Claude have
not been established. See [validation and limits](docs/VALIDATION.md).

## What it provides

- Separate moving parts, usable pivots and sockets, editable sources and export checks.
- Design references adapted to the project's genre, camera and intended player experience.
- Two opening research/planning roles, followed by asset building, animation, art critique
  and playtest QA when the task needs them.
- Blender inspection, multiple-view renders, animation reports and browser QA contracts.
- A focused workflow for a single model as well as a larger game project.

The skill directs work; it does not supply a game engine, install Blender or automatically
connect to a developer's desktop. An MCP connection is optional and must be configured for
the actual environment. The current packaging targets Claude Code.

## Install

For a local or cloud game project:

```bash
git clone --branch v{{VERSION}} https://github.com/{{PUBLICATION_REPOSITORY}}.git
bash game-studio-3d/install.sh /path/to/your-game
```

On Windows, run `./install.ps1 -Target C:\path\to\your-game` from the cloned folder.
Commit the installed `.claude/skills/game-studio` and `.claude/agents` in your game
repository when using cloud sessions. Upgrades keep previous customizations in backups;
they do not automatically merge them into the new installation.
Open a new Claude Code session and use [the matching activation prompt](PROMPT.md).

Where marketplace plugins are supported:

```text
/plugin marketplace add {{PUBLICATION_REPOSITORY}}#v{{VERSION}}
/plugin install game-studio@game-skill
```

Invoke `/game-studio:game-studio` for a plugin or `/game-studio` for a project copy.
Cloud sessions that do not support marketplace commands should use the project-copy install.

## Requirements

| Tool | When needed | Verification boundary |
|---|---|---|
| Existing Blender 4.2+ executable | Building, inspection and rendering | Tested on 4.3.2; other supported versions need checking |
| Node 18+ and project Playwright | Browser-game capture and input evidence | Tested with controlled Chromium fixtures |
| Project `gltf-validator` | Khronos GLB validation | Missing in the test environment; actual Khronos validation is unverified |
| Your project's game engine | Import, gameplay and performance checks | One Godot 4.6.3 prop-control pilot; no general engine-compatibility claim |

There is no mandatory paid service. Use the tools already installed for the project.
This installer copies the skill and agents; it does not install or configure Blender MCP.

## Give useful feedback

Please [report a bug](https://github.com/{{PUBLICATION_REPOSITORY}}/issues/new?template=bug_report.yml)
or [share design feedback](https://github.com/{{PUBLICATION_REPOSITORY}}/issues/new?template=design_feedback.yml).
Include the version, task, expected result and what actually happened. Visual feedback is most
useful with the model/render, viewing conditions and the reference used for comparison.
A structural pass is separate from a convincing design result.

Fixes and contributions are developed in [{{SOURCE_REPOSITORY}}](https://github.com/{{SOURCE_REPOSITORY}}).
This repository receives selected releases after the owner tests and approves the exact source
commit. Updates are not automatically mirrored. See [contributing](CONTRIBUTING.md) and
[the release policy](RELEASE-POLICY.md).

## Documentation

- [Hebrew explanation and component inventory](docs/SUMMARY.he.md)
- [Validation commands, evidence and limits](docs/VALIDATION.md)
- [Credits and research sources](docs/CREDITS.md)
- [Release changes](CHANGELOG.md)
- [Source commit and file hashes](RELEASE.json)

Research and handoff documents retained under `docs/` describe development history and its
evidence limits. Their earlier version numbers, installation examples and status reports are
historical. Use this README and `RELEASE.json` for the distributed version.
Runtime regression tests are included for reproduction and future checks. The distribution
preparer's own tests stay with that tool in the development repository.

## License

Original work is [MIT](LICENSE). Bundled references and adapted material retain their MIT or
Apache-2.0 licenses and notices. See [third-party notices](plugins/game-studio/THIRD_PARTY_NOTICES.md).

Prepared from [source commit {{SOURCE_SHA}}](https://github.com/{{SOURCE_REPOSITORY}}/commit/{{SOURCE_SHA}}).
Snapshot status: **{{STATUS}}**. A candidate is not an approved public release.
