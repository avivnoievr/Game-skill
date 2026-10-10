# 01: Design-sense skills to bundle (Round-2 Agent 1)
Date: 2026-10-10. Scope: existing skills that give Claude visual taste for 3D game art, lighting, UI/HUD and motion, plus how to bundle them into `game-studio`.
Method: I opened every SKILL.md and LICENSE cited here from raw.githubusercontent.com at HEAD on 2026-10-10. Byte and line counts are exact for the fetched files. Token figures are bytes ÷ 4 and are estimates.
Access limits: the GitHub API and github.com issue pages are blocked in this session (403 "GitHub access … not enabled"), so all star counts are [UNVERIFIED]. I listed files with tree-only clones (`git clone --depth 1 --filter=blob:none --no-checkout`). Downloads are in `SCRATCH/downloads2/1/{raw,raw2,docs,trees}`.

## 1. Summary
1. **No existing skill gives 3D-game design sense end to end.** Most "taste" skills target web pages, not games:
   - `taste-skill` says so itself: "Landing pages, portfolios, and redesigns. Not dashboards".
   - The same holds for `impeccable` and `ui-ux-pro-max`.
   - Only two sources carry real game taste: `majidmanzarpour/threejs-game-skills` (MIT) and Anthropic's `frontend-design` method (Apache-2.0). The second is a web skill whose method transfers to games.
2. **Recommended bundle (vendored, loaded per phase).** Rank and files:
   - (1) threejs-game-skills `threejs-aaa-graphics-builder` (scorecard, technical-art, recipes)
   - (2) threejs-game-skills `threejs-game-ui-designer`
   - (3) Anthropic `frontend-design`
   - (4) threejs-game-skills `game-feel.md`
   - (5) awesome-gamedev `game-ui-ux` (engineering side of HUDs)

   Everything else goes on the "recommend, don't bundle" list, or I borrow ideas from it with a citation.
3. **Don't declare plugin `dependencies` on design plugins.** Cross-marketplace dependencies need `allowCrossMarketplaceDependenciesOn` in our marketplace.json. When a dependency fails to resolve and was declared in `plugin.json`, "the install completes without the dependency and your plugin then fails to load". A missing design skill would therefore take game-studio down with it. Vendoring avoids this. [docs: plugins/dependencies]
4. **`frontend-design` is available in two places, byte-identical.**
   - `anthropics/skills` (`skills/frontend-design/SKILL.md`, 9,390 B, LICENSE.txt is Apache-2.0)
   - `claude-plugins-official` (`plugins/frontend-design`, plugin name `frontend-design`; `diff -q` shows no difference)
   - Only the docx/pdf/pptx/xlsx skills in anthropics/skills are "source-available, not open source".
5. **`threejs-game-skills` can only be vendored.** It has no `.claude-plugin/` (only `install.sh` and `agents/openai.yaml`), so it cannot be a plugin dependency.
6. **Loading at the start of a project can backfire.** After compaction, Claude Code re-attaches each invoked skill's first 5,000 tokens within a shared 25,000-token budget, starting from the **most recently invoked** skill. If 4–5 design skills are invoked after `game-studio`, the director skill itself can be dropped. Load design material per phase by reading reference files, not by invoking many skills. [docs: skills "Skill content lifecycle"]
7. **The subagent `skills:` field preloads the full SKILL.md**, up to 32 names, but it can't preload skills that set `disable-model-invocation: true`. The docs don't say how to write a *plugin* skill's name there. Plugin skills are invoked as `plugin-name:skill-name`, so use `game-studio:<skill>` and confirm with `--debug`, which logs a warning for a missing skill. [UNVERIFIED for the plugin form] An aggregator lists an open June 2026 report that preload doesn't inject content [UNVERIFIED: issue page blocked]. The safe fallback is an explicit "Read these files first" step in the agent body.
8. **Licenses allow vendoring the recommended set.**
   - MIT and ISC: copy the copyright and permission notice.
   - Apache-2.0 §4: (a) ship the license text, (b) mark modified files, (c) keep the existing notices, (d) carry the NOTICE content (awesome-gamedev has a NOTICE file).
   - OpenAI's `game-ui-frontend` has **no license file** in `openai/plugins`, so paraphrase it with a citation and never copy it.
