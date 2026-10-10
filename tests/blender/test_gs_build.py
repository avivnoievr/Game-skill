"""Geometry/ownership regression fixtures, executed by Blender's Python (no pip dependencies).

    blender -b --factory-startup --python-exit-code 1 -P tests/blender/test_gs_build.py -- --out work/gs-build-tests

The output directory contains a clean multipart car and atlas GLB for independent inspection. Tests
also feed malformed geometry, illegal moving-part joins, and lossy atlas inputs to the helpers.
"""
import argparse
import json
import math
import os
from pathlib import Path
import runpy
import struct
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import bpy
import bmesh
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "plugins/game-studio/skills/game-studio/scripts/blender"
sys.path.insert(0, str(SCRIPTS))
import gs_build as gb
from gs_common import is_collision, script_args
from inspect_model import Report, floating_parts


def glb_json(path):
    data = Path(path).read_bytes()
    magic, version, length = struct.unpack_from("<4sII", data)
    assert (magic, version, length) == (b"glTF", 2, len(data))
    chunk_length, chunk_type = struct.unpack_from("<I4s", data, 12)
    assert chunk_type == b"JSON"
    return json.loads(data[20:20 + chunk_length])


def topology(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    result = {"degenerate": sum(f.calc_area() < 1e-10 for f in bm.faces),
              "nonmanifold": sum(len(e.link_faces) > 2 for e in bm.edges),
              "loose": sum(not v.link_edges for v in bm.verts)}
    bm.free()
    return result


def world_vertices(obj):
    bpy.context.view_layer.update()
    return [obj.matrix_world @ v.co for v in obj.data.vertices]


class BuildTests(unittest.TestCase):
    output = None

    def setUp(self):
        gb.begin("tests")

    def assertPointsEqual(self, a, b):
        self.assertEqual(len(a), len(b))
        # Blender stores mesh coordinates in float32; 2 microns covers rounding in this ~10 m fixture.
        self.assertTrue(all((p - q).length < 2e-6 for p, q in zip(a, b)))

    def test_car_geometry_pivots_and_spike_regression(self):
        car = runpy.run_path(str(SCRIPTS / "examples/car_stylized.py"))
        root = car["build"]()
        body = bpy.data.objects["Body"]
        lo, hi = gb.bounds(body)
        self.assertGreaterEqual(hi.z, 1.439)
        self.assertLessEqual(hi.z, 1.451)  # original implementation produced a 1.490 m roof spike
        self.assertAlmostEqual(hi.y - lo.y, 4.5, places=4)
        self.assertEqual(topology(body), {"degenerate": 0, "nonmanifold": 0, "loose": 0})
        wheels = [o for o in root.children_recursive if o.get("joint") == "spin"]
        self.assertEqual({o.name for o in wheels}, {"Wheel_FL", "Wheel_FR", "Wheel_RL", "Wheel_RR"})
        for wheel in wheels:
            lo, hi = gb.bounds(wheel)
            self.assertLess(((lo + hi) / 2 - wheel.matrix_world.translation).length, 0.002)
            self.assertLess(abs(lo.z), 0.001)
            self.assertEqual(wheel["axis"], "X")
            self.assertTrue(all(s > 0 for s in wheel.scale))
            contact = Report()
            floating_parts([wheel], bpy.context.evaluated_depsgraph_get(), 0.002, contact)
            self.assertFalse(any(c["level"] == "WARN" and c["check"] == "floating" for c in contact.checks),
                             "rim, tire bead and spokes must physically connect within the rigid wheel")
        meshes = [o for o in root.children_recursive if o.type == "MESH" and not is_collision(o)]
        keep = {m.name for o in meshes for m in o.data.materials if m and m.get("gs_light")}
        gb.palette_atlas(meshes, self.output / "car_palette.png", name="car_palette", keep=keep)
        path = self.output / "car.glb"
        gb.export_glb(path, [root])
        gb.save_blend(self.output / "car.blend")
        g = glb_json(path)
        # Two independent lamp materials plus one opaque palette, not a misleading two-material count.
        self.assertEqual({m["name"] for m in g["materials"]}, {"car_palette", "head", "tail"})
        self.assertEqual(len(g["textures"]), 2)
        for sampler in g["samplers"]:
            self.assertEqual(sampler["magFilter"], 9728)
            self.assertEqual(sampler["minFilter"], 9984)
        names = {n["name"]: n for n in g["nodes"]}
        self.assertEqual(names["Wheel_FL"]["extras"]["joint"], "spin")
        self.assertEqual(names["Steer_FL"]["extras"]["joint"], "steer")
        self.assertIn("SOCKET_seat_driver", names)
        gb.begin("imported_car")
        bpy.ops.import_scene.gltf(filepath=str(path))
        self.assertEqual(bpy.data.objects["Wheel_FL"]["joint"], "spin")
        self.assertEqual(topology(bpy.data.objects["Body"])["degenerate"], 0)

    def test_recess_is_inward_and_rejects_missing_or_negative_inputs(self):
        obj = gb.box("Panel", (1, 1, 1))
        gb.recess(obj, lambda f: f.normal.z > 0.9, inset=0.05, depth=0.1)
        upper = sorted({round(v.co.z, 3) for v in obj.data.vertices if v.co.z > 0})
        self.assertEqual(upper, [0.4, 0.5])
        self.assertEqual(topology(obj)["degenerate"], 0)
        before = [v.co.copy() for v in obj.data.vertices]
        with self.assertRaisesRegex(ValueError, "no faces"):
            gb.recess(obj, lambda f: False)
        with self.assertRaisesRegex(ValueError, "nonnegative"):
            gb.recess(obj, lambda f: True, depth=-1)
        self.assertPointsEqual(before, [v.co for v in obj.data.vertices])

    def test_boolean_cleanup_does_not_destroy_real_panel_gap(self):
        body = gb.box("Block", (2, 2, 2))
        cutter = gb.box("Opening", (0.25, 3, 0.25))
        gb.cut(body, cutter)
        self.assertEqual(topology(body), {"degenerate": 0, "nonmanifold": 0, "loose": 0})
        bm = bmesh.new()
        v0 = bm.verts.new((0, 0, 0)); v1 = bm.verts.new((0, 0, 0))
        v2 = bm.verts.new((1, 0, 0)); v3 = bm.verts.new((0, 1, 0))
        bm.faces.new((v0, v1, v2, v3))  # intentionally defective zero-length edge
        self.assertTrue(any(e.calc_length() < 1e-10 for e in bm.edges))
        gb._clean_bmesh(bm)
        self.assertTrue(all(e.calc_length() > 1e-7 for e in bm.edges))
        self.assertEqual(len(bm.faces), 1)
        bm.free()
        gap = gb.box("SmallSeam", (0.003, 0.01, 0.02))
        gb._clean_mesh(gap)
        self.assertEqual(len(gap.data.polygons), 6)
        self.assertAlmostEqual(gb.bounds(gap)[1].x - gb.bounds(gap)[0].x, 0.003, places=6)

    def test_join_refuses_moving_parts_before_mutation(self):
        body = gb.box("Static")
        wheel = gb.box("Moving")
        gb.set_joint(wheel, "spin", "X")
        with self.assertRaisesRegex(ValueError, "moving parts"):
            gb.join([body, wheel])
        self.assertIn(wheel.name, bpy.data.objects)
        self.assertEqual(len(body.data.polygons), 6)

    def test_modifier_cleanup_preserves_custom_corner_normals(self):
        obj = gb.box("Beveled", (1, 2, 3))
        gb.bevel(obj, 0.08, segments=2)
        gb.weighted_normals(obj)
        bpy.context.view_layer.update()
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()

        def normals_by_corner(me):
            return {(tuple(round(c, 6) for c in p.center),
                     tuple(round(c, 6) for c in me.vertices[me.loops[i].vertex_index].co)):
                    me.corner_normals[i].vector.copy() for p in me.polygons for i in p.loop_indices}

        before = normals_by_corner(mesh)
        evaluated.to_mesh_clear()
        gb.apply_modifiers(obj)
        after = normals_by_corner(obj.data)
        self.assertTrue(obj.data.has_custom_normals)
        self.assertEqual(before.keys(), after.keys())
        self.assertTrue(all(before[k].dot(after[k]) > 0.9999 for k in before))

    def test_join_keeps_developer_linked_mesh_unchanged(self):
        obj = gb.box("Part")
        linked = obj.copy(); linked.data = obj.data
        bpy.context.scene.collection.objects.link(linked)
        before = world_vertices(linked)
        other = gb.box("Other", location=(2, 0, 0))
        gb.join([obj, other])
        self.assertEqual(len(linked.data.polygons), 6)
        self.assertNotEqual(obj.data, linked.data)
        self.assertPointsEqual(before, world_vertices(linked))

    def test_transform_helpers_preserve_geometry_and_linked_users(self):
        obj = gb.box("Part", (1, 2, 3), (4, 5, 6))
        obj.rotation_euler = (0.2, -0.3, 0.8)
        obj.scale = (1.3, 0.8, 1.1)
        linked = obj.copy(); linked.data = obj.data
        bpy.context.scene.collection.objects.link(linked)
        original = world_vertices(obj); other = world_vertices(linked)
        gb.set_origin(obj, "point", point=(4.1, 4.8, 6.3))
        self.assertPointsEqual(original, world_vertices(obj))
        self.assertPointsEqual(other, world_vertices(linked))
        self.assertNotEqual(obj.data, linked.data)
        gb.apply_rot_scale(obj)
        self.assertPointsEqual(original, world_vertices(obj))
        self.assertPointsEqual(other, world_vertices(linked))
        root = gb.empty("Root", (10, -3, 2)); root.rotation_euler.z = 0.5
        gb.parent(obj, root)
        self.assertPointsEqual(original, world_vertices(obj))

    def test_live_restart_preserves_developer_collections_objects_and_parent(self):
        developer = bpy.data.collections.new("Developer")
        bpy.context.scene.collection.children.link(developer)
        collision = bpy.data.collections.new("GS_live")  # an unowned name collision
        bpy.context.scene.collection.children.link(collision)
        user = bpy.data.objects.new("KeepMe", None); collision.objects.link(user)
        live_bpy = SimpleNamespace(app=SimpleNamespace(background=False), data=bpy.data, context=bpy.context)
        with patch.object(gb, "bpy", live_bpy):
            col = gb.begin("live")
        self.assertNotEqual(col, collision)
        shared = gb.box("Shared", location=(3, 2, 1)); developer.objects.link(shared)
        root = gb.empty("OldRoot", (5, 0, 0)); gb.parent(shared, root)
        before = world_vertices(shared)
        owned = gb.box("DiscardThis")
        name = owned.name
        unowned = bpy.data.objects.new("UserAdded", None); col.objects.link(unowned)
        nested = bpy.data.collections.new("UserNested"); col.children.link(nested)
        nested_obj = bpy.data.objects.new("NestedObj", None); nested.objects.link(nested_obj)
        with patch.object(gb, "bpy", live_bpy):
            again = gb.begin("live")
        self.assertEqual(again, col)
        self.assertNotIn(name, bpy.data.objects)
        self.assertIn(user.name, bpy.data.objects)
        self.assertEqual(list(collision.objects), [user])
        self.assertIn(shared.name, developer.objects)
        self.assertPointsEqual(before, world_vertices(shared))
        self.assertEqual(shared.parent, root)
        self.assertIn(unowned.name, bpy.context.scene.objects)
        self.assertIn(nested_obj.name, bpy.context.scene.objects)
        self.assertEqual(len(col.all_objects), 0)

    def test_live_material_and_atlas_never_overwrite_user_datablocks(self):
        user_mat = bpy.data.materials.new("Paint"); user_mat.use_nodes = True
        user_mat.diffuse_color = (0.1, 0.2, 0.3, 1)
        user_image = bpy.data.images.new("Palette", 4, 4)
        user_image.pixels[:] = [0.3, 0.4, 0.5, 1] * 16
        before_pixels = list(user_image.pixels)
        created = gb.material("Paint", "#FF0000")
        self.assertNotEqual(created, user_mat)
        self.assertAlmostEqual(user_mat.diffuse_color[0], 0.1)
        obj = gb.box("Asset"); gb.assign(obj, created)
        palette = gb.palette_atlas([obj], self.output / "isolated_palette.png", name="Palette")
        image = next(n.image for n in palette.node_tree.nodes if n.type == "TEX_IMAGE" and
                     n.image.colorspace_settings.name == "sRGB")
        self.assertNotEqual(image, user_image)
        self.assertEqual(list(user_image.pixels), before_pixels)
        self.assertEqual(tuple(user_image.size), (4, 4))

    def test_shared_owned_material_is_not_edited_on_rebuild(self):
        mat = gb.material("SharedPaint", "#AA0000")
        obj = gb.box("DeveloperCopy"); gb.assign(obj, mat)
        gb._collection().objects.unlink(obj)
        bpy.context.scene.collection.objects.link(obj)
        before = gb._bsdf(mat).inputs["Base Color"].default_value[:]
        rebuilt = gb.material("SharedPaint", "#0000AA")
        self.assertNotEqual(mat, rebuilt)
        self.assertEqual(gb._bsdf(mat).inputs["Base Color"].default_value[:], before)
        self.assertEqual(gb.material("SharedPaint", "#00AA00"), rebuilt)  # no material leak on repeat

    def test_palette_preserves_kept_faces_and_roughness_metallic_colors(self):
        obj = gb.box("Panel")
        paint = gb.material("Red", "#C8452F", roughness=0.35)
        metal = gb.material("Metal", "#A7AFB6", roughness=0.3, metallic=1)
        lamp = gb.material("Lamp", "#FFFFFF", emission="#FFFFFF")
        gb.assign(obj, paint)
        gb.assign(obj, metal, lambda f: f.normal.x > 0.9)
        gb.assign(obj, lamp, lambda f: f.normal.z > 0.9)
        expected_lamp_faces = sum(obj.data.materials[p.material_index] == lamp for p in obj.data.polygons)
        palette = gb.palette_atlas([obj], self.output / "palette.png", keep=[lamp.name])
        self.assertEqual(sum(obj.data.materials[p.material_index] == lamp for p in obj.data.polygons),
                         expected_lamp_faces)
        self.assertEqual(len(obj.data.materials), 2)
        tex = {n.image.colorspace_settings.name: n.image for n in palette.node_tree.nodes if n.type == "TEX_IMAGE"}
        # Find a cell through its face UV; check PNG samples, including gamma and ORM channels.
        for face in obj.data.polygons:
            if obj.data.materials[face.material_index] == lamp:
                continue
            uv = obj.data.uv_layers.active.data[face.loop_start].uv
            color = tex["sRGB"]; orm = tex["Non-Color"]
            x, y = int(uv.x * color.size[0]), int(uv.y * color.size[1])
            idx = (y * color.size[0] + x) * 4
            rgb = color.pixels[idx:idx + 3]
            expected = gb._hex_rgb("#A7AFB6" if face.normal.x > 0.9 else "#C8452F")
            self.assertTrue(all(abs(a - b) < 1 / 255 + 1e-6 for a, b in zip(rgb, expected)))
            self.assertAlmostEqual(orm.pixels[idx + 2], 1 if face.normal.x > 0.9 else 0, delta=1 / 255)
        gpath = self.output / "palette.glb"; gb.export_glb(gpath, [obj])
        g = glb_json(gpath)
        self.assertEqual({m["name"] for m in g["materials"]}, {"palette", "Lamp"})
        self.assertEqual(len(g["meshes"][0]["primitives"]), 2)

    def test_palette_refuses_lossy_inputs_before_mutation(self):
        obj = gb.box("Panel")
        emissive = gb.material("Emissive", "#FFFFFF", emission="#FFFFFF")
        gb.assign(obj, emissive)
        with self.assertRaisesRegex(ValueError, "keep emissive/transparent"):
            gb.palette_atlas([obj], self.output / "reject.png")
        self.assertEqual(list(obj.data.materials), [emissive])
        emissive = gb.material("Emissive", "#FFFFFF")  # reset emission on reuse
        self.assertEqual(gb._bsdf(emissive).inputs["Emission Strength"].default_value, 0)
        tex = emissive.node_tree.nodes.new("ShaderNodeTexImage")
        emissive.node_tree.links.new(tex.outputs["Color"], gb._bsdf(emissive).inputs["Base Color"])
        with self.assertRaisesRegex(ValueError, "not a constant palette"):
            gb.palette_atlas([obj], self.output / "reject.png")

    def test_operator_context_restored_on_success_and_failure(self):
        caller = gb.box("Developer")
        caller.select_set(True); bpy.context.view_layer.objects.active = caller
        bpy.ops.object.mode_set(mode="EDIT")
        a, b = gb.box("A"), gb.box("B", location=(2, 0, 0))
        gb.join([a, b], "Combined")
        self.assertEqual(bpy.context.view_layer.objects.active, caller)
        self.assertEqual(caller.mode, "EDIT")
        gb.export_glb(self.output / "context.glb", [a])
        self.assertEqual(bpy.context.view_layer.objects.active, caller)
        self.assertEqual(caller.mode, "EDIT")
        with patch.object(gb, "_select_tree", side_effect=RuntimeError("fixture export failure")):
            with self.assertRaisesRegex(RuntimeError, "fixture export failure"):
                gb.export_glb(self.output / "failed.glb", [a])
        self.assertEqual(bpy.context.view_layer.objects.active, caller)
        self.assertEqual(caller.mode, "EDIT")
        bpy.ops.object.mode_set(mode="OBJECT")
        self.assertEqual({o.name for o in bpy.context.selected_objects}, {"Developer"})

    def test_blueprints_stay_out_of_export(self):
        image = bpy.data.images.new("Source", 8, 8)
        image.filepath_raw = str(self.output / "source.png"); image.file_format = "PNG"; image.save()
        reference = gb.blueprint(str(self.output / "source.png"), "right", 4.5)
        self.assertTrue(reference.hide_select)
        self.assertTrue(reference.hide_render)
        self.assertTrue(reference.show_empty_image_only_axis_aligned)
        self.assertEqual(reference.empty_display_size, 4.5)
        gb.box("Asset")
        path = self.output / "reference.glb"; gb.export_glb(path)
        self.assertNotIn(reference.name, {n["name"] for n in glb_json(path)["nodes"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args(script_args())
    BuildTests.output = args.out or Path(tempfile.mkdtemp(prefix="gs-build-tests-"))
    BuildTests.output.mkdir(parents=True, exist_ok=True)
    result = unittest.main(argv=[sys.argv[0]], verbosity=2, exit=False).result
    if not result.wasSuccessful():
        raise RuntimeError("gs_build regression fixtures failed")
