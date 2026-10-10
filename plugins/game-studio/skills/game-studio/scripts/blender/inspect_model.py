"""Game-readiness inspection for a 3D asset. Prints a report and exits non-zero on FAIL.

Usage (Blender):  blender -b --factory-startup --python inspect_model.py -- MODEL [options]
Usage (pip bpy):  python inspect_model.py MODEL [options]

Options:
  --preset NAME          budget preset (see PRESETS below; overridden by explicit flags)
  --max-tris N           triangle budget for the whole asset
  --max-materials N      material budget (each material ~ one draw call per mesh)
  --max-texture PX       largest allowed texture edge in pixels
  --expect-height M      expected height in meters (Z extent), checked within +-10% / +-25%
  --expect-dims X,Y,Z    expected extents in meters (any axis may be 0 to skip)
  --texel-density PX/M   target texel density; reported deviation beyond +-35% is a WARN
  --pivot base|center|any  expected origin placement (default: base for props/characters)
  --contact-tol M        gap in meters below which separate pieces count as touching (default 0.002)
  --parts GLOBS          required render parts, comma-separated exact names or shell-style globs
  --part-pivot center|any  spin joints check centers by default; explicit center also checks untagged required parts
  --part-pivot-tol M     center tolerance floor in meters (default 0.005)
  --part-pivot-ratio F   center tolerance relative to largest part extent (default 0.02)
  --sockets NAMES        required empty attachment nodes; SOCKET_ prefix optional
  --json PATH            also write the full report as JSON

Exit codes: 0 = no FAIL, 1 = at least one FAIL, 2 = usage/load error.
"""
import argparse
import fnmatch
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402  (import before bmesh/mathutils: required by the PyPI bpy module)
import bmesh  # noqa: E402
import numpy as np  # noqa: E402  (bundled with Blender and with the bpy wheel)
from mathutils import Vector  # noqa: E402
from mathutils.bvhtree import BVHTree  # noqa: E402

from gs_common import (collision_objects, hierarchy_rows, joint_of, load_model, mesh_objects,
                       rigid_group, round_vec, script_args, world_bbox)  # noqa: E402

# Starting points only. The project's art bible / tech budget is the authority:
# pass explicit flags when it says otherwise.
PRESETS = {
    "web-prop-small": {"max_tris": 1000, "max_materials": 1, "max_texture": 512},
    "web-prop": {"max_tris": 3000, "max_materials": 2, "max_texture": 1024},
    "web-hero-prop": {"max_tris": 8000, "max_materials": 2, "max_texture": 2048},
    "web-character": {"max_tris": 10000, "max_materials": 3, "max_texture": 2048},
    "web-building": {"max_tris": 10000, "max_materials": 3, "max_texture": 2048},
    "mobile-prop": {"max_tris": 1500, "max_materials": 1, "max_texture": 512},
    "mobile-character": {"max_tris": 6000, "max_materials": 2, "max_texture": 1024},
    "desktop-prop": {"max_tris": 15000, "max_materials": 3, "max_texture": 2048},
    "desktop-character": {"max_tris": 40000, "max_materials": 5, "max_texture": 4096},
}

MERGE_DIST = 1e-5   # weld split vertices (UV seams / hard edges in glTF) before topology checks
AREA_EPS = 1e-10


class Report:
    def __init__(self):
        self.checks = []

    def add(self, level, check, message, obj=None):
        self.checks.append({"level": level, "check": check, "object": obj, "message": message})

    def count(self, level):
        return sum(1 for c in self.checks if c["level"] == level)


def parse():
    p = argparse.ArgumentParser(prog="inspect_model.py", description=__doc__.split("\n")[0])
    p.add_argument("model")
    p.add_argument("--preset", choices=sorted(PRESETS))
    p.add_argument("--max-tris", type=int)
    p.add_argument("--max-materials", type=int)
    p.add_argument("--max-texture", type=int)
    p.add_argument("--expect-height", type=float)
    p.add_argument("--expect-dims")
    p.add_argument("--texel-density", type=float)
    p.add_argument("--pivot", choices=["base", "center", "any"], default="base")
    p.add_argument("--contact-tol", type=float, default=0.002)
    p.add_argument("--parts", default="")
    p.add_argument("--part-pivot", choices=["center", "any"], default=None)
    p.add_argument("--part-pivot-tol", type=float, default=0.005)
    p.add_argument("--part-pivot-ratio", type=float, default=0.02)
    p.add_argument("--sockets", default="")
    p.add_argument("--json")
    a = p.parse_args(script_args())
    a.part_pivot_explicit = a.part_pivot is not None
    a.part_pivot = a.part_pivot or "center"
    if any(not math.isfinite(v) or v < 0 for v in (a.contact_tol, a.part_pivot_tol, a.part_pivot_ratio)):
        p.error("contact and part-pivot tolerances must be finite and nonnegative")
    budget = dict(PRESETS.get(a.preset, {}))
    for k in ("max_tris", "max_materials", "max_texture"):
        if getattr(a, k) is not None:
            budget[k] = getattr(a, k)
    a.budget = budget
    return a