9. **Rejected for bundling:**
   - taste-skill (87 KB SKILL, web only)
   - impeccable: it downloads a binary on first run, and its plugin hooks run that binary on every SessionStart, Edit/Write and Stop.
   - ui-ux-pro-max (web/app CSV database)
   - linegel (WebGPU/TSL r185 only)
   - emalorenzo (a performance checklist)
   - omer-metin and arjun988 (thin persona or generic three-point lighting)

## 2. Ready-to-use additions

### 2.1 Candidate table (opened, verified)
| # | Skill (repo → path) | Size | License (exact) | Game value | Decision |
|---|---|---|---|---|---|
| 1 | majidmanzarpour/threejs-game-skills → `skills/threejs-aaa-graphics-builder/` (SKILL.md + references/visual-scorecard.md, technical-art.md, authoring-recipes.md, shader-cookbook.md) | 4,468 + 5,972 + 5,445 + 10,889 + 15,881 B (45/64/73/172/286 L); ~4k tok core (SKILL + scorecard + tech-art), ~10.7k all | MIT, "Copyright (c) 2026 Majid Manzarpour" (root LICENSE only) | Highest: order of work, 10-category scorecard, auto-fail list, canvas metrics, PBR/bloom presets | **VENDOR** |
| 2 | same repo → `skills/threejs-game-ui-designer/` (SKILL.md + references/ui-patterns.md) | 2,368 + 5,230 B (34/55 L); ~1.9k tok | MIT (same) | Game HUD taste; bans web defaults | **VENDOR** |
| 3 | anthropics/skills → `skills/frontend-design/` (SKILL.md + LICENSE.txt) | 9,390 B / 71 L; ~2.3k tok | Apache-2.0 (LICENSE.txt, 177 L, no copyright line) | Method: ground in the subject's world; avoid templated defaults; deliberate type and palette. Web-worded ("the hero…") | **VENDOR** (also in claude-plugins-official as `frontend-design`; recommend, don't depend) |
| 4 | threejs-game-skills → `skills/threejs-gameplay-systems/references/game-feel.md` | 12,909 B / 315 L; ~3.2k tok | MIT (same) | Motion and juice: trauma shake, hitstop, squash, FOV punch, tuning table | **VENDOR** (file only) |
| 5 | gamedev-skills/awesome-gamedev-agent-skills → `skills/disciplines/game-ui-ux/` (SKILL.md + references/layout-and-flow.md) | 8,436 B / 151 L; ~2.1k tok (+ref, size not fetched) | Apache-2.0 + root `NOTICE` ("Copyright 2026 Abhishek Barali and the awesome-gamedev-agent-skills contributors") | HUD engineering: anchors, safe area, gamepad focus, screen stack, event-driven HUD. Says "Godot 4.7", "Unity 6.3 LTS" | **VENDOR** (optional; engineering, not taste) |
| 6 | openai/plugins → `plugins/game-studio/skills/game-ui-frontend/SKILL.md` | 5,060 B / 112 L | **No LICENSE in repo root or plugin** (README has no license mention) | Best HUD numbers seen: "one primary persistent HUD cluster and at most one small secondary"; "no more than roughly 20-25% of the viewport covered by persistent HUD on desktop"; keep centre and lower-middle clear | **PARAPHRASE + cite** (do not copy) |
| 7 | pbakaus/impeccable → `plugin/skills/impeccable/` (SKILL.md 12,541 B / 87 L, v4.5.2; ~45 refs, e.g. critique.md 42,682 B, craft-floor.md 4,484 B, animate.md 5,236 B) | ~3.1k tok SKILL + refs on demand | Apache-2.0 + NOTICE.md (ios/android refs derived from ehmo/platform-design-skills, MIT) | Web UI only. Needs a launcher binary "downloaded once on first run". Plugin hooks run it on SessionStart, PostToolUse Edit\|Write, Stop | **RECOMMEND** for web menus or a store page only; borrow `animate.md`/`craft-floor.md` ideas with citation |
| 8 | Leonxlnx/taste-skill → `skills/taste-skill/SKILL.md` (name `design-taste-frontend`) | 87,253 B / 1,206 L; ~22k tok | MIT, "Copyright (c) 2026 Leonxlnx" | Web landing pages only; 13 skills, all web | **REJECT** (borrow the one-line "Design Read" idea) |
| 9 | nextlevelbuilder/ui-ux-pro-max-skill → `.claude/skills/ui-ux-pro-max/` | 15,969 B / 214 L + CSV database + python search | MIT, "Copyright (c) 2024 Next Level Builder" | Web/app UI database; "game" appears 0× in SKILL.md | **RECOMMEND** for out-of-game menus only |
| 10 | linegel/threejs-complete-set-of-skill → `skills/threejs-visual-validation`, `threejs-exposure-color-grading`, `threejs-object-sculptor` | 6,205 / 8,049 / 10,576 B | ISC, "Copyright (c) 2026 Three.js WebGPU Skill Pack contributors" (per-skill LICENSE) | Rigorous but Three.js r185 WebGPU/TSL only. Rendering technique, not taste | **RECOMMEND** for WebGPU projects |
| 11 | emalorenzo/three-agent-skills → `skills/three-best-practices` | 13,205 B / 334 L | MIT (frontmatter) | Performance rules | **REJECT** for design |
| 12 | omer-metin/skills-for-antigravity → `skills/game-ui-design`, `skills/lighting-design` | 3,669 / 3,685 B | Apache-2.0 | Persona fluff ("You are a game UI designer who has shipped AAA titles…"). The substance lives in references I did not open | **REJECT** |
| 13 | arjun988/blender-skills → `.claude/skills/lighting`, `lookdev` (95 skills) | 3,716 / 2,015 B | MIT, "Copyright (c) 2026 blender-skills contributors" | Generic tables: three-point "Key 45° above, 30° side", Kelvin table, HDRI 0.5–2.0 | **REJECT** (generic three-point is the default look we ban) |

