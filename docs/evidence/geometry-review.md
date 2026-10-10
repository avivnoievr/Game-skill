# Geometry repair review

Baseline: upstream 81280882bce606dc69354f10f3c5b6f8b15d2be1, local source `<repo>`.
Verification binary: `/usr/bin/blender`, Blender **4.3.2**. No dependency installs, paid tools, external messages, or subagents.

## What changed

Owned files only:
- `plugins/game-studio/skills/game-studio/scripts/blender/gs_build.py`
- `plugins/game-studio/skills/game-studio/scripts/blender/examples/car_stylized.py`
- `tests/blender/test_gs_build.py` (new)

1. `recess()` uses a non-even region inset and area-weighted selected-face normals per inner vertex. This removes the unbounded miter/average-normal spikes. Negative offsets and empty selectors fail before changing the mesh. The border may vary in width on a curved panel; sharply folded/concave regions still require a sensible modeling split.
2. Numerical degenerate-edge cleanup runs after inset and after baking modifiers, including bevels. The tolerance is 0.1 microns, not a looser QA threshold. It fixes 4 zero-area bevel triangles in the actual saved car `.blend`. Tests confirm that a real 3 mm seam survives and custom corner normals survive the bake/cleanup.
3. Found and fixed a previously untested atlas bug: clearing mesh material slots AFTER writing remapped faces reset every face to slot 0, silently discarding `keep=` material semantics. Rebuilding slots before `bm.to_mesh` retains lamps correctly.
4. Atlas packing explicitly rejects emissive/transparent materials not named in `keep` and texture-driven base/roughness/metallic inputs rather than flattening their appearance silently. Generated images/materials use ownership tags and preserve developer name collisions and external users. Shared meshes outside the build are copied before remapping UV/material slots. Existing owned data is reused when safe to avoid name-collision leaks.
5. Live `begin()` identifies its collection by ownership, not only `GS_<name>`. It preserves developer collections that share the name, shared objects and their needed parents, unowned objects, and nested user collections. Preserved data is detached from the generated collection and remains in the scene.
6. `join()` rejects declared moving parts, copies a shared target mesh, and restores the developer's selection, active object and mode. `export_glb()` restores these even on an exception. `set_origin()` and `apply_rot_scale()` copy shared data before editing it. Blueprint reference empties are explicitly omitted from export.
7. Corrected a real tire/rim bead gap: tire bead at +/-0.92 half-width versus rim barrel ends at +/-0.90 left 2.05 mm axial clearance for a 205 mm tire. The barrel now extends to +/-0.94 half-width, seating the tire against continuous metal without matching/duplicating its boundary ring. The strict per-wheel contact graph now passes at the unchanged 2 mm threshold; wheels remain independent moving objects.
8. Example CLI now exports palette atlases by default and keeps the head/tail materials independently emissive. `--no-atlas` retains individual materials for comparison. Bumpers moved 5 cm inward at each end to match the stated 4.5 m total length. No decorative additions.

## Evidence

14 unittest fixtures pass, including malformed zero-length geometry, forbidden moving-part joins, unsupported/lossy palette input, simulated live restarts, external shared datablocks, linked transforms, export failure restoration and actual GLB import of joint extras:

```sh
/usr/bin/blender -b --factory-startup --python-exit-code 1 \
  -P tests/blender/test_gs_build.py -- --out work/geometry/tests
```

Log: `work/geometry/test-results.txt`. Result: **Ran 14 tests / OK**, about 1.05 seconds of test work.

Actual example CLI tested with a new nested output directory:

```sh
/usr/bin/blender -b --factory-startup --python-exit-code 1 \
  -P plugins/game-studio/skills/game-studio/scripts/blender/examples/car_stylized.py \
  -- --out work/geometry/cli/nested/car.glb
```

It created `car.glb`, `car.blend`, `car_palette.png` and `car_palette_orm.png` and exited 0.

Independent inspect invocation on the GLB (prior to the other agent's validator additions) reports:
- **10,098 triangles** (baseline 9,260; revised safe recess produces different bevel triangulation).
- 5 render meshes, 3 render materials, roughly 7 draw calls (baseline 7 materials, roughly 13 calls).
- **1.800 × 4.500 × 1.440 m** (baseline 1.800 × 4.600 × 1.490 m).
- No non-manifold or zero-area topology warning on the revised body.
- 4 intentionally open tire inner bead boundaries (64 edges each); these are hidden by the rim, not arbitrary repaired holes.
- The part-aware validator initially found 4 legitimate floating WARNs for disconnected rim/spoke subassemblies. Fixing the physical bead/barrel gap resolved all 4 without QA suppression or threshold changes.
- Final strict inspection with all 4 required wheel nodes, centered part pivots and 3 required sockets: **VERDICT PASS (0 fail, 0 warn)** at explicit 12,000 triangles / 3-material fixture budgets; no thresholds were weakened. JSON: `work/geometry/after/strict-report.json`.

Actual GLB JSON confirms **3 materials**: `car_palette`, `head`, `tail`. It has **2 embedded PNG textures**, base color and ORM. Sampler is `magFilter=9728` (NEAREST), `minFilter=9984` (NEAREST_MIPMAP_NEAREST). `keep=` retains separate emissive primitives; joint extras round-trip to Blender object custom properties. The handoff's illustrative '2 materials / 1 texture' is incorrect for this implementation and independently controllable lights.

## Render review

I inspected actual rendered contact sheets with `view_image`, not just reported their filenames:
- Before: `work/geometry/before/views/contact_sheet.png`
- After: `work/geometry/after/views/contact_sheet.png`
- Final three-quarter + exploded parts sheet: `work/geometry/final/views/contact_sheet.png`
- Clean final generated model: `work/geometry/tests/car.glb` and `car.blend`

The original sheet visibly shows cabin corner spikes above the roof in both side and three-quarter views. The revised sheet has a clean roof line and inward window recesses; the palette retains the orange-red body, dark glass/trim/tires, gray rim and pale headlights. This is a simple stylized sedan regression fixture, not a polished hero vehicle: mirrors, handles, door panels and exhaust geometry were deliberately not added.

## Limits / remaining risks

- No actual developer GUI or live MCP session was available. Live collection behavior was exercised through the real bpy data API with a simulated `background=False` branch. Blueprint creation, flags and export exclusion were tested; its interactive viewport appearance is not claimed verified.
- Verified version is Blender 4.3.2. Blender 4.2 and 5.x were not run here.
- `recess()` is not a general self-intersection solver; strongly concave or folded regions still need to be split and visually reviewed.
- Palette atlas supports constant base color/roughness/metallic. It is not a general texture/material baker.
- Small tire bead openings are intentional and should remain visible in QA reporting.
- CLI prints a system Draco-library warning, but this uncompressed export does not request Draco and the GLB succeeds. Workbench emitted EGL/cache diagnostics while producing valid PNG renders. No diagnostics were concealed or fixed through dependency installation.

Root should commit/publish after its independent review; nothing was committed by this agent.
