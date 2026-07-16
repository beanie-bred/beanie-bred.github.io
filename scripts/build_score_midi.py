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
melody_intervals = []
last_melody_end = -99.0
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
            # Keep the lead sheet's natural singing register. The previous
            # octave lift pushed the outro as high as E7 and sounded piercing.
            beat = float(item.offset) % 4
            absolute_start = cursor + float(item.offset)
            phrase_entrance = absolute_start - last_melody_end > .32
            # Expressive right-hand shaping: confident phrase entrances and
            # downbeats, gentler pickups, plus a little lift on singing high notes.
            velocity = 57
            if beat < .06:
                velocity += 3
            elif abs(beat-round(beat)) < .06:
                velocity += 1
            if 72 <= copied.pitch.midi <= 84:
                velocity += 2
            if float(item.duration.quarterLength) <= .25:
                velocity -= 2
            if phrase_entrance:
                velocity += 3
            copied.volume.velocity = max(49, min(65, velocity))
            # A small overlap creates finger-legato between adjacent notes;
            # printed rests remain intact because their events are untouched.
            # Preserve the lead sheet's written duration exactly. The sampled
            # upright supplies its own short natural release after note-off.
            melody_intervals.append((absolute_start,
                                     absolute_start + float(copied.duration.quarterLength),
                                     copied.pitch.midi))
            last_melody_end = absolute_start + float(item.duration.quarterLength)
        right.insert(cursor + float(item.offset), copied)
    cursor += float(flat.highestTime)

