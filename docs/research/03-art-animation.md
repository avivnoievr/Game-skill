# 03 — Art direction, non-AI look & animation (Research Agent 3)

Date: 2026-10-09. Scope: encoding design taste, 3D art direction rules, "AI/programmer-art" tells → fixes,
lighting/post recipes, animation quality, game feel, animation QA.

Evidence tags used below: **[src: X]** = I opened X (file, page or code) myself. **[secondary]** = only seen
through a WebSearch summary, original page not opened. **[judgment]** = my synthesis or starting value, not from a
source. **[UNVERIFIED]** = could not confirm.

Environment note: most article hosts were blocked or unreachable from this session. That includes threejs.org, docs.godotengine.org,
docs.blender.org, khronos.org, wikipedia, gamedeveloper.com, gdcvault, youtube, itch.io, gamedev.net,
polycount, bugnet.io, leadwerks and eiserloh.net. I worked around it with GitHub clones, raw.githubusercontent
(three.js source, godot-docs .rst, godot class XML, glTF-Blender-IO docs, Material Components docs) and a few hosts that
did answer: Valve's steamstatic PDFs, theorangeduck.com, modelviewer.dev, 80.lv, lizengland.com and blog.chosenconcept.dev.

---

## 1. Executive summary

1. **The strongest anti-"AI-look" mechanism is Anthropic's `frontend-design` skill, and it ports to 3D.** It works in five steps:
   (a) write an explicit token plan (palette, type, layout, principles) before any code;
   (b) review that plan against "what would I produce for any similar brief?" and revise whatever is generic;
   (c) work from a named list of current AI-default clusters;
   (d) "spend your boldness in one place";
   (e) critique your own screenshots and "remove one accessory".
   [src: anthropics/skills frontend-design SKILL.md, Apache-2.0]
2. **`majidmanzarpour/threejs-game-skills` is the best existing 3D art-quality skill set I found.** Its rules include
   "Glow does not make primitives look AAA. Build authored forms first, then materials, then lighting, then effects."
   It also has a 10-category visual scorecard with image anchors, "automatic failures", and canvas metrics.
   I recommend borrowing heavily from it, with credit (MIT, about 2.5k stars).
3. **Valve's TF2 papers are the best primary source for teachable stylized art direction:**
   - a read hierarchy (team → class → weapon);
   - shadows go cool, not black;
   - rim highlights instead of outlines;
   - muted colors dominate, with small saturated areas;
   - minimal repetition and visual noise;
   - characters validated as pure silhouettes;
   - backgrounds deliberately less detailed.
   [src: GDC2008 deck + SIGGRAPH07 course notes]
4. **Default lighting is a measurable tell, and popular agent skills spread it.** `cloudai-x/threejs-skills`
   "Three-Point Lighting" uses three white DirectionalLights plus `AmbientLight(0x404040)`. Its animation snippet still uses
   `THREE.Clock`, which is deprecated since r183. [src: repo + three.js Clock.js]
   The fix is a warm key, a cool sky/hemisphere fill, IBL, tone mapping and contact grounding.
5. **Tone mapping choice matters for stylized palettes.** Per the Khronos PBR Neutral write-up, ACES (and, to a lesser
   degree, AgX) cannot reach canary yellow or bright greens and blues; Lalish's write-up says this. Khronos PBR Neutral reproduces base colors 0.08–0.8
   exactly (minus 0.04) with no hue shifts. The three.js `webgl_tonemapping` example now defaults to Neutral.
   [src: KhronosGroup/ToneMapping README; modelviewer.dev write-up; three.js source]
6. **The art bible template should merge Donchitos' 9-section art bible with additions this project needs:**
   a render recipe, motion language, banned defaults, and verification shots. A review gate checks
   completeness and internal consistency (§3.2).
7. **Game-feel numbers with real sources:**
   - Swink: under 100 ms response correction cycle;
   - trauma shake: shake = trauma², decaying;
   - hitstop: 40–90 ms at 0.05 time scale, with feedback driven on real delta;
   - volume-preserving squash: other axes at 1/√s;
   - juice checklists from Juicy Breakout (source code) and two independent note sets of "The Art of Screenshake".
8. **Frame-rate independence is a top animation and camera bug.** `lerp(x, target, 0.1)` per frame is wrong. Use Holden's half-life damper
   `lerp(x, g, 1 - 2^(-dt/halflife))` or `exp(-k·dt)`. [src: theorangeduck.com spring-roll-call]
9. **Foot sliding is a speed mismatch between the simulation object and the clip.**
   - Holden frames the fix space as synchronize, adjust, clamp, then foot-lock with IK.
   - Turning rotation responsiveness too high causes on-the-spot spinning.
   - Research metrics give numeric thresholds for an automated check, e.g. a foot that slides more than 2.5 cm while under 5 cm high.
   [src: Holden; thresholds secondary]
10. **Blender → glTF animation export has silent-loss traps.** Actions not active or stashed on NLA tracks are not exported.
    Each action needs its own track. Blender 4.4 slotted actions changed how tracks merge. You need "reset pose bones between
    actions" and always-on sampling. [src: glTF-Blender-IO docs]
11. **Engine primitives for procedural secondary motion now exist natively in Godot:** SpringBoneSimulator3D,
    LookAtModifier3D and RetargetModifier3D (4.4+), and TwoBoneIK3D (4.6). SkeletonIK3D is deprecated.
    three.js has CCDIKSolver and `AnimationUtils.makeClipAdditive`. [src: godot doc/classes XML per branch; three.js source]
12. **Most community "art director" skills are thin.**
    - AlterLab: a persona plus PureRef-style human process.
    - ag-kit `game-art`: 2D-centric tables.
    - Donchitos: approval-gated process with little taste content.
    - Agents cannot see without screenshots, so the skill must force capture-and-critique loops with fixed shots.

---

## 2. Catalog

