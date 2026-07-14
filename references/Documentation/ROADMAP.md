# ROADMAP
- [x] Ring made wider + flatter (2026-07-14 follow-up): solid mystery-ring
      torus tube radius 6.6→9.5 with scale.y=0.3 (flattens the round tube
      into a wide flat band instead of a chunky donut); revealed cucumber
      ring band 9.6/7.2→14/10.5 (wider) with thick 4.4/3.2→2.2/1.6 (flatter).
      Verified both the solid pre-reveal ring and the post-reveal cucumber
      band read as a wide, flat, halo-like arc from in-game camera angles;
      full reveal-cutscene re-run, zero console errors.
- [x] Big polish batch (2026-07-14), full details in STORYLINE.md:
      - Cucumber ring 4x thicker / 3x wider band, now a REAL reveal mechanic:
        world starts as "🌱 Emerald Meadow" showing only a solid green ring
        (individual cucumbers + ground cucumbers all hidden); after bbak's
        4th-rejection hint, a scripted ~7s cutscene (new 'cukeReveal' state)
        pulls the camera back, winds the solid ring's spin to a stop, hard-
        swaps to the real cucumber ring + ground cucumbers with a sparkle
        burst, then renames to "🥒 Cucumber Meadow" and plays its title card.
      - Mission banner moved from top to bottom (was coinciding with the
        guide/interaction chips); auto-hides during dialogue too now (the
        box can grow tall enough to reach it otherwise).
      - ensureTalkDistance(): any dialogue with an npcPos now nudges Beanie
        backward along the sphere surface first if she was standing closer
        than 4 units, so the two-shot camera never frames her literally
        overlapping the NPC regardless of how close SPACE was pressed.
      - Planet titles: bumped clamp to fill more width (64-240px), text-
        shadow cut way down to a subtle dark glow (was a big warm blur),
        removed the gold rule lines above/below entirely.
      - Book Stacks renamed to **Main Stacks** (lore: the library Bred and
        Beanie used to study in).
      - Chicago: CHICAGO_START_N now literally IS the tower-adjacent seat
        position (was an unrelated arbitraryPerp direction) — one constant
        drives the intro sit pose, the gameplay start position, AND the
        post-letter title cutscene, so all three share the same "tower
        right beside her" vantage with zero pop on transition. Intro's idle
        camera rewritten from a fixed world-space XZ dolly to the same
        local-tangent-plane orbit the arrival cutscenes use. Lowered the
        landing-orbit distance/height floor (18/7 → 10/4) so a tiny world
        like Chicago keeps a close, tower-dominant frame instead of pulling
        back so far the landmark loses prominence (only Chicago is small
        enough to hit this floor — verified other worlds' radii are all
        well above it, so their cutscenes are unaffected).
      - New STORYLINE.md: the authoritative current narrative doc across
        every world (GAME_BIBLE.md's old "Story flow" section flagged stale
        and pointed at it instead of silently contradicting it).
      Full regression (Chicago letter+cutscene → Main Stacks → Cucumber
      reveal cutscene → Pigeon Plaza → zero console errors throughout) all
      independently verified.
