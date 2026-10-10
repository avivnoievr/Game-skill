# Round-2 implementation plan (director's working file)

Order: code -> test on car -> docs -> vendor design skills -> pilot + review (parallel) -> fixes -> validate -> push.

## Code
1. gs_build.py: begin(asset) (live-safe: own collection GS_<asset>; factory reset only when bpy.app.background),
   set_joint(), socket(), tire_dims(), reference_image(), palette_atlas(), export_glb(extras=True). DONE so far:
   cut(), apply_modifiers(), delete(), _update() fixes (stale matrix_world bug).
2. gs_common.py: is_collision(); mesh_objects() excludes collision proxies; collision_objects().
3. inspect_model.py: collision proxies reported separately (not in budgets); --parts GLOBS, --part-pivot,
   --sockets; joint extras auto-detected; floating check per rigid group; hierarchy print.
4. render_views.py: hide collision; diagonal scale-ref; "parts" view (exploded, flat color per part).
5. find_blender.sh: locate local Blender (PATH, macOS app, Windows Program Files/Steam via Git Bash, Linux).
6. examples/car_stylized.py: tire_dims, steer pivots, joints, sockets, palette option; recipe reference.
7. templates/build.py skeleton; templates/gitattributes.

## Docs
- references/blender-live.md (report 03): install (official Blender Lab >=5.1 default; ahujasid <=5.0), Claude Code
  registration, preflight, build loop, validation outside, retries, never-do.
- references/tool-matrix.md (report 02 §2.1 + never list) ; AI-3D decision rule into modeling.md §8.
- references/recipes/{vehicle,articulated,modular-kit,character,environment}.md (reports 04, 06 §3D).
- references/texturing.md (palette atlas, trim, Poly Haven PBR, bake, UV2) ; audio.md ; level-design.md.
- modeling.md: fix "join by material" -> within one rigid part; §5.6 parts that move; gs_build rule; AI rules.
- SKILL.md: preflight, never-do top list, design-sense load table, reference map.
- agents: asset-builder (gs_build, live MCP one-at-a-time, parts checks), art-critic (parts view, scorecard).
- toolchain.md: scripts table, MCP -> blender-live.md, fix safe-mode contradiction.
- vendor/: threejs-aaa-graphics-builder, threejs-game-ui-designer, frontend-design, game-feel.md, game-ui-ux
  (+ LICENSE/NOTICE, UPSTREAM-SKILL.md rename, THIRD_PARTY_NOTICES.md with SHAs). Read every file first.
- docs: SUMMARY.he.md, README, PROMPT, CREDITS, docs/research/round2/.

## Verify
- car example: inspect PASS with --parts, renders looked at; palette variant.
- pilot agent builds a different vehicle from the skill text only; independent review agent.
- plugin validate --strict, quick_validate, link checker; commit + push.