| Name | URL | Type | Stars / last update | License | Verdict | What exactly to borrow |
|---|---|---|---|---|---|---|
| frontend-design (Anthropic) | github.com/anthropics/skills/tree/main/skills/frontend-design | skill | repo HEAD 2026-10-09 | Apache-2.0 | 5 | Plan→"generic check"→build→critique loop; named default-clusters list; "boldness in one place"; "remove one accessory"; screenshot self-critique |
| canvas-design (Anthropic) | …/skills/canvas-design | skill | same | Apache-2.0 | 3 | Philosophy-first two-step; final pass "refine, don't add new elements". Its "repeat craftsmanship phrases" trick is untested and I would not copy it |
| algorithmic-art / theme-factory / brand-guidelines | …/skills/* | skill | same | Apache-2.0 | 2 | Seeded reproducibility (algorithmic-art). theme-factory is just named palettes (4 hex + fonts); thin |
| threejs-game-skills (majidmanzarpour) | github.com/majidmanzarpour/threejs-game-skills | skill set (9 skills) | ~2.5k★, last commit 2026-09-27 | MIT | 5 | `threejs-aaa-graphics-builder` (order of work, scorecard, auto-failures, metrics); `authoring-recipes.md`; `shader-cookbook.md` (PBR presets, bloom 0.35–0.6/0.2–0.4/0.85); `game-feel.md` (trauma, hitstop, squash, FOV punch, tuning table); `threejs-game-ui-designer` banned web defaults |
| Claude-Code-Game-Studios (Donchitos) | github.com/Donchitos/Claude-Code-Game-Studios | plugin / subagent set | ~26.0k★, 2026-10-08 | MIT | 3 | `docs/templates/art-bible.md` 9-section outline; AD-ART-BIBLE / AD-VISUAL gate prompts; batching sections 2–4 in one delegation. Process-heavy, little taste |
| AlterLab_GameForge game-art-director | github.com/AlterLab-IEU/AlterLab_GameForge | skill (persona) | 2026-03-30 | MIT | 2 | Silhouette-at-distance test, macro/meso/micro landmarks, value structure (high/low/full key), asset-review template. Persona fluff and human-studio process |
| ag-kit game-art (vudovn) | github.com/vudovn/ag-kit | skill | 2026-08-31 | MIT | 1 | Nothing beyond basics; 2D frame-count tables |
| cloudai-x/threejs-skills | github.com/cloudai-x/threejs-skills | skills (API ref) | 2026-01-20; ~2.8k★ per listing [UNVERIFIED] | MIT (README) | 2 | API reference only. Its lighting presets are the generic default (counter-example). Deprecated Clock |
| awesome-gamedev-agent-skills | github.com/gamedev-skills/awesome-gamedev-agent-skills | 75 skills | ~1.4k★, 2026-10-09 | Apache-2.0 | 4 | `game-feel` (feedback tiers, pitfalls), `camera-systems` (frame-rate-independent follow), `threejs-materials-lighting` (r186-pinned pitfalls). Says "Godot 4.7" [UNVERIFIED version] |
| Juicy Breakout | github.com/grapefrukt/juicy-breakout | code for "Juice it or lose it" talk | 2012 | zlib | 4 | `Settings.as`: the full toggle list of juice effects, with ranges |
| Khronos PBR Neutral | github.com/KhronosGroup/ToneMapping | spec | 2024 | CC-BY-4.0 | 5 | When to use Neutral; math; 1:1 range |
| three.js (r186, npm 0.186.1, 2026-09-24) | github.com/mrdoob/three.js | engine source | — | MIT | 5 | Tonemapping chunk (Linear/Reinhard/Cineon/ACES/AgX/Neutral); `crossFadeTo(…, warp)`; `mixer.setTime`; hemisphere example values; CCDIKSolver; LUTPass, OutlinePass, GTAOPass, SMAAPass, OutputPass; `material.dithering` |
| godot-docs + godot class XML | github.com/godotengine/godot-docs, godot/doc/classes | docs | master | CC-BY-3.0 [UNVERIFIED] | 5 | Tonemap modes, White 6–8, glow threshold, SSAO cautions, fog/aerial perspective, LUT 33³, shadow normal-bias rule, AnimationTree xfade/sync/advance-expression, skeleton modifiers |
| Valve TF2 illustrative rendering | cdn.fastly.steamstatic.com/apps/valve/2008/GDC2008_StylizationWithAPurpose_TF2.pdf ; advances.realtimerendering.com/s2007/… | papers / slides | 2007–2008 (old but timeless) | © Valve, paraphrase only | 5 | Read hierarchy, Leyendecker rules, team shape/material/hue contrast, repetition minimization, paint-over process |
| Daniel Holden articles | theorangeduck.com/page/spring-roll-call, /code-vs-data-driven-displacement, /dead-blending | articles + code | 2021–2023 | none stated (paraphrase); Spring-It-On repo | 5 | Exact dampers/springs, displacement sync/adjust/clamp, foot locking, dead blending |
| Lalish "PBR Neutral" write-up | modelviewer.dev/examples/tone-mapping | article | 2024 | — | 4 | ACES/AgX saturation loss explained |
| glTF-Blender-IO docs | github.com/KhronosGroup/glTF-Blender-IO docs/blender_docs/scene_gltf2.rst | docs | main | Apache-2.0 [UNVERIFIED for docs] | 5 | Animation export modes and traps |
| Material Components Android Motion.md | github.com/material-components/material-components-android | docs | master | Apache-2.0 [UNVERIFIED] | 4 | Duration tokens 50–1000 ms; easing cubic-beziers |
| Xavier Coelho-Kostolny thread (80.lv transcript) | 80.lv/articles/comparing-team-fortress-2-and-overwatch-art-direction | opinion article | — | — | 3 | Value hierarchy, restricted palette, "eliminate small details or bring their values closer" |
| Liz England review of Swink *Game Feel* | lizengland.com/blog/review-game-feel-by-steve-swink/ | review | 2015 | — | 3 | <100 ms correction-cycle definition |
| ShotgunTom notes / DK Liao blog | github.com/mingrui/ShotgunTom ; blog.chosenconcept.dev/posts/2022/11/0012-the-art-of-screenshake/ | fan notes | 2022 / older | — | 3 | 31-step "Art of Screenshake" list (two independent notes agree) |
| mixamo-mcp | github.com/V1xel/mixamo-mcp | MCP (Playwright browser automation) | 4★, date unknown | not stated | 1 | Shows Mixamo has no API; scripted browser use only. ToS not addressed. Avoid |
| npm libs | registry.npmjs.org | libs | see note | see note | — | gsap 3.15.0 ("Standard no-charge license", not OSI); @tweenjs/tween.js 25.0.0 MIT (2024-07); motion 14.0.0 MIT; @theatre/core 0.7.2 Apache (2024-05, stale); postprocessing 6.39.5 Zlib; n8ao 2.0.1 ISC; @pixiv/three-vrm 3.5.5 MIT (spring bones); camera-controls 3.1.2 MIT |
| wayline.io blog | wayline.io/blog/asset-pack-visual-identity | content-marketing blog (affiliate links) | 2025-08 | — | 1 | Only the generic "asset-flip = inconsistency" list; low evidential weight |

---

## 3. Distilled guidance

### 3.1 Taste-enforcement mechanisms (adapted from frontend-design / canvas-design / threejs-aaa)

1. **Ground it in the subject.** Name the game's subject, audience and the "primary job" of the visuals.
   Distinctive choices come from the subject's world, materials and vernacular. [src: frontend-design]
2. **Write the art plan before code:** palette as 5–7 named hex roles, value key, shape language, render recipe,
   UI type and motion. [frontend-design tokens; Donchitos §4]
3. **Run a generic-check pass.** Ask: "would I produce this plan for any similar game?" Revise every default part,
   and write down what changed and why. [src: frontend-design]
4. **Ban named defaults (3D version, §4 table).** The brief's own words always win; a banned default is allowed when asked for.
   [src: frontend-design principle]
5. **Boldness in one place.** One memorable element: a hero silhouette, a signature light, or a color accent.
   Everything else stays quiet. "Remove one accessory" before shipping. [src: frontend-design]
6. **Fixed order of work:** authored forms → materials → lighting → post/VFX. Glow, fog, bloom and darkness must never stand in
   for missing geometry. [src: threejs-aaa]
7. **Final pass refines, it does not add.** "If the instinct is to … draw a new shape, STOP and ask how to make what's
   already here more of a piece." [src: canvas-design]
8. **Critique screenshots against a scorecard with anchors.** Score active play, never title screens. See §3.11 for the categories.
   [src: threejs-aaa visual-scorecard.md]
9. **Keep a notes file of what was tried.** frontend-design: "if you have a space to jot down notes about what
   you've tried, it can help."

### 3.2 Art-bible template outline (for the skill's art-director agent)

Merged from Donchitos `art-bible.md` and AlterLab `templates/art-bible.md`; sections 10–13 are additions [judgment].

1. **Visual identity statement:** a one-line rule plus 2–3 principles, each with a design test ("when X is ambiguous,
   choose Y"). [Donchitos]
2. **Mood per game state** (explore / combat / victory / defeat / menu): emotion, light temperature, contrast, 3–5
   descriptors, energy. Every state must look distinct. [Donchitos]
3. **Shape language:** safe/organic vs danger/angular vs authority/orthogonal; hero vs supporting shapes; UI shape
   grammar; one distinguishing silhouette trait per archetype. [Donchitos, AlterLab, TF2]
4. **Color system:**
   - 5–7 palette roles with meaning;
   - semantic colors (danger, reward, interactable);
   - per-area temperature;
   - where the UI palette diverges;
   - colorblind backups (shape, icon or sound). [Donchitos]
5. **Value structure:** high-key, low-key or full-range. Gameplay objects sit in a different brightness band than the background.
   [AlterLab; TF2]
6. **Character direction:** proportions (e.g. "3.5 heads"), friend/foe/NPC distinction at a glance, pose style,
   detail that survives at camera distance. [AlterLab, Donchitos]
7. **Environment language:** architecture, texture philosophy (flat/vertex color vs painted vs PBR, with the reason), prop density
   per area, storytelling props, landmarks (macro/meso/micro). [Donchitos, AlterLab]
8. **Materials:** roughness/metalness per material class, albedo ranges, wear rules. [AlterLab]
9. **UI/HUD direction:**
   - diegetic vs screen-space;
   - typeface personality;
   - size hierarchy and minimum size;
   - icon style (stroke, grid);
   - UI motion feel. [Donchitos, AlterLab]
10. **Render recipe (code constants):**
    - tone mapper and exposure;
    - sun/sky colors and intensities;
    - shadow settings;
    - IBL;
    - fog;
    - post stack with values;
    - DPR cap. [judgment]
11. **Motion language:** easing families, durations, juice tiers (small/medium/large), animation style
    (snappy vs weighty). [judgment]
12. **Banned defaults and anti-references:** what this game must not look like. [AlterLab "anti-references"; frontend-design]
13. **Verification shots:** fixed camera bookmarks for color, grayscale, silhouette (black) and post-off versions,
    on desktop and mobile. [judgment]
14. **Asset standards:** formats, naming, budgets. This is Agent 2's area; link to it.
15. **References (3–5):** what to take from each and what to avoid, so the result does not read as a copy. [Donchitos]

Review gate prompt [paraphrased from Donchitos AD-ART-BIBLE]:
- Does the color system match the mood targets?
- Does the shape language follow from the identity statement?
- Can the standards be met on the target platform?
- Do sections contradict each other?
- Could an outside team build assets from this alone?

Verdict: APPROVE, CONCERNS or REJECT.

### 3.3 Choosing ONE executable style [judgment, supported where noted]

The default recommendation for an LLM-built pipeline is **stylized low-poly / flat-or-soft-shaded, with palette-driven
vertex colors or a small palette texture**, optionally toon/cel via `MeshToonMaterial` and a gradient map.

Why:
- the geometry can be built procedurally or composed from curated CC0 kits;
- no hand texture painting is needed;
- coherence is enforced by the palette;
- performance is cheap.

PBR realism needs scanned or authored textures and consistent texel density that an agent cannot paint. The low-poly
direction is backed by ag-kit's matrix ("Low-poly: fast, indie 3D"), which I rate as weak evidence. TF2 shows that stylization
"with a purpose" (readability) beats detail [src: TF2].

Choose toon/painterly only when outlines and ramps can be applied globally and consistently. Never mix styles: mixed packs are
the main asset-flip tell [secondary: wayline/bugnet].

### 3.4 Color rules

- **Restricted palette shared by characters, props and environment.** "Muted colors dominating and small areas of saturation."
  Secondary and tertiary complementary accents only on small props. [src: TF2 notes]
  The 60/30/10 split is an interior-design heuristic. It is fine as a starting ratio, but I found no game-art source for it
  [UNVERIFIED as game rule].
- **Shadows shift cool, not to black.** Saturation rises at the terminator, and extreme lights/darks are reserved for highlights
  and edges. [src: TF2 deck, Leyendecker conventions]
- **Value hierarchy before hue.** In TF2: team = color; class = silhouette, proportions, weapon; weapon = "highest contrast
  at chest level", with a gradient from dark feet to light chest. [src: TF2 deck]
  Fix noisy designs: "Eliminate the small details, or bring their values closer together." [src: 80.lv / Coelho-Kostolny,
  opinion]
- **Grayscale test.** Desaturate the screenshot. Player, threats and interactables must separate from the background. If everything
  turns into one flat grey, the values are too close. [secondary: several articles]
- **Squint test** for a single focal point [secondary; a heuristic from community skill files and artist interviews].
- **Team or faction contrast through several channels at once:** hue, material and shape.
  Example: red = warm, natural, angular; blue = cool, industrial, orthogonal. [src: TF2 notes]
- **Albedo ranges (PBR):**
  - no dielectric base color below about 30–50 sRGB or above about 240 sRGB, per channel;
  - metals about 155/180–255.
  [secondary: forum posts citing the Substance PBR guide; the validator may be stricter]
- **Wayfinding:** warm and saturated light toward goals, cooler and darker at the boundaries. [AlterLab opinion]

### 3.5 Shape, silhouette, scale

- **Silhouette first.** Every gameplay role must be identifiable as a filled black shape at gameplay distance.
  TF2 validated its classes this way during concept. [src: TF2 notes; threejs-aaa "silhouette first"]
- **Interior details echo the silhouette.** Keep proportional angles consistent across the cast; Xavier's example is the
  nose-to-forehead angle. [src: TF2; 80.lv]
- **Avoid "overly complex or geometrically off-kilter" modeling and keep repetitive structures to a minimum.**
  "Conveying the impression of repetition is more important than representing every detail." [src: TF2 notes]
- **Asymmetry and functional parts** (hinges, vents, bolts); detail goes where the camera looks; named child meshes;
  a separate collision proxy. [src: threejs-aaa authoring-recipes]
- **"Recolored cubes and cones are one variant, not a family."** "A box with two cylinders and a glow is a placeholder."
  [src: threejs-aaa]
- **Scale:** use one reference unit (player height) and familiar objects (doors, stairs) to fix scale. Break scale
  deliberately only for emphasis. [AlterLab; judgment]

### 3.6 Lighting recipes (three.js r155+ physical units; Godot equivalents noted)

- **Stack:**
  - key: one dominant direction, defines form;
  - fill: hemisphere/sky, keeps gameplay legible;
  - rim/back: separates player and hazards from the background;
  - practical/emissive: beacons, pickups;
  - contact grounding.
  [src: threejs-aaa authoring-recipes]
- **Outdoor starting point:**
  - `HemisphereLight` intensity 2, sky color HSL(0.6, 1, 0.6) (light blue), ground HSL(0.095, 1, 0.75) (warm);
  - `DirectionalLight` intensity 3, color HSL(0.1, 1, 0.95) (warm white);
  - shadow map 2048², `shadow.bias = -0.0001`;
  - fog matched to the background.
  [src: three.js `webgl_lights_hemisphere.html`]
  Another source puts the key light at about 1–3 in r155+ ("old tutorial intensities are too dark")
  [src: awesome-gamedev threejs-materials-lighting].
  Tune toward the palette: warm key with cool fill, or the reverse for night [judgment].
- **IBL is mandatory for any metal, gloss or clearcoat.**
  `scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture`, with `scene.environmentIntensity` about 1.0.
  "Metals and glossy dielectrics read as flat gray without an environment map." [src: threejs-aaa shader-cookbook]
- **Shadows:**
  - real shadows only on the hero, major hazards and large anchors;
  - fit the orthographic shadow camera tightly;
  - blob or contact planes for small and hovering items;
  - prefer **normal bias over bias** (less peter-panning) [src: Godot lights_and_shadows.rst];
  - set shadow max distance as low as the scene allows, for both quality and performance [src: Godot];
  - sun angular size 0.5° for PCSS contact-hardening, which is expensive, so use it on few lights [src: Godot].
- **AO:** SSAO only darkens *ambient* light. "Remain conservative" with intensity, because strong SSAO distracts in play.
  It looks best with a real indirect-light source. [src: Godot env docs]
  Cheap alternatives:
  - vertex-color AO on static props [src: threejs-aaa];
  - three.js `GTAOPass` / `SAOPass`;
  - `n8ao` (ISC).
- **Contact shadows:** use a radial-gradient `CanvasTexture` plane under objects, fading alpha with height. three.js
  `webgl_shadow_contact` shows a blurred-depth version. [src: threejs-aaa; three.js examples]
- **Fog / atmospheric perspective:**
  - depth plus height fog;
  - "aerial perspective" tints fog toward the sky color, and sun scatter tints toward the sun [src: Godot];
  - fog reveals depth and must never hide an empty world [src: threejs-aaa];
  - watch for banding: enable `material.dithering` (three.js) or follow the Godot banding guidance.

### 3.7 Post-processing with restraint

| Tone mapper | Character | Use when |
|---|---|---|
| Linear / None | clips highlights, "blown out" [Godot] | UI-only or unlit flat styles |
| Reinhard | dull, low contrast [Godot] | rarely |
| ACES (three.js uses a brightened variant, scale 1/0.6) | high contrast, desaturates brights; cannot reach canary yellow or bright greens/blues under sRGB inputs [Lalish] | cinematic, realistic, moody |
| AgX | film-like, best hue retention as colors brighten; slowest in Godot; Godot has an "AgX contrast" control | realistic or stylized with bright lights |
| Khronos PBR Neutral | output = input − 0.04 for channels in 0.08–0.8; no hue shift; highlight compression only above that [Khronos spec] | **palette-driven stylized games** where authored hex colors must survive; three.js `webgl_tonemapping` example default |

- **Exposure:**
  - start at 1.0;
  - tune on active gameplay, not on the title screen [src: threejs-aaa];
  - Godot "White" 6–8 for photoreal [src: Godot].
- **Bloom:**
  - only on authored emissive elements;
  - UnrealBloomPass strength 0.35–0.6, radius 0.2–0.4, threshold 0.85 (author's tested starting values)
    [src: threejs-aaa shader-cookbook];
  - Godot glow appears only above the HDR threshold (1.0 = tonemapper White);
  - Godot blend modes: Softlight is the subtle default; Additive is "generally too strong" [src: Godot];
  - "If a shape only reads because it glows, the geometry is missing." [src: threejs-aaa]
- **Grading:**
  - LUT 33×33×33 (also 17/51/65) is applied after tonemapping (Godot);
  - three.js has `LUTPass`;
  - prefer one global grade over per-asset tweaks to unify mixed sources.
- **Vignette** subtle, never darkening the play path. **Grain** low opacity. **Chromatic aberration** only as a brief event.
  Prefer geometry trails to motion blur. [src: threejs-aaa]
- **Outlines:** pick one method globally: `OutlinePass` for selection, `OutlineEffect` / inverted hull for toon.
  TF2 used rim highlights *instead* of outlines. [src: three.js; TF2]
- **Order:** composer → … → `OutputPass` last (tone mapping and sRGB). Cap DPR before adding passes, because post cost scales
  with DPR². Always compare post on vs post off. [src: threejs-aaa]

### 3.8 Camera

- **Defaults:**
  - three.js `PerspectiveCamera` fov = 50 (vertical) [src: three.js];
  - Godot `Camera3D` fov = 75 (vertical with keep_height), which is about 107.5° horizontal at 16:9 [src: Godot XML];
  - Unity default 60 vertical [UNVERIFIED].
- **Conversion:** `vFov = 2·atan(tan(hFov/2) · H/W)`. 90° horizontal ≈ 59° vertical at 16:9 [math].
  Typical starting points [judgment]:
  - FPS: about 90° horizontal;
  - third-person action: about 60–75° horizontal-equivalent;
  - top-down / isometric: narrow (30–45° vertical) or orthographic.
- **Smoothing must be frame-rate independent:** `x = lerp(x, g, 1 - exp(-ln2·dt/halflife))`.
  Never use a fixed `lerp(…, 0.1)` per frame. [src: Holden; awesome-gamedev camera-systems]
- **Camera follow:**
  - lag slightly behind the player;
  - lead in the aim or motion direction (look-ahead);
  - deadzone for small movement;
  - shake applied on top of follow, never to the simulated body.
  [src: screenshake notes #13–14; awesome-gamedev; threejs-aaa]
- **FOV punch:** +4–8° on boost or hit, decaying with a time constant of about 200 ms. Call `updateProjectionMatrix()`
  after the change. [src: threejs-aaa game-feel]
- **Composition:** keep the next decision visible (player, immediate threat or reward, route). Check mobile framing
  separately. [src: threejs-aaa]

### 3.9 Environment composition & set dressing

- **Layers:** play / near (speed and scale cues) / mid (playable corridor) / far (depth, cheap) / motion. Keep every layer clear of
  threats and the next decision. [src: threejs-aaa]
- **Repetition:**
  - break it with rotation, mirroring, 2–3 recolor variants, decals and vertex-paint variation [secondary: bugnet];
  - TF2 minimized repeated structures on purpose [src].
- **Clusters, not grids.** Group props in odd-numbered, varied-size clusters that share one material or color thread.
  Vary density between areas and leave rest areas. [judgment, partly secondary interior-design sources]
- **Ground contact:**
  - every object touches or casts a contact shadow;
  - darker contact material under important objects;
  - no floating props.
  [src: threejs-aaa "darker contact material", fake contact shadow]
- **Purpose:** every prop explains who uses the space. Polycount critique: "barrels with no clear purpose" [secondary].
- **Background detail:** keep it lower than the playable area so it does not generate noise. [src: TF2 skybox note]
- **Landmarks:** macro (navigation), meso (zone identity), micro (moment-to-moment). [AlterLab]

### 3.10 Materials

- Separate material roles by **roughness/metalness contrast, not hue alone**. Emissive is for authored signals only. Use a dark base
  color under emissive so only the glow reads. [src: threejs-aaa]
- Presets with values (MeshStandard / Physical) [src: threejs-aaa shader-cookbook]:
  - matte plastic r0.62;
  - rubber color 0x0a0a0b, r0.92, envMapIntensity 0.35;
  - brushed metal m1.0, r0.4;
  - clearcoat paint;
  - cloth with sheen.
- Color textures use `SRGBColorSpace`. Data maps (normal, roughness) stay linear. [src: awesome-gamedev materials]
- Use `MeshPhysicalMaterial` only when clearcoat, transmission or sheen is actually visible in play. [src: threejs-aaa]
- Wear, decals and trim imply scale and function. Reuse UI icon shapes as world decals for cohesion. [src: threejs-aaa]

### 3.11 Visual scorecard (adopt with credit) [src: threejs-aaa visual-scorecard.md]

**Categories** (scored 0–3): art direction, hero, obstacles/enemies, rewards/interactables, world, materials,
lighting/render, VFX/motion, UI/HUD, performance evidence.

**Premium bar:** every category ≥2 and average ≥2.3.

**Automatic failures:**
- placeholder-dominated or empty active screenshot;
- primitive-plus-glow hero;
- gameplay roles indistinguishable;
- HUD is mostly stat cards;
- fog, darkness or bloom replacing geometry;
- UI overlapping the play path or clipping text;
- no real-input playable shot;
- no renderer diagnostics.

**Advisory metrics** (author heuristics, not standards):
- colorEntropyBits <3.0 or dominantColorShare >0.6 means a flat, sparse scene;
- edgeDensity <0.04 means primitive-dominant;
- luminance.contrast <60 means fog/darkness compression.

"Do not add noise just to raise metrics."

### 3.12 UI/HUD for 3D games

- **Hierarchy:** survival/status → objective → feedback → flavor. Use meters, icons, rings, badges and diegetic markers before
  text. [src: threejs-game-ui-designer]
- **Banned web defaults in game UI** (unless the art direction calls for them):
  - cream or off-white panels;
  - italic accent words;
  - "01/02/03" labels;
  - monospace labels (tabular numerals are fine);
  - pill buttons;
  - one-note purple/blue gradients;
  - stat-card dashboards.
  [src: threejs-game-ui-designer ui-patterns.md, which derives from frontend-design's AI-default list]
- **Mechanics:**
  - fixed-width numeric slots;
  - safe areas;
  - touch targets about 44 CSS px;
  - focus/hover/pressed/disabled states;
  - test with the longest values;
  - UI reads state from a single source of truth. [src: same]
- **Icons:** one stroke weight, one grid, one abstraction level, "designed by one person in one sitting". Pick one
  HUD paradigm (diegetic, spatial or overlay) on purpose. [AlterLab]
- **UI motion durations** (Material tokens):
  - 50/100/150/200 ms (short);
  - 250–400 ms (medium);
  - 450–600 ms (long);
  - 700–1000 ms (extra long).
  **Easings:**
  - standard `cubic-bezier(0.2,0,0,1)`;
  - decelerate on enter `(0,0,0,1)`;
  - accelerate on exit `(0.3,0,1,1)`;
  - emphasized decelerate `(0.05,0.7,0.1,1)`.
  [src: material-components-android Motion.md]
  Game HUD reactions [src: threejs-aaa game-feel]:
  - score punch: scale 1.2→1 over 120 ms;
  - full-screen white flash: 0.8→0 over 90–120 ms on major events only.

### 3.13 Animation playbook

**Principles in games**
- The player's actions must respond in under 100 ms (Swink's correction cycle) [src: England review].
- Put weight into follow-through and recovery rather than wind-up for **player** actions.
- Use full anticipation for **enemy** telegraphs. [secondary: bugnet via search; consistent with Swink]
- Cooper's five fundamentals: Feel, Fluidity, Readability, Context, Elegance [secondary: book TOC summaries].
- Allow cancel windows (partial/complete) with buffered input [secondary: God of War article].

**Easing choice**
- ease-out (cubic/quad): settling, arrivals;
- back / overshoot: "pop" in;
- ease-in: wind-up and exits;
- ease-in-out (sine): camera and menu moves;
- elastic/bounce: sparingly, because it reads as cartoonish;
- linear: only for constant mechanical motion.
[src: awesome-gamedev feedback-recipes; threejs-aaa easeOutBack]

**Juice tiers** [src: threejs-aaa game-feel tuning table; awesome-gamedev game-feel]
- A satisfying hit is 5–8 small responses within about 100 ms. Feedback must return to rest.
- Scale feedback to importance:
  - pickup: pop + HUD punch + chime + 0.15 trauma;
  - hit: hitstop 70 ms + 0.4 trauma + flash + rumble;
  - kill: 40 ms + 0.3;
  - explosion: 90 ms + 0.7 + white flash + FOV +8°.

**Trauma screenshake**
- Add trauma per event, capped at 1.
- shake = trauma² (or ³).
- Linear decay of about 1.2–1.4 per second.
- Use smooth noise or sin, never per-frame random.
- In 3D, prefer rotational shake.
[src: threejs-aaa code; awesome-gamedev; Eiserloh model secondary]

**Hitstop**
- Scale gameplay delta to about 0.05 for 40–90 ms, heavy hits only.
- Keep rendering; camera, tweens and HUD use real delta.
- In Unity use `WaitForSecondsRealtime`; in Godot use a timer with ignore_time_scale.
- Juicy Breakout exposes freeze 0–320 ms with fade-in/out 0–160 ms.
[src: threejs-aaa; awesome-gamedev; juicy-breakout Settings.as]

**Squash and stretch**
- Preserve volume (other axes scale by 1/√s).
- About 1.15 stretch on takeoff, about 0.9 squash on landing, returning over about 180 ms with easeOutBack. [src: threejs-aaa]

**Juice checklists**
- *Juice it or lose it* (Juicy Breakout `Settings.as`) [src]:
  - tween-in of y/rotation/scale (0.7 s);
  - paddle stretch;
  - ball stretch/rotate/glow;
  - block jelly;
  - bouncy lines;
  - collision particles;
  - block destruction (scale, gravity, push, rotate, darken, shatter);
  - trail (length 30);
  - screen shake (power 0.5);
  - freeze;
  - "personality" (face, look-at-ball, smile, eyes);
  - final color glitch.
- *Art of Screenshake* (31 steps; two independent notes agree; talk not watched) [src: ShotgunTom notes; DK Liao]:
  - animation and sound;
  - lower enemy HP;
  - higher rate of fire;
  - bigger and faster bullets;
  - muzzle flash;
  - less accuracy;
  - impact effects;
  - hit flash;
  - enemy knockback;
  - permanence (corpses, shells, smoke);
  - camera lerp and look-ahead;
  - screen shake;
  - player knockback;
  - "sleep" about 20 ms at impact;
  - gun kick;
  - more bass;
  - random explosions;
  - camera kick opposite to firing;
  - bigger explosions;
  - meaning (player can die) and a death animation.

**Secondary motion / springs**
- Use critically damped springs or half-life dampers [src: Holden spring-roll-call].
- Second-order dynamics (frequency f, damping ζ, response r) come from t3ssel8r's video [UNVERIFIED; video only].
- Engine primitives:
  - Godot SpringBoneSimulator3D (4.4+);
  - three-vrm spring bones;
  - three.js CCDIKSolver;
  - Godot LookAtModifier3D (4.4+), TwoBoneIK3D (4.6+), RetargetModifier3D (4.4+);
  - Godot SkeletonIK3D is deprecated.

**Locomotion / root motion** [src: Holden code-vs-data-driven-displacement]
- **Synchronize** the character to the simulation: responsive, but slides unless the data matches.
- **Data-driven** movement: no sliding, but sluggish.
- **Adjust:** damp the character toward the simulation with a half-life.
- **Clamp** the maximum deviation.
- **Foot lock + IK** as a last resort.
- Do not set rotation responsiveness too high, or the character spins on the spot.
- Measure the clip's root speed (Holden's mocap: run about 4 m/s forward, walk about 1.75 m/s) and drive playback rate or blend
  weights from the actual speed.

**Blending**
- three.js:
  - `startAction.crossFadeTo(endAction, dur, warp=true)` after `endAction.enabled = true; setEffectiveTimeScale(1); setEffectiveWeight(1); time = 0`;
  - for cycles, cross-fade at the loop boundary (mixer 'loop' event);
  - additive layers: `AnimationUtils.makeClipAdditive`;
  - the example's 0.5–5 s fades are demo values, not gameplay values.
  [src: three.js examples/source]
- Gameplay crossfades: Unity default transition is 0.25 s [secondary]. Start at 0.1–0.25 s and use shorter fades for
  starts/stops/turns [judgment].
- Godot AnimationTree [src: godot-docs animation_tree.rst]:
  - StateMachine transitions with Xfade Time and Xfade Curve (non-linear);
  - Sync mode;
  - Advance Expression;
  - BlendSpace1D/2D;
  - OneShot with fade in/out and filters (layering);
  - root motion track.
- Inertialization / "dead blending" (extrapolate the source clip and crossfade) avoids pops on abrupt transitions.
  [src: Holden dead-blending]

**Pipeline** (rig → skin → animate → glTF)
- Mixamo has no public API. Automation exists only as browser scripting (mixamo-mcp, 4★; ToS not addressed); avoid it in a
  skill.
- Common Mixamo traps [secondary]:
  - "mixamorig:" bone prefix mismatches;
  - choose in-place vs root motion at download.
- Blender export (glTF-Blender-IO) [src]:
  - every action must be active or stashed on an NLA track, one action per track, otherwise it is not exported;
  - track name = glTF animation name;
  - Blender 4.4 slotted actions merge by action, not by name;
  - enable "Reset pose bones between actions" when bones are not keyed in every clip;
  - keep sampling on ("not sampling can lead to wrong export");
  - "Set all glTF Animation starting at 0" for loops;
  - "Export deformation bones only" bakes animation.
- three.js runtime: `THREE.Clock` is deprecated since r183; use `THREE.Timer`. Always call `mixer.update(dt)` with real delta.
  [src: three.js]

### 3.14 Animation QA checks (agent-runnable)

Unless marked, these are designs [judgment], with thresholds taken from sources where noted.

1. **Deterministic capture.**
   - Load all assets.
   - Pin renderer size and DPR.
   - For each clip, call `mixer.setTime(t)` for t = k/fps (k = 0..N) and render.
   - Montage the frames into a contact sheet (e.g. 4×6) for visual review.
   [`mixer.setTime` src: three.js; pattern secondary: HyperFrames docs]
2. **Foot skate.**
   - Log the world-space toe/ankle positions per frame.
   - Flag frames where a foot under 5 cm high slides more than 2.5 cm horizontally (OmniControl-style), or moves faster than
     10 cm/s below 10 cm (alternative).
   - Report the ratio of skate frames over contact frames.
   [thresholds secondary: research papers; the metric is not standardized]
3. **Pops.** Flag per-bone angular velocity spikes between consecutive frames, e.g. a jump of more than 3× the clip's median during
   a transition window [judgment threshold].
4. **Loop seam.** For looping clips, the first and last poses (and their velocities) must match within a tolerance [judgment].
5. **Bind/T-pose leaks.**
   - Compare bone quaternions against the bind pose on the first frames after load, spawn and transition.
   - Any frame equal to the bind pose on a visible character is a fail [judgment].
6. **Frame-rate independence.** Run the simulation at fixed dt 1/30, 1/60 and 1/144. Camera, follow and damper positions at
   t = 2 s must match within epsilon. Search the code for `lerp(…, constant)` and `Math.random` in feel paths.
   [src: Holden; threejs-aaa determinism]
7. **Speed match.** Compare root or simulation speed against the clip's measured stride speed. Playback rate must track it.
8. **Linear stiffness.** Inspect the tween/curve list for linear easing on non-mechanical motion. Check that keyframe interpolation is
   not STEP unintentionally (the glTF sampling fallback).
9. **Juice sanity.** Shake decays to 0. Input registers during hitstop. No effect hides the next threat. A
   reduced-motion/shake setting exists. [src: awesome-gamedev; threejs-aaa]
10. **A still image cannot prove animation quality.** Require unpaused motion evidence (frame sequence or video) of transitions
    and contacts. [src: threejs-aaa scorecard]

---

## 4. Failure modes & anti-patterns: tell → fix

| AI/programmer-art tell (3D) | Evidence | Fix |
|---|---|---|
| Default grey / unlit flat `MeshBasicMaterial` everywhere | Default-grey look [secondary]; scorecard "1 = basic" anchor [src] | Palette-role materials; lit materials + IBL |
| White key/fill/back + grey ambient (0x404040), no IBL | cloudai-x presets [src] | Warm key + cool hemisphere fill + RoomEnvironment PMREM + rim; tone mapping |
| No tone mapping or wrong mapper washing out the palette | ACES/AgX saturation loss [src: Lalish, Khronos] | Choose deliberately (§3.7); Neutral for palette-driven stylized games |
| Rainbow / oversaturated palette, every object a new hue | TF2 "muted dominant, small saturated" [src] | 5–7 role palette; saturation reserved for gameplay signals |
| Bloom/glow/fog as the "style" | threejs-aaa auto-failure [src] | Authored geometry first; bloom threshold about 0.85 on emissive only |
| Primitive hero (box + cylinders + glow), recolored-cube "families" | threejs-aaa [src] | Silhouette-first authored forms, functional parts, role-specific shapes |
| Floating objects, no contact shadows | threejs-aaa contact recipes [src] | Blob/contact shadows, vertex AO, darker contact material, snap to ground |
| Perfect grids, uniform scale/rotation/spacing, symmetric layouts | TF2 repetition note [src]; set-dressing advice [secondary] | Clusters, ±10–20% scale and rotation jitter (seeded) [judgment], density variation, rest areas |
| Mixed asset styles / detail levels | asset-flip articles [secondary, low weight] | One style in the bible; global grade; replace the most-seen assets first |
| Visual noise / high-frequency detail everywhere | TF2 notes [src] | Lower detail in background; group values; minimize repetition |
| Web-SaaS HUD (stat cards, cream panels, pills, gradient, emoji, generic font) | threejs-game-ui-designer + frontend-design lists [src] | Genre HUD clusters, world motifs, one deliberate typeface, consistent icon grid |
| Linear tweens, no anticipation/follow-through | awesome-gamedev pitfalls [src] | Easing table (§3.13) |
| `lerp(a, b, 0.1)` per frame; `Math.random` shake | Holden; awesome-gamedev [src] | Half-life damper; noise-based trauma shake |
| Foot sliding, spinning-on-the-spot turns | Holden [src] | Speed matching, adjustment/clamp, foot lock IK, lower rotation responsiveness |
| Missing clips after export; T-pose flashes | glTF-Blender-IO docs [src] | NLA stash rules, reset pose between actions, QA check 5 |
| Over-juicing (shake on footsteps, constant shake) | threejs-aaa / awesome-gamedev anti-patterns [src] | Importance tiers; accessibility toggle |
| "Done" claimed from a title screen or a still | threejs-aaa scorecard rules [src] | Active-play captures, grayscale/silhouette/post-off shots, motion evidence |

---

## 5. Hype vs. reality / honest gaps

- **Persona skills** (AlterLab "Sable Mori", Donchitos art-director) mostly encode collaboration protocol and human-studio
  process: PureRef boards, the "70-20-10" reference rule, "75% first-review pass rate". None of this is executable by an agent,
  and none of it is evidenced. Donchitos' art-director has `disallowedTools: Bash`, cannot see the game, and defers every
  decision to the user. That suits a human-led studio, not quality enforcement.
- **threejs-game-skills numbers are one author's tuned values.** Examples: bloom ranges, trauma per event, canvas metric
  thresholds. They are good starting points, not standards. I did not run its scripts (rules forbid it), and its anchor JPGs
  were not viewed.
- **canvas-design's "repeat 'master-level craftsmanship' phrases" tactic has no evidence it improves output.** I would not copy it.
- **Classic talks are video-only.** Art of Screenshake, Juice it or lose it, Juicing Your Cameras, 50 Camera Mistakes and
  Rosen's procedural animation were all inaccessible. I used code and fan notes as text proxies, and I did not reach Eiserloh's slides.
- **The 60/30/10 rule, the "rule of three" and the "squint test"** are art and interior-design heuristics with no game-specific
  primary source found [UNVERIFIED as rules].
- **Mixamo automation is fragile.** It is browser scripting with unclear ToS. GSAP is free but not OSI-licensed. Theatre.js has had
  no release since 2024-05.
- **Unverified items:** Unity default FOV (60) and the "Godot 4.7" mention in awesome-gamedev.
- **Blocked sources:** many articles behind bugnet.io, gamedev.net, polycount and gamedeveloper.com could not be read. Claims from
  them are [secondary].
- **Taste has limits as a rule set.** Rules prevent the worst defaults, but quality still needs screenshot critique,
  ideally by a separate reviewer agent with the scorecard and anchors.

---

## 6. Recommendations for the skill

1. **Art-director subagent (runs first, read-only plus writes docs).**
   - Produces `art-bible.md` (§3.2) plus a machine-readable `render-recipe.ts/json`: palette roles, tone mapper, exposure,
     lights, shadows, fog, post values, easing and juice tiers.
   - Must run the generic-check pass and list its banned defaults.
   - Gate: AD-review checklist (§3.2) before any asset or scene work.
2. **Enforce the order:** forms → materials → lighting → post/VFX. Block bloom, fog or post work while scorecard "Hero" or "World" < 2.
3. **Visual QA subagent (separate from the builder).**
   - Captures fixed camera bookmarks in four variants: color, grayscale, silhouette (unlit black on grey), and post-off.
   - Covers desktop and mobile.
   - Scores the 10-category scorecard with one evidence line each, plus the automatic-failure list and §4 tells.
   - Must name the weakest category and the next pass.
4. **Animation subagent.**
   - Owns the pipeline rules (§3.13), the juice tier table and the QA script (§3.14: deterministic `setTime` contact sheets,
     foot-skate ratio, pop detector, loop seam, bind-pose check, dt-invariance test).
   - Ships helpers: half-life damper, trauma shake, hitstop with real-delta feedback, volume-preserving squash, tween manager.
5. **Defaults to ship:**
   - stylized low-poly / palette style;
   - Neutral (or AgX) tone mapping;
   - hemisphere + warm sun + RoomEnvironment IBL;
   - one shadow-casting sun with a tight frustum;
   - blob contact shadows;
   - restrained bloom;
   - `OutputPass` last;
   - DPR cap.
   Each value lives in the recipe file so the reviewer can diff it.
6. **UI rules:** the banned web-default list plus Material duration tokens. Require icons from one set or one grid.
7. **Leave out:**
   - persona backstories;
   - human reference-board process;
   - unverifiable "success metrics";
   - craftsmanship-mantra repetition;
   - 2D frame-count tables;
   - Mixamo browser automation.
8. **Credit and licensing:**
   - credit anthropics/skills (Apache-2.0), threejs-game-skills (MIT), awesome-gamedev-agent-skills (Apache-2.0),
     Donchitos (MIT), juicy-breakout (zlib);
   - write our own text for Valve and Holden material (no reuse license), paraphrased with citation.

---

## 7. Videos found but not watchable

- "Juice it or lose it" (Jonasson & Purho, 2012): youtube.com/watch?v=Fy0aCDmgnxg. Text proxy: juicy-breakout README and `Settings.as`.
- "The Art of Screenshake" (Jan Willem Nijman, Vlambeer). Text proxy: ShotgunTom notes and DK Liao's post (31 steps).
- "Math for Game Programmers: Juicing Your Cameras With Math" (Squirrel Eiserloh, GDC 2016). Summaries [secondary]:
  trauma 0–1 with decay, shake = trauma^2–3, Perlin noise, rotational shake in 3D.
- "50 Common Game Camera Mistakes" (John Nesky, GDC 2014). Only a coverage article quote surfaced: "Cameras are most noticeable when they fail".
- "An Indie Approach to Procedural Animation" (David Rosen, GDC 2014). Few keyframes plus procedural interpolation [secondary].
- "Giving Personality to Procedural Animations using Math" (t3ssel8r): second-order dynamics [secondary].
- "The Art of Overwatch: Evolving" (GDC 2017). Readability pillar; Torbjörn used as the visual target [secondary].

---

## 8. Sources

**Opened (primary / code / docs)**
- github.com/anthropics/skills: skills/frontend-design, canvas-design, algorithmic-art, theme-factory, brand-guidelines (cloned 2026-10-09)
- github.com/majidmanzarpour/threejs-game-skills: threejs-aaa-graphics-builder (SKILL.md, visual-scorecard.md, authoring-recipes.md, shader-cookbook.md, technical-art.md), threejs-gameplay-systems/references/game-feel.md, threejs-game-ui-designer (SKILL.md, ui-patterns.md); GitHub page for stars
- github.com/Donchitos/Claude-Code-Game-Studios: .claude/docs/templates/art-bible.md, .claude/skills/art-bible/SKILL.md, .claude/agents/art-director.md, director-gates/ad-art-bible.md, ad-visual.md; GitHub page
- github.com/AlterLab-IEU/AlterLab_GameForge: skills/agents/game-art-director/SKILL.md, templates/art-bible.md
- github.com/vudovn/ag-kit: .agents/skills/game-development/game-art/SKILL.md
- github.com/cloudai-x/threejs-skills: threejs-animation, threejs-lighting SKILL.md
- github.com/gamedev-skills/awesome-gamedev-agent-skills: disciplines/game-feel (+ references/feedback-recipes.md), camera-systems, web-engines/threejs-materials-lighting; GitHub page
- github.com/grapefrukt/juicy-breakout: README.rst, src/…/Settings.as
- github.com/KhronosGroup/ToneMapping: PBR_Neutral/README.md
- github.com/mrdoob/three.js (dev): tonemapping_pars_fragment.glsl.js, AnimationAction.js, AnimationMixer.js, core/Clock.js, PerspectiveCamera.js, examples webgl_animation_skinning_blending/additive_blending/walk, webgl_lights_hemisphere, webgl_tonemapping, webgl_shadow_contact; existence of LUTPass, OutlinePass, OutlineEffect, GTAOPass, SAOPass, SSAOPass, SMAAPass, OutputPass, CCDIKSolver, MeshToonMaterial; Material.dithering
- github.com/godotengine/godot-docs: tutorials/3d/environment_and_post_processing.rst, lights_and_shadows.rst, high_dynamic_range.rst, animation/animation_tree.rst
- github.com/godotengine/godot doc/classes: SpringBoneSimulator3D, LookAtModifier3D, TwoBoneIK3D, SkeletonIK3D, RetargetModifier3D, Camera3D, Tween (branches 4.4/4.5/4.6/master)
- github.com/KhronosGroup/glTF-Blender-IO: docs/blender_docs/scene_gltf2.rst
- github.com/material-components/material-components-android: docs/theming/Motion.md
- cdn.fastly.steamstatic.com/apps/valve/2008/GDC2008_StylizationWithAPurpose_TF2.pdf
- advances.realtimerendering.com/s2007/Mitchell-IllustrativeRenderingInTF2(Siggraph07 Course Notes).pdf
- theorangeduck.com/page/spring-roll-call, /page/code-vs-data-driven-displacement, /page/dead-blending; github.com/orangeduck/Spring-It-On
- modelviewer.dev/examples/tone-mapping
- 80.lv/articles/comparing-team-fortress-2-and-overwatch-art-direction
- lizengland.com/blog/review-game-feel-by-steve-swink/
- github.com/mingrui/ShotgunTom (README); blog.chosenconcept.dev/posts/2022/11/0012-the-art-of-screenshake/
- github.com/V1xel/mixamo-mcp (GitHub page)
- wayline.io/blog/asset-pack-visual-identity (content marketing)
- registry.npmjs.org: three, gsap, @tweenjs/tween.js, motion, @theatre/core, @pixiv/three-vrm, postprocessing, n8ao, camera-controls

**Secondary only (WebSearch summaries; originals not opened)**
- bugnet.io blogs (asset-store look, lighting basics, foot sliding, animation basics)
- gamedev.net "Better Programmer Art" / "Programmer Art in Unity"
- leadwerks blog
- Unity issue tracker (0.25 s default transition)
- Animancer docs
- arXiv motion papers: OmniControl 2310.08580, Learning Motion Priors 2108.10399, RoHM 2401.08570, MVAE 2103.14274, NeMF 2206.03287, survey 2307.10894
- arXiv 2011.09201 (Designing Game Feel survey)
- Game Developer coverage of Overwatch GDC 2017 and Nesky GDC 2014
- polycount threads (PBR albedo ranges; set-dressing critique)
- HyperFrames three adapter docs
- Cooper *Game Anim* TOC summaries
