# three.js / React Three Fiber specifics

Contents: 1. Renderer setup · 2. Lighting recipe · 3. Assets and disposal · 4. QA hook (with silhouette and
post-off shots) · 5. Animation · 6. Traps

Check the installed version first (`node -p "require('three/package.json').version"`), then read the
matching source in `node_modules/three` for anything version-sensitive. The values below target r16x–r18x.

## 1. Renderer setup

```ts
import * as THREE from 'three';
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));    // cap: post cost scales with pixels
renderer.setSize(innerWidth, innerHeight);
renderer.toneMapping = THREE.NeutralToneMapping;   // palette-driven stylized; AgXToneMapping for realistic
renderer.toneMappingExposure = 1.0;                // tune on active gameplay
renderer.shadowMap.enabled = true;
// outputColorSpace is SRGBColorSpace by default; color textures: tex.colorSpace = THREE.SRGBColorSpace
```

With post-processing, the composer ends with `OutputPass`, which applies tone mapping and color space
once. Never apply them twice.
```ts
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
composer.addPass(new UnrealBloomPass(new THREE.Vector2(innerWidth, innerHeight), 0.45, 0.3, 0.85)); // strength, radius, threshold
composer.addPass(new OutputPass());
```

## 2. Lighting recipe (starting values; put the final ones in the art bible)

```ts
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;   // IBL: metals/gloss need it
scene.environmentIntensity = 0.8;                 // or an HDRI from Poly Haven via RGBELoader/HDRLoader + PMREM

const sky = new THREE.HemisphereLight(0xbfd8ff /* cool sky */, 0x8a6a48 /* warm ground */, 1.6);
const sun = new THREE.DirectionalLight(0xffe8cc /* warm key */, 2.8);
sun.position.set(8, 14, 6);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
Object.assign(sun.shadow.camera, { left: -15, right: 15, top: 15, bottom: -15, near: 1, far: 50 }); // fit tightly
sun.shadow.normalBias = 0.02;                     // prefer normal bias against acne / peter-panning
scene.add(sky, sun, sun.target);
scene.fog = new THREE.Fog(0xa9c2d8, 25, 90);      // fog tinted toward the sky color (aerial perspective)
```

**Contact shadow for props that don't cast real shadows:**
```ts
function blobShadow(radius: number) {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d')!; const grad = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  grad.addColorStop(0, 'rgba(0,0,0,0.45)'); grad.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = grad; g.fillRect(0, 0, 64, 64);
  const m = new THREE.Mesh(new THREE.PlaneGeometry(radius * 2, radius * 2),
    new THREE.MeshBasicMaterial({ map: new THREE.CanvasTexture(c), transparent: true, depthWrite: false }));
  m.rotation.x = -Math.PI / 2; m.position.y = 0.01; return m;   // fade opacity with the object's height
}
```

## 3. Assets and disposal

```ts
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { KTX2Loader } from 'three/addons/loaders/KTX2Loader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';
const ktx2 = new KTX2Loader().setTranscoderPath('/basis/').detectSupport(renderer); // copy three/examples/jsm/libs/basis
const gltfLoader = new GLTFLoader().setKTX2Loader(ktx2).setMeshoptDecoder(MeshoptDecoder);
```

- All loads go through the asset manifest and registry (`architecture.md` §4). A failed load throws in
  QA mode.
- **Dispose explicitly.** Removing an object from the scene frees nothing on the GPU.
```ts
function disposeObject(root: THREE.Object3D) {
  root.traverse((o: any) => {
    o.geometry?.dispose();
    const mats: any[] = Array.isArray(o.material) ? o.material : o.material ? [o.material] : [];
    for (const m of mats) {
      for (const v of Object.values(m)) if (v instanceof THREE.Texture) v.dispose();
      m.dispose();
    }
    o.skeleton?.dispose?.();
  });
}
```
Render targets need `.dispose()`; `ImageBitmap` textures need `.close()` on the source.

## 4. QA hook (dev builds or `?qa=1` only)

