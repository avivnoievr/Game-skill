# Validation of Game Studio 1.1.0

Verified on 2026-10-10 against Claude's handoff commit `81280882bce606dc69354f10f3c5b6f8b15d2be1`.
This records the continuation's checks, not every historical claim from earlier research.

## Regression results

**57 regression tests pass**, plus a separate Godot articulated-control pilot with eight true checks.

| Suite | Passed | What it establishes |
|---|---:|---|
| Blender build helpers | 14 | Geometry repair, atlas colors/ORM/emissive retention, ownership/shared-data/context protection and export metadata |
| Blender inspector | 9 | Required parts/sockets, GLB extras, spin pivots, hinge/static exemptions, rigid groups, collision separation and strict triangle caps |
| Blender renderer | 4 | Actual small PNGs, automatic/optional exploded views and restoration of parent transforms/colors after failure |
| Animation report | 3 | Stationary bone-head rotation pops fail; clean seams and quaternion sign equivalence pass |
| Verification entry | 5 | Empty/decoy/missing/failed project checks block; actual healthy scripts pass; full mode requires research and final plan |
| Live Chromium capture contract | 14 | Missing/thrown/rejected hooks, unknown counters, zero/invalid limits, reload evidence and action-frame budget checks |
| GLB budget guards | 4 | Missing measurements and invalid/zero limits fail; controlled healthy counts pass |
| Discovery/install | 4 | Installed override with spaces, version rejection, no silent override fallback, preserved customizations and portable notices |

Browser tests use controlled canvas/QA fixtures and preinstalled Chromium/Playwright. GLB guard tests
use a controlled validator response; they do **not** prove Khronos validation. The actual Khronos
package is absent here, and the independent fan's `check_gltf.mjs` correctly exited 2. Native GUI,
Unity, actual paid services and real-device GPU performance were not tested.

Reproduce from the repository root with installed tools:

```bash
blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_gs_build.py -- --out work/build-fixtures
blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_inspect_parts.py
blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_render_parts.py
blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_clip_report.py
node --test --test-isolation=none tests/qa/test_verify.mjs tests/qa/test_gltf_budgets.mjs tests/web/test_capture.mjs
python -m unittest discover -s tests/bootstrap -v
```

Blender tested: **4.3.2**. The sandbox needed an additional localhost network allowance for the browser
fixture and `--test-isolation=none` to avoid forbidden runner stdin pipes. No dependencies were
installed. These sandbox accommodations are not production dependencies. Shell/Python/JavaScript
syntax, JSON parsing, local links, source hashes and `git diff --check` also pass. Claude CLI is absent,
so this continuation does not claim `claude plugin validate` or a Claude/Opus quality evaluation.

## Negative proof and actual asset fixes

The unmodified baseline falsely passed an empty verification project and browser cases with thrown
stats, absent measurements and a zero-count budget. Current guards fail those cases. The animation
baseline also passed a 90-degree leaf-bone rotation pop because only bone heads were measured.
The revised report includes quaternion orientation evidence.

The car regression fixture now measures **1.8 × 4.5 × 1.44 m**, **10,098 render triangles**, five
render meshes, three materials, two embedded atlas images and a separate 12-triangle collider.
Four named wheels, pivots and three sockets pass strict inspection: **zero failures/warnings**.
The 12,000-triangle fixture limit is explicit; it is not the generic hero-prop starting budget.

Roof recess spikes and degenerate triangles were repaired. Atlas slot rebuilding previously discarded
kept emissive materials; head/tail semantics now survive actual GLB export. A real 2.05 mm tire/rim
bead gap was corrected geometrically so contact passes at the unchanged 2 mm threshold.
Nearest atlas sampling was checked; minification/game lighting still require target-engine review.
See [car-inspect.json](evidence/car-inspect.json), [geometry tests](evidence/geometry-tests.txt) and
[geometry review](evidence/geometry-review.md). Before/after and exploded renders were opened.

## Independent articulated-prop pilot

A fresh agent used the updated workflow to build a separate fan, not the car example: **2,344 triangles**,
three semantic meshes, two materials and 12 collision triangles. Parts/pivots/socket inspection passes
without warnings. Editable `.blend` reopened successfully. Godot **4.6.3** imported the actual GLB:
rotor geometry moves while its origin, base, guard and socket stay fixed. All eight control checks pass.
The portable committed fixture was separately run successfully after removing workspace-specific paths.

```bash
blender -b --factory-startup --python-exit-code 1 -P tests/pilot/desk_fan.py -- --skill-dir "$PWD/plugins/game-studio/skills/game-studio" --asset desk_fan --out "$PWD/work/fan.glb" --blend "$PWD/work/fan.blend"
godot --headless --path tests/pilot --script "$PWD/tests/pilot/control.gd" -- "$PWD/work/fan.glb" "$PWD/work/fan-control.json"
```

