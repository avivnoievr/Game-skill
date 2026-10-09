"""Render review images of a 3D asset so a vision-capable agent can judge it.

Usage (Blender):  blender -b --factory-startup --python render_views.py -- MODEL --out DIR [options]
Usage (pip bpy):  python render_views.py MODEL --out DIR [options]

Views (default: front,right,back,left,q_fl,q_fr,top,silhouette,wire):
  front/right/back/left/top  orthographic, for proportions and alignment
  q_fl/q_fr                  three-quarter perspective (front-left / front-right), for form
  silhouette                 flat black on white from q_fr, for shape readability
  wire                       three-quarter with wireframe overlay, for topology density
Options:
  --engine workbench|eevee|cycles  workbench (default) is fast and shows form/cavities; eevee/cycles
                                   add studio lights, a ground plane and contact shadows
  --size PX            square tile size (default 640)
  --views LIST         comma-separated subset of the views above
  --scale-ref          add a 1.8 m tall reference figure beside the asset
  --anim ACTION        also render a pose strip of this action (q_fr view)
  --anim-steps N       frames in the pose strip (default 8)
  --frame N            scene frame to render the static views at
  --no-sheet           skip the contact sheet
Outputs: one PNG per view, contact_sheet.png (row-major in the order of --views) and views.json.
"""
import argparse
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402  (import before mathutils: required by the PyPI bpy module)
import numpy as np  # noqa: E402
from mathutils import Vector  # noqa: E402

from gs_common import load_model, mesh_objects, script_args, world_bbox, world_points  # noqa: E402

ALL_VIEWS = ["front", "right", "back", "left", "q_fl", "q_fr", "top", "silhouette", "wire"]
DIRECTIONS = {  # camera position relative to the asset center (Blender: -Y is the asset's front)
    "front": (0, -1, 0), "back": (0, 1, 0), "right": (1, 0, 0), "left": (-1, 0, 0),
    "top": (0, -0.0001, 1), "q_fl": (-1, -1.1, 0.55), "q_fr": (1, -1.1, 0.55),
}
ORTHO_PLANE = {"front": (0, 2), "back": (0, 2), "right": (1, 2), "left": (1, 2), "top": (0, 1)}


def parse():
    p = argparse.ArgumentParser(prog="render_views.py", description=__doc__.split("\n")[0])
    p.add_argument("model")
    p.add_argument("--out", required=True)
    p.add_argument("--engine", choices=["workbench", "eevee", "cycles"], default="workbench")
    p.add_argument("--size", type=int, default=640)
    p.add_argument("--views", default=",".join(ALL_VIEWS))
    p.add_argument("--scale-ref", action="store_true")
    p.add_argument("--anim")
    p.add_argument("--anim-steps", type=int, default=8)
    p.add_argument("--frame", type=int)
    p.add_argument("--no-sheet", action="store_true")
    a = p.parse_args(script_args())
    a.views = [v.strip() for v in a.views.split(",") if v.strip()]
    bad = [v for v in a.views if v not in ALL_VIEWS]
    if bad:
        p.error(f"unknown views {bad}; choose from {ALL_VIEWS}")
    return a


def set_engine(scene, name):
    """EEVEE is BLENDER_EEVEE_NEXT in Blender 4.2-4.5 and BLENDER_EEVEE in 5.x (and before 4.2)."""
    if name == "workbench":
        scene.render.engine = "BLENDER_WORKBENCH"
    elif name == "cycles":
        scene.render.engine = "CYCLES"
    else:
        try:
            scene.render.engine = "BLENDER_EEVEE_NEXT" if (4, 2) <= bpy.app.version < (5, 0) else "BLENDER_EEVEE"
        except TypeError:
            scene.render.engine = "BLENDER_EEVEE"


def set_world(color, strength=1.0):
    scene = bpy.context.scene
    world = scene.world or bpy.data.worlds.new("gs_world")
    scene.world = world
    world.color = color[:3]
    if world.node_tree is None and hasattr(world, "use_nodes"):
        world.use_nodes = True
    if world.node_tree:
        bg = next((n for n in world.node_tree.nodes if n.type == "BACKGROUND"), None)
        if bg:
            bg.inputs["Color"].default_value = (*color[:3], 1.0)
            bg.inputs["Strength"].default_value = strength


