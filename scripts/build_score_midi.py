#!/usr/bin/env python3
"""Replace the generated top line with melody read directly from the PDF pages."""
from copy import deepcopy
from pathlib import Path
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
            copied.volume.velocity = 61
            # A small overlap creates finger-legato between adjacent notes;
            # printed rests remain intact because their events are untouched.
            copied.duration.quarterLength += .07
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
        copied.volume.velocity = 42
    remaining = cursor - float(item.offset)
    if float(copied.duration.quarterLength) > remaining:
        copied.duration.quarterLength = remaining
    left.insert(float(item.offset), copied)

left.makeMeasures(inPlace=True)
right.makeMeasures(inPlace=True)
score.insert(0, left)
score.insert(0, right)

# Sparse flute cushion: one quiet chord tone per measure, never doubling the
# active melody rhythm. It adds air and cheerfulness without becoming a duet.
flute = stream.Part()
flute.partName = "Soft flute background"
flute.insert(0, instrument.Flute())
for bar_start in range(0, int(cursor), 8):
    sounding = [e for e in source_left.notes if float(e.offset) <= bar_start < float(e.offset + e.duration.quarterLength)]
    if not sounding:
        continue
    source = sounding[-1]
    pitches = list(source.pitches) if isinstance(source, chord.Chord) else [source.pitch]
    chosen = max(pitches, key=lambda p: p.midi)
    f = note.Note(chosen)
    while f.pitch.midi < 72:
        f.transpose(12, inPlace=True)
    f.volume.velocity = 24
    f.duration.quarterLength = min(7.5, cursor-bar_start)
    flute.insert(bar_start, f)
flute.makeMeasures(inPlace=True)
score.insert(0, flute)
out = ROOT / "audio" / "popo-jazz-loop.mid"
score.write("midi", fp=out)
print(f"{out} ({cursor:.2f} quarter notes of PDF melody)")
