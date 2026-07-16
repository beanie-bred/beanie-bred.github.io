#!/usr/bin/env python3
"""Replace the generated top line with melody read directly from the PDF pages."""
from copy import deepcopy
from pathlib import Path
from music21 import converter, instrument, note, stream, tempo

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
print(f"{out} ({cursor:.2f} quarter notes of PDF melody)")
