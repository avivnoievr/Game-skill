# Research round 2 — find what the game-studio skill is still missing

SCRATCH = /tmp/claude-0/-home-user-Game-skill/ea996cfc-6e95-5d96-bc04-3236ec00ce89/scratchpad

## Context (read first)
- The plugin already exists at /home/user/Game-skill (READ-ONLY for you): plugins/game-studio/skills/game-studio/
  (SKILL.md, references/*.md, references/engines/*.md, templates/, scripts/) and plugins/game-studio/agents/*.md.
- Round-1 research reports are in /home/user/Game-skill/docs/research/01..05 — skim the ones relevant to your
  scope FIRST so you do not repeat them. Your job is what is MISSING or WEAK, not re-proving known facts.
- The user (a game developer) has Blender installed on his own computer and works in the Claude desktop app on
  that computer; every developer who uses the skill will also have Blender installed locally. So a live Blender
  MCP connection and the local Blender CLI are both available to the skill on users' machines.
- The user's main complaints: Claude's 3D models are bad (shapeless primitive assemblies), the game looks
  AI-made, and Claude does not know WHICH tools to use and HOW. He tried Higgsfield's image-to-3D and got a single
  fused mesh with mushy, uncontrollable textures and no separate parts. He wants a skill that actually works:
  correct tools, correct procedures, explicit "never do this" rules, and design-sense skills loaded at the start.

## Rules
- TRUTH ONLY. Open every source you cite. Mark anything unconfirmed [UNVERIFIED]. Report negative results.
- Evidence over opinion; when you give an opinion, label it [judgment].
- Do NOT modify /home/user/Game-skill. Do NOT push/post/comment anywhere. Do NOT call paid or credit-spending
  tools (e.g. any mcp__higsfild__ generation/creation tool). Read-only, free calls only.
- Do NOT install packages, build projects, or clone large repos. Fetch single files from raw.githubusercontent.com
  (curl works) or use WebFetch. Put downloads in SCRATCH/downloads2/<agent-number>/. Never execute downloaded code.
- Web tools: load with ToolSearch "select:WebSearch,WebFetch".
- YouTube is reachable. yt-dlp is installed: `python3 -m yt_dlp`.
  * search: python3 -m yt_dlp "ytsearch8:<query>" --flat-playlist --print "%(id)s | %(title)s | %(duration)s | %(channel)s"
  * transcript: python3 -m yt_dlp --skip-download --write-auto-subs --write-subs --sub-langs "en.*" --sub-format vtt -o "SCRATCH/downloads2/<n>/%(id)s" URL
    then clean: sed -e 's/<[^>]*>//g' FILE.vtt | grep -v -E -- '-->|^WEBVTT|^Kind|^Language|^$' | awk '!seen[$0]++'
  * Video/frame download is blocked by YouTube's bot check from this IP — do not try to bypass it (no cookies).
- Instagram: public pages only, never log in. Expect little usable text; do not spend many calls there.
- BUDGET: at most ~40 tool calls. Create your report file EARLY and append to it as you go, so partial work
  survives an interruption. Stop when returns diminish.

## Report format (markdown, ≤ 350 lines) — SCRATCH/research2/<your file>
1. Summary (≤ 10 bullets)
2. Ready-to-use additions for the skill: rules, step-by-step procedures, tables, numbers — written so they can
   be pasted into a skill with light editing. Attribute each item [source].
3. "Never do" list for your area, each with the reason and evidence.
4. Gaps you could not close, and unverified items.
5. Sources (URLs; for videos: URL + timestamp).
Final reply to the lead: ≤ 200 words + report path.
