# Startup: research → reconciled plan → production

Run this once for a new game, an existing game without a usable direction/plan, or a material change
to genre, tone, core loop or platform. Resume from the saved research/plan for ordinary sessions and
small asset fixes. The two opening agents count toward the normal three-agent concurrency limit.

1. **Director prepares a brief snapshot.** Preserve the user's original pitch and record known
   engine/camera/platform, emotional tone, core loop, scope, tools and current project state. A short
   provisional brief is enough to start research; do not demand a finished art bible first.
2. **Start two independent agents in parallel.** `genre-art-researcher` owns `design/research.md`;
   `production-planner` owns `design/plan-draft.md`. Both receive the snapshot, actual project paths,
   `SKILL_DIR`, ownership and limits. The researcher checks references and intent. The planner audits
   dependencies and drafts the slice with explicit style-dependent placeholders. No production assets
   or new gameplay implementation yet; read-only audits and boot checks are useful meanwhile.
3. **Director reconciles them.** Select the direction using user preferences and inspected evidence;
   resolve the draft's style-sensitive choices. Write final `design/plan.md` from `templates/plan.md`.
   If useful, return one narrow follow-up to the planner; do not automatically rerun both agents.
4. **Pre-production gate.** Before building require a coherent tone/style rationale, one end-to-end
   slice, ordered dependencies, explicit owners, budgets, acceptance evidence and unresolved decisions.
   Confirm the representative art/animation route is executable. A missing report or an unexplained
   generic style means this gate is incomplete. Unsupported source access is labelled, never fabricated.
5. **Proceed under existing authorization.** Resolve necessary user choices; if independent reversible
   work was authorized, record provisional choices and start the first bounded milestone. Do not treat
   elapsed time as approval. Carry the final direction into the art bible and plan into `progress.md`.

The planner's parallel draft is not the final plan: it cannot silently precede or ignore research.
Changing the selected style updates only affected source/tool/budget decisions and dependent milestones.
This prevents both skipped planning and redundant research on every session.

**Example intent mapping:** an absurd growing-baby simulator has simulation mechanics but may have a
comic, exaggerated visual world. Research should compare plausible visual/motion treatments; planning
should account for growth states, changing ability/rig/animation needs, comedic escalation and a small
slice that proves those systems. Neither "simulator → photorealism" nor "comedy → low-poly" is enough.

Read the two role definitions in `SKILL_DIR/../../agents/`. No new model, MCP, browsing capability or
paid service is granted by defining these roles. Report unavailable research tools and missing engine
evidence explicitly.
