# Not looking AI-made: tells and fixes

The "AI look" is not one thing. It is the sum of defaults: values nobody chose. Each default
alone looks harmless. Together they produce the generic, slightly empty, evenly lit, over-glowing
scene that players recognize instantly. Telling a model "avoid a generic look" mostly swaps one
default for another. Naming the concrete patterns works, so here they are.

A banned default is still allowed when the art bible deliberately calls for it. The point is that
someone *chose* it.

## 1. World and rendering tells

| Tell | Why it reads as AI/programmer art | Fix |
|---|---|---|
| Default grey materials, or unlit flat `MeshBasicMaterial` colors everywhere | Nobody art-directed the surfaces | Palette-role materials, lit, with tonal and roughness variation |
| Three white lights plus grey ambient (`0x404040`), no environment map | The tutorial default | Warm key + cool sky fill + IBL + rim (`art-direction.md` §5) |
| Metals that render black or flat grey | No environment map to reflect | IBL / HDRI on every scene with metal or gloss |
| No tone mapping, or ACES washing out a stylized palette | Colors look either clipped or muddy | Choose deliberately; PBR Neutral for palette-driven styles |
| Rainbow palette: every object a new saturated hue | No palette roles | 5–7 roles; muted dominant colors; saturation only for gameplay signals |
| Bloom, glow, fog or darkness used as "the style" | Covers missing geometry | Forms first; bloom only on authored emissives (threshold ≈ 0.85) |
| Hero built from primitives (box + cylinders + glow); "families" that are recolored cubes | Placeholder geometry presented as final | Silhouette-first authored forms (`modeling.md`) |
| Objects floating, with no contact shadows | Nothing feels grounded | Contact/blob shadows, vertex AO, snap to ground, darker contact material |
| Perfect grids, uniform scale/rotation/spacing, mirror-symmetric layouts | Procedural placement with no design | Clusters, seeded jitter (±10–20%), density variation, rest areas |
| Mixed asset styles side by side | Asset-flip look | One style; unify with palette, bevel scale and shading; one global grade |
| High-frequency detail and noise everywhere | No hierarchy, so the eye has nowhere to rest | Calm areas; background detail lower than the play space |
| Empty world disguised by fog | Fog hiding absence | Layers (near/mid/far), landmarks, set dressing with purpose |
| Pure black shadows, pure white highlights | Default light setup, no grading | Cool, colored shadows; extremes reserved for focal points |
| Same camera height and angle for everything, default FOV | Camera never designed | Genre FOV, look-ahead, composed shots |

## 2. UI tells (the web-app look in a game)

Banned by default in game HUD and menus:
- Stat-card dashboards: rounded rectangles with a big number and a label.
- Cream or off-white panels; glassmorphism blur panels over everything.
- One-note purple-blue gradients, especially on buttons and title text.
- Pill-shaped buttons; generic system or default sans fonts (Inter, Roboto, Arial) with no
  personality.
- Emoji used as icons; mixed icon sets with different stroke weights.
- "01 / 02 / 03" step labels; italic accent words; monospace labels for non-numeric text.
- Center-everything layouts with no hierarchy; text where an icon or meter would read faster.

Instead:
- A HUD paradigm chosen on purpose (diegetic / spatial / overlay).
- A typeface that belongs to the game's world.
- Icons on one grid.
- Meters and markers before text.
- UI shapes and colors taken from the game's own motifs.

## 3. Motion tells

| Tell | Fix |
|---|---|
| Linear tweens on non-mechanical motion | Easing by intent (`animation.md` §2) |
| No anticipation, follow-through or settle | 12 principles adapted to games (`animation.md` §1) |
| `lerp(a, b, 0.1)` per frame (frame-rate dependent) | Half-life damper with dt |
| Random per-frame screenshake; shake on every footstep | Trauma model with smooth noise; importance tiers |
| Foot sliding; spinning on the spot | Speed-matched playback, clamp, foot lock (`animation.md` §5) |
| T-pose flashes on spawn or transition | Bind-pose check in QA; correct export of all actions |
| UI elements popping in with no transition | 150–300 ms eased transitions |

## 4. Process tells (how AI-made games get made)

| Tell | Fix |
|---|---|
| "Done" judged from the title screen or one still frame | Active-play shots, grayscale/silhouette/post-off variants, motion evidence |
| Polishing the post stack while the forms are placeholder | Order of work: forms → materials → lighting → post |
| Every asset a different source and style | The routing in `modeling.md` §2, and one style sheet |
| Adding more things to fix a weak scene | Remove one accessory; strengthen what exists |
| Generic choices nobody wrote down | The art bible's generic check: "would I write this for any similar game?" |

## 5. Five-minute self-test (before handing a scene to `art-critic`)

1. Grayscale shot: do the player, threats and interactables separate from the background?
2. Silhouette shot: can you name every gameplay object by its shape alone?
3. Post-off shot: does the scene still look designed without bloom or grading?
4. Squint at the gameplay shot: is there one focal point, and is it the right one?
5. Count hues in a frame: are there more than the palette allows?
6. Find three things that touch nothing (floating) or repeat in a perfect pattern.
7. Read the HUD: is anything in §2 present without an art-bible reason?
8. Does anything glow only to look "premium"?

Any "no" in 1–4, or any find in 5–8, gets fixed before review.
