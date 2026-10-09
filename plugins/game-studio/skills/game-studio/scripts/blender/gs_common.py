"""Shared helpers for the game-studio Blender scripts.

Works both inside Blender (`blender -b --factory-startup --python script.py -- args`)
and with the `bpy` module from PyPI (`python script.py args`).
"""
import math
import os
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


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def load_model(path):
    """Open a .blend or import any supported format into an empty scene."""
    path = os.path.abspath(path)
    if not os.path.isfile(path):
        raise SystemExit(f"error: file not found: {path}")
    ext = os.path.splitext(path)[1].lower()
    if ext == ".blend":
        bpy.ops.wm.open_mainfile(filepath=path)
        return
    if ext not in IMPORTERS:
        raise SystemExit(f"error: unsupported format '{ext}' (supported: .blend {' '.join(sorted(IMPORTERS))})")
    reset_scene()
    IMPORTERS[ext](path)


def mesh_objects():
    """Renderable meshes, excluding objects used only as custom bone shapes by importers."""
    shapes = {pb.custom_shape for o in bpy.context.scene.objects if o.type == "ARMATURE"
              for pb in o.pose.bones if pb.custom_shape}
    return [o for o in bpy.context.scene.objects
            if o.type == "MESH" and not o.hide_render and o not in shapes]


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