```ts
// src/debug/qa.ts
const GAMEPLAY_LAYER = 1;   // gameplay roles also live on layer 1 (layers are per object, not inherited):
                            // player.traverse((o) => o.layers.enable(GAMEPLAY_LAYER))
export function installQa(game: Game) {
  if (!import.meta.env.DEV && !location.search.includes('qa=1')) return;
  const black = new THREE.MeshBasicMaterial({ color: 0x000000 });
  const render = (post = true) => (post ? game.composer.render() : game.renderer.render(game.scene, game.camera));
  const silhouette = () => {                          // gameplay roles as black shapes on white
    const { scene, camera } = game; const bg = scene.background, fog = scene.fog;
    scene.background = new THREE.Color(0xffffff); scene.fog = null; scene.overrideMaterial = black;
    camera.layers.set(GAMEPLAY_LAYER); game.renderer.render(scene, camera);
    camera.layers.enableAll(); scene.overrideMaterial = null; scene.background = bg; scene.fog = fog;
  };
  (window as any).__QA__ = {
    ready: false,
    stats: () => { const i = game.renderer.info;
      return { drawCalls: i.render.calls, triangles: i.render.triangles, geometries: i.memory.geometries,
               textures: i.memory.textures, programs: i.programs?.length ?? 0 }; },
    state: () => game.sim.snapshot(),
    shots: {
      gameplay:            async () => { game.cameraRig.apply('gameplay'); render(); },
      gameplay_postoff:    async () => { game.cameraRig.apply('gameplay'); render(false); },
      gameplay_silhouette: async () => { game.cameraRig.apply('gameplay'); silhouette(); },
      wide:                async () => { game.cameraRig.apply('wide'); render(); },
      hero:                async () => { game.cameraRig.apply('hero'); render(); },
    },
    advance: async (ms: number) => { game.stepFixed(ms / 1000); render(); },
    reload: async () => { await game.reloadMainScene(); render(); },   // leak test: --reloads 5
  };
  // QA mode runs no animation loop, so render the first frame explicitly, then mark ready.
  // Call installQa(game) after the boot asset group has loaded.
  render(); (window as any).__QA__.ready = true;
}
```
- In QA mode, don't run `setAnimationLoop`. The harness drives `advance`.
- If the game needs `preserveDrawingBuffer` for canvas reads, enable it only in QA mode.
- With an EffectComposer, set `renderer.info.autoReset = false` and call `renderer.info.reset()` at the
  start of each frame, so the counts cover all passes.

Run it: `node "$SKILL_DIR/scripts/web/capture.mjs" --require-qa --url "http://localhost:5173/?qa=1&seed=1" --out qa/out/m1 --budgets design/budgets.json --reloads 5 --sequence 8 --hold KeyW`

## 5. Animation

```ts
const mixer = new THREE.AnimationMixer(model);
const actions = Object.fromEntries(gltf.animations.map((c) => [c.name, mixer.clipAction(c)]));
const timer = new THREE.Timer();   // Clock is deprecated since r183; older: import { Timer } from 'three/addons/misc/Timer.js'
renderer.setAnimationLoop((t) => { timer.update(t); const dt = timer.getDelta(); /* fixed-step sim */ mixer.update(dt); });
```
- Crossfades and additive layers: `animation.md` §6.
- Deterministic capture of a clip: `mixer.setTime(k / fps)` per frame, then render.
- `SkinnedMesh` bounding volumes don't follow the animation. Set `frustumCulled = false` on skinned
  meshes that pop out of view, or compute bounds from the skeleton.

## 6. Traps

- Two render loops (a `requestAnimationFrame` plus `setAnimationLoop`, or the R3F loop plus your own)
  update twice and cost double.
- Tone mapping or sRGB conversion applied twice (`OutputPass` plus a manual conversion) gives washed-out
  or overly dark colors.
- Textures without `colorSpace = SRGBColorSpace` on color maps look washed out. Setting it on data maps
  breaks the lighting.
- Old tutorial light intensities are too dark under physical lighting. Start from §2.
- `MeshStandardMaterial` metals without `scene.environment` render black.
- Shadow acne or peter-panning: fit the shadow camera tightly and use `normalBias`, not a large `bias`.
- Per-frame allocations (`new Vector3()` in update loops) cause GC stutter. Reuse temporaries.
- Transparent objects sorting wrongly: use `depthWrite: false` for soft effects, and order them by
  `renderOrder` deliberately.
- R3F: never `setState` in `useFrame`. Mutate refs instead.
