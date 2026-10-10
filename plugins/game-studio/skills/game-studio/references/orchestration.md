# Orchestration: who does what, when to delegate, how gates work

Contents: 1. Why this team is small · 2. Roles · 3. When to spawn a subagent · 4. Delegation brief ·
5. Parallel work · 6. Gate protocol · 7. Cost controls · 8. Failure modes

## 1. Why this team is small

Evidence from projects that tried big "AI studios":
- The largest Claude Code game-studio pack (49 agents) measured its heavy mode. It wrote 30 documents
  before any code, and blind reviewers ranked it **last**. Its default is now minimal.
- The most successful autonomous game generator removed its multi-stage pipeline and kept only three
  things: proof from the running game, a short recorded video that the agent watches back, and
  engine-specific traps.

What does help is narrower:
- A separate, skeptical evaluator with hard thresholds, which reviews the running build, for work at
  the edge of the model's ability (Anthropic's harness study).
- Context isolation for verbose work (renders, logs, mesh reports).
- Parallelism for truly independent units (separate assets).

Role names add nothing by themselves. A subagent is the same model with a different prompt; what it
contributes is a fresh context, restricted tools, or parallel throughput. Multi-agent runs cost several
times the tokens of a single agent (Anthropic measured about 15× for research systems), so every
subagent must earn its cost.

## 2. Roles

| Role | Runs as | Owns | Never does |
|---|---|---|---|
| **Director** (you, main thread) | the session itself | Conversation with the user (subagents cannot ask questions), brief, art bible, architecture, gameplay code, integration, lighting/post/UI, game feel, final decisions | Grading its own work at a gate |
| **genre-art-researcher** | bounded opening subagent | Intent/genre/tone references and feasible visual/motion directions; writes `design/research.md` | Building assets, treating a genre label as a style or claiming uninspected media |
| **production-planner** | bounded opening subagent | Systems/dependencies, small slice, ownership and milestone evidence; writes `design/plan-draft.md` | Implementing code or finalizing research-dependent direction without the director |
| **asset-builder** | subagent, up to 3 in parallel | One asset (or a small kit) per brief: source/build → validate → render → self-check → deliver under `assets/<id>/` | Touching game code or other assets' folders |
| **animator** | subagent | Rigs, skin weights, clips, retargeting, pose strips; writes under `assets/<id>/` and `assets/anims/` | Gameplay code (it hands back clip names, lengths and events) |
| **art-critic** | subagent, read-only | Independent visual verdicts on assets and scenes against the art bible and scorecard | Editing anything; softening a failing score |
| **playtest-qa** | subagent, read-only | Runs the build, drives input, checks features, errors, performance counters and code hygiene | Editing anything; marking features as passing |

Use built-ins instead of adding agents:
- `Explore` for codebase searches.
- `/code-review` for diff correctness.
- `/simplify` for cleanup passes.

Subagent names:
- With the plugin installed: `game-studio:genre-art-researcher`, `game-studio:production-planner`,
  `game-studio:asset-builder`, `game-studio:animator`, `game-studio:art-critic`,
  `game-studio:playtest-qa`.
- When copied into a project's `.claude/agents/`: the plain names.
- If neither exists: spawn a general-purpose agent and paste the matching `agents/*.md` body into the brief.

## 3. When to spawn a subagent

Spawn one only if at least one of these is true:
- **(a) Verbose, isolated work.** Blender logs, mesh reports and dozens of renders would flood your
  context, and you only need the result.
- **(b) Independent judgment.** A fresh context that never saw your reasoning grades the work.
- **(c) Independent parallel units.** Separate assets with no shared files and no mid-task dependencies.
- **(d) Tool restriction.** A reviewer that cannot edit.

Stay in the main thread when:
- The task needs back-and-forth with the user.
- The steps share a lot of context (plan → implement → test of one feature).
- It's a quick, targeted edit.

Gameplay code is usually not parallelizable, because shared state means conflicts.

Scale to the task:
- New games or missing/invalidated plans start with the two opening roles and the reconciliation gate
  in `startup-planning.md`. Cache their reports; ordinary sessions resume instead of redoing research.
- A single prop fix needs no subagent.
- A batch of 6 independent props justifies 2–3 builders.
- Never spawn agents for simple lookups.

## 4. Delegation brief (copy, fill, send)

Subagents do not see this conversation or this skill. Everything they must know goes in the brief.
Pass paths, not pasted content.

```
OBJECTIVE: <one sentence: the outcome, not the method>
SKILL_DIR: <absolute path to this skill folder>   (scripts: SKILL_DIR/scripts, refs: SKILL_DIR/references)
READ FIRST: design/art-bible.md, design/budgets.json, <asset spec / feature ids>, <reference images>
OWNERSHIP: write ONLY under <dir>; do not touch <dirs>
ACCEPTANCE CRITERIA: <numbered, testable: numbers from budgets.json and the art bible>
EVIDENCE REQUIRED: <renders/captures/reports and their paths>. Say what you ran and what you saw; if
  you could not run something, say so explicitly.
OUTPUT: <files to write>; reply in ≤ 15 lines: status line first (DONE / BLOCKED / NEEDS-DECISION),
  then paths, measured numbers, open risks, questions for the user
LIMITS: at most <N> build-review iterations, then stop and report what blocks you.
  No paid services without explicit approval in this brief.
```