left = stream.Part()
left.partName = "Jazz piano accompaniment"
left.insert(0, instrument.Piano())
left.insert(0, tempo.MetronomeMark(number=85))
harmony_changes = []
for item in source_left.notesAndRests:
    if float(item.offset) >= cursor:
        continue
    copied = deepcopy(item)
    event_start = float(item.offset)
    active_melody = [pitch for start, end, pitch in melody_intervals
                     if start <= event_start < end]
    melody_active = bool(active_melody)
    if isinstance(copied, note.Note):
        if copied.pitch.midi < 48:
            copied.transpose(12, inPlace=True)
        copied.volume.velocity = 36 if melody_active else 53
    elif isinstance(copied, chord.Chord):
        harmony_changes.append(event_start)
        # Drop the ominous sub-bass; keep jazz extensions in a warm middle register.
        for p in copied.pitches:
            if p.midi < 48:
                p.midi += 12
        # Keep every accompaniment voice under the active melody, with an open
        # but warm C3-G4 working register and minimal inner-voice movement.
        ceiling = min(active_melody)-3 if active_melody else 67
        arranged = []
        for pitch in sorted(copied.pitches, key=lambda p: p.midi):
            p = deepcopy(pitch)
            while p.midi < 48: p.midi += 12
            while p.midi > ceiling: p.midi -= 12
            if p.midi >= 43: arranged.append(p)
        arranged = sorted({p.midi: p for p in arranged}.values(), key=lambda p: p.midi)
        if not arranged:
            continue

        # Cozy animation texture: negative space first. Repeated sections vary
        # between bass + shell, root + 10th, and a tiny rolled upper color.
        remaining = cursor - float(item.offset)
        duration = min(float(copied.duration.quarterLength), remaining)
        progress = event_start / max(cursor, 1)
        sparse = progress < .09 or progress > .9
        fuller = .34 <= progress <= .52 or .66 <= progress <= .86
        measure_variant = int(event_start//4) % 4
        count = 1 if sparse and measure_variant % 2 else (3 if fuller else 2)
        spacing = duration/max(count, 1)
        patterns = ([0,2,1], [0,1,3], [0,3,2], [0,2,3])
        pattern = patterns[measure_variant]
        for index in range(count):
            pitch = arranged[pattern[index] % len(arranged)]
            rolled = note.Note(pitch)
            base_velocity = (27 if melody_active else 34) if sparse else (29 if melody_active else 37)
            if fuller: base_velocity += 2
            if progress > .94: base_velocity -= round((progress-.94)*100)
            rolled.volume.velocity = max(20, min(43, base_velocity + (index == 0)*2))
            rolled.duration.quarterLength = min(spacing*.82, remaining-index*spacing)
            # A little behind the beat, with deterministic human variation.
            left.insert(event_start+index*spacing+.025+(measure_variant-index)*.006, rolled)
        continue
    remaining = cursor - float(item.offset)
    if float(copied.duration.quarterLength) > remaining:
        copied.duration.quarterLength = remaining
    left.insert(float(item.offset), copied)

left.makeMeasures(inPlace=True)
right.makeMeasures(inPlace=True)
score.insert(0, left)
score.insert(0, right)

# Warm upright-bass pulse for an upbeat café trio. It stays restrained under
# the lead and leans in slightly whenever the melody leaves breathing room.
bass = stream.Part()
bass.partName = "Upright bass"
bass.insert(0, instrument.AcousticBass())
for beat_start in range(0, int(cursor), 2):
    sounding = [e for e in source_left.notes
                if float(e.offset) <= beat_start < float(e.offset + e.duration.quarterLength)]
    if not sounding:
        continue
    source = sounding[-1]
    pitches = list(source.pitches) if isinstance(source, chord.Chord) else [source.pitch]
    root = min(p.midi for p in pitches)
    while root > 47: root -= 12
    while root < 36: root += 12
    b = note.Note(root)
    active = any(start <= beat_start < end for start, end, _ in melody_intervals)
    b.volume.velocity = 24 if active else 31
    b.duration.quarterLength = 1.68
    bass.insert(beat_start, b)
bass.makeMeasures(inPlace=True)
score.insert(0, bass)
# The PDF/song tempo is held at a steady 85 BPM. No swing or rubato is added;
# note starts, durations and rests remain on the written rhythmic grid.
score.insert(0, tempo.MetronomeMark(number=85))

out = ROOT / "audio" / "popo-jazz-loop.mid"
score.write("midi", fp=out)

# Add actual damper-pedal MIDI. Re-pedalling each beat connects the piano's
# sampled release tails while clearing harmony often enough for the lead
# sheet's quick passing chords to remain bright and readable.
midi = mido.MidiFile(out)
end_tick = round(cursor * midi.ticks_per_beat)
for track_index, track in enumerate(midi.tracks[1:]):
    hand_channel = min(track_index, 2)
    absolute = 0
    events = []
    for message in track:
        absolute += message.time
        if hasattr(message, "channel"):
            message = message.copy(channel=hand_channel)
        events.append((absolute, 1, message.copy(time=0)))
    if track_index < 2:
        pedal_ticks = sorted({round(change*midi.ticks_per_beat) for change in harmony_changes})
        for beat_tick in pedal_ticks:
            if beat_tick:
                events.append((max(0, beat_tick-8), 0,
                               mido.Message("control_change", channel=hand_channel,
                                            control=64, value=0, time=0)))
            events.append((beat_tick, 2,
                           mido.Message("control_change", channel=hand_channel,
                                        control=64, value=78, time=0)))
        events.append((end_tick, 0,
                       mido.Message("control_change", channel=hand_channel,
                                    control=64, value=0, time=0)))
    events.sort(key=lambda e: (e[0], e[1]))
    track.clear()
    previous = 0
    for tick, _, message in events:
        track.append(message.copy(time=tick-previous))
        previous = tick

# Simple café pulse: quarter-note brush texture, a tiny kick only on beat 1,
# and cross-stick on 2/4. No busy eighth-note pattern fighting the melody.
drum_events = []
for quarter in range(int(cursor)):
    tick = quarter*midi.ticks_per_beat
    beat = quarter
    active = any(start <= beat < end for start, end, _ in melody_intervals)
    hat = 10 if active else 14
    drum_events += [(tick,1,mido.Message("note_on",channel=9,note=42,velocity=hat,time=0)),
                    (tick+38,0,mido.Message("note_off",channel=9,note=42,velocity=0,time=0))]
    beat_in_bar = quarter % 4
    if beat_in_bar in (0,1,3):
        drum_note = 36 if beat_in_bar == 0 else 37
        vel = (12 if active else 16) if drum_note == 36 else (15 if active else 19)
        drum_events += [(tick,1,mido.Message("note_on",channel=9,note=drum_note,velocity=vel,time=0)),
                        (tick+55,0,mido.Message("note_off",channel=9,note=drum_note,velocity=0,time=0))]
drum_events.sort(key=lambda event:(event[0],event[1]))
drums=mido.MidiTrack(); drums.append(mido.MetaMessage("track_name",name="Cafe brushes",time=0))
previous=0
for tick,_,message in drum_events:
    drums.append(message.copy(time=tick-previous)); previous=tick
drums.append(mido.MetaMessage("end_of_track",time=max(0,end_tick-previous)))
midi.tracks.append(drums)
midi.save(out)
print(f"{out} ({cursor:.2f} quarter notes of PDF melody)")
