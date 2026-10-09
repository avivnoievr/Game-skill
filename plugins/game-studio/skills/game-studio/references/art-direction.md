# Art direction: making it look intentional

Contents: 1. The method · 2. Choose one executable style · 3. Color and value · 4. Shape, silhouette, scale ·
5. Lighting recipe · 6. Post-processing with restraint · 7. Camera · 8. Environment composition ·
9. Materials · 10. UI / HUD · 11. Verification shots

Read `anti-ai-look.md` with this file. That one lists the specific tells; this one is the method.

## 1. The method (do these in order, in writing, before building)

1. **Ground it in the subject.** Write down the game's world, audience and the job the visuals must
   do (readability in fast combat? calm exploration?). Distinctive choices come from the subject's own
   materials, eras, crafts and vernacular, not from "game-like" generic choices.
2. **Write the art plan** with `templates/art-bible.md`: identity statement, palette roles, value
   key, shape language, render recipe, UI and motion language, and banned defaults.
3. **Run the generic check.** Ask of every section: "Would I write exactly this for any similar
   game?" Every yes is a default. Replace it with a choice derived from the subject, and note what
   changed and why. This is the single most effective step against the "AI look".
4. **Offer 2–3 directions to the user** (§2): short written descriptions plus palette swatches, or a
   quick blockout render of each. Taste is the user's call. Record the decision in `progress.md`.
5. **Spend boldness in one place.** Pick one memorable element: a hero silhouette, a signature light,
   or one accent color. Everything else stays quiet and supports it.
6. **Build in a fixed order: forms → materials → lighting → post/VFX.** Glow, fog, bloom and darkness
   never stand in for missing geometry. "If a shape only reads because it glows, the geometry is
   missing."
7. **Final passes refine; they don't add.** Before shipping a scene, remove one accessory. When the
   instinct is to add a new element, first make what's already there more of a piece.
8. **Look at it** through the verification shots (§11), and have `art-critic` judge it.

## 2. Choose ONE style an agent pipeline can actually execute

| Style | What it needs | Fit for an agent-built game |
|---|---|---|
| **Stylized low-poly, flat or soft shaded, palette-driven** (vertex colors or a small palette atlas) | Clean forms, a strict palette, good light | **Best default.** Geometry is procedural or from cohesive CC0 kits, no texture painting, coherence enforced by the palette, cheap to render |
| Toon / cel (ramp shading + outlines) | A global ramp, outline method and line weight | Good, if outlines and ramps are applied globally and consistently |
| Hand-painted look | Painted textures | Weak: agents can't paint textures consistently |
| PBR realism | Scanned/authored textures, consistent texel density, IBL, many assets | Only with a strong external asset source (CC0 scans, a paid library); expensive to keep consistent |

Stylization with a purpose beats detail. Team Fortress 2's art was designed around readability first.
**Never mix styles.** A cartoon pack next to realistic AI-generated assets is the most recognizable
amateur tell.

## 3. Color and value

- **5–7 palette roles with meaning,** written as hex values in the art bible: dominant
  environment, secondary environment, hero/player, threat, reward/interactable, UI accent, shadow
  tint.
  - Muted colors dominate. Saturation is reserved for small gameplay-relevant areas.
  - The 60/30/10 split is a reasonable starting ratio, an interior-design heuristic rather than a game
    rule.
- **Semantic colors are consistent everywhere.** Danger always reads one way, as do rewards and
  interactables. Back up color with shape or icon for colorblind players.
- **Value before hue.** Gameplay objects sit in a different brightness band than the background.
  Desaturate a screenshot: the player, threats and interactables must still separate. If everything
  becomes one flat grey, the values are too close.
- **Shadows shift cool and keep color; never pure black.** Saturation rises near the
  light/shadow edge. Keep the extremes (darkest darks, brightest lights) for focal points.
- **Read hierarchy.** Decide what must read first, second and third (for example: faction → role →
  weapon). Put the highest contrast where the eye should go, at the point of interest. To quiet a noisy
  design, remove small details or bring their values closer together.
- **Temperature per area** helps wayfinding: warmer, more saturated light toward goals, cooler and
  darker toward boundaries.
- **PBR albedo ranges:** non-metal base colors stay within about 30–240 sRGB per channel. Metals are
  bright (about 155–255) and colored by the metal itself.

## 4. Shape, silhouette, scale

- **Silhouette first.** Every gameplay role (player, each enemy type, pickups, hazards) must be
  identifiable as a filled black shape at gameplay distance. Test it with the silhouette render
  (`render_views.py` silhouette view, or the in-game silhouette shot).