In restricted hosts, redirect Godot's XDG data/cache/config paths to permitted scratch folders.
Evidence: [pilot inspection](evidence/pilot-inspect.json), [Godot controls](evidence/pilot-godot-control.json),
[independent report](evidence/pilot-review.md). Contact/exploded/material/scale views were opened.
Both assets are functional stylized fixtures, not polished hero art. Center-relative explosion may
leave coaxial parts overlapping; bbox centers are not a universal shaft test for asymmetric rotors.

## Opening research/planning dry-run

Two fresh Codex agents followed the new role definitions on the user's absurd growth-simulator
example. Research inspected four primary creator/publisher text references; it correctly reported no
image/footage inspection and marked the visual recommendation provisional. The planner mapped growth,
rig/contact/collision/camera risks, dependencies, owners and a bounded slice without reading the
parallel research. The director then reconciled scope and direction into a final illustrative plan.

Artifacts: [research](evidence/startup-research.md), [independent draft](evidence/startup-plan-draft.md),
[reconciled plan](evidence/startup-plan.md). Role status semantics and unknown-engine handling were
clarified from this dry-run. This verifies the mechanism's use, not the proposed game's quality.

## Source/media boundaries

Eighteen bundled source files match their pinned original Git blobs and SHA-256 records. MIT and
Apache licenses/NOTICE are retained. Imported example quality scores are not endorsed. Research uses
only evidence actually accessed: earlier YouTube notes are caption-based; this continuation did not
directly watch the videos, and public Instagram access failed. Live ownership tests use the real
Blender data API with a simulated background flag, not a developer GUI/MCP connection.

Public evidence copies omit private session/inbox identifiers and local absolute path prefixes.
Numerical results are unchanged; provenance hashes describe the original local artifacts before
path sanitization, not rewritten public JSON files.

## Additive design-judgment verification (2026-10-10)

Scope: instruction/reference/attribution additions to published commit `660e9f7`. No production
script, inspector threshold, existing vendor archive or package version was changed.

- Compared every existing published blob against the local baseline. Modified existing files retain
  their exact prior bytes as a prefix; no original instruction line or file was removed.
- The original 19 published vendor files (18 upstream files plus their manifest) are unchanged.
- Five new license/NOTICE copies match the pinned upstream Git blob hashes exactly.
- JSON parses, local Markdown links resolve, public additions contain no private coordination
  addresses/session identifiers or absolute execution paths, and `git diff --check` passes.
- `python3 -m unittest discover -s tests/bootstrap -v`: **4 passed**.
- A separate temporary project-copy installation preserved the new reference, attribution manifest,
  five licenses/notices and appended builder/critic definitions byte-for-byte.
- One additional agent performed read-only method/consistency review. Its judging-order issue was
  corrected with explicit ordering for Procedure steps 1–3; no new standing agent was added.

These checks establish packaging, preservation and instruction consistency. The baseline's 57
regression results remain historical; they were not rerun for this documentation addition.
No new Claude/model taste evaluation, visual reference comparison on a real asset, Blender MCP
connection, actual-game quality claim or GPU benchmark is established by this supplement.

## Distribution candidate 1.1.1 (2026-10-10)

Development remains in `avivnoievr/Game-skill`. The proposed `game-studio-3d` repository is a
publication channel for source commits the owner tests and explicitly approves. No automatic
sync, push-triggered publication or first-release approval was introduced.

- `python3 -m unittest discover -s tests/distribution -v`: **6 passed**. These check committed
  input despite later edits, binary/license/test preservation, file modes and hashes, output
  overwrite prevention, full SHA/version requirements, exact approval matching, and rejection
  of output inside the source repository. Approval examples in tests are synthetic fixtures.
- Prepared a full candidate from a temporary committed copy, not from uncommitted input.
  `RELEASE.json` reports `candidate` and a null approval. All recorded SHA-256 hashes and modes
  matched the emitted files; local Markdown links and three issue-form YAML files parsed.
- Ran the candidate's existing bootstrap suite: **4 passed**. Installed discovery and preserved
  user-customization behavior remain the same. Runtime scripts and existing vendor files did
  not change; the 57 earlier regression results were not rerun or relabeled as current.
- One independent agent reviewed the pinned export, manifest, approval boundary and packaging
  claims. Fresh-history instructions and the distinction between backups and merging were
  clarified. Distribution-tool tests stay with their tool in the development repository.

The package metadata advances to 1.1.1; the production workflow files are preserved. The
preparation tool has no publishing capability. An approval record is a manual record, not a
cryptographic verification that the owner approved. Candidate install links point to a future
publication tag and become usable after that tag exists. There is still no new Claude quality
evaluation or observed real-game result from this packaging work.
