# ROADMAP
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
