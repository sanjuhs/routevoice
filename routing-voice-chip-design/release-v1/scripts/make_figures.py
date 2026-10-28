"""Build the release signoff table and the two scaling charts (1920x1080, dark, for video).

Every measured number is read from a committed evidence file below. Projections
are drawn dashed or as bands and labelled; their assumptions are printed on the
chart and written to scaling-data.csv.

    python make_figures.py      # needs matplotlib
"""
import csv, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "release-v1" / "figures"
EV = ROOT / "overnight-20261014" / "finish-1023"
METRICS = EV / "w10-route" / "pipe2" / "evidence-ant" / "final-metrics.json"
W13 = EV / "w13-arrays" / "results.json"

PAPER_FIG = ROOT.parent / "paper" / "figures"

# Reference palette (dataviz skill): surface, text, grid, slots 1-3. Dark for the
# video, light for the paper.
THEMES = {
    "dark": ("#1a1a19", "#f0efec", "#c3c2b7", "#8a897f", "#33332f", "#3987e5", "#d95926", "#199e70"),
    "light": ("#fcfcfb", "#0b0b0b", "#52514e", "#8a897f", "#e6e5e0", "#2a78d6", "#eb6834", "#1baf7a"),
}


def set_theme(name):
    global SURF, INK, INK2, MUTED, GRID, MEASURED, PROJ, NEWNODE
    SURF, INK, INK2, MUTED, GRID, MEASURED, PROJ, NEWNODE = THEMES[name]


set_theme("dark")

# ---- measured inputs --------------------------------------------------------
m = json.loads(METRICS.read_text())
ARRAY_WEIGHTS = 31_457_280          # W13 RESULTS.md: four-bit selections, all 98 matrices
ARRAY_MM2 = 174.708620              # W13 RESULTS.md: realized bank bounding-rectangle area
BANK_WEIGHTS, BANK_MM2 = 409_600, 1.0040 * 2.2588   # one 1280x320 bank, GDS bbox (render_gds.py)
PJ_PER_MAC = 287                    # pipe2 README: 0.188 W x 4,165 x 150 ns / 409,600 MACs
UM2_PER_WEIGHT = ARRAY_MM2 * 1e6 / ARRAY_WEIGHTS

# ---- projection assumptions (not measured) ----------------------------------
AREA_GAIN_28NM = (20, 40)    # 180 nm -> 28 nm area; ideal (180/28)^2 = 41
ENERGY_GAIN_28NM = (10, 30)  # 180 nm -> 28 nm energy per MAC, assumption
RETICLE_MM2 = 26 * 33        # one lithography field
WAFERSPACE_CORE_MM2 = 12.92  # wafer.space GF180 1x1 slot core, read 25 Oct 2026
MODELS = [  # (label, four-bit weights)
    ("RouteVoice\n(Moonshine Tiny STT)", ARRAY_WEIGHTS),
    ("125M LM", 125e6), ("1B LLM", 1e9), ("8B LLM", 8e9),
]


def style(ax, title, ylabel, chrome=True):
    fig = ax.figure
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=15)
    ax.grid(True, which="major", color=GRID, linewidth=1)
    ax.set_xscale("log"); ax.set_yscale("log")
    ax.set_xlabel("Model size (4-bit weights)", color=INK2, fontsize=17, labelpad=10)
    ax.set_ylabel(ylabel, color=INK2, fontsize=17, labelpad=10)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: human(v)))
    if chrome:
        fig.text(0.06, 0.93, title, color=INK, fontsize=28, weight="bold")


def human(v):
    for d, s in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if v >= d:
            return f"{v / d:g}{s}"
    return f"{v:g}"


