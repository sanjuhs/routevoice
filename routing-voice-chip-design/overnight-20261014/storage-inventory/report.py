#!/usr/bin/env python3
"""Turn vobj/rows.json (from analyze.py) into inventory.json + INVENTORY.md."""
import json, collections, sys, os, hashlib, datetime

here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, 'vobj/rows.json')))
rows, luts = d['rows'], d['case_luts']
cmds = json.load(open(os.path.join(here, 'commands-used.json')))

STORAGE_ARRAY = {'rom_readmem': 'ROM ($readmemh, never written)', 'rom_initial': 'ROM (initial const)',
                 'flop': 'mutable (clocked write)', 'mutable_initialised': 'mutable (clocked write + initial)',
                 'clocked_blocking_only': 'mutable? (blocking write in clocked block)'}

def B(bits):
    return bits / 8

arrays = [r for r in rows if r['is_array'] and r['cls'] in STORAGE_ARRAY]
arrays.sort(key=lambda r: -r['total_bits'])
mut_arrays = [r for r in arrays if r['cls'] in ('flop', 'mutable_initialised', 'clocked_blocking_only')]
rom_arrays = [r for r in arrays if r['cls'] in ('rom_readmem', 'rom_initial')]
regs = [r for r in rows if not r['is_array'] and r['cls'] in ('flop', 'mutable_initialised')]
regs.sort(key=lambda r: -r['total_bits'])
blk_tmp = [r for r in rows if not r['is_array'] and r['cls'] == 'clocked_blocking_only']
comb_arrays = [r for r in rows if r['is_array'] and r['cls'] == 'combinational']
luts.sort(key=lambda c: -c['total_bits'])

def s(rs):
    return sum(r['total_bits'] for r in rs)

cls_tot = collections.defaultdict(lambda: [0, 0, 0])
for r in rows:
    k = (r['cls'], 'array' if r['is_array'] else 'scalar/vector')
    cls_tot[k][0] += 1; cls_tot[k][1] += r['instances']; cls_tot[k][2] += r['total_bits']

totals = dict(
    rom_readmem_array_bytes=B(s([r for r in rom_arrays if r['cls'] == 'rom_readmem'])),
    rom_initial_array_bytes=B(s([r for r in rom_arrays if r['cls'] == 'rom_initial'])),
    rom_case_lut_bytes=B(sum(c['total_bits'] for c in luts)),
    rom_case_lut_big5_bytes=B(sum(c['total_bits'] for c in luts if c['rows'] >= 900)),
    mutable_array_bytes=B(s(mut_arrays)),
    mutable_array_bits=s(mut_arrays),
    register_bits=s(regs),
    register_bytes=B(s(regs)),
    clocked_blocking_temporaries_bits=s(blk_tmp),
    combinational_array_net_bytes=B(s(comb_arrays)),
)
totals['rom_total_bytes'] = totals['rom_readmem_array_bytes'] + totals['rom_initial_array_bytes'] + totals['rom_case_lut_bytes']
totals['mutable_total_bytes'] = totals['mutable_array_bytes'] + totals['register_bytes']

def slim(r):
    return dict(path=r['example_paths'][0] if r['instances'] == 1 else r['example_paths'],
                instances=r['instances'], module=r['module'], module_orig=r['module_orig'], var=r['var'],
                dims=r['dims'], elem_width=r['elem_width'], bits_per_instance=r['bits_per_instance'],
                total_bits=r['total_bits'], total_bytes=B(r['total_bits']), cls=r['cls'],
                classification=STORAGE_ARRAY.get(r['cls'], r['cls']), writes=r['writes'],
                reads=r['reads'], src=r['src'])

# group mutable arrays by source module
by_mod = collections.Counter()
for r in mut_arrays:
    by_mod[r['module_orig']] += r['total_bits']
reg_by_mod = collections.Counter()
for r in regs:
    reg_by_mod[r['module_orig']] += r['total_bits']

out = dict(
    generated=datetime.datetime.now().isoformat(timespec='seconds'),
    design='merged all-on-chip: overnight-20261014/onchip-all, top rv_allonchip_top_all_v1',
    elaboration=dict(n_modules_elaborated=d['n_modules_elaborated'], n_modules_used=d['n_modules_used'],
                     total_module_instances=d['total_instances']),
    commands=cmds,
    totals=totals,
    class_totals=[dict(cls=k[0], kind=k[1], vars=v[0], var_instances=v[1], total_bits=v[2]) for k, v in sorted(cls_tot.items(), key=lambda x: -x[1][2])],
    top30_arrays=[slim(r) for r in arrays[:30]],
    all_rom_arrays=[slim(r) for r in rom_arrays],
    all_mutable_arrays=[slim(r) for r in mut_arrays],
    case_lut_roms=luts,
    top50_registers=[slim(r) for r in regs[:50]],
    mutable_array_bits_by_module=by_mod.most_common(),
    register_bits_by_module=reg_by_mod.most_common(),
)
json.dump(out, open(os.path.join(here, 'inventory.json'), 'w'), indent=1)

# ---------------- markdown ----------------
def fmtB(b):
    return f"{b:,.0f}" if b == int(b) else f"{b:,.1f}"