- **Shape language with meaning:** rounded/organic for safe and friendly; angular for danger;
  orthogonal for authority, industry and structure. Give each archetype one distinguishing silhouette
  trait.
- **Interior details echo the silhouette.** Keep proportional angles consistent across a family of
  assets.
- **Families are designed, not recolored.** Recolored cubes and cones are one variant, not a family.
  A box with two cylinders and a glow is a placeholder.
- **Asymmetry and function:** hinges, vents, bolts, wear where hands touch. Detail goes where the
  camera looks.
- **Scale from one reference unit,** the player's height, plus familiar objects (doors 2.1 m, stairs
  0.18 m risers, railings 1 m). Break scale only on purpose, for emphasis.

## 5. Lighting recipe (record the exact values in the art bible's render recipe)

The default "three white lights plus grey ambient" setup is one of the most reliable tells of
programmer art, and popular agent skills still ship it. Use a designed stack instead:

1. **Key:** one dominant direction (the sun or a main light) that defines form. Warm for day, cool
   for night.
2. **Fill:** sky/hemisphere light in the complementary temperature (cool sky, warm ground bounce), so
   shadows keep color and gameplay stays legible.
3. **Image-based lighting (environment map):** mandatory for any metal, gloss or clearcoat. Without
   it, metals render black or flat grey. Use an HDRI (Poly Haven, CC0) or a generated room
   environment.
4. **Rim / back light** where the player and hazards must separate from the background.
5. **Practical / emissive lights** for authored signals: beacons, pickups, windows.
6. **Grounding:**
   - Real shadows only on the hero, major hazards and large anchors, with a tightly fitted shadow
     camera.
   - Blob or contact shadows for small props and hovering items.
   - Vertex-color AO on static props.
   - A darker contact material under important objects.
   - Prefer normal bias over constant bias against acne and peter-panning.
7. **Atmosphere:** distance and height fog tinted toward the sky color (aerial perspective) to
   create depth. Fog shows depth; it must never hide an empty world. Enable dithering if gradients
   band.

Engine code for this recipe: `engines/threejs.md`, `engines/godot.md`, `engines/unity.md`.

## 6. Post-processing with restraint

| Tone mapper | Character | Use for |
|---|---|---|
| **Khronos PBR Neutral** | Base colors in the 0.08–0.8 range come out almost exactly as authored (about −0.04), with no hue shifts; only highlights compress | **Palette-driven stylized games**, where authored hex colors must survive |
| AgX | Film-like, keeps hue well as colors brighten | Realistic or stylized scenes with strong lights |
| ACES (filmic) | High contrast; desaturates brights and cannot reach canary yellows or very bright greens/blues | Cinematic, moody, realistic |
| None / Linear | Clips highlights | Unlit flat styles and UI only |

- Tune exposure on **active gameplay**, never on the title screen.
- **Bloom** goes only on authored emissives. Threshold about 0.85; strength 0.35–0.6 and radius 0.2–0.4
  as three.js `UnrealBloomPass` starting values. In Godot, use glow with Soft Light blend (Additive
  is usually too strong).
- **One global color grade** (a LUT) unifies mixed sources better than per-asset tweaks.
- Keep vignette subtle and never let it darken the play path. Grain is low. Chromatic aberration only
  as a brief event. Prefer trails to motion blur.
- **Outlines:** pick one method for the whole game, or use rim light instead.
- Post order ends with the output/tone-mapping pass. Cap the pixel ratio before adding passes, since
  post cost scales with pixel count.
- **Always compare post-on vs post-off.** If the scene only works with post, the scene isn't done.

## 7. Camera

- **FOV defaults** differ by engine: three.js 50° vertical; Godot 75° vertical (≈ 107° horizontal at
  16:9). Convert with `vFov = 2·atan(tan(hFov/2) · H/W)`.
- Starting points:
  - first-person: about 90° horizontal;
  - third-person action: about 60–75° horizontal-equivalent;
  - top-down or isometric: narrow (30–45° vertical) or orthographic.
- **Follow behavior:**
  - a slight lag;
  - look-ahead in the movement or aim direction;
  - a deadzone for small movements;
  - collision handling so walls never cut between the camera and the player.
- **Smoothing must be frame-rate independent:** `x = lerp(x, target, 1 - exp(-ln2 · dt / halfLife))`.
  A fixed `lerp(x, target, 0.1)` per frame behaves differently at 30, 60 and 144 FPS.
