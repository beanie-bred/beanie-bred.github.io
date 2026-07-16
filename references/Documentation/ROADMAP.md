# ROADMAP
- [x] Conversation lighting rescaled to fix glare; dialogue choice buttons
      shrunk and repositioned above the dialogue box (2026-07-16): user sent
      screenshots of an overexposed pigeon close-up ("my eyes hurt") and
      oversized choice buttons covering the character's face.
      - **Glare**: `camFill` (a point light riding on the camera) has a fixed
        intensity tuned for normal ~9-unit gameplay distance, but
        `updateTalkCam`'s close-up conversation framing pulls the camera to
        just 1.9-4.3 units — at that range the same intensity blows out via
        inverse-square falloff (decay=2), worst on small subjects like
        pigeons, which sit at the closest 1.9-unit floor. Now rescaled every
        frame to the camera's actual shooting distance (`95 * (dist/9)²`) and
        restored to 95 on every path back out of a conversation (dialog end,
        QA warp mid-conversation). Verified numerically (`camFillDebug()`:
        4.23 during the exact reported pigeon shot, 95 after) and visually
        reproducing the same scene from the screenshots.
      - **Choice buttons**: were fixed at screen-center-right at a large size.
        Shrunk (~40% smaller font/padding/icons) and anchored the stack flush
        above the dialogue box's own right edge (same
        `right:calc(50vw - min(680px,90vw)/2)` formula the box itself uses),
        with the vertical gap computed in JS from the box's actual rendered
        height each time choices appear (`positionDialogChoices()`), so it
        holds regardless of how many lines the current line wraps to.
        Verified live: 0px right-edge diff, 14px gap, no longer overlapping
        the face; still fully clickable.
- [x] Per-planet journal redesign with sticker collages; pigeons coo instead
      of squealing in dialogue (2026-07-16): replace the plain grid-of-squares
      journal with one themed scrapbook page per planet, and differentiate
      pigeon speech from everyone else's.
      - **Journal**: one page per world (`JOURNAL_PAGES`), each with its own
        font, page texture/color palette, and a deterministic pseudo-random
        collage layout (`collagePlace()`/`jrand()`) of sticker silhouettes —
        locked stickers render as a dark silhouette, unlocked ones show the
        full sticker art. Reuses already-loaded web fonts and each world's
        existing CSS theme class.
      - **Dialogue sound**: every non-pigeon speaker now makes an
        Animal-Crossing-style syllable squeal while talking (existing
        `playSpeechSqueal`, now applied generally); pigeons/doves/the dodo
        instead get a new `playSpeechCoo()`, routed via
        `isPigeonSpeaker(speaker)`. Verified the speaker-routing regex against
        every actual speaker string in the codebase (9/9 cases correct).
- [x] Fall/landing rumble, planet-title arrival sound, more pigeon ambience
      (2026-07-16): asked for audio feedback on impact and on each planet's
      title reveal, plus a fuller pigeon soundscape.
      - Added `playFallRumble()` (low-oscillator rumble tied to the landing
        impact, alongside the existing camera shake) and `playTitleSound()`
        (a short arrival sting on each `showPlanetTitle()` call).
      - Pigeon Plaza's ambient pigeons now also coo and flutter their wings
        periodically (`playCoo`/new `playFlutter`), on top of their existing
        idle motion.
- [x] Bred's real rigged wave wired into the greet cutscene; couch glow fixed
      for good; THE END camera no longer opens underground (2026-07-16):
      follow-up round after the Garden endgame batch — Bred's greet cutscene
      was still using a procedural whole-body bob (his model had no rig yet
      at the time), the couch was reported bright enough to blow out whoever
      sat on it even after an earlier 60→12 light-intensity cut, and THE
      END's opening shot read as starting from underneath the planet.
      - **Rigged Bred**: exported a real rigged `bred_wave.glb` (idle +
        idle_wave clips, Draco + JPEG compressed) and wired it through
        `loadModelFull`/`AnimationMixer`, the same pattern as Beanie's own
        clips — `clipAction(wave).play()` then immediately paused/reset to
        frame 0 so it holds an idle pose until `userData.playWave()`
        triggers it. The greet cutscene (`startBredGreet`/`updateBredGreet`)
        now plays this real arm-wave instead of the old rock/bob, with a
        walk-toward-Beanie beat first and the couch positioned well clear of
        the shot.
      - **Couch glow, for real this time**: the earlier intensity cut
        (60→12) still wasn't enough — the near-white couch material itself
        (`0xf6f4ee`/`0xfdfbf6`) was pushing past the UnrealBloom threshold
        (0.82) under the Garden's bright daytime lighting. Removed the point
        light entirely and darkened the material (`0xdcd5c6`, cushions
        `0xe8e1d3`) to sit under the bloom threshold — Percy and Chippy are
        now clearly visible sitting on it.
      - **THE END camera**: `camPos.lerp()` from wherever the previous
        cutscene's camera was to the new orbit start cut a straight chord
        through the planet sphere (the two points are far apart on a large
        sphere), reading as "opens from underground." Fixed by snapping the
        camera straight to the orbit's start position instead of lerping
        across the arc, and anchoring the orbit basis to the direction the
        characters actually face (rather than an arbitrary perpendicular) so
        the shot deterministically opens on their faces.
- [x] Summer landed on her BACK during the fall/get-up — root cause was a
      skeleton-direction bug (2026-07-16): user asked "why does she land on her
      back? feels like her body was assigned to the wrong direction of the
      skeleton" — and that instinct was essentially right. Findings:
      - Her MESH binding is fine: in idle she stands upright and faces -Y with
        arms at her sides, following the skeleton correctly. Not a mesh problem.
      - The skeleton itself is the issue: Summer's entire spine chain (Hips,
        Spine, Chest, Neck, Head) is built **180° flipped** in rest orientation
        vs Winter's shared 19-bone skeleton (arms differ ~67°, and bone names
        aren't even identical — 21 vs 19 bones). Measured via per-bone
        rest matrix_local angular diff.
      - The fall ("SummerFall" -> LandFallGetUp) was retargeted from Winter by
        copying bone rotations WITHOUT accounting for that 180° spine
        difference, so her whole torso came out belly-UP: she landed supine and
        did Winter's face-down push-up motion while on her back. Confirmed
        numerically (chest ventral axis pointed +Z through the whole prone
        phase, vs Winter's -Z) and by a top-down render (saw her back + shoe
        soles, not her face).
      - Her idle/walk/run were authored natively for HER skeleton, so they were
        never affected — only the retargeted fall inherited the flip. (This is
        also why the earlier "fall matches Winter" claim was wrong: limb detail
        matched, but the gross body orientation was flipped and went unchecked.)
      - FIX: proper WORLD-SPACE retarget of Winter's correct face-down
        LandFallGetUp onto Summer — for each bone/frame, take Winter's world
        rotation delta from its own rest and apply it to Summer's rest
        (`delta = W_pose_world @ W_rest_world^-1; S_target = delta @ S_rest_world`),
        then convert to Summer-local and keyframe; Hips root translation scaled
        by the 0.842 height ratio. The 180°/67° rest differences cancel out
        automatically. Verified: belly -Z (face-down) through the prone phase,
        stands upright by the end, arms eased into Summer's idle hang over the
        last 60 frames for a seamless get-up->idle handoff.
      - LESSON: never retarget by copying local bone rotations between rigs
        whose rest orientations differ — always go through world space. And a
        180° torso in the fall is a louder symptom of a rest-orientation
        mismatch that also explains subtler arm weirdness.
- [x] Summer's idle/walk/run/get-up arms fixed properly — natural hang, smooth
      swing, no more tucking behind (2026-07-16): user sent an in-game
      screenshot showing her idle arms folded behind her back, plus "her
      arms move weirdly and not smoothly when she moves." Three distinct
      bugs, all now fixed:
      - **Idle arms tucked behind the back.** The idle pose (untouched by
        the earlier walk fix) hung the arms nearly straight but pulled
        *inward and backward* (hand offset X-0.12, Y+0.06-behind), so the
        hands vanished behind her hips. Winter's idle by contrast hangs
        them slightly out and neutral. Re-solved a natural hang (hands just
        outside the skirt, slightly forward, ~20° relaxed bend) and baked
        it flat across the whole idle so it's perfectly steady, with the
        torso's own breathing still carrying through.
      - **"Not smooth when moving" = violent per-frame snaps.** The walk
        arm bake had 158-174°/frame spikes at two frames per cycle (vs ~13°
        average) — the forearm was snapping. Two causes: (a) the swing was
        driven off *foot world-Y*, which for this in-place walk barely
        moves (the feet mostly go up/down, not forward/back), so the signal
        was near-stepped — held, then jumped; (b) the per-frame IK solve
        flipped the elbow (pole flip) at the swing reversal. Replaced the
        whole approach with a **rigid arm swing**: rotate the entire arm
        about the shoulder by a smooth angle proportional to the *thigh's*
        forward lean (a clean, high-amplitude signal), keeping the elbow
        bend fixed. Result: forearm velocity 0.1°/frame (dead smooth),
        upper-arm peak 20°/frame walk / 52° run, real visible swing, and
        100% correct opposite-arm/leg coordination. Same fix applied to Run.
      - **Get-up ended tucked back too.** The fall/get-up (LandFallGetUp)
        rose correctly but *settled* into the same old tucked-behind pose
        in its last ~40 frames, which is what the user meant by "weird when
        she stands up" — and it made the get-up→idle handoff pop. Eased the
        arms into the natural idle hang over frames 185-245 (smoothstep),
        leaving the dramatic fall/push-up/rise untouched, so it now ends
        exactly matching idle for a seamless transition.
      - **Root Blender lesson (why the earlier fix looked right but wasn't
        fully):** reading `pose_bone.rotation_quaternion` while an IK
        constraint is *actively solving* returns an incomplete value; the
        continuity check (`dot>0`) only catches >180° sign flips, not these
        large-but-under-180° snaps — you have to measure actual per-frame
        angular velocity. Also caught and merged around TWO concurrent
        re-exports by the parallel session mid-fix (it kept changing the
        shipped glb underneath this work); re-applied all three fixes onto
        their latest so their walk-timing and Run-cycle changes were kept.
