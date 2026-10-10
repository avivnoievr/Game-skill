# Character from a rigged pack: preserve the rig, prove motion

Prefer one coherent pack family when it meets the art bible. Verify the exact download's license,
mesh/rig/clip contents and engine compatibility. Do not assume every file from a familiar creator is
CC0 or animated. If login/browser access is needed, give the user the exact download and destination.

**Import contract:** source URL/license, desired character height/orientation, target skeleton,
required gameplay clip names/durations, root-motion policy, hand/weapon sockets, skin/texture budgets.
Save the original under `assets/_vendor/<pack>/`; customize/export a working copy.

1. Inventory mesh/armature/actions and run inspector/clip report. Compare the **exported** clip list
   with required states; a pack's store description is not an import test.
2. Normalize scale/orientation consistently with the rig, not one mesh independently. Check bind/rest
   pose and imported bone axes before retargeting. Similar bone names alone do not prove compatibility.
3. Recolor the existing atlas/material family without rebuilding topology or destroying UVs; confirm
   palette/roughness under the game lighting. Preserve skin attributes through optimization.
4. Map locomotion speed/root motion to simulation; test idle/start/stop/turn/jump/action transitions.
   Validate contacts, joint deformation, foot sliding, loop seams and attachments in motion.
5. Reuse approved rig revision. If retargeting is necessary, document source→target mapping and prove
   poses/contacts on the final target; do not silently combine incompatible skeletons/clip policies.

**Gate:** source rights, inspector JSON, exported clip inventory, representative pose sheet **and**
unpaused engine sequence at gameplay camera. Physics/controller scale and weapon socket offsets are
checked in the game. A numeric clip PASS or attractive bind-pose render is not character acceptance.

For a unique hero beyond the pack, planned human-quality topology/rig work or approved generation plus
retopology is a distinct scope. Code-only faces/hands remain placeholders. Automatic weights/remesh
are intermediate results until deformation evidence passes; Mixamo interaction stays user-driven.

Basis: original synthesis of round-2 reports 02/06 and existing [animation rules](../animation.md).
No third-party character, rig, download terms or animation files are bundled.
