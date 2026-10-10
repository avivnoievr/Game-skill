# 05 — Raw timestamped notes per video (appendix to 05-videos.md)


## Working notes (raw, cited) — will be distilled below

### V1 Nik Bear Brown — "Your First 3D Game Assets with Claude and Blender" https://www.youtube.com/watch?v=i-2NlEHaGjI
- 1:25 budget ≤6 primitives, ≤500 tris. Blender 5.1 counts: cube 12 tris, default cylinder 124, default UV sphere 960; sphere at 12 segments × 6 rings = 120 tris -> "ask Claude to lower the segment counts".
- 3:55–5:04 write a BRIEF before building: name/role/where; size in metres justified vs player height/tile; origin at centre of base, built at world origin with base on floor; look (shape + material colours); tri budget; ≥3 predicted failures each with a check ("arrives lying on its side").
- 4:38 origin trap: origin in middle -> sinks half its height; lifting the node hides the bug; check the origin itself.
- 6:26–6:50 safety: add-on runs Claude-written Python unguarded; keep port on localhost; save first; disable add-on when unused; don't open untrusted .blend while server runs.
- 6:58–7:18 fallback after ~2 h failing to connect: script route `blender -b --factory-startup --python script.py --python-exit-code 1` (without exit code flag Blender exits 0 on script error).
- 7:30–8:08 prompt pattern: plan first; start with get_scene_info and say what's in scene; propose steps, don't build yet; after approval ONE execute_blender_code call per object; after each, report location/size/rotation/scale; apply rotation & scale before finishing; forbid model downloads & AI generation tools; end with "say what you could not verify".
- 8:08–8:20 tool names drift: course-recorded version had get_object_info, get_viewport_screenshot, export_scene; "by 6 Oct, version 2.1.9 had removed all three and added a tool called look" [said in video; not independently verified].
- 8:20 "Look at it yourself in the viewport after every step. Claude can't tell you whether it looks right."
- 8:38 save every execute_blender_code body into a script per asset (git history); save .blend; don't commit .blend1.
- 8:54–9:20 export GLB with +Y up on (default); newer MCP has no export tool -> File>Export glTF 2.0 or run exporter via execute_blender_code.
- 9:34–10:20 headless check script: bbox size, node scale must be (1,1,1), upright axis; place on floor without moving -> sits/sinks/floats; tri count via Scene Statistics. "A check can prove less than it claims" — agent's floor check hit the object's own collider and proved nothing.
- 12:10 "A passing check shows ... size, orientation and scale ... It doesn't show they look right in your game. That judgment is yours."
- Credibility: university course (Northeastern-style course code CSYE 7270) assignment video; deliberately beginner-level (primitives only).

### V2 Stefan 3D AI — "Claude + Blender Is Insane Now — Full Free Setup" https://www.youtube.com/watch?v=wSY1kHXSap0
- 0:40–1:41 official Blender MCP add-on (Blender 5.1), drag-drop install, auto-starts; Claude Desktop: Connectors > add "Blender"; restart Claude fully after installing connector/skill.
- Use cases shown working in one prompt: bake high->low normal + AO and wire into shader (7:23–8:23); geometry-nodes scatter of 4 plant variants over terrain with density control (8:44–10:06); split keyboard by loose parts (66 keys) + wave drop animation (10:46–11:28); procedural "pearl chameleon" car paint = color ramp + layer weight (11:48–12:08); toon shader + outline modifier (12:28); LOD chain decimating mesh AND resizing textures 4K->1K->512 (12:48–13:30).
- 11:07 "It not necessarily does it right, but it can give you some ideas" (beginner caveat). 7:03 Tripo P1 generated parts "position a little bit off".
- Credibility: AI-3D YouTuber who sells a course; sponsored by 3D AI Studio (5:22) -> treat tool praise as promotional.

