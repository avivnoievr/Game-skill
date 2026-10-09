"""Numeric animation QA for every action on a rigged model: loop seam, root motion, implied ground speed, foot skate.

Usage (Blender):  blender -b --factory-startup --python-exit-code 1 -P clip_report.py -- MODEL [options]
Usage (pip bpy):  python clip_report.py MODEL [options]
Options:
  --feet A,B       foot/toe bone names (default: bones whose names contain foot/toe/ankle, lowest ones)
  --loops REGEX    clips that must loop (default: idle|walk|run|loop|cycle, case-insensitive)
  --json PATH      write the full report
Distances are in model units (glTF/Blender: 1 unit = 1 m). Exit codes: 0 = no FAIL, 1 = FAIL, 2 = error.

What it measures (see references/animation.md section 8):
  loop seam      jump from the last frame back to the first vs a normal frame step (a pop = FAIL)
  root speed     horizontal root displacement / duration (≈0 for in-place clips)
  ground speed   for in-place locomotion: median backward speed of planted feet = the speed gameplay must
                 move the character at to avoid foot sliding
  foot skate     root-motion clips: share of planted-foot frames whose foot moves > 2.5 cm/frame at 30 fps
"""
import argparse
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402
import numpy as np  # noqa: E402

from gs_common import die, load_model, script_args  # noqa: E402


def assign(arm, act):
    ad = arm.animation_data or arm.animation_data_create()
    for track in ad.nla_tracks:
        track.mute = True
    ad.action = act
    if hasattr(ad, "action_slot") and getattr(ad, "action_slot", None) is None and getattr(act, "slots", None):
        ad.action_slot = act.slots[0]


def sample(arm, f0, f1):
    """World-space bone head positions, shape (frames, bones, 3)."""
    scene = bpy.context.scene
    names = [pb.name for pb in arm.pose.bones]
    out = []
    for f in range(f0, f1 + 1):
        scene.frame_set(f)
        mw = arm.matrix_world
        out.append([tuple(mw @ pb.head) for pb in arm.pose.bones])
    return names, np.array(out, dtype=np.float64)


def main():
    p = argparse.ArgumentParser(prog="clip_report.py", description=__doc__.split("\n")[0])
    p.add_argument("model")
    p.add_argument("--feet")
    p.add_argument("--loops", default=r"idle|walk|run|loop|cycle")
    p.add_argument("--json")
    a = p.parse_args(script_args())
    load_model(a.model)
    arm = next((o for o in bpy.context.scene.objects if o.type == "ARMATURE"), None)
    if arm is None:
        die("no armature in the model")
    if not bpy.data.actions:
        die("no actions (animation clips) in the model")
    scene = bpy.context.scene
    fps = scene.render.fps / scene.render.fps_base
    root = next(i for i, pb in enumerate(arm.pose.bones) if pb.parent is None)

    reports, fails = [], 0
    for act in bpy.data.actions:
        assign(arm, act)
        f0, f1 = int(act.frame_range[0]), int(act.frame_range[1])
        if f1 <= f0:
            continue
        names, pos = sample(arm, f0, f1)
        height = float(pos[0, :, 2].max() - pos[0, :, 2].min()) or 1.0
        rel = pos - pos[:, root:root + 1, :]
        # Loop seam: the jump from the last frame back to the first, compared with ordinary frame-to-frame
        # motion. ~0 when the clip repeats its first pose at the end; ~1x a normal step when it doesn't.
        wrap = float(np.linalg.norm(rel[-1] - rel[0], axis=1).max())
        step = float(np.median(np.linalg.norm(np.diff(rel, axis=0), axis=2).max(axis=1)))
        seam = wrap / height
        seam_ratio = wrap / step if step > 1e-9 else (0.0 if wrap < 1e-9 else float("inf"))
        duration = (f1 - f0) / fps
        root_disp = pos[-1, root, :2] - pos[0, root, :2]
        root_speed = float(np.linalg.norm(root_disp)) / duration
        in_place = float(np.linalg.norm(root_disp)) < 0.05 * height

        if a.feet:
            feet = [names.index(n) for n in a.feet.split(",") if n in names]
        else:
            cand = [i for i, n in enumerate(names) if re.search(r"foot|toe|ankle", n, re.I)]
            cand.sort(key=lambda i: pos[0, i, 2])
            feet = cand[:2]
        entry = {"clip": act.name, "frames": [f0, f1], "fps": round(fps, 2), "duration_s": round(duration, 3),
                 "rig_height": round(height, 3),
                 "loop_seam_pct": round(seam * 100, 2), "root_speed": round(root_speed, 3), "in_place": in_place,
                 "feet": [names[i] for i in feet], "checks": []}
        entry["loop_jump_vs_step"] = round(seam_ratio, 2) if seam_ratio != float("inf") else None
        must_loop = re.search(a.loops, act.name, re.I) is not None
        if must_loop and seam > 0.005 and seam_ratio > 5:
            entry["checks"].append(["FAIL", f"pop at the loop point: wrap jump is {seam_ratio:.1f}x a normal frame step"])
        elif must_loop and seam > 0.005 and seam_ratio > 2.5:
            entry["checks"].append(["WARN", f"loop point jump is {seam_ratio:.1f}x a normal frame step"])

        if feet:
            speeds, skating, planted = [], 0, 0
            for fi in feet:
                z = pos[:, fi, 2]
                low = z <= z.min() + 0.05 * height / 1.8   # 'planted': within 5 cm (human scale) of the lowest point
                world_v = np.linalg.norm(np.diff(pos[:, fi, :2], axis=0), axis=1)            # per frame
                rel_v = np.linalg.norm(np.diff(rel[:, fi, :2], axis=0), axis=1) * fps        # per second
                stance = low[1:] & low[:-1]
                planted += int(stance.sum())
                skating += int((world_v[stance] * (fps / 30.0) > 0.025 * height / 1.8).sum())
                speeds.extend(rel_v[stance].tolist())
            if in_place and speeds:
                entry["ground_speed"] = round(float(np.median(speeds)), 3)
            if not in_place and planted:
                ratio = skating / planted
                entry["foot_skate_ratio"] = round(ratio, 3)
                if ratio > 0.2:
                    entry["checks"].append(["FAIL", f"feet slide on {ratio:.0%} of planted frames"])
                elif ratio > 0.05:
                    entry["checks"].append(["WARN", f"feet slide on {ratio:.0%} of planted frames"])
        else:
            entry["checks"].append(["INFO", "no foot bones found (pass --feet) — skate/ground speed not measured"])
        fails += sum(1 for c in entry["checks"] if c[0] == "FAIL")
        reports.append(entry)

    rig = reports[0]["rig_height"] if reports else 0
    print(f"\n== clip_report: {os.path.basename(a.model)} (rig height {rig} units, {len(reports)} clips) ==")
    for e in reports:
        extra = f" ground speed {e['ground_speed']}/s" if "ground_speed" in e else ""
        extra += f" skate {e['foot_skate_ratio']:.0%}" if "foot_skate_ratio" in e else ""
        print(f"  {e['clip']}: {e['duration_s']}s @ {e['fps']}fps | loop jump {e['loop_jump_vs_step']}x step | "
              f"root speed {e['root_speed']}/s {'(in place)' if e['in_place'] else '(root motion)'}{extra}")
        for level, msg in e["checks"]:
            print(f"    {level} {msg}")
    print(f"VERDICT: {'FAIL' if fails else 'PASS'} ({fails} fail)")
    if a.json:
        with open(a.json, "w", encoding="utf-8") as fh:
            json.dump(reports, fh, indent=2)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
