"""Read completed OpenROAD placement/PDN/IR evidence without running EDA."""
import json,re
from pathlib import Path
W=Path(__file__).resolve().parent

def summarize(run):
    p = W / 'runs' / run['name']
    m = json.loads((p / 'manifest.json').read_text())
    log = (W / 'logs' / (run['name'] + '.log')).read_text()
    drops = [float(v) for v in re.findall('Worstcase IR drop:\\s*([\\d.eE+-]+)', log)]
    assert len(drops) == 2, run['name']
    short = json.loads((p / 'floorplan.odb.shorts.json').read_text())
    boxes = [(t['x'] - 30, t['y'] - 30, t['x'] + t['w'] + 30, t['y'] + t['h'] + 30) for t in m['tiles']]
    overlaps = sum((min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1]) for i, a in enumerate(boxes) for b in boxes[i + 1:]))
    legal = not overlaps and all((a[0] >= 700 and a[1] >= 700 and (a[2] <= m['die_width_mm'] * 1000 - 700) and (a[3] <= m['die_height_mm'] * 1000 - 700) for a in boxes))
    r = {k: v for k, v in m.items() if k not in ['tiles', 'pads']}
    r.update(name=run['name'], placement_legal_check=legal, macro_overlap_count=overlaps, pdn_pass=all((f'W3_CONNECTIVITY_{net}_PASS' in log for net in ['VDD', 'VSS'])), ir_solver_pass=all((f'W3_IR_{net}_PASS' in log for net in ['VDD', 'VSS'])), worst_ir_drop_v=drops[0], worst_ground_rise_v=drops[1], combined_worst_bound_v=sum(drops), ir_5pct_pass=sum(drops) < 0.165, short_check=short, execution=json.loads((p / 'execution.json').read_text()), fits_assumed26x33_reticle=min(m['die_width_mm'], m['die_height_mm']) <= 26 and max(m['die_width_mm'], m['die_height_mm']) <= 33, requires_custom_sram=m['memory'] == 'sram_dense_custom', requires_accuracy_revalidation=m['levers'] == 'on', artifacts={k: str((p / v).relative_to(W)) for k, v in [('png', 'floorplan.png'), ('heatmap', 'ir_heatmap.png'), ('def', 'floorplan.def'), ('odb', 'floorplan.odb'), ('tcl', 'floorplan.tcl'), ('lef', 'macros.lef'), ('voltage_vdd', 'VDD_voltage.rpt'), ('voltage_vss', 'VSS_voltage.rpt')]})
    r['physical_screen_pass'] = legal and r['pdn_pass'] and r['ir_solver_pass'] and r['ir_5pct_pass'] and (short['short_count'] == 0)
    return r
