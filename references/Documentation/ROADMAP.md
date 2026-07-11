# ROADMAP
- [x] Engine: sphere walking, gravity orientation, camera orbit, aim-and-leap
- [x] Six worlds + eight moons, missions, progress dots
- [x] Percy sequence + iris wipe + Garden finale + card
- [x] Audio: music-box loop, birthday melody in garden, footsteps, chimes
- [x] Characters rebuilt to final turnaround sheet (2026-07-07)
- [x] Git LFS configured for future .fbx/.blend/.obj/.glb/.gltf/.png (2026-07-11)
- [x] Real-model pipeline proven: Chippy converted (Blender→Draco glb, 136KB)
      and live in-game on the Book Stacks planet (2026-07-11)
- [x] Real-model rollout, static props: Bred and Percy converted (Blender→Draco
      glb) and standing on the finale couch beside real-model Chippy; couch
      characters stand rather than sit (no rig on these three) (2026-07-11)
- [x] Beanie's *playable* avatar replaced with the rigged Beanie Winter model:
      AnimationMixer crossfading a baked "Idle" action (the rig's manually
      posed relaxed stance, baked into a real 1-frame action since Blender's
      glTF exporter ignores un-keyframed pose values) against "Walk" (the
      rig's native RunFK2 cycle — no Mixamo retargeting needed or attempted).
      Full 12-hop + Percy + Garden + finale regression passes, zero console
      errors (2026-07-11)
- [x] Doll-diorama art pass: PALETTE constants (felt/wool/knit muted colors)
      threaded through every world, planet, moon, and flower; warmer
      low-contrast lighting (no black shadows); grass reshaped from spiky
      cones into rounded "velvet tuft" capsules; tiny warm UnrealBloomPass
      (lanterns/fireflies/stars/prompts only, scene never blown out); belt
      buckle/necklace de-glossed to brushed hardware. Full regression passes,
      zero console errors (2026-07-12)
- [ ] POLISH: RunFK2's arm swing reads as a wide sideways reach rather than a
      natural front-back stride (see KNOWN_BUGS.md) — cosmetic, not blocking
- [ ] POLISH: no sitting/talking animation for Beanie yet — sit(true) holds
      the Idle pose rather than visually sitting (title screen, Percy mount)
- [ ] POLISH (out of scope for a procedural-geometry pass, listed for later):
      true fabric-weave/knit textures, embroidered detail, felt-layered
      mountains, dollhouse-style buildings with knitted curtains — the brief's
      material descriptions beyond color/roughness/shape would need an actual
      texture-authoring pipeline (Blender-painted textures per prop), not
      just code-side material tweaks.
- [ ] POLISH: personal card message from Bred (CONFIG at top of index.html)
- [ ] POLISH: playtest on the actual laptop Beanie will use (trackpad feel)
- [ ] SHIP: birthday build — copy index.html + game-assets/ anywhere, open in
      Chrome/Safari