### V3 Building Aeon — "Can Claude Fable Make AI Assets Game Ready?" https://www.youtube.com/watch?v=YwoPuZa8N_g
- 0:41 concept image first (palette/style), then split into a matrix of individual buildings/props as references -> visual consistency.
- 1:02–1:22 Tripo smart low-poly on a complex house: holes, missing chimney chunk, warped texture. "smart poly works really well for smaller props and simpler objects".
- 1:43–3:05 highest-quality gen = >1.8M tris; Blender Decimate ratio 0.02 -> ~37k tris but textures distorted + artifacts -> "this approach clearly was not going to work".
- 4:07–5:08 Claude via Blender MCP: duplicate, fresh Smart UV Project on low-poly, bake high->low; uses screenshots to judge; first pass "pretty disappointed ... distortion ... gaps".
- 5:28 after several feedback passes (~28 min) -> 39k tris acceptable; then 6:10 asked Claude to turn what it learned into a reusable Python script (target tris, texture sizes); 7:11 batch of 8 houses all <40k, 8K baked colour + normal map. Session ~2 h, 48 min API time, ~130k output tokens, ~300 lines Python (7:53).
- 8:55–9:39 smart-poly props ~4–5k tris each; generate 2–6 props in one image/model then split in Blender (fewer paid gens).
- 8:14 & 12:03 "AI-generated assets aren't quite production-ready right out of the box"; best results = AI models + existing asset packs (terrain, foliage, lighting) + cleanup.
- Credibility: small indie dev channel; shows failures honestly; no sponsor disclosed in transcript.

### V4 Mammoth Club Tuts — "Can AI Speed Up Low-Poly Modeling in Blender?" https://www.youtube.com/watch?v=QjTZaicpAaQ
- 0:21–3:51 official Blender connector: Claude Settings > Connectors > Blender (install), add-on from blender.org/lab/mcp ("MCP server"), Install from Disk, port 9876, Save Preferences, quit & restart Claude after any skill/connector install. Connector permission "needs approval" vs "always allow" (1:07).
- 5:39–9:31 prompt pattern: paste several low-poly reference images ("the more images ... the more it can see"), ask it to use references and either ask you questions first or "do its best" then iterate; ask for further suggestions.
- 10:12–13:21 first pass failures: "tents aren't in the middle", "floating land", "two floors", "a bunch of floating assets", tents off-centre from their beams; second prompt lists each defect explicitly + adds content.
- 13:42–18:53 "everything's not placed too great"; after ~3 prompts a "pretty decent start", then manual fixes: move/rotate/scale props, rebuild a poor vulture, duplicate fixed tree instead of fixing each copy, sink bones into ground, close holes (F), change colours. Lesson: AI blockout + human polish.
- Credibility: course-style tutorial channel; honest about defects.

### V5 Max Novak — "I connected Claude AI to Blender 3D...Mind-Blowing Results (MCP)" https://www.youtube.com/watch?v=r7H60u0kHRA
- 14:47–15:07 "If you try and tell it to model something from scratch ... it's going to try and build it from primitive objects and not really work." Also "issues with ... animation ... geometry nodes. Keep your expectations in check."
- 0:41–4:03 & 7:49–8:09 better pattern = KIT ASSEMBLY: agent picks from pre-made models/materials and assembles "like a puzzle"; works because each part has metadata (JSON in object custom properties) the agent reads; only colours/color-ramp changed on pre-made procedural materials (noise -> bump detail).
- 6:27–7:08 ask agent to rename cube.007 etc. to semantic part names from position/dimensions ("laces", "tongue", "collar foam").
- 9:10–10:39 lighting variants per mood as duplicated collections; it even wrote a mini add-on, but "the more in-depth you go, the more you're going to have to tinker" (HDRI switching bug).
- Credibility: 3D artist/YouTuber; early (2025) community blender-mcp install via uv + addon.py.

