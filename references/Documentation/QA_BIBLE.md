# QA BIBLE

## Definition of done
Runs with ZERO console errors/warnings through: title → SPACE → 12 real
aim-locked hops → Percy talk/ride/iris → Garden (bg switches, birthday melody)
→ walk to couch → finale hearts → envelope → typed card → replay → title.

## Regression procedure (headless)
Serve via .claude/launch.json (birthday-world). Because rAF pauses when the tab
is hidden, drive with __world.pump(). One-eval script: press SPACE, loop
{aimAtBody(chainNext), SPACE, pump(4.5)}, gotoPercy, SPACE through dialogue,
pump(10), gotoCouch, hold ArrowUp until finale, pump(4), click envelope.
Expect: hops=12, visited all-true, cardShown, envOpen, silent console.

## Visual checks
Front view of each character vs turnaround sheet (swing camera with synthetic
wheel events). Feet touch ground (no float). Face features visible (not
swallowed by head/hair). Blob shadows present. Draw calls: ~300 (garden) to
~1600 (pigeon plaza) — fine on desktop.

## Known traps
- Busy-wait in eval freezes the page's own timers — never use.
- preview_click on overlay sometimes misses; use element.click() in eval.
- Typewriter timers are wall-clock, not sim-time.
