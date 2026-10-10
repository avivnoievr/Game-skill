RESEARCH: PROVISIONAL

Intent and constraints
- Confirmed pitch: absurd comedic 3D growth/life simulator; begin as a baby, grow, and escalate from slapstick fighting to improbable guns/action. The user explicitly rejects automatically treating “life simulator” as realistic domestic simulation.
- Genre/core verbs: life-stage progression plus embodied comedy/action; proposed slice verbs are move, reach/grab, bonk, grow, aim/fire. These verbs are proposals, not confirmed mechanics.
- Emotional tone: surprise, physical farce and escalating incongruity. Familiar household rules make the improbable action legible; seriousness of violence remains undecided.
- Audience: assume players enjoy physical comedy and short action challenges; a baby protagonist does not establish a child audience or age rating.
- Realism needs: recognizable domestic objects, clear contact and cause/effect; anatomical accuracy, skin detail and realistic gun handling are unnecessary for this pitch.
- Evaluation assumptions only: Godot 4.6.3, desktop, third-person. The actual engine/platform/camera are unconfirmed; no existing game captures, asset audit, budget or art bible were supplied.
- Ownership: planning report only. No code, assets, generations, installations, purchases or external messages were produced.

Sources actually inspected — four primary references, all text
1. [Octodad: Dadliest Catch — Young Horses' Steam page](https://store.steampowered.com/app/224480/Octodad_Dadliest_Catch/) | Read the developer/publisher attribution, About This Game and Key Features text. The creator describes mundane tasks complicated by unwieldy tentacles and physics-based flailing. Inference: keep the household task understandable while the body creates the joke. Borrow this relationship, not its octopus identity or deliberately awkward controls.
2. [Human Fall Flat — developer/publisher Steam page](https://store.steampowered.com/app/477160/Human_Fall_Flat/) | Read About This Game, including its physics-platformer description, multiple routes and boulder/catapult/wall interaction example. Inference: a small number of large manipulable props can carry readable physical comedy; use recovery and contact as expressive moments. No locomotion, camera or art style was visually inspected.
3. [Katamari Damacy REROLL — Bandai Namco announcement](https://www.bandainamcoent.com/news/katamari-damacy-reroll-now-available) | Read the story and progression paragraph: objects range from a paperclip to a continent; progressively larger items serve a size goal. Inference: growth should change what the player can affect and how familiar landmarks feel, rather than merely raise a stat. This reference concerns object/scale progression, not human aging.
4. [Totally Accurate Battlegrounds — Landfall press kit](https://landfall.se/tabg-press-kit) | Read Description and Features: balloon crossbow, inflatable hammer, physics parkour and an escalating guns/action premise. This is a creator-described gameplay/motion reference, not observed footage. Inference: improbable weapons and physical comedy can coexist; preserve exaggerated prop and body language when action escalates. Do not borrow its battle-royale scope or first-person presentation.
- Supplemental same-reference text: [Bandai Namco's Katamari page](https://en.bandainamcoent.eu/katamari/katamari-damacy-reroll) describes a simple ball-rolling/object-collecting verb and absurd story. This is not a fifth independent reference.

Access and evidence limits
- https://octodad.com/ timed out in the read connector; its Steam page provided the accessible primary substitute.
- Human Fall Flat's linked About image (link 78) and header image (link 4) returned internal fetch errors. Bandai's linked announcement image (link 16) returned HTTP 404.
- Landfall's linked 1.png resolved to https://images.squarespace-cdn.com/content/v1/55dc59cae4b07dc2ebbe3ea3/1616590808719-N5OGD358Z1MXW2BMM8UU/1.png, but the connector returned only an image-display marker, no inspectable pixels. It supports no visual finding here.
- Two domain-filtered Steam image searches returned no results. No footage, GIF playback, screenshot pixels or transcripts were inspected. All visual recipes and timing below are prompt-derived design hypotheses informed by creator text.
- Shell networking is restricted/enforced through the session proxy; public text was read with the available read-only web connector. No proxy bypass, login or permission expansion was attempted.

Directions compared — recipes to test, not selected production art
1. Exaggerated domestic slapstick — recommended.
   Shape/proportions: infant has a broad head, short torso and mitt-like hands; later stages gain longer limbs and an overconfident chest while retaining the same hair tuft and distinctive costume motif. Use rounded, authored forms with large functional props; make a spoon, cushion and toaster recognizable in silhouette. Avoid faceted geometry as an automatic comedy style.
   Realism/materials: familiar household construction with deliberately exaggerated scale; soft shading, broad matte color areas, limited labels/seams and grounded contact shadows. Texture detail must survive the gameplay camera; no skin pores or pervasive grunge.
   Palette roles, provisional: slate-blue room #526778, muted ochre furniture #B59560, teal protagonist #3AA99A, coral threat #D65B4B, yellow interaction detail #EDC75A, deep plum contact/shadow #353146. Pair roles with shape/state cues; the room remains quieter than the body and active prop.
   Motion/comedy: responsive movement with authored waddles, broad reach poses, a short stumble after a bonk and exaggerated weapon recoil followed by an embarrassed settle. Keep full-body physics to recoverable impact moments; free ragdoll control is a hypothesis, not a requirement. Escalate the scale of the same gag instead of adding constant shake.
   HUD: one life-stage marker and current household objective; repeat the costume and interaction motifs in small icons. Show a temporary aim mark only when aiming. Let world scale communicate growth before HUD text.
   Future route: primitive blockout for scale/composition, then an editable authored character with stage-specific proportions/clips and separate moving prop parts; reuse a shared matte material kit. Godot staging is provisional until the engine and local tools are confirmed. Risk: “cute baby” proportions can weaken adult action or read as generic mascot art; the growth test must retain identity and change capability.
2. Cel-shaded action sitcom — feasible alternate if stronger action parody is desired.
   Shape/proportions: caricatured head and oversized hands/shoes, sharper shoulders with age, graphic household silhouettes; simplified realism, two broad lighting bands and sparse decals. Use the same world/hero/threat palette roles, with stronger value boundaries rather than more colors.
   Motion/HUD: strong anticipation and held comic reaction poses, quick firing response, restrained impact streaks; HUD uses a small chapter/age stamp and weapon silhouette. Future route: one shared toon shader plus authored rig/clips, with an outline added only after distance tests. Risk: outlines and fast pose changes can obscure hands, contacts and targets in a third-person view; reject if they make the slice harder to read or require disproportionate shader/rig work.

Recommendation
- Test exaggerated domestic slapstick first: bodily mismatch gives the baby stage a playable joke, fixed household landmarks make growth visible, and familiar props can evolve into improbable weapons without a new visual identity. This follows the pitch and the references' described relationships; it is not a claim that their observed visuals match this recipe.
- It should not resemble a photoreal domestic routine simulator, an interchangeable low-poly village, or a military shooter whose escalation loses the domestic joke. These are rejection criteria, not a prohibition on a later user-selected style.

Test slice: “Breakfast Promotion” — proposed 3–5 minute representative slice
- One room with a low bowl, spoon, cushion opponent, high cereal shelf and door as stable scale landmarks. Baby reaches and bonks; a milestone compresses progression into a later stage; longer reach opens the shelf interaction and a toaster-derived gun creates an absurd action beat against a clearly mechanical target. The compressed age change tests the language, not the full game's chronology or weapon policy.
- Keep one third-person camera relationship, then reframe height/distance across growth so hands, contact, target and next route remain visible. Test camera collision and close-wall views; do not assume a default FOV is correct.
- Compare both recipes using the same staging: can a viewer identify the life stage and protagonist without labels, recognize active props in silhouette at desktop gameplay distance, explain the new affordance after growth, and see contact/recovery while retaining control?
- Record active play and the growth/bonk/fire transitions before evaluating motion. Compare color, grayscale and post-off stills for hierarchy. A still cannot validate timing; no acceptance/art gate has passed in this planning test.
- Cheap first experiment: one stage-change character proxy plus spoon/cushion/toaster silhouettes in that room. Test authored growth changes against uniform whole-body scaling; reject the uniform scaling approach if it communicates only size rather than age and new capability.

Open decisions / not verified
- Confirm actual engine, desktop input target, camera, duration/budget, desired age range and the role of firearms in the final story. The slice's domestic task, costume motif, targets and compressed progression are proposals.
- Confirm whether deliberate awkward control is wanted; current recommendation preserves responsive input and puts the comic instability in pose/recovery. Body proportions, palette, cel shading, rig route and effect timings remain unvalidated.
- Read locally: design-loading.md; art-direction.md and anti-ai-look.md; animation.md; the named Ground/Process/Restraint, visual-scorecard Categories/Automatic failures, and game-feel opening/Tuning/Anti-Patterns/Determinism sections. Their examples informed restraint/readability criteria; no Three.js scaffold code or upstream default style was adopted.
