# STORYLINE — Beanie's Little Universe

The authoritative, current narrative design doc. Supersedes the "Story flow"
section of `GAME_BIBLE.md` (which is now a stale early pitch — worlds/radii
there predate the reboot). For Pigeon Plaza's full beat-by-beat script, see
`PIGEON_PLAZA_MISSION.md`; this doc summarizes it alongside every other world
so the whole journey lives in one place.

Cast: **Beanie = Rachel** (player character), **Bred = Justin** (who built
this for her). Chain order: **Chicago → Main Stacks → Cucumber Meadow →
Pigeon Plaza → The Garden**.

---

## Title screen
Dark pastel-blue space, Chicago's snowball planet slowly rotating. Beanie
spawns sitting **right beside Chicago's tall tower** (`CHICAGO_START_N =
(0.48, 0.86, 0.18)` normalized — close enough to the tower's collider
footprint to read as "leaning against it," not colliding with it). The
title-screen camera does a **close, local-tangent-plane orbit** around her
(radius 9, height 3.2, same angular speed as every world's arrival cutscene,
`2π / LAND_ORBIT_DURATION`) — so the tower sweeps through frame like it's
spinning around her. Press SPACE → third person, and she's already standing
in that exact spot (no jump/pop when gameplay starts).

## World 1 — Chicago
Small, gray, gently sad. Snow falls, wind blows. She's never gated from
walking here, but **the leap onward is gated** until she reads Bred's letter:
- ~1s after gameplay starts, a messenger pigeon swoops down and **lands on
  the surface** in front of her (not a hover — it visibly descends and
  touches down), then reads a short letter from Bred explaining he built her
  this universe and to follow it to the end, where he's waiting.
- Dialogue uses the shared two-character conversation camera (see **UI/UX
  conventions** below) with a minimum separation distance, so she and the
  messenger are never framed overlapping.
- Once the letter finishes: mission unlocks, messenger flies off, **and only
  now** does Chicago get its own arrival title cutscene — the same
  orbit-and-reveal every other world gets on arrival, just deliberately
  delayed until after the letter (since she didn't "arrive" via a jump this
  first time). Camera framing matches the title screen: close orbit, tower
  dominant beside her (orbit floor raised to 13/5.5 — was 9/3.2 — since the
  tighter radius used to swing the camera straight through the tower's own
  geometry; skyline decorations near her spawn point also now keep a minimum
  clearance from her so none of them ever stand directly in front of her).
- Alongside the letter, the messenger also hands her **a tiny notebook** —
  "somewhere to keep records of things" — which is the journal/sticker system
  (see **Journal & stickers** below) becoming available from this point on.
- Font: **Oswald** (condensed sans, city/skyline feel).

## Journal & stickers
Rachel loves journaling and stationery, so from the Chicago letter onward a
📔 button sits in the HUD beside the mute button. The first time Beanie talks
to each named character — Chippy, bbak, Percy, and every Pigeon Plaza pigeon
(Vanessa, Nibbles, Alfred, Sam, Sunny, Otto, Mochi, Buckle, Doodles) — a "met a
new friend!" toast shows that character's real sticker artwork (from the
`stickers/` folder) and adds it to the journal; meeting them again never
re-triggers it. The journal button opens a grid of every collected sticker
(uncollected ones show as a `?` placeholder) with a running count. Progress
persists across page reloads via localStorage.

## World 2 — Main Stacks
*(renamed from "Book Stacks" — this is the old library where Bred and
Beanie used to study together, back when.)* Pastel book towers everywhere.
- Find **Chippy** (napping on a book pile), who asks for **5 favourite
  books** — glowing gift-books scattered around the planet, collect with A,
  bring them all back.
- Font: **Playfair Display** (elegant serif — bookish).

## World 3 — Cucumber Meadow (starts as "Emerald Meadow")
The big reveal world. She has **no idea it's cucumbers** until bbak tells her.
- **On arrival she only ever sees:** a solid dark-green ring circling the
  planet, Saturn-style — a wide, flat, low-profile band sitting with a large,
  unmistakable gap between its inner edge and the planet's surface (never
  close to touching), ordinary grass, and a scattering of random full-size
  foods (burgers, cake, donuts, pizza, fries, ice cream) plus a handful of
  glowing "cold treat" pickups. The planet displays as **"🌱 Emerald
  Meadow"** — deliberately vague, tag: "a mysterious green ring circles
  overhead…". No cucumbers are visible on the ground at all yet
  (`groundCucumberHolders` all start `visible:false`, and the real
  cucumber-built ring — `cukeRingGroups`, hidden — sits underneath the solid
  one the whole time, same wide gap and ~5x cucumber density versus the
  original design, ready to swap in; both bands render through a single
  `THREE.InstancedMesh` each rather than one Object3D per cucumber).
- Find **bbak** (sleeping polar bear, overheating). Bring him a cold treat —
  he rejects each one with a food-specific reaction line. After his 4th
  rejection, he gives the final hint: *"It's green, and it's long. When I
  was just a cub, I used to eat it instead of meat!"* — that's the trigger.
- **The reveal cutscene** (`startCukeRevealCutscene`, ~7s, state `cukeReveal`,
  input frozen): the camera pulls back to a wide establishing shot while the
  solid ring's spin visibly winds down to a stop; at the halfway point it
  hard-swaps — solid ring hidden, the real cucumber ring + every ground
  cucumber fade in at once with a sparkle burst + chime. Immediately after,
  the world is renamed **"🥒 Cucumber Meadow"** (tag reverts to "they school
  like fish out here") and plays the same click-gated title-card cutscene
  every world gets, now correctly announcing the secret that was hiding in
  plain sight the whole time.
- She fetches the now-visible glowing special cucumber and brings it to
  bbak → he's cooled down → gate opens.
- Font: **Comfortaa** (geometric rounded sans — went through Baloo 2, then
  Fredoka, then this; the first two both got direct "looks ugly" feedback).

## World 4 — Pigeon Plaza
Full script lives in `PIGEON_PLAZA_MISSION.md`. Summary: find **Percy**, who
asks her to help find his long-lost friend. Seven decoy pigeons spawn one at
a time in a fixed order (Vanessa → Nibbles → Alfred → Sunny → Otto → Mochi →
Buckle), each with a real 3D model, a fun fact, and a firm "not me." Met
decoys stay standing (the flock visibly gathers). Stumped, she returns to
Percy for a hint (*"~1690, name started with a D"*) → finds **Doodles the
dodo**, lonely and missing his family → "we'll be your family" → leads him
back → reunion → the flock rings around them → **Percy grows huge and flies
her onward**, iris-wipe to the Garden.
Font: **Bungee** (blocky, playful).

## World 5 — The Garden (finale)
Pastel daylight, birthday music starts here (and only here). The biggest
world, full of hydrangeas/daisies/calla lilies/roses/tulips. A big white
couch, with **bred, percy (real model), chippy (real model), and bbak**
waving.
Font: **Cormorant Garamond** (delicate serif). Uses the non-blocking
`flashPlanetTitleAuto()` variant (shows + auto-fades after 3.2s, no
click-to-continue) since the Percy-flight + iris entrance shouldn't pause on
a click.

**STATUS: kiss cutscene not yet built.** Currently arriving and walking up to
Bred triggers the existing heart-burst finale + card. Still to design/build,
per Justin's original brief: a walk-toward-each-other beat ending in a kiss,
hearts, then the card, then the game ends. (See ROADMAP.md task #42.)

---

## UI/UX conventions (apply to every world)

- **Mission banner**: anchored to the **bottom** of the screen (moved down
  from the top, where it kept coinciding with the guide/interaction chips).
  Auto-hides during any dialogue (the dialogue box can grow tall enough to
  reach it otherwise).
- **Distance guide + locator beacon**: a text chip ("find X — N steps away")
  plus a tall glowing world-space beam+arrow hovering over whatever she
  needs to reach next, visible from far across a big planet.
- **Conversation camera**: profile two-shot (Beanie screen-left facing
  right, the NPC on the right facing back toward her), with
  `ensureTalkDistance()` nudging her backward along the sphere surface
  *before* the camera engages if she pressed SPACE while standing right on
  top of the NPC — so no dialogue ever frames them literally overlapping,
  regardless of how close she was standing.
- **Planet-arrival title cards**: one distinct Google Font per world (listed
  above per-world), plain name only (no emoji — the emoji still appears in
  the small HUD corner chip), forced to a **single line** via a shrink-to-
  fit pass (measures actual rendered width, steps the font-size down only if
  a given name/font combo would otherwise wrap), sized to fill almost the
  entire top of the screen with near-zero surrounding whitespace while
  keeping Beanie's full body visible below, with a **subtle** dark glow
  behind the letters (no gold rule lines above/below — removed). The sizing
  pass runs and settles *before* the reveal animation starts playing — it
  used to run one frame after, which could catch the reveal keyframe's
  transient huge letter-spacing mid-transition and over-shrink the title.

## Chicago's tower orbit — clearance note
The title-screen idle orbit, the post-letter arrival cutscene, and every
other world's landing all share one orbit camera. Its radius must stay large
enough that the camera never swings through solid geometry standing near
Beanie's fixed spot — Chicago's tower is the tightest case (it reaches ~8.7
world units above her on a tiny r5.25 planet), so if that camera's radius
setup is ever retuned again, re-verify against Chicago specifically by
sampling several full orbit angles, not just the resting frame.
- **QA**: number keys 1–5 warp to that world, force-clearing every mission
  gate, and play the SAME fall→orbit→title cutscene a real jump landing
  gets (via `startLandingSequence()`) rather than teleporting straight into
  gameplay — so the shortcut doubles as a way to review any world's landing
  cutscene on demand. Usable from the title screen or mid-dialogue.
- **Jump gating**: leaping onward is only ever possible once the current
  world's mission is done (`updateAim()` won't lock a target otherwise) or
  via the QA shortcut above — there is no other way to skip ahead.
- **Landing impact**: every landing (real jump or QA warp) throws a big dust
  burst around her (`spawnLandingDustBurst()`), and the fall/get-up pose now
  visibly sinks her into contact with the ground at its flattest point
  instead of hovering just above the surface.
