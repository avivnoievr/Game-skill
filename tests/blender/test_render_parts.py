"""Real Blender parent-aware exploded view and exception-restoration fixtures.

blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_render_parts.py
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
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "plugins/game-studio/skills/game-studio/scripts/blender"))
import render_views as renderer
from gs_common import world_bbox


class RenderPartsTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-1, 0, 0))
        self.parent = bpy.context.object
        self.parent.name = "Parent"
        bpy.ops.mesh.primitive_cube_add(size=0.5, location=(1, 0, 0))
        self.child = bpy.context.object
        self.child.name = "Child"
        world = self.child.matrix_world.copy()
        self.child.parent = self.parent
        self.child.matrix_world = world
        bpy.context.view_layer.update()
        self.meshes = [self.child, self.parent]  # deliberately wrong input order
        self.before = {o.name: o.matrix_world.copy() for o in self.meshes}
        self.colors = {o.name: tuple(o.color) for o in self.meshes}
        lo, hi = world_bbox(self.meshes)
        self.center = (lo + hi) / 2

    def assertRestored(self):
        for obj in self.meshes:
            self.assertTrue(all(abs(a-b) < 1e-6 for a,b in zip(sum((list(row) for row in obj.matrix_world), []),
                                                               sum((list(row) for row in self.before[obj.name]), []))))
            self.assertEqual(tuple(obj.color), self.colors[obj.name])
        self.assertEqual(self.child.parent, self.parent)

    def test_offsets_are_applied_once_parent_first(self):
        offsets = {}
        for obj in self.meshes:
            lo, hi = world_bbox([obj])
            offsets[obj.name] = ((lo + hi) / 2 - self.center) * 0.4
        def inspect(key):
            self.assertEqual(bpy.context.scene.display.shading.color_type, "OBJECT")
            self.assertEqual(bpy.context.scene.display.shading.light, "FLAT")
            self.assertEqual(len({tuple(v["color"]) for v in key}), 2)
            for obj in self.meshes:
                expected = self.before[obj.name].translation + offsets[obj.name]
                self.assertLess((obj.matrix_world.translation - expected).length, 1e-6)
        renderer.with_parts(self.meshes, self.center, inspect)
        self.assertRestored()

    def test_restore_after_render_failure(self):
        original = bpy.context.scene.display.shading.color_type
        with self.assertRaisesRegex(RuntimeError, "fixture"):
            renderer.with_parts(self.meshes, self.center,
                                lambda key: (_ for _ in ()).throw(RuntimeError("fixture")))
        self.assertRestored()
        self.assertEqual(bpy.context.scene.display.shading.color_type, original)

    def test_real_parts_thumbnail_and_key(self):
        with tempfile.TemporaryDirectory(prefix="render-parts-") as temp:
            directory = Path(temp)
            model = directory / "fixture.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(model))
            with patch.object(renderer, "script_args", return_value=[str(model), "--out", str(directory / "views"),
                                                                     "--views", "parts", "--size", "96"]):
                renderer.main()
            report = json.loads((directory / "views/views.json").read_text())
            self.assertEqual([v["view"] for v in report["views"]], ["parts"])
            self.assertEqual(len(report["parts"]), 2)
            self.assertGreater((directory / "views/parts.png").stat().st_size, 100)

    def test_default_multipart_selection_and_opt_out(self):
        # Blender operator namespaces are dynamic; these default views also render real small PNGs.
        with tempfile.TemporaryDirectory(prefix="render-default-") as temp:
            directory = Path(temp)
            model = directory / "fixture.blend"
            bpy.ops.wm.save_as_mainfile(filepath=str(model))
            for no_parts in [False, True]:
                args = [str(model), "--out", str(directory / "views"), "--no-sheet", "--size", "64"]
                if no_parts:
                    args.append("--no-parts")
                with patch.object(renderer, "script_args", return_value=args):
                    with contextlib.redirect_stdout(io.StringIO()):
                        renderer.main()
                report = json.loads((directory / "views/views.json").read_text())
                self.assertEqual("parts" in [v["view"] for v in report["views"]], not no_parts)


if __name__ == "__main__":
    result = unittest.main(argv=[sys.argv[0]], verbosity=2, exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError("render parts fixtures failed")