### 2.2 Exact vendoring layout (copy verbatim, add notices)
I recommend [judgment] one router skill plus vendored texts. A single listing entry avoids collisions with a user's own `frontend-design` install, and loading stays per phase:
```
plugins/game-studio/
├── THIRD_PARTY_NOTICES.md            # new: one section per vendored source (see 2.3)
└── skills/
    └── game-design-sense/            # new skill, our own SKILL.md (router, <150 lines)
        ├── SKILL.md                  # user-invocable: false; phase→file table (2.4); NO verbatim copies here
        └── vendor/
            ├── anthropic-frontend-design/   SKILL.md (unchanged) + LICENSE.txt (from anthropics/skills)
            ├── threejs-aaa-graphics-builder/ SKILL.md + references/{visual-scorecard,technical-art,authoring-recipes,shader-cookbook}.md + LICENSE (copy of root MIT)
            ├── threejs-game-ui-designer/     SKILL.md + references/ui-patterns.md + LICENSE (MIT)
            ├── threejs-game-feel/            game-feel.md + LICENSE (MIT)
            └── gamedev-game-ui-ux/           SKILL.md + references/layout-and-flow.md + LICENSE + NOTICE (Apache-2.0)
```
- Vendored SKILL.md files under `vendor/` sit below the skill root, so they aren't discovered as separate skills. Plugin skills are discovered at `skills/<name>/SKILL.md` [docs: skills table, "Plugin `<plugin>/skills/<skill-name>/SKILL.md`"]. To be safe, rename each vendored copy to `UPSTREAM-SKILL.md`.
  - [UNVERIFIED] whether nested SKILL.md files are scanned. Run `claude plugin validate` and check `/skills`.
  - For Apache files, the rename is a modification: put "Renamed from SKILL.md; content unchanged" in THIRD_PARTY_NOTICES.
