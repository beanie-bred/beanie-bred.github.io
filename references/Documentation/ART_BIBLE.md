# ART BIBLE

## Style
Handcrafted felt/wool/knit storybook diorama — Animal Crossing × The Little
Prince × Scandinavian children's books (2026-07-12 direction, matches the
doll-like character models). Not realism, not Pixar-glossy, not anime.
Rounded, soft-shadowed, readable silhouettes, warm bounce light everywhere.
Nothing metallic/plastic/glossy/industrial — see PALETTE and Lighting below.

## Palette & Lighting (index.html, top of the module script)
`PALETTE` is the single source of truth for color — every world pulls its
base colors from it rather than inlining hex values, so the whole diorama
stays cohesive. Named colors: cream, warmWhite, lightBeige, softBrown,
walnut, warmGray, sageGreen, moss, mutedPine, dustyBlue, skyBlue,
mutedLavender, softPink, warmPeach, mutedMustard, nightNavy (space
background — deep navy, never pure black), lampAmber (warm glow for
lanterns/fireflies/sparkles/prompts).
- Hemisphere light: warmWhite sky / lightBeige ground bounce, intensity 1.55
  (1.85 in the Garden) — the ground-bounce color is warm, not cold/purple, so
  undersides of objects never go dark or blue-tinted.
- Directional "sun": warmPeach, low intensity (1.05 baseline, 1.25 in the
  Garden for golden-hour) — deliberately low-contrast, no hard key light.
- Tiny warm bloom: `composer`/`bloomPass` (UnrealBloomPass, threshold 0.82,
  strength 0.35) — high threshold so only genuinely emissive things (star
  gates, fireflies, lanterns, the SPACE-prompt glow) soften-bloom; the
  diorama itself should never look blown out. All rendering goes through
  `renderScene()`, not `renderer.render()` directly — new render call sites
  must use `renderScene()` or bloom won't apply to them.
- Grass: `grassField()` uses a squat rounded CapsuleGeometry ("velvet tuft"),
  not a spiky cone — reads like short brushed fleece. Any new grass-like
  surface should reuse this shape, not reintroduce ConeGeometry blades.