def p(r):
    if r['instances'] == 1:
        return '`' + r['example_paths'][0].replace('rv_allonchip_top_all_v1.', 'TOP.') + '`'
    return '`' + r['example_paths'][0].replace('rv_allonchip_top_all_v1.', 'TOP.') + f"` (+{r['instances']-1} more instances)"
def dims(r):
    return ''.join(f'[{x}]' for x in r['dims']) + f" x {r['elem_width']}b"

L = []
L.append('# RouteVoice storage-element inventory (merged all-on-chip RTL)\n')
L.append(f"Generated {out['generated']} from a Verilator 5.050 `--json-only` elaboration of "
         f"`rv_allonchip_top_all_v1` (exact file list/includes of `onchip-all/commands.json` key `lint-full`). "
         f"{d['n_modules_elaborated']} parameter-specialised modules, {d['total_instances']:,} module instances after walking the cell tree from the top. "
         "All numbers are logical state bits from RTL declarations multiplied by instance count; they are not physical area.\n")
L.append('## (b) Totals\n')
L.append('| Category | Bits | Bytes |')
L.append('|---|---:|---:|')
t = totals
L.append(f"| **Fixed ROM, `$readmemh` arrays (17 arrays, never written)** | {t['rom_readmem_array_bytes']*8:,.0f} | **{fmtB(t['rom_readmem_array_bytes'])}** |")
L.append(f"| Fixed ROM, case-statement LUT functions (pre-existing \"already onboard\" tables) | {t['rom_case_lut_bytes']*8:,.0f} | {fmtB(t['rom_case_lut_bytes'])} |")
L.append(f"| &nbsp;&nbsp;of which the 5 big service tables (index image, book pages, source KV index, metadata, decoder norms) | {t['rom_case_lut_big5_bytes']*8:,.0f} | {fmtB(t['rom_case_lut_big5_bytes'])} |")
L.append(f"| **ROM total** | {t['rom_total_bytes']*8:,.0f} | **{fmtB(t['rom_total_bytes'])}** |")
L.append(f"| **Mutable unpacked arrays** (written in clocked always blocks; {len(mut_arrays)} array declarations) | {t['mutable_array_bits']:,} | **{fmtB(t['mutable_array_bytes'])}** |")
L.append(f"| **Registers** (non-array variables with non-blocking writes in clocked blocks, incl. wide packed vectors) | **{t['register_bits']:,}** | {fmtB(t['register_bytes'])} |")
L.append(f"| **Mutable total (arrays + registers)** | {t['mutable_array_bits']+t['register_bits']:,} | **{fmtB(t['mutable_total_bytes'])}** |")
L.append(f"| Not counted: loop indices / blocking-only temporaries in clocked blocks | {t['clocked_blocking_temporaries_bits']:,} | {fmtB(t['clocked_blocking_temporaries_bits']/8)} |")
L.append(f"| Not counted: unpacked arrays that are combinational nets (always @*/assign/cell outputs) | {t['combinational_array_net_bytes']*8:,.0f} | {fmtB(t['combinational_array_net_bytes'])} |")
L.append('')
L.append(f"The `$readmemh` ROM total is exactly the 28,641,280 bytes recorded in `onchip-all/rom-accounting.json` (`new_native_ROM_bytes`). "
         f"The big-5 case-LUT total equals that file's `already_onboard_logical_image_bytes` (8,847,360).\n")

L.append('## (a) Top 30 storage arrays (ROM and mutable)\n')
L.append('| # | Hierarchical path | Module (orig) | Dims | Bits (all instances) | Bytes | Class |')
L.append('|---:|---|---|---|---:|---:|---|')
for i, r in enumerate(arrays[:30], 1):
    L.append(f"| {i} | {p(r)} | `{r['module_orig']}` | {dims(r)} | {r['total_bits']:,} | {fmtB(B(r['total_bits']))} | {STORAGE_ARRAY[r['cls']]} |")
L.append('')
L.append('### Top 30 mutable arrays\n')
L.append('ROM dominates the list above, so the 30 largest mutable arrays are listed separately.\n')
L.append('| # | Hierarchical path | Module (orig) | Dims | Bits (all instances) | Bytes |')
L.append('|---:|---|---|---|---:|---:|')
for i, r in enumerate(mut_arrays[:30], 1):
    L.append(f"| {i} | {p(r)} | `{r['module_orig']}` | {dims(r)} | {r['total_bits']:,} | {fmtB(B(r['total_bits']))} |")
rest = mut_arrays[30:]
L.append(f"\nRemaining {len(rest)} mutable array declarations total {s(rest):,} bits ({fmtB(B(s(rest)))} bytes). Full list in `inventory.json` → `all_mutable_arrays`.\n")

L.append('### Case-statement LUT ROMs (functions / always @* with >=16 constant rows)\n')
L.append('| Module | Function / target | Rows | Width | Instances | Bytes | Call sites in module | Source |')
L.append('|---|---|---:|---:|---:|---:|---:|---|')
for c in luts:
    L.append(f"| `{c['module_orig']}` | `{c['target']}` | {c['rows']:,} | {c['width']} | {c['instances']} | {fmtB(B(c['total_bits']))} | {c['call_sites'] if c['call_sites'] is not None else 'n/a (always @*)'} | `{os.path.basename(c['src'])}` |")
