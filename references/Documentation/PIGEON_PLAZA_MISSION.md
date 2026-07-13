# 🕊️ PIGEON PLAZA — Mission Design Doc

World 4 in the rebooted chain (Chicago → Books → Cucumber → **Pigeon Plaza** →
Garden). This is the emotional turn of the journey: Beanie helps Percy find his
long-lost friend, and in gratitude Percy grows huge and flies her onward toward
Bred. Status: **BUILT & verified (2026-07-13)** — 8 real pigeon models
(`game-assets/pigeons/*.glb`), full quest flow (Percy intro → 7-decoy parade →
give-up → 1690/"D" hint → find Doodles → reunion → Percy flight → Garden), the
profile talk-camera + locator + guide, decoys stay standing, and every pigeon
bounces while talking **except Vanessa**. Coco cut. Runs clean end-to-end.

---

## Premise
Pigeon Plaza is *way* too full of pigeons. Among them is **Percy** (the grand
teal-headed one Beanie already meets in the current build). Beanie finds Percy;
Percy asks her to help find a dear friend he "hasn't seen in ages." Beanie then
meets a parade of unusual pigeons one at a time — each a charming dead end —
until, with a hint from Percy, she finally finds **Doodles the dodo**, Percy's
true long-lost friend. Reunion → every pigeon circles them → Percy grows huge →
Beanie rides him off-world (iris wipe → Garden).

---

## Flow (ordered beats)

1. **Land on Pigeon Plaza.** Guide/locator points to **Percy** (as today).
2. **Talk to Percy (intro).** Percy explains: long ago he had a best friend he
   misses terribly; would Beanie help find them among the plaza's pigeons?
   → mission starts; gate stays closed.
3. **Decoy parade.** Pigeons spawn **one at a time at a random coordinate** on
   the planet, in the fixed order below. For each:
   - The locator points to the newly-spawned pigeon.
   - Beanie walks over and talks (SPACE).
   - The pigeon **introduces itself + tells its fun fact**.
   - Beanie asks *"Are you the friend Percy has been missing?"* → pigeon says
     **"No!"** (each with its own flavor line).
   - On dismiss, the **next** pigeon in the order spawns.
   Order: **Vanessa → Nibbles → Alfred → Sunny → Otto → Mochi → Buckle** (7 decoys).
   Met decoys **stay standing on the plaza** (the flock visibly gathers).
4. **Give up → back to Percy for a hint.** After Buckle (the last decoy),
   Beanie has met everyone and is stumped. The locator flips back to Percy.
   Beanie returns and asks *"When did you last see your friend?"*
5. **Percy's hint.** *"Ohh… it was a long, long time ago. Around **1690**-ish?
   And his name started with a **D**…"* (Player realization: 1690 + dodo = the
   friend went extinct; he's a **dodo**.)
6. **Doodles is summoned.** **Doodles the dodo** spawns at a random coordinate;
   locator points to him.
7. **Talk to Doodles.** He shares his fun fact, then admits **he's sad and
   misses his family**. Beanie cheers him up: *"Then WE'LL be your family."*
   She asks him to **follow her to meet Percy**.
8. **Reunion.** Beanie leads Doodles back to Percy (Doodles walks/follows, or
   simply "joins" on arrival). **Percy + Doodles finally reunite** → mission
   **accomplished**, gate opens.
9. **Finale beat.** All the pigeons (decoys + crowd) **form a circle** around
   Percy and Beanie. **Percy grows huge**, tells Beanie to **hop on his back —
   he knows where Bred is.** → existing Percy-flight + iris wipe → Garden.

> This replaces the current simple "walk to Percy → 4-line dialog → fly" flow.
> The existing `beginPercyFlight()` / iris / `arriveGarden()` chain is reused
> verbatim for beat 9; only the lead-up changes.

---

## Pigeon roster

Emoji + species + the fun fact each one tells. **Model** = folder under
`pigeon collection/` (Rodin `base.obj` + PBR set, convert to `.glb` like
chippy/bbak). "❗" marks an asset gap.

| # | Name | Species | Model folder | Fun fact / dialogue note |
|---|------|---------|--------------|--------------------------|
| 1 | 👑 **Vanessa** | Victoria Crowned Pigeon | `victoria crowned pigeon/` | World's LARGEST pigeon; lace-like crest fans out like a royal crown. **Render ~3× the average pigeon size.** (A baby would already be as big as a normal rock dove.) |
| 2 | 🌈 **Nibbles** | Nicobar Pigeon | `nicobar pigeon/` | Closest living relative of the extinct dodo; stunning metallic rainbow feathers. (Nice foreshadowing of Doodles.) |
| 3 | 🫒 **Alfred** | African Green Pigeon | `african green pigeon/` | Olive-green feathers camouflage him so well he's usually *heard* before *seen*. **Include a beat where Beanie checks he's not "a parrot in disguise as a pigeon."** |
| 4 | 🎨 **Sunny** | Superb Fruit Dove | `superb fruit dove/` | One of the world's most colorful pigeons — looks almost hand-painted. |
| 5 | 🍊 **Otto** | Orange Dove | `orange dove/` | Found only in Fiji; brilliant orange plumage glows among tropical forests. |
| 6 | 🌈 **Mochi** | Many-colored Fruit Dove | `many-colored fruit dove/` | Every bird is a unique blend of pastel + vibrant colors — a tiny rainbow. |
| 7 | ❤️ **Buckle** | (Luzon) Bleeding-heart Dove | `luzon bleeding heart dove/` | Bright crimson chest patch looks like a tiny heart — hence the name. Last decoy. |
| 8 | 🦤 **Doodles** | Dodo bird | `dodo bird/` | **The real friend.** Dodos weren't clumsy — they evolved without predators and simply no longer needed to fly. He's sad; he misses his family. |

