# Art bible — <game title>

<!--
Written by the director in pre-production, using references/art-direction.md. Short, concrete, testable.
Every value here is something a builder can apply and a critic can check. Vague adjectives ("beautiful",
"AAA", "stunning") are not allowed; describe what the eye should see instead.
Status: draft | approved by user on YYYY-MM-DD
-->

## 1. Identity
- **One-line visual rule:** <e.g. "Sun-bleached frontier toys: chunky, warm, readable from far away">
- **Principles (2–3), each with a tie-breaker:** <e.g. "Readability over detail — when unsure, remove detail">
- **The one bold element:** <where this game spends its boldness: a signature light, a hero silhouette, one accent color>

## 2. Generic check (required)
| Section | First instinct (the default) | What we chose instead, from the subject | Why |
|---|---|---|---|
| Palette | | | |
| Lighting | | | |
| Shapes | | | |
| UI | | | |

## 3. Mood per game state
| State | Emotion | Light temperature / contrast | 3–5 descriptors |
|---|---|---|---|
| Explore | | | |
| Combat / danger | | | |
| Victory / reward | | | |
| Menu | | | |

## 4. Style
- **Rendering style:** <stylized low-poly flat/soft | toon | PBR realism> and why it fits this pipeline (art-direction.md §2)
- **Detail level by distance:** <what survives at gameplay distance; background lower than play space>

## 5. Color system
| Role | Hex | Used for | Never used for |
|---|---|---|---|
| Dominant environment | | | |
| Secondary environment | | | |
| Player / hero | | | |
| Threat | | | |
| Reward / interactable | | | |
| UI accent | | | |
| Shadow tint | | | |
- **Value key:** <high-key | low-key | full-range>; gameplay objects sit in the <brighter/darker> band than the background.
- **Saturation rule:** <where saturation is allowed>
- **Colorblind backups:** <shape/icon/sound cues for each semantic color>

## 6. Shape language and silhouettes
- Friendly / neutral / danger / structure shapes: <rounded | angular | orthogonal ...>
- One distinguishing silhouette trait per archetype: <player: ..., enemy A: ..., pickup: ...>
- Proportions: <e.g. characters 3.5 heads tall; doors 1.4× player height>

## 7. Environment language
- Architecture and materials of the world: <...>
- Prop density per area, rest areas, storytelling props: <...>
- Landmarks: macro <...>, meso <...>, micro <...>

## 8. Materials
| Class | Base color range | Roughness | Metalness | Variation / wear |
|---|---|---|---|---|
| | | | | |

## 9. Render recipe (exact values; mirrored in code config)
- Tone mapping: <Neutral | AgX | ACES>, exposure <1.0>
- Key light: color <hex>, intensity <n>, direction <...>; shadows <on/off, map size, normal bias, max distance>
- Fill: hemisphere sky <hex> / ground <hex>, intensity <n>
- IBL: <HDRI file or room environment>, intensity <n>
- Rim / practicals: <...>
- Fog: <type, color, near/far or density>
- Contact grounding: <blob shadows / vertex AO / contact material>
- Post: bloom <threshold/strength/radius>, grade <LUT file or adjustments>, vignette <n>, outlines <method or none>
- Pixel-ratio cap: <2>

## 10. Motion language
- Feel: <snappy | weighty | floaty>; player response < 100 ms
- Easing families and durations: <...>
- Juice tiers: small <...>, medium <...>, large <...> (animation.md §3)

## 11. UI / HUD
- Paradigm: <diegetic | spatial | overlay>
- Typeface(s): <name> because <reason from the subject>; minimum size <px>
- Icon style: <stroke weight, grid, abstraction level>
- HUD hierarchy: <status → objective → feedback → flavor>

## 12. Banned defaults and anti-references
- This game must NOT look like: <anti-references and why>
- Banned in this project (from anti-ai-look.md plus project-specific): <list>

## 13. Verification shots
| Shot | Camera / state | Checked for |
|---|---|---|
| gameplay | | |
| wide | | |
| hero | | |
| darkest area | | |
| busiest moment | | |
| UI over gameplay | | |
Each shot is captured in color, grayscale, silhouette and post-off variants.

## 14. Asset standards
- Style sheet values (bevel scale, shading, texel density, palette atlas): see design/assets.json `style_sheet`
- Budgets: design/budgets.json

## 15. References
| Reference | Take | Avoid |
|---|---|---|
| | | |