### V6 Stefan 3D AI — "The Complete AI 3D Workflow for Indie Game Devs (2026)" https://www.youtube.com/watch?v=mmpLXA-xzrQ (sponsored by 3D AI Studio, 6:09)
- 3:47–4:28 generating a whole asset at once gives "blurry stuff ... mesh is joined ... artifacts" — "your approach was absolutely wrong": split into parts, generate each individually, combine (control, animation, removable accessories). 4:28 "10, 20% it will fail even with the newest" model.
- 3:47 realistic: generate high-poly then retopologise (AI or manual). 5:29 RetopoFlow add-on on AI mesh ~5 min to game-ready.
- 6:49–9:52 AI colour textures good; AI PBR "sort of weak", metals/reflective surfaces average -> finish materials in Substance Painter.
- 9:52–10:54 don't generate geometry for walls/floors: use seamless tileable textures (+normal map). 9:10 trees = roots/base/branches separately + alpha-card leaves. 10:54 water/dynamic assets won't work (logic/particles).
- 7:29–8:09 auto-rig (AccuRIG [transcribed "Acrylic"], Mixamo) gives a base; weight fixes inevitable; hair bones/hair cards not solvable by AI.
- 17:18 "If you're gonna try shitty MCP or some paid solution, it most likely will work very bad".

### V7 Jonasson & Purho — "Juice it or lose it" (2012) https://www.youtube.com/watch?v=Fy0aCDmgnxg
- 0:40 definition (quoting Gamasutra "How to prototype a game in under 7 days"): "A juicy game feels alive and responds to everything you do – tons of cascading action and response for minimal user input." 1:21 "maximum output for minimum input".
- 2:03 step 1 = colour (tell good guys from bad guys). 3:46 cheap ease: move x 10% of the remaining distance each frame (note: frame-rate dependent; round-1 already gives the dt-correct form).
- 4:07–5:07 tween block entry: position with ease-out, then overshoot ("go slightly past our target"), bounce; also tween rotation & scale; "add a little bit of delay, a random delay to everything" (staggered entrance).
- 5:49–6:51 paddle stretch from pointer offset; ball: scale-up on hit then ease back, rotate toward travel direction, stretch by velocity, wobble on hit, flash WHITE on hit then return.
- 7:12–7:32 on hit, all blocks do a small scale tween ("jelly"); bouncy lines when hit.
- 7:32–9:14 sound = "the most cost-effective thing you can add"; Swink Game Feel demo: two circles passing through each other appear to bounce once a sound is added; music turns demo into "a real game".
- 9:36–11:44 particles: smoke puff on hit; destroyed block falls with gravity, gets pushed by the ball, spins, DARKENS so it doesn't blend with live blocks; shatter (expensive, "no one can tell"); confetti on paddle; ball trail from position history. "Don't write your own particle engine — trap for programmers; use an existing one."
- 12:05–12:49 screen shake on ball hit: tennis ball -> "helmet"; cranked up -> "freight train mode"; "with great power comes great responsibility" (use with care).
- 12:49–13:49 Kyle Gabler trick: add eyes (blink = hide eyes briefly), look at ball, smile on hit (scale Y), frown when ball far; "bigger eyes" better.
- Credibility: canonical talk (Nordic Game Indie Night 2012) by the Juicy Breakout authors; official grapefrukt channel.

