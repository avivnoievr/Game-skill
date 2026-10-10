# Audio: an event contract and a listening gate

Load when the game gains audible events. Define sound language with the art direction, then map
events to assets. An audio folder or successful playback API call is not evidence that the mix works.

| Requirement | Deliverable / proof |
|---|---|
| Event coverage | Table: gameplay event → sound ID → variants → bus → positional/2D → max voices → priority → cooldown; include silence where intentional |
| Repetition | Small pool for frequent footsteps/impacts; choose variants deterministically in QA. Pitch variation is a tuned range, not a substitute for different recordings |
| Routing/settings | Master/music/SFX/UI buses or equivalent; persisted controls and mute. World sounds positional, interface sounds 2D unless design calls for another route |
| Simultaneous events | Voice limits/stealing policy, loop start/stop ownership, listener placement; pause/scene-exit stops owned playback without cutting unrelated music |
| Source rights | Asset file + author/source URL + exact license/attribution in `assets/LICENSES.md`; inspect the pack's license, not a site's default |
| Web start | Unlock/resume the AudioContext from an actual user gesture. Boot/pause/resume evidence covers a fresh browser, not only an already-unlocked session |

**Sourcing order:** user/CC0 pack → licensed material or locally synthesized effect → approved paid
service only if it serves the event. Filter Freesound by the required license; BY needs attribution,
BY-NC cannot silently enter a commercial project. Speech, SFX and music endpoints are distinct: inspect
the available tool before requesting output. Service plan/commercial rights need current verification.

**Acceptance:** play a short critical-path recording with audio enabled: footsteps/material changes,
impact/event feedback, repeated events, positional near/far, pause/resume and retry. Check clipping,
loop seams, event timing, missing/doubled triggers, voice-count bounds and settings persistence. Meter
peaks/voice counts where possible and have the user listen to the final mix. A model inspecting a
waveform cannot certify artistic quality or hearing comfort.

Headless runs with a Dummy audio driver, screenshots or mute prove no audible result. If the environment
cannot record/play real sound, state **audio not listened to** and retain that acceptance gap. Avoid
arbitrary universal loudness targets; record the project's mix/headroom decisions and test the target device.

Basis: original event/QA contract synthesized from round-2 reports 02 and 06. Playback classes depend on
the chosen engine; use its installed API. No paid generation, third-party sound or vendor terms are bundled.
