# Architecture that stays clean

Contents: 1. Principles · 2. Web (TypeScript + Vite + three.js / R3F) · 3. The game loop · 4. Core patterns ·
5. Godot 4 · 6. Unity · 7. Keeping an agent-maintained codebase from rotting · 8. Debugging discipline ·
9. CLAUDE.md skeleton for the game repo

## 1. Principles

1. **Simulation and presentation are separate.** Game rules live in a pure core with no renderer,
   DOM or engine-node imports. They are deterministic (fixed timestep, seeded RNG) and testable
   without a GPU. The view layer reads core state and draws it. This one split makes QA, saves,
   replays and refactors tractable.
2. **One source of truth.** Every tunable number (speeds, damage, budgets, colors) lives in config,
   never inline. Every asset is listed once in a manifest.
3. **Explicit lifecycle.** Whatever creates a resource disposes it. Scenes have `enter()` / `exit()`,
   and `exit()` releases everything `enter()` made.
4. **Machines enforce rules.** Prose conventions erode, while lint rules, layer checks and tests don't.
   Every rule that matters gets a check in `qa/verify.sh` (G1).
5. **Boring and small.** Prefer plain modules and functions to frameworks of your own invention.
   Files that change together live together. No file above ~300–400 lines without a reason.

## 2. Web: TypeScript + Vite + three.js (or React Three Fiber)

```
src/
  core/          pure TS simulation: NO 'three', 'react' or DOM imports (enforced)
    sim.ts  systems/  components/  fsm/  rng.ts (seeded)  loop.ts (fixed step)
  render/        three objects, materials, view-sync from core state; owns dispose()
  assets/        manifest.ts (id, url, type, group) + registry.ts (load, cache, refcount, dispose)
  scenes/        Scene interface: enter(), update(dt), exit()
  input/         device → action mapping; gameplay reads actions, never keys
  config/        tunables, palette, budgets: the only place numbers live
  ui/  audio/
  debug/         QA hook (window.__QA__), stats, dev GUI; excluded from production builds
  main.ts
tests/           unit tests for core/ (vitest), e2e/ (playwright)
qa/              verify.sh, shot list, baselines/, out/ (gitignored)
docs/            ARCHITECTURE.md (one page), adr/NNNN-title.md
```

**Gates (G1):**
- TypeScript `strict`, `noUncheckedIndexedAccess`, `noImplicitOverride`.
- ESLint `max-lines` (300–400, as an error) and `max-lines-per-function`.
- dependency-cruiser rule: `core` may not import `render|ui|three|react`.
- knip for unused files, exports and dependencies.
- size-limit for the bundle budget.

**three.js specifics:**
- Run one renderer and one loop (`renderer.setAnimationLoop`). Two loops cause double updates and
  doubled GPU cost.
- Cap the pixel ratio: `renderer.setPixelRatio(Math.min(devicePixelRatio, 2))`.
- Color management:
  - Use the current defaults (`ColorManagement.enabled`, sRGB output).
  - Set `texture.colorSpace = SRGBColorSpace` only on color maps (base color, emissive). Data maps
    stay linear.
  - With an EffectComposer, end with `OutputPass` so tone mapping and color conversion happen once.
- Disposal: removing a mesh does **not** free GPU memory. Call `geometry.dispose()`,
  `material.dispose()` and `texture.dispose()`, dispose render targets and skeletons, and call
  `ImageBitmap.close()`.
- Loaders: register `MeshoptDecoder` and `KTX2Loader` (with `detectSupport(renderer)`) on
  `GLTFLoader` when the assets use them.
- Reuse `Vector3`, `Matrix4` and similar temporaries in hot paths. Allocating per frame causes GC
  hitches.
- Use instancing (`InstancedMesh`) for repeated props. Merge static geometry by material.

**R3F specifics:**
- Never `setState` inside `useFrame` or fast events. Mutate refs and use the frame delta.
- Don't create objects in render loops.
- `useLoader` and `useGLTF` cache, so preload hero assets.
- Use `frameloop="demand"` with `invalidate()` for scenes that come to rest.
- Toggle `visible` instead of remounting heavy subtrees.

## 3. The game loop: fixed timestep, interpolated render

```ts
const DT = 1 / 60;                 // simulation step (s)
let acc = 0, last = performance.now() / 1000;
function frame(nowMs: number) {
  const now = nowMs / 1000;
  acc += Math.min(now - last, 0.25);   // clamp: avoids the "spiral of death" after a stall
  last = now;
  while (acc >= DT) { sim.step(DT); acc -= DT; }
  view.render(sim, acc / DT);          // alpha in [0,1): interpolate between the last two states
}
renderer.setAnimationLoop(frame);
```

- Physics and gameplay only ever see `DT`, which makes them deterministic and testable.
- In QA mode the harness calls `sim.step` directly (`qa-protocol.md` §2). The loop is not free-running.
- Never multiply by a variable frame delta inside the simulation. Frame-rate-dependent movement is a
  classic bug: it jumps on slow machines and tunnels through walls.

## 4. Core patterns

- **State machines** for anything with modes: player (idle/run/jump/attack/hurt), enemies, game flow
  (boot/menu/play/pause/gameover). Use an explicit transition table where every state has
  `enter/update/exit`. Do not use nests of booleans like `isJumping && !isAttacking`.
