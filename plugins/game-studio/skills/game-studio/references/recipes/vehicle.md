# Vehicle: shape plus four controllable wheels

Use [modeling](../modeling.md), [articulated parts](articulated.md) and the engine's actual vehicle API.
The bundled `scripts/blender/examples/car_stylized.py` is a structural example, not a promise of a
finished realistic car or separate native objects for every static detail. Record whether the target
is stylized, realistic, chase-camera or cockpit.

**Brief contract:** verified or deliberately fictional length/width/height, wheelbase/track, tire radius/
width, axle positions, ground clearance, front axis, camera, opening panels, sockets, material/triangle
budget and collider strategy. Tire dimensions can come from `gb.tire_dims`; do not guess from the mesh.

**Minimum hierarchy** (case-sensitive names agreed with game code):

```text
VEH_<id>                  asset ground/root; physics center of mass is a separate engine decision
  Body                    lofted shell; windows/arches/recesses owned by this rigid part
  Steer_FL / Steer_FR      joint steer; each at its wheel center
    Wheel_FL / Wheel_FR   separate spin nodes; local X axle; origins on axle center
  Wheel_RL / Wheel_RR     separate spin nodes
  Body-colonly            simple chassis proxy above ground-clearance line
  SOCKET_seat_driver / SOCKET_cam_chase / SOCKET_exhaust
```

1. Match orthographic reference proportions with a station table along the length: width, sill,
   beltline and roof at each station. Loft coherent sections; reject a detailed wrong silhouette.
2. Cut arches before bevels, with liners hiding the shell interior. Check the **swept tire envelope**
   at full steer/suspension travel, not an arbitrary universal gap.
3. Recess glass/lights/grille; only split doors/hood when gameplay opens them. Opening panels need
   jamb/interior faces and a hinge, not holes cut out of a fused shell.
4. Build one wheel from revolved tire/rim profiles, share geometry when appropriate, keep four objects.
   Right-side wheels use rotation, not negative scale. Calipers stay outside the spinning node.
5. Allocate detail by camera: chase-car silhouette/arches/mirrors first; cockpit needs a real interior.
   Panel grooves/tread/badges may be textures at low budgets. Budget **all four wheels** together.
6. Join only an export copy within each rigid part. Preserve source parts, joint metadata, socket names
   and enough hierarchy for engine wheel poses. [Texture route](../texturing.md) must preserve light toggles.

**Checks:** `inspect_model.py MODEL --parts 'Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR' --part-pivot center
--sockets seat_driver,cam_chase,exhaust` plus project dimensions/budgets; inspect `parts`/ortho sheets;
spin every wheel and sweep steering/panels in the engine. Verify imported axes, clearances and shadows.
Names/pivot-center checks do not prove the axle direction or swept clearance; show motion evidence.

Raycast-wheel designs normally use separate wheel visuals, chassis collider and engine wheel/controller
nodes; their suspension/axis conventions differ. Godot's built-in vehicle nodes document realism limits.
Do not assume a DCC ground-root is the physics center of mass, or a wheel visual needs its own collider.

Basis: original adaptation of round-2 report 04 and the bundled example. Budgets/clearances are selected
per project; production realism and each target-engine vehicle integration remain separately tested.
