# Credits and sources

The text of this plugin is original, written from the research in `docs/research/`. Ideas, methods and
some starting values were adapted from the sources below, and short quotations are attributed where
they appear. No text was copied from sources whose license does not allow it: Anthropic's claude-code
plugins (all rights reserved), Unity's agent plugin (Unity Companion License), terma (CC-BY-SA) and
GPL-licensed skill packs.

## Skills, plugins and agent setups

| Source | License | What informed this plugin |
|---|---|---|
| [majidmanzarpour/threejs-game-skills](https://github.com/majidmanzarpour/threejs-game-skills) | MIT | Scorecard categories and 0–3 anchors, automatic failures, canvas-metric idea, order of work (forms → materials → lighting → effects), bloom and game-feel starting values, "lead + few workers, one independent review" pattern, banned web-UI defaults in game HUDs; quoted lines about glow and recolored primitives |
| [anthropics/skills — frontend-design, canvas-design](https://github.com/anthropics/skills) | Apache-2.0 | Plan → generic check → build → critique loop; named default clusters; "boldness in one place"; "remove one accessory"; refine-don't-add final pass |
| [obra/superpowers](https://github.com/obra/superpowers) | MIT | Verification-before-completion ideas, red-flag phrases, rationalization table, "watch the test fail", 3-failed-fixes rule, reviewer that treats reports as unverified claims |
| [Donchitos/Claude-Code-Game-Studios](https://github.com/Donchitos/Claude-Code-Game-Studios) | MIT | Art-bible section outline, verdict token on the first line, evidence that heavy multi-agent process ranked last, run-and-observe rule |
| [htdt/godogen](https://github.com/htdt/godogen) | MIT | "Proof over claims", watching back a recorded proof, engine silent-failure traps, de-scaffolding evidence |
| [scottstts/Threejs-Awesome-Graphics-Agent-Skills](https://github.com/scottstts/Threejs-Awesome-Graphics-Agent-Skills) | MIT | Operation-by-form table, bevel bands per part class, segment budgets by radius, join rules, fixed-view visual validation |
| [scenario-labs/skills (Blender expert family)](https://github.com/scenario-labs/skills) | MIT | Expert brief→stage→gate loop, modifier stack order, Harden Normals + Weighted Normal, retopology budgets, review-sheet approach |
| [achimala/TheLongSilence](https://github.com/achimala/TheLongSilence) | MIT | Detail by recess, calm areas, apply scale before bevel, join by material to cut draw calls |
| [kai-chop/blender-industrial-kit](https://github.com/kai-chop/blender-industrial-kit) | MIT | Never-list idea, human-scale figure in reviews, multi-view verification |
| [czlonkowski/blender-web-3d-skill](https://github.com/czlonkowski/blender-web-3d-skill) | MIT | Idempotent managed build scripts, glTF delivery traps |
| [img2threejs/img2threejs](https://github.com/img2threejs/img2threejs) | Apache-2.0 | Pass order and geometric gates before rendering |
| [gamedev-skills/awesome-gamedev-agent-skills](https://github.com/gamedev-skills/awesome-gamedev-agent-skills) | Apache-2.0 | Game-feel and frame-rate-independent camera pitfalls |
| [AlterLab-IEU/AlterLab_GameForge](https://github.com/AlterLab-IEU/AlterLab_GameForge) | MIT | Landmark scales, anti-references, "icons drawn by one person in one sitting" |
| [grapefrukt/juicy-breakout](https://github.com/grapefrukt/juicy-breakout) | zlib | Juice checklist ("Juice it or lose it") |

## Research, documentation and articles

- Anthropic engineering:
  - "Harness design for long-running application development" (2026);
  - "Effective harnesses for long-running agents" (2025);
  - "How we built our multi-agent research system" (2025);
  - "Building effective agents" (2024).
  Ideas only, with short attributed quotes.
- Claude Code documentation (code.claude.com/docs): skills, subagents, plugins, marketplaces, hooks,
  cloud environments, best practices. Claude prompt-engineering guidance (platform.claude.com/docs).
- Benchmarks:
  - 3DCodeBench (gaoypeng/3dcodebench, Apache-2.0): Blender 5 API drift, failure taxonomy;
  - 3DHarnessBench (llada60/3DHarnessBench, Apache-2.0): multi-view inspection, correction priority.
- Papers on self-correction and LLM-as-judge (Huang et al. 2024; Kamoi et al. 2024; Zheng et al. 2023;
  Chen et al. "MLLM-as-a-Judge" 2024; Taesiri et al. "GlitchBench" 2024; MAST, Cemri et al. 2025),
  read at abstract level as noted in the research reports.
- Valve, "Illustrative Rendering in Team Fortress 2" (SIGGRAPH 2007) and "Stylization with a Purpose"
  (GDC 2008): read hierarchy, color and silhouette principles, paraphrased.
- Daniel Holden (theorangeduck.com): spring/damper math, locomotion displacement, dead blending.
- Khronos PBR Neutral tone mapper (CC-BY-4.0) and the model-viewer tone-mapping write-up.
- three.js source and examples (MIT): tone mappers, animation API, deterministic e2e approach.
- Godot documentation (CC-BY-3.0): environment, lights and shadows, Movie Maker, command line,
  Performance monitors, AnimationTree, project organization.
- Material Design motion tokens (Apache-2.0).
- Glenn Fiedler, "Fix Your Timestep!"; Robert Nystrom, *Game Programming Patterns*.
- Steve Swink, *Game Feel* (via review), plus notes on "The Art of Screenshake" (Jan Willem Nijman) and
  "Juicing Your Cameras With Math" (Squirrel Eiserloh). The talks are video-only and were not watched;
  text proxies were used.

## Tools referenced (not bundled)

Blender and `bpy` (GPL), glTF-Transform (MIT), gltfpack/meshoptimizer (MIT), Khronos glTF-Validator
(Apache-2.0), KTX-Software (Apache-2.0), Playwright (Apache-2.0), Chrome DevTools MCP (Apache-2.0),
Blender Lab MCP (GPL), ahujasid/mcp-for-blender (MIT), hi-godot/godot-ai (MIT), CoplayDev/unity-mcp (MIT).
Asset sources: Poly Haven, Kenney, Quaternius, KayKit, ambientCG (CC0; check each pack's license file).
