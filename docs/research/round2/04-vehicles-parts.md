# 04 — Vehicles, articulated parts, realistic hard-surface (Round-2 Agent 4)

## 1. Summary
- **Answer to the user's question today: no, not reliably.** `modeling.md` routes vehicles to "code modeling" but has no
  vehicle procedure, no wheel/pivot/hinge rules, no vehicle dimensions, no engine wiring. `inspect_model.py`'s
  floating-part check (islands that don't touch the largest island within 2 mm) would WARN on every correctly
  separated wheel, because a wheel sits in its arch with clearance and touches nothing.
- All four target engines treat wheels the same way: **the body mesh has no wheels; each wheel is a separate node
  whose origin is the axle center; physics is a raycast per wheel, not a wheel collider mesh** (Godot, Unity,
  Rapier, cannon-es: docs/source opened). That makes "split into parts with correct pivots" a hard requirement.
- Engine traps found in source: cannon-es defaults to **X-forward** (`indexForwardAxis=0`) while glTF assets face +Z;
  Rapier's forward-axis setter is literally named `setIndexForwardAxis` (assign with `=`); Godot wants the wheel
  node origin at the *bottomed-out* position, lowered by `wheel_rest_length`; Unity raises the collider by
  `suspensionDistance/2`.
- Pro workflow (2 transcripts): orthographic blueprints scaled to a real L×W×H box; body topology flows front→back
  and **wheel arches are cut into that flow** (a radial fan around the arch breaks shading); windows = inset with
  depth; arch lip by extrude.
- Budgets (verified): GTA V cars L0 60–120k tris down to L4 0.5–1k; PGR3 (Xbox 360) ~85–105k polys incl. interior,
  PGR2 ~10k. Web/mobile numbers are forum-grade [UNVERIFIED].
- Dimension table below: 10 vehicle classes from Wikipedia infobox wikitext. The tire diameter formula is verified
  (Tire code). Track width and ground clearance could not be verified from a primary source (sites blocked). They
  are given as rules of thumb, labeled.
- No open-source procedural car/wheel generator was found (GitHub search API blocked; web search negative).
  Rigacar (GPL-3, bl_info Blender 2.83) is a car *animation rig* add-on. It does show a useful convention:
  `DEF-Wheel.Ft.L / .Bk.R / DEF-WheelBrake / DEF-Body`, wheel size from the bound-object bbox. It is not needed
  for games, where physics drives the wheels.
- **Honest ceiling [judgment]:** code can reach a correctly proportioned, correctly split, engine-ready vehicle at
  stylized-to-clean-mid-poly quality. It cannot reach photoreal body surfacing of a specific real car. No evidence
  of LLM-built bpy cars at that level was found. For realism, use a CC0 or bought body (or an AI body) and then
  split it with the procedure in §2.7: cut out the wheels, rebuild them procedurally and set the pivots.

## 2. Ready-to-use additions

### 2.1 Engine contract for wheeled vehicles (paste into engines/*.md + modeling.md)
| | Godot 4 | Unity (6.x) | three.js + Rapier | three.js + cannon-es |
|---|---|---|---|---|
| Body | `VehicleBody3D` (RigidBody3D). Its **origin = center of gravity, keep it low**: move the MeshInstance3D and CollisionShape3D up instead | Root GameObject + Rigidbody (tutorial: mass 1500 kg); body child has a **convex** MeshCollider | dynamic RigidBody + cuboid/convex collider | `CANNON.Body` + Box |
| Wheel physics | `VehicleWheel3D` child of the body, one per wheel. It acts as the raycast collider | `WheelCollider` on its **own GameObject, not a child of the wheel model**. It is a single raycast down local −Y | `DynamicRayCastVehicleController.addWheel(chassisConnectionCs, directionCs, axleCs, suspensionRestLength, radius)` | `RaycastVehicle.addWheel({radius, directionLocal, axleLocal, chassisConnectionPointLocal, suspensionRestLength, …})` |
| Wheel visual | MeshInstance3D child of the VehicleWheel3D (Godot demo `truck_town/car_base.tscn`). The body mesh "should generally not include meshes for the wheels" | Separate wheel model GameObject, posed every frame by script from the collider | Separate Object3D per wheel, posed from `wheelSuspensionLength/wheelSteering/wheelRotation(i)` | Copy `wheelInfos[i].worldTransform` after `updateWheelTransform(i)` |
| Wheel node origin | Place it at the **bottomed-out** wheel position, then `wheel_rest_length` lowers the wheel to rest. "Don't set this to 0.0 and move the wheel into position" | Wheel center + `suspensionDistance/2` (default 0.3 → +0.15) | Connection point is where the suspension ray starts. [inference] Put it at wheel center + rest length along up | same as Rapier |
| Forward | `Vector3.MODEL_FRONT` = +Z (matches glTF +Z) | +Z | `indexUpAxis` / `setIndexForwardAxis` (0 = x, 1 = y, 2 = z) | **Defaults: right = 2, forward = 0 (X!), up = 1.** Set forward = 2 and right = 0 for glTF assets |
| Starter numbers | `wheel_radius` = tire radius (default 0.5); travel 0.1–0.3; stiffness < 50 off-road, 50–100 race, ~200 F1; damping 0.3 compress / 0.5 relax (race 0.5); `suspension_max_force` > mass/4, good results at 3–4× that; `wheel_friction_slip` 1.0 to start; engine_force 25–50 and brake 25–30 for mass 1000 | radius from the model (demo 0.44); tutorial `steeringRange = 30` | — | WheelInfo defaults radius 1, rest length 1, stiffness 100, frictionSlip 10.5, rollInfluence 0.01 |
| Caveat | "known issues and isn't designed to provide realistic 3D vehicle physics" | Raycast wheels "pop" up steps. Keep the ground collision smooth | Apache-2.0 | MIT |
[Godot VehicleBody3D.xml / VehicleWheel3D.xml (master); Unity Manual 6.6 wheel-colliders-introduction + WheelColliderTutorial; rapier.js ray_cast_vehicle_controller.ts; cannon-es RaycastVehicle.ts + WheelInfo.ts]

The Godot demo `car_base.tscn` is a toy-scale minivan:
- Body = VehicleBody3D.
- Wheel1–4 are VehicleWheel3D nodes at x ±0.574, z +1.104 front / −0.783 rear, with `wheel_radius` 0.25,
  stiffness 40, `friction_slip` 1.0 and `roll_influence` 0.4. Each has a MeshInstance3D child that uses one
  shared `wheel.res` mesh.
- Body MeshInstance3D + CollisionShape3D + CameraBase. Only the front wheels have `use_as_steering`.

**Consequence for the model** [judgment derived from the above]:
- Wheels never need collision meshes. Physics is a raycast in all four engines.
- The body collision proxy must stay **above the ground-clearance line**, or the hull scrapes the ground.
- Export each wheel's radius and width with the asset (glTF extras, §2.6), so engine code configures the
  wheels from data instead of guesses.

### 2.2 Vehicle dimension table (mm; Wikipedia infobox wikitext fetched 2026-10-10; inches converted ×25.4)
| Class | Example (generation) | Length | Width (no mirrors) | Height | Wheelbase | L − WB (both overhangs) | Mass kg |
|---|---|---|---|---|---|---|---|
| City car | Kia Picanto (3rd gen) | 3595 | 1595 | 1485 | 2400 | 1195 | 836–945 |
| Compact hatch | VW Golf Mk8 | 4284 | 1789 | 1456 | 2636 | 1648 | 1255–1465 |
| Compact sedan | Toyota Corolla E210 saloon (intl) | 4630 | 1780 | 1435–1455 | 2700 | 1930 | — |
| Mid-size sedan | Toyota Camry XV70 | 4879–4910 | 1839 | 1445 | 2824 | ~2070 | 1480–1660 |
| Compact SUV | Toyota RAV4 XA50 | 4570–4600 | 1855 | 1660 [check: trims differ] | 2690 | ~1900 | — |
| Full-size SUV | Toyota Land Cruiser J300 | 4950–5015 | 1980–1990 | 1945 | 2850 | ~2130 | 2310–2645 |
| Full-size pickup | Ford F-150 (14th gen) SuperCrew | 5885–6185 | 2029 (Raptor 2200) | 1920–1971 | 3693–3993 | ~2190 | ≥ 1824 |
| Large van (US) | Ford Transit (2015+) | 5532–6759 | 2052–2126 | 2088–3051 | 3300 (regular) | — | — |
| Large van (EU) | Mercedes-Benz Sprinter (3rd gen) | 5425–7345 | — | 2435–3005 | — | — | — |
| Motorcycle | Yamaha MT-07 | 2085 | 745 | seat 805 | 1400 | — | 179–181 wet |
| Bicycle wheels | ISO bead-seat Ø | 622 = 700c/29er, 584 = 650B/27.5, 559 = 26", 406 = 20" BMX | outer Ø ≈ ISO + 2 × tire width | | | | |

**Wheel size from a tire code** (Wikipedia "Tire code": width mm / aspect = sidewall % of width / R rim inches):
`D_outer = rim_in × 25.4 + 2 × width × aspect/100`. Worked examples:
- 175/65R14 → 583 mm
- 205/55R16 → 632
- 225/45R17 → 634
- 235/45R18 → 669
- 225/65R17 → 724
- 275/65R18 → 815
- 235/65R16C (van) → 712
- moto 120/70R17 → 600, 180/55R17 → 630
- 700×25c bicycle → 672

Which tire each example model uses is [UNVERIFIED]. Pick by class: city 14–15", compact 16–17", sedan 16–18",
SUV 17–19", pickup 17–20".

**Rules of thumb [judgment, check against the model]:**
- Wheel center Z at rest = tire radius (ground at Z = 0).
- Track (center-to-center) ≈ body width − tire width − 20…40 mm, so the outer tire face sits just inboard of the
  arch lip. A Camry SE search snippet gives track 1580/1595 mm and clearance ~137 mm, tires 205/65R16 –
  235/40R19; this fits the rule within ~25 mm [UNVERIFIED: source pages blocked].
- Arch radius = tire radius + 25–50 mm (road), + 60–100 mm (off-road).
- Ground clearance: car 130–160, SUV 180–220, pickup 200–240 mm [UNVERIFIED typical].
- Max steer angle 30–35° (the Unity tutorial uses 30).

### 2.3 Vehicle recipe (code modeling, Blender headless). Brief first, then build.py
**Brief additions for vehicles:**
- class and dimension row (§2.2);
- tire code → radius and width;
- track front/rear, front-axle Y, arch radius, ground clearance, mass;
- camera (top-down / chase / cockpit) → interior level;
- which parts move: wheels always; doors/hood/trunk only if gameplay opens them;
- target engine;
- triangle budget split.

1. **Reference.** For a real model use orthographic blueprints only. Reject perspective sets: front and side
   won't line up.
   - Make a bbox cube of the real L×W×H and fit the side view to it.
   - Duplicate and rotate (front: −90° Z; top: −90° X then +90° Z) for the other views without rescaling.
   - Image empties: perspective display off, opacity on, the front image set to Front-only and the rear to
     Back-only, collection unselectable.
   [Enpix oiDEKMAy_Xs 00:01:58–00:09:25]
   - For headless runs, render the contact sheet *with* the blueprint empties visible in the ortho views, so the
     silhouette can be compared directly [judgment].
2. **Stations, not boxes.** Write a station table along the length (Y): bumper, hood leading edge, front axle,
   A-pillar base, roof front, B-pillar, roof rear, C-pillar base, deck, rear axle, rear bumper.
   - At each station record half-width, sill Z, beltline Z and top Z.
   - **Put stations on the panel seams** (door front and rear, hood and trunk lines, beltline) so every seam
     becomes an edge loop you can groove or split later [judgment].
3. **Body shell = loft** of rounded-section rings (≈ 12–16 verts per half; equal counts).
   - Add tumblehome: the greenhouse rings are narrower than the shoulder.
   - Build one half and use a Mirror at X = 0. The front faces −Y.
   - Topology runs front→back and is never fanned radially around an arch [Potter ub00akPm7kQ 00:02:16–00:03:02].
4. **Wheel arches.**
   - Cut the arches on the low-poly shell before the bevel: EXACT boolean with a cylinder (axis X, r = arch
     radius).
   - Add a 15–30 mm lip by extruding the arch edge outward [Potter 00:03:02–00:03:48].
   - Add a dark wheel-well liner (an inner half-cylinder) so the body never shows see-through gaps.
5. **Openings by inset, not glue.**
   - Windows: inset faces (boundary off), then inset depth 5–10 mm. Not a plain extrude [Potter 00:06:49–00:08:20].
   - Glass is a separate object with a black frit band 20–40 mm wide [judgment].
   - Lights, grille and plate are recesses. The lamp lens is its own mesh with an emissive material so brake and
     headlights can toggle.
6. **Panel gaps.**
   - Hero / mid-poly: a groove 3–5 mm wide and 4–8 mm deep on the seam loops.
   - Low-poly: texture or normal map only.
   - Opening panels: split along the seam loops (`split_part`), solidify 30–50 mm inward, add a dark jamb on the
     body side, origin on the hinge line.
7. **Wheel**, built once and instanced ×4 (linked data):
   - Tire: revolve a tire profile (bead → bulging sidewall → shoulder → tread) around X, 32–48 segments for
     hero/chase, 16–24 for low-poly.
   - Rim: revolve the barrel, then the spokes = one spoke duplicated by spin N = 5/6/10 times.
   - Brake disc: r ≈ rim radius − 30–40 mm, 25–30 mm thick.
   - **Caliper is a separate object that does not spin** (child of the steer pivot).
   - Origin at the axle center, axle along local X.
   - Right side = rotate 180° about Z, **never negative scale**.
8. **Interior by camera:**
   - top-down or tinted glass: none (black interior plane);
   - chase camera: seats, dash and steering-wheel block-in (≤ 15% of the budget);
   - cockpit: full [judgment].
9. **Details at about 1/60 of the length, clustered:** mirrors, handles (recessed), exhaust tips, wipers (hero
   only), badge as texture.
10. **Edges and normals:** the bevel bands and Weighted Normal from `modeling.md` §5.3. Car paint uses Principled
    with Coat → `KHR_materials_clearcoat` [UNVERIFIED in this run: exporter mapping not executed].
11. **Hierarchy, pivots, collision, sockets:** §2.4. Then validation (§2.6) and the engine wiring (§2.1).

**What is modeled vs. textured** [judgment + Potter]:
- Modeled: silhouette, arches, lips, glass inset, light recesses, grille recess, mirrors.
- Modeled at mid-poly and above, textured at low-poly: panel grooves, door handles.
- Always texture or normal map: tread pattern, sidewall lettering, badges, disc holes, lamp reflectors, grille mesh.

**Budget split [judgment]** for a 10k-tri chase-cam car: body + glass 45%, 4 wheels 30% (≈ 750 each), lights and
details 15%, interior 10%. Wheels are the easiest place to overspend: 4 × a 3k wheel is already 12k.

| Use | Triangles per car | Source |
|---|---|---|
| GTA V (L0 / L1 / L2 / L3 / L4) | 60–120k / 20–30k / 10–15k / 5–10k / 0.5–1k | modding-forum LOD guide (verified) |
| PGR3 2005 (PGR2) | 85–105k polys incl. interior (≈ 10k) | bit-tech (verified) |
| Mobile hero car | ~20–25k | Unity forum [UNVERIFIED, page blocked] |
| Web chase-cam hero / traffic / top-down stylized | 8–20k / 2–6k / 0.5–3k | [judgment] |

### 2.4 Bill of materials, hierarchy and pivots (Blender Z-up, front −Y → glTF +Y up, front +Z)
```
VEH_<Name>          Empty. Origin = ground (Z=0) center, midway between the axles. Custom props: spec (§2.6)
├─ Body             loft shell + arches + recesses; mat paint/trim
│  ├─ Glass         split from greenhouse, inset; mat glass (or opaque tinted for low-poly)
│  ├─ Lights_F / Lights_R   lens meshes; emissive mats (toggle)
│  ├─ Door_FL …     ONLY if it opens. Origin on the hinge axis (front door edge), local Z = hinge axis
│  ├─ Hood / Trunk  ONLY if it opens. Origin on the hinge line (windscreen base / rear-window base), local X = axis
│  └─ Interior      per camera
├─ Steer_FL / Steer_FR    Empty at wheel center (≈ kingpin). Rotates about Z (±30–35°)
│  ├─ Wheel_FL      tire + rim + disc (one mesh). Origin = axle center; spins about local X
│  └─ Caliper_FL    does NOT spin
├─ Wheel_RL / Wheel_RR (+ Caliper_RL/RR)  directly under the root
├─ COL_Body-colonly convex hull or 1–3 boxes, bottom ≥ ground clearance (Godot suffix; Unreal UCX_)
└─ SOCKET_* empties: Seat_Driver, Cam_Chase, Exhaust_L/R, Headlight_L/R, Tow
```
- Side suffixes `_FL _FR _RL _RR` everywhere. Rigacar uses `.Ft.L/.Bk.R`; either is fine, but be consistent.
- Engines re-parent wheels under their own wheel nodes (§2.1), so the asset's job is a **correct origin and a
  clean name**. Keep the hierarchy shallow.
- Single-material wheels can be merged per wheel. Never merge wheels into the body.

### 2.5 Articulated-asset rules (doors, turrets, weapons, props): paste as a general section
1. **One moving part = one object.** Its origin sits on its motion axis. Its local axis is aligned to the motion
   (hinge = local Z or X, slide = local Y). The rest pose has identity local rotation.
2. Write the joint into custom props → glTF `extras` (export with `export_extras=True`):
   `{"joint":"hinge","axis":"Z","min_deg":0,"max_deg":70}` or `{"joint":"slide","axis":"Y","max_m":0.35}` or
   `{"joint":"spin","axis":"X"}`. The engine script reads it; nothing is guessed.
3. Set origins **before** parenting and before instancing linked data. A data-level origin move changes every
   user of the mesh.
4. Pivot placements:
   - **Door** (building or vehicle): hinge edge, at the mid-height of the hinge line.
   - **Drawer**: closed position, slides along its depth axis.
   - **Turret**: yaw pivot at the turret-ring center. The gun is a child with its pitch pivot at the trunnion.
   - **Weapon**: slide, bolt, trigger, magazine and hammer each on their own axis, plus `SOCKET_Muzzle`,
     `SOCKET_Grip`, `SOCKET_Eject`.
   - **Lever / valve**: pivot at the shaft. **Cart / trolley wheel**: axle center.
   - **Character props** (sword, shield): pivot at the grip point, which matches the hand socket.
5. Clearance check: sweep every joint to its min and max (render or test intersections). Parts must not
   interpenetrate along the motion range (wheel vs. arch at full steer, door vs. body at max angle).
6. Moving parts may not touch the parent: the gap is intentional. The validator must exempt objects that carry a
   `joint` prop from the floating-part WARN, and check the pivot instead.
7. Collision: one simple proxy per *independently moving* rigid part that needs physics (door, turret). Never use
   the render mesh.

### 2.6 Helper functions a modeling library (`gs_model.py`) should provide
All are bmesh/data-API based (no `bpy.ops` where avoidable). Signatures are a proposal [judgment]. Verify the API
names on the installed Blender: bpy was not runnable in this sandbox.
```python
tire_dims(code: str) -> dict                       # "205/55R16" -> {outer_r, width, rim_r} (m)
vehicle_spec(cls: str, **over) -> dict             # §2.2 row + derived track/arch/axle Y; JSON-serializable
blueprint_setup(images: dict[str, str], L: float, W: float, H: float) -> dict[str, Object]  # ortho-only image empties
section_ring(half_w, z_bottom, z_top, n=12, exponent=2.5, tumble=0.0) -> list[Vector]       # rounded body section
loft(rings: list[list[Vector]], name: str, cap=True, mirror_x=True) -> Object                # equal-count rings
revolve(profile_rz: list[tuple[float, float]], name, segments=32, axis="X", weld=True) -> Object  # bmesh.ops.spin
sweep(profile: list[Vector], path: list[Vector], name, twist=0.0) -> Object
radial_duplicate(obj, count: int, axis="X") -> Object                                       # spokes, bolts
inset_recess(obj, face_pred, inset: float, depth: float) -> list[int]                      # windows, lights, grille
groove_loop(obj, edge_pred, width=0.004, depth=0.006) -> None                              # panel gap on a seam loop
cut_arch(body, center: Vector, radius: float, width: float, lip=0.02) -> None              # EXACT boolean + lip + liner
make_wheel(code: str, spokes=5, segments=32, disc=True) -> tuple[Object, Object]           # (wheel, caliper); origin = axle
place_wheels(proto, spec: dict, root) -> dict[str, Object]                                 # linked copies, R side rot 180° Z
split_part(obj, vert_pred, name: str, solidify=0.0) -> Object                              # doors/hood from seam loops
separate_cylinder(obj, center, axis, radius, half_width, name) -> Object                   # cut wheels out of AI/fused mesh
set_origin(obj, world_pt: Vector) -> None                                                  # data-level; see snippet
set_pivot(obj, origin: Vector, axis: Vector, up: Vector) -> None                          # origin + local frame on hinge
set_joint(obj, kind: str, axis: str, lo: float, hi: float) -> None                         # custom props -> glTF extras
collision_proxy(objs, kind="convex"|"boxes", min_z: float = 0.0, suffix="-colonly") -> Object
add_socket(name: str, loc: Vector, rot=(0, 0, 0), parent=None) -> Object
validate_vehicle(root, spec) -> dict   # 4 wheels found; wheel origin within 2 mm of the wheel bbox center;
                                       # tire bottom Z within ±5 mm of 0; arch clearance at ±max_steer; L/W/H/WB within
                                       # ±3 % of spec; no negative scale; names match pattern; COL present, bottom
                                       # ≥ clearance; extras present
joint_sweep_sheet(root, out_dir, steps=3) -> str   # top + side renders at min/mid/max of every joint
```
`set_origin` (load-bearing: no ops, works headless):
```python
def set_origin(obj, world_pt):
    mw = obj.matrix_world.copy(); local = mw.inverted() @ world_pt
    obj.data.transform(Matrix.Translation(-local))      # affects every user of a linked mesh
    obj.matrix_world = mw @ Matrix.Translation(local)   # children follow: set origins before parenting
```

### 2.7 Realistic route: CC0/bought/AI body + procedural functional parts
- **Loose-part kits** (CC0 packs, bought models): `separate(type='LOOSE')` or `'MATERIAL'`. Then rename to the §2.4
  scheme, `set_origin` each wheel to its bbox center, and build the hierarchy and collision.
- **Fused mesh** (image-to-3D, scans: the Higgsfield complaint). Wheels cannot simply be "found". Use this order:
  1. Scale to the real length, front to −Y, ground at Z = 0.
  2. From the spec (wheelbase, track, radius) run `separate_cylinder` at the 4 wheel positions and delete the result.
  3. Add arch liners to hide the holes.
  4. Insert `make_wheel` instances with the exact radius.
  5. Keep doors closed. Cutting doors from a shell with no inner geometry exposes holes, so build a jamb and inner
     panel or don't open them [judgment].
  6. Glass and lights are only separable if the generator emitted materials. Otherwise re-model them as recessed
     separate meshes.
- **Part-aware generators**, which output parts instead of one blob:
  - PartCrafter (MIT, NeurIPS 2025, "jointly generates multiple parts ... from a single RGB image").
  - Hunyuan3D-Part (P3-SAM segmentation + X-Part completion; "Tencent Hunyuan 3D-Part Community License",
    2025-09-23; territory terms [UNVERIFIED]).
  - NVIDIA PartPacker (license file not at repo root [UNVERIFIED]).

  None gives pivots, hinges or exact wheel radii. The steps above still apply. Quality on vehicles is
  [UNVERIFIED]: not tested.

## 3. Never-do list
| Never | Why / evidence |
|---|---|
| Wheels fused into the body mesh | Godot: the body model "should generally not include meshes for the wheels". Unity: model and collider "need to be on two separate GameObjects" |
| Wheel origin anywhere but the axle center | The wheel wobbles when spun. The Unity collider must be centered on the wheel model |
| Right-side wheels by negative scale | Flips normals, and the inspector FAILs negative scale. Rotate 180° about Z |
| Caliper inside the spinning wheel node | It would spin with the wheel. It belongs to the steer pivot |
| Render mesh as the vehicle collider; a hull below the clearance line | Unity tutorial uses a convex body collider. Raycast wheels mean the hull must ride above the ground |
| cannon-es vehicle with default axes on a glTF car | Default `indexForwardAxis = 0` (X), and glTF fronts are +Z (source) |
| Godot `wheel_rest_length = 0` with the wheel moved into place | Explicitly warned against in VehicleWheel3D docs |
| Bumpy ground collision under raycast cars | Unity manual: wheels clip and then "pop" on steps |
| Radial polygon fan around the wheel arch | Breaks the body's shading flow [Potter 00:02:16] |
| Perspective "blueprints" | Front and side views can't both be matched [Enpix 00:00:40] |
| Guessed size / wheel size | Use §2.2 and `tire_dims`. A Corolla is 4.63 m, not "about 4" |
| Opening doors cut from a hollow fused AI mesh | Exposes holes. Needs jamb and inner panel geometry [judgment] |
| Treating a separated wheel's "floating" WARN as a defect | It is intended. Validate the pivot and ground contact instead |

## 4. Gaps and unverified items
- **Validator change needed:** `inspect_model.py` floating check (largest-island contact graph, `--contact-tol`
  0.002) flags wheels and glass inset with a gap. It should exempt joint-tagged parts and add vehicle checks.
- Track width and ground clearance: no primary source opened (auto123 timed out; the Toyota PDF on priuschat
  returned HTML). The Camry numbers are a search snippet only.
- RAV4 XA50 height (1660) came from a section-scoped regex. Trims differ; check it.
- Mobile and web polycounts: Unity forum page blocked. Asset-store "7–10k" is a search snippet.
- LLM-built vehicle quality: no benchmark or demo found. Two YouTube demos (Claude + Blender MCP F1 / "GTA6":
  qlhE6Sd7dec, b36wBJzS9Og) were found, but their transcripts failed to download. Not assessed.
- No open-source procedural car/wheel bpy generator found. The GitHub search API is blocked in this session
  (403 "bound to configured repositories"). Rigacar's Blender 4.x/5.x compatibility was not checked
  (bl_info says 2.83).
- `KHR_materials_clearcoat` export mapping, `export_extras` and `bmesh.ops.spin(use_duplicate=…)`: not executed
  (bpy not installed here). Verify on the user's Blender.
- License plate (EU 520×110, US 305×152 mm), door opening angles and the EU/US truck width limits were not
  verified. Omitted from the tables.

## 5. Sources (all opened unless marked)
- Godot class docs (source XML): https://raw.githubusercontent.com/godotengine/godot/master/doc/classes/VehicleBody3D.xml ,
  …/VehicleWheel3D.xml
- Godot demo: https://raw.githubusercontent.com/godotengine/godot-demo-projects/master/3d/truck_town/vehicles/car_base.tscn
- Unity Manual 6.6: https://docs.unity3d.com/Manual/wheel-colliders-introduction.html ;
  https://docs.unity3d.com/Manual/WheelColliderTutorial.html
- Rapier.js: https://raw.githubusercontent.com/dimforge/rapier.js/master/src.ts/control/ray_cast_vehicle_controller.ts (Apache-2.0)
- cannon-es: https://raw.githubusercontent.com/pmndrs/cannon-es/master/src/objects/RaycastVehicle.ts , …/WheelInfo.ts (MIT)
- Rigacar: https://github.com/digicreatures/rigacar (README, __init__.py bl_info v7.1 / Blender 2.83, car_rig.py; GPL-3)
- Wikipedia wikitext via API (2026-10-10): Kia Picanto; Volkswagen Golf Mk8; Toyota Corolla (E210); Toyota Camry (XV70);
  Toyota RAV4 (#XA50); Toyota Land Cruiser (J300→redirect); Ford F-Series (fourteenth generation); Ford Transit;
  Mercedes-Benz Sprinter; Yamaha MT-07; Tire code; Bicycle wheel
- GTA V LODs: https://www.modding-forum.com/guide/1-lod-models/ ; PGR3: https://bit-tech.net/news/gaming/pgr3_poly_count_lie/1/
- Video: Enpix "The Perfect Car Blueprints Setup in Blender" https://www.youtube.com/watch?v=oiDEKMAy_Xs (00:00:40–00:09:25)
- Video: Thomas Potter "The Ultimate Low Poly Car Guide in Blender" https://www.youtube.com/watch?v=ub00akPm7kQ (00:01:31–00:09:05)
- Part generation: https://github.com/wgsxm/PartCrafter (README + MIT LICENSE); https://github.com/Tencent-Hunyuan/Hunyuan3D-Part
  (README + LICENSE header); https://github.com/NVlabs/PartPacker (README only)
- Not opened / blocked: Camry spec (auto123, priuschat PDF), Unity mobile poly thread, the 2 Claude+Blender MCP videos.
- Downloads: SCRATCH/downloads2/4/