- Give the generator the same criteria the critic will use. Builders who know the rubric produce
  better first drafts.
- Avoid inflated wording. "Museum quality" made outputs converge on a single look; concrete criteria
  work better.

## 5. Parallel work

Opening research and planning can run in parallel because the planner leaves style-sensitive choices
explicitly unresolved. The director merges both into `design/plan.md` before production. Do not run
builders while the first usable slice/direction plan is still absent. Read-only audit and boot checks
can proceed meanwhile. The two opening agents consume two of the normal three slots.

- Run at most **3** subagents at once. More multiplies cost, and integration conflicts grow faster
  than throughput.
- Only one builder may mutate a shared live Blender scene. Use separate headless processes and
  files for parallel asset construction; folder ownership alone does not isolate a shared scene.
- Give each builder its own folder (`assets/<id>/`). Two agents never write the same file.
- Establish a known base revision before delegating. Verify each worktree's actual base and avoid
  shared-file edits; do not assume isolation settings or branch selection.
- While builders work, you build the greybox gameplay loop and the QA hook. Don't sit idle, and don't
  duplicate their work.
- A subagent that needs a decision returns `NEEDS-DECISION` with options. You ask the user, then resume
  or re-brief it.

## 6. Gate protocol

Gates sit at milestones, not at every edit:
- Asset acceptance.
- Vertical slice.
- Each content milestone.
- Release.

**Who:**
- `art-critic` judges anything visible.
- `playtest-qa` judges anything that runs.
- At milestone gates, both run in parallel on the same build revision.

**Input to critics:**
- Raw evidence: renders, captures, frame sequences, metrics, report JSON.
- The art bible, the scorecard (`templates/scorecard.md`) and `features.json`.
- Never your self-assessment or your explanation of why it's fine.

**Verdict format:**
- The first line is machine-readable: `ART-GATE: PASS|FAIL` or `QA-GATE: PASS|FAIL`.
- Then the scores per criterion, each with a cited evidence path.
- Then at most 10 ranked defects with concrete fixes.

**Thresholds are hard.** Any criterion below its threshold fails the gate, whatever the average.

**Calibration:**
- Critics anchor scores to the scorecard's anchor descriptions.
- Their stance: "Your job is to find how it breaks, not to confirm it works."
- A critic that finds an issue may not talk itself out of it. Severity is decided by the rubric, not
  by how much work the fix is.

**Avoid over-criticism:** only defects that break a requirement, the art bible or a threshold block a
gate. Mark everything else `optional` and don't chase it.

**Rounds:**
1. Fix.
2. Re-check only the failed criteria.
3. Allow at most **2 rounds** per gate, then escalate to the user with the evidence and the options.

Endless review loops burn budget and rarely converge.

**Human checkpoints:**
- Art direction choice, during pre-production.
- The vertical slice, with a proof video or a capture sheet.
- Taste is the user's call. Bring them evidence, not adjectives.

## 7. Cost controls

- Use `model: inherit` for judgment roles. Never downgrade the critic to a small model to save money:
  a lenient critic costs more in rework.
- Set `maxTurns` on every agent. Agents may not spawn agents.
- Returns are ≤ 15 lines. Artifacts go to files.
- Prototype previews may skip critic gates, but never run-and-look checks. This does not satisfy
  standard/premium asset acceptance or release; report deferred checks explicitly.
- Re-render only the views you changed. Use small render sizes (512–640 px) for iteration and larger
  ones only for final evidence.
- Paid generation needs a cost preflight and the user's OK. Never blind-retry a paid job.

## 8. Failure modes and countermeasures

| Failure | Countermeasure |
|---|---|
| Document bloat; the planning becomes the project | Only the state files in SKILL.md; each stays short and is kept current |
| Self-evaluation leniency ("looks great!") | Separate read-only critic, fresh context, hard thresholds, anchors |
| Critic finds a problem, then rationalizes it away | Verdict is decided by rubric thresholds; every score cites evidence |
| Critic always finds *something* → endless polishing | Only blocking-class defects block; ≤ 2 rounds; escalate |
| Same-model blind spots | Non-LLM evidence (inspect reports, validator, metrics, tests) + human checkpoints |
| Vague delegation → wrong or duplicated work | The brief template; one owner per folder |
| Subagent silently assumes a design decision | It returns `NEEDS-DECISION`; you ask the user |
| Premature "done" | `features.json` flips to `passes: true` only with evidence; final proof is reviewed before claiming done |
| Context loss after compaction | `progress.md` is read first; the standards sit at the top of SKILL.md |
| Too many agents / token blow-up | ≤ 3 concurrent, milestone gates, no nesting, short returns |
