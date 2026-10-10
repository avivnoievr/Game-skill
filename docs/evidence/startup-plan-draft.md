PLAN-DRAFT: PROVISIONAL

Current state / assumptions
- Dry-run only: supplied repository contains game-studio authoring material; filename audit found no Godot project/scenes/scripts or other engine project. No game source, build, input setup, state/save system, tests or owned asset library was supplied to audit.
- Godot 4.6.3, desktop and third-person camera are test assumptions, not verified user choices or installed capabilities. Actual engine, target hardware, accessibility/input requirements and production constraints remain unknown.
- Pitch: deliberately absurd comedic 3D life/growth simulator; a baby grows and action eventually escalates from slapstick to improbable guns. Comedy does not determine realism, materials, proportions or a rig/source route.
- Proposed mechanics below are replaceable assumptions. This draft authorizes no implementation, downloads, asset generation, installs, paid calls or external communication; it is neither approval nor QA evidence.

Core loop / progression
- Assumed verbs: move/turn, camera orbit, interact/collect and a harmless shove; pause and restart support testing. No aiming, shooting or inventory in this slice.
- States: infant exploration → collect three absurd growth snacks → explicit growth trigger → toddler exploration/shove → push one soft toy into a marked goal → comic success beat → restart.
- Infant moves in a crawl; toddler walks and gains the shove interaction. Counters, identity, world position and objective state persist through growth; body proportions, movement values, interaction reach, rig/clip bindings, collision and camera target may change together.
- Collection emits one gameplay event; growth happens once at the threshold; the target landing in the goal triggers the joke/win. Falling out of bounds resets to a safe checkpoint without losing the current growth state. No combat death or damage model is assumed.
- This is a falsifiable growth/action loop, not a definition of the full life-simulation economy or narrative.

Vertical slice
- One compact greybox room, one protagonist in two adjacent growth states, three reusable pickups, one shoveable toy, one goal and one restartable objective; a short playable route should demonstrate the whole loop.
- Largest risk: a growth transition that changes silhouette and locomotion while keeping grounding, contact, collision, sockets, camera framing and player control coherent.
- Representative final slice must use one style-consistent character source and a small motion set; primitives are allowed for the earlier greybox but cannot prove deforming-character readiness.
- Must-have motion: infant idle/crawl, toddler idle/walk, collection response, growth transition and toddler shove; reaction can be toy physics or one bounded clip. Interrupt/restart behavior belongs in the contract.
- Defer later ages, open world, jobs/economy, additional locations, enemy AI, guns/projectiles/recoil, vehicles, branching story, voiceover, facial performance and commercial content volume.
- Future action need: preserve an explicit hand/socket convention and source editability; do not build weapon assets or full combat systems merely to anticipate it.

Proposed architecture / interfaces (apply only after the real-project audit)
- Director owns game code and integration. Prefer small self-contained scenes, typed GDScript, fixed-step physics and Resource configuration; preserve a working existing core if one appears.
- `game/growth_state.gd`: age stage, pickup count and objective flags as versioned serializable data; `collect(id)`, `can_grow()` and `complete_goal()` implement rules without presentation/node lookups.
- `config/stage_profile.gd` + stage resources: per-stage movement, body/collision dimensions, reach, camera target and clip map. These are the single tuning source; no runtime filesystem or deep global-bus architecture is needed.
- `characters/player/player.tscn` / `player.gd`: CharacterBody3D owns physics and input actions; a visual child owns skeleton/AnimationTree. `apply_stage(profile)` synchronizes visuals, colliders, reach and camera target at a safe transition boundary.
- `levels/growth_room/`: pickup/target scenes report past-tense signals to the level objective controller; parents inject dependencies. UI observes objective state. A single restart route resets owned objects and disconnects/destroys scene-owned resources.
- `qa/`: explicit action injection, state snapshots and capture hooks restricted to QA mode. Restart/checkpoint state is enough for the slice; persistent save UI is deferred, with state round-trip verification if saves are later selected.
- Define InputMap actions and clip identifiers before asset handoff. Do not assume automatic retargeting, exact skeleton compatibility or arbitrary proportion morphs work.

