"""Real Blender inspector fixtures: required parts, pivots, sockets and glTF extras.

blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_inspect_parts.py
"""
import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plugins/game-studio/skills/game-studio/scripts/blender"))
import inspect_model as inspector
from gs_common import load_model


def box(name, size, location, parent=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.transform(Matrix.Diagonal((*size, 1)))
    mat = bpy.data.materials.get("FixtureMaterial") or bpy.data.materials.new("FixtureMaterial")
    obj.data.materials.append(mat)
    if parent:
        world = obj.matrix_world.copy()
        obj.parent = parent
        obj.matrix_world = world
    return obj


def fixture():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    root = bpy.data.objects.new("Vehicle", None)
    bpy.context.collection.objects.link(root)
    box("Body", (2, 4, 1), (0, 0, 1), root)
    for side, x in [("L", -1.3), ("R", 1.3)]:
        for end, y in [("F", -1), ("R", 1)]:
            wheel = box(f"Wheel_{end}{side}", (0.3, 0.6, 0.6), (x, y, 0.3), root)
            wheel["joint"], wheel["axis"] = "spin", "X"
    socket = bpy.data.objects.new("SOCKET_seat_driver", None)
    bpy.context.collection.objects.link(socket)
    socket.parent = root
    col = box("Body-colonly", (2, 4, 1), (0, 0, 1), root)
    col.hide_render = True
    bpy.context.view_layer.update()
    return root


class InspectorPartsTests(unittest.TestCase):
    def setUp(self):
        fixture()
        self.tmp = tempfile.TemporaryDirectory(prefix="inspect-parts-")
        self.addCleanup(self.tmp.cleanup)

    def inspect(self, *args, glb=False):
        directory = Path(self.tmp.name)
        model = directory / ("fixture.glb" if glb else "fixture.blend")
        if glb:
            bpy.ops.export_scene.gltf(filepath=str(model), export_format="GLB", export_extras=True)
        else:
            bpy.ops.wm.save_as_mainfile(filepath=str(model))
        report = directory / "report.json"
        with patch.object(inspector, "script_args", return_value=[str(model), "--json", str(report), *args]):
            with contextlib.redirect_stdout(io.StringIO()), self.assertRaises(SystemExit) as exit_info:
                inspector.main()
        return exit_info.exception.code, json.loads(report.read_text())

    def test_good_parts_and_glb_extras_round_trip(self):
        code, report = self.inspect("--parts", "Wheel_FL,Wheel_FR,Wheel_RL,Wheel_RR", "--sockets", "seat_driver", glb=True)
        self.assertEqual(code, 0)
        self.assertEqual(len(report["parts"]), 4)
        self.assertTrue(all(p["joint"] == "spin" for p in report["parts"]))
        self.assertFalse(any(c["check"] == "floating" for c in report["checks"]))
        self.assertEqual(report["summary"]["meshes"], 5)
        self.assertEqual(report["summary"]["triangles"], 60)  # collision excluded
        self.assertEqual(report["collisions"][0]["triangles"], 12)
        wheel = next(n for n in report["hierarchy"] if n["name"] == "Wheel_FL")
        self.assertEqual(wheel["parent"], "Vehicle")
        self.assertEqual(wheel["axis"], "X")

    def test_even_small_declared_triangle_overrun_fails(self):
        code, report = self.inspect("--max-tris", "59")
        self.assertEqual(code, 1)
        self.assertTrue(any(c["check"] == "budget" and c["level"] == "FAIL"
                            and "triangles 60 / budget 59" in c["message"] for c in report["checks"]))

    def test_missing_part_socket_and_geometry_fail(self):
        bpy.data.objects.remove(bpy.data.objects["Wheel_FR"], do_unlink=True)
        dummy = bpy.data.objects.new("Dummy", None)
        bpy.context.collection.objects.link(dummy)
        code, report = self.inspect("--parts", "Wheel_FL,Wheel_FR,Dummy", "--sockets", "missing")
        self.assertEqual(code, 1)
        fails = [c for c in report["checks"] if c["level"] == "FAIL"]
        self.assertTrue(any("Wheel_FR" in c["message"] for c in fails))
        self.assertTrue(any(c["object"] == "Dummy" for c in fails))
        self.assertTrue(any(c["check"] == "socket" for c in fails))

    def test_displaced_spin_pivot_fails_even_without_required_flags(self):
        wheel = bpy.data.objects["Wheel_FL"]
        wheel.data.transform(Matrix.Translation((0.1, 0, 0)))
        code, report = self.inspect()
        self.assertEqual(code, 1)
        self.assertTrue(any(c["level"] == "FAIL" and c["check"] == "part_pivot" for c in report["checks"]))
        code, _ = self.inspect("--part-pivot", "any")
        self.assertEqual(code, 0)

    def test_hinge_pivot_is_not_assumed_to_be_center(self):
        door = box("Door", (0.2, 1, 1), (4, 0, 1))
        door["joint"], door["axis"] = "hinge", "Z"
        door.data.transform(Matrix.Translation((0, 0.5, 0)))
        code, report = self.inspect("--parts", "Door")
        self.assertEqual(code, 0)
        self.assertFalse(any(c["check"] == "part_pivot" and c["object"] == "Door" for c in report["checks"]))

    def test_floating_piece_still_warns_inside_one_moving_group(self):
        wheel = bpy.data.objects["Wheel_FL"]
        box("LooseLug", (0.05, 0.05, 0.05), (-3, -1, 0.3), wheel)
        code, report = self.inspect()
        self.assertEqual(code, 1)  # the detached piece also displaces the group's bounds center
        self.assertTrue(any(c["check"] == "floating" and c["rigid_group"] == "Wheel_FL" for c in report["checks"]))

    def test_joint_axis_and_dense_collision_are_reported(self):
        del bpy.data.objects["Wheel_FL"]["axis"]
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16)
        bpy.context.object.name = "Dense-colonly"
        code, report = self.inspect()
        self.assertEqual(code, 1)
        self.assertTrue(any(c["level"] == "FAIL" and c["check"] == "joint" for c in report["checks"]))
        self.assertTrue(any(c["level"] == "WARN" and c["check"] == "collision" for c in report["checks"]))
        self.assertEqual(report["summary"]["triangles"], 60)

    def test_glob_matches_and_untagged_required_part_pivot(self):
        code, _ = self.inspect("--parts", "Wheel_*")
        self.assertEqual(code, 0)
        wheel = bpy.data.objects["Wheel_FL"]
        del wheel["joint"]
        wheel.data.transform(Matrix.Translation((0.1, 0, 0)))
        code, report = self.inspect("--parts", "Wheel_FL", "--part-pivot", "center")
        self.assertEqual(code, 1)
        self.assertTrue(any(c["check"] == "part_pivot" and c["object"] == "Wheel_FL" and c["level"] == "FAIL"
                            for c in report["checks"]))

    def test_required_static_body_does_not_default_to_center_pivot(self):
        body = bpy.data.objects["Body"]
        body.data.transform(Matrix.Translation((0, 0, 0.5)))  # base origin is legitimate for a static body
        code, report = self.inspect("--parts", "Body,Wheel_*")
        self.assertEqual(code, 0)
        self.assertFalse(any(c["check"] == "part_pivot" and c["object"] == "Body" for c in report["checks"]))


if __name__ == "__main__":
    result = unittest.main(argv=[sys.argv[0]], verbosity=2, exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError("inspector parts fixtures failed")