def tolerance_level(actual, expected, warn=0.10, fail=0.25):
    if expected <= 0:
        return "PASS"
    dev = abs(actual - expected) / expected
    return "PASS" if dev <= warn else ("WARN" if dev <= fail else "FAIL")


def image_textures(mat):
    if not mat or not mat.node_tree:
        return []
    return [n.image for n in mat.node_tree.nodes if n.type == "TEX_IMAGE" and n.image]


def analyze_mesh(obj, deps, rep):
    oe = obj.evaluated_get(deps)
    me = oe.to_mesh()
    stats = {"name": obj.name, "vertices": len(me.vertices), "faces": len(me.polygons)}
    stats["triangles"] = sum(len(p.vertices) - 2 for p in me.polygons)
    stats["uv_layers"] = len(me.uv_layers)
    stats["materials"] = [s.material.name if s.material else None for s in obj.material_slots]
    stats["color_attributes"] = len(me.color_attributes)

    # World-space surface area and UV area (active UV layer) for texel density / overlap heuristics.
    me.calc_loop_triangles()
    n_tris = len(me.loop_triangles)
    tri_verts = np.empty(n_tris * 3, dtype=np.int32)
    me.loop_triangles.foreach_get("vertices", tri_verts)
    co = np.empty(len(me.vertices) * 3, dtype=np.float64)
    me.vertices.foreach_get("co", co)
    mw = np.array(oe.matrix_world)
    co = co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3]
    v = co[tri_verts.reshape(-1, 3)]
    world_area = float(0.5 * np.linalg.norm(np.cross(v[:, 1] - v[:, 0], v[:, 2] - v[:, 0]), axis=1).sum())
    has_uv = me.uv_layers.active is not None and n_tris > 0
    uv_area = 0.0
    stats["uv_bounds"] = None
    if has_uv:
        tri_loops = np.empty(n_tris * 3, dtype=np.int32)
        me.loop_triangles.foreach_get("loops", tri_loops)
        uvs = np.empty(len(me.loops) * 2, dtype=np.float64)
        me.uv_layers.active.data.foreach_get("uv", uvs)
        t = uvs.reshape(-1, 2)[tri_loops.reshape(-1, 3)]
        uv_area = float(0.5 * np.abs((t[:, 1, 0] - t[:, 0, 0]) * (t[:, 2, 1] - t[:, 0, 1])
                                     - (t[:, 2, 0] - t[:, 0, 0]) * (t[:, 1, 1] - t[:, 0, 1])).sum())
        flat = t.reshape(-1, 2)
        stats["uv_bounds"] = [round_vec(flat.min(axis=0)), round_vec(flat.max(axis=0))]
    stats["surface_area_m2"] = round(world_area, 4)
    stats["uv_area"] = round(uv_area, 4) if has_uv else None

    # Topology checks on a welded copy (glTF splits vertices at seams, which would look like holes).
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=MERGE_DIST)
    bm.normal_update()
    stats["ngons"] = sum(1 for f in bm.faces if len(f.verts) > 4)
    stats["boundary_edges"] = sum(1 for e in bm.edges if e.is_boundary)
    stats["nonmanifold_edges"] = sum(1 for e in bm.edges if len(e.link_faces) > 2)
    stats["wire_edges"] = sum(1 for e in bm.edges if e.is_wire)
    stats["loose_vertices"] = sum(1 for v in bm.verts if not v.link_edges)
    stats["zero_area_faces"] = sum(1 for f in bm.faces if f.calc_area() < AREA_EPS)
    stats["flipped_normal_edges"] = sum(1 for e in bm.edges if e.is_manifold and not e.is_contiguous)
    closed = stats["boundary_edges"] == 0 and stats["nonmanifold_edges"] == 0 and len(bm.faces) > 0
    signed_volume = 0.0
    if closed:
        for f in bm.faces:
            vs = [v.co for v in f.verts]
            for i in range(1, len(vs) - 1):
                signed_volume += vs[0].dot(vs[i].cross(vs[i + 1])) / 6.0
    stats["closed"] = closed
    stats["signed_volume"] = round(signed_volume, 6) if closed else None
    bm.free()
    oe.to_mesh_clear()

    n = obj.name
    if stats["flipped_normal_edges"]:
        rep.add("FAIL", "normals", f"{stats['flipped_normal_edges']} edges join faces with opposite winding "
                "(flipped normals -> holes with backface culling). Recalculate outside.", n)
    if closed and signed_volume < 0:
        rep.add("FAIL", "normals", "closed mesh has negative volume: normals point inward.", n)
    if stats["nonmanifold_edges"]:
        rep.add("WARN", "topology", f"{stats['nonmanifold_edges']} edges shared by >2 faces (non-manifold).", n)
    if stats["loose_vertices"] or stats["wire_edges"]:
        rep.add("WARN", "topology", f"{stats['loose_vertices']} loose vertices, {stats['wire_edges']} wire edges "
                "(stray geometry; delete loose).", n)
    if stats["zero_area_faces"]:
        rep.add("WARN", "topology", f"{stats['zero_area_faces']} zero-area faces (degenerate; dissolve).", n)
    if stats["ngons"]:
        rep.add("INFO", "topology", f"{stats['ngons']} n-gons (fine for static props; avoid on deforming meshes).", n)
    if stats["boundary_edges"]:
        rep.add("INFO", "topology", f"{stats['boundary_edges']} open boundary edges (ok for planes/cards/hidden "
                "faces; otherwise a hole).", n)

    has_textures = any(image_textures(s.material) for s in obj.material_slots)
    if has_textures and not has_uv:
        rep.add("FAIL", "uv", "uses image textures but has no UV map.", n)
    elif has_uv and uv_area > 1.05:
        rep.add("WARN", "uv", f"UV area {uv_area:.2f} > 1.0: overlapping or tiling UVs (fine for tiling/mirrored "
                "trims; wrong for unique bakes/lightmaps).", n)
    if not obj.material_slots or all(s.material is None for s in obj.material_slots):
        rep.add("WARN", "material", "no material assigned (renders as engine default grey).", n)

    s = obj.matrix_world.to_scale()
    if obj.matrix_world.determinant() < 0:
        rep.add("FAIL", "transform", "negative scale (mirrored): flips normals in engines. Apply scale.", n)
    elif any(abs(c - 1.0) > 1e-4 for c in s) and obj.parent is None:
        rep.add("WARN", "transform", f"unapplied scale {round_vec(s)}. Apply transforms before export.", n)
    return stats, world_area, uv_area