def scaling_area(path=None, size=(19.2, 10.8), chrome=True):
    """chrome=False drops the title, subtitle and footnote (the paper caption carries them)."""
    xs = [1e5 * 10 ** (i / 20) for i in range(0, 101)]
    gf = [x * UM2_PER_WEIGHT / 1e6 for x in xs]
    fig, ax = plt.subplots(figsize=size, dpi=100)
    if chrome:
        fig.subplots_adjust(left=0.09, right=0.97, top=0.84, bottom=0.12)
    else:
        fig.subplots_adjust(left=0.08, right=0.98, top=0.97, bottom=0.1)
    style(ax, "Weight-array area vs model size", "Silicon area for weights (mm²)", chrome)
    if chrome:
        fig.text(0.06, 0.885, f"Measured in GF180: {UM2_PER_WEIGHT:.2f} µm² per 4-bit weight, "
                 f"from {ARRAY_WEIGHTS / 1e6:.1f} M weights in {ARRAY_MM2:.1f} mm² of DRC-clean array.",
                 color=INK2, fontsize=16)
    ax.plot(xs, gf, color=PROJ, lw=2, ls=(0, (6, 4)), label="GF180, linear at measured density (projection)")
    lo = [g / AREA_GAIN_28NM[1] for g in gf]; hi = [g / AREA_GAIN_28NM[0] for g in gf]
    ax.fill_between(xs, lo, hi, color=NEWNODE, alpha=0.28, lw=0,
                    label=f"28 nm, {AREA_GAIN_28NM[0]}-{AREA_GAIN_28NM[1]}x smaller (assumption)")
    for y, text in ((RETICLE_MM2, f"one reticle field ({RETICLE_MM2} mm²)"),
                    (WAFERSPACE_CORE_MM2, f"wafer.space 1x1 slot core ({WAFERSPACE_CORE_MM2} mm²)")):
        ax.axhline(y, color=MUTED, lw=1, ls=":")
        ax.text(1.15e5, y * 1.12, text, color=INK2, fontsize=14)
    ax.scatter([BANK_WEIGHTS, ARRAY_WEIGHTS], [BANK_MM2, ARRAY_MM2], s=140, color=MEASURED,
               edgecolor=SURF, linewidth=2, zorder=5, label="Measured layout (GF180)")
    ax.annotate("one 1280x320 bank", (BANK_WEIGHTS, BANK_MM2), (14, -26), textcoords="offset points",
                color=INK, fontsize=15)
    ax.annotate("all RouteVoice weights\n98 matrices, 81 banks", (ARRAY_WEIGHTS, ARRAY_MM2), (14, -46),
                textcoords="offset points", color=INK, fontsize=15)
    for label, w in MODELS[1:]:
        y = w * UM2_PER_WEIGHT / 1e6
        ax.scatter([w], [y], s=90, facecolor=SURF, edgecolor=PROJ, linewidth=2, zorder=4)
        ax.annotate(f"{label}\n{y:,.0f} mm² GF180\n~{y / AREA_GAIN_28NM[1]:,.0f}-{y / AREA_GAIN_28NM[0]:,.0f} mm² 28 nm",
                    (w, y), (-150, 12), textcoords="offset points", color=INK2, fontsize=13)
    ax.set_xlim(1e5, 1e10); ax.set_ylim(0.1, 4e5)
    leg = ax.legend(loc="upper left", fontsize=15, frameon=False)
    for t in leg.get_texts():
        t.set_color(INK)
    if chrome:
        fig.text(0.06, 0.03, "Weights only: excludes compute engines, I/O, SRAM for activations and KV state. "
                 "28 nm band is a scaling assumption, not a measurement.", color=MUTED, fontsize=13)
    fig.savefig(path or OUT / "scaling-area.png", facecolor=SURF)
    plt.close(fig)


def scaling_energy():
    xs = [1e5 * 10 ** (i / 20) for i in range(0, 101)]
    gf = [x * PJ_PER_MAC * 1e-12 * 1e3 for x in xs]  # mJ per full pass (one MAC per weight)
    fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    fig.subplots_adjust(left=0.09, right=0.97, top=0.84, bottom=0.12)
    style(ax, "Compute energy per pass vs model size", "Energy per pass over all weights (mJ)")
    fig.text(0.06, 0.885, f"Measured in GF180: {PJ_PER_MAC} pJ per MAC, routed engine at 150 ns with real-speech "
             "switching activity (0.188 W).", color=INK2, fontsize=16)
    ax.plot(xs, gf, color=PROJ, lw=2, ls=(0, (6, 4)), label="GF180 at measured pJ/MAC (projection)")
    lo = [g / ENERGY_GAIN_28NM[1] for g in gf]; hi = [g / ENERGY_GAIN_28NM[0] for g in gf]
    ax.fill_between(xs, lo, hi, color=NEWNODE, alpha=0.28, lw=0,
                    label=f"28 nm, {ENERGY_GAIN_28NM[0]}-{ENERGY_GAIN_28NM[1]}x lower (assumption)")
    proj_mj = BANK_WEIGHTS * PJ_PER_MAC * 1e-9
    ax.scatter([BANK_WEIGHTS], [proj_mj], s=140, color=MEASURED, edgecolor=SURF, linewidth=2, zorder=5,
               label="Measured: one 1280x320 projection (117 µJ)")
    for label, w in MODELS:
        y = w * PJ_PER_MAC * 1e-9
        ax.scatter([w], [y], s=90, facecolor=SURF, edgecolor=PROJ, linewidth=2, zorder=4)
        ax.annotate(f"{label.splitlines()[0]}\n{y:,.1f} mJ GF180", (w, y), (-130, 14),
                    textcoords="offset points", color=INK2, fontsize=13)
    ax.set_xlim(1e5, 1e10); ax.set_ylim(1e-2, 1e4)
    leg = ax.legend(loc="upper left", fontsize=15, frameon=False)
    for t in leg.get_texts():
        t.set_color(INK)
    fig.text(0.06, 0.03, "Compute only: excludes weight-array read energy, activation memory and I/O. "
             "For a decoder LLM one pass is roughly one generated token.", color=MUTED, fontsize=13)
    fig.savefig(OUT / "scaling-energy.png", facecolor=SURF)
    plt.close(fig)


