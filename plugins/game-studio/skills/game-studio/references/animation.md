# Animation and game feel

Contents: 1. Principles in games · 2. Easing by intent · 3. Game feel (juice) · 4. Springs and dampers ·
5. Locomotion without foot sliding · 6. Blending and state machines · 7. Pipeline: rig → clips → engine ·
8. Animation QA

## 1. Principles in games

- **Responsiveness beats realism for player actions.** The player must see a reaction to input within
  about 100 ms (Swink's correction cycle). Put weight into follow-through and recovery, not into
  wind-up delays before the action happens.
- **Enemies get full anticipation.** A telegraph is how the player learns to react. A readable wind-up
  is a gameplay feature, not decoration.
- **Cancel windows:** let players interrupt recovery into dodge or jump at defined frames, with input
  buffering (≈ 100–150 ms) so presses just before the window still count.
- **The 12 principles still apply.** In games the ones that carry the most weight are:
  - anticipation;
  - follow-through and overlapping action (hair, cloth, tails and weapons settle after the body);
  - slow-in/slow-out (easing);
  - arcs (limbs move on curves, not straight lines);
  - squash and stretch (stylized games);
  - secondary action;
  - timing (frame counts sell weight).
- **Readability:** a pose must read in silhouette, so check the pose strip as silhouettes for key
  attacks.

## 2. Easing by intent

| Intent | Easing |
|---|---|
| Arrivals, settling, UI enter | ease-out (cubic/quad); emphasized `cubic-bezier(0.05, 0.7, 0.1, 1)` |
| "Pop" in, pickups, score punch | back / overshoot (easeOutBack) |
| Wind-up, exits, UI leave | ease-in (`cubic-bezier(0.3, 0, 1, 1)`) |
| Camera moves, menu slides | ease-in-out (sine) |
| Constant mechanical motion (conveyor, rotor) | linear, and only here |
| Cartoon bounce | elastic/bounce, sparingly |

Durations:
- UI micro-reactions 100–200 ms; panels 250–400 ms; scene transitions 450–600 ms.
- Gameplay feedback must finish fast enough to never block the next input.

## 3. Game feel (juice)

A satisfying hit is 5–8 small responses inside about 100 ms, all returning to rest. Scale feedback to
importance. Juice on everything is noise.

| Event | Response (starting values; tune by feel) |
|---|---|
| Pickup | Item pop (scale 1.2 → 1, ~120 ms easeOutBack) + HUD punch + chime + trauma 0.15 |
| Light hit | Hitstop ~40 ms + trauma 0.3 + hit flash (1–2 frames white/tint) + small knockback |
| Heavy hit | Hitstop ~70 ms + trauma 0.4 + flash + particles + rumble |
| Explosion | Hitstop ~90 ms + trauma 0.7 + brief full-screen flash (≤ 120 ms) + FOV +8° decaying ~200 ms |
| Jump / land | Stretch ≈ 1.15 on takeoff, squash ≈ 0.9 on landing, back to 1 over ~180 ms (easeOutBack); dust puff on land |

**Trauma screenshake** (Eiserloh's model):
```ts
trauma = Math.min(1, trauma + amount);                 // per event
const shake = trauma * trauma;                         // squared: small events stay subtle
camera.rotation.z = maxRoll * shake * noise(t * 25);   // smooth noise, NOT Math.random per frame
camera.position.x += maxOffset * shake * noise(t * 25 + 100);
trauma = Math.max(0, trauma - decayPerSecond * dt);    // ~1.2–1.4 per second
```
- In 3D, rotational shake reads best.
- Apply shake on top of the follow camera, never to the simulated body.
- Ship a "reduce screen shake" option.

**Hitstop:**
- Scale the *gameplay* delta to about 0.05 for 40–90 ms on heavy hits only.
- Rendering, camera, tweens and HUD keep using the real delta, so the freeze reads as impact, not lag.
- Input still registers during hitstop.

**Squash and stretch** preserve volume: scale Y by `s`, and X and Z by `1/√s`.

The full juice checklists from the classic talks ("Juice it or lose it", "The Art of Screenshake"),
for the playtest-qa feel pass:
- tween-in of spawned things;
- impact particles;
- hit flashes;
- knockback (enemy and player);
- permanence (debris, shells and decals stay a while);
- camera lerp and look-ahead;
- camera kick opposite to firing;
- a brief sleep frame on impact;
- bass in impact sounds;
- muzzle flash;
- death animations;
- trails on fast objects.

## 4. Springs and dampers (frame-rate independent)

Never `x = lerp(x, target, 0.1)` per frame. It converges at different speeds at 30, 60 and 144 FPS.

```ts
// Half-life damper: covers half the remaining distance every `halfLife` seconds, at any frame rate.
const damp = (x: number, target: number, halfLife: number, dt: number) =>
  x + (target - x) * (1 - Math.pow(2, -dt / halfLife));

// Critically damped spring (smooth follow with velocity; no overshoot)
function springDamper(x: number, v: number, target: number, halfLife: number, dt: number) {
  const y = (4 * Math.LN2) / (halfLife + 1e-5) / 2;   // damping
  const j0 = x - target, j1 = v + j0 * y, e = Math.exp(-y * dt);
  return { x: e * (j0 + j1 * dt) + target, v: e * (v - j1 * y * dt) };
}
```
(Damper forms after Daniel Holden's "Spring-It-On" articles.)

**Secondary motion:**
- Use springs on antennae, tails, ears, cloth tips and held items.
- Engine primitives:
  - Godot 4.4+: `SpringBoneSimulator3D`, `LookAtModifier3D`, `RetargetModifier3D`.
  - Godot 4.6+: `TwoBoneIK3D` (`SkeletonIK3D` is deprecated).
  - three.js: `CCDIKSolver`; spring bones via `@pixiv/three-vrm` for VRM rigs.

## 5. Locomotion without foot sliding

Foot sliding is a speed mismatch between how fast the character object moves and how fast the clip's
feet move.

1. **Measure each clip's root speed.** Reference: walk ≈ 1.75 m/s, run ≈ 4 m/s for adult mocap.
   Measure your actual clips.
2. **Drive playback rate and blend weights from the actual speed:** a 1D blend space of
   idle/walk/run keyed by speed, with playback scaled to match.
3. **Synchronize vs. data-driven:**
   - Moving the character purely by simulation is responsive but slides when the data mismatches.
   - Root motion doesn't slide but feels sluggish.
   - The middle ground: **adjust** the character toward the simulation with a damper, and **clamp**
     the maximum deviation.
4. **Foot locking with two-bone IK** is the last resort for the remaining slip.
5. Keep turn-rate responsiveness moderate. Very high rotation responsiveness makes characters spin
   on the spot.

## 6. Blending and state machines

- Model character animation as a state machine with explicit transitions, synchronized with the
  gameplay state machine (`architecture.md` §4). Never pick clips from scattered booleans.
- Crossfade durations:
  - 0.1–0.25 s for gameplay transitions;
  - shorter for starts, stops and turns;
  - longer only for calm state changes.
  - The 0.5–5 s values in library demos are not gameplay values.
- **three.js:**
  ```ts
  next.enabled = true; next.setEffectiveTimeScale(1); next.setEffectiveWeight(1); next.time = 0;
  current.crossFadeTo(next, 0.2, true);               // warp=true matches cycle speeds
  mixer.update(dt);                                   // every frame, real delta
  ```
  - For cycles, crossfade at the loop boundary (the mixer 'loop' event).
  - Additive layers (breathing, recoil) use `AnimationUtils.makeClipAdditive`.
  - `THREE.Clock` is deprecated since r183; use `THREE.Timer`.
- **Godot:** `AnimationTree` with a StateMachine.
  - Transitions use Xfade Time and a non-linear Xfade Curve.
  - BlendSpace1D/2D for locomotion; OneShot with filters for upper-body actions.
  - Advance Expressions read gameplay state.
  - Use the root-motion track when using root motion.
- **Unity:** Animator with blend trees for locomotion. Keep transitions short (the default 0.25 s is
  long for actions) and turn off Exit Time for interruptible actions.
- **Pops on abrupt transitions:** inertialization ("dead blending") extrapolates the outgoing pose
  instead of snapping.

## 7. Pipeline: rig → clips → engine

1. **Choose the route** (`modeling.md` §2 decides the character source):
   - CC0 rigged packs come with clips. Check the clip list against the design.
   - Humanoids can be auto-rigged and animated with Mixamo by hand. It has no official API, and
     automating it carries terms-of-service risk.
   - Generated characters: Meshy auto-rig is humanoid-only; Tripo offers creature rig types.
   - Custom rigs are scripted in Blender.
2. **In-place vs. root motion:** decide per clip at download or export, and match the engine-side
   approach (§5).
3. **Blender → glTF export traps:**
   - An action that is neither active nor stashed on an NLA track **is not exported**. Put each
     action on its own track; the track name becomes the glTF animation name.
   - Since Blender 4.4, actions are slotted, and tracks merge by action, not by name.
   - Enable "Reset pose bones between actions" when not every bone is keyed in every clip.
   - Keep sampling on. Unsampled export can produce wrong curves.
   - Use "Set all glTF animation starting at 0" for loops.
   - "Export deformation bones only" bakes the animation. Check the result.
4. **Naming:**
   - Clips are `Idle`, `Walk`, `Run`, `Jump_Start`, `Jump_Loop`, `Land`, `Attack_Light`, never
     `Armature|mixamo.com|Layer0`.
   - Mixamo bone prefixes (`mixamorig:`) must be consistent across all clips that share a skeleton.
5. **Skinning limits:** at most 4 influences per vertex, and bone counts reasonable for the platform
   (`inspect_model.py` warns).
6. **Clip events** (footstep, hit-frame, VFX spawn) are defined in data, at frame numbers recorded in
   the asset report. Gameplay listens to them; it doesn't guess timings.

## 8. Animation QA (agent-runnable)

A still image cannot prove animation quality. Every check below uses motion evidence.

1. **Pose strips per clip:** `render_views.py MODEL --anim <Clip> --anim-steps 8 --out ...`. Check:
   - contact and passing poses;
   - arcs;
   - silhouette clarity of key poses;
   - loop closure (the first and last poses match);
   - no bind/T-pose frames.
2. **In-game sequences:** `capture.mjs --sequence 12 --step-ms 50 --hold KeyW` (or the engine
   equivalent). Check:
   - transitions without pops;
   - feet planted while in contact;
   - camera smoothness.
3. **Foot skate (numeric):** log world-space foot positions per frame. Flag frames where a foot lower
   than 5 cm slides more than 2.5 cm horizontally, and report the skate ratio over contact frames.
   Thresholds are heuristics; tune per game.
4. **Pops:** per-bone angular velocity spikes above ~3× the clip median inside a transition window.
5. **Loop seam:** for looping clips, the first and last pose (and their velocities) match within a
   tolerance.
6. **Bind-pose leaks:** no visible frame equals the bind pose after spawn, load or transitions.
7. **Frame-rate independence:** run the simulation at fixed dt 1/30, 1/60 and 1/144. Camera, follow
   and damper positions at t = 2 s must match within epsilon. Search for `lerp(` with a constant and
   for `Math.random` in feel code.
8. **Speed match:** simulation speed versus clip stride speed; playback rate tracks it.
9. **Juice sanity:**
   - shake returns to zero;
   - input works during hitstop;
   - no effect hides the next threat;
   - a reduce-motion/shake option exists.
