# Unity specifics

Contents: 1. Project setup · 2. Lighting and post recipe (URP) · 3. Importing assets · 4. QA: tests, captures,
metrics · 5. Animation · 6. Traps

Unity was not available in the environment where this skill was built and tested. The settings below
are standard Unity practice, but treat the C# snippets as starting points and verify them in the
project. For Unity projects, also install Unity's official agent plugin (`toolchain.md`).

## 1. Project setup

- **URP** suits most indie 3D games. Use HDRP only for high-end PC/console realism.
- **Color space: Linear** (Project Settings → Player → Other Settings). PBR lighting is wrong in Gamma.
- Folder layout and assembly definitions: `architecture.md` §6.

## 2. Lighting and post recipe (URP)

| Element | Starting point |
|---|---|
| Sun | One Directional Light, warm color, realtime or mixed. Shadows with Normal Bias tuned before Depth Bias; shadow distance as low as the scene allows |
| Sky and ambient | Skybox from an HDRI (Poly Haven); Environment Lighting source = Skybox |
| Reflections | **Reflection Probes** in every area with metal or gloss (without them, metals look dead). Light Probes for dynamic objects when lighting is baked |
| Global Volume | **Tonemapping:** Neutral for palette-driven stylized looks, ACES for cinematic. **Bloom:** threshold ~1, low intensity, emissives only. **Color Adjustments / White Balance** for the grade. Subtle Vignette |
| SSAO | URP Screen Space Ambient Occlusion renderer feature, conservative intensity |
| Static scenes | Bake lightmaps (Mixed lighting). This is the biggest single lighting upgrade for static environments |

## 3. Importing assets

- FBX from Blender: set Apply Transform / "Bake Axis Conversion" so objects arrive with identity
  rotation and scale 1.
- glTF: use Unity's glTFast package.
- Characters meant for retargeting use the **Humanoid** rig type. Check the avatar mapping, and
  verify muscle limits on extreme poses.
- Texture import: sRGB on for color maps, **off** for normal, mask and roughness maps. Normal maps are
  set to type "Normal map".
- Prefab per asset, with collider proxies (simple colliders) instead of mesh colliders on moving
  objects.

## 4. QA: tests, captures, metrics

```bash
Unity -batchmode -projectPath . -runTests -testPlatform EditMode -testResults qa/out/editmode.xml
Unity -batchmode -projectPath . -runTests -testPlatform PlayMode -testResults qa/out/playmode.xml
```

Screenshots from a fixed camera in a PlayMode test or editor script:
```csharp
public static class QaCapture {
    public static void Capture(Camera cam, string path, int w = 1280, int h = 720) {
        var rt = new RenderTexture(w, h, 24);
        var prev = cam.targetTexture;
        cam.targetTexture = rt; cam.Render();
        RenderTexture.active = rt;
        var tex = new Texture2D(w, h, TextureFormat.RGB24, false);
        tex.ReadPixels(new Rect(0, 0, w, h), 0, 0); tex.Apply();
        System.IO.File.WriteAllBytes(path, tex.EncodeToPNG());
        cam.targetTexture = prev; RenderTexture.active = null;
        Object.DestroyImmediate(rt); Object.DestroyImmediate(tex);
    }
}
```

- In Play Mode, `ScreenCapture.CaptureScreenshot(path)` is the simplest alternative.
- Run `image_metrics.py <shots> --gray` on the PNGs for image metrics and grayscale copies.
- Running with `-nographics` disables rendering, so captures need a graphics device.
- On a desktop, CoplayDev unity-mcp or Unity's MCP can take editor screenshots.

Metrics, read in a QA script:
- `ProfilerRecorder.StartNew(ProfilerCategory.Render, "Draw Calls Count")`, and similarly
  `"Triangles Count"` and `"SetPass Calls Count"`.
- Use the Frame Debugger to find why a draw call isn't batched.

## 5. Animation

- Animator Controller with blend trees for locomotion, keyed by speed (`animation.md` §5).
- Keep action transitions short. The default 0.25 s is long for attacks.
- Disable **Has Exit Time** on interruptible transitions.
- Use Animation Events for footsteps and hit frames.
- Animation Rigging package: Two Bone IK for foot locking, Multi-Aim for look-at.
- Hitstop: `Time.timeScale` near 0 with `WaitForSecondsRealtime` for the timer. Use unscaled time for
  UI and camera feedback.

## 6. Traps

- Gamma color space makes all PBR tuning wrong.
- Metals without reflection probes render flat or dark.
- Data textures imported as sRGB break the shading.
- A mesh collider on everything costs performance. Use primitive colliders on dynamic objects.
- `Update` vs `FixedUpdate`: physics forces belong in `FixedUpdate`. Movement in `Update` must use
  `Time.deltaTime`.
- Scene and prefab files are YAML, but editing them by hand is fragile. Change them through the editor
  or an MCP whenever possible, and keep scripts as the source of truth for behavior.