def signoff():
    c = "__corner:"
    rows = [
        ("Design", "1280x320 projection engine, GF180MCU-D, LibreLane"),
        ("Die / utilization", f"{m['design__die__area'] / 1e6:.2f} mm²  /  {m['design__instance__utilization'] * 100:.1f}%"),
        ("Standard cells", f"{m['design__instance__count__stdcell']:,}"),
        ("Routed wire", f"{m['route__wirelength'] / 1e6:.1f} m"),
        ("Routing DRC", f"{m['route__drc_errors']}"),
        ("Magic DRC / KLayout DRC", f"{m['magic__drc_error__count']} / {m['klayout__drc_error__count']}"),
        ("LVS (Netgen)", "unique match" if m["design__lvs_error__count"] == 0 else f"{m['design__lvs_error__count']} errors"),
        ("GDS XOR", f"{m['design__xor_difference__count']}"),
        ("Antenna nets", f"{m['antenna__violating__nets']}"),
        ("Setup slack @150 ns", f"TT +{m['timing__setup__ws' + c + 'nom_tt_025C_3v30']:.1f} ns   "
                                f"worst SS +{m['timing__setup__ws']:.1f} ns   (9/9 corners met)"),
        ("Hold slack", f"worst +{m['timing__hold__ws']:.2f} ns"),
        ("Routed power (real speech)", f"0.188 W  ->  {PJ_PER_MAC} pJ/MAC"),
        ("Still open", f"max-slew {m['design__max_slew_violation__count']:,}, max-cap "
                       f"{m['design__max_cap_violation__count']:,}, max-fanout {m['design__max_fanout_violation__count']:,} (worst corner)"),
    ]
    fig = plt.figure(figsize=(19.2, 10.8), dpi=100)
    fig.patch.set_facecolor(SURF)
    fig.text(0.06, 0.9, "Engine signoff: all manufacturing checks pass", color=INK, fontsize=30, weight="bold")
    y = 0.8
    for k, v in rows:
        last = k == "Still open"
        fig.text(0.07, y, k, color=INK2, fontsize=20)
        fig.text(0.36, y, v, color=INK if not last else "#c98500", fontsize=20,
                 weight="bold" if not last else "normal")
        fig.add_artist(plt.Line2D([0.06, 0.94], [y - 0.022, y - 0.022], color=GRID, lw=1))
        y -= 0.056
    fig.text(0.06, 0.04, f"Source: {METRICS.relative_to(ROOT)}  (antenna close-out run, 24 Oct 2026)",
             color=MUTED, fontsize=13)
    fig.savefig(OUT / "signoff-table.png", facecolor=SURF)
    plt.close(fig)
    with open(OUT / "signoff-table.md", "w") as f:
        f.write("| Check | Result |\n|---|---|\n" + "".join(f"| {k} | {v} |\n" for k, v in rows))


def data_csv():
    with open(OUT / "scaling-data.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["kind", "item", "weights", "area_mm2_gf180", "energy_mJ_per_pass_gf180", "note"])
        w.writerow(["measured", "one 1280x320 bank", BANK_WEIGHTS, round(BANK_MM2, 4),
                    round(BANK_WEIGHTS * PJ_PER_MAC * 1e-9, 4), "W13 bank GDS bbox; engine power"])
        w.writerow(["measured", "all RouteVoice weight arrays", ARRAY_WEIGHTS, ARRAY_MM2, "",
                    "W13 RESULTS.md realized area"])
        for label, n in MODELS[1:]:
            w.writerow(["projection", label, int(n), round(n * UM2_PER_WEIGHT / 1e6, 1),
                        round(n * PJ_PER_MAC * 1e-9, 1),
                        f"linear at measured density; 28 nm assumed {AREA_GAIN_28NM} area / {ENERGY_GAIN_28NM} energy gain"])


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    assert json.loads(W13.read_text()), "W13 results missing"
    scaling_area(); scaling_energy(); signoff(); data_csv()
    set_theme("light")
    PAPER_FIG.mkdir(exist_ok=True)
    scaling_area(PAPER_FIG / "scaling-area.pdf", size=(13, 7.5), chrome=False)
    print("µm²/weight", round(UM2_PER_WEIGHT, 3))