- Pin the upstream commit in THIRD_PARTY_NOTICES. HEAD on 2026-10-10:
  - anthropics/skills 2026-10-09T18:45:49Z
  - threejs-game-skills 2026-09-27T23:23:17-04:00
  - awesome-gamedev 2026-10-09T16:03:19+05:45

  Record the SHAs with `git ls-remote` when vendoring.
- Alternative if the user wants each design skill invocable on its own (`/game-studio:frontend-design`): put each folder at `skills/<name>/SKILL.md` instead. This costs one listing entry each and risks the compaction-budget problem in §1.6.

### 2.3 License obligations (verified against the fetched license texts)
- **MIT** (threejs-game-skills, taste, ui-ux-pro-max, arjun988): "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software." (LICENSE line 12) → ship the LICENSE file next to the copied files.
- **ISC** (linegel): "provided that the above copyright notice and this permission notice appear in all copies" → ship the LICENSE.
- **Apache-2.0 §4** (frontend-design, awesome-gamedev, impeccable, omer-metin), lines 90–107 of the fetched LICENSE.txt:
  - (a) give recipients a copy of the License
  - (b) "cause any modified files to carry prominent notices stating that You changed the files"
  - (c) retain copyright, patent, trademark and attribution notices
  - (d) if the Work has a NOTICE file, include its attribution notices in a NOTICE you distribute

  Practical steps: ship LICENSE.txt, copy awesome-gamedev's `NOTICE` verbatim, and add a header line to any file we edit.
- **No license** (openai/plugins `game-ui-frontend`): all rights reserved by default → paraphrase facts and numbers with a citation only.
- THIRD_PARTY_NOTICES.md row format: `component | upstream URL@commit | path(s) | license | copyright line | modified? (what)`.
- The game-studio plugin itself stays MIT. Apache-2.0 and MIT subfolders can coexist when each keeps its notices. [judgment; standard practice]

### 2.4 Phase → design material loading table (for game-studio SKILL.md)
Rule: **read the files for the current phase at phase start. Don't invoke all design skills up front.** Re-read after compaction if they're needed again.
| Phase (game-studio) | Load (Read) | Why |
|---|---|---|
| Intake / brief / art bible (main thread) | `frontend-design` UPSTREAM-SKILL.md (method only; ignore web "hero" specifics) + `threejs-aaa-graphics-builder` SKILL + `technical-art.md` + `visual-scorecard.md` | Ground in the subject's world, avoid named defaults, write gradable criteria before building |
| Blockout and modeling | `technical-art.md` only (silhouette, shape language, scale) | Keep context free for modeling refs |
| Lighting, materials, post (three.js) | `authoring-recipes.md` + `shader-cookbook.md`. WebGPU projects: also recommend linegel `threejs-exposure-color-grading` (one tone-map/output owner) | Presets with numbers |
| Lighting (Godot/Unity) | `technical-art.md` + game-studio art-direction.md. No vendored engine-specific design skill exists | Gap (§4) |
| UI / HUD | `threejs-game-ui-designer` SKILL + `ui-patterns.md` + `gamedev-game-ui-ux` (layout, safe area, focus) + paraphrased OpenAI HUD budget (≤1 primary + ≤1 small secondary cluster; ≤~20–25% viewport persistent HUD; centre and lower-middle clear) | Taste plus engineering |
| Motion / game feel / animation polish | `game-feel.md` | Tuning values for juice |
| Visual review (`art-critic`) | Agent body: "Read `visual-scorecard.md` and `design/art-bible.md` before scoring". Optionally `skills: [game-studio:game-design-sense]` [UNVERIFIED naming] | Independent judge with anchors |
| Out-of-game web (store page, launcher, settings web app) | Recommend the user install `frontend-design@claude-plugins-official` or `impeccable` | Web-specific skills fit here |

