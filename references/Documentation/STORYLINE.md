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
  dominant beside her (orbit floor lowered from the default 18/7 down to
  10/4 specifically so a tiny world like Chicago doesn't pull back so far
  the tower loses its dominance in frame).
- Font: **Oswald** (condensed sans, city/skyline feel).

## World 2 — Main Stacks
*(renamed from "Book Stacks" — this is the old library where Bred and
Beanie used to study together, back when.)* Pastel book towers everywhere.
- Find **Chippy** (napping on a book pile), who asks for **5 favourite
  books** — glowing gift-books scattered around the planet, collect with A,
  bring them all back.
- Font: **Playfair Display** (elegant serif — bookish).

## World 3 — Cucumber Meadow (starts as "Emerald Meadow")
The big reveal world. She has **no idea it's cucumbers** until bbak tells her.
- **On arrival she only ever sees:** a solid pastel-green ring circling the
  planet (a plain torus, no individual cucumbers visible), ordinary grass,
  and a scattering of random full-size foods (burgers, cake, donuts, pizza,
  fries, ice cream) plus a handful of glowing "cold treat" pickups. The
  planet displays as **"🌱 Emerald Meadow"** — deliberately vague, tag: "a
  mysterious green ring circles overhead…". No cucumbers are visible on the
  ground at all yet (`groundCucumberHolders` all start `visible:false`, and
  the real cucumber-built ring — `cukeRingGroups`, hidden — sits underneath
  the solid one the whole time, 4x thicker / 3x wider band than the
  original single-ring design, ready to swap in).
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
- Font: **Baloo 2** (rounded, cute).

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
  a given name/font combo would otherwise wrap), sized to fill most of the
  available width, with a **subtle** dark glow behind the letters (no gold
  rule lines above/below — removed).
- **QA**: number keys 1–5 instantly warp to that world and force-clear every
  mission gate (`qaWarp()`), usable from the title screen or mid-dialogue.