def setup_render(a, has_textures):
    scene = bpy.context.scene
    r = scene.render
    set_engine(scene, a.engine)
    r.resolution_x = r.resolution_y = a.size
    r.resolution_percentage = 100
    r.film_transparent = False
    r.image_settings.file_format = "PNG"
    r.image_settings.color_mode = "RGBA"
    if a.engine == "workbench":
        scene.view_settings.view_transform = "Standard"
        sh = scene.display.shading
        sh.light = "STUDIO"
        sh.color_type = "TEXTURE" if has_textures else "MATERIAL"
        sh.show_cavity = True
        sh.cavity_type = "BOTH"
        sh.show_object_outline = True
        sh.show_specular_highlight = True
        scene.display.render_aa = "8"
        set_world((0.214, 0.214, 0.214))
    else:
        if a.engine == "cycles":
            scene.cycles.samples = 48
            scene.cycles.use_denoising = True
            scene.cycles.device = "CPU"
        set_world((0.18, 0.19, 0.21), 0.6)


def add_studio_lights(center, radius):
    """Key / fill / rim area lights scaled to the asset; existing lights are hidden from render."""
    for o in bpy.context.scene.objects:
        if o.type == "LIGHT":
            o.hide_render = True
    d = max(radius, 0.05) * 3.0
    rigs = [("gs_key", (-1.0, -1.2, 1.4), 90.0, 1.0), ("gs_fill", (1.4, -0.8, 0.5), 30.0, 1.5),
            ("gs_rim", (0.4, 1.5, 1.2), 60.0, 0.8)]
    for name, direction, power, size in rigs:
        light = bpy.data.lights.new(name, type="AREA")
        light.energy = power * d * d
        light.size = size * d * 0.5
        obj = bpy.data.objects.new(name, light)
        bpy.context.scene.collection.objects.link(obj)
        obj.location = center + Vector(direction).normalized() * d
        aim(obj, center)


