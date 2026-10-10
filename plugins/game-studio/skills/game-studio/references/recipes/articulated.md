# Articulated prop: explicit joints and attachment frames

**Contract:** one object per independently moving rigid part; named root, parent, pivot location,
local axis, motion units/limits, attachment sockets, collision needs and initial pose. Immutable trim
may share the part; moving pieces never disappear into a material-based merge.

| Object | Pivot / hierarchy | Required evidence |
|---|---|---|
| Door/chest lid/lever | Hinge line or shaft; parented under body | Closed/mid/open pose, frame/jamb/interior faces, clearance |
| Drawer/bolt/magazine | Rest attachment frame + slide direction | Start/end translation, no stretching/rotation, stop position |
| Turret | Yaw root at ring, gun pitch child at trunnion | Combined yaw/pitch sweep, correct parent order |
| Handheld weapon/tool | Grip frame; distinct moving magazine/slide; muzzle/offhand/eject sockets as needed | Engine hand attachment and effect origin; gameplay-camera view |
| Wheel/fan/valve | Spin shaft, centered geometry where intended | Full rotation without wobble; no stationary hardware rotating with it |

Use `gb.set_origin` before parenting; use `gb.set_joint(obj, kind, axis, lo, hi)` and `gb.socket`.
The helper writes `joint`, `axis`, `axis_gltf`, `min`/`max` and `units` (meters for slides, degrees for
angular limits). `axis` is Blender-local; the importer/game code must consume `axis_gltf` with the node
transform. glTF extras are data, **not** an automatic engine joint or animation.

Keep mesh data single-user before a pivot edit that changes geometry; helper origin/transform operations
copy shared data. Preserve world transforms when parenting. Apply scale/rotation before finalizing the
joint frame; re-verify both exported axis and limit direction after any transform change.

Deliver the editable source, deterministic build script, export and part manifest. Keep each moving
part separate even if the same material covers the whole asset. For physics, choose simple proxies per
moving body that needs collision; don't make a render mesh into a collider by accident.

**Gate:** required names via `--parts`/`--sockets`; inspect hierarchy and `parts` view; min/mid/max
motion poses and an actual continuous sweep/engine replay. Center checks apply to spinning centered
parts; a hinge pivot belongs on an edge, so a bbox-center check does not validate it. Explicitly selected
untagged required parts can be center-checked; tag noncenter joints correctly or choose `--part-pivot any`
and retain the joint-specific evidence. Never weaken a spinning-part check to hide wobble.

A deliberate joint gap is not proof of an unwanted floating island. Validate attachment/clearance per
rigid group; remaining loose pieces **inside** that group still need investigation. A clean static sheet
does not prove collision-free articulation or usable attachment frames.

Basis: original contract from round-2 vehicle/parts report §2.5 and the installed `gs_build`/inspection
interfaces. No vendor generator is treated as providing finished hinges, hidden faces or exact sockets.