Milestones (ordered dependencies, owners and exits)
- M0 — prerequisite/decision freeze; owner Director, using planner + genre-art-researcher reports. Confirm actual engine/version, project path/status, target device, camera/input and scope; inspect existing architecture/assets/license evidence. Reconcile art direction and source route into `design/plan.md`, art bible and explicit budgets. Exit: approved scope assumptions, one viable editable rig/source route, named baseline device and measurable targets; no build work before this reconciliation.
- M1 — depends M0; owner Director. First validate/freeze the body/reach/socket contract with proxy contacts, then build the greybox route, input, stage/objective data and checkpoint/restart. Exit: target-engine scripted and human-input runs complete collection → growth → shove → win; stage switches exactly once, counters survive growth and all failure/restart paths return to a playable state. Independent playtest-qa reviews logs/state evidence; primitives remain marked temporary.
- M2 — depends M0 and the early M1 body/reach/socket contract; may overlap the remaining M1 loop. Owners: asset-builder for owned character/environment source, then animator for character rig/motion. Import both stage presentations and clip inventory; validate license/source, named mesh parts, skeleton, hand socket, clip durations/events and export units. Exit: editable source plus imported crawl/walk, transition and shove evidence, inspected from front/side and gameplay camera; art-critic checks silhouette/material coherence, playtest-qa checks import. Model-source details remain pending research.
- M3 — depends M1 + M2; owner Director. Integrate representative art/motion, floor contacts, stage-specific collision, reach, camera and the comic beat. Exit: growth and shove occur under real input without teleporting the world position, persistent foot/hand sliding, visible mesh collapse, stuck colliders or camera occlusion of the objective. Animator supplies contact/pose strips; independent reviewers receive raw gameplay capture on the exact revision.
- M4 — depends M3; owners independent playtest-qa + art-critic. Review the same frozen build revision and evidence; Director fixes defects. Exit: complete input-driven route and restart, zero reproducible script/import errors, no missed transition/objective trigger, and approved visible/motion thresholds. At most two review rounds before a concrete decision; untested items remain open.

Budgets / evidence contract
- Proposed slice scope caps: one room, two growth states, one active shove target and three pickups; no extra content to hide loop or motion failures. Effort: greybox is small; editable coherent two-stage character motion is the dominant uncertain effort; integration/QA are moderate.
- Provisional runtime acceptance to confirm in M0: sustain 60 fps at 1080p on a named baseline desktop over a complete repeated route; record frame-time distribution and transition hitches. Set triangle, material, texture, skinning and draw-call ceilings after the source sample/device check rather than fabricate current measurements.
- M0 must define contact tolerances and art/motion thresholds using the chosen style and reference sample. For M3/M4, include a real-time input recording, side/front contact views, logs and state trace covering three complete loops including fall recovery and restart during each age.
- Numeric/runtime gates require the actual Godot version/build and target-device run. A source validator, still render or this document cannot establish camera feel, deformation quality, import behavior, collision correctness or performance.

Parallelism / ownership
- Opening planner and genre-art-researcher may work independently; Director resolves conflicting constraints. Neither consumes or rewrites the other's draft.
- After the early M1 metric/contract pass, Director can finish greyboxing while asset-builder works in a separate `assets/player/` source folder; optional environment work uses its own folder. At most three specialists run concurrently.
- Animator waits for the agreed character source/rig contract; asset-builder and animator never simultaneously mutate that character source or a shared live Blender scene. Handoff freezes a named revision/copy.
- Only Director writes gameplay/shared scenes/manifests and integrates assets. At the gate, critics are read-only and inspect the same revision; no review-triggered shared writers.

Research-dependent decisions
- Open: stylization/realism and comic reference vocabulary, silhouette/proportion strategy, infant-to-toddler anatomical change, model source/license and editability, same-rig versus controlled stage swap, texture pipeline, clip detail/retarget feasibility, lighting/render budget and readable interaction feedback.
- Director must choose from inspected research/sample evidence. A rigged pack is a candidate, not an assumed suitable baby model; no claim that a generated mesh or uniform scale alone meets age, deformation or contact needs.

Open risks / fallback
- Missing real game/engine is the immediate production blocker: stay at planning/read-only audit until M0 resolves it; adapt this dependency plan to the confirmed engine rather than import a new architecture blindly.
- If one rig cannot express both age silhouettes/contacts, use two deliberately compatible stage presentations with a brief explicit transition and stable gameplay root; still prove both imports and movement/contact. If licensed editable sources cannot be secured, keep a clearly temporary articulated placeholder and do not pass representative-art acceptance.
- If dynamic growth colliders cause grounding failures, commit stage replacement at a verified grounded safe point; defer arbitrary continuous scaling. If retargeting fails, author the few essential clips on the selected rig instead of accumulating unrelated animation packs.
- If costs, service access or license terms are unknown, use owned/verified local source and greybox evidence; obtain concrete source/cost authorization before any paid production call. Nothing in this plan asserts available APIs or license rights.
- If gun/combat mechanics later prove central to the user's intended first slice, Director must revise scope/dependencies before expanding; the present adjacent-age slice intentionally proves the growth/motion foundation first.
