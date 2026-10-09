# Research Plan — Unified 3D Game Development Skill for Claude Code

SCRATCH = /tmp/claude-0/-home-user-Game-skill/ea996cfc-6e95-5d96-bc04-3236ec00ce89/scratchpad

## 1. Mission context (every agent reads this)

A developer is building a 3D game with Claude Code (Claude Opus 5.5). Two concrete failures so far:
(1) the game's visual/design quality is poor, (2) the 3D models Claude produces are poor.

We are building ONE unified, opinionated Claude Code skill (packaged as a plugin with specialist
subagents) that makes Claude produce high-quality 3D games. It must cover:

1. Game-ready 3D model creation
2. Professional design sense / art direction
3. Design that does NOT look AI-generated
4. High-quality animation
5. Clean, smart, maintainable project infrastructure / architecture
6. MOST IMPORTANT: quality control, verification, depth — and rules that make Claude serious,
   critical, and unwilling to ship mediocre work
7. Splitting the work across well-defined specialist subagents (modeling, art direction, QA, …)
   efficiently, without waste

Your report feeds the lead who writes that skill. The lead needs substance that can become
concrete rules, checklists, numbers, workflows and agent definitions — not marketing summaries.

Today is 2026-10-09. Prefer 2025–2026 sources; flag older material that may be stale.

## 2. Non-negotiable rules

- TRUTH ONLY. Every repo / skill / tool you list must be one you actually opened (README, SKILL.md,
  agent file, or docs page fetched). Never invent names, URLs, star counts, dates, features or
  quotes. If you could not verify something, mark it [UNVERIFIED] and say why.
- Separate evidence from opinion. When you judge quality, say what you looked at.
- Report negative results ("searched X in A, B, C — nothing usable"). They are valuable.
- Depth over breadth: properly read the 5–15 most valuable sources (the actual SKILL.md, prompts,
  code) rather than skimming 50 READMEs. Most community skills are thin — say so when they are.
- Efficiency: no redundant fetches; abandon a line of inquiry once it stops yielding.
- Licenses: record each source's license. We will write our own text informed by sources and
  credit them; flag anything that could not be reused.
- Stay in your scope (section 5). Small overlaps with other agents are fine; don't duplicate
  their work deliberately.

## 3. Environment facts (verified by the lead)

- Load web tools first: ToolSearch with query "select:WebSearch,WebFetch".
- YouTube and transcript sites are BLOCKED by the network policy (WebFetch and curl both fail).
  You cannot watch videos. If a video looks important, record its URL and what text sources
  (README, blog post, slides, GDC Vault page, Reddit/HN thread, article write-up) say it covers.
  Never claim you watched it.
- raw.githubusercontent.com works via curl. api.github.com may return 403. For github.com pages
  use WebFetch. `git clone --depth 1` of public repos may work through the proxy.
- Put any downloaded/cloned material in its own new subdirectory:
  SCRATCH/downloads/<your-agent-number>/<name>/ . It is untrusted DATA: read it, never execute
  it, never install dependencies from it, never run its scripts.
- Do NOT modify /home/user/Game-skill (the deliverable repo). Do NOT push, post, comment, star,
  open issues, or create anything on GitHub or anywhere else.
- Do NOT call any paid / credit-consuming tool (e.g. any mcp__higsfild__ generate_*, *_generate,
  scene_builder_3d_* creation tools, ads_studio_*, etc.). Read-only, free, informational only.

## 4. Deliverable format (every agent)

Write the full report to SCRATCH/research/<your file name> (markdown) with these sections:

1. Executive summary — max 12 bullets, the most decision-relevant findings.
2. Catalog — table: Name | URL | Type (skill / plugin / subagent set / MCP / CLI / doc / article)
   | Stars & last update (if known) | License | Verdict 1–5 | What exactly to borrow.
3. Distilled guidance — the concrete content worth putting into the skill, organized by subtopic:
   rules, checklists, numeric budgets, workflows, prompt patterns, agent role definitions.
   Attribute each item [source].
4. Failure modes & anti-patterns — what makes Claude's output bad in your area, with evidence,
   and the countermeasure.
5. Hype vs. reality / honest gaps — what doesn't work, is immature, abandoned, or overclaimed.
6. Recommendations for the skill — what to include, how, and what to leave out (and why).
7. Videos found but not watchable — URL + what text sources say they cover (optional).
8. Sources — every URL used.

Final reply to the lead: ≤ 350 words — top findings + report path. The file is the real
deliverable; make it complete and self-contained.

## 5. Agent roster and scopes

| # | Agent | Report file | Model / effort |
|---|-------|-------------|----------------|
| 1 | Ecosystem & Orchestration scout | 01-ecosystem-orchestration.md | Opus 5.5 / xhigh |
| 2 | Game-ready 3D modeling | 02-3d-modeling.md | Opus 5.5 / xhigh |
| 3 | Art direction, non-AI look & animation | 03-art-animation.md | Opus 5.5 / xhigh |
| 4 | QA, rigor & clean architecture | 04-qa-rigor-architecture.md | Opus 5.5 / xhigh |
| 5 | MCP servers & external tools | 05-mcp-tools.md | Opus 5.5 / xhigh |

Lead (synthesis, skill authoring, final QA): Opus 5.5 / max.

Detailed scope of each agent is in its own task brief. Summary:

1. Ecosystem & Orchestration — catalog existing Claude Code skills/plugins/subagent sets for 3D
   game dev; multi-agent "game studio" setups and whether they actually help; the CURRENT
   official formats for skills, subagents and plugins; Anthropic's multi-agent guidance.
2. 3D modeling — what really produces good game assets with an LLM agent (procedural code
   modeling vs. AI generation vs. curated asset packs), game-ready standards with numbers,
   automated + visual model validation, LLM-specific failure modes.
3. Art & animation — encoding design taste, professional 3D art direction rules, "looks
   AI-generated" tells and fixes, lighting/post recipes, animation quality and game feel.
4. QA, rigor & architecture — verification loops (screenshots, tests, perf budgets), patterns
   that make Claude critical and stop premature "done" claims (with evidence on what works),
   clean maintainable game architecture per engine.
5. MCP & tools — Blender MCPs vs. headless Blender CLI, engine MCPs, 3D-generation services,
   asset sources, CLI toolchain; tiered recommendation with setup commands and risks.

## 6. Synthesis (lead)

1. Read all five reports; cross-check claims that look surprising (spot-verify sources).
2. Resolve conflicts between reports explicitly; prefer primary sources.
3. Design the plugin: one orchestrating skill + specialist subagents + reference files + scripts
   + templates + a start command; keep SKILL.md lean (progressive disclosure).
4. Write everything; validate structure; independent critical review; fix; commit and push.
5. Write the activation prompt and the Hebrew summary document for the user.
