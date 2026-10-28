#!/usr/bin/env python3
"""Replay the recorded RTL simulation of the three bit-exact clips, for screen recording.

Nothing is simulated here. The script reads the real Verilator console logs and
receipts in logs/<clip>/ (recorded 21 Oct 2026) and prints them fast-forwarded,
so a run of about an hour plays back in about 20 seconds.

    python3 replay.py              # all three clips
    python3 replay.py --play       # also play each WAV (macOS afplay)
    python3 replay.py --clip 1 --seconds 30
"""
import argparse, json, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
B, D, G, C, Y, R = "\033[1m", "\033[2m", "\033[32m", "\033[36m", "\033[33m", "\033[0m"


def kv(line):
    return dict(re.findall(r"(\w+)=(\S+)", line))


def say(text="", pause=0.0):
    print(text, flush=True)
    time.sleep(pause)


def replay(clip, seconds, play):
    logs = HERE / "logs" / clip["clip"]
    lines = (logs / "positive.log").read_text().splitlines()
    render = json.loads((logs / "render.json").read_text())
    compare = (logs / "compare.log").read_text().strip()
    final = kv(next(l for l in lines if "_EOS_PASS" in l))
    total_clocks = int(final["common_clocks"])
    step = seconds / (len(lines) or 1)

    say(f"{B}Input{R}  {clip['wav']}  {clip['seconds']:.2f} s, {clip['samples']:,} samples, 16 kHz PCM", 0.6)
    if play:
        subprocess.run(["afplay", str(HERE / "clips" / clip["wav"])], check=False)
    say(f"{D}Feeding PCM into the RTL chip model (Verilator, one common clock)...{R}", 0.6)

    tokens = 0
    for line in lines:
        f = kv(line)
        if line.startswith("CHUNK_COMMIT"):
            say(f"  {C}frontend{R}  audio chunk {int(f['chunk']) + 1:>2}/16 -> encoder   "
                f"{D}clock {int(f['common_clocks']):>12,}{R}", step)
        elif line.startswith("LAYER_ACCEPT"):
            say(f"  {C}encoder {R}  layer {int(f['layer']) + 1}/6 done            "
                f"{D}clock {int(f['clocks']):>12,}{R}", step)
        elif line.startswith("OBSERVED_TOKEN_DONE"):
            tokens += 1
            say(f"  {C}decoder {R}  token {tokens} emitted", step)
        elif line.startswith("ONCHIP"):
            say(f"  {G}on-chip{R}   {f['service']:<20} replies {int(f['rtl_replies']):>11,}   "
                f"host replies {f['host_replies']}   mismatches {f['mismatches']}", step)
        else:
            time.sleep(step / 4)

    say()
    say(f"{B}Token IDs{R}  {render['tokens']}", 0.4)
    say(f"{B}Text     {R}  {Y}{B}\"{render['text']}\"{R}", 0.8)
    ok = "pass" in compare.lower()
    say(f"{B}Check    {R}  {G if ok else ''}all 18 internal outputs bit-identical to the frozen reference model{R}"
        if ok else f"{B}Check{R}  {compare}", 0.3)
    say(f"{D}Simulated {total_clocks:,} clocks (recorded run, fast-forwarded to {seconds:.0f} s).{R}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clip", type=int, choices=(1, 2, 3))
    ap.add_argument("--seconds", type=float, default=20.0, help="replay length per clip")
    ap.add_argument("--play", action="store_true", help="play the WAV before each replay (macOS)")
    a = ap.parse_args()
    clips = json.loads((HERE / "clips" / "clips.json").read_text())
    if a.clip:
        clips = [clips[a.clip - 1]]
    say(f"{B}RouteVoice v1: speech transformer as hardwired-weight logic{R}")
    say(f"{D}Replay of recorded RTL simulation runs, 21 Oct 2026. Weights stored as fixed index + codebook.{R}", 1.0)
    for i, clip in enumerate(clips):
        say(f"\n{B}--- Clip {i + 1}/{len(clips)} ---{R}")
        replay(clip, a.seconds, a.play)
        time.sleep(1.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