- [x] Real foot-locked walk + run cycles for both Beanies, built from an
      analytical 2-bone IK solve rather than hand-tuned constants
      (2026-07-16): the user's request this round was an unusually precise,
      fully-spec'd animation brief — hard constraints on weight transfer,
      zero foot slide/sink/float, a proper stance→compress→push-off→swing
      cycle, and a true flight phase for running. Built genuinely new `Walk`
      and `Run` actions for both `BeanieRig` (Winter) and `SummerRig`
      (Summer) using real per-frame inverse kinematics — not the sine-wave-
      constant recipe used for earlier walk/idle passes on this rig (see the
      main rigging memory for that method; this is a different, stricter one
      for when "looks right in a clay render" isn't enough and the actual
      foot position needs to be provably fixed to the ground).
      - **Method**: for each leg, at every single frame, solve the 2-bone
        (thigh+shin) triangle via law of cosines so the ankle lands exactly
        on its intended target — a FIXED point for the whole stance window
        (zero-slip, by construction, not by tuning), or a smoothstepped arc
        from release to next-contact during swing. Authored the whole gait
        in a mental reference frame where the hips genuinely travel forward
        each cycle (this is what makes weight-transfer and stance-timing
        reasoning correct), then subtracted that net drift back out of only
        the Hips' translation at bake time — rotations don't need any
        correction for this, since they only depend on the *relative*
        hip→ankle vector, so the result is a seamless in-place loop that
        still slots into this engine's existing architecture (JS drives her
        actual world movement externally; the clip itself must never net-
        translate).
      - **Verified with hard numbers, not screenshots**: sampled the ankle
        bone's real evaluated world position at every frame and asserted it
        doesn't move during that leg's own stance window. This caught two
        real bugs a viewport glance did not — a bone-local-axis mixup
        (Winter's and Summer's rigs do NOT share the same local-axis
        conventions, confirmed the hard way) and a reach-limit bug (a
        "compress only under load" hip-bob model can push the required leg
        extension past 100% right at heel-strike/toe-off, exactly the
        moments a naive model assumes zero compression). Fixed with a
        permanent baseline crouch throughout the whole cycle, not just a
        load-triggered dip. Final check: sub-micrometer slip on Winter (her
        rig's leg bend axes are perfectly parallel), ~2% of leg length on
        Summer (that rig has a small ~1.6° built-in skew between her own
        thigh/shin bend axes — a real, tiny rest-pose imperfection, well
        under any visible threshold at this character's scale).
      - **A second export bug found only by parsing the shipped `.glb`'s own
        keyframe TIMES, not just checking clip names/values looked
        reasonable**: placing multiple actions' NLA strips at sequentially
        staggered start frames (to keep Blender's own timeline tidy) leaked
        that stagger directly into each exported clip's sample times —
        every action after the first came out with keyframes starting at
        some large non-zero time instead of 0, so `THREE.AnimationClip`
        (which derives duration from the last keyframe assuming a 0-start)
        played several clips far too slowly in-game. Fixed by starting every
        strip at the same frame on its own independent track. Also switched
        the export to Draco mesh compression + JPEG textures (matching this
        project's established asset convention) after a first pass came out
        7-13MB per character instead of the shipped ~1-1.5MB — the mesh
        itself wasn't the issue, embedded full-resolution PNGs were.
      - Also added `herSummerRunAction` (Summer never had one loaded before),
        mirroring how `herRunAction` already sits loaded-but-dormant for
        Winter — both are ready and correct, but neither has a gameplay
        trigger yet since running isn't a mechanic this game currently has;
        flagging that as a real follow-up decision, not assuming it.
      - This composes with, rather than replaces, the arm-specific fix
        below — confirmed the shipped `beanie_summer.glb`'s `Walk` clip
        still carries this same leg-IK timing signature after that
        additional pass landed on top of it.
- [x] Summer's walk-cycle arms genuinely fixed — the earlier "fixed" bake was
      silently wrong (2026-07-16): user reported (a second time, with fresh
      Blender screenshots) that Summer's arms go backward instead of
      spreading forward when she runs and gets up, plus pasted a detailed
      human-biomechanics checklist as a standing validation bar going
      forward.
      - **Root cause: reading `rotation_quaternion` while a `chain_count=2`
        IK constraint is actively solving does not return the complete
        pose.** The constraint visibly drives the bone correctly on
        screen and even echoes a plausible-looking value back through
        `rotation_quaternion`, but that value silently omits part of what
        the solve actually did — baking it into a keyframe and later
        replaying it with the constraint removed reproduces a completely
        different (and wrong) arm position. Proved this by capturing the
        exact same "solved" quaternion and manually reassigning it with no
        constraint present: it reproduced the wrong pose, not the one seen
        live. The fix is to capture `pose_bone.matrix` (the full evaluated
        transform) while the constraint is active, drop the constraint's
        influence to zero, and reassign that matrix directly — Blender
        back-solves the correct `rotation_quaternion` from it. This is
        almost certainly why the walk-arm fix earlier this same day looked
        right in a quick check but wasn't.
      - **Second, independent bug found via the biomechanics checklist:**
        the rebuilt swing was timed off Winter's own walk cycle sampled at
        the matching fractional time, which silently assumes both
        characters' leg cycles start at the same phase. They don't —
        measured against the checklist's "opposite arm/leg" rule, only
        23% of frames had the correct arm leading the opposite leg. Fixed
        by driving each arm's swing directly from Summer's own leg
        position (`Foot.R.y - Foot.L.y` for the left arm and vice versa)
        instead of a foreign, phase-assumed signal — now 100% of frames
        pass the check, and elbow flexion stays within the checklist's
        0-150° range throughout (was 54-138°).
      - **Two visual red herrings during verification, worth remembering:**
        a viewport screenshot showed what looked like a T-pose even after
        the fix — turned out to be a stale OpenGL draw-cache artifact
        specific to the interactive viewport under rapid scripted bone
        edits; a proper `bpy.ops.render.render()` to a file showed the
        correct bent-arm pose immediately. Separately, re-checking the
        exported glb's animations looked "frozen" on re-import — the
        importer had set `animation_data.action` to one of the three clips
        directly, which overrides NLA-track playback regardless of each
        track's own mute state; clearing it let the tracks evaluate
        correctly. Neither was a real data bug; both would have sent this
        down a wrong path if trusted at face value.
      - **Explicitly re-checked against the user's checklist:** walk-cycle
        knees bend in a single consistent direction (never backward or
        sideways), straight during stance and flexing only during swing,
        confirmed on both the old and new arm data — the repeated "legs
        fold back" report was never a real leg bug. Also re-verified the
        fall/get-up motion's arms frame-by-frame against Winter's own
        reference clip (prone push-up, crouch, stand) — they match
        Winter's pattern at every checkpoint checked, so that motion was
        not touched.
      - **Caught a concurrent-edit clash before it shipped:** first export
        landed fine, but a live file-hash check right before committing
        showed `beanie_summer.glb` had changed size again underneath this
        session — another parallel session had added a whole new `Run`
        animation and touched `Idle` since this fix was copied in. Because
        this fix lived only in the Blender MCP server's in-memory session
        (never saved to a shared `.blend`), their re-export naturally
        didn't include it, and it would have been silently lost on a blind
        overwrite. Re-imported their latest export, confirmed `Run` had
        the identical frozen-arm and broken-coordination bug (arm swing
        stuck within 0.001 units across the whole cycle, coordination
        right on only 10/21 frames), applied the same leg-phase-driven fix
        to both `Walk` and `Run` on top of their current file, and
        re-exported all four tracks (`Idle`, `Walk`, `Run`,
        `LandFallGetUp`) together so nothing either session did got lost.
      - Re-exported `beanie_summer.glb` with Draco compression (the first
        export attempt omitted it and bloated the file 3x; matched back to
        the original ~1.4MB once enabled), verified the fix survives
        export/re-import with NLA tracks properly isolated, and confirmed
        live in-game that movement correctly enters the `"walk"` animation
        state.
- [x] Garden endgame cutscene + polish batch (2026-07-16): a big combined
      request — fainter/weightier footsteps, dimmer couch, Bred navigation, a
      scripted greeting cutscene, a single-option letter, a reworked THE END,
      and removing the planet-title glow.
      - **Footsteps**: they rendered solid black because `updateEphemerals`
        overwrote each decal's opacity every frame with a fade curve clamped
        to 1.0, ignoring the material's own faint 0.22 — so footprints peaked
        FULLY OPAQUE right after spawn. Added a `maxOpacity` arg to
        `spawnEphemeral` (default 1, so nothing else changes) and pass 0.5 for
        footprints (+ a softer dark-brown tone instead of pure black), so they
        read as faint pressed marks. **Weight**: the per-step camera "punch"
        was a barely-there 0.1 dip on a 7.5 height — bumped to 0.32 with a
        slower recovery (exp(-9) vs -12) so each stride lands with real heft.
        Both apply to Winter and Summer (shared footstep block in updateWalk).
      - **Couch glow**: the Garden couch's PointLight was intensity 60, which
        blew out the white couch and washed the characters on it to
        unrecognisable — dropped to 12 (range 26). Percy + Chippy are now
        clearly visible sitting on it.
      - **Planet-title glow**: removed the radial-gradient backdrop behind
        `#planetTitle` — the big world names now sit cleanly on the sky.
      - **Bred navigation**: the "find Bred" compass never showed because the
        Garden was the ONE world left at the default `missionDone = true` (only
        worlds 0-3 get flipped false near WORLD_DEFS), which suppressed its
        guide entirely. It has no next world to gate, so setting it false just
        turns on the "💛 find Bred, N steps away" compass like every other
        world. Verified live.
      - **Greeting cutscene**: replaced the old "walk into Bred → heart burst"
        finale with a scripted sequence — she notices him ("💭 Oh…! Someone's
        over there!"), he turns to face her, waves, walks across the meadow to
        her, and a letter floats over into her hands, opening the card.
        Implemented by reparenting Bred out of the couch group into the scene
        (`scene.attach`) so he can turn/walk in plain world space; phases
        (notice/turn/wave/walk/handoff) drive his facing + position, with the
        camera framing both of them. **Caveat:** Bred's model is unrigged, so
        the "wave" is a happy whole-body bob-and-sway, NOT the authored
        arm-wave in `bred T/Bred_idle_wave.blend` — using that needs a rigged
        animated glb export + an AnimationMixer swap, a riskier rework of the
        now-working cutscene, left as a dedicated follow-up.
      - **Letter → THE END**: the finale card now offers ONLY "close the
        letter" (the replay button is hidden; replay lives on the THE END
        screen). **THE END** reworked: the pair stands out in the meadow a
        good arc from the couch (which, with Chippy + Percy still on it, sits
        far behind them), both facing the SAME way (outward) side by side
        holding hands, and the orbit camera pulls out further (radius 15,
        height 5.5 vs 8/3.2) for the 360. Verified the whole endgame end to
        end — notice → wave → walk → letter → close → THE END — with no
        console errors. (bbak lives on Cucumber Meadow, not the Garden, so
        only Chippy + Percy are actually behind them.)
- [x] Summer's fall-motion arms fixed via IK; wired into the Garden landing
      (2026-07-16): user sent a screenshot of Summer mid-fall with her arms
      tucked against her torso instead of spread out, said "her arms go in
      when she tries to stand up... unlike winter beanie... her legs also
      both fold back for no reason," and asked for this to actually play
      "as the same interface as when winter beanie falls on other planets."
      - **The quaternion-conjugation retarget (used for the walk-cycle fix)
        did not hold up for this pose.** Tried both possible conjugation
        directions on the arm chain and measured the resulting hand
        position against Winter's own — neither got within half of her
        actual reach distance, confirming this wasn't just a sign error
        this time.
      - **Switched to a geometric fix: 2-bone IK against Winter's real hand
        position.** For each frame, took Winter's actual hand position
        relative to her shoulder, scaled by Summer's own ARM-length ratio
        specifically (not overall body scale — her arms are proportionally
        shorter relative to her torso than Winter's, so scaling by body
        size alone put the IK target beyond her actual reach), and solved
        for the shoulder/elbow rotations that place her hand there — using
        Blender's own IK constraint system rather than hand-rolled aim
        math (an earlier custom aim-solver attempt had a 0.45-unit error
        even after two rounds of fixing dimension-mismatch bugs; the
        built-in IK solver reproduced the target position exactly).
        Verified by measuring hand-to-chest offset error numerically (was
        ~50% short of target, now exact) before ever re-rendering.
      - **The reported leg problem turned out to be a false alarm** — a
        side-by-side Euler-angle readout showed Summer's thigh rotations
        with a consistent sign flip vs Winter's, which looked like a real
        bug, but a low, front-on render at the same frame showed both feet
        already positioned naturally. Comparing raw Euler angles across two
        differently-rested rigs isn't reliable (same lesson as the walk fix,
        this time on the other side of the coin — the flip data can also
        make a CORRECT retarget look wrong on paper). Trusted the render,
        not the numbers, and left the legs untouched.
      - **Exported the fixed clip into `beanie_summer.glb` as a real
        `LandFallGetUp` animation and wired `arriveGarden()` through
        `startLandingSequence()`/`updateLandingAnim()`** — the exact same
        machinery every other world already uses (fall on face, dust
        burst, camera shake, get up, orbit, click-gated title card).
        Previously she just teleported in standing the instant the iris
        opened, which is what made the mismatch against Winter's landings
        so obvious once actually compared. `updateLandingAnim()` and
        `landingClipDuration()` now pick whichever character's own fall
        action applies, mirroring the existing `showSummer` pattern used
        everywhere else in the animation code.
      - Verified end-to-end via `qaWarp` on both Summer's world (Garden)
        and Winter's (Main Stacks) — full fall → dust → get-up → orbit →
        click-gated title → normal walk, on both characters, zero console
        errors either way.
- [x] Fall-landing camera flipped to a front view + a big performance pass
      (2026-07-16): Bred asked for the fall/landing POV to be "the opposite
      view (so when she stands up, the player can see her face side)," and
      reported the game "is still laggy."
      - **Landing camera → front**: the fall/get-up camera sat BEHIND her
        (a deliberate 3/4-back angle from the reference-matching pass), so as
        the get-up clip finished she rose facing AWAY from the camera and you
        saw her back. Flipped the camera's forward offset from `-0.8` to
        `+0.8` so it now sits in FRONT of her looking back — verified live at
        the end of the get-up clip: she rises to face the camera and her face
        is clearly visible. (At the ~4-7 unit landing distance the camera is
        well clear of her head, so the old "+fwd clips into her head" concern
        from a much closer framing doesn't apply.)
      - **Performance — measured, not guessed**: temporarily exposed the
        renderer + scene and read `renderer.info.render` after a single
        non-composer render per world (the bloom EffectComposer resets
        `info` to its 1-call final pass, which is why the existing `info()`
        debug always reported ~1 draw call). The picture was damning:
        **the Garden rendered 13.6M triangles, and Emerald Meadow AFTER the
        cucumber reveal hit ~48M triangles / 9,000+ draw calls** — by far the
        worst spots, and both mid-gameplay. A per-mesh triangle census
        pinned the two root causes:
        - **The cucumber model is ~5,600 triangles each**, and the planetary
          RING instances it ~4,000 times = **~22M triangles** just for the
          ring. Fixed by driving the ring off a low-poly capsule (~70 tris)
          while keeping the model's material — at ring distance (tiny,
          distant, tumbling) it's indistinguishable, confirmed by screenshot.
          The individually-cloned hero + ground cucumbers she actually walks
          up to and picks up still use the full-detail model, so nothing she
          sees up close changed. Emerald post-reveal dropped 48M → ~2M tris,
          9,000+ → ~700 draw calls.
        - **The grass "velvet tuft" was a 156-triangle capsule**, instanced
          60,000× in the Garden + 11,000× on Emerald = **~11M triangles**.
          Dropped the capsule to (1,4) subdivisions (~40 tris) and trimmed
          counts (Garden 60k→40k, Emerald 11k→8k) — still reads as a dense
          fleecy meadow, confirmed by screenshot. Garden grass 9.36M → 1.6M.
        - Also trimmed the flower-head sphere segments (tulips 8×8→6×5, daisy
          centres 8×6→6×5, etc.). Garden overall 13.6M → ~5M triangles.
        Net: the whole-scene triangle budget fell from ~40M+ to ~8M — roughly
        a 5× cut concentrated exactly on the two heaviest worlds. Verified a
        clean pass through all five worlds afterward with zero console errors,
        and that the low-poly cucumber ring + trimmed grass/flowers still look
        right. (Pigeon Plaza's ~980 draw calls from 520 un-instanced pigeons
        is a separate, lower-impact CPU cost left for a future instancing
        pass — the triangle bottlenecks above were the dominant lag source.)
- [x] Summer Beanie's walk arms retargeted from Winter's proven motion,
      full arm chain (2026-07-16): the hand-on-back fix above worked, but
      user said the arms still didn't look right — "always fold back and
      dont spread out to the sides... unlike winter beanie" — and asked
      specifically for the natural counter-swing gait (left arm forward
      when right foot is forward).
      - **Stopped hand-tuning angles and retargeted Winter's own walk
        animation directly instead.** The previous fix only touched
        `UpperArm.L/R` with a from-scratch swing; the rest of the arm
        chain (`Shoulder`, `LowerArm`, `Hand`) still sat at old,
        disconnected values, and an approximated swing was never going to
        genuinely match Winter's actual proven motion no matter how much
        the angles got tuned. Instead: sampled Winter's real
        Shoulder/UpperArm/LowerArm/Hand rotation at the fractionally-
        corresponding point in Summer's own walk cycle (their two cycles
        run at different lengths/timing), and re-expressed each through
        the same per-bone rest-orientation compensation already proven
        for the fall-motion retarget earlier this session. This carries
        over Winter's actual swing character (including the natural
        counter-swing against the same-side leg) instead of reconstructing
        an approximation of it.
      - Verified from behind and from the side across the full cycle
        (confirmed opposite-arm-opposite-leg coordination directly, not
        just "no longer touching her back") and live in the Garden.
- [x] Summer Beanie's walk-cycle arm swing fixed — hand was landing on her own
      back (2026-07-16): user sent an in-game screenshot from behind her
      showing a round shape in the middle of her back while walking in the
      Garden, asked to "fix summer beanie's skeleton and movements."
      - **Root cause: the walk cycle's arm swing was never authored around
        her actual rest pose.** Summer's bind pose already IS a natural
        relaxed-arms-at-sides stance (unlike Winter's T-pose bind, where
        every pose needs a correction to look relaxed) — confirmed by
        checking her Idle action, which holds the arms at exactly (0,0,0)
        rotation, i.e. untouched rest. The walk cycle's `UpperArm.L/R`
        channels instead held a large, nearly-constant ~70° rotation away
        from that rest, which — given how this specific rig's local axes
        are oriented — swept the hand inward and up behind her torso at
        the extreme of the swing. The actual cycling component (on a
        different axis) moved the hand almost nowhere, which is why the
        pose read as "stuck" rather than a normal alternating swing.
      - **Diagnosed by rendering the walk cycle directly in Blender** (the
        live game's own camera/UI made it hard to catch the exact swing
        phase) — rendering the peak-swing frame reproduced the user's
        screenshot exactly, both hands landing on her back.
      - **Found and fixed a real gap in the diagnostic tooling itself**:
        `window.__world.beanieBoneDebug()` always read `her.children[0]`
        — which is permanently Winter's model, added first, regardless of
        `showingSummer`. Every earlier check of "Summer's" pose this
        session was silently reading Winter's static bones instead,
        which is what made the frozen-looking values so confusing to
        debug at first. Fixed to select the actually-visible model.
      - **Rebuilt only the two `UpperArm` channels** (legs, forearms, and
        hands were already correct and untouched) as a modest ±18° swing
        on the empirically-confirmed correct axis, perfectly synced to
        the existing leg-stepping keyframe timing. First attempt swung the
        arm in phase with the same-side leg (both forward together) —
        still visibly wrong, caught it from a side-view render and
        flipped the sign so arm and same-side leg move in true
        opposition, matching a real walking gait.
      - Verified live in-game across multiple points in the cycle (zoomed
        screenshots from behind, matching the original bug report's
        angle) and via direct inspection of the exported glb's animation
        data. Zero console errors.
- [x] Garden daytime haze: the other worlds barely visible in the day sky
      (2026-07-16): Bred asked to make the other planets "barely visible from
      the garden because it's daytime." The other four worlds hang 840–1500
      units out and, unfogged, read as saturated coloured orbs in the Garden's
      clear blue sky (Emerald Meadow especially, a vivid green ringed planet) —
      which breaks the bright-midday feel, since in real daylight you can barely
      make anything out up there. Fixed with a linear `THREE.Fog` (mid-day
      sky-blue `#a6ccef`) applied ONLY on the Garden, set in `applyWorldSky()`
      alongside the sky swap and cleared to `null` on every other world (space/
      dawn/morning all want their planets and stars crisp). The trick is the
      huge gap between the compact Garden and the distant worlds: the fog's
      `near` (200u) sits well past everything the player ever sees of the Garden
      itself — the roaming camera is ~9u back and even the wide arrival-orbit
      establishing shot only pulls to ~76u (content out to ~160u) — so the
      flowers, couch, and ground stay 100% crisp, while the `far` (1050u) sits
      short of the nearest other world, blending every planet 75–100% into the
      sky. Verified by probing the fog blend factor at each distance (Garden
      content 0% faded; Chicago 75%, Main Stacks 98%, Emerald Meadow and Pigeon
      Plaza 100%) and with a frozen-camera before/after: the vivid green ringed
      planet drops to a barely-there ghost while Chicago stays crisp and
      unfogged. No per-frame cost — it's a single scene-level fog toggle.
- [x] Per-world skies: a night→sunrise→day arc across the whole journey
      (2026-07-16): Bred asked for the sky to "show bits of more sunrise
      starting from emerald meadow," to be "sky blue for the garden," and to
      "always [be] a really amazing gradient... even the sky in the garden
      must be a pretty gradient." Turned this into a full day-cycle told
      through the sky as she travels: the two early worlds (Chicago, Main
      Stacks) stay deep night; the sunrise first breaks at Emerald Meadow;
      it opens into a golden morning at Pigeon Plaza; and by the Garden it's
      a bright, clear daytime sky-blue — every one of them a real multi-stop
      vertical gradient, the daytime Garden included (no more flat blue fill).
      - **One gradient builder, one per-world table**: refactored the old
        single hardcoded `SPACE_BG_TEXTURE` canvas-gradient into a reusable
        `makeSkyGradient(stops)` and defined a `WORLD_SKY[]` table indexed by
        `curI` — Chicago/Main Stacks reuse the (now richer) night gradient,
        Emerald Meadow gets a dawn gradient (cool blue zenith bleeding down
        through mauve into warm coral/gold at the horizon), Pigeon Plaza a
        golden-morning gradient (morning blue up top, apricot/cream low), the
        Garden a bright day gradient (sky-blue zenith easing to near-white
        pale blue at the horizon). scene.background is a screen-space 2D
        canvas texture, so each is a fixed zenith-to-horizon vertical wash —
        stylized and non-directional, which reads right for this storybook
        look.
      - **Stars fade with the dawn**: added a single `nightFactor` that scales
        the opacity of every night-only sky element together — all the
        `makeStars` point-cloud layers plus the constellation anchor stars and
        their connecting lines (the anchors/lines had to be made `transparent`
        to fade; previously they stayed at full opacity even in daylight).
        Full at the night worlds, a faint 0.35 at the Emerald Meadow dawn (a
        few dawn stars still linger), 0.1 at Pigeon Plaza, and 0 in the
        Garden. Shooting stars now also stop spawning once `nightFactor` drops
        past a faint-dawn threshold, so none streak across a morning/day sky.
      - **Applied at the right moment**: `applyWorldSky(bi)` (sets the sky +
        the star factor) is called at the START of a landing so the fall/
        get-up + orbit/title cutscene already shows the sky of the world she's
        arriving under, and again as a backstop in `arrive()` for the paths
        that skip the landing (procedural-fallback jump, QA number-key warps).
        Replaced the Garden's old flat `GARDEN_BG` fill + manual
        `star.visible = false` toggling (in both `arriveGarden` and the
        `gotoCouch` debug helper) with the same call — the old `.visible`
        toggle also never touched the constellations, so those used to hang in
        the Garden's daytime sky. Verified live across all five worlds: deep
        navy + stars + constellations at Chicago/Main Stacks, the coral dawn
        at Emerald Meadow, the golden morning at Pigeon Plaza, and the clear
        blue day in the Garden, with no console errors.
- [x] Landing-camera reference match, Bred stand-and-wave scene, a real
      ending, journal redesign, messenger pacing (2026-07-16): Bred rejected
      the previous round's 90°-rolled landing camera outright ("아니 이게 아니라")
      and gave a Blender reference screenshot instead — a level, near-ground,
      3/4-back shot of her lying pose with a gentle horizon curve, nothing
      like the steep Dutch-angle roll that shipped before. Also asked for
      Bred to stand beside the couch instead of sitting on it (with a proper
      "notice him, then he waves" beat), a real closing cutscene after his
      birthday card — Beanie and Bred standing together holding hands under
      a "THE END" title, same treatment every world's arrival gets — a
      genuine redesign of the journal interface, and a slower messenger-
      pigeon landing beat. The Garden flower-sway request in this same
      message was explicitly deferred to a scheduled 4am pass (see the entry
      below — it ended up running mid-session, since a scheduled task reads
      whatever is on disk at fire time, not a snapshot from when it was
      requested, and picked up everything below already in place).
      - **Landing camera**: dropped the 90° image roll entirely rather than
        adjusting its angle — re-reading the reference, the dramatic diagonal
        was never supposed to come from rotating the CAMERA (a real Dutch
        angle rolls the horizon too, which the reference clearly doesn't
        have); it comes from her own fallen body reading diagonally against
        an otherwise level shot. `camera.up` is now just her true up vector,
        matching every other camera in the game. Repositioned lower/closer
        behind-and-to-one-side for a 3/4 back angle, and flipped which side
        the camera favors so her head lands on the right of frame (reference:
        head-right/legs-left) instead of the left.
      - **Bred stands beside the couch**: moved off the cushion to stand on
        the ground next to it (Percy and Chippy still sit — only Bred was
        asked to stand). His model has no rig at all (a single fused mesh,
        confirmed by traversing it live), so "happily waving" couldn't be a
        real arm animation — it's a whole-body rock/tilt instead, triggered
        once she's close. Reused the existing per-world `guideFn`/
        `guideLabel` compass system (previously unset for the Garden, so she
        got zero notice/compass guidance toward him at all) to get the
        generic "spotted them" glance for free, then added a second, closer-
        range beat (`startBredGreet`/`updateBredGreet`, `BRED_GREET_DIST=9`)
        specifically for his wave, ahead of the existing 5.5-unit finale-
        embrace trigger — notice, then wave, then embrace, in that order.
      - **A real ending**: after the birthday card's message finishes typing,
        a new "💛 close the letter" button (previously the ONLY option there
        was an instant restart) hides the card and starts `startTheEnd()` —
        the same orbit-camera + big-title treatment every world's arrival
        gets (`showPlanetTitle`), pointed at Beanie and Bred standing
        together instead of a planet, titled "THE END." **Hit the exact same
        position bug documented elsewhere in this file's spirit but never
        actually written down before now**: `updatePose()` unconditionally
        rebuilds `her.position` from `orientation` + the body's own
        center/radius every time it's called — setting `her.position`
        directly and then calling `updatePose()` right after just gets
        silently overwritten, collapsing her back onto emptiness or, in this
        case, exactly onto Bred's own position (confirmed live: a 0.75-unit
        intended offset came out as 0.09 actual). Fixed by deriving a
        genuinely distinct point's own up-vector FIRST (`bp + side*0.9`, then
        its own `normalize(pos - center)`), and building her orientation from
        THAT, so `updatePose()` lands her at the right spot instead of
        re-deriving Bred's. Neither character has a rig for actually clasping
        hands, so it's sold with close standing proximity plus a couple of
        drifting hearts between them — reused the finale's own heart-particle
        system rather than inventing a new one. The old "click to continue"
        prompt text now reads "click to play again" and reloads, since
        continuing to gameplay doesn't apply once the game has actually
        ended.
      - **Journal redesign**: the two-page-book structure from an earlier
        round was structurally already a book (rotateY hinge, spine), but
        with no cover, no page-stack depth, and flat colors it read as "two
        beige rounded rectangles," not a keepsake journal. Added a proper
        hardcover shell (`#journalCover`, warm leather-brown gradient with an
        inset gold border) that pops in before the pages swing open (staged
        with a `transition-delay` so the two motions read as distinct beats
        instead of happening simultaneously), a woodgrain spine with
        stitching detail, a pink ribbon bookmark peeking out the top, and
        layered box-shadows on each page's outer edge to suggest a stack of
        paper rather than one flat card.
      - **Messenger pigeon pacing**: the swoop-down landing used to call the
        "start talking" callback in the exact same frame `k` (the landing
        lerp progress) crossed 1 — she'd touch down and start talking with
        zero beat to register a pigeon had even landed. Added a 0.85s
        settle pause (folded wings, small idle bob) between landing and the
        letter conversation actually starting.
      - **Testing gotcha worth keeping**: this round's browser tests kept
        reading `document.documentElement.outerHTML` to confirm a fresh
        reload actually picked up the latest edit before trusting any
        result — the local dev-server tab silently served a stale cached
        copy more than once mid-session despite repeated `navigate()` calls
        to the same URL; only a brand new tab (`tabs_create` + navigate)
        reliably picked up new bytes. Separately, real-wall-clock-gated
        things (the birthday card's `setInterval` typewriter, and this
        round's new messenger settle timer while testing via `waitFor`)
        crawled far slower than requested with multiple background tabs
        open — closing the unused ones and switching dt-gated checks to
        `pump()` instead of `waitFor` resolved it; `requestAnimationFrame`-
        driven game state apparently throttles hard in a backgrounded tab
        even when plain `setTimeout` in the same tab still fires close to
        on-time.
- [x] Garden flowers sway away from Beanie as she walks by (2026-07-16):
      Bred asked (2026-07-15, explicitly deferred to a later pass) for the
      flower field to bend away from Beanie "like how a person would walk by a
      flower field," then spring back once she's passed — a gentle bow-wave
      parting around her, not an instant snap. The hard part was never the
      look; it was doing it without wrecking the framerate. The Garden field is
      ~35k instanced stems plus ~35k instanced heads (tulips, daisies, roses,
      hydrangea puffs, calla lilies), every one of them a STATIC pre-baked
      transform matrix written exactly once at build time. Re-writing all of
      them every frame — the naive reading of "make the flowers move" — would
      have meant rebuilding ~90k matrices and re-uploading megabytes of
      instance buffers 60 times a second, for flowers she can't even see. So
      the whole feature is built around only ever touching the handful within
      arm's reach of her.
      - **Spatial bucketing, radius-limited updates**: at build time each
        flower's foot is dropped into a coarse 3D grid keyed on its rounded
        local position (cell size 4 world units). Each frame the animator looks
        up only the 3×3×3 cells around her current position — a few dozen
        candidate flowers — instead of scanning the field. A flower within
        `SWAY_RADIUS` (3.6u) gets a target lean whose magnitude falls off by
        smoothstep with distance; everything else is ignored. The cell size is
        deliberately larger than the radius so the 3×3×3 neighbourhood is
        guaranteed to contain every flower that could possibly be in range.
      - **Rigid stem+head bending**: `heads()` pops build-time spots in reverse
        order, so a stem's instance index has NO relation to its petal/centre
        indices — there was no way to bend a flower as a unit without first
        recording, per flower, every instanced-mesh part that shares its base
        point. Added an `allFlowers` registry doing exactly that. Each part
        bends by the SAME tilt quaternion about the SAME foot pivot (the tilt
        axis is `surfaceNormal × away-from-her`, so the flower tips directly
        away from her along the ground), and the head's radial offset is
        rotated by that tilt too so it stays planted on top of its stem instead
        of sliding off.
      - **Spring in AND out, with a tiny active set**: the applied bend eases
        toward its target with `cur += (target-cur)*(1-exp(-k·dt))`, so it
        bows in and springs back smoothly rather than snapping. Flowers she has
        walked past can't spring back if we've stopped looking at them, so any
        flower with a non-zero bend stays in a small `active` set: each frame
        their targets decay to zero, they keep integrating toward upright, and
        the instant they settle we write their exact rest matrix one last time
        and drop them from the set. When she stands still in open ground the
        set drains to empty and the per-frame cost is essentially nothing.
      - **Instance buffers flagged only when touched**: only the instanced
        meshes that actually had an instance rewritten this frame get their
        `instanceMatrix.needsUpdate` set (via a per-frame `touched` set), and
        all field buffers are marked `DynamicDrawUsage`. Standing idle uploads
        nothing at all; walking uploads only the flower-type buffers she's
        currently brushing through.
      - **The couch-ring bed** (84 real non-instanced `Group` flowers) gets the
        same treatment far more cheaply — all 84 processed every frame in the
        couch's own local frame, no grid needed.
      - **Verification**: driven headlessly via `pump()` in the Garden. Probed
        the raw instance matrices as she walked ~21 units: nearby stems bent
        0.6–0.9 rad (heads tipping ~35–52° away from her), flowers beyond the
        radius stayed at exactly 0, and a full-field scan for "stuck" bent
        flowers behind her read 0 at every step and after she stopped —
        confirming the spring-back never leaves a trail of flattened flowers.
        The couch bed showed the same signature (bent-count rising near her,
        falling back to baseline once she left). No console errors.
- [x] Large batch: landing-camera polish, per-world navigation/content fixes,
      weightier movement, footprints, night-sky detail, and Beanie's own
      dialogue lines (2026-07-15, later still same day): one big combined
      request covering nearly every world in the game — landing-camera zoom/
      glare/rotation, more evenly-spread Main Stacks book piles plus a real
      2x-tall landmark tower, Chippy always facing her, the "notice" cutscene
      only ever firing once across ALL pigeons instead of per-pigeon, bbak
      sinking into his own snow pile, walking through (not over) snow piles,
      a proper two-act 10s cucumber-reveal cutscene with a post-reveal
      mission update, Doodles/decoy pigeons landing absurdly far away, a
      Pigeon-Plaza landing cutscene where nearby pigeons flee, tighter
      dialogue box sizing, a stamp sound+ring effect on the sticker toast, a
      slower/heavier food-toss animation, slower walk speed and camera drag
      sensitivity with a per-step camera "punch," temporary footprints,
      shooting stars and constellations, and giving Beanie her own lines in
      conversations instead of only ever listening.
      - **Landing camera**: the reference "close diagonal, head bottom-left"
        shot got a genuine 90°-CCW roll — a first attempt rotated her raw
        body-up directly around the view axis and measured ~53° instead of
        90° (her body-up wasn't perpendicular to the view axis to begin with,
        so any parallel component just didn't rotate); fixed by projecting
        out that parallel component FIRST to get a true perpendicular "0°"
        reference, then rotating exactly 90° from there. **While chasing
        this, found `landingDebug()`'s own `camUp` field was reading a stale
        module-level scratch vector (shared with `followCam`/`updateTalkCam`),
        not the actual `camera.up` — it never reflected this code's own
        changes at all, and every earlier numeric check against it was
        silently checking the wrong thing.** Added `camActualUp`/`screenUp`
        (derived from `camera.quaternion` directly) to verify against instead.
        Also confirmed live that the pose read as a flat vertical stand
        rather than diagonal at t=3s into the clip specifically because by
        then she's already mostly stood back up — the intended dramatic
        diagonal reads clearly earlier in the same clip, right as she's
        actually sprawled from the fall.
      - **Chippy always faces her**: his whole seated group's orientation is
        a hand-tuned "face the landing spot" pose (`orientToNormal` + a fixed
        `rotateY`) that the generic per-conversation auto-face logic
        deliberately skips, since re-deriving it from her CURRENT position/up
        would un-seat him. Instead, only his loaded MODEL (a child of the
        seated group, so the seat itself never moves) gets a heading-only
        rotation each frame, computed as a DELTA from his own known-good
        default facing rather than rebuilt from scratch — sidesteps ever
        needing to know his model's raw-front offset. Verified via a new
        `teleportNearWorldPos(pos, angle, azimuth)` debug helper (teleport +
        face a point from an arbitrary angle, for testing NPC-facing without
        fighting maze pathing) across 4 different approach angles: consistent
        ~0.86 dot product toward her every time, vs. wildly different numbers
        before the fix.
      - **"Notice" cutscene only fired once, ever**: its dedup key was
        `curI + guideLabel`, but every Pigeon Plaza decoy shares the
        identical generic label ("say hello to that pigeon") — so only the
        very FIRST decoy she ever approached got the "should go talk to them"
        beat; the 2nd through 8th (each a genuinely new character) silently
        never did. Fixed by keying on the target's actual position too.
      - **bbak buried in his own snow pile**: he was placed at a hand-picked
        offset (`radius*0.32`) with no relation to the mound's real height,
        and the mound's height was itself randomized on top of that — so he
        ended up genuinely buried past his shoulders about as often as not.
        Now his placement is derived directly from the mound's own known
        peak height (lift + radius*yScale), minus a small intentional sink so
        he still reads as resting IN the snow rather than floating above it.
      - **Walking on snow piles**: her position was always `bodyCenter +
        up*R` — a fixed radius with zero awareness of decorative terrain.
        Snow piles are now recorded (direction, angular footprint, peak
        height) in an array; `updatePose()` checks her current direction
        against every recorded pile and adds a smooth dome-shaped height
        bump when she's within one's footprint, so she now genuinely climbs
        onto them like real hills. Confirmed live: ~1.47 of a possible ~1.9
        units of rise while approaching bbak's own (widest) pile.
      - **Doodles/decoy pigeons landing absurdly far away**: `spawnStoryPigeon`
        (used for all 8 decoys AND Doodles) placed them via `dirNear(plazaN,
        0.7 + rand*1.5)` — `dirNear` doesn't reliably control angular distance
        at spreads this large, and even at face value that's up to ~126° from
        the plaza center on this small planet. Confirmed live: Doodles landed
        ~108° of arc away, a genuinely long walk through 520 background
        pigeons with only a compass to go on. Switched to `tiltDir` (exact,
        bounded angular distance every time) with a much tighter 0.35-0.75
        rad range.
      - **Cucumber reveal cutscene**: rebuilt as two acts, 10s total (the
        requested minimum) instead of one continuous 7s establishing orbit.
        Act 1 (0-5s): a close, ground-level POV — genuinely different from
        every other cutscene's wide orbit — watching the ring's solid-to-
        cucumber crossfade AND the ground cucumbers sprouting, kept coupled
        to start at the same moment since both read from the same shared
        `cucumberMat` (ground cucumbers are clones of the same loaded model)
        — starting them at different times would make whichever finishes
        first blink as the other's opacity ramp reset the shared material
        out from under it. Act 2 (5-10s): a close pass alongside just the
        ring band itself (not the whole planet), showing off the now-fully-
        cucumber result up close. Also fixed `arrive()` falling straight back
        to the generic "find bbak and talk to him" introMission every time
        this cutscene's own title-reveal re-triggers that same arrival path —
        now checks `bbakQuest.cukeRevealed` first and sets the real "bring
        bbak a cucumber" mission instead.
      - **Pigeon Plaza landing**: nearby ground pigeons now scatter outward
        on impact (fleeing, not permanently removed like Percy's departure
        scatter — she's arriving, not leaving) and resettle a few seconds
        later; any CONTINUOUSLY-FLYING pigeon within a tight safety radius of
        her exact landing point gets briefly hidden, since those follow
        independent orbits with zero awareness of where she's about to touch
        down and could otherwise clip straight through her.
      - **Movement feel**: walk speed down ~30% (12.0 -> 8.5), drag/wheel
        look sensitivity down ~30%, and a small decaying downward camera
        "punch" set on each footstep (consumed once per frame in `followCam`)
        — no dedicated bob animation needed, just real per-step weight.
      - **Dialogue can now include Beanie's own lines**: `startDialog`'s
        `lines` array can mix plain strings (unchanged, spoken by the
        conversation's one `opts.speaker`, exactly as before) with
        `{ speaker, text }` objects for a line-specific override — fully
        backward compatible with every existing conversation. Woven into the
        Chicago letter, Chippy, bbak, and Percy's intro/reunion beats so she
        actually participates instead of only ever listening. Verified live:
        the speaker name in the dialogue box correctly alternates line-by-
        line between the NPC and "Rachel 💫".
      - **Not fixed — needs Blender, not code**: Summer Beanie's hand resting
        on her back mid-walk is baked into the exported walk-cycle animation
        itself (`Summer beanie/Summer_walk.blend`), not anything index.html
        controls. Checked for a live Blender MCP connection to fix it
        directly; none was available this session (`Could not connect to
        Blender — make sure the addon is running`). Needs the same kind of
        pass as the Talking-pose retargeting work elsewhere in this file, the
        next time Blender is actually connected. **Re-confirmed live and
        still present** after the parallel session's same-day belly-
        deformation fix (commit `1427494`): forced `summerWalkWeight` to 1 via
        `goto(4)` + real `ArrowUp` key dispatch (her Walk action doesn't
        engage through `turnStep`/teleport helpers, only through the real
        input path), then visually inspected across multiple walk frames — a
        skin-toned mass (her hand/forearm) sits fixed against the same spot
        on her mid-lower back every frame, not swinging like a real arm-swing
        would. This is a DIFFERENT bug from commit `1427494`'s belly fix
        (that was ~450 waist/hem vertices mis-weighted to Spine/Hips/thigh —
        a weight-painting discontinuity; this looks like the right arm chain
        itself is posed behind her back in the Walk action, not stretched
        there by bad weights) — fixing one did not fix the other. Still
        needs its own Blender pass on `Summer_RIGGED.blend`'s Walk action.
- [x] Dialogue typewriter sped up 2x and de-jankified; Chicago messenger
      cutscene + fixed mission chip popping up mid-conversation
      (2026-07-15, later same day): asked to make the dialogue typewriter
      "2 times faster and smoother... rn its so laggy," for the Chicago
      mission to appear only after the pigeon conversation (it wasn't), and
      for a short cutscene before that pigeon first talks to her — idle,
      then a pigeon lands in front of her with a letter in its mouth.
      - The dialogue typewriter was a per-character `setInterval` (22ms/
        char) — competing with the rAF render loop for the JS thread reveals
        characters in uneven bursts under any load, which reads as
        stuttery/laggy rather than a smooth type-on, independent of speed.
        Replaced with a dt-driven reveal (`dialog.lineT` accumulated in the
        same per-frame `step(dt)` that already drives everything else, at
        half the per-character duration = 2x speed) — same mechanism `pump()`
        already advances for every other animation, so this is also now
        directly testable via `pump()` instead of needing real timer waits.
      - Traced the mission-chip-showing-too-early complaint to last round's
        own blanket cutscene-hide rule: `missionEl.classList.toggle('hidden',
        isCutsceneState)` force-*removed* 'hidden' every single frame outside
        a cutscene state — including `state==='talk'`. Chicago's messenger
        conversation runs in `state==='talk'`, so the very first frame after
        it started silently undid `startJourney()`'s own explicit "keep this
        hidden until the letter is read" gate — confirmed live via a step-by-
        step trace (`missionHidden` flips to `false` within the first
        `pump()` after the conversation begins, mission text already fully
        typed out in the background despite being invisible the whole time
        beforehand). Changed the blanket rule to only ever *add* 'hidden'
        during a cutscene, never remove it — revealing the mission stays each
        caller's own explicit job (`setMission()`/`arrive()` already do this
        correctly at the end of every world's arrival). Verified the full
        sequence live: mission stays hidden through the entire letter
        conversation AND the orbit/title cutscene afterward, appearing only
        once she's back in normal control — and checked every other cutscene-
        ending path (cukeReveal → landing → arrive(), percyfly → arriveGarden
        → arrive(), the non-click-gated Garden flash-title) already reveals
        the mission explicitly on its own, so none of them regressed.
      - Added the requested cutscene: the messenger pigeon now carries a
        small folded-letter prop (a simple box + a colored "wax seal"
        cylinder) clamped in its beak, and the whole ~950ms-wait + ~1.15s-
        swoop-in approach now gets its own two-shot camera (same side-offset
        composition `updateTalkCam` already uses for conversations, just
        with a taller/farther-back floor since the pigeon starts far higher
        above the surface than any conversation partner ever stands) instead
        of holding the very first static camera snapshot through the whole
        beat. She was already guaranteed to stand in idle pose throughout
        (`introLocked` already freezes movement) — the gap was purely that
        the camera never followed the pigeon's entrance. Verified live via
        screenshots across the sequence: a wide idle establishing shot before
        the pigeon spawns, both her and the descending pigeon in frame
        together as it swoops down, and the landed pigeon reading the letter.
- [x] Landing camera: close diagonal shot, fixed clipping into her own face,
      and stopped the bigger dust cloud from hiding her the whole time
      (2026-07-15): user sent a reference screenshot asking for the
      just-landed camera to be "this close and her body shown diagonally
      with her head facing bottom left," alongside a separate ask to make
      the landing dust cloud "slower, smoother, and a much bigger cloud
      that rumbles more."
      - The first diagonal-camera attempt used `+fwd` to offset the camera
        from her position, which put the camera directly in front of her
        face — the codebase's own `followCam` always negates `fwd` first
        (`cA.copy(fwd).multiplyScalar(-1)`) to sit behind her; using the
        opposite sign here is what caused the clipping. Fixed by matching
        that convention.
      - With that fixed, a live screenshot at the moment of impact still
        showed nothing but a wall of pale round shapes — traced via a
        temporary scene-traversal debug accessor to `spawnLandingDustBurst`'s
        own puffs (confirmed by exact color match, `0xd6cdbc`), not snow or
        any other decor. The dust cloud's own sizing was bumped way up this
        same round (up to 5.6x scale, 42-56 puffs) per the "much bigger
        cloud" ask, and a camera sitting only ~4 units from her spawn point
        was consistently inside that cloud for the first 1-2+ seconds of its
        life — confirmed live that she was still almost entirely hidden
        behind puffs at landing.t=1.6s.
      - Rather than shrinking the cloud back down (it was sized that way on
        request), eased the camera in from a wide establishing distance
        (~9 units, reads as "the big dust cloud swallows her on impact")
        down to the close diagonal framing (~4 units) over 1.6s — timed to
        land right around when the puffs have traveled clear of her.
        Verified via screenshots across the whole fallgetup phase (impact,
        mid-ease, settled-close, standing-up, transition to orbit): dust
        reads as an atmospheric settling cloud in the background instead of
        an opaque wall, and she's clearly visible in the diagonal pose
        throughout.
      - Also gave Cucumber Meadow's decorative snow piles (separately made
        much bigger/wider this round, up to radius 3) a keep-clear zone
        around her actual fixed landing spot, same pattern as the Book
        Stacks maze's `LAND_CLEAR` — 70 of them scattered fully at random
        on a small planet made a pile landing on top of her arrival point
        a real (if intermittent) risk, independent of the dust issue above.
- [x] Cucumber Meadow feeding quest polish: fixed pizza model, added more
      food variety, wider snow mounds, and a proper cucumber-ring reveal
      cutscene (2026-07-15): several related asks in the same batch — pizza
      "all separated again," not enough food options ("makes the gameplay
      take too long"), snow piles should be bigger and not flat circles, and
      the cucumber-ring reveal should show the ring actually turning into
      ground cucumbers over ~3 seconds, with cucumbers then pickable nearby
      and a cutscene of them forming on the ground.
      - Pizza: the crust `TorusGeometry` used `rotation.x = Math.PI/2` while
        the slice `CircleGeometry` used the opposite sign — a mirror-image
        azimuth mapping that put the crust arc on the wrong side of the
        wedge. Fixed by matching signs; confirmed live (walked her up to a
        spawned slice, screenshotted) that it now reads as one continuous
        piece, and that its existing spin animation plays correctly on the
        fixed geometry.
      - Added popsicle/watermelon/hotdog/sushi to the pickup-food rotation
        (was 6 types/6 instances, now 10 types/14 instances) so a wrong-food
        try is never far away.
      - Snow patches are now lumpy squashed-sphere mounds instead of flat
        circles, sized up (background patches 1.3-3.0 radius, bbak's own
        patch 3.4) — see the landing-camera entry above for the keep-clear
        fix this required.
      - Cucumber reveal: rewrote as a genuine crossfade — the always-present
        solid ring fades out while the real cucumber-band ring (sharing the
        same material, so animating its opacity affects every instance at
        once) fades in over 3 seconds, then ground cucumbers individually
        grow in with a per-cucumber random delay + ease-out scale-in. She
        can pick up any ground cucumber near her once revealed, not just a
        single designated one.
      - Picking up any food now immediately redirects the "next" guide/
        locator to bbak ("take it back to bbak") regardless of which food
        she grabbed — confirmed this was already wired correctly
        (`refreshBbakGuide`'s `bbakQuest.holding` branch runs on every
        pickup), so no change needed there, just verified it holds for the
        new food types too.
- [x] Cutscene and conversation polish: mission box hidden during every
      cutscene, Chippy's book pile now part of him, bigger achievement-stamp
      sticker toast, bbak toss happens in conversation mode
      (2026-07-15): batch of smaller asks — Chippy's book pile still showing
      disconnected behind him mid-conversation, the Meadow mission box
      revealing the exact objective before meeting bbak instead of just
      pointing to him, the friend-sticker toast cropping the sticker image,
      and the food-toss-to-bbak not being staged as part of the conversation.
      - Chippy's seat was a sibling object in the world group, not a child
        of Chippy's own Object3D, so `hideNearbyObstacles()` (which only
        exempts the NPC object itself, not nearby-but-unrelated objects) was
        hiding it during talk. Fixed by truly re-parenting the seat onto
        Chippy with compensating local rotation/position so its world
        transform is unchanged.
      - Broadened the existing cutscene mission-hiding rule to cover every
        cutscene state (`intro`, `fly`, `landing`, `percyfly`, `finale`,
        `cukeReveal`) in one place, and gated the Meadow's landing mission
        text behind actually meeting bbak, showing only "find bbak" first.
      - Sticker toast image grew 40px -> 70px with `object-fit: contain` (was
        cropping) and a forced-reflow-restarted "stamp" keyframe animation
        (scale/rotate overshoot settling in) so it reads as an achievement
        stamp landing on the notification.
      - `talkBbak()` now enters `state='talk'` (camera + hidden obstacles)
        before playing the toss animation, so the whole exchange reads as
        one continuous conversation instead of a walk-up toss followed by a
        separate dialogue cut.
- [x] Pigeon Plaza density, aim-lock softlock, and QA shortcuts
      (2026-07-15): asked for roughly double the pigeons with more flying
      continuously, plus a QA shortcut to progressively hand off quest items
      (press P: book to Chippy, another book, food to bbak, etc.) for faster
      testing, and separately that jumping from Cucumber Meadow onward was
      "hard to find."
      - Pigeon count 260 -> 520, continuously-flying subset 18 -> 42.
      - Added a `P` keydown handler (`qaGiveNext()`) that advances whichever
        of the books/bbak quests is currently active by one step per press.
      - The Cucumber Meadow -> Pigeon Plaza jump turned out to be not just
        "hard" but genuinely unlockable at any camera angle: `updateAim()`'s
        aim-lock had a hardcoded `surf < 800` distance cap left over from
        before an earlier repositioning of Cucumber Meadow this same
        session, and the actual inter-world distance had since grown past
        it (~936-903 depending on approach angle, confirmed live via the
        aim debug's `targetDistance`). Raised the cap to 1000 — verified via
        a full pitch/yaw aim sweep that it now locks on.
      - Also found and fixed an unrelated bridge-command bug while verifying
        the new talking-pose animation (a separate in-progress effort this
        session): the QA `talk()` shortcut called a nonexistent
        `startTalk()`; it now mirrors the real keydown handler's NPC-
        proximity dispatch (Chippy -> bbak -> plaza pigeon -> Percy) so it
        actually engages a conversation with whichever NPC she's near.
- [x] Talking pose: fixed the actually-broken elbow, raised into a real
      explaining gesture (2026-07-15, later still same day): user sent 3
      reference images (an in-game screenshot plus a robot-figure render and
      its skeleton, both showing arms raised with elbows bent upward) and
      asked "why are her elbows bent inside out?? make it bend upwards."
      - **This was a real bug, not a style preference — the two previous
        rounds' elbow bend used the wrong local rotation axis for the
        joint's hinge.** Confirmed by rendering the elbow bent 75° on all 4
        candidate axis/sign combinations and comparing: local +X on
        `LowerArm` produces a clean bicep-curl-style bend (hand rises
        straight up past the shoulder); the axis used in both previous
        rounds (`LowerArm` local Z) instead swings the forearm sideways and
        across the body, which is what actually reads as broken/"inside
        out" — not a subtle judgment call, one look at the 4 renders side
        by side made it obvious which was right.
      - **Redesigned the pose shape to match the reference**: arms raised to
        roughly shoulder height and spread outward (well above the previous
        "reach forward" pose's height), elbows bent upward through the
        confirmed-correct axis so both hands land near shoulder/face height
        — a real "explaining/presenting with your hands" shape, much more
        visually active than the earlier low, subtle reach. Re-targeted
        onto the existing keyframes the same way as the previous round
        (compose the net rotation needed on top of what's already there),
        so the gesture's original timing and wiggle carried over unchanged
        — only WHERE the arms end up changed, not WHEN they move.
      - Verified via renders at start/mid/settle-tail frames (all
        consistent — no jarring difference between the peak gesture and the
        end pose) and a live in-game screenshot. **Learned from the last
        round's deployment-check false positive**: this export also landed
        on the same byte count as the previous one, so verified the actual
        SHA-256 content hash against the live site instead of trusting
        size, and confirmed genuinely deployed (took 5 polls / ~100s this
        time, not just 1).
- [x] Talking pose re-tuned: relaxed shoulders, straight forward reach
      (2026-07-15, later still same day): the scarecrow-arms fix above still
      wasn't quite right — user said her shoulders looked "awkwardly lifted"
      and her elbows were bent more than they needed to be; wanted arms kept
      straight while still reaching forward.
      - **Recomputed the SAME gesture's timing/wiggle, re-targeted to a new
        base pose**, rather than re-authoring from scratch: mathematically
        undid the previous offset and applied a new one in one step (`net =
        new_offset @ old_offset.inverted()`, composed directly onto the
        already-once-offset keyframes) — avoids any risk of drifting back
        toward the original raw-bind-pose wiggle by mistake.
      - **Shoulder height brought back down close to her actual Idle hang
        angle** (was noticeably more raised than Idle in the first pass —
        that's exactly what read as "awkwardly lifted"), while the forward
        swing increased so the reach itself stays strong. **Elbow bend cut
        way down**, from a real bend to barely more than Idle's own natural
        slight bend — reads as a straight arm now, not a curled one.
      - Verified via renders at 4 points through the gesture (all
        consistent: relaxed shoulder, straight-ish arm, hand out front) and
        a live in-game screenshot at a larger resolution than the previous
        round's check, which made the silhouette much easier to judge.
      - **Deployment-verification gotcha hit while confirming this shipped**:
        this export happened to come out the exact same byte SIZE as the
        previous (different) export, so the usual "does local size match
        remote size" poll gave a false positive before GitHub Pages had
        actually updated. Switched to comparing a SHA-256 hash of the full
        file content instead of just size — caught that the CDN was still
        serving the previous version for ~60s longer than the size-only
        check would have reported. Worth using a content hash instead of
        size for this kind of check going forward whenever two consecutive
        exports could plausibly land on the same byte count.
- [x] Talking pose "scarecrow arms" fix (2026-07-15, later still same day):
      user saw the newly-wired Talking animation live and said her arms bend
      "a bit forward" was needed — "shes standing like a scarecrow."
      - **Root cause: the gesture was authored as a few-degree wiggle around
        the rig's raw T-pose bind pose, not around her relaxed standing
        pose.** At full animation weight that reads as arms held straight
        out to the sides — a real scarecrow/T-pose silhouette — since the
        "gesture" was only ever a small perturbation on top of a pose she
        never actually holds during normal gameplay.
      - **Found the correct fix axis by measuring, not guessing**: rotated
        `UpperArm.L` a test angle around each of its 3 local axes and
        measured which one actually moved `Hand.L`'s world position toward
        her facing direction (-Y, per the established Winter-faces- -Y
        convention) — local Z turned out to be the forward-swing axis
        (negative = forward), local X the up/down swing, local Y just a
        twist/roll with no effect on hand position. Repeated for the elbow
        (`LowerArm.L`) with the shoulder already swung forward, since a
        child bone's effective bend direction depends on its parent's
        current orientation.
      - **Composed a forward-and-down offset onto every existing keyframe**
        of both arms (shoulder swing + elbow bend, mirrored L/R matching
        the rig's established sign convention) rather than replacing the
        animation — this preserves the original gesture's timing and subtle
        wiggle, just repositioned so it reads as talking with her hands
        instead of holding a T-pose. Verified via direct render at 4 points
        across the clip (early gesture, mid, late, and the settle-to-idle
        tail) — arms clearly bent forward with a visible gap from the
        torso at every one, no self-clipping.
      - **Two more Blender export mechanics discovered while re-shipping
        this**: (1) after hiding two objects to isolate a render, forgot to
        un-hide them before the SUBSEQUENT export — `hide_render` silently
        drops an object from `use_selection=True` export even while
        `select_set(True)`, producing a valid-looking but nearly-empty
        132-byte glb with zero warning; (2) this export's node names came
        out WITH dots (`UpperArm.L`) instead of the previous export's
        sanitized no-dot names (`UpperArmL`) — confirmed harmless (glTF
        animation channels bind by node INDEX, not name string, and
        `grep`-confirmed the game's own code never references a bone by
        exact name string anywhere), but worth knowing this can vary
        between export sessions.
      - Re-verified live end-to-end via the local dev server (bbak
        conversation, real screenshot) and via direct parsing of the
        exported glb's own animation sampler data. Zero console errors
        related to Beanie/animation (one unrelated pre-existing pigeon-
        asset fetch error noted, out of scope for this fix).
- [x] Winter Beanie's Talking pose wired into real conversations (2026-07-15,
      later still same day): user asked to have the Talking animation (built
      earlier this session, previously only shown in Blender preview GIFs)
      actually play in-game whenever she's talking to a character.
      - **`game-assets/beanie/beanie.glb` gained a 7th animation.** Imported
        the live glb fresh (glTF import, not FBX — the FBX importer is the
        one that crashes the Blender MCP bridge; glTF import turned out
        safe), appended the `Talking` action authored earlier, and re-
        exported with all 7 clips (Idle/Walk/JumpLaunch/JumpSoar/JumpLand/
        LandFallGetUp/Talking) intact — deliberately did NOT rebuild from
        the various individual source .blend files (idle/walk/jump each
        live in their own file, and the jump/landing clips were originally
        hand-extracted-and-retimed frame ranges, not simple named actions),
        since re-deriving those risked subtly regressing already-shipped,
        already-tuned animations. Backed up the pre-change glb first.
      - **Two real Blender export bugs found and fixed along the way:**
        (1) a freshly-appended action assigned only via `.action = clip`
        silently failed to export — Blender 5.1's slotted-actions system
        also needs `.action_slot` explicitly bound, or the action evaluates
        to a frozen, unchanging pose despite correct weight/time (traced by
        comparing the SAME bone's rotation at multiple frames via the
        properly-evaluated depsgraph and finding them bit-for-bit
        identical); (2) even with a correctly-slotted NLA strip, the
        exporter's default `export_animation_mode='ACTIONS'` still
        exported a frozen Talking clip — switching to
        `export_animation_mode='NLA_TRACKS'` (samples each NLA track
        directly instead of internally reassigning `.action`) fixed it.
        Verified by parsing the exported glb's raw animation sampler data
        directly (not a re-import): Spine's rotation channel showed 97 real
        keyframes sweeping through the gesture and settling back to
        identity at the end, not a static repeated value.
      - **`animBeanieSkinned()` now blends a 3-way Idle/Walk/Talk crossfade**
        instead of just Idle/Walk — `state==='talk'` (and Winter only;
        Summer has no Talking clip yet) fades Talk in and Idle out, matching
        the existing `dt*8` blend rate used everywhere else. `startDialog()`
        resets and replays the Talking action fresh every time a new
        conversation begins (works for every NPC and the Chicago letter
        scene alike, since they all share this one function) — a LoopOnce
        clip that settles into an idle-like pose by design, so a
        longer-than-4s conversation just holds a calm settled pose rather
        than jarringly snapping back to the gesture's start.
      - **Closed a real gap this surfaced**: `jumpTo()` and
        `updateLandingAnim()` already explicitly zero Idle/Walk/Run weights
        at the start of a leap/landing (to prevent any bleed-through), but
        had no idea `herTalkAction` existed yet — added the same
        `setEffectiveWeight(0)` line for it in both places, closing a
        possible residual-Talk-pose-bleed edge case if a jump ever starts
        while a talk-fade is still mid-transition.
      - Verified live end-to-end via the local dev server: a real bbak
        conversation shows the Spine/Chest/Head/arm bones visibly posing
        differently at 3 separate points through the gesture (not just the
        blend weight changing over an unchanged pose), correctly fades back
        to Idle when the conversation ends, and a full jump→flight→landing
        cycle immediately after shows `talkWeight` pinned at 0 throughout.
        Zero console errors.
- [x] Dense polar maze rebuild, bigger Main Stacks, next-jump compass hint
      (2026-07-15, later still same day): user sent a Main Stacks title-card
      screenshot showing the maze looking sparse/empty ("where did all of
      the books go?? ... i need many many tall piles of books that make it
      a maze type feel"), plus asked to make Main Stacks look bigger from
      Chicago and to add a hint for which planet to jump to next ("헷갈려" —
      confusing).
      - **Root cause of the sparse look**: the previous maze (4 concentric
        rings, each with independently-random gaps — see the "Gift books
        away from Chippy" entry below) leaves the space BETWEEN rings
        completely bare by construction (nothing is ever placed in the
        moats), which is exactly what makes a straight-line approach always
        findable, but also reads as empty/sparse rather than a labyrinth.
      - **Rebuilt as a proper polar maze**: an 8-ring x 16-sector grid around
        Chippy, connected via randomized depth-first search (recursive
        backtracking) — the identical algorithm any textbook Cartesian maze
        generator uses, just walked in (ring, sector) space instead of
        (row, col). This guarantees full connectivity BY CONSTRUCTION (a
        spanning tree is always fully connected), so walls can fill nearly
        every remaining boundary — 113-127 tall stacks (6-10 books each),
        more than double the old ~49 — with zero risk of ever sealing off
        the path to Chippy, unlike independent-per-ring gaps which only
        happened to be probably solvable.
      - **Verification had a real, hard-won lesson.** The first version of
        this rebuild had a genuine bug: wall footprint sizing didn't account
        for Beanie's own collision buffer (`isBlocked()` adds
        `HER_FOOTPRINT/R` on top of every collider's own radius) on top of
        the tightest (innermost-ring) spacing, leaving ~0 margin and
        actually trapping her — confirmed live (`blockedSteps` at/near
        every step, in every tested direction). Fixed by widening the
        innermost ring radius and shrinking the wall footprint with the
        buffer properly included. But naive empirical retesting (walking a
        single randomly-explored path with a greedy seek-and-skirt script)
        kept "failing" even after that fix — traced entirely to test-script
        issues, not the maze: `goto()` faces her toward the NEXT chain body
        (Cucumber Meadow) on arrival, not toward the maze, so a large
        initial heading error made a naive turn+step-every-iteration script
        arc away from the target instead of turning in place first; and
        loose convergence thresholds let small positional drift compound
        over a long path. **The verification that actually settled it**:
        exposed the maze's exact open/closed graph via a new
        `mazeDebug()` debug method, then exhaustively checked EVERY one of
        the ~127 "open" edges (not just one explored path) by sampling
        points along the straight line between each pair of adjacent cell
        centers and testing against every collider in the scene — 0 false
        blocks out of 127 open edges, confirmed across 3 independent fresh
        reloads (each with a new random maze). This is a strictly stronger
        proof than "a wall-following script happened to reach the center
        once" — every intended passage is provably walkable, not just the
        one path that got tried.
      - **Main Stacks pulled closer to Chicago**: distance reduced to 65% of
        its previous value (same direction, so no other angular relationship
        changes) so it reads as noticeably bigger/closer in the default
        view instead of a small dot next to Cucumber Meadow's much bigger,
        brighter ring.
      - **"Jump to next world" compass hint added**: the existing on-planet
        guide-arrow mechanism (previously only active for "go find this NPC"
        tasks) now also activates once a world's mission is done and it has
        a `chainNext`, pointing at the next body's direction with a
        "🚀 jump to `<emoji> <name>`" label — covers every leg in the game,
        not just a one-off Chicago fix, directly answering "which planet do
        I jump to next."
- [x] Landing-cover bug, title screen cleanup, journal reset + book redesign
      (2026-07-15, later still same day): user sent two screenshots — a large
      gift book floating directly over Beanie's head during the Main Stacks
      landing cutscene, and the title screen with its subtitle/controls text.
      Four requests:
      - **Gift book covering her during landing, root-caused and fixed the
        same way as the earlier grand-stack softlock**: gift books placed
        via `dirNear(chippyN, spread)` with no clearance check against
        `landN` — `dirNear` doesn't reliably control angular distance at
        this spread, so a book could land right on her own landing spot.
        Switched to `tiltDir(chippyN, giftAngle, randomAzimuth)` with a
        reroll-until-clear-of-landN loop, matching the grand stack's fix
        exactly. **Also added a general safeguard**, not just a one-off
        patch: `startLandingSequence()` now calls the same
        `hideNearbyObstacles(null)` conversations already use to declutter
        props near her, restored in `arrive()` once the cutscene concludes —
        so no future decorative object placed near any world's landing spot
        can ever cover her during a fall/get-up + orbit/title beat again.
        Verified clean across 3 fresh reloads (gift book placement is
        randomized each load) by pumping into the landing sequence and
        screenshotting the close-up fall/get-up frames directly.
      - **Title screen simplified**: removed the "a tiny journey…" subtitle
        and the "arrow keys walk…" controls line entirely (that control hint
        is already re-taught in-game via the idle `#hint` chip) — kept only
        "press SPACE to start", enlarged (16-21px → 22-34px clamp, weight
        600→700) and switched its pulse animation from a plain opacity fade
        to an actual glow pulse (animating `text-shadow` blur/spread between
        two states) for real prominence.
      - **Journal/sticker diary no longer persists across reloads.** It was
        the only `localStorage` usage in the entire file
        (`beanieMetFriends`) — removed both the read-on-load and the
        write-on-meet entirely (not just disabled) so a fresh page load
        always starts at 0/12 friends met, confirmed live by earning
        Chippy's sticker then reloading and checking the count reset.
      - **Journal rebuilt to open like a book** (two pages hinged at a
        central spine) instead of a single flat modal card: `#journalPage`
        left/right each start folded flat against the spine
        (`rotateY(±100deg)`, `transform-origin` on the spine-side edge) and
        swing open to `rotateY(0)` when `.show` is added, with `perspective`
        on the book container making the rotation read as a real page-turn
        in 3D. Title/count/first 6 stickers on the left page, remaining 6
        stickers + close button on the right. Hit and fixed two follow-on
        layout bugs during verification: the right page's flex-column
        parent (needed to pin the close button to the bottom) used
        `align-items:center`, which shrank its sticker grid to almost
        nothing next to the left page's normally-sized one — fixed via
        `align-items:stretch` + explicit `width:100%` on the grid; and the
        sticker cells themselves were sized by `1fr` columns filling a full
        page width (~168px each), which made 3 rows overflow the book's
        height entirely, hiding the close button below an invisible
        scroll — fixed by capping cell size with
        `clamp(64px,9vw,92px)` columns instead of `1fr`.
- [x] Main Stacks findable from Chicago by default (2026-07-15, later still
      same day): user reported "why can't i find mainstacks from chicago???
      where is beanie supposed to go??? it should be the planet that looks
      closest to chicago." The parallel session's re-facing fix (see the
      Summer Beanie entry below — Beanie now faces `chainNext` again after
      the letter dialogue) fixed HER raw body orientation, but live-testing
      the full intro→letter→cutscene flow afterward still showed the
      default settled view containing Cucumber Meadow prominently and NO
      trace of Main Stacks anywhere in frame.
      - **Root cause: `arrive()`'s generic post-cutscene `camPitch = 0.3`
        reset.** Confirmed via `updateAim()`'s own dataset (`aimAngle`):
        even with her body facing Main Stacks to within ~14°, the actual
        rendered camera direction (`aimDir`) was over a full radian (~57°)
        off — the standard follow-camera has a baseline downward tilt
        (positions itself behind-and-above her, looking back down near her
        feet, by design, for normal walking) that works fine for regular
        gameplay but put a world sitting fairly high in Chicago's sky
        completely out of frame.
      - **Fixed with a Chicago-specific resting pitch**: `arrive()` now sets
        `camPitch = bi===0 ? -0.55 : 0.3` — tilts the settled view up enough
        that Main Stacks reads clearly as the one nearby, obviously-reachable
        world (no competing Cucumber Meadow in the same shot), while still
        leaving a small additional drag needed to fully lock the aim, so the
        mission text's own "drag/swipe to aim" instruction still applies.
        Verified via `aimAtBody(1)` before and after (false → true) and by
        actually completing the leap to Main Stacks end-to-end from this
        resting view.
      - **Testing gotcha found along the way**: a loop that presses SPACE
        and exits once `state==='walk'` is not sufficient to get through
        Chicago's intro — `state` reads `'walk'` briefly *before* the
        messenger pigeon even arrives (950ms setTimeout gate), so the loop
        can exit having done nothing, leaving `introLocked` stuck `true`
        and the letter/mission/camera never actually initialized. Confirmed
        via `camDebug().introLocked` staying `true` despite `state==='walk'`;
        fixed by waiting past the 950ms gate first, then advancing through
        all 7 real dialogue lines before checking `introLocked === false`.
      - Added a `setCam(yaw, pitch)` debug helper (`window.__world`) for
        directly tuning/probing camera angles in future testing, alongside
        the existing `camDebug()`/`aimAtBody()`.
- [x] Summer Beanie mesh-deformation root-cause fix, file reorganization, LFS
      re-fix (2026-07-15, later still same day): a GitHub Desktop screenshot
      showed the user's own push rejected (`GH008: ...52 unknown Git LFS
      objects`), plus a report that Summer Beanie's belly/hem region looked
      boxed-out and jagged (misread at a glance as an odd "mouth" shape) and
      that her upper and lower body seemed to move separately.
      - **Root cause found via the bind-pose diagnostic**: reset Summer's
        armature to a true bind pose (every bone's `rotation_quaternion` set
        to identity) — the defect vanished completely. That's conclusive:
        deformation that disappears at bind pose but reappears under
        animation is a weight-painting bug, not broken mesh topology. (Ruled
        out topology first — `remove_doubles` and `dissolve_degenerate` on a
        scratch copy had zero visible effect, which is what motivated
        checking bind pose instead of chasing bigger mesh-repair thresholds.)
      - **Quantified exactly why Winter Beanie never showed this bug**: ran
        the same neighbor-weight-jump check (compare each vertex's weight in
        a bone's group against the average of its immediate mesh-neighbors;
        a jump >0.15-0.25 signals unsmoothed weight painting) on both rigs
        across `['Hips','Spine','Chest','Neck','Thigh.L','Thigh.R']` in the
        belly/waist region. Winter: 0 outliers, max jump 0.01 — clean.
        Summer: 447 outliers, jumps up to 0.6+ — a real cluster of vertices
        weighted almost randomly to Spine/Hips/thigh bones, so a couple
        degrees of spine rotation sent them flying while their neighbors
        barely moved. Both characters share identical bone names and run the
        identical procedural Talking-pose code, so this confirms the
        difference was always in Summer's source skinning data, never in the
        animation authoring.
      - **Fixed by smoothing, not rebuilding**: expanded the 447 outliers to
        a 2-ring neighborhood (1646 vertices) and ran 9 iterations of
        neighbor-average weight smoothing across all vertex groups together,
        renormalizing each vertex back to sum=1.0 after every pass — scoped
        to just the affected region plus a margin, so it fixes the defect
        without flattening legitimate weight painting elsewhere or
        introducing a new hard boundary at the edge of the fix. Verified
        clean via test-pose renders before touching the canonical files.
      - **Caught and fixed a real gap: the first fix never shipped.** An
        earlier pass in this same round had already "fixed" the mesh, but
        only inside a scratch preview `.blend` — never exported back into
        the canonical `Summer beanie/Summer_RIGGED.blend` or the live
        `game-assets/beanie/beanie_summer.glb`, so the user correctly saw no
        change at all in-game. This time the fix went into the actual
        source file (`Summer_RIGGED.blend`, saved in place) and was
        re-exported to a fresh `beanie_summer.glb` (Draco level 6, JPEG
        textures, both `Idle`/`Walk` actions re-attached), verified by
        direct glTF binary/JSON parsing (not a re-import) and live-tested in
        the actual game via a local dev server before being committed.
      - **File organization**: renamed the dot-prefixed `.blender_preview_scratch/`
        (hidden by Finder by default — the direct cause of "cant find this")
        to a visible `blender-preview-wip/`, and cleared out redundant
        intermediate render frames, keeping only the final comparison
        images/GIFs and a `backups/` copy of the pre-fix `.blend`/`.glb`.
      - **Git LFS push rejection fixed again** (recurring issue — same root
        cause as the earlier sticker fix, different files this time): the
        newly re-exported `beanie_summer.glb` and other binary assets needed
        `git lfs push origin main --all` to actually upload the real LFS
        objects before GitHub would accept the ref update; this round it was
        494 objects / 1.8GB. Unblocked both this push and the user's own
        pending GitHub Desktop push.
      - Also included in this commit: two small unrelated `index.html` fixes
        from the parallel session (Chicago's flag cloth stripes/stars now
        reparented so they sway with the cloth instead of separately; Beanie
        now re-faces toward her next destination after the Chicago letter
        dialogue ends) — reviewed and verified consistent before bundling in.
      - Verified live post-deploy: fetched `beanie_summer.glb` directly from
        the production URL and confirmed its byte size matches the fixed
        local file exactly.
- [x] Gift books away from Chippy, mission-reveal gating, Book Stacks maze
      (2026-07-15, later still same day): user sent 3 screenshots — a glowing
      gift book right next to Beanie with Chippy visible behind her; the
      Chicago aim view showing Main Stacks, the ring, and Cucumber Meadow all
      reading as adjacent; and the guide compass spelling out the first
      mission ("find Chippy, he is resting on a book pile") before she'd even
      met him. Batch of 7 requests, all fixed and verified:
      - **Gift books repositioned** farther from Chippy's own talk spot
        (`dirNear(chippyN, 1.3 + (i/5)*1.4 + ...)`, was `0.9 + ...`) so none
        of the 5 collectibles land in the same shot as a Chippy conversation.
      - **Journal notebook button** now force-revealed inside `qaWarp()` —
        it was normally only granted mid-letter in Chicago, so any number-key
        warp used before reading the real letter left it hidden for the rest
        of the session.
      - **Guide text simplified** to just "find Chippy" / "find bbak" (no
        descriptive aside), per the request for "just an arrow and x steps
        away."
      - **Mission text now gated behind first meeting**: Books/Cucumber/
        Pigeon's `<b>MISSION:</b>...` text used to reveal on arrival, before
        she'd met Chippy/bbak/Percy — now withheld (`arrive()` hides it for
        those 3 worlds) and only shown once `talkChippy()` /
        bbak's phase-0 handler / `talkPercy()` finish their first exchange.
      - **No mission/dialogue during cutscenes**: `jumpTo()` and
        `startLandingSequence()` (the qaWarp entry path) both now hide
        `#hud`/`#mission` for the whole flight→landing→title stretch — it was
        only ever hidden starting at the orbit/title phase, so the world she
        was leaving kept its mission banner up through the entire jump arc.
      - **Chicago view: Cucumber Meadow repositioned.** Two earlier passes
        already doubled world spacing and shrunk the ring, but the ring still
        visually touched Main Stacks — root cause was never distance, it was
        that Cucumber Meadow's direction from Chicago was only ~12° from
        Books' own direction. Verified via Python/numpy angle-between-vectors
        math, then moved to `pos:[500,-500,-450]` (~47° from both Books and
        Pigeon Plaza, comparable to the ~42° Books/Pigeon already had).
      - **Book Stacks redesigned as a real maze**: replaced the 420-stack
        random-scatter (only a sparse subset ever collided, so it visually
        read as clutter without being a real obstacle) with 4 concentric
        rings of colliding shelf segments around Chippy (`MAZE_RINGS`, 12-24
        segments per ring, 30-45% left open as gaps), built via `tiltDir()`
        for deterministic, evenly-spaced placement.
      - **Maze solvability verification was the hard part.** `walkToward()`
        (the existing debug helper) got Beanie stuck at an identical distance
        forever partway through the rings — traced to `walkToward` always
        steering straight at the final target every step, so it can never
        sidestep a wall sitting directly on that bearing (it has no lateral-
        avoidance logic, unlike a real player who can turn to face a visible
        gap and walk toward *that* instead). Added a new `turnStep(turnRad,
        seconds)` debug primitive that mirrors the real keyboard scheme
        exactly (turn in place, THEN walk straight — never both at once,
        confirmed by reading `updateWalk()`'s actual Arrow-key handling),
        then drove a wall-following navigator (seek target; on full block,
        turn a fixed increment and keep walking until clear) through 4+ fresh
        random layouts — all reached Chippy.
      - **Found and fixed a real softlock bug along the way**: the "grand"
        landmark book tower used `dirNear(chippyN, 2.0)`, but `dirNear()` is
        `normalize(n + spread*randomUnitVector)` — for a spread this large it
        does NOT reliably control angular distance from `n` (unlike
        `tiltDir()`, which the maze rings correctly use), so it could land
        almost anywhere on the sphere. One test run reproduced it landing
        directly on Beanie's own spawn point, blocking her in every direction
        from the very first frame — a genuine first-quest softlock. Fixed by
        switching to `tiltDir(chippyN, 1.8, randomAzimuth)` (fixed angular
        distance, random azimuth only) plus a rejection-sampling reroll
        against `landN` (same `LAND_CLEAR` pattern the maze rings already
        use), since the landing spot itself sits at almost the same ~1.8 rad
        from Chippy and a random azimuth alone wasn't enough clearance.
- [x] Chippy's book-pile visibility, guide/locator dialogue-hiding clarified
      (2026-07-15, later still same day): user screenshot during a Chippy
      conversation asked why the guide compass and 3D locator weren't
      visible, and reported the book pile not reading as "right below" him.
      - **Guide compass + 3D locator hiding during dialogue is intentional,
        not a bug** — confirmed by triggering a real Chippy conversation and
        checking both (`state==='talk'` turns off `updateLocator()`'s
        `active` condition and `startDialog()` explicitly hides the guide
        chip). Every NPC in the game works this way: the guide exists to
        help her find someone, and correctly stops once she's found them and
        is already talking to them. Left unchanged since this matches every
        other conversation, not something specific to Chippy.
      - **Chippy's own seat WAS a real, fixable problem**: 3 books at scale
        1.1 (height 0.858) sitting right next to the randomly-scattered
        700-pile stacks (up to 6 books @ 1.4 scale, plus a looser jitter
        that reads as more voluminous) — his own pile was so short and neat
        by comparison that it was effectively invisible under him, reading
        as him just standing on bare ground. Bumped to 5 books @ scale 1.3
        (height 1.69, ~2x taller) and the exclusion collider to match (0.99
        → 1.2). Verified via both a debug top-down shot and the real talk-
        camera view — book shapes now clearly read at his base.
- [x] World spacing doubled, elliptical ring, gradient sky, Chicago clouds
      (2026-07-15, later still same day): user screenshot showed the ring
      (even after the earlier shrink pass) still visually engulfing Main
      Stacks from the aim-and-leap view.
      - **World positions doubled again** (all non-Chicago `pos:` in
        `WORLD_DEFS` — Chicago stays at the origin). The ring's own absolute
        size wasn't really the remaining problem; Cucumber Meadow just
        needed real empty space between it and its neighbors regardless of
        ring size. New gaps: Chicago→Books ~434, Books→Cucumber ~648,
        Cucumber→Pigeon ~746 (were ~217/324/373).
      - **Updated the aim-lock's hardcoded distance cap** (`surf < 250` →
        `surf < 800` in `updateAim()`) — this doesn't auto-scale with world
        positions the way flight duration/jump-arc height already do (both
        are computed live from actual distance), so leaving it at 250 would
        have made every hop past Chicago un-lockable. Verified end-to-end:
        aimed from Chicago, leaped, landed correctly on Main Stacks at the
        new distance.
      - **Ring reshaped into a true ellipse**: a `RING_ELLIPSE_SQUASH=0.62`
        scale on the Z axis of both the solid pre-reveal ring and each real
        cucumber-band holder (same tilted, spinning groups, so the reveal
        swap still reads as one object). Verified visually from a top-down
        debug shot — reads as a clear tilted oval, not a circle.
      - **Star field radii pushed way out** (461-940 → 1350-2600) — with
        Pigeon Plaza now ~1305 units from the origin, the old star radii
        would have put her standing farther out than her own stars. Bumped
        into "more prominent stars" too: bigger points (1.8-2.6 → 2.6-3.6),
        higher opacity, more of them, plus a new sparse extra-bright "hero
        star" layer.
      - **New: gradient space background.** Replaced the flat
        `PALETTE.nightNavy` fill with a small vertical-gradient canvas
        texture (deep navy at top easing into the richer nightNavy tone
        lower down) assigned to `scene.background`. Since that's no longer
        a plain `THREE.Color`, updated the two `scene.background.copy(
        GARDEN_BG)` call sites (Garden arrival) to `scene.background =
        GARDEN_BG.clone()` instead — reassignment, not an in-place copy a
        Color-shaped object can't do to a Texture.
      - **Chicago's clouds**: were 3 identical rows of 4 same-size spheres,
        orbiting only 3-4.4 units above the surface — level with the tower,
        not above it. Rebuilt as actual cumulus clusters (6-8 varied-size
        puffs scattered in a rough flattened circle per cloud) orbiting
        8-10.6 units up, clearing the ~8.7-unit tower.
- [x] Landing polish, title-timing, left-side compass, melted snow, sticker
      fix (2026-07-15, later still same day):
      - **Fall pose sink reduced 0.6→0.22** (`updateLandingAnim()`) — the
        prior pass's fix for "floating above the ground" overshot into
        visibly burying her face-down pose most of the way into the surface.
      - **Landing dust burst slowed** (`spawnLandingDustBurst()`): speed
        4-10→1.5-4 units/sec, life 0.7-1.3s→1.4-2.3s, spin 1.1→0.5 — read as
        a sharp explosion before, now settles like real dust.
      - **New: camera rumble on impact.** `updateLanding()`'s 'fallgetup'
        branch jitters `camera.position` by a magnitude that decays linearly
        over the first 0.4s of `landing.t` (pure function of elapsed time —
        no extra persistent state, works under `pump()` for testing).
      - **Fall-cutscene camera pulled in**: `followCam` distance during
        'fallgetup' 11→5.5, so the fall itself reads as a close, legible
        beat instead of a distant wide shot.
      - **Title-card minimum display time.** No code bug in the hide/reveal
        itself (`showPlanetTitle()`/`arrive()` were already correct — traced
        through and confirmed live), but `finalizeLanding()` had no cooldown
        after entering the 'orbit' phase, so a reflexive SPACE press (dialogue
        trains her to mash it to advance) landing right as 'fallgetup'
        finished could dismiss the title before it had even finished its own
        1.5s reveal animation — reading as "the HUD/mission chip come back
        too soon". Added a `landing.t < 1.5` guard; verified live that an
        early press during that window is ignored and a later one works.
      - **New: mission text typewriter.** Dialogue's existing typewriter
        (`showDialogLine()`) does a plain `textContent.slice()`, which would
        mangle the mission string's `<b>` gold-keyword tags mid-reveal.
        Added `typewriterHTML()` — walks a scratch DOM tree into a flat
        per-character list tagged bold/not, so a partial reveal always
        re-wraps in a balanced `<b>`. `setMission()` now drives text through
        it instead of setting `innerHTML` directly. Verified live: bold
        spans render correctly at every point mid-type, including with two
        separate `<b>` runs in the same string.
      - **Guide/compass moved to the left edge of the screen** (was a
        top-center banner) — now a narrow vertical badge (compass arrow
        above the distance text) at `left:18px`, vertically centered.
      - **New: melted-snow ground patches in Cucumber Meadow** — 70 flat,
        irregular, near-white (`0xf3faff`, 78-96% opacity) circles scattered
        across the grass, a quiet nod to the world previously being bbak's
        icy home before it thawed. First pass at 50-75% opacity barely
        registered against the muted sage-green grass; bumped whiter/more
        opaque and re-verified visually.
      - **Root-caused "why aren't the stickers showing": GitHub Pages
        cannot serve Git LFS pointers, and `stickers/*.png` was never
        exempted from the blanket `*.png filter=lfs` rule the way
        `game-assets/**/*.glb` and `logo.png` already were** — confirmed by
        curling the live URL directly: it returned a 132-byte LFS pointer
        text file, not the real ~2-4MB image, for every sticker. Added
        `stickers/**/*.png -filter -diff -merge -text` to `.gitattributes`
        and `git add --renormalize`'d the 17 sticker files so they're
        committed as plain blobs instead.
      - Not done: Talking.fbx retargeting, still blocked on the Blender MCP
        connection from the previous round.
- [x] Cucumber ring scale-down + ground-cucumber reveal re-verify (2026-07-15,
      later same day): user screenshot from the aim-and-leap view (standing on
      Chicago, aiming toward Main Stacks) showed the ring so large it visually
      swallowed Main Stacks in the background, well past just "touching its
      own planet" (the problem earlier passes fixed).
      - **Root cause: the camera-clearance margin was way more generous than
        needed.** `RING_INNER = R + landCamMaxReach + 60` with 40/8/20-unit
        bands pushed the outer radius to ~249 at R=45 (~500 across) — `+60`
        on top of `landCamMaxReach` (already a conservative worst-case bound
        on the establishing-shot camera's reach) was pure excess. Cut the
        margin to `+15` and the bands to 20/5/10, landing the outer radius at
        ~171 (~31% smaller radius, ~52% less area) — still verified clear of
        every camera position, just no longer big enough to visually reach
        neighboring worlds. Re-verified via `aimAtBody()` from Chicago's
        surface toward Main Stacks: the ring now reads as a contained halo
        well behind/around the target-locked planet instead of engulfing it.
        World positions (`pos:` in `WORLD_DEFS`) were left untouched — no
        need to touch jump/flight-arc tuning for this.
      - **Ground cucumbers re-verified (2026-07-15): already correctly
        gated, not a bug.** `groundCucumberHolders` are built with
        `holder.visible = false` and only ever flipped to `true` inside
        `updateCukeReveal()`'s hard-swap at the reveal cutscene's midpoint —
        confirmed live via `window.__world.ringDebug()` on a fresh load
        (`groundCukeVisible:false`, `cukeRevealed:false` at `bbakQuest.phase
        0`) and by re-reading `startCukeRevealCutscene()`'s only call site
        (gated on `bbakQuest.tries >= bbakQuest.need`, i.e. exactly bbak's
        4th/final hint). No code change made here; if cucumbers were ever
        seen on the ground before the hint, the likelier explanation is a
        stale cached page rather than this code path.
- [x] 4am feedback batch #2 (2026-07-15): 12 items checked against the other
      session's work first (`git fetch` + re-reading current code) before
      touching anything, to avoid redoing what was already shipped — 2 of the
      12 turned out already done (QA-warp-plays-landing-cutscene, jump-gate-
      already-correct via `updateAim()`'s `cur.missionDone` check) and were
      just re-verified, not re-implemented.
      - Mission banner made bigger/bolder (font `clamp(14px,2vw,18px)`,
        heavier border/glow) — it wasn't reading as an urgent current
        objective at its old 13.5px size.
      - **Chippy exempted from the generic face-Beanie dialogue override** —
        it used HER local up (not his book-pile's own surface normal) to
        reorient him, which could pop him off his hand-tuned seated pose;
        now skipped specifically for `worldRefs.books.chippy`. He also
        bounces (`chippyModel.position.y`) while `dialog.npcObj === chippy`.
      - Main Stacks' 700 book-stack piles cut to 420 with a minimum angular
        separation between neighbors (rejection-sampled) — the old density
        could box her in with no way around a cluster even though only a
        sparse subset actually collide.
      - `nearestFoodPickup()` now returns `null` while `bbakQuest.phase < 1`
        — she could grab food before bbak ever asked for anything. Verified
        live: blocked at phase 0, unlocks the instant phase becomes 1.
      - Pigeon Plaza's guide arrow already correctly targets whichever decoy
        she hasn't met yet (`refreshPlazaGuide()`/`plazaTargetHolder()`) —
        verified live end-to-end (Percy intro → Victoria → Nibbles), no
        change needed.
      - Locator redesigned as an actual 5-point star (`starGeometry()`, a
        `THREE.Shape`-based outline) instead of the previous crossed-
        octahedron sparkle, which read as a soft blob at real distances.
      - `#foodPocket` now also hides whenever `curI !== 2` (was only gated on
        `bbakQuest.holding`), refreshed on every `arrive()`.
      - All 9 Pigeon Plaza character speaker tags now show full species
        names ("Sam the Spinifex Pigeon", "Doodles the Dodo", etc.) instead
        of just their given name.
      - **New: a "spotted them!" notice beat.** The first time she's within
        `guideNear*6` of a character she hasn't met yet (but not yet at talk
        range), a new `'notice'` state pauses movement for 1.8 simulated
        seconds, turns the camera toward the target's bearing, and shows a
        "💭 Hmm… I should go talk to that character!" bubble. Scoped to only
        "find <x>" / "say hello…" guide labels (not "bring/take/fetch it
        back" item errands) after live testing showed it firing oddly for
        a food-pickup guide — there's no character to react to when the
        guide is just pointing at a snack.
      - Not done: retargeting the user's new `movements/Talking.fbx` onto
        Winter Beanie/Bred/Summer Beanie for a talking animation during
        dialogue — blocked mid-attempt by a Blender MCP connection crash
        (a known headless-context bug in the FBX importer hitting
        `bpy.ops.object.mode_set` with no active object). Blender itself
        stayed open; only its MCP bridge died. Needs Blender relaunched
        before this can be retried.
- [x] Title single-line revert, Cucumber Meadow font swap #2, planet spacing
      (2026-07-15, same-day):
      - **Titles forced back to a strict single line.** The prior "let it
        wrap to 2+ lines instead of shrinking" change (see below) backfired
        in practice — a 2-line title grows tall enough to cover Beanie's own
        body during the cutscene, which is worse than a smaller one-liner.
        `#planetTitleName` is `white-space:nowrap` again, `fitPlanetTitleOneLine()`
        shrinks by scroll*width* again (not height).
      - **Real bug found in that shrink loop**: it stepped font-size down by
        a flat 4px per iteration, capped at 40 iterations — fine for modest
        shrinks, but a wide name/font combo (e.g. "EMERALD MEADOW" in the
        new Comfortaa) needed ~50+ steps to fit, blew past the guard, and
        was left rendering wider than the screen. Rewrote it to shrink
        *proportionally* (`cur * (maxW/scrollWidth) * 0.97`) each step,
        which converges in 1-2 iterations regardless of how far overshoot
        is. Verified computed font-size settles at a value that actually
        fits (`scrollWidth <= innerWidth*0.92`) rather than trusting the
        loop merely "ran".
      - **Cucumber Meadow's title font changed again**, Fredoka → **Comfortaa**
        (geometric rounded sans) — still not loved, per direct feedback.
      - **All non-Chicago world positions scaled 1.5x** (Main Stacks,
        Cucumber Meadow, Pigeon Plaza, Garden) — the cucumber ring's much
        larger radius (from the earlier Saturn-ring rework) reached far
        enough that it was visibly bleeding into neighboring Main Stacks,
        breaking the illusion that each world is its own separate place.
        Verified: standing on Main Stacks' title/orbit shot no longer shows
        any trace of the ring.
- [x] Landing cutscene, QA, and movement polish batch (2026-07-15, same-day):
      - **Dust explosion on landing**: `spawnLandingDustBurst()` (new, next to
        the existing footstep `spawnDust()`) throws ~30 big dust puffs
        outward+upward from her position, fired from `startLandingSequence()`
        at the moment of impact — every jump landing and every QA warp (see
        below) now gets a real impact burst instead of nothing.
      - **Fixed Beanie floating instead of touching down**: the fall/get-up
        clip's own root motion was authored for a flat ground plane and
        didn't quite reach this planet-scale surface, so lying flat read as
        hovering just above it. `updateLandingAnim()` now sinks the visual
        model down (`herWinterGroup.position.y`) proportional to the fall
        clip's own blend weight — deepest at the flattest point of the pose,
        easing back to the normal idle height as she stands back up.
        Verified via close-up screenshots at the peak of the fall — she now
        visibly lies flat ON the surface, not embedded in it or floating
        above it.
      - **QA number keys (1-9) now replay the full fall→orbit→title
        cutscene** on that world instead of instantly teleporting — `qaWarp()`
        now positions her at the landing spot and calls
        `startLandingSequence()` (the same path a real jump lands through)
        instead of the instant `goto()`. Still force-clears every mission
        gate first, same as before.
      - **Jump-gating re-verified, no change needed**: confirmed in code and
        live that normal SPACE-to-leap is already fully blocked until
        `bodies[curI].missionDone` — the aim/target-lock in `updateAim()`
        (`if (surf<250 && ang<th && cur.missionDone) target = b`) never sets
        a lock otherwise, and `jumpTo()` only ever fires from that lock. The
        only bypass is the intentional QA path (number keys / `jumpChain()`),
        exactly as intended.
      - **Titles can now grow taller instead of always shrinking to one
        line**: `#planetTitleName` wraps normally now (was `nowrap`, forced
        single-line), and the shrink-to-fit pass (`fitPlanetTitleOneLine`,
        name kept for compatibility) now caps by scroll*height* against half
        the viewport instead of scroll*width* against one line — a name too
        wide to read well on one line now wraps to two/three lines at full
        size instead of shrinking down small. No currently-used world name
        actually needs this (all fit on one line already) — this is
        forward-looking robustness, verified with an artificial long test
        string.
      - **Cucumber ring tilt reduced further (26°→9°) and Emerald/Cucumber
        Meadow re-verified for POV blocking**: the previous 26° tilt still
        read as edge-on / a near-vertical wall from a lot of the positions
        Beanie can actually walk to on the sphere, which both looked like
        touching and could dominate the view during normal exploration. A
        much shallower tilt reads as clearly horizontal from nearly every
        angle. Verified by actually walking her to several different points
        on the sphere and checking the normal gameplay camera (not a custom
        debug shot) — the ring stays low and out of the way at every
        position tested.
      - **Normal movement now plays the Walk clip at its natural pace**: an
        old flat `*2` multiplier on `herWalkAction.timeScale` meant even
        default (non-Shift) movement played the walk cycle at double speed,
        which read as running all the time. Removed the `*2` — Shift-held
        running is now the only thing that speeds the leg animation up
        (`*1.6`), normal movement plays the walk clip at its authored pace.
- [x] Second cucumber ring fix + title/HUD polish (2026-07-15, same-day):
      user screenshots from the live site showed the ring STILL merging with
      the planet even after the previous fix, plus stale HUD info showing
      under the title card. Root causes and fixes:
      - **Real root cause of the "still merging" ring**: sizing it by an
        arbitrary multiple of the planet radius R (tried R+13.5, then R*4)
        never accounted for how far the establishing-shot orbit camera
        itself travels. `updateLanding`'s 'orbit' phase pulls the camera out
        to `min(70, R*2.2)` distance / `min(30, R*0.95)` height from BEANIE
        — at R=45 that's a camera up to ~76 units from her, i.e. up to ~121
        from the planet's center, which sat *inside* the ring's own radius.
        The camera was literally flying through the ring's footprint, not
        past it. Fixed by deriving the ring's inner radius from the same
        camera-distance formula the landing code uses, plus a 60-unit safety
        margin on top, so the ring's inner edge (now ~181 at R=45) is
        guaranteed to clear every possible camera position for that world.
        Also reduced the ring's tilt from 1.15 rad (66°) to 0.45 rad (26°) —
        a steep tilt put the disc nearly edge-on to the camera for much of
        the orbit, which reads as "touching" even with a real 3D gap.
        Verified by driving the actual jump→landing→orbit sequence (not a
        custom debug camera shot, which is what let the previous "fix" pass
        review while still being broken in real gameplay) and sampling
        multiple points across the real 15s orbit, pre- and post-reveal.
      - **Emerald/Cucumber Meadow doubled in size** (r 22.5 → 45), per
        request.
      - **Stale HUD during title cards fixed**: the old planet-name chip and
        the bottom mission banner used to keep showing the *previous*
        world's info for the entire time a title card was up (they only
        refresh in `arrive()`, which doesn't run until she clicks past the
        title) — e.g. Pigeon Plaza's title card was showing Cucumber
        Meadow's leftover "find bbak" mission text underneath it. Both now
        hide the moment `showPlanetTitle()` fires and reappear (with fresh,
        correct content) once the title is dismissed — handled for both the
        click-gated cutscene and the Garden's non-blocking auto-flash
        variant.
      - **Titles bigger again**: clamp raised from 80–260px/24vw to
        100–340px/30vw, padding-top dropped 11vh→6vh, gap 8px→4px.
- [x] Cucumber ring follow-up fix (2026-07-15, same-day): the previous pass's
      ring still visually merged with the planet in real screenshots — a fat
      TorusGeometry tube bulges toward the viewer at a steep tilt even when
      flattened, so its near surface could dip back into the planet from
      some angles despite the centerline sitting clear. Rebuilt the solid
      pre-reveal ring as a true flat disc (`THREE.RingGeometry`, zero bulge
      at any viewing angle, double-sided material) and pushed the gap out
      much further: inner edge now R*4 (90 units on a r22.5 planet, a
      67.5-unit gap — ~5x the previous attempt's ~11.5). The two real
      cucumber-ring bands were moved out to match (inner 90/118, outer
      114/134) with flatter vertical scatter (thick 2.2/1.6 → 1.0/0.7) so
      they read as a disc too, not a puffy band. Verified from multiple
      camera distances/angles pre- and post-reveal — the ring now reads as
      an unmistakably separate, thin, dark green disc with a huge visible
      gap, zero console errors.
- [x] 4am polish batch (2026-07-15): Chicago cutscene fix, bigger titles,
      journal/sticker system, Saturn-style cucumber ring rework.
      - **Chicago tower clipping fixed**: the arrival/title orbit camera
        (shared by the title-screen idle orbit, the post-letter cutscene, and
        every other world's landing) orbited at a fixed 9-unit radius around
        Beanie — but Chicago's tower reaches ~8.7 world units above her (a
        tall tower on a tiny r5.25 planet), so the camera swung straight
        through the tower's geometry at some angles. Chicago's orbit now
        starts at 13/5.5 (dist/height) instead of 9/3.2, easing out further
        from there, clearing the tower at every angle. Also found and fixed a
        second contributor: the 9 random gray skyline blocks near the tower
        could spawn directly in Beanie's fixed spot (their spread radius
        overlapped hers), occasionally standing right in front of her and
        reading as her body merging into a building — they now retry their
        spawn direction until they're ≥~37° clear of her spot.
      - **Planet-arrival titles much bigger**: font clamp raised from
        64–240px to 80–260px (24vw base, was 15vw), padding-top dropped
        14vh→11vh, gap 22px→8px — titles now fill almost the entire top of
        the screen with tight whitespace while Beanie's full body stays
        clearly visible below. Verified across Chicago/Oswald, Main
        Stacks/Playfair, Cucumber Meadow/Baloo 2 (both stages), Pigeon
        Plaza/Bungee, and Garden/Cormorant Garamond.
      - **Real bug found + fixed**: fitPlanetTitleOneLine()'s shrink-to-fit
        measured scrollWidth on the very next animation frame after adding
        the `.play` reveal class — catching the titleReveal keyframe's
        transient `letter-spacing:26px` (its 0% state) mid-transition, which
        massively inflated the measured width and over-shrunk the font (seen
        shrinking "Cucumber Meadow" all the way down to 36px instead of its
        intended ~192px). This was likely the real cause behind titles
        occasionally reading as missing/illegible. Fixed by sizing the title
        to rest BEFORE adding the `.play` class, so the reveal animation only
        ever starts once the font-size is already final.
      - **Verified every world's arrival title fires correctly**, including
        Main Stacks specifically (the one the previous session flagged as
        maybe-missing) and both of Cucumber Meadow's stages (pre-reveal
        "Emerald Meadow" and post-reveal "Cucumber Meadow").
      - **New: journal + sticker collection system.** Rachel loves journaling
        and stationery, so the messenger pigeon now also hands Beanie a tiny
        notebook right after Bred's letter in Chicago ("somewhere to keep
        records of things"), which reveals a new 📔 HUD button beside the
        mute button. The very first time she talks to each named character
        (Chippy, bbak, Percy, and every Pigeon Plaza pigeon — Vanessa,
        Nibbles, Alfred, Sam, Sunny, Otto, Mochi, Buckle, Doodles) shows a
        "met a new friend!" toast with that character's real sticker artwork
        (from the new `stickers/` folder) and adds it to her journal; talking
        again never re-triggers it. The journal button opens a simple grid
        modal showing every collected sticker plus `?` placeholders for
        characters not yet met, with a live "N / 12 friends met" count.
        Progress persists across reloads via localStorage. Verified end-to-
        end: talked to Chippy in a fresh session, got the toast + sticker,
        confirmed it persisted after a page reload and shows correctly in the
        journal grid.
      - **Cucumber Meadow ring completely reworked** — the previous pass's
        "wider + flatter" change (see the entry below) had increased the
        solid ring's tube radius without moving its base radius outward to
        compensate, so its inner edge actually sank below the planet's own
        surface radius: it visually intersected the planet. Rebuilt from
        scratch as a proper Saturn-style ring: dark saturated forest green
        (`#1f4d29`, replacing the pale `PALETTE.moss` that blended into the
        grass) for the solid pre-reveal ring; both the solid ring and the
        real cucumber ring's two bands now have their inner edge at
        R+13.5 — a large, obvious, unmistakable gap from the planet at every
        point around the orbit, verified visually from multiple camera
        distances/angles. Cucumber density raised ~5x (520/280 → 2600/1400
        cucumbers across the two bands); since that many individual cloned
        Object3D cucumbers would have been a real frame-rate risk, the ring
        now drives each band off a single `THREE.InstancedMesh` built from
        the loaded cucumber model's geometry (baked to world-space so per-
        instance orientation still matches the individually-cloned ground
        cucumbers elsewhere), cutting per-band draw calls from hundreds down
        to one. Re-ran the full bbak quest + reveal cutscene end-to-end:
        solid ring never touches the planet pre-reveal, the reveal swap still
        works, the real cucumber ring never touches the planet post-reveal
        either, and it reads as a dense, dark green, clearly Saturn-like band
        from every angle tested.
      - Zero console errors across every verification pass above.
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