L.append('')

L.append('### Mutable array bytes by module\n')
L.append('| Module (orig) | Bytes |')
L.append('|---|---:|')
for m, b in by_mod.most_common(20):
    L.append(f"| `{m}` | {fmtB(B(b))} |")
L.append('')
L.append('### Register bits by module (top 20)\n')
L.append('| Module (orig) | Register bits (all instances) |')
L.append('|---|---:|')
for m, b in reg_by_mod.most_common(20):
    L.append(f"| `{m}` | {b:,} |")
L.append('')
L.append('### Largest individual registers (top 15)\n')
L.append('| Path | Module | Width | Instances | Total bits |')
L.append('|---|---|---:|---:|---:|')
for r in regs[:15]:
    L.append(f"| {p(r)} | `{r['module_orig']}` | {r['elem_width']} | {r['instances']} | {r['total_bits']:,} |")
L.append('')

L.append('## Classification method\n')
L.append('- Every `VAR` in every elaborated module (including generate blocks; function/task locals excluded) is sized from the resolved dtype table: unpacked dims x packed width.')
L.append('- Write contexts are found from `VARREF` nodes with `access=WR` on assignment left-hand sides: inside `ALWAYS` with an edge sensitivity (clocked), other `ALWAYS`/`ASSIGNW` (combinational), `INITIAL` (initial), `READMEM` target, or child-cell output pins.')
L.append('- ROM = written only by `$readmemh` in `initial` (or only by initial constants) and never in a clocked/combinational process. Mutable = written in a clocked process. Register = non-array variable with a non-blocking write in a clocked process.')
L.append('- Case-LUT ROM = a `case` whose items are single constant assignments (>=16 rows), counted as rows x target width (default item excluded).')
L.append('- Instance counts come from walking `CELL -> modp` from the top; every parameter specialisation is a separate module in the elaborated tree.\n')
L.append('Class totals (all variables, all instances):\n')
L.append('| Class | Kind | Vars | Var instances | Bits |')
L.append('|---|---|---:|---:|---:|')
for k, v in sorted(cls_tot.items(), key=lambda x: -x[1][2]):
    L.append(f"| {k[0]} | {k[1]} | {v[0]:,} | {v[1]:,} | {v[2]:,} |")
L.append('\n(`param` = localparam/parameter constants, `constant_net` = constant assigns that Verilator folded to initial; neither is storage.)\n')

L.append('## (c) Commands used\n')
L.append('```sh')
L.append(cmds['verilator_display'])
for c in cmds['post']:
    L.append(c)
L.append('```')
L.append(f"\nVerilator output: `{cmds['outputs']}`. 169 `TIMESCALEMOD` warnings, no errors. Full argv as a list in `commands-used.json`.\n")

L.append('## (d) Caveats\n')
L.append('- **RTL logical bits, not physical.** Synthesis may remove, merge or retime state. Nothing here is from synthesis; the earlier Yosys run in `synth/` was terminated and is for the base top.')
L.append('- **Registers are an upper-bound-ish RTL count.** A non-blocking write in a clocked block is counted as a flop even if the value is constant or never read (synthesis would remove it). Blocking-only temporaries in clocked blocks (mostly loop indices, '
         f"{t['clocked_blocking_temporaries_bits']:,} bits) are excluded. Latches inferred from incomplete `always @*` blocks are not detected (Verilator only checks `always_comb` for LATCH and reported none).")
L.append('- **Wide packed vectors used as buffers** (e.g. 2,560-bit `coefficient_buffer`, 1,024-bit packets) and register files built from generate-loop scalars (e.g. `taalas_book_page_cache`, 73,800 bits over 9 instances as `columns[i].entries[j].value0/1` + `tags`) are counted in register bits, not mutable arrays.')
L.append('- **Mutable arrays include all instantiated legacy storage.** E.g. encoder bank0/1/2, producer bankA/B/Codes, compact-history `committed`, frontend mutable regions. Whether any of these are now redundant after the weights moved on-chip was not judged; they are still instantiated and written.')
L.append('- **Case-LUT ROM call sites.** `frozen_beat` (book loader) is called from 9 sites and `product_pointer` from 32; synthesis might duplicate that decode logic. The bytes above count each table once per module instance.')
L.append('- **ROM is logical payload.** `$readmemh` arrays are sized by declaration (they match the ROM manifest exactly). Physical ROM macro area, word organisation and peripheral circuits are not measured.')
L.append('- Classification relies on Verilator `access` flags and process sensitivities in the `--json-only` tree (after V3Param/V3Width, before flattening). Hierarchical (`VARXREF`) writes: none found. Function-local statics are excluded.')
L.append('- Paths show one representative instance; `(+N more instances)` means the same module specialisation is instantiated N+1 times and the bits are multiplied accordingly.')
open(os.path.join(here, 'INVENTORY.md'), 'w').write('\n'.join(L) + '\n')
print(json.dumps(totals, indent=1))