### V8 Squirrel Eiserloh — "Math for Game Programmers: Juicing Your Cameras With Math" (GDC 2016) https://www.youtube.com/watch?v=tu-Qe66AvtY
- 3:25 "camera shake is a lot like salt": none = landings don't feel hard; too much = nauseating.
- 3:46–4:28 separate `trauma` variable; big hit +0.5, small stress +0.1–0.2; trauma decreases linearly over time (time-based); shake = trauma² or trauma³ (not linear). 5:10–6:38 why: spring-like realism, minor/moderate/major distinguishable, stacked minor hits escalate; linear trauma "stops very suddenly".
- 6:38–7:22 2D: translational + rotational combined feels best. 7:22–9:05 3D: rotational only — translational looks spastic near geometry, barely moves distant objects, and pushes the camera INTO WALLS. 9:30 VR: don't shake at all.
- 9:54–10:37 code: angle = maxAngle·shake·noise(−1..1) (e.g. maxAngle 10°), offsetX/Y = maxOffset·shake·noise; apply to a SHAKY COPY of the base camera each frame — never mutate the base camera. 3D: separate yaw/pitch/roll amplitudes, tweak individually.
- 11:37–14:44 use Perlin/smooth noise, not random: random = infinite frequency, breaks in slow motion; noise is coherent, frame-rate independent, works with time scale, adjustable frequency (slow noise = handheld-camera effect), reproducible; use DIFFERENT seeds per channel (yaw/pitch/roll/x/y) or they move in lockstep.
- 15:45–17:35 asymptotic averaging x += (target−x)·k: k 0.01 "really slow", 0.10 "reasonably fast", 0.50 "quite fast"; near-instant convergence "starts feeling like it's just snapping". Smooths stair pops.
- 19:17–20:19 treat axes separately: follow horizontally always, vertically only when player LANDS (no camera bob on jumps); can be lazier going up than down; follow TIGHTLY when player falls. 20:42 make it time-scaled (framerate-dependent otherwise).
- 21:43–22:25 never lose sight of the player (primary focus); secondary focus (lock-on target) keep on screen if possible, drop it before the player. 22:47–25:33 points of interest (treasure, levers, secret doors, designer markers): bias camera subtly; feather influence e.g. 0 interest beyond 10 tiles, ramp up between 10 and 5 tiles; weight = closeness × importance; weighted average of all POIs; avoid heavy-handed dip-and-return.
- 25:33–26:34 co-op framing options all intrusive (block, off-screen, kill, teleport, drag, zoom out); fixed split wastes screen 95% of the time -> Voronoi dynamic split (Lego Star Wars): split perpendicular to the line between players at the midpoint, re-centre each player, feather the merge to avoid a snap (27:18–29:44).
- Credibility: GDC Math for Game Programmers tutorial, official GDC channel; slides at essentialmath.com.

### V9 Jan Willem Nijman — "The Art of Screenshake" (INDIGO Classes 2013) https://www.youtube.com/watch?v=SkgkIXZ_13Y (re-upload; Dutch Game Garden original AJdEqssNZ-U was bot-blocked)
- 7:02 retitled "30 tiny tricks that will make your action game better". 8:27 basic animation + sound first (sfxr).
- 8:48–9:54 lower enemy HP; higher rate of fire; more enemies with less HP each ("tiny differences ... feels better").
- 9:54–10:57 bigger bullets ("at least like the size of your chest"; tiny dots = beginner mistake); muzzle flash = first frame of bullet sprite drawn as a circle; faster bullets; 10:57 less accuracy (spread) "so it looks different every single time".
- 11:38–12:20 impact effects on walls/enemies; hit animation = white flash. 12:20–12:43 enemy knockback "a couple of pixels" -> creates dynamic combat.
- 13:03–14:24 PERMANENCE: corpses, rubble, props that react to misses; "computers ... could just put a million corpses in there". 20:26 shells stay forever.
- 14:24–16:29 camera lerp (slight lag); camera shifts AHEAD toward where you aim ("the game is about shooting things in front of you"); Luftrausers: camera dips toward nearby water and toward the centroid of bullets so off-screen threats become dodgeable.
- 16:29 screen shake; 16:52–17:37 player knockback when firing = "give someone a reason to not press" the fire button.
- 17:59–18:41 "sleep": pause game ~20 ms at impact on hit and on death — "your brain won't notice" but impact registers.
- 19:23 gun lags/kicks back when firing; 24:00 gun kick "just like three pixels". 21:34–22:37 more bass: anecdote — Raven dev boosted gunshot bass +12 dB and investors said the gun now "feels good".
- 23:39 random explosions: 33% chance enemies explode on death. 25:53 camera kick: move camera back opposite to firing direction (plus shake).
- 26:54–27:35 "make really big explosions" (Cactus); explosion = circle flashing black->white; 27:35 smoke that lingers after battle.
- 28:17–29:28 "meaning": enemies must be able to kill you; death in slow motion (dropped to 10 fps), then speed back up.
- Q&A 32:14–32:35: had to add an option to DISABLE screen shake in Nuclear Throne — some players got nauseous; designers get used to shake and stop noticing ("don't put things in your game that hurt people physically"). 31:33 "you're the worst playtester in the world" — get other people. 35:29 "we make our games in a couple of days and then we spend the year polishing them".
- Credibility: canonical talk, Vlambeer co-founder (Nuclear Throne, Luftrausers).

