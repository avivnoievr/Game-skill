# Bundled third-party reference material

Game Studio's original files are licensed under the repository's MIT license. The reference
material below keeps its own license. These copies are a selected archive, not installed plugins:
no upstream executables, hooks, dependency manifests, generation clients or credentials are shipped.
The routing and scope adaptations are in `references/design-loading.md`.

Verified against the pinned GitHub source files on **2026-10-10**. Files named `UPSTREAM-SKILL.md`
were renamed from `SKILL.md` to distinguish reference text from plugin skill entry points; their
content is unchanged. All other upstream files are unchanged. Local source paths, byte counts and
SHA-256 hashes are recorded in `vendor/sources.json`.

## Three.js game design references — MIT

Upstream: [majidmanzarpour/threejs-game-skills](https://github.com/majidmanzarpour/threejs-game-skills/tree/8286774b22a2566bf894dbc825825c16921866af).
Pinned commit: `8286774b22a2566bf894dbc825825c16921866af`.

Copyright (c) 2026 Majid Manzarpour.

| Local directory, under `vendor/` | Upstream files preserved |
|---|---|
| `threejs-aaa-graphics-builder/` | `skills/threejs-aaa-graphics-builder/SKILL.md`, `references/technical-art.md`, `references/visual-scorecard.md`, `assets/scorecard-anchors/scene-1.jpg`, `scene-2.jpg`, `scene-3.jpg` |
| `threejs-game-ui-designer/` | `skills/threejs-game-ui-designer/SKILL.md`, `references/ui-patterns.md` |
| `threejs-game-feel/` | `skills/threejs-gameplay-systems/references/game-feel.md` |

Each directory includes an unchanged copy of the upstream root
[LICENSE](https://github.com/majidmanzarpour/threejs-game-skills/blob/8286774b22a2566bf894dbc825825c16921866af/LICENSE).
Retain its copyright and permission notice in redistributed copies or substantial portions.
Unselected graphics tutorial references, agent definitions and source scripts are not included.
The example images' scores belong to the source author; they are not a Game Studio quality claim.

## Anthropic frontend design reference — Apache-2.0

Upstream: [anthropics/skills, frontend-design](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design).
Pinned commit: `dbd4588f9e1033efb41dad4bef2f7947c8993d44`.

Local directory: `vendor/anthropic-frontend-design/`.

- `UPSTREAM-SKILL.md`: unchanged contents of `skills/frontend-design/SKILL.md`.
- `LICENSE.txt`: unchanged contents of
  [skills/frontend-design/LICENSE.txt](https://github.com/anthropics/skills/blob/dbd4588f9e1033efb41dad4bef2f7947c8993d44/skills/frontend-design/LICENSE.txt).

The copied skill states that its complete terms are in `LICENSE.txt`; the file contains the
Apache License, Version 2.0. No additional copyright attribution appears in these two source files.
The upstream root `THIRD_PARTY_NOTICES.md` was checked: its listed software and font components
are not contained in this two-file selection. No frontend-design-specific NOTICE is present in the
pinned subtree. Other Anthropic skills, font assets and packages are not bundled.

## Engine-neutral game UI/UX reference — Apache-2.0

Upstream: [gamedev-skills/awesome-gamedev-agent-skills, game-ui-ux](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/tree/0a70cfc64672d512c5b5b6006b5dcb5cf90dbdbd/skills/disciplines/game-ui-ux).
Pinned commit: `0a70cfc64672d512c5b5b6006b5dcb5cf90dbdbd`.

Copyright 2026 Abhishek Barali and the awesome-gamedev-agent-skills contributors.

Local directory: `vendor/gamedev-game-ui-ux/`.

- `UPSTREAM-SKILL.md`: unchanged contents of `skills/disciplines/game-ui-ux/SKILL.md`.
- `references/layout-and-flow.md`: unchanged file from that skill.
- `LICENSE`: unchanged upstream root
  [LICENSE](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/0a70cfc64672d512c5b5b6006b5dcb5cf90dbdbd/LICENSE).
- `NOTICE`: unchanged upstream root
  [NOTICE](https://github.com/gamedev-skills/awesome-gamedev-agent-skills/blob/0a70cfc64672d512c5b5b6006b5dcb5cf90dbdbd/NOTICE), including copyright and trademark attributions.

The examples' engine versions and code are source context, not a promise of compatibility with
the current game. No related engine-specific skill is implicitly installed.

## Maintaining this selection

Keep the license/NOTICE files beside their components. Preserve notices that pertain to the
redistributed material. If editing Apache-2.0 files, add prominent change notices in those files;
keep upstream originals and place project-specific guidance in the router whenever practical.
Update the pinned commit, source URL and hash together after reviewing any source update.
The license permits redistribution; it does not endorse the sources' quality scores or tool choices.

## Additional adapted design-judgment reference — Apache-2.0 and MIT sources

`references/design-judgment.md` is a changed/adapted synthesis dated 2026-10-10, distributed under
Apache-2.0 rather than the repository's default MIT license. The source methods were rewritten for
3D assets, reference evidence and game motion. These upstream skill bodies, commands and executables
are not shipped or activated; the existing five-component archive is unchanged.

| Source | Pinned commit | License / copyright |
|---|---|---|
| [pbakaus/impeccable](https://github.com/pbakaus/impeccable) | `d631a8827f99414d2b6daba4ef08b7f8701751d7` | Apache-2.0; Copyright 2025 Paul Bakaus |
| [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill) | `717446e07a78d4e6d7918b1fde1a263378eebac9` | MIT; Copyright 2026 Leonxlnx |
| [nextlevelbuilder/ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) | `50d8a7de0900119855614541f15a1a616691eb33` | MIT; Copyright 2024 Next Level Builder |
| [emilkowalski/skills](https://github.com/emilkowalski/skills) | `e8a175de22ae1e49370fc144c1f3bb9aeedf988d` | MIT; Copyright 2026 Emil Kowalski |

Unchanged license copies and Impeccable's root `NOTICE.md` are under
`vendor/design-judgment-sources/`. That NOTICE names platform-design-skills; its iOS/Android
reference content is not selected here. Exact reviewed sections and copied-notice hashes are in
`vendor/design-judgment-sources/sources.json`. Retain these notices with the adapted reference.
Valve/Riot publications are research citations, not redistributed text or art assets.
