"""Render a GF180 GDS as a zoom sequence of 1920x1080 PNGs for the release video.

Uses the `klayout` Python package (pip install klayout), headless. Each zoom
level shows its own layer set, so the wide views are not hidden under metal fill
and top-level power straps:

    die    (zoom < 3)    Metal4 routing only (everything else saturates)
    wide   (zoom < 20)   Metal3, Metal4 routing
    mid    (zoom < 150)  Metal1, Metal2, Metal3
    cells  (zoom >= 150) COMP (transistor diffusion), Poly2, Metal1, Via1
                         (Via1 positions program the weight-bank index bits)

Fill (datatype 4) is never drawn.

    python render_gds.py <file.gds> <out_dir> <name> [--zooms 1,8,64,400] [--cx 0.5 --cy 0.5]

zooms are magnifications of the full-die view; cx, cy pick the zoom centre as a
fraction of the die bounding box.
"""
import argparse, json, os
import klayout.db as db
import klayout.lay as lay

W, H = 1920, 1080
# (name, layer, datatype, colour, dither pattern); colours are the dark-mode
# categorical slots of the release figures.
LAYERS = {
    "COMP": (22, 0, 0x199E70, 2), "Poly2": (30, 0, 0xE66767, 2),
    "Metal1": (34, 0, 0x3987E5, 5), "Via1": (35, 0, 0xEDA100, 0), "Metal2": (36, 0, 0xD95926, 9),
    "Metal3": (42, 0, 0x199E70, 13), "Metal4": (46, 0, 0x9085E9, 9),
}
SETS = {
    "die": ["Metal4"],
    "wide": ["Metal4", "Metal3"],
    "mid": ["Metal3", "Metal2", "Metal1"],
    "cells": ["Via1", "Metal1", "Poly2", "COMP"],
}


def layer_set(z):
    return "die" if z < 3 else "wide" if z < 20 else "mid" if z < 150 else "cells"


def show(view, names):
    view.clear_layers()
    for n in names:
        l, d, c, dither = LAYERS[n]
        p = lay.LayerPropertiesNode()
        p.source = f"{l}/{d}@1"
        p.name = n
        p.fill_color = p.frame_color = c
        p.dither_pattern = dither
        p.transparent = True
        view.insert_layer(view.end_layers(), p)


ap = argparse.ArgumentParser()
ap.add_argument("gds"); ap.add_argument("out"); ap.add_argument("name")
ap.add_argument("--zooms", default="1,8,64,400")
ap.add_argument("--cx", type=float, default=0.5); ap.add_argument("--cy", type=float, default=0.5)
a = ap.parse_args()

view = lay.LayoutView()
view.set_config("background-color", "#000000")
view.set_config("grid-visible", "false")
view.set_config("text-visible", "false")
view.load_layout(a.gds, False)
view.max_hier()
cell = view.active_cellview().cell
box = cell.dbbox()
print(f"top={cell.name} bbox={box.width():.1f} x {box.height():.1f} um")
os.makedirs(a.out, exist_ok=True)
centre = db.DPoint(box.left + a.cx * box.width(), box.bottom + a.cy * box.height())
frames = []
for z in (float(s) for s in a.zooms.split(",")):
    names = SETS[layer_set(z)]
    show(view, names)
    w = max(box.width(), box.height() * W / H) * 1.04 / z
    h = w * H / W
    target = db.DBox(centre.x - w / 2, centre.y - h / 2, centre.x + w / 2, centre.y + h / 2)
    view.zoom_box(target)
    path = os.path.join(a.out, f"{a.name}-zoom{int(z):04d}.png")
    view.save_image_with_options(path, W, H, 0, 2, 0, target, False)
    frames.append(dict(png=os.path.basename(path), zoom=z, field_um=[round(w, 2), round(h, 2)], layers=names))
    print(f"{path}: field {w:.1f} x {h:.1f} um, layers {names}")
with open(os.path.join(a.out, f"{a.name}.json"), "w") as f:
    json.dump(dict(gds=os.path.basename(a.gds), top=cell.name,
                   die_um=[round(box.width(), 2), round(box.height(), 2)], frames=frames), f, indent=1)
