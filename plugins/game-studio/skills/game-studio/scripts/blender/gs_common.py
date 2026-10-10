"""Shared helpers for the game-studio Blender scripts.

Works both inside Blender (`blender -b --factory-startup --python script.py -- args`)
and with the `bpy` module from PyPI (`python script.py args`).
"""
import math
import os
import re
import sys

import bpy
import numpy as np
from mathutils import Vector

IMPORTERS = {
    ".glb": lambda p: bpy.ops.import_scene.gltf(filepath=p),
    ".gltf": lambda p: bpy.ops.import_scene.gltf(filepath=p),
    ".fbx": lambda p: bpy.ops.import_scene.fbx(filepath=p),
    ".obj": lambda p: bpy.ops.wm.obj_import(filepath=p),
    ".stl": lambda p: bpy.ops.wm.stl_import(filepath=p),
    ".ply": lambda p: bpy.ops.wm.ply_import(filepath=p),
    ".usd": lambda p: bpy.ops.wm.usd_import(filepath=p),
    ".usda": lambda p: bpy.ops.wm.usd_import(filepath=p),
    ".usdc": lambda p: bpy.ops.wm.usd_import(filepath=p),
    ".usdz": lambda p: bpy.ops.wm.usd_import(filepath=p),
}


def script_args():
    """Arguments after `--` when run inside Blender, otherwise argv[1:]."""
    if "--" in sys.argv:
        return sys.argv[sys.argv.index("--") + 1:]
    return sys.argv[1:]


def die(msg, code=2):
    """Usage/load errors exit 2, so that exit 1 always means a FAIL verdict."""
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def load_model(path):
    """Open a .blend or import any supported format into an empty scene."""
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        die(f"file not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=path)
        return
    if ext not in IMPORTERS:
        die(f"unsupported format '{ext}' (supported: .blend {' '.join(sorted(IMPORTERS))})")
    reset_scene()
    IMPORTERS[ext](path)


COLLISION_SUFFIXES = ("-col", "-colonly", "-convcol", "-convcolonly")   # Godot import hints
COLLISION_PREFIXES = ("UCX_", "UBX_", "USP_", "UCP_", "COL_")            # Unreal, generic


def is_collision(obj):
    """True for collision proxies named by engine convention (Godot -col/-colonly/-convcol/-convcolonly,
    Unreal UCX_/UBX_/USP_/UCP_, or COL_). Blender's .001 duplicate suffix is ignored."""
    name = re.sub(r"\.\d{3}$", "", obj.name)
    return name.lower().endswith(COLLISION_SUFFIXES) or name.startswith(COLLISION_PREFIXES)


def mesh_objects(include_collision=False):
    """Renderable meshes, excluding custom bone shapes and (by default) collision proxies."""
    shapes = {pb.custom_shape for o in bpy.context.scene.objects if o.type == "ARMATURE"
              for pb in o.pose.bones if pb.custom_shape}
    return [o for o in bpy.context.scene.objects
            if o.type == "MESH" and not o.hide_render and o not in shapes
            and (include_collision or not is_collision(o))]


def collision_objects():
    return [o for o in bpy.context.scene.objects if o.type == "MESH" and is_collision(o)]


def joint_of(obj):
    """The joint an object declares (custom property / glTF extra "joint"), or None."""
    try:
        return obj.get("joint")
    except TypeError:
        return None


def rigid_group(obj, part_names=()):
    """Name of the rigid group an object moves with: its nearest ancestor-or-self that declares a joint or
    is listed in part_names; "body" otherwise."""
    o = obj
    while o is not None:
        if joint_of(o) or o.name in part_names:
            return o.name
        o = o.parent
    return "body"


def world_bbox(objs):
    """Axis-aligned world-space bounds of the evaluated objects -> (min, max) Vectors."""
    deps = bpy.context.evaluated_depsgraph_get()
    lo = Vector((math.inf, math.inf, math.inf))
    hi = Vector((-math.inf, -math.inf, -math.inf))
    for o in objs:
        oe = o.evaluated_get(deps)
        for corner in oe.bound_box:
            w = oe.matrix_world @ Vector(corner)
            lo = Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    if lo.x == math.inf:
        return Vector((0, 0, 0)), Vector((0, 0, 0))
    return lo, hi


def round_vec(v, nd=3):
    return [round(float(c), nd) for c in v]


def world_points(objs, max_points=40000):
    """World-space vertex positions of the evaluated meshes (subsampled), as an (N, 3) array."""
    deps = bpy.context.evaluated_depsgraph_get()
    chunks = []
    for o in objs:
        oe = o.evaluated_get(deps)
        me = oe.to_mesh()
        co = np.empty(len(me.vertices) * 3, dtype=np.float64)
        me.vertices.foreach_get("co", co)
        mw = np.array(oe.matrix_world)
        chunks.append(co.reshape(-1, 3) @ mw[:3, :3].T + mw[:3, 3])
        oe.to_mesh_clear()
    pts = np.concatenate(chunks) if chunks else np.zeros((0, 3))
    if len(pts) > max_points:
        pts = pts[:: len(pts) // max_points + 1]
    return pts
