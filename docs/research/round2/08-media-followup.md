# Media follow-up: add evidence, not another large checklist

Access checked: **2026-10-10**. Scope: professional prop construction, silhouette/readability and animation staging. Read `05-videos.md` and its access ledger first: that round already reports 15 caption-based videos and explicitly says no frames were watched. Those historical caption claims were not independently re-downloaded here.

**Outcome:** the existing research is sufficient for silhouette-first work, reference boards, style consistency, screenshot critique and high-to-low baking. Keep those rules. Two small procedural additions are justified below; more inspirational media would add little to the runtime skill.

## Primary evidence ledger

| Source | Publication date | Access/evidence actually available in this pass | What it supports |
|---|---|---|---|
| [Grant Abbitt — 3 Vital Tips to Improve Low Poly Work](https://www.youtube.com/watch?v=xOIQzgg5ebs) | **2020-11-18**, verified in indexed YouTube metadata | Indexed creator/title/date/description readable. Direct page returned only YouTube footer; no fresh captions, audio or frames inspected. Existing round-2 caption notes are historical evidence, not a viewing claim here. | Creator description explicitly names varied references, silhouette and character details. All three are already represented in `art-direction.md` / `modeling.md`; no new rule needed. |
| [Blender Studio — Animation pipeline](https://studio.blender.org/tools/pipeline-overview/shot-production/animation) | Undated documentation; publication/update date not established | Indexed primary page text readable, including requirements, blocking, polishing and delivery sections. Direct open failed with **402 Payment Required**; current live page not confirmed. No video inspected. | Tested rigs precede animation; rough performance receives feedback before polish. Final pass checks contacts/intersections and asset synchronization. Adapt the staging principle to game clips rather than importing the studio's film delivery process. |
| [James Ray Cock / Poly Haven — Simple Prop Workflow](https://blog.polyhaven.com/simple-prop-workflow/) | **2022-07-15**, shown on the primary page | Primary article fully readable. Embedded images were not visually inspected. | References should include manufacture, assembly and material use; blockout emphasizes silhouette/proportion. Critique comes before expensive UV/baking. Checker textures expose stretching and inconsistent texel density; orient grain deliberately and compare materials under different lights. |

These are **three primary creator/official sources**, not three newly watched videos. A creator's descriptive metadata is weaker than a transcript, and a transcript is weaker than inspecting the visual demonstration. No source here proves that a particular agent-generated model looks professional.

## YouTube / Instagram access attempts

| Exact URL | Result | Consequence |
|---|---|---|
| https://www.youtube.com/@BlenderOfficial | Page title and footer only; account iframe present | Official channel was reachable as metadata, but its video contents were not available for review. |
| https://www.youtube.com/embed/zhktftWbumE?controls=1 | **Online fetch throttled** | This Snow animation-workflow embed was discovered through [a dated secondary syndication page](https://blender.fi/2022/05/05/snow-blender-character-animation-workflow/). That page contains descriptive text and chapter links; video authorship/publication date and visual demonstration were not independently verified. Do not treat its timestamps as fresh verified evidence. |
| https://www.instagram.com/blender.official/ | **Error fetching** | No readable public post/caption or frames. No post permalink established. |
| https://www.instagram.com/grantabbitt/ | **Error fetching** | No readable public post/caption or frames. No post permalink established. |
| https://www.instagram.com/polyhaven/ | **Error fetching** | No readable public post/caption or frames. No post permalink established. |

Targeted searches also sought public `/p/` and `/reel/` posts from the same creators; none yielded a verifiable relevant permalink. No login, cookies, scraper bypass, installation, paid generation or media download was used. This is a limitation of this research session, **not** a claim that Instagram is generally unusable. The accessible written primary material above is the fallback evidence. Stop repeated access attempts when they return the same limitation.

## Only justified changes to the runtime skill

### 1. Add a blocking checkpoint to `animation.md`

**Observed gap:** the file covers rig/export/engine/QA extensively but jumps from route selection to export concerns; it does not define a cheap motion-blocking review before polish.

**Proposed instruction (our adaptation of Blender Studio's pipeline):**

> Before splining, secondary motion or detailed polish, produce a short blocking preview of the clip's important poses and gameplay timing. The manager or art critic checks intent/readability, contact and transitions from the actual gameplay camera. Record the verdict; fix the largest defect first. Then polish and review the exported clip in motion. Reuse approved rigs and record the rig/asset revision.

Use an internal review when the user has delegated direction; do not create an approval stop for every clip. Existing animation QA already checks contacts and motion, so reference it instead of duplicating that list.

### 2. Make the UV visual check explicit in `modeling.md`

**Observed gap:** the UV section discusses projection/seams/map existence but does not instruct the agent to inspect a checker preview before committing to texture work.

**Proposed instruction (our adaptation of Poly Haven's prop workflow):**

> For image-textured assets, inspect a checker-material preview for stretched squares and inconsistent density before baking/texturing; orient directional materials deliberately. Save the review evidence. Palette/vertex-color assets need their own readability check instead. Compare finished materials under neutral and game lighting.

Do not universalize Poly Haven's no-overlap advice: deliberate mirrored/stacked UVs, trim sheets and palettes can be valid. Do not convert article examples or numerical lighting settings from earlier videos into universal quality limits.

## Existing rules to retain without expansion

- Native source assets and semantic parts must remain editable; joining/decimation is an optimization of an export copy, chosen only when it preserves the needed part/animation behavior. This follows the user's requirement and the existing part-contract work, **not a new demonstrated claim from these videos**. `modeling.md` currently says to join parts by material in its game-version step; qualify that line instead of adding another long paragraph.
- Silhouette/proportion review precedes fine detail. Existing blockout and art-direction instructions already cover this.
- Early critique prevents redoing costly downstream work. Existing modeling blockout review already provides the hook; no new mandatory external artist, social posting or extra agent is needed.
- An inspected gameplay capture is evidence of appearance; metadata, a numeric validator or a successful tool call is not. Existing QA protocol already states this distinction.

No third-party skill text was imported, and no new installation is proposed by this media follow-up. Keep full sources/access notes in research documentation; load only the relevant short procedural rule into the runtime skill.