**Coco the Crested Partridge is cut** (per Justin, 2026-07-13) — no model for
it, so 7 decoys total. Unused-but-present in `pigeon collection/`: `spinifix
pigeon/` and `images/` (ref renders incl. `pink necked green pigeon.png`).

---

## Dialogue template (per decoy)

Each decoy uses the generic `startDialog(lines, onDone, {speaker, npcObj, npcPos})`
(the profile two-shot camera + prop-hiding already applied):

```
<Name>:  "<greeting> — I'm <Name> the <Species>! 🕊️"
<Name>:  "<fun fact>"
Beanie:  "…Are you the friend Percy has been missing?"
<Name>:  "Me? Oh — no, no! <flavor no-line>"
```
onDone → mark this decoy met, spawn the next in order, re-point the locator.

Per-pigeon flavor lines to write (keep them cute/short):
- **Vanessa** — regal, a little vain about her crown.
- **Nibbles** — dazzled by her own rainbow sheen; "…the dodo? we're *related*, but no."
- **Alfred** — Beanie: "wait… are you a parrot in disguise?" Alfred (offended):
  "I am NOT a parrot. I'm a pigeon, thank you very much." Then the camouflage fact.
- **Sunny** — "hand-painted, aren't I?"
- **Otto** — glowing orange, homesick for Fiji.
- **Mochi** — pastel rainbow, sweet.
- **Buckle** — shows off the little heart on his chest; last "no."

**Doodles** (beat 7):
```
Doodles: "Oh! Hello… I'm Doodles. A dodo. 🦤"
Doodles: "Everyone thinks we were clumsy — we weren't! We just… never needed to
          fly. No predators, see. It was peaceful."
Doodles: "…but it gets lonely now. I miss my family."
Beanie:  "Then we'll be your family. Come with me — someone has missed you for
          a very, very long time."
```
→ leads Doodles to Percy.

**Percy hint (beat 5):**
```
Percy:  "The last time I saw him…? Goodness. It was AGES ago — around 1690, I
         think. And his name… started with a D."
```

**Percy reunion + grow (beat 9):** reuse `PERCY_LINES`-style dialog then the
existing `beginPercyFlight()` (Percy scales up, crowd scatters/circles, Beanie
mounts, iris → Garden).

---

## Mechanics / implementation notes

Reuse the systems already built in `index.html`:
- **Sequential spawn:** keep a `plazaQuest = { step, order:[...], metVanessa…], found:false }`.
  Spawn only the *current* target pigeon at a `dirNear(plazaN, random)` surface
  coordinate; hide/despawn (or leave standing) after "No"; spawn next.
- **Gating:** `bodies[PIGEON_I].missionDone = false` until Percy + Doodles reunite;
  Percy's flight is the "leap" (no aim-lock leap on this world).
- **Locator + guide:** set `bodies[PIGEON_I].guideFn` to the current target
  (Percy → each decoy in turn → back to Percy → Doodles → Percy). Reuse the
  floating-arrow **locator** and the distance **#guide** bar.
- **Talk camera:** the profile two-shot + `hideNearbyObstacles(npcObj)` already
  handle framing; pass each pigeon's holder as `npcObj`.
- **Models:** convert each `pigeon collection/<species>/base.obj` (+ diffuse) to
  `game-assets/pigeons/<name>.glb` via the headless Blender pipeline
  (`/tmp/chippy_pipeline/` — same as chippy/bbak). Scale per-species; **Vanessa
  ≈ 3× average**. Tune each model's `rotateY` to face Beanie (Rodin has no
  consistent forward).
- **"Follow me" (Doodles):** simplest = on cheer-up, attach a small follower that
  lerps behind Beanie until she reaches Percy; or just despawn Doodles and
  re-spawn him beside Percy on arrival for the reunion beat.
- **Circle finale:** reposition the crowd holders onto a ring around Percy before
  `beginPercyFlight()`; Percy scale-up already exists in that function.

## Existing crowd
`buildPigeons()` already fills the plaza with ~290 grounded plush pigeons (now
with eyes) + Percy. The 9 named story pigeons are *additional*, real-model
characters spawned by the quest — not part of the decorative crowd.

## Decisions (locked)
- **Coco: CUT** — 7 decoys (Vanessa, Nibbles, Alfred, Sunny, Otto, Mochi, Buckle).
- **Met decoys stay standing** on the plaza (flock visibly gathers).

## Open questions
1. Doodles "follow" vs "re-spawn at Percy" for the reunion (default: re-spawn).