- [x] Planet-title cinematic overhaul (2026-07-14): dropped the emoji from the
      big title (plain world name only), forced single-line with
      white-space:nowrap + a JS shrink-to-fit pass (fitPlanetTitleOneLine —
      measures scrollWidth, steps font-size down until it fits, since
      different per-world fonts have very different average glyph widths),
      and replaced the warm peach text-shadow with a pure dark glow
      (rgba(0,0,0,...) only) so the white letters read as naturally
      prominent against the navy sky instead of glowing amber. Added one
      distinct Google Font per world via showPlanetTitle(b)/WORLD_FONT_CLASS:
      Chicago=Oswald (condensed sans), Book Stacks=Playfair Display (serif),
      Cucumber Meadow=Baloo 2 (rounded/cute), Pigeon Plaza=Bungee (blocky
      playful), Garden=Cormorant Garamond (delicate serif). Each font's own
      letter-spacing survives the reveal animation via a --tls CSS custom
      property (previously the keyframe's hardcoded final letter-spacing
      clobbered any per-font override). Also gave the Garden its own title
      moment via a new non-blocking flashPlanetTitleAuto() (shows + auto-
      fades after 3.2s, no click-to-continue gate, since the Percy-flight+
      iris entrance shouldn't pause on a click). Verified all 5 fonts/text
      render correctly via real jump-landings + the Percy/Doodles quest,
      zero console errors.
- [x] Chicago now gets the same orbit+title cutscene every other world gets,
      just timed to fire AFTER the messenger's letter dialogue finishes
      (startChicagoTitleCutscene(), reuses the existing landing/orbit/
      click-to-continue machinery with phase:'orbit' — skips the fall/get-up
      beat since she's already standing normally). Verified: letter dialogue
      -> "CHICAGO" title (Oswald, dark glow, one line) -> click to continue
      -> normal mission/gameplay, zero console errors.
- [x] HUD polish (2026-07-14): #planetTitle cinematic card (big "BOOK STACKS"-
      style reveal) was vertically centered, so on small planets it sat right
      on top of Beanie standing there — moved to justify-content:flex-start +
      padding-top:14vh so she's clearly visible below it. Also removed the
      arrival showToast(name, tag) call in arrive() — the planetTitle card
      already announces the world by name, and the toast chip (top:76px) sat
      directly on top of the mission banner/guide chip. Verified via a real
      jumpChain() landing (fall/get-up/orbit/title/click-to-continue), zero
      console errors.
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
- [x] Trackpad/wheel camera-look locked to stopped-only: while Beanie is
      actively walking, drag/wheel input on the camera is ignored (arrow-key
      steering already drives the view then); free-look returns the instant
      she stops (2026-07-12)
- [x] Real jump animation wired into leaps: extracted+retimed 3 clips
      (JumpLaunch/JumpSoar/JumpLand) from winter-beanie-jump.blend (same
      BeanieRig, no retargeting needed), crossfaded across flight progress.
      Replaced the old whole-body Euler front-flip for the real model (kept
      as a fallback-only effect if the glb fails to load) (2026-07-12)
- [x] Removed all 8 mini-moons — she now leaps directly world-to-world.
      Reworked the flight arc to a cubic bezier with asymmetric height (tall
      pull at launch, shallow at landing) so it reads as "jump up high, fall
      flat" instead of a symmetric loft; widened the aim-lock range (was
      64u, now 130u) and flight duration (was capped 3.2s, now 2.5-4.5s) to
      match the much longer world-to-world distances (~70-95 surface units,
      vs. ~15-25 for the old moon-hops). Chain is now just [0,1,2,3,4].
      Full regression (4 hops + Percy + Garden + finale) passes, zero
      console errors (2026-07-12)
- [x] Solid-object collision: buildings (Chicago) and book stacks (Book
      Stacks) now block movement — walking into one "bumps back" instead of
      passing through, while turning is still allowed. Modeled as circular
      footprints on the sphere surface (direction + angular radius); checked
      in updateWalk() after the tentative forward step, reverting just the
      step (not the turn) if blocked. Water and all other worlds have zero
      colliders and are fully walkable, as requested. Verified: she gets
      stuck exactly at a collider boundary and continued input doesn't push
      her through; Deep Blue (water) confirmed unobstructed; full regression
      (4 hops + Percy + Garden + finale) passes, zero console errors
      (2026-07-12)
- [x] QA warp: number keys 1-6 instantly jump to that world (skips aim-and-
      leap) via window.__world.goto(i), for fast manual testing (2026-07-12)
- [x] Raised the follow-camera framing (more sky/headroom, lower horizon) —
      position height offset 1.3→7.5, lookAt height 1.5 (2026-07-12)
- [x] Reworked movement: Up/Down purely translate forward/backward along her
      current facing (no turning, so backing up never spins her whole body);
      Left/Right turn her in place and ease the camera yaw toward the side
      she's turning (swings to a front-ish view), decaying back to directly
      behind when released or stopped. Walk animation timeScale reverses when
      moving backward. Verified via facing()/camDebug() dot-product and yaw-
      swing checks (2026-07-12)
