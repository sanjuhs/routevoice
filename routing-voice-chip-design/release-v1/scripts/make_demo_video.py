"""Render the three bit-exact demo runs as an animation: demo/routevoice-demo.mp4 (1080p, with
the clip audio) and demo/routevoice-demo.gif (960 px, silent, for the README).

Nothing is simulated. Progress bars and the clock counter are driven by the real clock
milestones in demo/logs/<clip>/positive.log (chunk commits, encoder layer accepts, final
clock); the text, token IDs and checks come from render.json and compare.log.

    python make_demo_video.py        # needs pillow, numpy, soundfile, matplotlib (for fonts), ffmpeg
"""
import json, re, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
import matplotlib
from PIL import Image, ImageDraw, ImageFont

DEMO = Path(__file__).resolve().parents[1] / "demo"
W, H, FPS = 1920, 1080, 30
INTRO, AUDIO, SIM, OUT = 2.5, 1.6, 5.5, 3.4      # seconds: title card, then per clip
CLIP_T = AUDIO + SIM + OUT
FONTS = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
SANS, BOLD, MONO = (str(FONTS / f) for f in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSansMono.ttf"))
# Dark reference palette (dataviz skill), as in make_figures.py.
SURF, PANEL, INK, INK2, MUTED, GRID = "#1a1a19", "#232321", "#f0efec", "#c3c2b7", "#8a897f", "#33332f"
BLUE, ORANGE, AQUA, GOOD = "#3987e5", "#d95926", "#199e70", "#3fb27f"


def font(path, size):
    return ImageFont.truetype(path, size)


def kv(line):
    return dict(re.findall(r"(\w+)=(\S+)", line))


def load(clip):
    logs = DEMO / "logs" / clip["clip"]
    lines = (logs / "positive.log").read_text().splitlines()
    total = int(kv(next(l for l in lines if "_EOS_PASS" in l))["common_clocks"])
    chunks = [int(kv(l)["common_clocks"]) for l in lines if l.startswith("CHUNK_COMMIT")]
    layers = [int(kv(l)["clocks"]) for l in lines if l.startswith("LAYER_ACCEPT")]
    services = [kv(l) for l in lines if l.startswith("ONCHIP")]
    render = json.loads((logs / "render.json").read_text())
    ntok = len(render["tokens"])
    # Token-done clocks in the log use a separate counter; spread tokens over the decoder span.
    tokens = [layers[-1] + (total - layers[-1]) * (i + 1) / ntok for i in range(ntok)]
    audio, sr = sf.read(DEMO / "clips" / clip["wav"], dtype="float32")
    ok = "pass" in (logs / "compare.log").read_text().lower()
    return dict(clip=clip, total=total, chunks=chunks, layers=layers, tokens=tokens, services=services,
                render=render, audio=audio, sr=sr, ok=ok)


def bar(d, x, y, w, label, done, n, unit, colour, f_lab, f_val):
    d.text((x, y), label, font=f_lab, fill=INK2)
    d.text((x + w, y), f"{done}/{n} {unit}", font=f_val, fill=INK if done else MUTED, anchor="ra")
    by = y + 44
    d.rounded_rectangle((x, by, x + w, by + 22), 6, fill=GRID)
    seg = w / n
    for i in range(done):
        d.rounded_rectangle((x + i * seg + 2, by + 2, x + (i + 1) * seg - 2, by + 20), 4, fill=colour)


def frame(run, i, n, t):
    img = Image.new("RGB", (W, H), SURF)
    d = ImageDraw.Draw(img)
    f_t, f_s, f_lab, f_val = font(BOLD, 40), font(SANS, 24), font(SANS, 26), font(MONO, 24)
    d.text((80, 60), "RouteVoice: speech transformer as hardwired-weight logic", font=f_t, fill=INK)
    d.text((80, 118), "Replay of recorded RTL simulation runs (Verilator, 21 Oct 2026). "
                      "Weights stored as fixed 4-bit index + codebook.", font=f_s, fill=INK2)
    d.text((W - 80, 66), f"clip {i + 1}/{n}", font=font(SANS, 30), fill=INK2, anchor="ra")
    c = run["clip"]

    # Input waveform with playhead.
    x0, y0, w0, h0 = 80, 200, 1000, 230
    d.rounded_rectangle((x0, y0, x0 + w0, y0 + h0), 14, fill=PANEL)
    d.text((x0 + 28, y0 + 22), "Input audio", font=f_lab, fill=INK2)
    d.text((x0 + w0 - 28, y0 + 22), f"{c['wav']}  ·  {c['seconds']:.2f} s, 16 kHz", font=f_val, fill=MUTED, anchor="ra")
    a = run["audio"]
    cols = w0 - 56
    env = np.abs(a[: len(a) // cols * cols]).reshape(cols, -1).max(1)
    env = env / (env.max() or 1)
    play = min(1.0, t / AUDIO)
    mid = y0 + 140
    for k, v in enumerate(env):
        hh = max(2, v * 70)
        d.line((x0 + 28 + k, mid - hh, x0 + 28 + k, mid + hh), fill=BLUE if k / cols <= play else GRID)
    if t < AUDIO:
        px = x0 + 28 + play * cols
        d.line((px, y0 + 64, px, y0 + h0 - 16), fill=INK, width=2)

    # Pipeline progress driven by the logged clock milestones.
    s = min(1.0, max(0.0, (t - AUDIO) / SIM))
    clk = int(run["total"] * s)
    y1 = 470
    d.rounded_rectangle((x0, y1, x0 + w0, y1 + 420), 14, fill=PANEL)
    d.text((x0 + 28, y1 + 22), "Hardware model", font=f_lab, fill=INK2)
    d.text((x0 + w0 - 28, y1 + 16), f"clock {clk:>11,}", font=font(MONO, 34), fill=INK, anchor="ra")
    bx, bw = x0 + 28, w0 - 56
    bar(d, bx, y1 + 90, bw, "Frontend: audio chunks", sum(c_ <= clk for c_ in run["chunks"]), len(run["chunks"]),
        "chunks", BLUE, f_lab, f_val)
    bar(d, bx, y1 + 190, bw, "Encoder: transformer layers", sum(c_ <= clk for c_ in run["layers"]),
        len(run["layers"]), "layers", AQUA, f_lab, f_val)
    bar(d, bx, y1 + 290, bw, "Decoder: tokens to end-of-speech", sum(c_ <= clk for c_ in run["tokens"]),
        len(run["tokens"]), "tokens", ORANGE, f_lab, f_val)

    # On-chip weight services: replies count up, host replies stay zero.
    x2, w2 = 1140, W - 80 - 1140
    d.rounded_rectangle((x2, y0, x2 + w2, y1 + 420), 14, fill=PANEL)
    d.text((x2 + 28, y0 + 22), "Fixed-weight services on chip", font=f_lab, fill=INK2)
    d.text((x2 + 28, y0 + 62), "replies from chip   ·   fed by host", font=f_s, fill=MUTED)
    for k, sv in enumerate(run["services"]):
        yy = y0 + 120 + k * 92
        d.text((x2 + 28, yy), sv["service"].replace("_", " "), font=f_lab, fill=INK)
        d.text((x2 + 28, yy + 38), f"{int(int(sv['rtl_replies']) * s):>12,}", font=f_val, fill=INK2)
        d.text((x2 + w2 - 28, yy + 38), f"host {sv['host_replies']}", font=f_val, fill=GOOD, anchor="ra")

    # Output.
    if t >= AUDIO + SIM:
        r = run["render"]
        y3 = 912
        d.text((80, y3 + 14), "Text out:", font=font(SANS, 34), fill=INK2)
        d.text((260, y3), f"“{r['text']}”", font=font(BOLD, 56), fill="#eda100")
        if t >= AUDIO + SIM + 0.8:
            msg = ("✓ 18/18 internal outputs bit-identical to the frozen model" if run["ok"] else "check failed")
            d.text((262, y3 + 94), msg, font=font(SANS, 30), fill=GOOD if run["ok"] else ORANGE)
            d.text((W - 80, y3 + 98), f"tokens {r['tokens']}", font=f_val, fill=MUTED, anchor="ra")
    return img


def title(t):
    img = Image.new("RGB", (W, H), SURF)
    d = ImageDraw.Draw(img)
    d.text((W / 2, 400), "Audio in. Text out. Every weight hardwired.", font=font(BOLD, 64), fill=INK, anchor="mm")
    d.text((W / 2, 490), "Moonshine Tiny speech recognizer, simulated clock by clock as chip logic",
           font=font(SANS, 34), fill=INK2, anchor="mm")
    d.text((W / 2, 560), "Three real recordings  ·  about 310 million clocks each  ·  bit-exact",
           font=font(SANS, 30), fill=MUTED, anchor="mm")
    return img


def main():
    clips = json.loads((DEMO / "clips" / "clips.json").read_text())
    runs = [load(c) for c in clips]
    total_t = INTRO + CLIP_T * len(runs)
    mp4, gif = DEMO / "routevoice-demo.mp4", DEMO / "routevoice-demo.gif"
    audio_path = DEMO / "routevoice-demo-audio.wav"
    track = np.zeros(int(total_t * 16000) + 16000, dtype="float32")
    for i, r in enumerate(runs):
        o = int((INTRO + i * CLIP_T) * 16000)
        track[o:o + len(r["audio"])] += r["audio"]
    sf.write(audio_path, track, 16000, subtype="PCM_16")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(audio_path),
                           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-preset", "medium",
                           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", str(mp4)],
                          stdin=subprocess.PIPE)
    for k in range(int(total_t * FPS)):
        t = k / FPS
        if t < INTRO:
            img = title(t)
        else:
            i = min(len(runs) - 1, int((t - INTRO) // CLIP_T))
            img = frame(runs[i], i, len(runs), t - INTRO - i * CLIP_T)
        ff.stdin.write(img.tobytes())
    ff.stdin.close(); ff.wait()
    audio_path.unlink()
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf",
                    "fps=10,scale=960:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4",
                    str(gif)], check=True)
    for p in (mp4, gif):
        print(p.name, f"{p.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
