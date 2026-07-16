#!/usr/bin/env python3
"""Build the eight-bar PDF transcription as a two-track General MIDI file."""
from pathlib import Path
import struct

PPQ = 480
BPM = 85

MELODY = [
    (0,0,72,.5),(0,1,67,.75),(0,1.75,68,.125),(0,1.875,70,.125),
    (0,2,68,.5),(0,3,65,.75),(0,3.75,67,.125),(0,3.875,65,.125),
    (1,0,63,4),(2,0,70,3),
    (4,0,67,.5),(4,.5,65,.5),(4,1,66,.5),(4,1.5,67,.5),
    (4,2,63,.5),(4,2.5,68,.5),(4,3,67,.5),(4,3.5,65,.25),
    (4,3.75,63,.125),(4,3.875,62,.125),
    (5,0,60,1.5),(5,2,67,.5),(5,2.5,65,1.5),(6,0,70,3),(7,0,58,4),
]

CHORDS = [
    (0,0,1,[48,58,63,67]),(0,1,1,[46,56,61,65]),
    (0,2,1,[44,55,60,63]),(0,3,1,[43,53,58,62]),
    (1,0,4,[41,48,55,60,63]),(2,0,4,[46,53,58,63,67]),
    (3,0,4,[48,58,63,67]),
    (4,0,.5,[48,58,63,67]),(4,.5,.5,[47,57,62,65]),
    (4,1,.5,[46,56,61,65]),(4,1.5,.5,[51,58,62,68]),
    (4,2,1,[44,55,60,63]),(4,3,1,[43,53,58,62]),
    (5,0,4,[41,48,55,60,63]),(6,0,4,[46,53,58,63,67]),
    (7,0,4,[46,53,58,61,65]),
]

# Full lead-sheet form after the intro. Each item is one measure; split chords
# represent the within-measure changes printed above the staff. The form covers
# both lyric passes, the alternate ending and all eight page-three outro lines.
VOICINGS = {
    "Fm9":[41,48,55,60,63], "Fm11":[41,48,58,63,67], "Fm7":[41,48,56,63],
    "Bb9s":[46,53,58,61,65], "Bb13s":[46,53,58,63,67], "Bb9":[46,56,60,65],
    "EbM9":[39,46,55,58,65], "B7":[47,54,57,63], "Gbdim":[42,48,51,57],
    "G7a":[43,53,57,62,65], "G7b":[43,53,56,59,64], "C9s":[48,55,58,62,65],
    "C7":[48,55,58,64], "AbM7":[44,51,55,60], "AbM9":[44,51,55,58,63],
    "Gm7":[43,50,53,58], "AbmB":[47,51,56,59], "Gdim":[46,50,53,56],
}
VERSE = [
    ["Fm9"],["Bb9s","Bb9"],["EbM9"],["B7","Gbdim"],
    ["Fm11"],["Bb13s"],["C9s"],["C7"],
    ["Fm9"],["Bb13s"],["EbM9"],["AbmB"],
    ["Fm9"],["G7a","G7b"],["C9s"],["C7"],
    ["Fm9"],["G7a"],["C9s"],["EbM9"],
]
OUTRO_A = [["Fm9"],["G7a","G7b"],["C9s"],["Gdim"]]
OUTRO_B = [["Fm9"],["G7a","G7b"],["AbM9","Gm7"],["Fm9","Bb9s"]]

intro_chords, intro_melody = CHORDS[:], MELODY[:]
CHORDS, MELODY = intro_chords[:], intro_melody[:]

def add_section(measures, start_bar, quieter=False):
    """Add jazz-piano comping plus a light upper-register melodic line."""
    contour = [0,1,2,3,2,1,3,2]
    for local_bar, names in enumerate(measures):
        bar = start_bar + local_bar
        span = 4/len(names)
        for part, name in enumerate(names):
            chord = VOICINGS[name]
            CHORDS.append((bar,part*span,span,chord))
        # Right hand remains lyrical and connected instead of blocky. These
        # chord-extension tones follow the complete score form underneath.
        upper = VOICINGS[names[0]][1:]
        for step, beat in enumerate([0,.5,1,1.5,2,2.5,3,3.5]):
            note = upper[contour[step] % len(upper)] + 12
            MELODY.append((bar,beat,note,.48 if not quieter else .42))
    return start_bar + len(measures)

bar = 8
bar = add_section(VERSE, bar)
# The PDF's first ending returns to the written intro before verse two.
for b,beat,note,dur in intro_melody: MELODY.append((bar+b,beat,note,dur))
for b,beat,dur,chord in intro_chords: CHORDS.append((bar+b,beat,dur,chord))
bar += 8
bar = add_section(VERSE, bar)
bar = add_section([["Fm7"],["EbM9"],["Bb13s"],["C7"]], bar)
# Page three: four A/B outro pairs, matching its eight printed systems.
for pair in range(4):
    bar = add_section(OUTRO_A, bar, quieter=pair>1)
    bar = add_section(OUTRO_B, bar, quieter=pair>1)

def vlq(n):
    out = [n & 0x7f]
    n >>= 7
    while n:
        out.append((n & 0x7f) | 0x80)
        n >>= 7
    return bytes(reversed(out))

def make_track(events, prefix=b""):
    data, last = bytearray(prefix), 0
    for tick, order, payload in sorted(events, key=lambda e: (e[0], e[1])):
        data += vlq(tick-last) + payload
        last = tick
    data += b"\x00\xff\x2f\x00"
    return b"MTrk" + struct.pack(">I", len(data)) + data

def tick(bar, beat):
    return round((bar*4+beat)*PPQ)

tempo = round(60_000_000/BPM)
meta = make_track([], b"\x00\xff\x51\x03" + tempo.to_bytes(3,"big") + b"\x00\xff\x58\x04\x04\x02\x18\x08")

piano = []
for bar, beat, dur, chord in CHORDS:
    start, stop = tick(bar,beat), tick(bar,beat+dur*.9)
    for i, note in enumerate(chord):
        # A relaxed upward roll avoids the blocky/choppy chord attack.
        on = start + i*12
        piano += [(on,1,bytes([0x90,note,54])),(stop,0,bytes([0x80,note,30]))]

sax = []
for bar, beat, note, dur in MELODY:
    start = tick(bar,beat)
    # Nearly full written value for connected jazz phrasing, while keeping rests.
    stop = tick(bar,beat+dur*(.98 if dur >= .5 else .9))
    velocity = 78 if dur >= .5 else 70
    sax += [(start,1,bytes([0x91,note,velocity])),(stop,0,bytes([0x81,note,34]))]

# Both hands use acoustic grand piano; the second track is the right hand.
piano_track = make_track(piano, b"\x00\xc0\x00")
sax_track = make_track(sax, b"\x00\xc1\x00")
header = b"MThd" + struct.pack(">IHHH",6,1,3,PPQ)

out = Path(__file__).resolve().parents[1]/"audio"/"popo-jazz-loop.mid"
out.parent.mkdir(exist_ok=True)
out.write_bytes(header+meta+piano_track+sax_track)
print(out)
