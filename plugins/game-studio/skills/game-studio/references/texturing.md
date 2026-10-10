# Texturing: choose a route, prove the export

Texture only after form/part acceptance. Record route, palette/material classes, density, texture budget
and target renderer in the asset brief. The game's material viewer is the acceptance camera/light setup;
Workbench validates form, not PBR appearance.

| Route | Use when | Contract / check |
|---|---|---|
| Constant palette atlas | Opaque, flat-color stylized surfaces | `gb.palette_atlas` packs colors **and ORM** into two images + one material; invoke after export-copy joins. Keep emissive/transparent materials by name in `keep`. Check exported sampler, colors, roughness/metallic and kept faces |
| Vertex colors | Color/AO variation without image textures | Verify `COLOR_0` is consumed by the engine's actual material; do not assume an importer enables it. Show an imported gradient test before committing the route |
| Shared trim sheet | Many related modular/hard-surface surfaces | One strip specification, density and material family; align directional UVs, preserve borders. Assemble adjacent pieces to expose discontinuous grain/scale |
| CC0 PBR maps | Tiling surfaces/realistic reusable materials | Read the actual pack; select compatible resolution and channel convention; tile 3×3 and inspect under neutral + game lighting |
| Procedural high → image low | Authored procedural shading/high detail needs glTF | Bake into UV image targets, then rebuild the export material from those images. Check low mesh in the engine, not only the high-poly source |

## Palette atlas limits

`palette_atlas(objs, png, keep=(material_names, ...))` is a **constant-material** shortcut: each face's UVs
collapse to a cell center. It produces color PNG + `_orm.png` (roughness G, metalness B), with NEAREST
mag / NEAREST_MIPMAP_NEAREST min sampling in the tested export. Inspect distant/minified gameplay views
for mip mixing, particularly if the engine/LOD changes UVs or sampler settings. It is not a
gradient unwrap, detail bake or atlas for texture-driven materials.
Preserve UV detail/normal maps with another route; create separate lightmap UVs if needed. Do not feed
collision meshes to the palette packer. Kept emissive materials may leave more than two materials total;
report the actual count rather than promising a universal count.

## Image/trim/bake checks

1. Inspect a checker preview for stretching and density before expensive texturing; align wood grain,
   brushed metal and trim direction. Preserve deliberate mirrored/stacked UVs; lightmap UVs are different.
2. Base color/emissive are sRGB; roughness/metalness/AO/normal are data. For glTF, packed R=AO,
   G=roughness, B=metalness and tangent-space normals use the glTF convention. Adapt an engine-native
   shader's packing/normal convention explicitly; do not assume the same maps work with every shader.
3. For procedural baking, create a target Image Texture node **active in every material slot**, use the
   final low mesh's UVs, save images and keep the high/bake source. Bake albedo color without direct/
   indirect light; normal/AO/roughness are separate passes. Inspect cage miss/skew/seam defects.
4. Keep lighting separate from albedo. Render generated/scanned texture under opposite light directions;
   a painted dark side that stays fixed requires cleanup/retexturing.
5. If GI needs UV2, use a nonoverlapping padded lightmap unwrap or the engine's generator; verify the
   imported channel and bake. Never reuse collapsed palette UVs/stacked trim UVs as a lightmap unwrap.
6. Validate the uncompressed GLB, then load the final compressed asset in the actual engine. Compare
   material classes, palette and seams at gameplay distance; alpha, emissive or normal data must survive.

**Evidence:** checker shot where applicable; map/channel inventory; exported material/texture counts;
same fixed asset-viewer shots before/after. The inspector's density estimate does not prove absence of
stretching, bake defects or acceptable lighting.

Basis: round-2 reports 02/06 and [Poly Haven's Simple Prop Workflow](https://blog.polyhaven.com/simple-prop-workflow/)
(written article read in the media follow-up). glTF conventions derive from the
[Khronos specification](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html). `gs_build.py` is the source
for the atlas contract; its export is tested separately. This text is original; no third-party art assets bundled.