### 2.5 Integration mechanics (verified in official docs)
- **Cross-marketplace `dependencies`** [plugins-reference `dependencies`; plugins/dependencies]:
  - An entry is `"name"`, `"name@marketplace"` or `{ "name", "marketplace", "version" }`. Bare names resolve in our own marketplace.
  - A cross-marketplace dependency installs only if the root marketplace.json has `"allowCrossMarketplaceDependenciesOn": ["claude-plugins-official"]`, or if the user already has the dependency enabled at the same scope.
  - If it's not allowed and declared in plugin.json: "the install completes without the dependency and your plugin then fails to load". If declared in the marketplace entry, the install is refused.
  - `version` ranges resolve against `<plugin>--v<version>` git tags.
  - Example, if ever used: `"dependencies":[{"name":"frontend-design","marketplace":"claude-plugins-official"}]` plus the allowlist.
  - The official marketplace is added automatically "the first time you start an interactive terminal session" [discover-plugins]. Whether the desktop app does the same is [UNVERIFIED]. **Decision: don't use dependencies for design skills.**
- **Subagent `skills:`** [sub-agents]: "The full content of each listed skill is injected into the subagent's context at startup, up to the first 32 distinct names". A missing or disabled skill is skipped with a debug-log warning. Skills with `disable-model-invocation: true` can't be preloaded. Plugin agents support `skills` [plugins/components]. The plugin-skill name format isn't documented: use `game-studio:game-design-sense` and test. [UNVERIFIED]
- **Skill naming**: a plugin skill is `/plugin-name:skill-name`. It doesn't collide with a user's own `frontend-design` because "plugin skills are namespaced" [skills].
- **Context**: invoked skill content "stays in context across turns". Compaction keeps the first 5,000 tokens per skill within 25,000 total, filled from the most recent [skills]. Set `user-invocable: false` on the router so it lists for Claude but stays hidden from `/`.

## 3. "Never do" list
1. **Never declare a hard plugin dependency on a third-party design plugin.** An unresolved cross-marketplace dependency makes game-studio fail to load [docs, plugins/dependencies].
2. **Never vendor impeccable as a plugin component.** Its hooks.json runs a downloaded binary on every SessionStart, every Edit|Write and every Stop. Plugin hooks "fire on every matching event in every session" (round-1 01 §3.5) [impeccable plugin/hooks/hooks.json; SKILL.md "downloaded once on first run"].
3. **Never load taste-skill into a game session.** It is 87 KB (~22k tokens), longer than the whole compaction re-attach budget per skill (5k), and it scopes itself to web landing pages ("Not dashboards…").
4. **Never copy text from openai/plugins `game-ui-frontend`.** It has no license file.
5. **Never invoke more than ~3 skills at session start.** Older invoked skills, including the director, can be dropped after compaction (25k shared budget, most recent first).
6. **Never use the generic three-point and Kelvin presets as a look** (arjun988 `lighting`, "Key 45° above, 30° side"). Round 1 found default lighting is a measurable AI tell (03 §1.4). Lighting must come from the art bible.
7. **Never rely on `skills:` preload alone for the critic.** It's unverified for plugin names and reportedly flaky [UNVERIFIED], so also add explicit Read steps in the agent body.
8. **Never strip LICENSE or NOTICE files when vendoring**, and never edit vendored Apache files without a change note (Apache §4(b),(d)).

