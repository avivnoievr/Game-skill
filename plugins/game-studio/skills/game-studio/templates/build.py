"""Copy to assets/<asset>/build.py and replace build_asset with the approved part plan.

Run with the developer's existing Blender:
  blender -b --factory-startup --python-exit-code 1 -P build.py -- \
    --skill-dir /absolute/game-studio --asset crate --out out/crate.glb
The starter block is a blockout, not an accepted finished asset.
"""
import argparse
import json
from pathlib import Path
import sys


def build_asset(gb, asset_id):
    gb.begin(asset_id)
    root = gb.empty(asset_id)
    body = gb.box("Body", size=(0.6, 0.6, 0.6), location=(0, 0, 0.3))
    gb.assign(body, gb.material("blockout", "#617D73"))
    gb.set_origin(body, mode="base")
    gb.parent(body, root)
    # Add required moving objects/joints and sockets here; never join moving parts.
    return root


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, required=True)
    parser.add_argument("--asset", default="blockout")
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
        "asset": args.asset, "output": str(output), "stage": "blockout",
        "render_parts": [o.name for o in objects if o.type == "MESH" and not o.name.endswith("-colonly")],
        "joints": {o.name: o.get("joint") for o in objects if o.get("joint")},
        "sockets": [o.name for o in objects if o.name.startswith("SOCKET_")],
        "blender_version": bpy.app.version_string,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
