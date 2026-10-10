# Independent articulated-prop pilot

Scope: read-only review of Game Studio changes plus a fresh desk-fan pilot in `work/pilot-review/`. No repository files edited, no installation or paid request. Used installed Blender 4.3.2 and Godot 4.6.3. This is a functional workflow proof, not independent professional-art acceptance of my own asset.

## Contract and result

The numerical/part contract was written first in `pilot-review/brief.md`: desktop fan, width 0.30 m × depth 0.20 m × height 0.45 m, fixed Base and Guard, separately controllable four-blade Rotor about Blender-local Y, cord socket, ≤ 4,000 triangles, two materials, no textures, ≤ 12 collision triangles. Build starts from a copy of the skill's template, replacing only its blockout function with profile/revolve/sweep/extrude forms; it does not use the car example.

| Check | Result | Evidence |
|---|---|---|
| Exported dimensions | 0.304 × 0.200 × 0.452 m, within predeclared 2% | `pilot-review/inspect.json` |
| Render geometry | 2,344 triangles, 3 meshes, 2 materials, no textures | `pilot-review/inspect.json` |
| Collision geometry | Distinct Base-colonly, 12 triangles, excluded from render budget | `pilot-review/inspect.json` |
| Required parts/socket | Base, Guard, Rotor, SOCKET_cord present | `pilot-review/inspect.json` |
| Centered spin pivot | Distance 0.000000 m against 0.005035 m tolerance | `pilot-review/inspect-rotor.json` |
| Inspector verdict | PASS, zero FAIL and zero WARN | Both inspector JSON files |
| GLB control metadata | Rotor extras joint=spin, axis=Y, axis_gltf=-Z; hierarchy retains independent nodes | `pilot-review/gltf-nodes.json` |
| Native editable source | Source re-opened successfully; 3 render parts, root, collision, socket, Rotor joint preserved | `pilot-review/source.blend`, actual Blender source-open probe |
| Engine control | Godot imports actual GLB; Rotor rotates 45° about glTF-local -Z while origin, Base, Guard and socket remain fixed; test vertex moves 0.013776 m | `pilot-review/control.gd`, `pilot-review/godot-control.json` |
| Images inspected | Opened five-view workbench sheet, two Eevee views, and scale-reference sheet | `pilot-review/review/contact_sheet.png`, `look/contact_sheet.png`, `scale/contact_sheet.png` |
| Khronos validator | NOT VERIFIED: existing environment has no gltf-validator; script honestly exited 2 | Actual check_gltf.mjs invocation; no dependency installation |

Hashes and sizes of the build, source, export and evidence are recorded in `pilot-review/provenance.json`.

The rotor's axial origin is Y=-0.0105 rather than the brief's Y=-0.015; this 4.5 mm shift remains on the identical physical shaft line and does not affect rotation. No off-axis drift occurred in the engine check.

## Visual assessment and limits

The fan reads immediately in the opened silhouette and views. Proportion, contact and fixed-versus-moving forms are coherent; the guard, rotor and stand remain addressable. The restrained cream/sage material roles survive export. The four flat paddle profiles and sparse guard are still simple; they establish a stylized control fixture, not a finished hero prop or realistic fan simulation. No mechanical blade pitch, switches, physical safety grille, material wear or professional target-game art comparison is claimed. Eevee's studio lighting makes the cream near-white and sage much lighter than the workbench colors: actual target-game lighting/material acceptance remains necessary.

The colored exploded view separates the lower base, but Rotor and Guard overlap because their bounds centers nearly coincide. This is a known limitation of the requested center-relative explosion formula; color and normal orthographic views still make the three parts inspectable. A 1.8 m scale reference correctly dwarfs this 0.45 m prop, so use its dedicated scale sheet alongside the close-up sheet, not as the only detail evidence.

Only one geometry build was needed. The Godot proof first exposed a harness initialization mistake; awaiting the first process frame fixed that harness before the final asserted pass. Managed-shell data/cache paths were redirected with XDG variables after the first Godot start could not write its user-data directory. No repo helper was changed to obtain these passes.

## Consequential review findings

1. **Packaging/provenance link:** at review time the project/user installers copied only the skill and agents; the aggregate plugin `THIRD_PARTY_NOTICES.md` was omitted, while the design-loading router pointed outside the copied installation to it. Root notified with concrete fix: carry notices into standalone installs and provide a valid installed path. Individual vendor licenses were present; this is an attribution/inspection packaging gap, not a claim that all vendor licenses disappeared.

Earlier destructive prefix-deletion/material-wide joins/all-parts-touch instructions and four-round versus two-round disagreement were found, communicated, and rechecked as removed/fixed in the latest modeling and asset-builder files. The false concern that a factory-startup Cube polluted saved source was withdrawn after reading gb.begin's separate headless empty-scene branch. No remaining structural blocker was observed in the actual positive articulated-prop workflow.

One limitation to keep explicit: bounding-box-center validation suits symmetric wheels/rotors; it is not a universal shaft proof for an asymmetric or three-blade propeller. Such assets need a declared physical shaft and engine sweep evidence, not blindly relocating their pivot to a bbox center. The articulated recipe already says centered geometry where intended and actual engine motion checks.

## Reproduction

```bash
/usr/bin/blender -b --factory-startup --python-exit-code 1 -P work/pilot-review/build.py -- --skill-dir <repo>/plugins/game-studio/skills/game-studio --asset desk_fan --out work/pilot-review/fan.glb --blend work/pilot-review/source.blend
/usr/bin/blender -b --factory-startup --python-exit-code 1 -P <repo>/plugins/game-studio/skills/game-studio/scripts/blender/inspect_model.py -- work/pilot-review/fan.glb --preset web-prop --max-tris 4000 --expect-dims 0.3,0.2,0.45 --parts Rotor,Base,Guard --part-pivot any --sockets cord --json work/pilot-review/inspect.json
/usr/bin/blender -b --factory-startup --python-exit-code 1 -P <repo>/plugins/game-studio/skills/game-studio/scripts/blender/inspect_model.py -- work/pilot-review/fan.glb --preset web-prop --max-tris 4000 --parts Rotor --part-pivot center --sockets cord --json work/pilot-review/inspect-rotor.json
/usr/bin/blender -b --factory-startup --python-exit-code 1 -P <repo>/plugins/game-studio/skills/game-studio/scripts/blender/render_views.py -- work/pilot-review/fan.glb --out work/pilot-review/review --size 480 --views front,right,q_fr,silhouette,parts --explode-factor 0.7
/usr/bin/blender -b --factory-startup --python-exit-code 1 -P <repo>/plugins/game-studio/skills/game-studio/scripts/blender/render_views.py -- work/pilot-review/fan.glb --out work/pilot-review/look --engine eevee --size 480 --views q_fl,q_fr
XDG_DATA_HOME=work/pilot-review/runtime-data XDG_CACHE_HOME=work/pilot-review/runtime-cache XDG_CONFIG_HOME=work/pilot-review/runtime-config godot --headless --path work/pilot-review --script work/pilot-review/control.gd
```
