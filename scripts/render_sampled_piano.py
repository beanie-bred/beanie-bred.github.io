#!/usr/bin/env python3
"""Offline-render MIDI through the sampled Salamander Yamaha C5 piano."""
from functools import lru_cache
from pathlib import Path
import re

import mido
import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

ROOT = Path(__file__).resolve().parents[1]
SFZ = Path("/tmp/upright/KeyPleezer LivingRoom Upright - Free Micro SFZ.sfz")
MIDI = ROOT / "audio/popo-jazz-loop.mid"
OUT = ROOT / "audio/popo-premium-cafe-v9.wav"
SR = 44_100

def parse_sfz():
    regions = []
    for line in SFZ.read_text(errors="ignore").splitlines():
        if not line.startswith("<region>"):
            continue
        values = dict(re.findall(r"(\w+)=([^ ]+)", line))
        regions.append({
            "sample": SFZ.parent / values["sample"].replace("\\", "/"),
            "lo": int(values.get("lokey", 0)), "hi": int(values.get("hikey", 127)),
            "lov": int(values.get("lovel", 1)), "hiv": int(values.get("hivel", 127)),
            "center": int(values.get("pitch_keycenter", 60)),
        })
    return regions

REGIONS = parse_sfz()

@lru_cache(maxsize=10)
def read_sample(path):
    data, rate = sf.read(path, dtype="float32", always_2d=True)
    if rate != SR:
        raise RuntimeError(f"Unexpected sample rate {rate}: {path}")
    return data

def region_for(key, velocity):
    matches = [r for r in REGIONS if r["lo"] <= key <= r["hi"] and r["lov"] <= velocity <= r["hiv"]]
    if not matches:
        raise RuntimeError(f"No piano sample for key={key}, velocity={velocity}")
    return matches[0]

def midi_events():
    midi = mido.MidiFile(MIDI)
    tempo_value = 500_000
    seconds = 0.0
    active, notes = {}, []
    for message in mido.merge_tracks(midi.tracks):
        seconds += mido.tick2second(message.time, midi.ticks_per_beat, tempo_value)
        if message.type == "set_tempo":
            tempo_value = message.tempo
        elif message.type == "note_on" and message.velocity:
            active[(message.channel, message.note)] = (seconds, message.velocity)
        elif message.type in ("note_off", "note_on"):
            key = (message.channel, message.note)
            if key in active:
                start, velocity = active.pop(key)
                notes.append((start, max(.06, seconds-start), message.note, velocity, message.channel))
    return notes, seconds

notes, duration = midi_events()
mix = np.zeros((round((duration+2.2)*SR), 2), dtype=np.float32)

for start, held, key, velocity, channel in notes:
    region = region_for(key, velocity)
    sample = read_sample(str(region["sample"]))
    ratio = 2 ** ((key-region["center"])/12)
    if abs(ratio-1) > 1e-5:
        positions = np.arange(0, len(sample)-1, ratio)
        lo = positions.astype(np.int64)
        frac = (positions-lo)[:,None]
        sample = sample[lo]*(1-frac) + sample[lo+1]*frac
    # Character-upright release: short, woody and bouncy instead of grand/cinematic.
    wanted = min(len(sample), round((held+.48)*SR))
    sample = sample[:wanted].copy()
    release = min(round(.48*SR), wanted)
    sample[-release:] *= np.linspace(1,0,release,dtype=np.float32)[:,None] ** 1.35
    # Accompaniment lives slightly left; melody is centered and forward.
    if channel == 0:
        sample *= np.array([.92,.72], dtype=np.float32)
    else:
        sample *= np.array([.94,.94], dtype=np.float32)
    at = round(start*SR)
    end = min(len(mix), at+len(sample))
    mix[at:end] += sample[:end-at]

# Gentle top end and a nearly dry 0.48 s café-room reflection.
mix = sosfilt(butter(2, 7_000, btype="low", fs=SR, output="sos"), mix, axis=0).astype(np.float32)
rng = np.random.default_rng(20260716)
ir_len = round(.48*SR)
t = np.arange(ir_len)/SR
decay = np.exp(-t*11.5)
ir = rng.normal(0,1,(ir_len,2)).astype(np.float32)*decay[:,None]
ir[0] += 4
for delay, amount in [(.021,.45),(.043,.25),(.071,.14)]:
    ir[round(delay*SR)] += amount
ir /= np.max(np.abs(ir),axis=0,keepdims=True)
wet = np.column_stack([fftconvolve(mix[:,c],ir[:,c],mode="full")[:len(mix)] for c in range(2)]).astype(np.float32)
mix = mix*.975 + wet*.025
peak = float(np.max(np.abs(mix)))
if peak:
    mix *= .89/peak
sf.write(OUT, mix, SR, subtype="PCM_24")
print(f"{OUT} | {len(notes)} notes | {len(mix)/SR:.2f}s")
