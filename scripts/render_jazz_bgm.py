#!/usr/bin/env python3
"""Build the eight-bar PDF transcription as a two-track General MIDI file."""
from pathlib import Path
import struct

PPQ = 480
BPM = 82

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

# Program 0 acoustic grand; program 66 tenor sax in zero-based General MIDI.
piano_track = make_track(piano, b"\x00\xc0\x00")
sax_track = make_track(sax, b"\x00\xc1\x42")
header = b"MThd" + struct.pack(">IHHH",6,1,3,PPQ)

out = Path(__file__).resolve().parents[1]/"audio"/"popo-jazz-loop.mid"
out.parent.mkdir(exist_ok=True)
out.write_bytes(header+meta+piano_track+sax_track)
print(out)
