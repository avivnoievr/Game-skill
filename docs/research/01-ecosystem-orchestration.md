# 01 — Ecosystem & Orchestration (Research Agent 1)

Date: 2026-10-09. Downloads (untrusted, read-only): `SCRATCH/downloads/1/` (docs/, anthropic/, cloned repos).
Official docs were pulled as `.md` from `code.claude.com/docs/en/*.md` on 2026-10-09 and read directly.

## 1. Executive summary

1. **No existing project solves our problem.** Most game-dev "studio" packs are process and role-play scaffolding, and most Three.js/engine skills are API cheat sheets. The one strong exception for 3D web games is `majidmanzarpour/threejs-game-skills`, which has a director, a scorecard, measured canvas metrics and an evidence manifest. Borrow its patterns.
2. **The biggest "studio" project's own measurement argues against heavy process.** Donchitos/Claude-Code-Game-Studios has about 26k stars and 49 agents. Its README reports that the `standard` rigor build wrote 30 docs before any code, and two blind reviewers plus a human playtest ranked it **last**. Its default is now `minimal`, and its team skills "name ten and run one" agent by default.
3. **The most successful autonomous game generator removed its multi-agent pipeline.** htdt/godogen has about 7k stars. Its changelog shows three steps: a single-context architecture (2026-04-03), dropping the external Gemini verification pass ("added no signal", 2026-04-26), and replacing the multi-stage skill pipeline with a thin runtime (2026-07-02). What it kept: proof from the running game, a 15–20 s video watched back, and engine "silent-failure" traps.
4. **Anthropic's strongest relevant evidence is the harness-design post (Mar 24 2026).** It used a planner + generator + **separate skeptical evaluator** with gradable criteria and Playwright interaction. A retro game maker: solo run 20 min / $9 with a **broken game**; full harness 6 h / $200, which worked.
   - Out of the box, "Claude is a poor QA agent": it talked itself into approving bugs. The evaluator needed calibration.
   - On Opus 4.6 the sprints were dropped and the evaluator moved to one end pass. The evaluator "is worth the cost when the task sits beyond what the current model does reliably solo."
5. **Self-evaluation is lenient, especially for design** (same post). Separating the doer from the judge is the strongest lever. Tune the judge to be skeptical, give it a rubric with **hard thresholds** and few-shot anchors, and give it real interaction with the running build.
6. **Multi-agent work costs a lot of tokens.** Anthropic measured agents at about 4× chat tokens and multi-agent systems at about 15×. Agent teams use about 7× in plan mode. Multi-agent is a poor fit for shared-context, dependency-heavy work and for most coding. → **Lean design: the main thread builds; subagents only for (a) verbose isolated work, (b) independent verification, (c) parallel independent assets.**
7. **Role names alone add nothing measurable.** Zheng et al. (EMNLP Findings 2024) found that personas in system prompts do not improve objective-task accuracy. The MAST study of 1600+ traces measured 41–86.7% failure rates across 7 multi-agent frameworks. Verifiers often did only superficial checks: a ChatDev chess game compiled but broke the rules.
8. **Subagents cannot ask the user** (`AskUserQuestion` is removed for all subagents). So intake, art direction choices and taste checkpoints must happen in the **main thread**.
9. **Cloud sessions (claude.ai/code) do not load marketplace plugins**, whether user-enabled or declared in the repo's `.claude/settings.json`. They **do** load committed `.claude/skills/`, `.claude/agents/` and `CLAUDE.md`. Ship both a plugin and a "copy into the project's `.claude/`" install path.
10. **Current official formats are verified** (section 3.6). Several facts matter for the design:
    - Plugin agents **ignore** `hooks`, `mcpServers`, `permissionMode` and `initialPrompt`.
    - Plugin hooks fire in **every** session where the plugin is enabled.
    - The `memory` field auto-grants Read/Write/Edit, so it breaks read-only reviewers.
    - Subagent worktrees branch from the **default branch**, not HEAD, unless `worktree.baseRef: "head"`.
    - Subagents can nest up to 3 levels deep by default, with at most 20 running at once.
11. **There is a built-in way to measure our plugin:** `claude plugin eval` runs each case with and without the plugin (3 runs each) and reports Δ. `claude plugin validate --strict` checks structure. Use both before shipping.
12. **Official verification levers to wire in:**
    - Stop hooks of `type: "prompt"` or `type: "agent"` (agent hooks are experimental).
    - `/goal` conditions.
    - The bundled `/code-review`, `/simplify` and `/verify` skills. These are cheaper than custom reviewer agents for code correctness.

## 2. Catalog

