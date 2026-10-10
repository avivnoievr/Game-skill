"""Example: a stylized game sedan built with gs_build (vehicle recipe: docs/HANDOFF.md, references/recipes/ planned).

    blender -b --factory-startup --python-exit-code 1 -P car_stylized.py -- --out out/car.glb
    python car_stylized.py --out out/car.glb            (PyPI bpy)

What it demonstrates:
  * real dimensions (sedan: 4.5 m long, 1.8 m wide, 1.45 m tall, 2.7 m wheelbase, 0.66 m wheels)
  * body from cross-sections (loft), cabin with tumblehome, wheel wells cut with booleans
  * detail cut INTO surfaces (recessed windows, grille), bevels + weighted normals
  * moving parts kept SEPARATE: Wheel_FL/FR/RL/RR, origin at the axle center, spin axis = local X
  * hierarchy Car (root, origin at ground center) -> Body, wheels, Car-colonly collision proxy
  * palette materials; export GLB with modifiers applied
Front faces -Y in Blender (+Z in glTF). The driver's left is +X.
"""
import argparse
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import bpy  # noqa: E402
from mathutils import Matrix  # noqa: E402
import gs_build as gb  # noqa: E402
from gs_common import script_args  # noqa: E402

TIRE = gb.tire_dims("205/60R16")  # radius 0.326 m, width 0.205 m
DIM = {"length": 4.5, "width": 1.8, "height": 1.45, "wheelbase": 2.7, "track": 1.55,
       "wheel_radius": TIRE["radius"], "wheel_width": TIRE["width"], "clearance": 0.15}
PALETTE = {"paint": "#C8452F", "glass": "#1C2630", "trim": "#262626", "tire": "#1A1A1A",
           "rim": "#A7AFB6", "head": "#FFF4DA", "tail": "#C81E1E"}


def section(y, width, z0, z1, radius, top_width=None, n=5):
    """Cross-section ring at Y: rounded rectangle in XZ, optionally narrower at the top (tumblehome)."""
    pts = []
    for x, z in gb.rounded_rect(width, z1 - z0, radius, corner_segments=n, center=(0.0, (z0 + z1) / 2)):
        if top_width is not None:
            t = (z - z0) / (z1 - z0)
            x *= 1 + (top_width / width - 1) * t
        pts.append((x, y, z))
    return pts


