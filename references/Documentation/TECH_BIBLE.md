# TECH BIBLE

## Stack
Single self-contained index.html. Three.js r160 via CDN importmap. No build
step, no assets — all geometry/materials/audio generated in code. Works from
file:// (needs internet once for the CDN).

## Architecture (single module script, ~2100 lines)
CONFIG (names + card text, top of file) → renderer/lights → helpers (quat sphere
math, placeOn, ephemerals) → audio engine (WebAudio: melodies, footsteps per
surface, chime, coo) → makeChibi factory → creature factories → world builders →
body assembly (6 worlds + 8 moons, jump chain) → movement/camera → percy
sequence → finale → HUD/DOM → main loop (step(dt) + rAF tick).

## Movement
Quaternion orientation on sphere; camera-relative steering (↑ walks toward the
view, avatar turns at 11 rad/s, camYaw compensates then decays 0.9/s). Walk 6.0
u/s. Footstep sound on each half walk-cycle, keyed by body.step
(stone/grass/water/book/pop).

## Camera
Orbit around avatar: drag or trackpad swipe (wheel deltas), pitch clamp
(-1.05, 1.2), pinch (ctrl+wheel) zoom 5–16. followCam lerps position/up;
arrive() resets yaw=0 pitch=0.3.

## Jumping
updateAim: camera forward vs body centers, threshold atan2(r*1.3, d)+0.055,
range surface-dist ≤ 52. Locked target → gold ring + prompt → SPACE →
quadratic-bezier flight (1.5–3.2 s by distance) with front-flip + sparkle trail.

## Testing (page paused when tab hidden — rAF)
window.__world: pump(seconds) steps the sim manually; aimAtBody(i) brute-forces
a real aim lock; goto/gotoPercy/gotoCouch; jumpChain; info(). ?test=1 enables a
hashchange bridge; inert otherwise. Full regression = chain 12 hops via
aimAtBody+SPACE, percy dialogue, garden, finale, card, console must be silent.
