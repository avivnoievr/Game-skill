"""Original articulated fan fixture; validates generic source/part workflow, not hero-art quality."""
import argparse
import json
from pathlib import Path
import sys


def build_asset(gb, asset_id):
    import math
    from mathutils import Matrix
    gb.begin(asset_id)
    root = gb.empty(asset_id)
    cream = gb.material("enamel", "#D7CEAF", roughness=0.45)
    sage = gb.material("rotor", "#426A61", roughness=0.38)
    # A sealed rounded foot, tapered neck and profile-built motor casing form one fixed rigid part.
    foot = gb.extrude("Foot", gb.rounded_rect(0.200, 0.170, 0.035, 3), 0.030, axis="Z", centered=False)
    gb.bevel(foot, 0.003, segments=2)
    neck = gb.sweep("Neck", [(0, 0.035, 0.028), (0, 0.050, 0.100),
                            (0, 0.056, 0.205), (0, 0.065, 0.300)],
                    gb.rounded_rect(0.025, 0.020, 0.004, 2))
    motor = gb.revolve("Motor", [(0, 0.020), (0.035, 0.020), (0.044, 0.030),
                                 (0.044, 0.080), (0.036, 0.108), (0, 0.115)],
                       segments=24, axis="Y")
    motor.location.z = 0.300
    base = gb.join([foot, neck, motor], "Base")
    gb.assign(base, cream)
    gb.set_origin(base, mode="base")
    gb.parent(base, root)
    base["rigid_group"] = "Base"

    cage = []
    for y in (-0.045, 0.045):
        profile = [(0.146, y-0.003), (0.150, y-0.003), (0.150, y+0.003),
                   (0.146, y+0.003), (0.146, y-0.003)]
        rim = gb.revolve("CageRim", profile, segments=32, axis="Y", cap=False)
        rim.location.z = 0.300
        cage.append(rim)
    for k in range(12):
        a = 2 * math.pi * k / 12
        x, z = math.sin(a), math.cos(a)
        rail = gb.sweep("CageRail", [(0.145*x, -0.045, 0.300+0.145*z),
                                    (0.150*x, 0, 0.300+0.150*z),
                                    (0.145*x, 0.045, 0.300+0.145*z)], gb.circle(0.002, 6))
        cage.append(rail)
        spoke = gb.sweep("CageSpoke", [(0.020*x, -0.045, 0.300+0.020*z),
                                      (0.080*x, -0.049, 0.300+0.080*z),
                                      (0.146*x, -0.045, 0.300+0.146*z)], gb.circle(0.0016, 6))
        cage.append(spoke)
    cap = gb.revolve("CageCap", [(0, -0.051), (0.019, -0.051), (0.023, -0.046),
                                 (0.023, -0.040), (0, -0.040)], segments=16, axis="Y")
    cap.location.z = 0.300
    cage.append(cap)
    guard = gb.join(cage, "Guard")
    gb.assign(guard, cream)
    gb.set_origin(guard, mode="point", point=(0, 0, 0.300))
    gb.parent(guard, root)
    guard["rigid_group"] = "Base"

    rotor_parts = []
    hub = gb.revolve("RotorHub", [(0, -0.025), (0.018, -0.025), (0.024, -0.018),
                                  (0.024, -0.006), (0.018, 0.004), (0, 0.004)],
                        segments=20, axis="Y")
    hub.location.z = 0.300
    rotor_parts.append(hub)
    paddle = [(-0.011, 0.011), (0.011, 0.011), (0.039, 0.052),
              (0.043, 0.110), (0.029, 0.126), (-0.004, 0.122),
              (-0.011, 0.095), (-0.013, 0.043)]
    for k in range(4):
        blade = gb.extrude("Blade", paddle, 0.006, axis="Y")
        blade.data.transform(Matrix.Rotation(k*math.pi/2, 4, "Y"))
        blade.location = (0, -0.015, 0.300)
        gb.bevel(blade, 0.001, segments=1)
        rotor_parts.append(blade)
    rotor = gb.join(rotor_parts, "Rotor")
    gb.assign(rotor, sage)
    gb.set_origin(rotor, mode="point", point=(0, -0.0105, 0.300))
    gb.set_joint(rotor, "spin", "Y")
    gb.parent(rotor, root)
    gb.socket("cord", (0, 0.080, 0.025), parent_obj=root)
    collision = gb.collision_box(base, include_children=False)
    gb.parent(collision, root)
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, required=True)
    parser.add_argument("--asset", default="desk_fan")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--blend", type=Path, help="Optional editable source copy")
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else sys.argv[1:]
    args = parser.parse_args(argv)
    scripts = args.skill_dir.resolve() / "scripts" / "blender"
    if not (scripts / "gs_build.py").is_file():
        parser.error("--skill-dir must contain scripts/blender/gs_build.py")
    if args.out.suffix.lower() != ".glb":
        parser.error("--out must end in .glb")
    if args.blend and args.blend.suffix.lower() != ".blend":
        parser.error("--blend must end in .blend")
    sys.path.insert(0, str(scripts))
    import bpy
    import gs_build as gb
    root = build_asset(gb, args.asset)
    output = args.out.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    gb.export_glb(str(output), roots=[root])
    if args.blend:
        source = args.blend.resolve()
        source.parent.mkdir(parents=True, exist_ok=True)
        gb.save_blend(str(source))
    objects = [o for o in bpy.data.objects if o.get("gs_owner") == args.asset]
    print("GS_BUILD_JSON " + json.dumps({
        "asset": args.asset, "output": str(output), "stage": "functional-fixture",
        "render_parts": [o.name for o in objects if o.type == "MESH" and not o.name.endswith("-colonly")],
        "joints": {o.name: o.get("joint") for o in objects if o.get("joint")},
        "sockets": [o.name for o in objects if o.name.startswith("SOCKET_")],
        "blender_version": bpy.app.version_string,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