def add_ground(lo, hi):
    size = max(hi.x - lo.x, hi.y - lo.y, 1.0) * 6
    bpy.ops.mesh.primitive_plane_add(size=size, location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    ground = bpy.context.object
    ground.name = "gs_ground"
    mat = bpy.data.materials.new("gs_ground_mat")
    mat.diffuse_color = (0.32, 0.32, 0.33, 1.0)
    if mat.node_tree is None and hasattr(mat, "use_nodes"):
        mat.use_nodes = True
    bsdf = next((n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (0.32, 0.32, 0.33, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.85
    ground.data.materials.append(mat)
    return ground


def add_scale_ref(lo, hi):
    """1.8 m tall, 0.45 m wide figure placed 0.4 m to the right of the asset."""
    h, w = 1.8, 0.45
    r = w / 2
    x, y = hi.x + 0.4 + r, (lo.y + hi.y) / 2
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h - r, location=(x, y, lo.z + (h - r) / 2))
    body = bpy.context.object
    body.name = "gs_scale_ref_1.8m"
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=(x, y, lo.z + h - r))
    head = bpy.context.object
    mat = bpy.data.materials.new("gs_scale_ref_mat")
    mat.diffuse_color = (0.9, 0.35, 0.1, 1.0)
    for o in (body, head):
        o.data.materials.append(mat)
        o.color = (0.9, 0.35, 0.1, 1.0)
    return [body, head]


def aim(obj, target):
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def place_camera(cam, view, center, points, fill=0.85):
    """Aim at `center` from the view direction and fit the projected vertices to `fill` of the frame."""
    direction = Vector(DIRECTIONS["q_fr" if view in ("silhouette", "wire") else view]).normalized()
    radius = max(float(np.linalg.norm(points - np.array(center), axis=1).max()) if len(points) else 1.0, 1e-3)
    ortho = view in ORTHO_PLANE
    cam.data.type = "ORTHO" if ortho else "PERSP"
    cam.data.lens, cam.data.sensor_width = 50, 36
    half_fov_tan = 18 / 50
    dist = radius * 3 if ortho else radius / math.sin(math.atan(half_fov_tan))
    cam.location = center + direction * dist
    aim(cam, center)
    rot = np.array(cam.rotation_euler.to_matrix())
    right, up, back = rot[:, 0], rot[:, 1], rot[:, 2]
    rel = points - np.array(center)
    if ortho:
        half = max(np.abs(rel @ right).max(), np.abs(rel @ up).max(), 1e-4)
        cam.data.ortho_scale = 2 * half / fill
    else:
        for _ in range(5):
            v = points - np.array(cam.location)
            depth = np.maximum(-(v @ back), 1e-6)
            spread = max(np.abs(v @ right / depth).max(), np.abs(v @ up / depth).max()) / half_fov_tan
            dist *= max(spread / fill, 0.5)
            cam.location = center + direction * dist
    cam.data.clip_start = max(dist - radius * 2, dist * 0.001, 1e-3)
    cam.data.clip_end = dist + radius * 4


def with_silhouette(render):
    scene = bpy.context.scene
    sh = scene.display.shading
    saved = (scene.render.engine, sh.light, sh.color_type, tuple(sh.single_color), sh.show_cavity,
             sh.show_object_outline, sh.show_specular_highlight, scene.view_settings.view_transform,
             tuple(scene.world.color))
    scene.render.engine = "BLENDER_WORKBENCH"
    sh.light, sh.color_type, sh.single_color = "FLAT", "SINGLE", (0, 0, 0)
    sh.show_cavity = sh.show_object_outline = sh.show_specular_highlight = False
    scene.view_settings.view_transform = "Standard"
    scene.world.color = (1, 1, 1)
    hidden = [o for o in scene.objects if o.name.startswith(("gs_ground", "gs_scale_ref"))]
    for o in hidden:
        o.hide_render = True
    render()
    for o in hidden:
        o.hide_render = False
    (scene.render.engine, sh.light, sh.color_type, sh.single_color, sh.show_cavity, sh.show_object_outline,
     sh.show_specular_highlight, scene.view_settings.view_transform, scene.world.color) = saved


def with_wireframe(meshes, radius, render):
    """Overlay dark wire copies on light-grey surfaces (Workbench does not render overlays)."""
    scene = bpy.context.scene
    sh = scene.display.shading
    saved = (scene.render.engine, sh.color_type)
    scene.render.engine = "BLENDER_WORKBENCH"
    sh.color_type = "OBJECT"
    copies, colors = [], {}
    for o in meshes:
        colors[o.name] = tuple(o.color)
        o.color = (0.78, 0.78, 0.78, 1)
        c = o.copy()
        scene.collection.objects.link(c)
        mod = c.modifiers.new("gs_wire", "WIREFRAME")
        mod.thickness = max(radius * 0.0025, 1e-4)
        mod.use_replace = True
        mod.use_even_offset = False
        c.color = (0.05, 0.05, 0.05, 1)
        copies.append(c)
    render()
    for c in copies:
        bpy.data.objects.remove(c, do_unlink=True)
    for o in meshes:
        o.color = colors[o.name]
    scene.render.engine, sh.color_type = saved


def find_action_target(action_name):
    act = bpy.data.actions.get(action_name)
    if act is None:
        raise SystemExit(f"error: action '{action_name}' not found; available: {[x.name for x in bpy.data.actions]}")
    arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
    target = arm or next(iter(mesh_objects()), None)
    if target is None:
        raise SystemExit("error: nothing to animate")
    ad = target.animation_data or target.animation_data_create()
    for track in ad.nla_tracks:
        track.mute = True
    ad.action = act
    if hasattr(ad, "action_slot") and getattr(ad, "action_slot", None) is None and getattr(act, "slots", None):
        ad.action_slot = act.slots[0]
    return act


def contact_sheet(paths, out_path, cols):
    imgs = [bpy.data.images.load(p) for p in paths]
    w, h = imgs[0].size
    rows = math.ceil(len(imgs) / cols)
    sheet = np.ones((rows * h, cols * w, 4), dtype=np.float32)
    for i, im in enumerate(imgs):
        px = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(px)
        r, c = divmod(i, cols)
        y0 = (rows - 1 - r) * h  # Blender image rows start at the bottom
        sheet[y0:y0 + h, c * w:(c + 1) * w] = px.reshape(h, w, 4)
    out = bpy.data.images.new("gs_contact_sheet", cols * w, rows * h, alpha=True)
    out.pixels.foreach_set(sheet.ravel())
    out.filepath_raw = out_path
    out.file_format = "PNG"
    out.save()


def main():
    a = parse()
    load_model(a.model)
    os.makedirs(a.out, exist_ok=True)
    for old in os.listdir(a.out):  # never review a stale image as fresh
        if old.endswith(".png") or old == "views.json":
            os.remove(os.path.join(a.out, old))
    scene = bpy.context.scene
    if a.frame is not None:
        scene.frame_set(a.frame)
    meshes = mesh_objects()
    if not meshes:
        raise SystemExit("error: no mesh objects to render")
    has_textures = any(n.type == "TEX_IMAGE" and n.image for o in meshes for s in o.material_slots
                       if s.material and s.material.node_tree for n in s.material.node_tree.nodes)
    lo, hi = world_bbox(meshes)
    setup_render(a, has_textures)
    extras = []
    if a.scale_ref:
        extras += add_scale_ref(lo, hi)
    frame_lo, frame_hi = world_bbox(meshes + extras)
    center = (frame_lo + frame_hi) / 2
    radius = (frame_hi - frame_lo).length / 2
    points = world_points(meshes + extras)
    if a.engine != "workbench":
        add_studio_lights(center, radius)
        add_ground(frame_lo, frame_hi)

    cam = bpy.data.objects.new("gs_cam", bpy.data.cameras.new("gs_cam"))
    scene.collection.objects.link(cam)
    scene.camera = cam

    written = []

    def shoot(view, path):
        place_camera(cam, view, center, points)
        scene.render.filepath = path
        bpy.ops.render.render(write_still=True)
        written.append({"view": view, "file": path})

    for view in a.views:
        path = os.path.join(a.out, f"{view}.png")
        if view == "silhouette":
            with_silhouette(lambda: shoot(view, path))
        elif view == "wire":
            with_wireframe(meshes, radius, lambda: shoot(view, path))
        else:
            shoot(view, path)

    if not a.no_sheet and len(written) > 1:
        sheet = os.path.join(a.out, "contact_sheet.png")
        contact_sheet([w["file"] for w in written], sheet, cols=min(3, len(written)))
        print(f"contact sheet: {sheet} (row-major: {', '.join(w['view'] for w in written)})")

    strip = []
    if a.anim:
        act = find_action_target(a.anim)
        f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        steps = max(2, a.anim_steps)
        for k in range(steps):
            f = round(f0 + (f1 - f0) * k / (steps - 1 if f1 > f0 else 1))
            scene.frame_set(f)
            place_camera(cam, "q_fr", center, points, fill=0.7)  # rest-pose fit + margin: no camera jumps
            path = os.path.join(a.out, f"anim_{a.anim}_{k:02d}_f{f}.png")
            scene.render.filepath = path
            bpy.ops.render.render(write_still=True)
            strip.append({"frame": f, "file": path})
        if not a.no_sheet:
            sheet = os.path.join(a.out, f"anim_{a.anim}_strip.png")
            contact_sheet([s["file"] for s in strip], sheet, cols=min(4, len(strip)))
            print(f"pose strip: {sheet} (frames {[s['frame'] for s in strip]})")

    with open(os.path.join(a.out, "views.json"), "w", encoding="utf-8") as fh:
        json.dump({"model": os.path.abspath(a.model), "engine": a.engine, "views": written, "anim": strip,
                   "bounds_min": list(lo), "bounds_max": list(hi)}, fh, indent=2)
    print(f"rendered {len(written)} views" + (f" + {len(strip)} anim frames" if strip else "") + f" -> {a.out}")


if __name__ == "__main__":
    main()
