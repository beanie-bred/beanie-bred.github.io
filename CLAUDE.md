# Beanie Bred World - Agent Notes

## Background music

- Normal play starts `audio/executive-lounge.mp3` automatically when the page opens.
- Executive Lounge loops continuously through every world before the Garden.
- `arrive(GARDEN_I)` crossfades over 3.5 seconds to `audio/pixeltown.mp3`.
- Do not restore any generated Popo MIDI/M4A files to game playback.
- The in-game mute button controls both the active track and a track currently fading out.
- Audible browser autoplay may be blocked until the first pointer or keyboard interaction; the game retries automatically on that first interaction.

## Silent QA for Codex and Claude

Run automated QA with one of these URL query parameters:

- `?qa=codex`
- `?qa=claude`
- `?qa=1`

The game also detects `navigator.webdriver`. Any of these conditions starts all BGM muted so automated testing does not play audio. Do not globally mute normal player sessions.

## Music credits

The visible footer in `index.html` must retain both Uppbeat credits and links:

- The Executive Lounge - Dan Barton
- Pixeltown - Color Parade
