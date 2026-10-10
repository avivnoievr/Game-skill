"""gs_build: tested building blocks for game-asset modeling in Blender (4.2+ and 5.x, headless or live).

Import it from the asset's build script (assets/<id>/build.py). The same script runs headless
(blender -b --factory-startup --python-exit-code 1 -P build.py -- --out X.glb) and in a live Blender MCP
session:

    import sys; sys.path.insert(0, r"<SKILL_DIR>/scripts/blender")
    import gs_build as gb
    gb.begin("crate")          # headless: empty scene. Live: clears and reuses only collection GS_crate

Conventions (references/modeling.md): meters; Z up; the asset's FRONT faces -Y (+Z in glTF); origin at the
base center for the asset, ON THE JOINT for every part that moves. Built with the data API and bmesh, so a
build script is deterministic and can be re-run any number of times.

Shapes come from the operation that owns the form, not from primitive soup:
  loft(name, sections)            changing cross-section (car body, hull, handle, bottle)
  revolve(name, profile, axis)    axially symmetric (wheel, barrel, column, lamp)
  extrude(name, outline, depth)   constant cross-section (beam, trim, rail, bracket, light lens)
  sweep(name, path, outline)      along a path (pipe, cable, handrail, tube frame)
  box(name, size)                 blocks and blockout only
Finishing:  cut(obj, cutter) -> bevel(obj, width) -> weighted_normals(obj) · recess(obj, select, ...)
            sharp_by_angle(obj) · apply_modifiers(obj)
Materials:  material(name, "#hex", roughness, metallic) · assign(obj, mat, select) · palette_atlas(objs, png)
Structure:  empty(name) · parent(child, parent) · set_origin(obj, mode) · join(static_parts) · delete(obj)
            set_joint(part, "spin"|"hinge"|"slide"|"steer", axis) · socket(name, location) · collision_box(obj)
Parts:      wheel(name, radius, width) · tire_dims("205/55R16")
Reference:  blueprint(png, view, width)  (image empty for modeling against orthographic references)
Output:     export_glb(path, roots) · save_blend(path)
"""
import math
import os
import re
from contextlib import contextmanager

import bpy  # import before bmesh/mathutils (required by the PyPI bpy module)
import bmesh
from mathutils import Matrix, Vector

__all__ = ["begin", "material", "assign", "palette_atlas", "circle", "rounded_rect", "loft", "revolve",
           "extrude", "sweep", "box", "shade_smooth", "sharp_by_angle", "bevel", "weighted_normals", "recess",
           "apply_modifiers", "cut", "bounds", "set_origin", "apply_rot_scale", "parent", "join", "delete",
           "empty", "socket", "set_joint", "collision_box", "tire_dims", "wheel", "blueprint", "export_glb",
           "save_blend"]

_STATE = {"asset": None, "collection": None}
JOINTS = ("spin", "hinge", "slide", "steer")
GLTF_AXIS = {"X": "X", "Y": "-Z", "Z": "Y"}  # Blender local axis -> glTF local axis (+Y up export)


# ---------------------------------------------------------------- session

def begin(asset):
    """Start (or restart) building `asset`; call once at the top of every build script.

    Headless (blender -b): a fresh factory scene in meters. Live session (MCP): the user's scene is NOT
    reset. Only collection GS_<asset> is emptied and reused, so re-running the script is idempotent and never
    touches the user's other objects.
    """
    if bpy.app.background:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.context.scene.unit_settings.system = "METRIC"
        bpy.context.scene.unit_settings.scale_length = 1.0
    scene = bpy.context.scene
    if abs(scene.unit_settings.scale_length - 1.0) > 1e-6:
        print(f"gs_build WARNING: scene unit scale is {scene.unit_settings.scale_length}, not 1.0; "
              "sizes in this script are meters")
    name = f"GS_{asset}"
    # A user may already have a collection with this name. Never adopt or clear it by name alone.
    col = next((c for c in bpy.data.collections if c.get("gs_owner") == asset and c.get("gs_build")), None)
    if col is None:
        col = bpy.data.collections.new(name)
        col["gs_owner"], col["gs_build"] = asset, True
    else:
        protected = {o for o in col.objects if o.get("gs_owner") != asset or
                     any(c != col for c in o.users_collection)}
        for o in list(protected):
            p = o.parent
            while p is not None and p in col.objects.values():
                protected.add(p)
                p = p.parent
        for o in list(col.objects):
            # Objects linked into another collection may be used by the developer's scene. Detach them
            # from this build, rather than deleting them everywhere. Unowned objects receive the same care.
            if o in protected:
                if len(o.users_collection) == 1:
                    scene.collection.objects.link(o)
                col.objects.unlink(o)
            else:
                delete(o)
        # Library builders link directly into col. Preserve any child collections the user added.
        for child in list(col.children):
            col.children.unlink(child)
            if child not in scene.collection.children_recursive:
                scene.collection.children.link(child)
    if col not in scene.collection.children_recursive:
        scene.collection.children.link(col)
    _STATE.update(asset=asset, collection=col)
    return col