- **Events:**
  - Use a typed event bus only for cross-system notifications (`EnemyDied`, `LevelCompleted`, past
    tense). Inside a module, call functions directly.
  - A global bus is still global state. The world may have changed by the time an event is handled,
    and event loops are possible. Keep handlers small and side-effect-aware.
- **Asset registry:**
  - Load everything through the manifest, with load-by-group (boot, level-1) and a progress callback.
  - Refcount shared assets and dispose them on scene exit.
  - A load failure is an error, never a silent placeholder.
- **Input:** map devices to named actions (`move`, `jump`, `interact`) in one place, so rebinding,
  gamepads and QA input injection all work.
- **Object pools** for frequently spawned objects (projectiles, particles, damage numbers).
- **Config:** typed, frozen objects. Balance values and palette come from the art bible and game
  design. Any number that appears twice belongs in config.
- **Save/load:** serialize core state only (plain data, versioned schema), never scene objects.

## 5. Godot 4

```
res://
  addons/                third-party plugins only
  game/                  autoloads that truly need global access (keep few): game_state.gd, save.gd
  characters/player/     player.tscn, player.gd, player_states/, art/
  enemies/<type>/
  levels/<level>/        level.tscn + level-specific props
  ui/  audio/  shared/   (reusable components, shaders, materials)
  config/                Resource files (.tres) with tunables
  test/                  GUT or gdUnit4 tests
  qa/                    qa_autoload.gd (active only with the --qa user arg), capture scripts
```

- snake_case for files and folders (exported packs are case-sensitive); PascalCase for node names.
- **Self-contained scenes:** a scene should not reach up into its parents. Parents inject
  dependencies. Signals report what happened (past tense: `died`, `item_collected`); they don't
  command.
- **Autoloads** are only for systems that own their data, must be global, and stand alone. Systems
  that modify other systems' data are regular nodes.
- Static typing everywhere (`var speed: float = 4.0`, typed function signatures). Turn on the
  stricter GDScript warnings.
- Data lives in custom `Resource` classes (`.tres`), not hard-coded in scripts.
- Physics in `_physics_process` (fixed rate); visuals in `_process`.
- Tests: GUT (`godot --headless -s addons/gut/gut_cmdln.gd -gdir=res://test -gexit`) or gdUnit4.
  Both have CLI runners with JUnit output.

## 6. Unity

- `Assets/_Project/` with `Scripts/{Core,Gameplay,UI,Editor}`, `Art/`, `Prefabs/`, `Scenes/`,
  `Settings/`. Keep third-party packages out of `_Project`.
- One assembly definition per layer (Core has no UnityEngine-heavy dependencies), so the layer rules
  are enforced by the compiler.
- ScriptableObjects for configuration and shared data.
- EditMode tests for pure logic; PlayMode tests for integration:
  `Unity -batchmode -runTests -projectPath . -testPlatform EditMode -testResults results.xml`.
- Unity's own agent plugin covers URP, physics and UI conventions; install it for Unity projects
  (`toolchain.md`).

## 7. Keeping an agent-maintained codebase from rotting

- **CLAUDE.md in the game repo, under 200 lines.** It holds the commands, the architecture map
  (folders → responsibility), the gates, and the gotchas you actually hit. Every line should prevent
  a real mistake. Move detail into `.claude/rules/*.md` with `paths:` globs, so it loads only when
  matching files are touched.
- **ADRs** for every hard-to-reverse choice (engine, physics library, ECS vs. scene graph, asset
  pipeline, render style). Use `docs/adr/NNNN-title.md` with Title / Status / Context / Decision /
  Consequences, about 15 lines each.
- **Refactor gate:**
  - When a file crosses the line limit, or a function grows a third responsibility, split it
    *before* adding more.
  - When three fixes for the same bug have failed, stop and question the design.
- **Surgical changes:**
  - Touch only what the task needs.
  - Remove the dead code your change created, and no unrelated "cleanups" mixed into feature commits.
- **No speculative abstractions.** Build the second use case before generalizing.
- **Plans name files and interfaces first.** A feature plan lists the files it will touch and the
  interfaces between them before code is written.
- **Commit after each verified feature**, with a message that says what was verified.

## 8. Debugging discipline

1. Reproduce first, ideally as a failing test or a scripted QA sequence.
2. Find the root cause before changing code. A fix without a cause is a guess.
3. A bug fix ships with a regression test that you **saw fail** before the fix.
4. After three failed fixes, stop. The problem is probably the architecture or a wrong assumption.
   Re-read the relevant code and data from scratch.
5. Never hard-code special cases to make a test or a screenshot pass. If a test seems wrong, say so;
   don't work around it.

## 9. CLAUDE.md skeleton for the game repo

```markdown
# <Game> — project memory
Engine: <three.js r1xx + Vite | Godot 4.x | Unity 6>  ·  Art bible: design/art-bible.md  ·  Progress: progress.md
Skill: game-studio (scripts at <absolute path>/scripts — export GAME_STUDIO_SCRIPTS=<that path>)

## Commands
- dev: npm run dev · verify (all gates): bash qa/verify.sh · quick: bash qa/verify.sh --quick

## Architecture map
- src/core: pure simulation (no three/DOM) · src/render: view + dispose · src/assets: manifest/registry
- src/config: all tunables · src/input: actions · src/debug: QA hook (dev only)

## Rules that prevented real mistakes
- <one line per real gotcha, e.g. "metals need the HDRI env map or they render black">
```
