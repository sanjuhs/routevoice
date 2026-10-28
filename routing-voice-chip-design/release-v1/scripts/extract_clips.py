"""Write the three bit-exact demo clips as 16 kHz WAV files.

Each clip is the exact PCM segment the RTL consumed. Its float32 bytes must
hash to the source_PCM_sha256 recorded in the v49 tally before it is written.
"""
import hashlib, json, sys
from pathlib import Path
import numpy as np, soundfile as sf

OFFLOAD = Path("/Volumes/Extreme Pro Dev/routevoice-checkpoints/laptop-offload-20261014/routing-voice-chip-design/experiments")
OUT = Path(__file__).resolve().parents[1] / "demo" / "clips"
CLIPS = [
    ("01-switch-on-the-lights", "voice-e2e-20261011-wispr-v1/k64-007/line-0.npy",
     "e8b54ce6dde0b831d0bfa6c1a195732ae77f353717ef01ca95d0aec365186d5a", "Switch on the lights", "wispr-007-seg0"),
    ("02-plant-present", "voice-e2e-20261011-wispr-v1/k64-031/line-1.npy",
     "99f32da368e24863d4b04a96ea20a531e6c4c9bfe54af5d1f0409fd3f565afbb", "Plant present.", "wispr-031-seg1"),
    ("03-seasonable", "voice-e2e-20261011-software-v1/k64-input-002/line-0.npy",
     "9678c2c6ff095d0cbb45c56619bbad87582fcdcab5b1d2ec7343d3c7eb9c441e", "Seasonable.", "software-1919-142785-0022-seg0"),
]
manifest = []
for name, rel, want, text, case in CLIPS:
    x = np.load(OFFLOAD / rel, allow_pickle=False).astype("<f4", copy=False).reshape(-1)
    got = hashlib.sha256(x.tobytes()).hexdigest()
    if got != want:
        sys.exit(f"{name}: sha256 {got} != tally {want}")
    pcm = np.round(x * 32768.0)
    assert np.array_equal(pcm / 32768.0, x.astype(np.float64)), "not exact PCM16"
    path = OUT / f"{name}.wav"
    sf.write(path, pcm.astype("<i2"), 16000, subtype="PCM_16")
    manifest.append(dict(clip=name, case=case, samples=int(x.size), seconds=x.size / 16000,
                         source_PCM_sha256=want, rtl_text=text, wav=path.name,
                         wav_sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    print(f"{name}: {x.size} samples ({x.size/16000:.2f} s) hash OK -> {path.name}")
(OUT / "clips.json").write_text(json.dumps(manifest, indent=1) + "\n")