def build():
    gb.begin("car_stylized")
    m = {k: gb.material(k, c, roughness=r, metallic=mt, emission=e) for k, c, r, mt, e in [
        ("paint", PALETTE["paint"], 0.35, 0.0, None), ("glass", PALETTE["glass"], 0.08, 0.0, None),
        ("trim", PALETTE["trim"], 0.7, 0.0, None), ("tire", PALETTE["tire"], 0.92, 0.0, None),
        ("rim", PALETTE["rim"], 0.3, 1.0, None), ("head", PALETTE["head"], 0.2, 0.0, PALETTE["head"]),
        ("tail", PALETTE["tail"], 0.3, 0.0, PALETTE["tail"])]}

    # Lower body: bumper -> hood -> doors -> trunk (front at -Y)
    body = gb.loft("Body", [
        section(-2.25, 1.66, 0.26, 0.62, 0.12),
        section(-2.15, 1.76, 0.20, 0.72, 0.16),
        section(-1.85, 1.80, 0.18, 0.80, 0.18),
        section(-0.80, 1.80, 0.18, 0.90, 0.18),
        section(0.90, 1.80, 0.18, 0.93, 0.18),
        section(1.90, 1.78, 0.20, 0.90, 0.17),
        section(2.20, 1.72, 0.24, 0.82, 0.14),
        section(2.25, 1.66, 0.30, 0.76, 0.12)])
    gb.assign(body, m["paint"])
    # Wheel wells: one cutter per wheel, from just inside the wheel to beyond the body side. The cut faces take
    # the cutter's (dark) material, so the inside of each well reads as a dark opening, not body paint.
    hx, hy, r = DIM["track"] / 2, DIM["wheelbase"] / 2, DIM["wheel_radius"]
    for sx in (-1, 1):
        for y in (-hy, hy):
            well = gb.revolve("well_cutter", [(r + 0.06, hx - DIM["wheel_width"] / 2 - 0.08), (r + 0.06, 1.3)],
                              segments=40, axis="X")
            if sx < 0:
                well.data.transform(Matrix.Scale(-1, 4, (1, 0, 0)))
                well.data.flip_normals()
            well.location = (0.0, y, r)
            gb.assign(well, m["trim"])
            gb.cut(body, well)
    # Grille: recess the front face and paint it trim
    gb.assign(body, m["trim"], select=lambda f: f.normal.y < -0.95)
    gb.recess(body, lambda f: f.normal.y < -0.95, inset=0.06, depth=0.025)
    gb.bevel(body, width=0.012, segments=2, angle_deg=35)
    gb.weighted_normals(body)

    # Cabin (greenhouse) with tumblehome; side/front/rear faces become glass, recessed into the frame
    cabin = gb.loft("Cabin", [
        section(-0.95, 1.62, 0.84, 0.90, 0.04, top_width=1.58),
        section(-0.30, 1.60, 0.84, 1.40, 0.10, top_width=1.30),
        section(0.55, 1.60, 0.84, 1.44, 0.10, top_width=1.30),
        section(1.20, 1.62, 0.84, 0.96, 0.05, top_width=1.56)])
    gb.assign(cabin, m["paint"])
    window = lambda f: abs(f.normal.z) < 0.8 and f.calc_center_median().z > 0.97  # noqa: E731
    gb.assign(cabin, m["glass"], select=window)
    for side in (lambda f: window(f) and f.normal.x > 0.5, lambda f: window(f) and f.normal.x < -0.5,
                 lambda f: window(f) and f.normal.y < -0.3, lambda f: window(f) and f.normal.y > 0.3):
        gb.recess(cabin, side, inset=0.035, depth=0.012)
    gb.bevel(cabin, width=0.01, segments=2, angle_deg=35)
    gb.weighted_normals(cabin)

    # Lights and bumpers: small static parts, touching the body, each with its own bevel
    parts = []
    for x in (-0.58, 0.58):
        hl = gb.extrude("Headlight", gb.rounded_rect(0.36, 0.11, 0.04, center=(x, 0.66)), 0.05, axis="Y")
        hl.location.y = -2.165
        gb.assign(hl, m["head"])
        tl = gb.extrude("Taillight", gb.rounded_rect(0.34, 0.10, 0.03, center=(x, 0.74)), 0.05, axis="Y")
        tl.location.y = 2.215
        gb.assign(tl, m["tail"])
        parts += [hl, tl]
    for y, z in ((-2.25, 0.32), (2.25, 0.36)):
        bumper = gb.extrude("Bumper", gb.rounded_rect(0.10, 0.14, 0.04, center=(y, z)), 1.72, axis="X")
        gb.assign(bumper, m["trim"])
        parts.append(bumper)
    for part in parts:
        gb.bevel(part, width=0.008, segments=1)
        gb.weighted_normals(part)
    body = gb.join([body, cabin] + parts, "Body")  # static parts only; join() applies each part's modifiers

    # Root (origin on the ground, between the axles) + SEPARATE moving parts with their pivots
    root = gb.empty("Car")
    gb.parent(body, root)
    hx, hy, r = DIM["track"] / 2, DIM["wheelbase"] / 2, DIM["wheel_radius"]
    for name, x, y in (("Wheel_FL", hx, -hy), ("Wheel_FR", -hx, -hy), ("Wheel_RL", hx, hy), ("Wheel_RR", -hx, hy)):
        w = gb.wheel(name, radius=r, width=DIM["wheel_width"], rim_ratio=TIRE["rim_radius"] / r,
                     tire_mat=m["tire"], rim_mat=m["rim"])  # origin = axle center, joint spin about X
        if x < 0:  # right side: turn the wheel so its face points outward; spin axis stays X
            w.rotation_euler.z = math.pi
            gb.apply_rot_scale(w)
        holder = root
        if name.startswith("Wheel_F"):  # front wheels hang under a steer pivot (rotates about Z)
            holder = gb.empty("Steer_" + name[-2:], (x, y, r), root)
            gb.set_joint(holder, "steer", "Z", -35, 35)
        w.location = (x, y, r)
        gb.parent(w, holder)
    # Sockets the game code looks up by name
    gb.socket("seat_driver", (0.38, 0.25, 0.55), root)
    gb.socket("cam_chase", (0.0, 6.5, 2.2), root)
    gb.socket("exhaust", (-0.5, 2.3, 0.28), root)
    # Collision proxy: body only, bottom at the ground clearance (wheels are raycasts in every engine)
    col = gb.collision_box(body, suffix="-colonly", min_z=DIM["clearance"])
    gb.parent(col, root)
    return root


def main():
    p = argparse.ArgumentParser(prog="car_stylized.py")
    p.add_argument("--out", required=True, help="output .glb path (a .blend is saved next to it)")
    a = p.parse_args(script_args())
    os.makedirs(os.path.dirname(os.path.abspath(a.out)), exist_ok=True)
    root = build()
    gb.export_glb(a.out, [root])
    gb.save_blend(os.path.splitext(a.out)[0] + ".blend")
    print(f"exported {a.out}")


if __name__ == "__main__":
    main()