- Shake is applied on top of the follow camera, never to the simulated body (`animation.md` §4).
- **Composition:** the player, the immediate threat or reward, and the route must stay visible.
  Check mobile aspect ratios separately when they're a target.

## 8. Environment composition and set dressing

- **Layers:**
  - play space;
  - near (speed and scale cues);
  - mid (the playable corridor);
  - far (depth, cheap);
  - sky.
- Keep the next decision readable through all of them. Background detail stays *lower* than the
  playable area.
- **Clusters, not grids.** Group props in varied-size clusters that share a material or color thread.
  Vary density between areas, and leave rest areas. Perfect rows and uniform spacing read as
  generated.
- **Break repetition** with seeded rotation, mirroring, ±10–20% scale jitter, 2–3 recolor variants,
  decals and vertex-paint variation. Only *the impression* of repetition is needed, not every
  instance.
- **Every prop has a purpose.** Ask who uses this space, and let props tell it (a camp has a cold
  fire, bedrolls, a cooking pot). "Barrels with no clear purpose" is a classic critique.
- **Landmarks** at three scales:
  - macro, for navigation from afar;
  - meso, for zone identity;
  - micro, for moment-to-moment interest.
- **Ground contact everywhere:** nothing floats, everything touches or casts a contact shadow.

## 9. Materials

- Separate material roles by roughness/metalness contrast, not hue alone.
- Starting values:
  - matte plastic roughness ≈ 0.6;
  - rubber ≈ 0.9 with low environment intensity;
  - brushed metal metallic 1, roughness ≈ 0.4.
- Add variation within surfaces (tonal ±10%, roughness variation, edge wear on convex edges).
  Perfectly uniform values read as CG.
- Emissive is for authored signals only, on a dark base so only the glow reads.
- Color textures are sRGB; data textures (normal, roughness, metalness, AO) are linear.
- Use advanced material features (clearcoat, transmission, sheen) only where they are visible in play.
- Wear, decals and trims imply scale and use. Reusing UI icon shapes as world decals ties the game
  together.

## 10. UI / HUD

- **Hierarchy:** survival/status → objective → feedback → flavor. Prefer meters, icons, rings and
  diegetic markers to text.
- **Pick one HUD paradigm on purpose:**
  - diegetic (in the world);
  - spatial (anchored in 3D);
  - overlay (screen space).
- **One typeface with personality** that fits the subject (plus at most one more for numbers), with
  a clear size hierarchy and a minimum size. Use tabular numerals for counters, in fixed-width slots
  so digits don't jitter.
- **Icons from one set or one grid:** same stroke weight, same abstraction level, "as if drawn by one
  person in one sitting".
- **Web-app defaults are banned in game UI** unless the art bible calls for them: stat-card
  dashboards, cream panels, pill buttons, one-note purple/blue gradients, emoji as icons, generic
  system fonts and "01/02/03" labels (full list in `anti-ai-look.md`).
- **Mechanics:**
  - respect safe areas;
  - touch targets ≥ 44 CSS px;
  - hover, focus, pressed and disabled states;
  - test with the longest strings and numbers;
  - the UI reads game state from one source of truth.
- **Motion durations:**
  - small reactions 100–200 ms;
  - panels and transitions 250–400 ms;
  - large scene transitions 450–600 ms.
- **Easings:**
  - standard `cubic-bezier(0.2, 0, 0, 1)`;
  - enter decelerate `(0, 0, 0, 1)`;
  - exit accelerate `(0.3, 0, 1, 1)`.
- **HUD reactions:**
  - score punch: scale 1.2 → 1 over about 120 ms;
  - full-screen flashes: only on major events, 90–120 ms.

## 11. Verification shots (define them in the art bible; used by every visual gate)

Fixed camera bookmarks, the same every time:
- gameplay camera, at rest and in action;
- wide establishing shot;
- hero close-up;
- darkest area;
- busiest moment;
- UI over gameplay.

Check four variants of each:
1. **Color:** the real look.
2. **Grayscale:** `capture.mjs` writes `*_gray.png` automatically. This tests the value structure.
3. **Silhouette:** gameplay-relevant objects flat black on a light background. This tests shape
   readability. Implement it as a `__QA__.shots` entry (`engines/threejs.md` §4).
4. **Post-off:** without the composer. This tests that forms, materials and lighting carry the scene
   without post.

The art bible's verification section names these shots, and `art-critic` scores them with
`templates/scorecard.md`.