| Name | URL | Type | Stars / last commit | License | Verdict | What exactly to borrow |
|---|---|---|---|---|---|---|
| threejs-game-skills | github.com/majidmanzarpour/threejs-game-skills | skill pack (9) | 2,456★ / 2026-09-27 | MIT | **5** | Director skill pattern; "lead + up to two workers, separate file ownership, I/O contract, acceptance criteria"; one independent review with raw captures + rubric, "ask for concrete defects rather than endorsement", "no recursive review cycles"; 10-category visual scorecard (premium = every cat ≥2, avg ≥2.3); automatic-failure list; canvas inspector metrics (colorEntropyBits <~3.0, dominantColorShare >~0.6, edgeDensity <~0.04, luminance.contrast <~60 = evidence against high scores); evidence manifest; workflow-evaluation scenario table |
| godogen | github.com/htdt/godogen | thin runtime + 1 skill | 7,070★ / 2026-09-22 | MIT | **4** | "Proof over claims" delivery rule; watch back a 15–20 s proof video before calling done; README.md as durable state; engine guides with only silent-failure traps + capture recipes (Godot `--write-movie`, Babylon headless-Chrome GPU check for swiftshader/llvmpipe); confirm spend before paid generation; changelog = evidence for de-scaffolding |
| Claude-Code-Game-Studios | github.com/Donchitos/Claude-Code-Game-Studios | 49 agents / 74 skills / 12 hooks | 25,972★ / 2026-10-08 | MIT | **3** | Do NOT copy the hierarchy. Borrow: "a story that changes anything the player sees is not closed until launched, observed and a screenshot retained" (never waived); `.claude/docs/run-and-observe.md` per-engine capture table; gate verdict token on the first line; rigor modes (minimal default) and their measurement; path-scoped rules idea |
| Threejs-Awesome-Graphics-Agent-Skills | github.com/scottstts/Threejs-Awesome-Graphics-Agent-Skills | skill pack (24) | 885★ / 2026-09-22 | MIT | 4 (for art/graphics) | `threejs-visual-validation`: freeze seeds, no-post baseline, near/design/far camera, stress seed, temporal checks; failure conditions ("approval relies on a single frame", "temporal artifacts judged from stills"). Repo is ~260 MB (example gallery) — reference, don't vendor |
| 3dviz-pro-max | github.com/viettranx/3dviz-pro-max | plugin + marketplace | 698★ / 2026-09-11 | MIT | 4 (for modeling) | Honest-reporting rule ("separate what was built, observed, numerically checked and still limited"; "never describe an unobserved frame"); single-repo marketplace+plugin packaging (`source: "./"`) |
| GodotPrompter | github.com/jame581/GodotPrompter | plugin (56 skills, 9 agents) | 800★ / 2026-10-06 | MIT | 3 (Godot only) | Version-annotated Godot 4.5–4.7 API notes; 16 KB SKILL.md budget enforced by validator; multi-harness packaging. Agent descriptions use long `<example>` blocks (costly against the 15k-token description budget) |
| awesome-gamedev-agent-skills | github.com/gamedev-skills/awesome-gamedev-agent-skills | 75 skills + router | 1,373★ / 2026-10-09 | Apache-2.0 | 2 | Router-as-entrypoint idea; three.js notes pinned to r186. Visual-quality content is basic (materials/lighting 101) |
| CloudAI-X/threejs-skills | github.com/CloudAI-X/threejs-skills | 10 skills | 3,494★ / 2026-01-20 | MIT (README) | 2 | API cheat sheets Claude already knows; stale. Contradicts the official "Claude is already very smart" guidance |
| unity (official marketplace) | github.com/Unity-Technologies/unity-agent-plugin | vendor plugin (32 skills) | — / 2026-10-06 | Unity Companion License (restricts reuse) | 3 (Unity users) | Recommend installing for Unity projects (URP post-processing, physics, UI skills); don't copy text |
| unreal-engine-skills-for-claude-code (official) | github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin | vendor plugin (MCP) | — / 2026-09-17 | MIT | 3 (UE users; see agent 5) | Pattern: SessionStart hook injects a short "this is a UE project, prefer skill X" note |
| feature-dev (Anthropic demo plugin) | github.com/anthropics/claude-code/tree/main/plugins/feature-dev | command + 3 agents | — / 2026-10-08 | © Anthropic, all rights reserved | 4 (pattern) | 2–3 parallel explorers with different focuses; 2–3 architects (minimal / clean / pragmatic); 3 reviewers with different focuses; report only confidence ≥80; explicit user approval before implementation. Ideas only, no text reuse |
| develop-web-game (OpenAI Codex skill) | read via mirror github.com/nota-america/forgecat-agent-profiles (not present in openai/skills main on 2026-10-09) | skill | — | [UNVERIFIED] | 3 (→ agent 4) | `window.render_game_to_text()` JSON state, `window.advanceTime(ms)` deterministic stepping, `progress.md` with "Original prompt:", input-burst Playwright loop, "treat screenshots as source of truth" |
| GameStudio | github.com/bullish0x/GameStudio | CCGS-style, 55 agents | 19★ / 2026-06-13 | MIT | 2 | CCGS structure for web engines; `web3d-asset-pipeline` agent (72 lines) is a competent but thin Draco/Meshopt/KTX2/LOD checklist |
| Claude-Code-Solo-Studio | github.com/Ghraven/Claude-Code-Solo-Studio | 6 agents | 3★ / 2026-09-12 | MIT | 1 | Right instinct (no hierarchy), but its "skills" are `.claude/skills/*/prompt.md`, not `SKILL.md`. Per the docs they will not load as skills (my inference). The "~95% tokens to code" claim is unsubstantiated |
| game-developer subagent | github.com/VoltAgent/awesome-claude-code-subagents (07-specialized-domains/game-developer.md) | subagent | list 25,601★ | MIT | 1 | Keyword lists ("60 FPS stable maintained"); references a nonexistent "context manager". Nothing to borrow |
| blender-game-skills | github.com/majidmanzarpour/blender-game-skills | skill | 135★ / 2026-09-23 | MIT | n/a (README only → agent 2) | "Gated phases … each passed on rendered and measured evidence" |
| Substack critique of CCGS | gameproductionalchemist.substack.com/p/claude-code-game-studios-49-agents | article (Rob Sandberg, 2026-05-19) | — | © author | 3 | Valid points: same-model "independent" reviewers share biases; maintenance burden ("the planning tool becomes the project"). Factual error: it says all 49 agents share one context window, but each subagent has its own isolated context per the official docs |
| Harness design for long-running apps | anthropic.com/engineering/harness-design-long-running-apps | article (2026-03-24) | — | © Anthropic | **5** | Planner/generator/evaluator; gradable criteria (design quality, originality, craft, functionality); "sprint contract"; file-based handoffs; costs table |
| Effective harnesses for long-running agents | anthropic.com/engineering/effective-harnesses-for-long-running-agents | article (2025-11-26) | — | © Anthropic | 4 | `feature_list.json` with `"passes": false`; one feature at a time; progress file + git; `init.sh`; end-to-end testing "as a human user would" |
| Multi-agent research system | anthropic.com/engineering/multi-agent-research-system | article (2025-06-13) | — | © Anthropic | 4 | Token multipliers; delegation-brief elements; scale effort to complexity; outputs to filesystem |
| Building effective agents | anthropic.com/engineering/building-effective-agents | article (2024-12-19, older) | — | © Anthropic | 3 | "Simplest solution, increase complexity only when needed"; evaluator-optimizer pattern "when we have clear evaluation criteria" |
| MAST (Cemri et al., arXiv 2503.13657 v3) | arxiv.org/abs/2503.13657 | paper | — | arXiv | 4 | 14 failure modes; superficial verifiers; +15.6% from adding a high-level objective verification step to ChatDev. Models are older (GPT-4o, Claude 3.7) |
| Persona study (Zheng et al., arXiv 2311.10054) | arxiv.org/abs/2311.10054 | paper | — | arXiv | 3 | Persona prompts don't reliably improve objective tasks (2023–24 models) |
| Official Claude Code docs | code.claude.com/docs/en/{skills,sub-agents,plugins/*,plugin-evals,agent-teams,agents,workflows,hooks-guide,best-practices,costs,cloud-environments,worktrees}.md | docs | fetched 2026-10-09 | © Anthropic | **5** | All format facts in section 3.6 |
| Skill authoring best practices | platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | docs | fetched 2026-10-09 | © Anthropic | 5 | Concise; third-person descriptions; one-level-deep references; TOC for references >100 lines; eval-first |
| Agent Skills spec | agentskills.io/specification | spec | fetched 2026-10-09 | — | 5 | name ≤64 chars, `[a-z0-9-]`, no leading/trailing/double hyphen, **must match directory**; description ≤1024; body <5000 tokens recommended; <500 lines |

Negative / unverified results:
- No Reddit or Hacker News thread evaluating whether game-studio multi-agent setups produce better games. Searches returned listings and promos only. One r/ClaudeAI anecdote (2.7B tokens, mostly cache reads, for a game with per-character subagents) surfaced only in a search summary. [UNVERIFIED, not opened]
- No PlayCanvas-specific skill found. Bevy and Babylon.js are covered only inside godogen.
- These were seen in listings but **not opened**, so they are [UNVERIFIED]. Agents 2, 3 and 5 should check them:
  - `elithril/blender-kiln` (Blender MCP → validated GLB; listed in awesome-claude-code)
  - `Leonxlnx/taste-skill` (~94k★, "stops generic slop")
  - `OthmanAdi/planning-with-files` (~27k★)
  - `ozanzeng/blender-LPM-skill`
  - `linegel/threejs-complete-set-of-skill` ("screenshot-backed visual validation")
  - `emalorenzo/three-agent-skills`
- In Anthropic marketplaces (fetched `marketplace.json`), the official marketplace has `unity` and `unreal-engine-skills-for-claude-code` for games. The community marketplace (2,284 entries) has `godot-prompter`, `quick-question` (Unity harness), `summer`, `sprite-gen`, `spritecook` and `meta-vr`. No first-party 3D-game skill exists. `anthropics/skills` has no game skill (example-skills: algorithmic-art, canvas-design, frontend-design, webapp-testing, …).

## 3. Distilled guidance

### 3.1 When to use a subagent (decision rule) [docs: sub-agents, agents, best-practices; research post]
Spawn a subagent only if at least one of these holds:
- **(a) Verbose, isolated work.** The output would flood the main context with logs, mesh stats or many renders, and only a summary is needed back.
- **(b) Independent judgment.** A fresh context that never saw the generator's reasoning ("the agent doing the work isn't the one grading it").
- **(c) Independent parallel units.** No shared files and no mid-task dependencies.
- **(d) Tool restriction.** For example, a reviewer with no Write/Edit.

Stay in the main thread when the task needs back-and-forth with the user, when phases share a lot of context (plan → implement → test of one feature), or for quick targeted edits. [docs "Choose between subagents and main conversation"]

Scale effort to the task [research post]:
- Simple: one agent, 3–10 tool calls.
- Comparison: 2–4 subagents.
- Never spawn many subagents for simple work. "Spawning 50 subagents for simple queries" was an observed early failure.

### 3.2 Delegation brief template [research post: "objective, an output format, guidance on the tools and sources to use, and clear task boundaries"; threejs-game-director; best-practices]
```
OBJECTIVE: <one sentence, the outcome, not the method>
INPUTS (read these files, don't expect me to paste them): <abs paths: brief, art bible, asset spec, rubric, reference dir>
OWNERSHIP: you may write ONLY under <dir>; do not touch <dirs>
OUTPUT CONTRACT: write <path> (schema/sections ...); return ≤15 lines: verdict/status line first, paths, open risks
ACCEPTANCE CRITERIA: <numbered, testable — numbers from budgets.json / art bible>
EVIDENCE REQUIRED: <renders/screenshots/metrics paths>; "say what you ran and saw; if you couldn't run it, say so"
OUT OF SCOPE / STOP CONDITIONS: <...>; max <N> fix iterations then report blockers
```
- Subagents do not see the conversation or previously invoked skills, so restate any rule that must reach them. [sub-agents "What loads at startup"]
- Pass file references, not content ("lightweight references back to the coordinator").

### 3.3 Evaluator design (the critical role) [harness post unless noted]
- Separate agent with a fresh context and **no Write/Edit**. It gets raw evidence (captures, video frames, metrics, code paths) plus the art bible and rubric, **not** the generator's self-assessment.
- Convert taste into gradable criteria. The harness used Design quality, Originality, Craft and Functionality, and weighted design and originality higher because Claude already does well on craft. It explicitly penalised "AI slop" patterns such as "purple gradients over white cards".
- **Hard threshold per criterion. Any criterion below its threshold fails the gate**, with concrete feedback.
- Calibrate with few-shot examples or anchor images that carry detailed score breakdowns. threejs-game-skills ships `scene-1/2/3.jpg` anchors: 1 = primitive player/flat arena, 2 = authored kit + designed HUD + intentional lighting, 2.5–3 = dense layered world.
- The evaluator must **interact** with the running build (Playwright, or the engine's capture), not score one static frame. Animation needs unpaused motion evidence. [threejs-game-skills; graphics-skills visual-validation]
- Counter leniency explicitly. Observed failure: the evaluator found real issues, then "talk[ed] itself into deciding they weren't a big deal". Add: "your job is not to confirm this holds — find how it breaks" [CCGS team-polish] and "ask for concrete defects rather than endorsement of the lead's score" [threejs-game-director].
- Counter over-criticism too. "A reviewer prompted to find gaps will usually report some … Chasing every finding leads to over-engineering". Flag only gaps that affect correctness, the stated requirements, or a rubric threshold; treat the rest as optional. [best-practices]
- Verdict token on the first line (`ART-GATE: FAIL`). The caller parses it. [CCGS]
- Limit rounds: fix, then re-review **only the failed criteria**, with at most 2 rounds per gate, then escalate to the user. "Resolve findings without recursive review cycles." [threejs-game-director]
- Criteria wording steers the generator. Give the generator the same criteria up front: "outputs were noticeably better than a baseline … even on the first iteration". Avoid phrases that cause convergence ("museum quality" did). [harness post]
- Use the evaluator at milestones where the task is at the edge of the model's ability, not per edit. [harness post v2]

### 3.4 Durable state & anti-"premature done" [effective-harnesses; godogen; develop-web-game]
- `design/features.json`: every feature or acceptance test starts `"passes": false`. Agents may only flip `passes`, and only with evidence. Removing or editing tests is "unacceptable". JSON is used because "the model is less likely to inappropriately change or overwrite JSON files compared to Markdown".
- `progress.md`: the original prompt sits at the top; append decisions, done items, pending asset jobs (with IDs and costs), known defects, next step. Read it first after compaction or `/clear`. Godogen keeps the same content in README.md.
- One feature at a time; commit after each verified feature.
- Every session starts with: run → smoke test → only then build new features.
- "Judge progress from the running game, never from a clean build." Final proof is a short video or a capture set that the agent **reviews** before claiming done. [godogen]

### 3.5 Packaging facts that change the design (all verified in official docs, 2026-10-09)
- **Skill body persists in context** after it is invoked. On compaction only the **first 5,000 tokens** of each invoked skill are re-attached, within a 25k shared budget, so put the non-negotiable rules at the top of SKILL.md. Claude does not re-read the file, so write standing rules, not one-time steps. [skills]
- Description plus `when_to_use` is truncated at **1,536 chars** in the listing. The Agent Skills spec caps `description` at **1,024**, so stay ≤1,024 for portability. Write descriptions in the third person and put the key use case first. [skills; spec; best-practices]
- Keep SKILL.md under 500 lines (the spec recommends a body under 5,000 tokens). Keep references one level deep, and give any reference over 100 lines a table of contents. [skills; spec; best-practices]
- Combined subagent descriptions over **15,000 tokens** trigger a startup warning. Keep agent descriptions short and put detail in the body. [sub-agents]
- Subagents **cannot use** `AskUserQuestion`, `EnterPlanMode`, `ScheduleWakeup` or `Workflow`. `Agent` is withheld at the depth limit, which defaults to **3**. Concurrency limit is **20**. [sub-agents]
- Fork mode is on by default in interactive sessions, so subagents run in the **background** with a narrower built-in tool set: Read, Grep, Glob, LSP, Bash, PowerShell, Edit, Write, NotebookEdit, WebFetch, WebSearch, TodoWrite, Skill, ToolSearch, EnterWorktree, ExitWorktree, Monitor, TaskStop, SendMessage, Artifact. All MCP tools are kept. [sub-agents]
- The `memory:` field auto-enables Read/Write/Edit. **Don't give memory to read-only reviewers.** [sub-agents]
- Plugin agents support only these fields: `name, description, model, effort, maxTurns, tools, disallowedTools, skills, memory, background, omitClaudeMd, isolation ("worktree"), color, experimental.cacheTtl`. **Ignored** in plugins: `permissionMode, hooks, mcpServers, initialPrompt`. [plugins/components]
- Plugin hooks register when the plugin loads and fire on **every** matching event in every session. Guard them with a project marker check, or scope them through a skill's `hooks:` frontmatter, which registers when the skill is invoked and lasts the rest of the session. [plugins/components; skills table] Whether skill-frontmatter hooks work for **plugin** skills is not stated. [UNVERIFIED: test with `claude plugin validate` and a run]
- `isolation: worktree` branches from the **remote default branch**, not your HEAD, unless settings have `worktree.baseRef: "head"`. Even then it gets commits only. **Commit before delegating.** [worktrees]
- Model resolution: per-invocation parameter > frontmatter `model` > `CLAUDE_CODE_SUBAGENT_MODEL` > main model. If the main session is Opus 5.5, `model: opus` resolves to the main model, including `[1m]`. Use `inherit` for judgment roles. [sub-agents]
- A skill's `model:` field: the docs say it applies for the rest of the turn. CCGS's model-tiers.md claims it is **not** applied when Claude invokes the skill through the Skill tool, only when the user types `/name`. [UNVERIFIED community claim] Don't rely on skill-level model switching.
- `context: fork` skills run the body as a subagent prompt without conversation history, in the background by default (`background: false` to wait). Use them only for skills with explicit tasks. [skills]
- Agent teams are **experimental and disabled by default** (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). The docs recommend 3–5 teammates. There is no file isolation, no nested teams, and in-process teammates are not restored on resume. **Don't depend on them.** [agent-teams]
- Dynamic workflows: a JS script orchestrates many subagents and can be shipped in a plugin's `workflows/`. They show a "Large workflow" warning above 25 agents or 1.5M projected tokens. Optional; not needed for v1. [workflows]

### 3.6 Exact packaging spec (copied or adapted from official docs; URL per block)

**Recommended repo layout.** The marketplace sits at the repo root and the plugin in a subfolder, following the documented walkthrough. The deliverable repo's root `CLAUDE.md` then doesn't trigger the "CLAUDE.md at the plugin root is not loaded" validate warning.
```
<repo>/
├── .claude-plugin/marketplace.json
└── plugins/<plugin-name>/
    ├── .claude-plugin/plugin.json        # ONLY this file inside .claude-plugin/
    ├── skills/<skill-name>/SKILL.md      # + references/ scripts/ assets/
    ├── agents/<agent>.md                 # one file per subagent
    ├── hooks/hooks.json                  # optional, guarded
    ├── bin/                              # optional; NOTE: claude.ai/Cowork won't install a plugin with top-level bin/
    └── settings.json                     # optional; only "agent" and "subagentStatusLine" take effect
```

**plugin.json** (code.claude.com/docs/en/plugins/create.md + manifest-reference.md). Only `name` is required, in kebab-case.
- Names starting with `claude-`, `anthropic-` or `cc-plugin-` are an **error**.
- A whole-word `claude` elsewhere in the name is a warning.
- `version` pins users until it changes; omit it to track commits (see host-marketplace docs).
```json
{
  "name": "my-first-plugin",
  "description": "A greeting plugin to learn the basics",
  "version": "1.0.0",
  "author": { "name": "Your Name" }
}
```
Other fields: `displayName, homepage, repository, license, keywords, metadata, defaultEnabled, dependencies, settings, userConfig, skills (adds to default scan), commands, agents (replaces scan; .md files only), hooks, mcpServers, lspServers, outputStyles, workflows, experimental{themes,monitors,evals}`. Unknown top-level keys are stripped with a warning.

**marketplace.json** (code.claude.com/docs/en/plugins/create-marketplace.md). Requires `name`, `owner` and `plugins[]`; each entry needs `name` and `source`. Relative sources resolve from the marketplace root, must start with `./` and must not contain `..`.
```json
{
  "name": "my-marketplace",
  "description": "Plugins for my team",
  "owner": { "name": "Your Name" },
  "plugins": [
    { "name": "my-first-plugin", "source": "./plugins/my-first-plugin",
      "description": "A greeting plugin to learn the basics" }
  ]
}
```
- Reserved marketplace names include `claude-code-marketplace`, `claude-plugins-official`, `agent-skills`, `anthropic-*`-like impersonations, any non-ASCII name, `npm`, `github`, `inline`, `skills-dir`, and anything starting with `claudeai-`.
- Entries also accept `category`, `tags`, `strict` (default true), `version`, `displayName`, `dependencies` and `relevance`. An entry `version` is overridden by the one in plugin.json.

**Install commands** (plugins/install.md, cli-reference.md):
```
/plugin marketplace add owner/repo            # GitHub; pin a branch/tag: owner/repo#ref  (CLI also accepts owner/repo@ref)
/plugin install <plugin>@<marketplace-name>   # opens details; choose scope user|project|local
claude plugin marketplace add owner/repo#dev --scope project     # shell
claude plugin install <plugin>@<marketplace> --scope project
/plugin install <plugin> --marketplace owner/repo   # add+install in one step (session, v2.1.275+)
claude --plugin-dir ./plugins/<plugin-name>          # dev: load for one session, no install
claude plugin validate ./plugins/<plugin-name> --strict
/reload-plugins                                       # apply on-disk edits
```
Yes, a marketplace can come from a non-default branch: `owner/repo#branch`. The `extraKnownMarketplaces` source objects also take `ref`.

**Manual / cloud-session install** (cloud-environments.md: committed `.claude/skills/`, `.claude/agents/`, `.claude/commands/`, `CLAUDE.md`, `.claude/settings.json` hooks and `.mcp.json` load; marketplace plugins do not):
```
cp -r plugins/<p>/skills/*  <game-repo>/.claude/skills/
cp    plugins/<p>/agents/*.md <game-repo>/.claude/agents/
# commit. Names lose the plugin prefix: /<skill> and agent "art-critic" instead of "<p>:art-critic".
# Local-only alternative: ~/.claude/skills and ~/.claude/agents (NOT seen by cloud sessions).
```
- Placing `.claude-plugin/plugin.json` inside `.claude/skills/<name>/` makes a "skills-dir plugin". At project scope this loads only after the workspace trust dialog is accepted, and cloud sessions never show that dialog. [cloud behaviour UNVERIFIED] Prefer the plain copy for cloud sessions.
- Don't name a skill folder `synced` or `anthropic-skills*`.

**SKILL.md frontmatter** (code.claude.com/docs/en/skills.md). All fields are optional; `description` is recommended. Unknown fields are silently ignored.
- `name`: defaults to the directory name. In a plugin the command becomes `/<plugin>:<name>`, and bare `/<name>` also works if no other command uses it.
- `description`, `when_to_use`
- `argument-hint`, `arguments`
- `disable-model-invocation`: user-only, and **cannot be preloaded into subagents**.
- `user-invocable: false`: Claude-only.
- `allowed-tools`: pre-approval for that turn only.
- `disallowed-tools`
- `model`, `effort` (`low|medium|high|xhigh|max`)
- `context: fork`, `agent`, `background`
- `hooks`, `paths` (globs)
- `shell`, `metadata`, `license`, `compatibility`
- Substitutions available in the body: `$ARGUMENTS`, `$0`, `${CLAUDE_SKILL_DIR}`, `${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_EFFORT}`, `${CLAUDE_SESSION_ID}`.
- `` !`cmd` `` lines run before the content is sent. A failing command (non-zero exit) aborts the skill, so append `|| true`.
- claude.ai / API uploads accept only `name, description, license, compatibility, metadata, allowed-tools`. Anything else is a hard error there.

Example (skills.md):
```yaml
---
name: render-chart
description: Render a chart from a CSV file
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/render.sh *)
---
Run `${CLAUDE_SKILL_DIR}/scripts/render.sh <csv-file>` to render the chart.
```

**Subagent file** (sub-agents.md). Only `name` and `description` are required. Field names are camelCase. The `name` cannot contain `:`. In a plugin the name becomes `<plugin>:<name>`, with subfolders adding `:<sub>`. Mention with `@agent-<plugin>:<name>`.
- Full field list: `name, description, tools, disallowedTools, model (sonnet|opus|haiku|fable|full ID|inherit), permissionMode, maxTurns, skills, mcpServers, hooks, memory (user|project|local), background, omitClaudeMd, effort, isolation (worktree), color (red|blue|green|yellow|purple|orange|pink|cyan), initialPrompt, experimental.cacheTtl`.
- Adding "use proactively" to the description encourages auto-delegation.
- `tools: Agent(x, y)` type allowlists apply only to `--agent` main threads.
```markdown
---
name: code-reviewer
description: Expert code review specialist. Proactively reviews code for quality, security, and maintainability. Use immediately after writing or modifying code.
tools: Read, Grep, Glob, Bash
model: inherit
---
You are a senior code reviewer ensuring high standards of code quality and security. ...
```

**Hooks for quality gates** (hooks-guide.md). These go in `hooks/hooks.json`, which has the same shape as `settings.json`'s `"hooks"`. In plugin hooks, use `"${CLAUDE_PLUGIN_ROOT}/scripts/x.sh"`.
```json
{ "hooks": { "Stop": [ { "hooks": [ { "type": "agent",
  "prompt": "Verify that all unit tests pass. Run the test suite and check the results. $ARGUMENTS",
  "timeout": 120 } ] } ] } }
```
- Prompt hooks return `{"ok": false, "reason": ...}`, and that keeps Claude working.
- Agent hooks are **experimental**, allow up to 50 turns, and time out after 60 s by default.
- Stop hooks are overridden after **8** consecutive blocks (`CLAUDE_CODE_STOP_HOOK_BLOCK_CAP`). Command hooks should check `stop_hook_active`.

**Referencing plugin files from agents:** `${CLAUDE_PLUGIN_ROOT}` resolves inline in skill, command and agent Markdown bodies of a **plugin**. It is not available to Bash commands Claude runs, and it stays literal in a manually copied agent.
- Robust pattern: the orchestrating SKILL.md renders `${CLAUDE_SKILL_DIR}` into an absolute path and puts that path in every delegation brief.
- Fallback pattern (threejs-game-director): resolve the sibling path first, then the known install locations.
- Whether the agent `skills:` field needs namespaced plugin skill names is not documented. [UNVERIFIED: test]

**Validation & evaluation** (plugin-evals.md; skills.md). Requires v2.1.269+; it consumes plan usage, and costs are printed as list-price estimates.
- `claude plugin eval init` creates the cases.
- `claude plugin eval .` runs each case 3× with the plugin and 3× without it, reporting WITH / W/OUT / Δ.
- A `tool_used: Skill` grader checks triggering.
- `claude plugin validate .claude/skills` (v2.1.233+) finds bad frontmatter.

## 4. Failure modes & anti-patterns (multi-agent) → countermeasures

| Failure | Evidence | Countermeasure |
|---|---|---|
| Studio hierarchy / doc bloat → more cost, no better game | CCGS README: 30 docs before code, `standard` ranked last; Substack: "the planning tool becomes the project" | No director/lead tiers. Four durable files only: `brief.md`, `art-bible.md`, `features.json`, `progress.md` (+ optional `budgets.json`) |
| Self-evaluation leniency | harness post ("confidently praising the work") | Separate read-only critic, fresh context, hard thresholds, anchors |
| Evaluator talks itself out of findings; shallow tests | harness post; MAST FM-3.2/3.3 (ChatDev chess compiled but broke rules) | Require real input + rules checks + active-play captures; "find how it breaks"; score each criterion with a cited evidence path |
| Reviewer always finds something → over-engineering | best-practices callout | Severity tags; only correctness/requirement/threshold gaps block; ≤2 review rounds |
| Same-model correlated blind spots | Substack critique; persona study | Add non-LLM evidence (canvas metrics, mesh validator, tests, perf counters) and a **human checkpoint** at taste decisions (art direction, vertical slice) |
| Vague delegation → duplicate/misread work | research post (semiconductor example) | Brief template (3.2) with ownership + output contract |
| Too many agents / token blowup | research post (15×), agent teams (~7×), research-post anecdote "50 subagents" | ≤3 concurrent subagents; milestone-only evaluation; outputs to files; ≤15-line returns |
| Premature "done" | effective-harnesses; MAST FM-3.1 | `features.json` passes-gating; Stop prompt/agent hook (guarded) or `/goal` |
| Context loss/compaction | harness posts; skills lifecycle | progress.md; rules at top of SKILL.md; commit per feature |
| Parallel file conflicts | agent-teams docs | Strict per-asset directory ownership; worktree only after commit (base-branch footgun) |
| Subagent can't ask user → silent assumptions | sub-agents tool filter | Subagents return options/questions; main thread asks |
| Read-only reviewer gains write via `memory:` | sub-agents memory section | No `memory` on critics; no Write/Edit tools |
| Plugin hook fires in unrelated sessions | plugins/components "When plugin hooks fire" | Hook script exits 0 unless a project marker (e.g. `design/features.json`) exists |
| Plugin agents silently drop `mcpServers`/`hooks` | plugins/components | Declare MCP in plugin `.mcp.json` (visible to main too), or tell users to copy the agent to `.claude/agents/` for agent-scoped MCP |
| Plugin not available in cloud session | cloud-environments | Document the project-copy install; test in a cloud session |
| Stale API knowledge | GodotPrompter/CCGS engine reference dirs; godogen "verify against installed version" | Rule: read installed package source/types (`node_modules/three`, `godot --version`) before using version-sensitive APIs |

## 5. Hype vs. reality / honest gaps
- "49 agents = a studio": the agents are one model with different prompts. Persona labels don't add capability. CCGS's own data and its scaled-down defaults suggest the structure mostly buys traceability.
- "Token % to code" claims (Solo Studio ~95%, CCGS-style 30–50%): no measurements published. [UNVERIFIED]
- Separate evaluator, contradictory evidence:
  - Godogen: an external **different-model** (Gemini) vision pass "added no signal" on Opus 4.7. Author's statement, no data.
  - Anthropic: a **tuned skeptical Claude** evaluator gave large lift for apps at the edge of capability; the lift was smaller on Opus 4.6 for in-capability tasks.
  - Reconciliation: self-verification from captures is the default; one calibrated independent evaluator at milestones is for ambitious or premium work. Measure with `claude plugin eval`.
- QA by LLM still misses things: small layout issues, unintuitive interactions, deeply nested bugs [harness post]. Claude can't hear audio [harness post]. Headless WebGL often falls back to software rendering (swiftshader/llvmpipe) and produces blank or slow captures [godogen]. Browser alert modals aren't visible via Puppeteer [effective-harnesses].
- `claude plugin eval` costs real usage (cases × 3 × 2 runs plus judge calls).
- Agent hooks and agent teams are experimental.
- Most catalogued Three.js/engine skills duplicate knowledge Claude already has. Only a few encode taste with measurable gates (threejs-game-skills, graphics-skills visual-validation).

## 6. Recommendations for the skill (orchestration blueprint)

### 6.1 Roles: main thread + 3 custom subagents (+ built-ins)
| Role | Where | Why it exists (criterion 3.1) | Inputs → Outputs |
|---|---|---|---|
| **Director/Integrator** (the orchestrating skill) | main thread | Owns user dialogue (subagents can't ask), shared interfaces, integration, final call | user brief → `design/brief.md`, `design/art-bible.md`, `design/features.json` (passes:false), `design/budgets.json`, asset list; code; `progress.md` |
| **asset-builder** | subagent, parallel ≤3, `model: inherit` | (a) verbose: Blender/script logs, mesh stats, many renders; (c) assets are independent | asset spec + art bible + budgets → `assets/<id>/` (GLB, source script), `assets/<id>/report.md` (tri count, materials, UVs, scale, rig/clips, validator output), turntable/contact-sheet PNGs. Writes only `assets/<id>/` |
| **art-critic** | subagent, read-only (`tools: Read, Glob, Grep, Bash`; `disallowedTools: Write, Edit`), `model: inherit`, `effort: high` | (b) independence; (d) no writes | captures/video frames + metrics + art bible + scorecard/anchors → first line `ART-GATE: PASS/FAIL`, per-category score + evidence path, ≤10 ranked defects with fixes. Used for asset acceptance and milestone gates |
| **playtest-qa** | subagent, no Write/Edit to `src/` (return report; main saves) | (b)+(a): drives real input, long logs | running build URL/command + `features.json` + budgets → `QA-GATE` verdict, failing feature IDs with repro steps, console errors, perf numbers (frame time, draw calls, triangles), captures |
| Exploration/API lookup | built-in `Explore` | read-only, cheap | — |
| Code correctness | bundled `/code-review`, `/simplify` | already exists | diff → findings |

Not recommended as subagents:
- **Art director.** Generation, not judgment, and it needs the user's taste input. Make it a main-thread phase driven by the art-direction reference and enforced by `art-critic`.
- **Generic gameplay programmer.** Coding is mostly not parallelizable and has shared state.
- **Producer or any director tiers.**
- **Animator.** Fold rig/clip export into `asset-builder`. Gameplay animation and game feel belong in the main thread, checked by both critics. Add a separate animator only if the clip volume demands it.

### 6.2 Phases (parallel vs sequential)
1. **Intake** (main, sequential): ask ≤5 questions → `brief.md`. Pick a rigor level: `prototype | standard | premium`, from the user's words, as threejs-game-director does.
2. **Pre-production** (main): art bible, architecture sketch, `features.json`, `budgets.json`, asset specs.
   - Generator and critic get the same criteria up front.
   - **Human checkpoint:** approve the art direction (2–3 directions offered).
   - Commit.
3. **Production** (parallel): main builds the greybox playable loop and the test hooks (`render_game_to_text`, `advanceTime`, capture script) **while** up to 3 `asset-builder`s produce hero assets.
   - Each asset gets an `art-critic` acceptance pass on its turntable, at most 2 rounds.
4. **Integration + vertical slice** (main, sequential), then a **gate**: `art-critic` and `playtest-qa` run **in parallel** on the same build revision.
   - Main fixes; re-check only the failed criteria; at most 2 rounds.
   - Second **human checkpoint** with the proof video.
5. **Content expansion**: repeat steps 3–4 per milestone, not per edit. Narrow edits get targeted checks only.
6. **Release gate**: full QA + scorecard + perf budgets + `final-evidence.md`.

### 6.3 Cost controls
- At most 3 concurrent subagents.
- No `Agent` tool in subagents' `tools` (no nesting).
- Set `maxTurns` (e.g. builder 40, critics 25).
- Returns ≤15 lines; artifacts go to files.
- Evaluators run only at gates.
- Prototype rigor skips the critic gates but **never** the run-and-look rule.
- Use `inherit` for judgment roles. Don't use haiku for any judging.
- Measure Δ with `claude plugin eval` on 3–5 realistic briefs before claiming the plugin helps.

### 6.4 Leave out
- Hierarchies.
- More than about 5 agents.
- Agent teams (experimental).
- Dynamic workflows in v1.
- Per-edit reviews.
- Long `<example>` blocks in agent descriptions.
- API cheat-sheet skills.
- Copying Anthropic text: the claude-code repo is "all rights reserved", so reimplement ideas only.
- Copying Unity's text (Unity Companion License).
- MIT sources (CCGS, godogen, threejs-game-skills, graphics-skills, 3dviz) can be adapted with credit.

## 7. Videos found but not watchable
- godogen demos: youtu.be/eUz19GROIpY. The README says they show the agent building games, generating assets, and producing proof clips.
- threejs-game-skills demo games are linked as X posts plus Netlify builds: ridgedrift, snookerarena, starshipdogfight, tidesinger, ripcore (`*.netlify.app`). Not opened.

## 8. Sources
- Claude Code docs (all fetched 2026-10-09):
  - code.claude.com/docs/en/skills.md, sub-agents.md
  - plugins/overview, plugins/create, plugins/components, plugins/manifest-reference, plugins/create-marketplace, plugins/marketplace-reference, plugins/install, plugins/cli-reference, plugins/loading, plugins/anthropic-marketplaces, plugins/host-marketplace, plugins/publish, plugins/measure
  - plugin-evals.md, agent-teams.md, agents.md, workflows.md, hooks-guide.md, best-practices.md, costs.md, cloud-environments.md, worktrees.md, features-overview.md, llms.txt
- platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- agentskills.io/specification
- Anthropic engineering:
  - anthropic.com/engineering/harness-design-long-running-apps
  - anthropic.com/engineering/effective-harnesses-for-long-running-agents
  - anthropic.com/engineering/multi-agent-research-system
  - anthropic.com/engineering/building-effective-agents
  - anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Anthropic marketplaces (`.claude-plugin/marketplace.json` via raw.githubusercontent.com): anthropics/claude-plugins-official, anthropics/claude-plugins-community, anthropics/skills, anthropics/claude-code; plugins/feature-dev, plugins/frontend-design
- Community repos (all opened):
  - github.com/Donchitos/Claude-Code-Game-Studios
  - github.com/htdt/godogen
  - github.com/majidmanzarpour/threejs-game-skills
  - github.com/majidmanzarpour/blender-game-skills
  - github.com/scottstts/Threejs-Awesome-Graphics-Agent-Skills
  - github.com/CloudAI-X/threejs-skills
  - github.com/gamedev-skills/awesome-gamedev-agent-skills
  - github.com/viettranx/3dviz-pro-max
  - github.com/jame581/GodotPrompter
  - github.com/Ghraven/Claude-Code-Solo-Studio
  - github.com/bullish0x/GameStudio
  - github.com/Unity-Technologies/unity-agent-plugin
  - github.com/EpicGames/unreal-engine-skills-for-claude-code-plugin
  - github.com/VoltAgent/awesome-claude-code-subagents
  - github.com/hesreallyhim/awesome-claude-code
  - github.com/VoltAgent/awesome-agent-skills
  - raw mirror of develop-web-game: github.com/nota-america/forgecat-agent-profiles
- gameproductionalchemist.substack.com/p/claude-code-game-studios-49-agents
- arxiv.org/abs/2503.13657 (+ html v3)
- arxiv.org/pdf/2311.10054 (abstract via search summary)
