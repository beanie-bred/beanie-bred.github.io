#!/usr/bin/env python3
"""Replace the generated top line with melody read directly from the PDF pages."""
from copy import deepcopy
from pathlib import Path
import mido
from music21 import chord, converter, instrument, note, stream, tempo

ROOT = Path(__file__).resolve().parents[1]
base = converter.parse(ROOT / "audio" / "popo-jazz-loop.mid")
parts = list(base.parts)
if not parts:
    raise RuntimeError("The accompaniment MIDI has no piano part")

score = stream.Score()
source_left = parts[0].flatten()

right = stream.Part()
right.partName = "PDF melody"
right.insert(0, instrument.Piano())
right.insert(0, tempo.MetronomeMark(number=85))

cursor = 0.0
for page in range(1, 4):
    parsed = converter.parse(ROOT / "music" / f"popo-page-{page}.musicxml")
    source = list(parsed.parts)[0]
    flat = source.flatten()
    for item in flat.notesAndRests:
        copied = deepcopy(item)
        # The lead sheet is monophonic. OMR grace-note artifacts with zero
        # duration are kept short enough to ornament without breaking timing.
        if copied.duration.quarterLength == 0:
            copied.duration.quarterLength = .0625
        if isinstance(copied, note.Note):
            # The requested bright register: melody exactly one octave higher.
            copied.transpose(12, inPlace=True)
            beat = float(item.offset) % 4
            # Expressive right-hand shaping: confident phrase entrances and
            # downbeats, gentler pickups, plus a little lift on singing high notes.
            velocity = 76
            if beat < .06:
                velocity += 9
            elif abs(beat-round(beat)) < .06:
                velocity += 4
            if copied.pitch.midi >= 84:
                velocity += 4
            if float(item.duration.quarterLength) <= .25:
                velocity -= 5
            copied.volume.velocity = max(68, min(91, velocity))
            # A small overlap creates finger-legato between adjacent notes;
            # printed rests remain intact because their events are untouched.
            copied.duration.quarterLength += .16
        right.insert(cursor + float(item.offset), copied)
    cursor += float(flat.highestTime)

left = stream.Part()
left.partName = "Jazz piano accompaniment"
left.insert(0, instrument.Piano())
left.insert(0, tempo.MetronomeMark(number=85))
for item in source_left.notesAndRests:
    if float(item.offset) >= cursor:
        continue
    copied = deepcopy(item)
    if isinstance(copied, note.Note):
        if copied.pitch.midi < 48:
            copied.transpose(12, inPlace=True)
        copied.volume.velocity = 43
    elif isinstance(copied, chord.Chord):
        # Drop the ominous sub-bass; keep jazz extensions in a warm middle register.
        for p in copied.pitches:
            if p.midi < 48:
                p.midi += 12
        # Romantic jazz comping: quietly roll each voicing bottom-to-top,
        # leaving space for the melody rather than striking a heavy block chord.
        remaining = cursor - float(item.offset)
        for index, pitch in enumerate(sorted(copied.pitches, key=lambda p: p.midi)):
            rolled = note.Note(pitch)
            rolled.volume.velocity = 31 + min(index, 3)
            rolled.duration.quarterLength = min(float(copied.duration.quarterLength)*.92, remaining)
            left.insert(float(item.offset)+index*.035, rolled)
        continue
    remaining = cursor - float(item.offset)
    if float(copied.duration.quarterLength) > remaining:
        copied.duration.quarterLength = remaining
    left.insert(float(item.offset), copied)

left.makeMeasures(inPlace=True)
right.makeMeasures(inPlace=True)
score.insert(0, left)
score.insert(0, right)

out = ROOT / "audio" / "popo-jazz-loop.mid"
score.write("midi", fp=out)

# Add actual damper-pedal MIDI. Re-pedalling each beat connects the piano's
# sampled release tails while clearing harmony often enough for the lead
# sheet's quick passing chords to remain bright and readable.
midi = mido.MidiFile(out)
end_tick = round(cursor * midi.ticks_per_beat)
for track in midi.tracks[1:]:
    absolute = 0
    events = []
    for message in track:
        absolute += message.time
        events.append((absolute, 1, message.copy(time=0)))
    for beat_tick in range(0, end_tick, midi.ticks_per_beat):
        if beat_tick:
            events.append((max(0, beat_tick-8), 0,
                           mido.Message("control_change", control=64, value=0, time=0)))
        events.append((beat_tick, 2,
                       mido.Message("control_change", control=64, value=78, time=0)))
    events.append((end_tick, 0,
                   mido.Message("control_change", control=64, value=0, time=0)))
    events.sort(key=lambda e: (e[0], e[1]))
    track.clear()
    previous = 0
    for tick, _, message in events:
        track.append(message.copy(time=tick-previous))
        previous = tick
midi.save(out)
print(f"{out} ({cursor:.2f} quarter notes of PDF melody)")
