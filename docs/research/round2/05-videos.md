# 05 — YouTube & Instagram: practitioner rules from videos (Round-2 Agent 5)

Method: I pulled auto-captions (yt-dlp, `en-orig` track) for 15 videos and read them in full or grepped for key terms.
Every rule below is something said in a video. It is cited as [V# m:ss], and the video list is in §5.
Raw timestamped notes for each video are in `05-videos-notes.md` (same folder).
I watched no frames, so anything that is only *shown* on screen is not covered.
Tags: [judgment] = my own inference; [UNVERIFIED] = said in a video but I did not check it independently.

## 1. Summary

- **Claude "modelling from scratch" in Blender gives primitive assemblies.** Several videos say so directly. "If you try and tell it to model something
  from scratch … it's going to try and build it from primitive objects and not really work" [V5 14:47]. The setups that worked were kit assembly
  from pre-made parts with metadata [V5], technical jobs (baking, LODs, geometry-nodes scatter, shaders, batch scripts) [V2, V3], or a
  generated mesh used only as scaffolding [V12].
- **Typical first-pass defects of an LLM-built scene:** floating assets, duplicate ground planes, off-centre parts, overlapping objects,
  hard-to-read areas, and dozens of one-colour materials [V4 10:12–13:21; V12 0:21]. The fix in every case was an explicit defect list, then hand polish.
- **A disciplined MCP loop from a university course** (V1): written brief (size in metres, origin, triangle budget, predicted failures) → `get_scene_info` →
  plan without building → one `execute_blender_code` per object → report transforms → apply transforms → headless numeric check → human visual check.
- **AI image-to-3D is reliable only when used as follows:**
  - split the asset into parts and generate each part separately [V6 3:47];
  - generate high-poly, then bake onto a fresh low-poly (Decimate alone wrecks textures) [V3 2:23–5:28];
  - use smart-low-poly modes only for small props [V3 1:22, 8:55];
  - expect to rebuild the PBR maps [V6 6:49; V11 3:26].
  - Even the best models fail 10–20% of the time [V6 4:28].
- **Art direction:** choose a style you can produce in volume, built from "small replicable geometric shapes" [V13 10:31]. Silhouette comes first for low-poly
  work [V10 2:01–4:05]. A single palette texture for the whole world plus triplanar noise is a cheap way to get a cohesive stylized look [V15 21:24–23:06].
- **Lighting / post (Kyle Banks):** pick the emotion first; shadow strength about 0.9, not 1; ACES; "go too far then dial back" on contrast and saturation;
  bloom "less is more"; shadow cards and light cards; subtle film grain against banding [V15].
- **Game-feel talks, now watched:**
  - Eiserloh confirms trauma² or trauma³ with linear decay, Perlin noise with a separate seed per channel, and rotation-only shake in 3D;
  - Nijman confirms a ~20 ms "sleep" on hit and gives many concrete tricks;
  - Nesky's 50 camera mistakes are now itemised (§2.7);
  - "Juice it or lose it" ranks sound as "the most cost-effective" juice [V7 7:32].
- **Accessibility from two talks:** screen shake, camera bob and FOV shifts must be optional or tunable. Vlambeer had to add a toggle after players got nauseous
  [V9 32:14; V14 50:12–51:57].
- **Instagram is not usable without login:** tag pages redirect to a JS shell with no captions, and profiles redirect to login with HTTP 429.

## 2. Ready-to-use additions for the skill

### 2.1 Blender MCP workflow (Claude driving Blender)

**Setup facts (2026)**
- An official Blender MCP add-on exists. Download it from blender.org/lab/mcp, then Edit › Preferences › Add-ons › Install from Disk. It auto-starts on port
  9876. Save Preferences [V4 1:48–3:51; V2 1:01–1:41].
- In Claude Desktop, enable the "Blender" connector (Settings › Connectors) and restart Claude fully after installing any connector or skill
  [V4 0:21–4:11; V2 1:41].
- The connector has a per-tool "needs approval / always allow" setting [V4 1:07].
- Safety: the add-on runs Claude-written Python inside Blender with no guard. Keep the port on localhost. Save before sessions. Disable the add-on when
  idle. Don't open untrusted .blend files while it is running [V1 6:26–6:50].
- **Tool names drift between versions.** V1 says the community version it recorded had `get_object_info`, `get_viewport_screenshot` and `export_scene`,
  and that v2.1.9 (6 Oct) removed all three and added `look` [V1 8:08–8:20] [UNVERIFIED]. Rule for the skill: list the tools the live server offers
  before planning. Never hard-code tool names.
- **Fallback when MCP won't connect** (V1 allows about 2 h of trying first):
  `blender -b --factory-startup --python build.py --python-exit-code 1`.
  Without `--python-exit-code 1`, Blender exits 0 even when the script raised an error [V1 6:58–7:18].

**Procedure: one asset** [V1 3:55–10:20 unless noted]
1. Write a brief before building anything:
   - name, role and where it appears in the game;
   - size in metres, justified against the player's height or the tile size (1 Blender unit = 1 m = 1 Godot unit);
   - origin at the centre of the base, built at the world origin with the base on the floor;
   - look: the silhouette-defining shape plus material colours;
   - triangle budget;
   - at least 3 predicted failures, each with the check that would catch it (e.g. "arrives lying on its side").
2. The prompt asks Claude to:
   - call `get_scene_info` first and say what is already in the scene;
   - propose steps without building yet.
3. After approval: one `execute_blender_code` call per object. After each call, report location, size, rotation and scale.
4. Apply rotation and scale before finishing. The prompt forbids model downloads and AI-generation tools (when the task is hand-built geometry) and ends
   with "say what you could not verify".
5. Save every `execute_blender_code` body into a per-asset script so git shows how the asset was built. Save the .blend file and don't commit the .blend1 backup.
6. Export GLB with +Y Up on (the default). The newer MCP has no export tool, so run the glTF exporter through `execute_blender_code` [V1 8:54–9:20].
7. Run a headless check script that prints, per asset:
   - bounding-box size, compared against the brief;
   - node scale, which must be (1,1,1);
   - up axis;
   - placement on the floor without moving it: sit, sink or float? This tests the origin.
   - Moving the node to compensate only hides the bug [V1 4:38, 9:54].
8. Read the check Claude wrote. "A check can prove less than it claims": in one case an agent's floor check hit the object's own collider [V1 10:10].
9. A human orbits the asset (including from behind and below) and makes at least one hand edit [V1 8:20, 10:20].
   "Claude can't tell you whether it looks right" [V1 8:20]. A passing numeric check "doesn't show they look right in your game" [V1 12:10].

**Triangle facts** [V1 1:25–1:45, Blender 5.1]
- Cube = 12 tris.
- Default cylinder = 124 tris.
- Default UV sphere = 960 tris. A UV sphere at 12 segments × 6 rings = 120 tris.
- Rule: always set segment and ring counts explicitly on primitives.

**Prompting patterns that improved results**
- Paste several reference images, then ask Claude either to ask clarifying questions first or to "do its best" and iterate. Ask for further suggestions
  at the end [V4 5:39–9:31].
- The second prompt should list every visible defect by name, e.g. "tents off-centre from beams; two floors; floating assets" [V4 11:15–13:21].
- Iterate with screenshots and named defects. In V3, one bake/retopo job took several passes (about 28 min) before it was acceptable [V3 4:27–5:28].
- After a successful manual or agent pass, ask Claude to turn what it learned into a reusable, parameterised Python script (e.g. target tris and texture
  size). V3 then batched 8 houses [V3 5:49–7:11].
- Get the agent to rename `Cube.007` etc. to semantic part names inferred from position and dimensions (laces, tongue …) [V5 6:27–7:08].
- **Kit-assembly mode:**
  - keep a library of pre-made parts and materials;
  - attach JSON metadata to each part as object custom properties;
  - the agent selects and assembles parts "like a puzzle";
  - the agent only recolours procedural materials (colour ramp; noise → bump keeps the detail) [V5 0:41–4:03, 7:49–8:09].
- **Jobs Claude + Blender MCP did well in one prompt** [V2]:
  - bake high→low normal + AO and wire them into the shader (7:23–8:23);
  - geometry-nodes scatter of several plant variants over terrain with a density control (8:44–10:06);
  - split a mesh by loose parts and animate the parts (10:46–11:28);
  - procedural car paint (colour ramp + layer weight) (11:48);
  - toon shader + outline modifier (12:28);
  - an LOD chain that decimates the mesh AND downsizes textures 4K→1K→512 (12:48–13:30).

### 2.2 Modelling rules (game-ready, low-poly / stylized)

- **References:** gather a reference board. Include real-world photos of the object, not only other artists' stylized versions ("don't go straight for the
  stylized art") [V10 0:40–1:41].
- **Silhouette first:** sketch many thumbnails, push one too far and pull back, then fill the chosen shape black.
  "If your silhouettes look good your objects are probably going to look good." For low-poly the silhouette is "all important" because there are only flat
  colours and no fine detail [V10 2:01–4:05].
  - Skill procedure [judgment]: render the asset as a black silhouette from 3–4 angles and judge it before adding colour.
- **Character details:** add small asymmetric notches and nicks (bevel an edge, then edge-slide with Auto Merge, or use the knife) so the object "has a story"
  [V10 4:26–6:09].
- **Split complex objects into parts:** e.g. tree = roots / trunk base / branches + alpha-card leaf planes [V6 9:10]. Fence nets = planes with a transparent
  texture [V11 3:06].
- **Walls and floors:** don't model or generate the geometry; use seamless tileable textures with normal maps [V6 9:52–10:54].
- **Use the generator's output in the right role:** a messy generated level mesh or rough 3D is scaffolding to model over, never the shipped asset [V12 1:03–1:24].
- **Material count:** collapse "one material per colour" into prefabs plus a single texture atlas [V12 0:21, 1:45].
  The same idea appears as one palette texture for the whole world [V15 22:04].
- **Triangle budgets seen in practice (examples, not standards):**
  - 500 tris per beginner prop [V1];
  - 500 polys (quads) per background prop and 15,000 for a hero prop [V11 1:42–2:03];
  - about 4–5k tris per small AI prop [V3 8:55];
  - under 40k tris per AI-generated house with 8K colour + normal maps (he notes the textures could be compressed) [V3 7:11–7:32].

### 2.3 AI 3D generation (Tripo / Hunyuan / Meshy-style) — what practitioners report

| Finding | Source |
|---|---|
| Generating a whole complex asset at once → blurry areas, joined mesh, artifacts. "Your approach was absolutely wrong": split into parts, generate each, combine | V6 3:47–4:28 |
| Even the newest models fail on 10–20% of attempts | V6 4:28 |
| Smart/low-poly mode is good for small simple props. On a complex building it produced holes, a missing chimney chunk and warped textures | V3 1:02–1:22, 8:55 |
| Highest quality gives more than 1.8M tris. Decimate at 0.02 (about 37k tris) → distorted textures and artifacts: "clearly was not going to work" | V3 1:43–3:05 |
| What worked: duplicate → fresh Smart UV Project on the low-poly → bake high→low (colour + normal) → iterate with screenshots → script it | V3 4:07–7:32 |
| AI colour textures are good. AI PBR is "sort of weak", and metal/reflective surfaces come out "average" → set the materials by hand (Substance Painter or similar) | V6 6:49–9:52 |
| "Even if you ask to create PBR right away … you still need to recreate some of them" | V11 3:26 |
| Better pipeline: style-consistent 2D concept → 4 generated views → quad mesh at a target poly count → unwrap → texture | V11 1:21–1:42 |
| Concept → "matrix" sheet of individual assets in one style keeps a set consistent | V3 0:41; V11 1:01 |
| Generate 2–6 small props in one image or model, then split them in Blender (saves paid generations) | V3 9:17–9:39 |
| Auto-rigging (AccuRIG [caption read "Acrylic"], Mixamo) gives a base, but weight fixes are "inevitable". Hair bones and hair cards: AI is a "dead end" | V6 7:29–8:09 |
| Water and other dynamic or logic-driven assets don't suit generation | V6 10:54 |
| Best results come from mixing AI assets with existing asset packs (terrain, foliage, lighting) plus manual cleanup | V3 8:14, 12:03 |
| A 3D artist's verdict: AI pays off most in code; for 3D, "explaining every visual and technical decision takes longer than just doing it myself" | V12 1:45–2:05 |

Caveat: V2, V6 and V11 are sponsored or creator-promotional (3D AI Studio, Customuse), so treat their tool praise with care. Their reported failures are more trustworthy than the praise.

### 2.4 Art direction

- **Score candidate styles on four criteria** [V13 4:11–6:19]:
  1. the team likes it;
  2. audience response against a measured baseline;
  3. **ease of creation:** can the team produce hundreds of assets in it?
  4. what gameplay the style implies or allows.
- Reject styles that are unaffordable (isometric + heavy detail) or forgettable ("generic … you would probably not remember") [V13 7:01–10:09].
- Prefer styles built from small replicable geometric shapes that can be reused across buildings and the world [V13 10:31–11:12].
- Set art constraints up front, e.g. a maximum sprite or texture resolution [V13 20:32].
- Art style constrains gameplay: in V13 only 6–7 buildings fit on screen, so the game was designed around that limit [V13 14:18–16:42].
- Realism is easier to keep consistent with CC0 PBR texture libraries. Stylized looks need more deliberate work but can mask an artist's limits [V15 1:01–1:43].
- Colour: step 1 of juice is colour so friend and foe read apart [V7 2:03]. Use a complementary pair such as blue/orange for contrast [V15 12:13].
- Keep separate the elements that must read as different: dying blocks darken so they don't blend with live ones [V7 10:39–11:00].

### 2.5 Lighting & post-processing recipe [V15 unless noted]

1. Name the target emotion first (e.g. calm nostalgia vs. lonely). Lighting and post serve it (3:23–4:05, 16:59).
2. Key light: a warm sun placed so it crosses the space at an angle, giving room for light shafts (4:05).
3. Bake indirect lighting. Lower skybox intensity for interiors (4:25).
4. Shadow strength about **0.9**, not 1.0. Pure-black shadows look fine on the dev's screen but go pitch black for players (5:05).
5. SSAO to ground contact points, kept modest: "really easy to go too far" (5:25).
6. Use **shadow cards** (semi-transparent black gradient planes, unlit, soft particles) to ground furniture where AO has nothing to latch onto.
   Use **light cards** (warm planes or cones with scrolling noise) for windows and spotlights. Fade cards as the camera approaches (10:32–11:32, 23:47).
7. Volumetrics: jitter with noise to hide step banding, render at ½–⅛ resolution, tie to quality tiers, and fall back to light cards on low-end hardware (6:26–10:11).
8. Grading:
   - ACES tonemapper;
   - contrast and saturation: "go way too far, then dial it back";
   - lift midtones slightly and drop shadows slightly (12:53–14:15).
9. Vignette: soft and low intensity (14:15).
10. Bloom: threshold around 0.25 in his scene. "One of the biggest mistakes … they go way too far with the bloom … less is more." Downscale to half resolution, 4–5 iterations (14:36–15:18).
11. Film grain: very subtle. It also masks colour banding after streaming or YouTube compression (15:39).
12. Mirrors and glossy surfaces need a baked reflection probe (17:19).
13. Ambient life:
    - dust particles around the camera;
    - wind sway via a sine-wave vertex shader masked by vertex colour;
    - shadow-only objects orbiting outside a window to fake a bird flock (18:20–20:42).
    "Keep it simple … until you really need the added complexity" (21:03).
14. Fog tinted to the mood (light blue = cold, nautical) (24:07).

### 2.6 Game feel / juice (confirmations and new specifics vs. round 1)

**Eiserloh** [V8]
- **Trauma model:**
  - keep a separate `trauma` variable;
  - hits add to it: a big hit about +0.5, small stress +0.1–0.2;
  - it decays linearly and time-based;
  - shake = trauma² or trauma³ (3:46–4:28).
  - Why: minor, moderate and major hits become distinguishable, stacked hits escalate, and linear shake "stops very suddenly" (5:10–6:38).
  - He gives no decay-rate number, so round 1's 1.2–1.4 per second is not from this talk.
- **Shake dimensions:**
  - 2D: translation + rotation;
  - 3D: rotation only, because translational shake looks spastic near geometry and pushes the camera into walls;
  - VR: no shake at all (6:38–9:30).
- **Code shape:**
  - `angle = maxAngle·shake·noise`, e.g. maxAngle 10°;
  - `offset = maxOffset·shake·noise`;
  - apply to a shaky **copy** of the base camera, rebuilt every frame, and never mutate the base camera;
  - 3D: separate yaw, pitch and roll amplitudes (9:54–11:37).
- **Noise:**
  - use Perlin or smooth noise, not random: random has infinite frequency and breaks in slow motion;
  - noise is frame-rate independent and has a tunable frequency (slow noise gives a handheld-camera feel);
  - use a **different seed per channel** (11:37–14:44).
- **Smoothing:** `x += (target−x)·k`, with k 0.01 slow / 0.10 reasonably fast / 0.50 quite fast. Make it time-scaled (17:12–20:42).
- **Axes can follow differently:** horizontally always; vertically only when the player lands; tightly when the player falls (19:17–20:19).
- **Framing:**
  - never lose the player;
  - drop a secondary target before the player;
  - points of interest pull the camera subtly with feathered weights (e.g. ramp from 10 to 5 tiles; weight = closeness × importance) (21:43–25:33).
- **Co-op:** Voronoi dynamic split screen with a feathered merge (25:33–29:44).

**Nijman** [V9]
- **Weapons:**
  - bullets at least "the size of your chest";
  - muzzle flash = the first frame as a circle;
  - faster bullets;
  - spread / less accuracy (9:54–10:57).
- **Hits:** white hit flash; enemy knockback of a few pixels; impact effects on walls (11:38–12:43).
- **Permanence:** corpses, rubble and shells stay; props react to missed shots (13:03–14:24, 20:26).
- **Camera:** lerp, plus a shift toward the aim. In Luftrausers the camera biases toward nearby water and the centroid of bullets (14:24–16:29).
- **Player knockback on firing:** "give someone a reason to not press" the button (16:52–17:37).
- **Sleep:** about 20 ms on hit and on death (17:59–18:41).
- **Gun kick:** about 3 px. **Camera kick** opposite to the firing direction (24:00, 25:53).
- **Audio:** more bass. Anecdote: a +12 dB bass boost "fixed" an unpopular gun (21:34–22:37).
- **Explosions and death:** a 33% chance that enemies explode on death; "make really big explosions" (a circle flashing black→white, plus lingering
  smoke); death plays in slow motion (10 fps) (23:39–29:28).
- **Process:** "make our games in a couple of days and then spend the year polishing" (35:29). "You're the worst playtester" (31:33).

**Jonasson & Purho** [V7]
- **Block entrance:** ease-out, then overshoot or bounce. Tween rotation and scale too, and add a **random delay per object** (4:07–5:07).
- **Ball and paddle:** ball scale-pops on hit, rotates toward its velocity, stretches by speed, wobbles, flashes white; paddle stretches from the pointer
  offset; all blocks jiggle on any hit (5:49–7:32).
- **Sound:** "the most cost-effective thing you can add". The Swink demo: two circles seem to bounce instead of overlap once sound is added (7:32–8:33).
- **Particles:** use an existing particle system, don't write your own ("trap for programmers"); smoke on impact; debris that falls with gravity, gets
  pushed, spins and darkens; confetti; a trail drawn from position history (9:36–11:44).
- **Eyes on objects:** blink, look at the ball, smile on hit (12:49–13:49).

### 2.7 Third-person camera checklist (Nesky, Journey) [V14]

Use this checklist when the game has a 3D follow camera:
- **Pick the camera style:** for jams and small projects prefer fixed-angle or first person; a dynamic third-person camera is the hardest kind (6:34).
- **Representation:** orbit the avatar using yaw, pitch, distance and offset. Never pivot in place. Store Euler angles (8:41–10:43).
- **Occlusion:**
  - whisker raycasts swing the camera away early, so it never snap-zooms (a snap violates the 30° rule);
  - player input always wins; if the player turns toward an obstacle, ease the camera closer;
  - sphere-cast so the camera never sits inside geometry;
  - narrow columns may occlude briefly;
  - on hills, rise above the slope;
  - when backed into a corner, pull in (11:44–19:26).
- **Constraint priority:** resolve constraints per degree of freedom (yaw, pitch, roll, 3 offsets, FOV), not as competing forces. No general solver (14:52, 56:30).
- **Avatar collider:** make it wider than the mesh, so the near plane never clips the avatar against a wall (19:26).
- **Pitch drives distance and FOV:** derive both from pitch, like gears.
  - Looking up: glide down to a worm's-eye view and widen the FOV.
  - Looking down: pull out a little (20:27–23:58).
- **Auto-guidance:**
  - drift yaw behind the **velocity**, not the stick input;
  - pitch down ahead of cliffs and slopes using averaged raycasts ahead of the avatar;
  - align the critical axis (e.g. a catwalk) with the screen plane (29:12–33:05).
- **Rule of thirds:** slide sideways, and only while the player stands still. Re-centre while running (33:29).
- **Hints:**
  - designer hints help, but players can override them;
  - wait a short delay before a hint resumes;
  - turn hints off for experts;
  - for a nearby target, pull back instead of rotating; for a distant target, rotate (36:39–43:18).
- **Comfort options:**
  - invert axis;
  - S-curve stick response;
  - limit how far the avatar can drift from the screen centre;
  - wider FOV (a narrow FOV makes motion sickness worse);
  - avoid rapid FOV shifts;
  - screen shake and camera bob can be disabled;
  - no camera lock on jumps (wait for the landing);
  - ease into pitch limits (43:39–54:44).

## 3. "Never do" list (reason → evidence)

1. **Never ask Claude to "model X from scratch" with primitives and accept the result.** It yields primitive assemblies that "not really work" [V5 14:47]. Use a reference-driven
   brief plus a kit, or generated scaffolding plus retopology, or parts generation plus a bake [V3, V5, V12].
2. **Never trust a first-pass agent scene without checking it.** Expected defects: floating or overlapping objects, duplicate floors, off-centre parts, a material for every colour
   [V4 10:12–13:21; V12 0:21]. Run a numeric check (bbox, scale, floor contact) AND a human or screenshot review [V1 9:34–10:20].
3. **Never fix a sinking or floating asset by moving the node.** That hides a wrong origin [V1 4:38, 10:00].
4. **Never leave primitive segment counts at their defaults** in low-poly work: a default UV sphere is 960 tris [V1 1:37].
5. **Never ship a raw image-to-3D mesh.** Never "fix" it with Decimate alone, because textures distort [V3 2:23–3:05]. Bake to a fresh-UV low-poly instead.
6. **Never generate a complex asset as one piece.** The result is a joined mesh with blurry artifacts [V6 3:47–4:28].
7. **Never rely on AI PBR for metal or reflective surfaces** without a manual material pass [V6 9:31–9:52; V11 3:26].
8. **Never hard-code Blender MCP tool names.** They changed between versions [V1 8:08] [UNVERIFIED specifics].
9. **Never run the MCP add-on exposed beyond localhost, or with untrusted .blend files open** [V1 6:26–6:50].
10. **Never trust a headless Blender script's exit code** without `--python-exit-code 1` [V1 7:13].
11. **Never use translational camera shake in 3D.** It pushes the camera into walls and looks spastic [V8 7:22–9:05].
12. **Never use per-frame random for shake.** It breaks in slow motion and has infinite frequency [V8 12:41–13:41].
13. **Never mutate the base camera when shaking.** Shake a per-frame copy [V8 10:37].
14. **Never ship shake, bob or FOV-punch without an off or tune-down option.** Players got nauseous [V9 32:14; V14 50:12–51:57].
15. **Never snap the camera forward on occlusion, and never fight the player's camera input** [V14 11:44–14:10].
16. **Never overdo bloom, SSAO or contrast.** Push past the target, then dial back [V15 5:25, 13:13, 14:57].
17. **Never use pure-black shadows (strength 1.0) by default** [V15 5:05].
18. **Never write your own particle engine** for juice [V7 9:57].

## 4. Gaps and unverified items

- **Bot-check blocked (could not fetch):**
  - Imphenzia (hK5N_dTDMPw "Let's Model GAME ASSETS", DCEvFtrQCNw "Modular Dungeons");
  - Stefan 3D AI "Game-Ready Topology with AI? I Compared Best AI Tools" (3hagi51IxeY);
  - GDC "Fast, Cheap and Flashy: An Indie Art Direction Adventure" (rSk8adHotDA);
  - the original Dutch Game Garden upload of "Art of Screenshake" (AJdEqssNZ-U). I used the MSA re-upload (SkgkIXZ_13Y), which has the same 2650 s duration.
  - Effect: no Imphenzia-specific rules on modular kits, palettes or bevels. That is the biggest remaining modelling gap.
- **YouTube search hit HTTP 403/429** during the session, so the lighting search was cut short. I sampled one lighting video (V15, Unity URP). Its values (bloom
  threshold, shadow strength) are one developer's settings, not universal constants.
- **Captions are auto-generated.** Names were sometimes mangled ("Acrylic" = probably AccuRIG; "Chipo/triple P1" = Tripo P1; "full AI" = fal.ai) [UNVERIFIED mappings].
  Numbers were taken as spoken.
- **V1's claim about tool removal in "v2.1.9"** is unverified. V1 also does not make clear whether it refers to the community blender-mcp or the official add-on.
- **No video showed an LLM producing a good organic or stylized hero model by direct `bpy` modelling.** All good results relied on kits, generators plus baking, or
  technical tasks. Absence of evidence, not proof it is impossible [judgment].
- **Instagram (2 calls, not usable):** explore/tags/lowpoly → /popular/lowpoly/ (title "Lowpoly • 4.2M reels on Instagram") with no caption text in the
  HTML; the imphenzia profile → login redirect, HTTP 429.
- **Not watched:** frames and visuals (blocked). Any rule that depends on what is shown rather than said is absent.

## 5. Sources (videos used; credibility note)

| # | Video | URL | Credibility |
|---|---|---|---|
| V1 | Nik Bear Brown — Your First 3D Game Assets with Claude and Blender | https://www.youtube.com/watch?v=i-2NlEHaGjI | University course assignment (CSYE 7270); careful, process-focused, honest about unverified steps |
| V2 | Stefan 3D AI — Claude + Blender Is Insane Now — Full Free Setup | https://www.youtube.com/watch?v=wSY1kHXSap0 | Pro 3D artist / AI course seller; sponsored by 3D AI Studio |
| V3 | Building Aeon — Can Claude Fable Make AI Assets Game Ready? | https://www.youtube.com/watch?v=YwoPuZa8N_g | Indie dev; shows failures and iteration time and tokens honestly |
| V4 | Mammoth Club Tuts — Can AI Speed Up Low-Poly Modeling in Blender? | https://www.youtube.com/watch?v=QjTZaicpAaQ | Course-style tutorial; candid about defects |
| V5 | Max Novak — I connected Claude AI to Blender 3D (MCP) | https://www.youtube.com/watch?v=r7H60u0kHRA | 3D artist; early community MCP; candid limits |
| V6 | Stefan 3D AI — The Complete AI 3D Workflow for Indie Game Devs (2026) | https://www.youtube.com/watch?v=mmpLXA-xzrQ | Same creator as V2; sponsored; failure rates and limits still useful |
| V7 | Jonasson & Purho — Juice it or lose it | https://www.youtube.com/watch?v=Fy0aCDmgnxg | Canonical talk, authors' own channel (grapefrukt) |
| V8 | Squirrel Eiserloh — Juicing Your Cameras With Math (GDC 2016) | https://www.youtube.com/watch?v=tu-Qe66AvtY | GDC Math for Game Programmers tutorial, official GDC channel |
| V9 | Jan Willem Nijman — The Art of Screenshake (INDIGO 2013) | https://www.youtube.com/watch?v=SkgkIXZ_13Y | Canonical; Vlambeer co-founder; third-party re-upload (original AJdEqssNZ-U blocked) |
| V10 | Grant Abbitt — 3 Vital Tips to Improve Low Poly Work | https://www.youtube.com/watch?v=xOIQzgg5ebs | Long-standing Blender game-art educator |
| V11 | Creauctopus — How I Create Game Props Faster With AI (MCP Workflow) | https://www.youtube.com/watch?v=Hzb8CY3h1RQ | Indie dev; promotes Customuse |
| V12 | Opusgeo — I Let Claude + Unity MCP Build My Game Level. Then I Deleted It. | https://www.youtube.com/watch?v=1zMG3TAECH0 | Working 3D artist; short first-hand verdict |
| V13 | Vladimir (Cold Wild Games) — Aesthetic Driven Development (GDC) | https://www.youtube.com/watch?v=4m-_WTKd8rE | GDC talk, small studio; self-described "sample size of one" |
| V14 | John Nesky — 50 Game Camera Mistakes (GDC 2014) | https://www.youtube.com/watch?v=C7307qRmlMI | Journey's camera designer; official GDC channel |
| V15 | Kyle Banks — How to Create Beautiful Games in Unity | https://www.youtube.com/watch?v=1agSNKuAfTM | Shipped indie dev (Farewell North); plugs Patreon code |

Instagram probes: https://www.instagram.com/explore/tags/lowpoly/ and https://www.instagram.com/imphenzia/. Both unusable without login.
Transcripts: SCRATCH/downloads2/5/*.txt (cleaned) and *.vtt (raw).