## 4. Gaps and unverified items
- No skill found gives design sense for **Godot or Unity lighting and post** or for **Blender look-dev with real taste**. The Blender packs are generic. RobLe3/cc-blender-skill has `blender-lighting`, `reference-look-calibration` and `quality-refinement-autoloop` (MIT, 2026-05-01) but **I did not open them** (budget). Agent covering Blender should check them.
- Star counts: all [UNVERIFIED] (API blocked).
- The plugin-skill name format in `skills:` is [UNVERIFIED]. The claimed preload bug (claudeissues #67251, #51007) is [UNVERIFIED]: the page was unreachable.
- Whether the desktop app auto-adds `claude-plugins-official` is [UNVERIFIED]. Whether nested `vendor/**/SKILL.md` is discovered as a skill is [UNVERIFIED]; renaming to UPSTREAM-SKILL.md avoids the question.
- Not opened:
  - awesome-gamedev `create-game-assets/references/art-direction.md`
  - OpenAI `three-hud-layout-patterns.md` and `frontend-prompts.md`
  - omer-metin references
  - arjun988 mood skills (`cozy-wholesome-mood`, `dark-gritty-mood`, …)
  - impeccable `animate.md`/`craft-floor.md` (only their sizes)
- Motion-design skills found by search (LottieFiles/motion-design-skill, dylantarre/animation-principles, vibe-motion/skills disney-animation-rule-skill, iart-ai/motion-design-skills) were **not opened**. They appear to target UI and web motion [UNVERIFIED].

## 5. Sources
- Official docs (fetched .md, 2026-10-10): https://code.claude.com/docs/en/plugins-reference (dependencies, defaultEnabled), https://code.claude.com/docs/en/plugins/dependencies (cross-marketplace, allowlist, failure modes, tags), https://code.claude.com/docs/en/sub-agents ("Preload skills into subagents"), https://code.claude.com/docs/en/skills (locations/namespacing, lifecycle 5k/25k, user-invocable), https://code.claude.com/docs/en/plugins/components (plugin agent fields incl. `skills`), https://code.claude.com/docs/en/discover-plugins (official marketplace auto-added in terminal)
- https://github.com/anthropics/skills: skills/frontend-design/{SKILL.md,LICENSE.txt}, canvas-design/LICENSE.txt, README.md (license statement), .claude-plugin/marketplace.json
- https://github.com/anthropics/claude-plugins-official: .claude-plugin/marketplace.json (315 plugins; `frontend-design` at ./plugins/frontend-design), plugins/frontend-design/{.claude-plugin/plugin.json, skills/frontend-design/SKILL.md, LICENSE, README.md}
- https://github.com/majidmanzarpour/threejs-game-skills: LICENSE; skills/threejs-game-ui-designer/{SKILL.md,references/ui-patterns.md}; skills/threejs-aaa-graphics-builder/{SKILL.md, references/*}; skills/threejs-gameplay-systems/references/game-feel.md
- https://github.com/gamedev-skills/awesome-gamedev-agent-skills: LICENSE, NOTICE, skills/disciplines/game-ui-ux/SKILL.md
- https://github.com/openai/plugins: plugins/game-studio/skills/game-ui-frontend/SKILL.md; README.md (no license)
- https://github.com/pbakaus/impeccable: LICENSE, NOTICE.md, .claude-plugin/marketplace.json, plugin/.claude-plugin/plugin.json, plugin/hooks/hooks.json, plugin/skills/impeccable/SKILL.md, plugin/agents/impeccable-{finish-reviewer,asset-producer}.md
- https://github.com/Leonxlnx/taste-skill: LICENSE, .claude-plugin/{marketplace,plugin}.json, skills/llms.txt, skills/taste-skill/SKILL.md (+ gpt-tasteskill, redesign-skill, minimalist-skill)
- https://github.com/nextlevelbuilder/ui-ux-pro-max-skill: LICENSE, .claude-plugin/plugin.json, .claude/skills/ui-ux-pro-max/SKILL.md
- https://github.com/linegel/threejs-complete-set-of-skill: LICENSE, README.md, skills/threejs-{visual-validation,exposure-color-grading,object-sculptor,choose-skills,ambient-contact-shading,sky-atmosphere-and-haze}/SKILL.md
- https://github.com/emalorenzo/three-agent-skills: README.md, skills/three-best-practices/SKILL.md
- https://github.com/omer-metin/skills-for-antigravity: LICENSE, skills/{game-ui-design,lighting-design}/SKILL.md
- https://github.com/arjun988/blender-skills: LICENSE, .claude/skills/{lighting,lookdev,pixel-art-style}/SKILL.md
- https://github.com/RobLe3/cc-blender-skill: LICENSE only (tree listed)
- Search-only (not opened): claudskills.com, skills.sh, claudemarketplaces.com listings for motion-design skills; claudeissues.com #67251/#51007 (unreachable).