def floating_parts(meshes, deps, tol, rep, max_islands=200):
    """Islands (connected surface pieces, all objects, world space) that do not touch the main body.

    Builds a contact graph: two islands touch when their triangles intersect or a sampled vertex of one
    lies within `tol` metres of the other. Islands not connected to the largest island are floating.
    """
    islands = []
    for obj in meshes:
        oe = obj.evaluated_get(deps)
        me = oe.to_mesh()
        bm = bmesh.new()
        bm.from_mesh(me)
        oe.to_mesh_clear()
        bm.transform(obj.matrix_world)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=MERGE_DIST)
        seen = set()  # BMesh elements are hashable; indices are stale after remove_doubles
        for f in bm.faces:
            if f in seen:
                continue
            stack, comp = [f], []
            seen.add(f)
            while stack:
                cur = stack.pop()
                comp.append(cur)
                for e in cur.edges:
                    for nf in e.link_faces:
                        if nf not in seen:
                            seen.add(nf)
                            stack.append(nf)
            index = {}
            polys = []
            for face in comp:
                polys.append([index.setdefault(v, len(index)) for v in face.verts])
            coords = [None] * len(index)
            for v, i in index.items():
                coords[i] = v.co.copy()
            pts = np.array([tuple(c) for c in coords])
            islands.append({"object": obj.name, "pts": pts, "tree": BVHTree.FromPolygons(coords, polys),
                            "lo": pts.min(axis=0) - tol, "hi": pts.max(axis=0) + tol,
                            "faces": len(comp)})
            if len(islands) > max_islands:
                bm.free()
                rep.add("INFO", "floating", f"more than {max_islands} separate pieces; floating-part check skipped.")
                return
        bm.free()
    if len(islands) < 2:
        return

    def touch(a, b):
        if np.any(a["hi"] < b["lo"]) or np.any(b["hi"] < a["lo"]):
            return False
        if a["tree"].overlap(b["tree"]):
            return True
        small, big = (a, b) if len(a["pts"]) <= len(b["pts"]) else (b, a)
        step = max(1, len(small["pts"]) // 400)
        return any(big["tree"].find_nearest(Vector(p), tol)[0] is not None for p in small["pts"][::step])

    n = len(islands)
    adj = {i: set() for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            if touch(islands[i], islands[j]):
                adj[i].add(j)
                adj[j].add(i)
    main = max(range(n), key=lambda i: islands[i]["faces"])
    reached, stack = {main}, [main]
    while stack:
        for k in adj[stack.pop()] - reached:
            reached.add(k)
            stack.append(k)
    loose = [islands[i] for i in range(n) if i not in reached]
    if loose:
        where = "; ".join(f"{p['object']} piece at {round_vec((p['lo'] + p['hi']) / 2, 2)} ({p['faces']} faces)"
                          for p in loose[:6])
        rep.add("WARN", "floating", f"{len(loose)} of {n} separate pieces do not touch the main body within "
                f"{tol * 1000:.0f} mm (floating parts read as bugs unless intentionally detached): {where}")


def inspect_parts(meshes, a, rep):
    """Required nodes plus pivot evidence. Hinge/steer/slide origins are never assumed to be centers."""
    objects = list(bpy.context.scene.objects)
    required = set()
    for pattern in filter(None, (v.strip() for v in a.parts.split(","))):
        matches = [o for o in objects if fnmatch.fnmatchcase(o.name, pattern)
                   and o.type in {"MESH", "EMPTY"} and o not in collision_objects()]
        if not matches:
            rep.add("FAIL", "parts", f"required part pattern {pattern!r} matches no render node")
        for obj in matches:
            descendants = set(obj.children_recursive)
            geometry = [m for m in meshes if m == obj or m in descendants]
            if not geometry:
                rep.add("FAIL", "parts", "required part has no renderable mesh geometry", obj.name)
            else:
                required.add(obj.name)
                rep.add("PASS", "parts", f"required part matches {pattern!r}", obj.name)

    groups = {}
    for obj in meshes:
        groups.setdefault(rigid_group(obj, required), []).append(obj)
    parts = []
    for obj in objects:
        joint = joint_of(obj)
        if not joint and obj.name not in required:
            continue
        geometry = groups.get(obj.name, [])
        entry = {"name": obj.name, "joint": joint, "axis": obj.get("axis"),
                 "origin": round_vec(obj.matrix_world.translation, 6),
                 "meshes": [m.name for m in geometry]}
        if joint:
            if joint not in {"spin", "steer", "hinge", "slide"}:
                rep.add("WARN", "joint", f"unknown joint kind {joint!r}", obj.name)
            if obj.get("axis") not in {"X", "Y", "Z"}:
                rep.add("FAIL", "joint", "joint must declare local axis X, Y or Z", obj.name)
        check_center = a.part_pivot == "center" and (joint == "spin" or (not joint and a.part_pivot_explicit))
        if check_center:
            if not geometry:
                rep.add("FAIL", "part_pivot", "no rigid-group geometry for bounds-center check", obj.name)
            else:
                lo, hi = world_bbox(geometry)
                error = ((lo + hi) / 2 - obj.matrix_world.translation).length
                tolerance = max(a.part_pivot_tol, max(hi - lo) * a.part_pivot_ratio)
                entry.update({"bounds_min": round_vec(lo, 6), "bounds_max": round_vec(hi, 6),
                              "pivot_distance_m": round(error, 6), "pivot_tolerance_m": round(tolerance, 6)})
                rep.add("PASS" if error <= tolerance + 1e-8 else "FAIL", "part_pivot",
                        f"bounds-center distance {error:.6f} m / tolerance {tolerance:.6f} m "
                        "(max of absolute floor and relative extent)", obj.name)
        parts.append(entry)

    sockets = []
    for name in filter(None, (v.strip() for v in a.sockets.split(","))):
        full = name if name.startswith("SOCKET_") else f"SOCKET_{name}"
        obj = bpy.context.scene.objects.get(full)
        if obj is None or obj.type != "EMPTY":
            rep.add("FAIL", "socket", f"required empty attachment node {full!r} is missing")
        else:
            rep.add("PASS", "socket", "required attachment node exists", full)
            sockets.append(full)
    return parts, groups, sockets


def collision_report(deps, rep):
    rows = []
    for obj in collision_objects():
        oe = obj.evaluated_get(deps)
        mesh = oe.to_mesh()
        triangles = sum(len(p.vertices) - 2 for p in mesh.polygons)
        oe.to_mesh_clear()
        lo, hi = world_bbox([obj])
        rows.append({"name": obj.name, "triangles": triangles,
                     "dimensions_m": round_vec(hi - lo), "origin": round_vec(obj.matrix_world.translation, 6)})
        if triangles > 500:
            rep.add("WARN", "collision", f"collision proxy has {triangles} triangles (>500); simplify it", obj.name)
    return rows


def main():
    a = parse()
    try:
        load_model(a.model)
    except SystemExit:
        raise
    except Exception as e:  # importer errors
        print(f"error: could not load {a.model}: {e}", file=sys.stderr)
        sys.exit(2)

    rep = Report()
    deps = bpy.context.evaluated_depsgraph_get()
    meshes = mesh_objects()
    if not meshes:
        rep.add("FAIL", "content", "no mesh objects found.")

    per_mesh = []
    total_world_area = 0.0
    texel_samples = []
    for obj in meshes:
        stats, world_area, uv_area = analyze_mesh(obj, deps, rep)
        per_mesh.append(stats)
        total_world_area += world_area
        sizes = [max(img.size) for sl in obj.material_slots for img in image_textures(sl.material) if img.size[0]]
        if sizes and uv_area > 0 and world_area > 0:
            # px per meter, assuming UV area maps onto the largest texture of the mesh
            texel_samples.append((obj.name, math.sqrt(uv_area * max(sizes) ** 2 / world_area)))

    parts, groups, sockets = inspect_parts(meshes, a, rep)
    for name, members in groups.items():
        group_report = Report()
        floating_parts(members, deps, a.contact_tol, group_report)
        for check in group_report.checks:
            check["rigid_group"] = name
            check["message"] = f"rigid group {name!r}: {check['message']}"
        rep.checks.extend(group_report.checks)
    collisions = collision_report(deps, rep)
    hierarchy = hierarchy_rows()

    lo, hi = world_bbox(meshes)
    dims = hi - lo
    total_tris = sum(m["triangles"] for m in per_mesh)
    materials = sorted({s.material.name for o in meshes for s in o.material_slots if s.material})
    draw_calls = sum(max(1, len([s for s in o.material_slots if s.material])) for o in meshes)

    images = {}
    for img in bpy.data.images:
        if img.size[0] and img.users:
            images[img.name] = {"size": list(img.size), "colorspace": img.colorspace_settings.name,
                                "pot": all(v & (v - 1) == 0 for v in img.size)}

    # Budgets
    b = a.budget
    if "max_tris" in b:
        lvl = "PASS" if total_tris <= b["max_tris"] else "FAIL"
        rep.add(lvl, "budget", f"triangles {total_tris} / budget {b['max_tris']}")
    if "max_materials" in b:
        lvl = "PASS" if len(materials) <= b["max_materials"] else "FAIL"
        rep.add(lvl, "budget", f"materials {len(materials)} / budget {b['max_materials']}")
    if "max_texture" in b:
        for name, info in images.items():
            if max(info["size"]) > b["max_texture"]:
                rep.add("FAIL", "budget", f"texture {name} {info['size']} exceeds {b['max_texture']}px")
    for name, info in images.items():
        if not info["pot"]:
            rep.add("WARN", "texture", f"texture {name} {info['size']} is not power-of-two (mipmaps/compression).")

    # Scale and pivot
    if a.expect_height:
        lvl = tolerance_level(dims.z, a.expect_height)
        rep.add(lvl, "scale", f"height {dims.z:.3f} m vs expected {a.expect_height} m")
    if a.expect_dims:
        exp = [float(x) for x in a.expect_dims.split(",")]
        for axis, actual, e in zip("XYZ", dims, exp):
            if e > 0:
                rep.add(tolerance_level(actual, e), "scale", f"{axis} extent {actual:.3f} m vs expected {e} m")
    if not (a.expect_height or a.expect_dims) and meshes:
        big = max(dims)
        if big > 100 or big < 0.01:
            rep.add("WARN", "scale", f"largest extent {big:.4f} m looks like a unit error (1 unit must be 1 m).")
    if meshes and a.pivot != "any":
        center = (lo + hi) / 2
        size = max(max(dims), 1e-6)
        if a.pivot == "base":
            ok = abs(lo.z) <= 0.02 * size and abs(center.x) <= 0.05 * size and abs(center.y) <= 0.05 * size
            want = "origin at bottom-center (asset rests on Z=0, centered on X/Y)"
        else:
            ok = center.length <= 0.05 * size
            want = "origin at bounds center"
        rep.add("PASS" if ok else "WARN", "pivot",
                f"expected {want}; bounds min {round_vec(lo)} max {round_vec(hi)}")

    if a.texel_density and texel_samples:
        for name, td in texel_samples:
            lvl = tolerance_level(td, a.texel_density, warn=0.35, fail=1.0)
            rep.add("PASS" if lvl == "PASS" else "WARN", "texel_density",
                    f"{td:.0f} px/m vs target {a.texel_density:.0f}", name)

    # Rigs and animation
    armatures = [o for o in bpy.context.scene.objects if o.type == "ARMATURE"]
    rigs = [{"name": o.name, "bones": len(o.data.bones)} for o in armatures]
    for r in rigs:
        if r["bones"] > 100:
            rep.add("WARN", "rig", f"{r['bones']} bones: heavy for web/mobile skinning.", r["name"])
    for obj in meshes:
        if obj.vertex_groups and any(m.type == "ARMATURE" for m in obj.modifiers):
            over = sum(1 for v in obj.data.vertices if sum(1 for g in v.groups if g.weight > 1e-4) > 4)
            if over:
                rep.add("WARN", "skinning", f"{over} vertices influenced by >4 bones (glTF/engines keep 4).", obj.name)
    actions = [{"name": act.name, "frames": round_vec(act.frame_range, 1)} for act in bpy.data.actions]

    result = {
        "file": os.path.abspath(a.model),
        "summary": {
            "triangles": total_tris, "meshes": len(meshes), "materials": len(materials),
            "draw_calls_estimate": draw_calls, "dimensions_m": round_vec(dims),
            "bounds_min": round_vec(lo), "bounds_max": round_vec(hi),
            "surface_area_m2": round(total_world_area, 3), "textures": images,
            "texel_density_px_per_m": {n: round(t) for n, t in texel_samples},
            "armatures": rigs, "actions": actions, "budget": b,
        },
        "meshes": per_mesh,
        "parts": parts,
        "rigid_groups": {name: [m.name for m in members] for name, members in groups.items()},
        "sockets": sockets,
        "collisions": collisions,
        "hierarchy": hierarchy,
        "checks": rep.checks,
        "verdict": "FAIL" if rep.count("FAIL") else ("WARN" if rep.count("WARN") else "PASS"),
    }

    s = result["summary"]
    print(f"\n== inspect_model: {os.path.basename(a.model)} ==")
    print(f"triangles {s['triangles']} | meshes {s['meshes']} | materials {s['materials']} | "
          f"draw calls ~{s['draw_calls_estimate']} | size (m) X{s['dimensions_m'][0]} "
          f"Y{s['dimensions_m'][1]} Z{s['dimensions_m'][2]}")
    if images:
        print("textures: " + ", ".join(f"{n} {i['size'][0]}x{i['size'][1]}" for n, i in images.items()))
    if texel_samples:
        print("texel density (px/m): " + ", ".join(f"{n} {t:.0f}" for n, t in texel_samples))
    if rigs or actions:
        print(f"rigs: {rigs} | actions: {[x['name'] for x in actions]}")
    if collisions:
        print("collision proxies (excluded from render budgets): " + ", ".join(
            f"{c['name']} {c['triangles']} tris" for c in collisions))
    print("hierarchy (world origins in meters):")
    for node in hierarchy:
        label = f" joint={node['joint']} axis={node['axis']}" if node["joint"] else ""
        print(f"  {'  ' * node['depth']}{node['name']} [{node['type']}]{label} origin={node['origin']}")
    for c in rep.checks:
        where = f" [{c['object']}]" if c["object"] else ""
        print(f"  {c['level']:<4} {c['check']}{where}: {c['message']}")
    print(f"VERDICT: {result['verdict']} ({rep.count('FAIL')} fail, {rep.count('WARN')} warn)")

    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
    sys.exit(1 if rep.count("FAIL") else 0)


if __name__ == "__main__":
    main()
