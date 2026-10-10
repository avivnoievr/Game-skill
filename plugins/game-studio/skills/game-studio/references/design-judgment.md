# Design judgment for 3D assets and games

Additive guidance: keep the existing workflow, scorecard and technical checks. Read this for a new
visual direction, substantial asset design or art review; reuse settled decisions for routine fixes.
This reference adapts selected frontend design methods to 3D. It supplies no tools or guaranteed taste.

## 1. Interpret the project before choosing a recipe

Record one sentence in the existing brief: subject, player feeling, audience, camera/distance and
the object's role. Separate these facts from an unsettled style recommendation. For an existing
game, retain successful visual choices and accepted assets before proposing changes.

The recipes in `art-direction.md` and tells in `anti-ai-look.md` provide starting points and diagnosis.
Low-poly, warm key/cool fill, colored shadows, wear, asymmetry, layout jitter and extra motion are
not universal definitions of quality. Choose them only when the brief, references and observed
result support them. A purposeful grid, immaculate surface, unlit graphic material or symmetrical
machine can be correct. Conversely, a written style excuse cannot justify unreadable required parts.
Record consequential exceptions before review, with their intended effect and a comparison that
tests it; keep technical, control and accessibility requirements intact.

## 2. Give even a single model a visual comparison

For standard/premium visual acceptance, open at least one relevant visual reference: a user-supplied
image, an accepted project asset or suitable creator/game imagery. A familiar object may also need
a construction reference. Record the URL/local path, the image or footage frame actually inspected,
the useful visible properties and what must not be copied. A text description is not visual evidence.
Reuse references across a coherent asset family; no fresh broad research for every prop.

Compare the current asset at its intended screen size and a useful close view. Match viewpoints
where practical and disclose lighting/camera differences. Compare shape relationships, hierarchy,
material treatment and tone rather than counting details. A cinematic promotional image is not
an honest gameplay-quality baseline. Reference use is analysis, not permission to copy protected assets.

If no reference can be inspected, continue authorized exploration with labelled assumptions and
report visual comparison `NOT VERIFIED`. Technical results may still be reported separately; the
missing required comparison cannot pass standard/premium art acceptance or establish professional quality.

## 3. Make thought visible through decisions and checkpoints

Before substantial visual work, add a few lines to the existing brief or progress note:

- The specific player-visible problem and what already works and should remain.
- The chosen form/material/motion decision, why it serves this subject, and one plausible alternative
  when the choice is consequential or unsettled. Routine repairs need no alternative-design exercise.
- The observed reference property supporting it, the main uncertainty and a cheap way to test it.
- What would show the choice failed, in the actual camera and relevant action state.

Use these as an executable design commitment, not a long essay. Review the outcome even if it
contradicts the commitment; do not invent a new rationale after seeing the output just to approve it.

Check primary form before expensive texture work: open a blockout/silhouette at the intended distance,
compare proportions and readable role, then fix the dominant discrepancy. For a new hero identity
with an unresolved shape, compare two cheap shape candidates; a settled style or small fix needs one.
Keep a defining primary feature, supporting secondary forms and restrained tertiary detail. Repeated
motifs can create a family; every prop does not need arbitrary novelty. Neither smooth bevels nor
more polygons repair a weak design.

## 4. Test the visual purpose of polish

Try removing or quieting one nonfunctional decorative layer in a reversible comparison: glow,
scratch noise, tiny greebles, excessive roughness variation or repeated HUD ornament. Keep the change
only if it improves the intended hierarchy or feeling. Do not remove required controls, collision,
information or defining features in the name of minimalism. An intentionally rich style may keep detail.

For textures, compare a neutral/material view and the intended game view. Check that pattern scale,
grain direction, seams and contrast support the primary forms. Do not add dirt or noise to improve
image metrics. An intentionally flat style does not owe a PBR surface treatment.

For motion, state its purpose and how often the player sees it. Inspect normal-speed action first,
then slow/frame-stepped motion to diagnose contact, timing and transitions. Test rapid retrigger,
interruption and changed state without hiding input feedback. Frequent cosmetic motion can become
tiring; tune or remove it when it competes with play. Frontend rules banning keyboard animation,
requiring CSS properties or prescribing sub-300-ms timing do not apply to character/world animation.
Use engine, animation and reduced-motion contracts for the actual effect.

## 5. Keep aesthetic judgment independent of technical success

The critic first opens raw output and references and records a short observation of hierarchy,
specificity and emotional fit. Read automated flags and technical reports only after this first
observation; then reconcile them with actual evidence. The critic may know the brief and budgets,
but a claimed quality label or a clean inspection is not a visual verdict. One independent critic
is enough for this pass; no extra standing agents or duplicate detector run are required.

Report separately: technical/control evidence, reference comparison, project-specific visual
strengths and the largest visible mismatch. Cite the exact view/region, the criterion it fails and
one concrete remedy. Say what is worth preserving. Preferences outside the brief are optional;
do not invent defects, lower a standard for effort spent, or hide a visible problem in an average.

Apply `templates/scorecard.md` to the relevant asset/genre. Its scores are reviewer judgments,
not statistical probabilities, a validated aesthetic detector or proof of human approval. Coherence
alone does not demonstrate distinctive professional art. If a consequential aesthetic choice remains
unresolved, record the disagreement/uncertainty; use existing user preferences or present concrete
alternatives when necessary. A fresh agent reduces shared context, not shared model limitations.

Prototype completion proves only its declared prototype scope. If the purpose of a test is design
taste or final model appearance, use standard/premium visual review even when the deliverable is a
single model. Preserve the distinction between a valid editable export and visually accepted work.

## Source and adaptation notice

Changed/adapted for Game Studio on 2026-10-10: selected concepts from Impeccable critique/distill
(Copyright 2025 Paul Bakaus, Apache-2.0), Taste Skill (Copyright 2026 Leonxlnx, MIT), UI UX Pro Max
(Copyright 2024 Next Level Builder, MIT), and Emil Kowalski's design-engineering/motion review
(Copyright 2026 Emil Kowalski, MIT). Wording and 3D contracts were rewritten; this is not any
upstream skill's unmodified entry point. This adapted file is distributed under Apache-2.0;
the source MIT permission notices are retained with the component licenses.

Exact pins, sections and unchanged license/NOTICE copies are in
[`../vendor/design-judgment-sources/sources.json`](../vendor/design-judgment-sources/sources.json)
and [`../THIRD_PARTY_NOTICES.md`](../THIRD_PARTY_NOTICES.md). Valve's
[TF2 paper, sections 3–4](https://cdn.fastly.steamstatic.com/apps/valve/2007/NPAR07_IllustrativeRenderingInTeamFortress2.pdf)
and Riot's [Clarity in League](https://www.leagueoflegends.com/en-us/news/dev/clarity-in-league/)
inform the primary-feature and gameplay-hierarchy guidance; their text/assets are not redistributed.
