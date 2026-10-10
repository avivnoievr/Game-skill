"""Real Blender animation fixtures for a positional blind spot and quaternion sign invariance.

blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_clip_report.py
"""
import contextlib
import io
import json
import math
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import bpy
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plugins/game-studio/skills/game-studio/scripts/blender"))
import clip_report as clips


class ClipRotationTests(unittest.TestCase):
    def fixture(self, pop):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        data = bpy.data.armatures.new("Rig")
        arm = bpy.data.objects.new("Rig", data)
        bpy.context.collection.objects.link(arm)
        bpy.context.view_layer.objects.active = arm
        arm.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")
        root = data.edit_bones.new("root")
        root.head, root.tail = (0, 0, 0), (0, 0, 1)
        leaf = data.edit_bones.new("leaf")
        leaf.head, leaf.tail, leaf.parent = (0, 0, 1), (0, 0, 2), root
        bpy.ops.object.mode_set(mode="POSE")
        bone = arm.pose.bones["leaf"]
        bone.rotation_mode = "XYZ"
        # Both clips have stationary heads. The bad one jumps by 90 degrees at the loop seam.
        for frame, angle in [(1, 0), (15, math.pi / 4), (30, math.pi / 2 if pop else 0)]:
            bone.rotation_euler.y = angle
            bone.keyframe_insert("rotation_euler", frame=frame)
        arm.animation_data.action.name = "WalkLoop"
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.context.scene.frame_set(1)

    def run_clip(self, pop):
        self.fixture(pop)
        with tempfile.TemporaryDirectory(prefix="clip-rotation-") as temp:
            directory = Path(temp)
            model, report = directory / "rig.blend", directory / "report.json"
            bpy.ops.wm.save_as_mainfile(filepath=str(model))
            with patch.object(clips, "script_args", return_value=[str(model), "--json", str(report)]):
                with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as result:
                    clips.main()
            return result.exception.code, json.loads(report.read_text())[0]

    def test_good_pose_loop_passes(self):
        code, report = self.run_clip(False)
        self.assertEqual(code, 0)
        self.assertEqual(report["loop_rotation_jump_deg"], 0)

    def test_rotation_pop_fails_even_when_bone_heads_do_not_move(self):
        code, report = self.run_clip(True)
        self.assertEqual(code, 1)
        self.assertEqual(report["loop_seam_pct"], 0)
        self.assertAlmostEqual(report["loop_rotation_jump_deg"], 90, places=2)
        self.assertTrue(any(c[0] == "FAIL" and "rotation pop" in c[1] for c in report["checks"]))

    def test_quaternion_sign_does_not_make_a_fake_pop(self):
        q = np.array([[math.sqrt(0.5), math.sqrt(0.5), 0, 0]])
        self.assertLess(float(clips.rotation_jump(q, -q)[0]), 1e-6)


if __name__ == "__main__":
    result = unittest.main(argv=[sys.argv[0]], verbosity=2, exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError("clip rotation fixtures failed")