### V10 Grant Abbitt — "3 Vital Tips to Improve Low Poly Work" https://www.youtube.com/watch?v=xOIQzgg5ebs
- 0:40–1:41 references: Pinterest boards; search the REAL object as well as stylized/low-poly versions — "don't go straight for the stylized art".
- 2:01–4:05 silhouette: sketch many thumbnails, iterate (too far -> pull back to in-between), fill final shape black; "if your silhouettes look good your objects are probably going to look good"; for low poly the silhouette is "all important" because flat colours and no fine detail.
- 4:26–6:09 add "character": small notches/nicks via Ctrl+B bevel on an edge + edge-slide (GG) with Auto Merge, or knife (K); gives the object a story (battle damage).
- Credibility: long-running Blender game-art educator (Gabbitt), large following, courses.

### V11 Creauctopus — "How I Create Game Props Faster With AI (MCP Workflow)" https://www.youtube.com/watch?v=Hzb8CY3h1RQ (promotes Customuse; link in description)
- 1:01 mood images in a Claude project -> 2D prop images (OpenArt) in a consistent style first.
- 1:21–2:03 Claude Code drives Customuse MCP -> Tripo: "create four different views [from the image], then based on those views create a quad mesh with 500 polygons, and [unwrap] it, then generate the texture"; confirm first prop looks good, then batch the rest; hero/complex prop (broken car) given 15,000 polys; ~5–7 min per prop.
- 3:06–3:47 "it's not always game ready right away": PBR maps had to be recreated, normal map made from texture, colour variants in Photoshop, fence net = planes with transparent texture in Blender; for more control (poly count, UV layout) uses the generator directly.

### V12 Opusgeo (Rock) — "I Let Claude + Unity MCP Build My Game Level. Then I Deleted It." https://www.youtube.com/watch?v=1zMG3TAECH0
- 0:21 failures: objects overlapped, areas hard to read, ~30 materials created "mostly just to give individual objects different colors".
- 0:43 "Fixing that scene felt like fixing a bad AI generated mesh ... making it again gives you more control and ... less time."
- 1:03–1:45 better: concept image -> rough generated 3D mesh used ONLY as scaffolding/reference; place own placeholders over it one by one -> proper prefabs + a single texture atlas instead of 30 materials; scaffold "comes out before anything ships".
- 1:45–2:05 "Coding is where I get the most value from AI ... With 3D it's the opposite. Explaining every visual and technical decision takes longer than just doing it myself."
- Credibility: working 3D artist making a commercial physics game; short but first-hand.