def _collection():
    return _STATE["collection"] or bpy.context.scene.collection


def _owner():
    return _STATE["asset"] or "gs"


def _update():
    """Refresh matrix_world and evaluated meshes. Setting obj.location does not update matrix_world until
    the view layer updates, so transforms are read only after this."""
    bpy.context.view_layer.update()


def _link(name, bm, smooth=False):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    if smooth:
        me.polygons.foreach_set("use_smooth", [True] * len(me.polygons))
    obj = bpy.data.objects.new(name, me)
    obj["gs_owner"] = _owner()
    _collection().objects.link(obj)
    return obj


# ---------------------------------------------------------------- materials

def _hex_rgb(hexs):
    h = hexs.lstrip("#")
    return [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _linear_to_srgb(c):
    return c * 12.92 if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def _bsdf(mat):
    return next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")


def _new_material(name):
    """A material this build owns. An existing material of the same name that this build did not create
    (e.g. the user's own, in a live session) is never edited: Blender gives the new one a .001 name."""
    candidates = [m for m in bpy.data.materials if m.get("gs_owner") == _owner() and
                  (m.name == name or m.get("gs_name") == name)]
    own_objects = set(_collection().all_objects)
    mat = next((m for m in candidates if not any(o not in own_objects and o.type == "MESH" and
               m in list(o.data.materials) for o in bpy.data.objects)), None)
    if mat is None:
        mat = bpy.data.materials.new(name)
        mat["gs_owner"] = _owner()
    mat["gs_name"] = name
    if mat.node_tree is None and hasattr(mat, "use_nodes"):
        mat.use_nodes = True
    return mat


def material(name, color="#808080", roughness=0.6, metallic=0.0, emission=None, emission_strength=2.0,
             alpha=1.0):
    """glTF-safe Principled BSDF material from an sRGB hex color (art-bible palette). Reused by name."""
    mat = _new_material(name)
    mat["gs_hex"] = color
    lin = tuple(_srgb_to_linear(c) for c in _hex_rgb(color))
    bsdf = _bsdf(mat)
    bsdf.inputs["Base Color"].default_value = (*lin, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    sock = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
    sock.default_value = (*(_srgb_to_linear(c) for c in _hex_rgb(emission or "#000000")), 1.0)
    bsdf.inputs["Emission Strength"].default_value = emission_strength if emission else 0.0
    bsdf.inputs["Alpha"].default_value = alpha
    mat.diffuse_color = (*lin, alpha)  # viewport / Workbench color
    mat.roughness = roughness
    mat.metallic = metallic
    return mat


def assign(obj, mat, select=None):
    """Add `mat` to obj; with `select(face) -> bool`, assign it only to matching faces (else all faces)."""
    mats = obj.data.materials
    if mat.name not in [m.name for m in mats if m]:
        mats.append(mat)
    idx = [m.name if m else None for m in mats].index(mat.name)
    if select is None:
        obj.data.polygons.foreach_set("material_index", [idx] * len(obj.data.polygons))
    else:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        for f in bm.faces:
            if select(f):
                f.material_index = idx
        bm.to_mesh(obj.data)
        bm.free()
    return obj


def palette_atlas(objs, image_path, name="palette", cell_px=8, keep=()):
    """Collapse the palette materials of `objs` into ONE material: a color atlas (sRGB) plus an ORM atlas
    (G = roughness, B = metallic), sampled with nearest filtering. Each face's UVs collapse to the center of
    its material's cell. Fewer draw calls, and the whole asset shares the art bible's palette texture.

    Materials named in `keep` stay separate (emissive lights that gameplay toggles, transparent glass).
    Run it after the last join() and before export. Writes <image_path> and <image_path>_orm.png.
    Only constant opaque, non-emissive palette materials may be packed. Name emissive/transparent
    materials in `keep`; texture-driven materials need a real bake instead of this palette shortcut.
    Produces TWO textures (color and ORM), not a single texture. Tested with Blender 4.3.2 GLB export.
    """
    image_path = os.fspath(image_path)
    if cell_px < 1:
        raise ValueError("palette_atlas: cell_px must be positive")
    objs = [o for o in objs if o.type == "MESH"]
    used = []
    for o in objs:
        for m in o.data.materials:
            if m and m.name not in keep and m not in used:
                used.append(m)
    if not used:
        raise ValueError("palette_atlas: no materials to pack")
    for m in used:
        bsdf = _bsdf(m)
        emission = bsdf.inputs.get("Emission Color") or bsdf.inputs.get("Emission")
        if (bsdf.inputs["Alpha"].default_value < 1.0 or
                (bsdf.inputs["Emission Strength"].default_value > 0 and any(emission.default_value[:3]))):
            raise ValueError(f"palette_atlas: keep emissive/transparent material {m.name!r} separate")
        if any(s.is_linked for s in (bsdf.inputs["Base Color"], bsdf.inputs["Roughness"],
                                    bsdf.inputs["Metallic"], bsdf.inputs["Alpha"], emission)):
            raise ValueError(f"palette_atlas: {m.name!r} is not a constant palette material; bake it instead")
    n = math.ceil(math.sqrt(len(used)))
    size = 4
    while size < n * cell_px:
        size *= 2
    cells = {m: (i % n, i // n) for i, m in enumerate(used)}
    color = [0.0] * (size * size * 4)
    orm = [0.0] * (size * size * 4)
    for m, (cx, cy) in cells.items():
        if m.get("gs_hex"):
            rgb = _hex_rgb(m["gs_hex"])
        else:
            rgb = [_linear_to_srgb(c) for c in _bsdf(m).inputs["Base Color"].default_value[:3]]
        rough = _bsdf(m).inputs["Roughness"].default_value
        metal = _bsdf(m).inputs["Metallic"].default_value
        for y in range(cy * cell_px, (cy + 1) * cell_px):
            for x in range(cx * cell_px, (cx + 1) * cell_px):
                i = (y * size + x) * 4
                color[i:i + 4] = [*rgb, 1.0]
                orm[i:i + 4] = [1.0, rough, metal, 1.0]
    orm_path = re.sub(r"\.png$", "", image_path, flags=re.I) + "_orm.png"
    images = []
    for img_name, pixels, path, space in ((name, color, image_path, "sRGB"),
                                          (f"{name}_orm", orm, orm_path, "Non-Color")):
        # Names are not ownership. Also preserve owned images subsequently used outside this asset.
        candidates = [im for im in bpy.data.images if im.get("gs_owner") == _owner() and
                      (im.name == img_name or im.get("gs_name") == img_name)]
        img = next((im for im in candidates if not any(mat.node_tree and
            any(node.type == "TEX_IMAGE" and node.image == im for node in mat.node_tree.nodes) and
            (mat.get("gs_owner") != _owner() or any(o.type == "MESH" and o not in objs and
                mat in list(o.data.materials) for o in bpy.data.objects)) for mat in bpy.data.materials)), None)
        if img is None:
            img = bpy.data.images.new(img_name, size, size, alpha=False)
            img["gs_owner"] = _owner()
        img["gs_name"] = img_name
        if tuple(img.size) != (size, size):
            img.scale(size, size)
        img.colorspace_settings.name = space
        img.pixels.foreach_set(pixels)  # byte image: values are stored as given (sRGB for the color atlas)
        img.filepath_raw = path
        img.file_format = "PNG"
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        img.save()
        images.append(img)

    pal = _new_material(name)
    nt = pal.node_tree
    for node in [x for x in nt.nodes if x.type in ("TEX_IMAGE", "SEPARATE_COLOR", "SEPRGB")]:
        nt.nodes.remove(node)
    bsdf = _bsdf(pal)
    tex, tex_orm = nt.nodes.new("ShaderNodeTexImage"), nt.nodes.new("ShaderNodeTexImage")
    tex.image, tex_orm.image = images
    tex.interpolation = tex_orm.interpolation = "Closest"  # glTF NEAREST; inspect minified gameplay views too
    nt.nodes.active = tex  # Workbench texture shading should show color, not the data-only ORM atlas
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex_orm.outputs["Color"], sep.inputs["Color"])
    nt.links.new(sep.outputs["Green"], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs["Blue"], bsdf.inputs["Metallic"])

    # Editing UV/material slots must not alter a linked instance outside this build.
    for o in objs:
        if any(other.type == "MESH" and other not in objs and other.data == o.data for other in bpy.data.objects):
            o.data = o.data.copy()
        me = o.data
        old = list(me.materials)
        new = [pal] + [m for m in dict.fromkeys(old) if m and m not in cells and m != pal]
        remap = {i: (0 if (m in cells or m is None or m == pal) else new.index(m)) for i, m in enumerate(old)}
        bm = bmesh.new()
        bm.from_mesh(me)
        uv = bm.loops.layers.uv.verify()
        for f in bm.faces:
            m = old[f.material_index] if f.material_index < len(old) else None
            if m in cells:
                cx, cy = cells[m]
                u, v = (cx + 0.5) * cell_px / size, (cy + 0.5) * cell_px / size
                for loop in f.loops:
                    loop[uv].uv = (u, v)
            f.material_index = remap.get(f.material_index, 0)
        # Clearing mesh material slots resets polygon indices. Do it BEFORE writing the remapped bmesh,
        # otherwise keep= silently becomes material 0 (and emissive/transparent semantics disappear).
        me.materials.clear()
        for m in new:
            me.materials.append(m)
        bm.to_mesh(me)
        bm.free()
    return pal


# ---------------------------------------------------------------- profiles

def circle(radius, segments=24, center=(0.0, 0.0)):
    return [(center[0] + radius * math.cos(2 * math.pi * i / segments),
             center[1] + radius * math.sin(2 * math.pi * i / segments)) for i in range(segments)]


def rounded_rect(width, height, radius, corner_segments=4, center=(0.0, 0.0)):
    """Closed 2D outline (counter-clockwise) of a rectangle with rounded corners."""
    r = min(radius, width / 2, height / 2)
    cx, cy = center
    pts = []
    corners = [(cx + width / 2 - r, cy + height / 2 - r, 0), (cx - width / 2 + r, cy + height / 2 - r, 90),
               (cx - width / 2 + r, cy - height / 2 + r, 180), (cx + width / 2 - r, cy - height / 2 + r, 270)]
    for x, y, a0 in corners:
        for k in range(corner_segments + 1):
            a = math.radians(a0 + 90 * k / corner_segments)
            pts.append((x + r * math.cos(a), y + r * math.sin(a)))
    return pts


# ---------------------------------------------------------------- shape builders

def loft(name, sections, closed=True, cap_start=True, cap_end=True, smooth=True):
    """Skin consecutive rings of 3D points (same count each) into one surface.

    sections: list of rings, e.g. car-body cross-sections along Y. closed=True joins each ring's last point to
    its first. Caps are n-gons (triangulated on export).
    """
    n = len(sections[0])
    if any(len(s) != n for s in sections):
        raise ValueError("loft: every section needs the same number of points")
    bm = bmesh.new()
    rings = [[bm.verts.new(p) for p in sec] for sec in sections]
    for a, b in zip(rings, rings[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            bm.faces.new((a[i], a[j], b[j], b[i]))
    if closed and cap_start:
        bm.faces.new(list(reversed(rings[0])))
    if closed and cap_end:
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _link(name, bm, smooth)


def revolve(name, profile, segments=32, axis="Z", smooth=True, cap=True):
    """Lathe: rotate a profile [(radius, height), ...] (open polyline) around `axis` ('X', 'Y' or 'Z').

    Points with radius 0 become poles (welded). If the profile does not start/end on the axis and cap=True,
    the open rims are filled.
    """
    def place(r, h, a):
        c, s = r * math.cos(a), r * math.sin(a)
        return {"Z": (c, s, h), "X": (h, c, s), "Y": (s, h, c)}[axis]

    bm = bmesh.new()
    rings = [[bm.verts.new(place(r, h, 2 * math.pi * k / segments)) for r, h in profile] for k in range(segments)]
    m = len(profile)
    for k in range(segments):
        a, b = rings[k], rings[(k + 1) % segments]
        for i in range(m - 1):
            quad = (a[i], b[i], b[i + 1], a[i + 1])
            if len({v.co.to_tuple(6) for v in quad}) >= 3:
                bm.faces.new(quad)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
    if cap:
        edges = [e for e in bm.edges if e.is_boundary]
        if edges:
            bmesh.ops.holes_fill(bm, edges=edges, sides=0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _link(name, bm, smooth)


def _frame(axis):
    """Map 2D profile coords (u, v) and an extrusion distance t onto 3D for the given extrusion axis."""
    return {"X": lambda u, v, t: (t, u, v), "Y": lambda u, v, t: (u, t, v), "Z": lambda u, v, t: (u, v, t)}[axis]


def extrude(name, profile2d, depth, axis="Y", centered=True, smooth=False):
    """Constant cross-section: a closed 2D outline extruded `depth` meters along `axis`.
    Outline coordinates map to (Y, Z) for axis X, (X, Z) for axis Y, (X, Y) for axis Z."""
    f = _frame(axis)
    t0 = -depth / 2 if centered else 0.0
    return loft(name, [[f(u, v, t0) for u, v in profile2d], [f(u, v, t0 + depth) for u, v in profile2d]],
                smooth=smooth)


def sweep(name, path, profile2d, closed_profile=True, smooth=True):
    """Sweep a 2D profile along a 3D polyline (parallel-transport frames, no twisting)."""
    pts = [Vector(p) for p in path]
    tangents = []
    for i in range(len(pts)):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        tangents.append((b - a).normalized())
    up = Vector((0, 0, 1)) if abs(tangents[0].z) < 0.9 else Vector((1, 0, 0))
    normal = tangents[0].cross(up).normalized()
    sections = []
    for i, p in enumerate(pts):
        if i:
            axis = tangents[i - 1].cross(tangents[i])
            if axis.length > 1e-8:
                ang = tangents[i - 1].angle(tangents[i])
                normal = (Matrix.Rotation(ang, 3, axis.normalized()) @ normal).normalized()
        binormal = tangents[i].cross(normal).normalized()
        sections.append([tuple(p + normal * u + binormal * v) for u, v in profile2d])
    return loft(name, sections, closed=closed_profile, smooth=smooth)


def box(name, size=(1.0, 1.0, 1.0), location=(0.0, 0.0, 0.0)):
    """Axis-aligned block (blockout, simple parts). Prefer the profile builders for final forms."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    obj = _link(name, bm)
    obj.location = location
    return obj


# ---------------------------------------------------------------- finishing

def shade_smooth(obj):
    obj.data.polygons.foreach_set("use_smooth", [True] * len(obj.data.polygons))
    return obj


def sharp_by_angle(obj, angle_deg=30.0):
    """Mark edges sharper than `angle_deg` as sharp and smooth the rest (version-proof 'smooth by angle')."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    lim = math.radians(angle_deg)
    for e in bm.edges:
        e.smooth = not (e.is_manifold and e.calc_face_angle(0.0) > lim) and not e.is_boundary
    for f in bm.faces:
        f.smooth = True
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def bevel(obj, width, segments=2, angle_deg=30.0, harden=True, clamp=True):
    """Bevel modifier sized to the part (references/modeling.md §5.3). Add weighted_normals() after it."""
    m = obj.modifiers.new("gs_bevel", "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = "ANGLE"
    m.angle_limit = math.radians(angle_deg)
    m.harden_normals = harden
    m.use_clamp_overlap = clamp
    m.miter_outer = "MITER_ARC"
    if hasattr(obj.data, "use_auto_smooth"):  # Blender < 4.1 needs auto smooth for custom normals
        obj.data.use_auto_smooth = True
    shade_smooth(obj)
    return m


def weighted_normals(obj, keep_sharp=True):
    """Weighted Normal modifier, kept last in the stack: flat faces stay flat, bevels catch the light."""
    m = obj.modifiers.new("gs_weighted_normal", "WEIGHTED_NORMAL")
    m.keep_sharp = keep_sharp
    m.mode = "FACE_AREA"
    if hasattr(obj.data, "use_auto_smooth"):
        obj.data.use_auto_smooth = True
    return m


def _clean_bmesh(bm):
    """Dissolve numerical zero-length edges left by exact booleans/insets, without welding panel gaps.

    This does not fill holes or pretend to repair arbitrary non-manifold input. The 0.1-micron tolerance
    is far below a modeled seam; a QA inspection still owns the final topology verdict.
    """
    bmesh.ops.dissolve_degenerate(bm, edges=list(bm.edges), dist=1e-7)
    bm.normal_update()


def _clean_mesh(obj):
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    _clean_bmesh(bm)
    bm.to_mesh(obj.data)
    bm.free()


def recess(obj, select, inset=0.01, depth=0.005):
    """Inset detail INTO a surface, offsetting each inner vertex along its selected-region normal.

    select(face) -> bool picks faces (e.g. by normal and center position). Use for windows, vents, panels.
    Uses a non-even inset: a bounded border on curved/acute regions is safer than a constant-width miter
    that can shoot cabin corners outside the original silhouette. Split sharply folded or concave panels
    into sensible regions; this is not a general-purpose self-intersection solver.
    """
    if inset < 0 or depth < 0:
        raise ValueError("recess: inset and depth must be nonnegative")
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.normal_update()
    faces = [f for f in bm.faces if select(f)]
    if not faces:
        bm.free()
        raise ValueError(f"recess: selector matched no faces on {obj.name}")
    bmesh.ops.inset_region(bm, faces=faces, thickness=inset, depth=0.0, use_even_offset=False)
    bm.normal_update()
    region = set(faces)
    verts = {v for f in faces for v in f.verts}
    normals = {v: sum((f.normal * f.calc_area() for f in v.link_faces if f in region), Vector()).normalized()
               for v in verts}
    for v in verts:
        v.co -= normals[v] * depth
    _clean_bmesh(bm)
    bm.to_mesh(obj.data)
    bm.free()
    return obj


def apply_modifiers(obj):
    """Bake the modifier stack into the mesh (data API, works headless and live). Keeps materials and
    custom normals, so bevel + weighted_normals survive a later join()."""
    if not obj.modifiers:
        return obj
    _update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(obj.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
    old = obj.data
    obj.modifiers.clear()
    obj.data = me
    if old.users == 0:
        bpy.data.meshes.remove(old)
    me.name = obj.name
    # Bevel can create collapsed corner triangles too. Clean the baked result, not only boolean input;
    # bmesh preserves the remaining corner-normal layer (checked by the geometry regression fixtures).
    _clean_mesh(obj)
    return obj


def cut(obj, cutter, keep_cutter=False):
    """Boolean DIFFERENCE, applied now (wheel wells, door gaps, window openings, sockets).

    Faces created by the cut take the cutter's material, so give the cutter the material the opening's inner
    walls should have (e.g. dark trim inside a wheel well). Cut before bevel() so the new edges get beveled.
    """
    if obj.modifiers:  # applying the cut would also apply these
        raise ValueError(f"cut: {obj.name} already has modifiers {[x.name for x in obj.modifiers]}; "
                         "call cut() before bevel()/weighted_normals()")
    m = obj.modifiers.new("gs_cut", "BOOLEAN")
    m.operation, m.solver, m.object = "DIFFERENCE", "EXACT", cutter
    if hasattr(m, "material_mode"):
        m.material_mode = "TRANSFER"
    apply_modifiers(obj)
    if not keep_cutter:
        delete(cutter)
    return obj


# ---------------------------------------------------------------- transforms and structure

def bounds(obj, world=True, evaluated=True):
    """(min, max) corners of the object's mesh (with modifiers by default), in world space by default."""
    _update()
    mw = obj.matrix_world if world else Matrix.Identity(4)
    if evaluated:
        ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        me = ev.to_mesh()
        pts = [mw @ v.co for v in me.vertices]
        ev.to_mesh_clear()
    else:
        pts = [mw @ v.co for v in obj.data.vertices]
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    return lo, hi


def set_origin(obj, mode="base", point=None):
    """Move the origin without moving the geometry.

    mode: 'base' (bottom center: the asset root, props, characters), 'center' (bounds center: wheels and
    anything that spins), 'point' (a given world point: door hinge, turret ring, lever shaft).
    Call before parenting. Shared mesh data is copied so other linked objects keep their geometry.
    """
    lo, hi = bounds(obj, world=True, evaluated=False)
    if mode == "base":
        target = Vector(((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    elif mode == "center":
        target = (lo + hi) / 2
    elif mode == "point":
        target = Vector(point)
    else:
        raise ValueError(f"set_origin: unknown mode {mode}")
    local = obj.matrix_world.inverted() @ target
    if obj.data.users > 1:
        obj.data = obj.data.copy()  # preserve other linked objects' geometry
    obj.data.transform(Matrix.Translation(-local))
    obj.matrix_world = obj.matrix_world @ Matrix.Translation(local)
    return obj


def apply_rot_scale(obj):
    """Bake rotation and scale into the mesh, keep the location (like Apply > Rotation & Scale)."""
    _update()
    loc = obj.matrix_basis.to_translation()
    rs = obj.matrix_basis.copy()
    rs.translation = Vector((0, 0, 0))
    if obj.data.users > 1:
        obj.data = obj.data.copy()
    obj.data.transform(rs)
    obj.matrix_basis = Matrix.Translation(loc)
    return obj


def parent(child, parent_obj):
    """Parent while keeping the child's world transform."""
    _update()
    mw = child.matrix_world.copy()
    child.parent = parent_obj
    child.matrix_world = mw
    return child


def join(objs, name=None):
    """Merge STATIC parts into the first object (fewer draw calls). Never join parts that move separately.

    Each part's modifiers are applied first, so per-part bevels and weighted normals are kept.
    """
    objs = list(dict.fromkeys(objs))
    if not objs or any(o.type != "MESH" for o in objs):
        raise ValueError("join: provide one or more mesh objects")
    if any(o.get("joint") in JOINTS for o in objs):
        raise ValueError("join: moving parts must stay separate")
    target = objs[0]
    if target.data.users > 1:
        target.data = target.data.copy()
    for o in objs:
        apply_modifiers(o)
    with _preserve_context():
        for o in bpy.context.view_layer.objects:
            o.select_set(o in objs)
        bpy.context.view_layer.objects.active = target
        with bpy.context.temp_override(active_object=target, object=target, selected_objects=objs,
                                       selected_editable_objects=objs):
            bpy.ops.object.join()
    if name:
        target.name = target.data.name = name
    return target


def delete(obj):
    """Remove an object (and its mesh if nothing else uses it)."""
    data = obj.data if obj.type == "MESH" else None
    bpy.data.objects.remove(obj, do_unlink=True)
    if data is not None and data.users == 0:
        bpy.data.meshes.remove(data)


def empty(name, location=(0.0, 0.0, 0.0), parent_obj=None, display="PLAIN_AXES", size=0.25):
    """Empty in the asset's collection: asset root, pivot (steer, turret yaw), or group node."""
    e = bpy.data.objects.new(name, None)
    e["gs_owner"] = _owner()
    e.empty_display_type = display
    e.empty_display_size = size
    _collection().objects.link(e)
    e.location = location
    if parent_obj is not None:
        parent(e, parent_obj)
    return e


def socket(name, location, parent_obj=None, rotation=(0.0, 0.0, 0.0)):
    """Attachment point exported as a glTF node: SOCKET_<name> (muzzle, grip, seat, exhaust, hand_R).
    Game code finds it by name, so keep names stable (and pack with gltfpack -kn)."""
    full = name if name.startswith("SOCKET_") else f"SOCKET_{name}"
    s = empty(full, location, None, "ARROWS", 0.15)
    s.rotation_euler = rotation
    if parent_obj is not None:
        parent(s, parent_obj)
    return s


def set_joint(obj, kind, axis, lo=None, hi=None):
    """Declare how a separate part moves, as custom properties exported to glTF `extras`.

    kind: 'spin' (wheel, fan, rotor; unlimited), 'steer' (front-wheel pivot; lo..hi degrees), 'hinge' (door,
    lid, lever; lo..hi degrees), 'slide' (drawer, bolt, magazine; lo..hi meters). axis: the object's LOCAL
    axis in Blender ('X'|'Y'|'Z'); `axis_gltf` records the same axis after the +Y-up export. The origin must
    already sit on the joint (set_origin). Engine code reads these instead of guessing.
    """
    if kind not in JOINTS:
        raise ValueError(f"set_joint: kind must be one of {JOINTS}")
    if axis not in GLTF_AXIS:
        raise ValueError("set_joint: axis must be 'X', 'Y' or 'Z' (the object's local axis)")
    obj["joint"] = kind
    obj["axis"] = axis
    obj["axis_gltf"] = GLTF_AXIS[axis]
    if lo is not None:
        obj["min"] = float(lo)
    if hi is not None:
        obj["max"] = float(hi)
    obj["units"] = "m" if kind == "slide" else "deg"
    return obj


def collision_box(obj, suffix="-colonly", padding=0.0, min_z=None, include_children=False):
    """Box collision proxy around obj (optionally with its mesh children), named for engine import
    (Godot '-colonly'; use name 'UCX_<obj>' for Unreal). min_z raises the bottom, e.g. to the ground
    clearance of a vehicle whose wheels are raycasts. Hidden in renders; engines must not draw it."""
    objs = [obj] + ([c for c in obj.children_recursive if c.type == "MESH"] if include_children else [])
    los, his = zip(*(bounds(o) for o in objs if o.type == "MESH" and len(o.data.vertices)))
    lo = Vector((min(v.x for v in los), min(v.y for v in los), min(v.z for v in los))) - Vector((padding,) * 3)
    hi = Vector((max(v.x for v in his), max(v.y for v in his), max(v.z for v in his))) + Vector((padding,) * 3)
    if min_z is not None:
        lo.z = max(lo.z, min_z)
    col = box(f"{obj.name}{suffix}", size=tuple(hi - lo), location=tuple((lo + hi) / 2))
    col.display_type = "WIRE"
    col.hide_render = True
    return col


def tire_dims(code):
    """Wheel size in meters from a tire code, e.g. '205/55R16' -> radius 0.316, width 0.205, rim radius 0.203.
    Outer diameter = rim inches * 25.4 mm + 2 * width * aspect% (tire-code formula)."""
    m = re.fullmatch(r"\s*(\d{2,3})\s*/\s*(\d{2,3})\s*[A-Z]*R?\s*(\d{2}(?:\.\d)?)\s*[A-Z]?\s*", code.upper())
    if not m:
        raise ValueError(f"tire_dims: cannot parse {code!r} (expected like 205/55R16)")
    width_mm, aspect, rim_in = float(m.group(1)), float(m.group(2)), float(m.group(3))
    rim_r = rim_in * 25.4 / 2000.0
    return {"radius": rim_r + width_mm * aspect / 100.0 / 1000.0, "width": width_mm / 1000.0, "rim_radius": rim_r}


def wheel(name, radius=0.33, width=0.22, rim_ratio=0.62, spokes=5, segments=32, tire_mat=None, rim_mat=None,
          axis="X"):
    """Game wheel: rounded-shoulder tire + dished rim + spokes, ONE object with its origin at the axle center
    and joint 'spin' about `axis` (X for vehicles whose front faces -Y).

    Keep it a SEPARATE object (parent it to the root or a steer pivot), never joined into the body. For the
    right side, rotate 180 degrees about Z and apply_rot_scale(); never mirror with negative scale.
    """
    r_rim = radius * rim_ratio
    hw = width / 2
    sh = min(radius * 0.18, width * 0.3)  # shoulder radius
    tire_prof = [(r_rim, -hw * 0.92), (radius - sh, -hw)]
    for k in range(1, 5):
        a = math.radians(90 * k / 4)
        tire_prof.append((radius - sh + sh * math.sin(a), -hw + sh - sh * math.cos(a)))
    tire_prof += [(radius, hw - sh)]
    for k in range(1, 5):
        a = math.radians(90 * k / 4)
        tire_prof.append((radius - sh + sh * math.cos(a), hw - sh + sh * math.sin(a)))
    tire_prof += [(r_rim, hw * 0.92)]
    tire = revolve(f"{name}_tire", tire_prof, segments=segments, axis=axis, cap=False)
    # The barrel reaches beyond the tire's +/-0.92hw bead so the rubber seats on metal. Stopping at
    # +/-0.90hw left a real 2.05 mm gap for a 205 mm tire. Overlap the bead into the barrel rather than
    # duplicating its boundary ring, which would create a three-face edge when export seams are welded.
    rim_prof = [(0.0, hw * 0.55), (r_rim * 0.25, hw * 0.6), (r_rim * 0.92, hw * 0.35), (r_rim, hw * 0.94),
                (r_rim, -hw * 0.94), (r_rim * 0.9, -hw * 0.85), (0.0, -hw * 0.6)]
    rim = revolve(f"{name}_rim", rim_prof, segments=segments, axis=axis)
    parts = [tire, rim]
    for k in range(spokes):
        a = 2 * math.pi * k / spokes
        sp = box(f"{name}_spoke{k}", size=(width * 0.18, r_rim * 0.16, r_rim * 0.75))
        sp.data.transform(Matrix.Translation((hw * 0.45, 0, r_rim * 0.5)))
        sp.data.transform(Matrix.Rotation(a, 4, "X"))
        parts.append(sp)
    if tire_mat:
        assign(tire, tire_mat)
    if rim_mat:
        for p in parts[1:]:
            assign(p, rim_mat)
    w = join(parts, name)
    sharp_by_angle(w, 40)
    set_joint(w, "spin", axis)
    return w


# ---------------------------------------------------------------- reference images (live modeling)

def blueprint(path, view, width, center=(0.0, 0.0, 0.0), opacity=0.5):
    """Orthographic reference image as an image empty that shows only in its own axis view (Front/Right/Top
    numpad views in a live session). view: front|back|right|left|top. width: the real-world width in meters
    that the image spans. Place `center` behind the model for that view. Never rendered or exported."""
    rot = {"front": (math.pi / 2, 0, 0), "back": (math.pi / 2, 0, math.pi), "right": (math.pi / 2, 0, math.pi / 2),
           "left": (math.pi / 2, 0, -math.pi / 2), "top": (0, 0, 0)}[view]
    e = empty(f"REF_{view}", center, None, "IMAGE", width)
    e.data = bpy.data.images.load(path, check_existing=True)
    e.rotation_euler = rot
    e.empty_image_side = "FRONT"
    e.show_empty_image_only_axis_aligned = True
    e.use_empty_image_alpha = True
    e.color[3] = opacity
    e.hide_select = True
    e.hide_render = True
    e["gs_reference"] = True
    return e


# ---------------------------------------------------------------- output

def _select_tree(roots):
    keep = set()
    for r in roots:
        keep.add(r)
        keep.update(r.children_recursive)
    keep = {o for o in keep if not o.get("gs_reference")}
    for o in bpy.context.view_layer.objects:
        o.select_set(o in keep)
    return keep


@contextmanager
def _preserve_context():
    """Restore developer selection, active object and mode, including when an operator raises."""
    selected = {o.as_pointer() for o in bpy.context.view_layer.objects if o.select_get()}
    active = bpy.context.view_layer.objects.active
    mode = active.mode if active else "OBJECT"
    if active and mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    try:
        yield
    finally:
        current = bpy.context.view_layer.objects.active
        if current and current.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT")
        for o in bpy.context.view_layer.objects:
            o.select_set(o.as_pointer() in selected)
        try:
            exists = active is not None and bpy.data.objects.get(active.name) == active
        except ReferenceError:
            exists = False
        bpy.context.view_layer.objects.active = active if exists else None
        if exists and mode != "OBJECT":
            bpy.ops.object.mode_set(mode=mode)


def export_glb(path, roots=None, extras=True):
    """Export roots (and their children) as GLB: +Y up, modifiers applied, custom properties (joints) as
    extras. Default roots: the top-level objects of this asset's collection. The selection is restored."""
    roots = roots or [o for o in _collection().all_objects if o.parent is None]
    with _preserve_context():
        _select_tree(roots)
        bpy.ops.export_scene.gltf(filepath=str(path), export_format="GLB", use_selection=True, export_apply=True,
                                  export_yup=True, export_extras=extras)
    return path


def save_blend(path):
    """Save the build as .blend. In a live session it saves a COPY, so the user's open file stays theirs."""
    bpy.ops.wm.save_as_mainfile(filepath=str(path), copy=not bpy.app.background)
    return path
