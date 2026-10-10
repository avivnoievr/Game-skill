# Modular kit: a snapping and seam contract

Specify grid/module sizes, pivot rule, axis frame, player/camera clearances, visible joint treatment,
material family and each piece's budget. Use [level metrics](../level-design.md), not a copied room size.
Corner-on-floor pivots suit snapping; record any different rule so the placement tool can consume it.

**Minimum family** only as required by this level: wall, door/window wall, inner/outer corner, floor/
edge, stairs, pillar/roof/trim. Write edge dimensions and neighbor compatibility before detail.
Build from profiles with `gs_build`; share a [trim/palette route](../texturing.md) across the family.

1. Place a player/camera clearance reference beside the greybox assembly.
2. Snap mating boundaries to the declared grid/tolerance; preserve those boundaries through bevel,
   optimization and LOD. Use explicit reveals or overlap rules to hide joints without z-fighting.
3. Create simple collision/navigation shapes and metadata; visual openings must agree with traversal.
4. Retain individual source modules and functional pieces. Instancing identical modules reduces
   repeated geometry; material unification does not guarantee instancing or fewer calls.
5. Export copies with stable node/material names and test the engine import/snapping route.

**Gate fixture:** assemble an L-shaped room, two adjacent floors, inner/outer corner, door and stairs.
Inspect top/3/4/gameplay views, grazing light and a checker material. Traverse seams/thresholds, turn the
camera through corners and sweep the door. No cracks, z-fighting, shifted pivots, reversed normals or
inconsistent texture direction/density. Test relevant LOD transitions at shared borders.

Required evidence: dimension/edge table; assembled fixture and input route; exported budget/UV/material
counts. A single attractive module is not an approved kit. Preserve snapping constraints when reducing
triangles; rerun the assembly after every geometry-affecting export change.

Basis: original recipe from round-2 gap audit §3D; numerical grid/clearance values are project decisions,
not a universal architectural standard.