### V13 Vladimir (Cold Wild Games) — "Aesthetic Driven Development: Choosing Your Art Before Making a Game" (GDC) https://www.youtube.com/watch?v=4m-_WTKd8rE
- 4:11–6:19 score each art candidate on 4 criteria: (1) the team likes it, (2) audience response vs a measured baseline, (3) EASE OF CREATION — can a 2-person team make hundreds of assets in it, (4) game-design constraints the style implies.
- 7:01–9:26 rejected: isometric + heavy detail (unaffordable), high-res/detailed ruins; liked-but-generic images "you would probably not remember".
- 10:31–11:12 chosen style: unique AND "consists of small replicable geometric shapes that you can use for other ... buildings or the world".
- 14:18–16:42 art style constrains gameplay: only 6–7 buildings fit per screen -> designed around it (map as glue).
- 20:32 next time: set art constraints up front (e.g. max sprite size).
- Credibility: GDC talk by small-studio founder; self-described "sample size of one" (21:56).

### V14 John Nesky — "50 Game Camera Mistakes" (GDC 2014, Journey) https://www.youtube.com/watch?v=C7307qRmlMI
- 1:03 "cameras are most noticeable when they fail". 6:34 #1 don't use a dynamic 3rd-person camera when another works — "for student projects, game jams ... pick an easier camera style such as first person or fixed angle" (Mario 3D World / Link Between Worlds reverted to fixed angles).
- 7:37 #2 design levels and camera together. 8:41 #3 store camera as orbit around avatar: yaw/pitch (Euler) + distance + lateral/vertical offset, not global XYZ/quaternion; camera pivots around the avatar "like a moon", never in place.
- 10:43 #4 keep default distance short enough to preserve line of sight. 11:44–12:48 #5 don't snap closer on side occlusion (a cut that violates the 30° rule); cast "whisker" rays and pre-emptively swing away. 13:09–14:10 #6 always honour player's camera input; if player swings toward an obstacle, gradually pull closer instead. 14:32 #7 sphere-cast so the camera never ends inside geometry.
- 14:52–16:15 #8 don't let forces compete: organise constraints per degree of freedom (yaw, pitch, roll, 3 offsets, FOV = 7 DOF) and prioritise per axis (player input highest on yaw).
- 16:15–17:59 #9–10 tag narrow columns as allowed to break line of sight briefly, but sphere-check so they never intersect the camera. 17:59 #11 hills: rise above, don't swing sideways (check surface normal). 18:42 #12 backed into a corner: ray behind camera -> pull closer, don't swing.
- 19:26 #13 near-plane clipping into avatar: make avatar collision radius wider than the mesh so the camera fits between avatar and wall.
- 20:27 #14 distance varies with pitch: smooth curve gliding to worm's-eye at feet looking up; pull OUT a bit when looking down (less claustrophobic). 21:51 #15 widen FOV when looking at the sky. 22:34 #16 derive distance AND FOV from pitch together "like gears" (else avatar grows/shrinks); other modifiers multiply a base.
- 23:58 #17 cut only when passing through opaque surfaces. 24:43 #18 cuts remap controls — give a safe moment/transition. 25:45 #19 show landmarks after cuts. 27:07 #20 180° rule (cutscenes). 28:10 #21 show ground at the avatar's feet and far goals too.
- 28:31 #22 don't rely on players steering the camera ("patting your head and rubbing your belly") — auto-guide. 29:12 #23 drift yaw behind the avatar using VELOCITY, not stick direction (don't show the wall/invisible wall).
- 30:13 #24 align the axis the player must judge (e.g. catwalk) with the screen plane — depth is hard to judge. 31:37 #25 ray down ahead of avatar; pitch down near cliffs. 32:41 #26 pitch with slope using averaged ray-cast ahead, not the noisy ground under feet.
- 33:29 #27 rule of thirds by sliding sideways (not rotating) and only while standing still; re-centre while running (players aim by screen centre). 35:36 #28 separate logic per locomotion mode; when flying/jumping show the landing spot.
- 36:39 #29 add designer "camera hints" (scripted targets), esp. in small closed spaces. 38:25 #30 avoid getting lost without arrows: at world boundary spin camera back toward the goal; detect backtracking.
- 39:27 #31 nearby target: pull back/slide to include it, don't rotate (Arkham spinning). 40:29 #32 distant target: rotate. 41:10 #33 tilt down slightly to see over the avatar's head.
- 41:33 #34–36 let players override hints; after player camera input, delay before hints resume; disengage hints for experts.
- 43:39 #37 provide invert-axis option (Journey's only control option). 44:20 #38 avoid accidental inputs (gyro). 45:24 #39 S-curve stick response for slow fine control. 46:24 #40 limit how far the avatar can drift from centre with a lazy camera; look-ahead in run direction.
- 47:27–49:32 #41 small FOV makes motion fast -> simulation sickness; zoom out more; FPS: offer/expand FOV. 49:32 #42 rapid FOV shifts (scope zoom, boost FOV) trigger sickness. 50:12 #43 screen shake: offer a setting to tune down/turn off (TowerFall). 51:16 #44 walk-cycle camera bob: allow disabling. 51:57–53:00 #45 don't lock camera vertically to jumps; wait until landing on a higher surface; rubber-band vertical motion.
- 53:00 #46 fast smooth transitions are as jarring as cuts. 53:40 #47 ease pitch speed down before the pitch limit. 55:27 #49 test with broad demographics; testers hide motion sickness. 56:30 #50 don't write a general constraint solver — unpredictable, can't be designed; understand and prioritise constraints.
- Credibility: Journey camera designer (thatgamecompany), official GDC channel.