- Small metal accents (Bred's belt buckle, the necklace pendant) are
  deliberately low metalness (0.25–0.3) + raised roughness (0.55–0.6) —
  "brushed hardware", never chrome/glossy.

## Characters (source of truth: turnaround sheet in character designs/)
Proportions: feet y=0, head top ≈2.1, head ≈46% of height, long legs, thin arms
hanging nearly straight. Skeleton (makeChibi): hip pivot y0.62, shoulder y1.2,
head center y1.6 (r0.5, scale 1.06/0.98/1.0).
- Beanie: skin 0xfcd9be; near-black hair 0x241a14 — center part, hairline band,
  front locks to waist (sway groups), wavy back mass; thin brows; big brown eyes
  0x3a2014 with 2 glints; round blush 0xf5a2ac (hers only); orange nose 0xe8794a;
  coral cardigan 0xf0917c + 3 buttons + gold necklace; denim skirt 0x27334f;
  white socks; chunky white sneakers.
- Bred: skin 0xf8c9a2; hair 0x33251a feathery fringe + top tufts; THICK brows;
  closed happy eyes ∩; small smile; no blush; black tee 0x232329; brown belt
  0x6a4426 + silver buckle; black baggy jeans 0x17171c; brown loafers 0x5c3a24;
  crossbody strap + hip pouch + brown puppy charm (purple bow, white tag).

## Hard-won rules
- Face features must sit proud of the head ellipsoid: z ≥ 0.44 with the r0.5
  head, or they vanish inside the skin. Verify per-feature when moving them.
- Hair shells must keep front extent < 0.42 at feature heights.
- Both characters cast a blob shadow (dotTex-mapped plane, opacity 0.32).

## Creatures
Jellycat-plush pigeons (Percy: teal head, purple ring, wing stripes), Chippy
(cream bean + tweed flat cap + corduroy legs), pastel whales/fish/seahorses.
(Procedural versions above; Chippy now also has a real-model replacement —
see "Real 3D models" below.)

## Real 3D models (Blender/Rodin.ai pipeline)
Source assets live at the repo root: `chippy/`, `percy/`, `bred T/`,
`beanie spring T/`, `beanie winter T/` — each a Rodin.ai base mesh
(`base.obj`, no material link, UV-mapped) refined in Blender with a full PBR
texture set (`texture_diffuse/normal/roughness/metallic.png`, 2K–4K). Beanie
Winter is further along: it has a rigged `.blend` and 13 Mixamo-retargeted
animation clips in `movements/` (Idle, Start Walking, Running Jump, Sitting,
Waving, Kiss-guy/girl, etc.). Bred, Percy, Chippy, Beanie Spring are static
(unrigged) meshes.

**Status: Chippy converted and live in-game (2026-07-11).** Proven pipeline,
repeat for the rest:
1. Headless Blender import (`bpy.ops.wm.obj_import`), no GUI needed.
2. Bake a uniform scale into the mesh (`transform_apply`) so the exported
   glb is already in final game units — avoid extra `.scale` juggling in
   Three.js. Target heights follow the procedural originals (Chippy: 0.75).
3. Build a minimal Principled BSDF material: diffuse texture resized to
   512px (`image.scale`), flat roughness/metallic (skip normal/roughness/
   metallic maps for small background props — not worth the weight).
4. Export GLB with `export_draco_mesh_compression_enable=True` (level 6) and
   `export_image_format='JPEG'`. Chippy: 1078KB → **136KB**.
5. Output goes to `game-assets/<character>/<character>.glb` (gitignored from
   the huge source folders' size, tiny enough to commit directly).
6. In-game: `GLTFLoader` + `DRACOLoader` (added to the import map as
   `three/addons/`), loaded async into a placeholder `THREE.Group()` so
   world-building never blocks on the network. `chippy.rotateY(2.4)` tunes
   the model's raw front to face the landing spot — **re-tune per character**,
   Rodin exports have no consistent forward convention.
7. Verify with a debug camera, not the normal follow-cam — on a small
   planet, most placed objects are below the player's local horizon from
   their landing spot. Use `__world.framePoint(x,y,z, planetCenter, dist)`
   (planetCenter matters — planets are NOT at the world origin) and
   `__world.freeze(true)` to stop the render loop from clobbering the shot
   before an external screenshot tool captures it.

Script templates for this pipeline: `/tmp/chippy_pipeline/*.py` (session-local
scratch, not in the repo — recreate from this doc if needed).

## Real-model risks / open decisions
- Bred, Percy, Beanie Spring have no rig — fine for static props (Bred/Percy
  sitting on the finale couch), not usable as a walking/animated avatar
  as-is.
- Beanie Winter IS rigged with Mixamo animations ready, but swapping her in
  as the **playable** avatar is a much bigger job than a static prop: needs
  AnimationMixer wiring, blending Idle/Walk/Jump clips against the existing
  sphere-walk state machine, and re-verifying the whole aim-and-leap flow
  with a skinned mesh. Do NOT start this without a checkpoint — confirm
  scope with Justin first (see ROADMAP.md).
- Git LFS is configured (`.gitattributes` at repo root) for future
  `.fbx/.blend/.obj/.glb/.gltf/.png` — existing history (319MB, no LFS)
  was intentionally left alone; do not run `git lfs migrate` or rewrite
  history without explicit sign-off (repo has a pushed remote).

## Lighting
Hemisphere 0xe8eeff/0x8a7a9e @1.45, sun 0xfff6e8 @1.4, camera fill point light,
ACES tone mapping exposure 1.14. Garden bumps hemi 1.7 / sun 1.7.