- [x] Scaled every world after Chicago 5x larger: radius 9.5/12/14/16/22 →
      47.5/60/70/80/110 (Chicago stays r:7), world positions scaled 5x to
      keep proportional gaps, aim-lock range 130→500, jump arc height
      24-60→100-260, flight duration formula dist/30 clamp[2.5,4.5] →
      dist/150 clamp[2.6,5.5], Percy-flight bezier control offsets 45/150/40
      → 225/750/200. Walk speed needed no change (linear surface speed =
      WALK_SPEED*dt is radius-invariant by construction). Bumped ambient
      decoration density so worlds don't read empty at the new scale: Book
      Stacks random stacks 28→140, Cucumber grass 550→2200 + wildflowers
      24→96 + resting cucumbers 6→24, Garden grass 4200→12000 + all scattered
      flower-head counts ~3x. Sea and Pigeon Plaza left as-is (orbiter-based
      schools / plazaN-clustered crowd don't thin out the same way). Full
      regression (4 real aim-and-leap jumps via jumpChain() + Percy flight +
      finale heart-burst + card) passes, zero console errors (2026-07-12)
- [x] Further density pass (5x on top of the prior scale-up bump) + 2x walk
      speed + footstep dust: Book Stacks stacks 140→700, Cucumber grass
      2200→11000 + wildflowers 96→480 + resting cucumbers 24→120, Pigeon
      Plaza crowd 44→220 + orbiting flock 14→70, Garden grass 12000→60000 +
      all scattered flower-head/stem counts 5x. WALK_SPEED 6.0→12.0 (her walk-
      cycle timeScale and footstep cadence doubled to match, so legs don't
      slide). New spawnDust() fires 3-4 small ephemeral dust-colored puffs
      per footstep (skipped on water — splash territory, not dust), reusing
      the existing spawnEphemeral/updateEphemerals system. Full regression
      (4 real jumps + Percy flight + finale + card) passes, zero console
      errors (2026-07-12)
- [~] STORYLINE REBOOT (2026-07-12, in progress) — new game design doc from
      Justin. beanie=Rachel, bred=Justin. Staged rollout:
      - [x] logo.png (Beanie & Bred cloud logo) is the title art (replaced the
            cursive H1); floats gently, drop-shadowed
      - [x] whole universe scaled 0.5x ("2x smaller"): all radii + positions
            + jump/flight constants halved (Chicago r3.5 … Garden r55, still
            increasing so "worlds get bigger and bigger" holds)
      - [x] pastel palette lift + space background now DARK PASTEL BLUE
            (0x394a6b, was near-navy); garden stays light pastel blue
      - [x] cursor/trackpad changes perspective ALWAYS now, even while walking
            (cameraLookLocked() → false; reverses the earlier move-lock)
      - [x] bbak (sleeping polar-bear plush) converted bbak/base.obj →
            game-assets/bbak/bbak.glb (Draco, 269KB) for the garden finale
      - [x] SEA world archived (kept the food/cucumber world instead, per
            Justin's correction). Chain is now Chicago→Books→Cucumber→Pigeon→
            Garden; worlds re-spaced so every hop stays inside aim-lock range;
            GARDEN_I=4, PIGEON_I=3, chain=[0,1,2,3].
      - [x] generic NPC dialogue: startDialog(lines, onDone, {speaker}) drives
            the box; SPACE / A / ENTER advances. Percy migrated onto it.
      - [x] mission-gating: bodies[i].missionDone; updateAim() won't lock the
            next world until the current world's mission is done. Chicago is
            gated by the letter; distance-to-NPC guide (#guide) framework in
            place (lights up on worlds that set guideFn/guideLabel).
      - [x] Chicago intro: snow falls radially inward + sideways wind gusts
            (320-flake InstancedMesh), pale cold "snowball" planet; on start a
            breathless messenger pigeon flutters in and reads Bred's letter
            ("come find me"), then flies off → mission appears, first leap
            unlocks. Verified end-to-end incl. downstream Percy/finale/card.
      - [x] all pigeons given big glinting eyes (were tiny dots, invisible at
            range); Chicago messenger now SWOOPS DOWN and LANDS on the surface
            before talking; Pigeon Plaza flock mostly grounded (orbiters 70→10).
      - [x] Chicago 2x bigger (r3.5→7) per follow-up (still the smallest world).
      - [x] conversation two-shot camera: during any dialogue the camera frames
            Beanie screen-left facing right + the NPC on the right facing her
            (both faces visible). Beanie auto-turns to face the NPC (rotation
            only). TALK_CAM_SIDE flips the handedness. Used by every startDialog.
      - [x] item pickup: press A near a glowing item to collect it (inventory).
      - [x] World 2 quest: 5 glowing "gift books" float around the planet; find
            Chippy (🐿️, resting), he asks for 5 favourite books, press A to
            collect each, bring them back → he's satisfied → Book Stacks gate
            opens. Verified: walk, pickup 0→5, Chippy talk phase 0→1, gate.
            NOTE: only ~1/22 book stacks are colliders now — colliding on all
            700 fenced her in and made the quest unwalkable.
      - [ ] TODO title polish: beanie sitting against the tower on the rotating
            snowball (currently stands; no sit anim yet)
      - [x] all pigeons given big glinting eyes; Chicago messenger swoops down
            and LANDS on the surface before talking; Pigeon Plaza flock grounded.
      - [x] conversation camera = profile two-shot (Beanie screen-left, NPC
            right, both faces visible); nearby props auto-hide during a talk so
            nothing covers her; Beanie holds Idle while talking.
      - [x] anim: Idle whenever still (incl. talking), Walk clip when walking,
            Shift = run (1.5x speed + faster cycle). Feet-sink fixed with a
            small radial model lift (HER_MODEL_LIFT). NOTE: distinct walk-vs-run
            *clips* still pending — source clips are Mixamo 65-bone skeleton vs
            the in-game 19-bone BeanieRig, so a retarget pass is needed; for now
            "run" reuses the walk clip sped 1.5x. herRunAction is wired so a
            'Run' clip drops in automatically once retargeted.
      - [x] world-space NPC locator beacon (floating arrow + halo) hovers over
            the current mission target; gift books enlarged + beacons + guide
            now points to the nearest uncollected book; book-cover+title pop-up
            on pickup. Number keys 1-6 no longer drag Chicago's letter along.
      - [x] World 3 (Food/Cucumber) built + bbak cooling quest: bbak (real glb)
            lounges on the grass; scattered foods + glowing pickable cold treats
            (makeFood factory); talk bbak → bring 3 foods (each rejected) →
            he reveals a glowing special cucumber → fetch + give → gate opens.
            Verified end-to-end (talk, 3 rejects, cucumber reveal, give, gate,
            leap to Pigeon Plaza), zero console errors (2026-07-12).
      - [x] Pigeon Plaza mission built (see PIGEON_PLAZA_MISSION.md): 8 real
            pigeon glbs (7 decoys + Doodles the dodo) converted from
            `pigeon collection/`; find Percy → he asks for his lost friend →
            decoys spawn one-at-a-time in order (Vanessa 3×/no-bounce, Nibbles,
            Alfred "not a parrot", Sunny, Otto, Mochi, Buckle) each intro+fun-
            fact+"No" and STAY standing → give up → Percy's "~1690, starts with
            D" hint → Doodles appears (lonely, misses family) → "we'll be your
            family" → lead him back → reunion → flock rings Percy → Percy grows
            + Beanie rides → Garden. Pigeons bounce while talking except Vanessa.
            Verified full flow, zero console errors (2026-07-13).
      - [x] Pigeon Plaza polish (2026-07-14): crowd 290→480 spread over the
            whole sphere, each pecking / walking around the surface / hopping+
            flapping, + 40 truly flying; Percy is now the real model
            (game-assets/percy/percy.glb) instead of the plush; Percy-flight
            wing-flap guarded for the rig-less real model.
      - [x] QA: number keys 1-6 now skip EVERY mission/gate (incl. Chicago's
            letter) and can be pressed from the title/dialog too (qaWarp()).
      - [ ] TODO distinct run-clip retarget (Mixamo→BeanieRig); title beanie-sit
      - [ ] TODO Garden finale: bred+percy+chippy+bbak wave + walk-toward + KISS
            cutscene → hearts → card
      - NOTE: WALK_SPEED still 12 — feels fast on the tiny Chicago (r3.5);
        revisit during the Chicago rework (may drop to ~8 or make per-world).
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
