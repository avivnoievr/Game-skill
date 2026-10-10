# Level design: traversal contracts before decoration

Choose one authoring source: engine scenes, versioned level data, or Blender layout + named markers/
extras. Record the choice and coordinate/import rules in an ADR; do not maintain competing layouts.
Treat gameplay metrics as config and test inputs, not numbers copied from real-world architecture.

## Greybox contract

| Input | Required decision / evidence |
|---|---|
| Player controller | Capsule/vehicle bounds, speeds, step height, slope, jump trajectory, stopping/turning clearance; use the actual controller |
| Camera | Mode, collision volume, near plane and worst follow/turn behavior; walkthrough catches occlusion/pinching |
| Critical route | Spawn → learned verb → challenge → goal/failure → retry; reproducible inputs and checkpoints |
| Read hierarchy | Landmark from spawn, objective/threat/interactable distinctions, rest areas; gameplay-camera captures |
| State | Spawn/trigger/checkpoint IDs, collision/nav blockers and reset/save policy; unique IDs round-trip through import |

As provisional third-person **heuristics**, a 1.8 m capsule with radius 0.3–0.4 m might use a 1.2×2.4 m
doorway and 2.5–3 m corridor. These are starting test cases, not universal minima. Measure the camera,
enemy/vehicle passage and player acceleration too. Gameplay clearance overrides a real-world prop size.

1. Greybox with a scale checker; run the critical path using real input before adding final kit content.
2. Test edges: turning in narrow spaces, thresholds/steps, moving-door clearance, slopes, ceiling/jump,
   collision seams, camera wall push and an interrupted trigger/reset. Use swept movement/collisions,
   not a few static point samples, to validate reachable space.
3. Separate visual silhouette, collision and navigation. No render-only shortcut that changes cover,
   traversal or landmark visibility; proxies must match gameplay use.
4. Record failures with route/node IDs, input/seed and a capture. State why a metric was changed and rerun
   the affected route. Do not move the finish marker to make a traversal check pass.
5. Replace greybox modules gradually; repeat route/camera checks after import and lighting. The art pass
   may hide a cue or create visual obstacles without changing the collider.

**Gate evidence:** config revision + level/asset revisions; critical-path input/replay; gameplay-camera
shots at spawn/challenge/goal; failure/retry proof; collision/nav errors. Functional reachability does not
prove the loop is enjoyable: request a focused human playtest at the vertical slice, within the user's
already delegated direction. No approval stop for every module.

Basis: round-2 gap audit §3E; the numeric examples are explicitly author heuristics. This reference defines
checks and ownership, not a claim that a generic level-generating algorithm produces good levels.