### V15 Kyle Banks — "How to Create Beautiful Games in Unity" https://www.youtube.com/watch?v=1agSNKuAfTM (dev of Farewell North; plugs Patreon code bundle)
- 1:01 realism is easier to keep consistent with asset/CC0 textures (ambientCG); 1:22 stylized = more intentional work (2 years to nail Farewell North's style), but can mask artistic limits.
- 2:03 detail-map noise overlay to break tiling + mask for dirt at wall bottoms; 2:43 height/parallax + AO maps from ambientCG.
- 3:23–4:05 decide the EMOTION first; "lighting does a lot to convey emotion". 4:05 sun through window at an angle for light shafts; warm orange directional light.
- 4:25 bake indirect lighting; reduce skybox intensity for interiors. 5:05 "a lot of devs make the mistake of leaving the shadow strength at 1" -> ~0.9 (pitch black on players' screens otherwise).
- 5:25 add SSAO to ground contact points; "really easy to go too far".
- 6:26–10:11 ray-marched volumetrics: add per-pixel noise (jitter) to hide step banding, run at 1/2–1/8 resolution + blur, tie to quality tiers; fallback = light cards.
- 10:32–11:32 SHADOW CARDS: black semi-transparent gradient plane (unlit, soft particles) under/behind furniture to ground it; warm orange LIGHT CARDS in windows; fade cards as camera approaches.
- 12:13 colour theory: complementary blue/orange pair. 12:53–14:15 grading recipe: ACES tonemapper; contrast and saturation "go way too far, then dial it back"; shadows/midtones/highlights: raise midtones slightly, lower shadows slightly.
- 14:15 soft, low-intensity vignette. 14:36–15:18 bloom: threshold ~0.25 (per his settings), "one of the biggest mistakes ... they go way too far with the bloom ... less is more"; downscale to half res, 4–5 iterations.
- 15:39 very subtle film grain: also hides colour banding after stream/YouTube compression. 16:59 sad mood = lower contrast + bluer hues.
- 17:19 mirrors need a baked reflection probe. 18:20–20:42 life: dust particles around camera; curtains swayed by a sine-wave vertex shader masked by vertex colour; shadow-only spinning capsules outside window fake a bird flock (two groups, different speeds).
- 21:03 "keep it simple and lean into the constraints ... until you really need the added complexity".
- 21:24–23:06 stylized scene (Control-inspired): one small COLOUR-PALETTE TEXTURE for the whole world (unwrap UVs into swatches; no per-object textures), multiplied by world-space triplanar noise + planar normal grit; one shader -> single batch; 7 texture samples total.

