#!/usr/bin/env python3
"""Storage inventory from Verilator 5.050 --json-only elaborated tree.

Usage: python3 analyze.py vobj/top.tree.json vobj/top.tree.meta.json out.json
"""
import json, sys, collections, re

tree_path, meta_path, out_path = sys.argv[1:4]
t = json.load(open(tree_path))
meta = json.load(open(meta_path))
files = {k: v['filename'] for k, v in meta.get('files', {}).items()}

# ---------------- dtypes ----------------
dt = {}
def collect_dtypes(n):
    if isinstance(n, dict):
        if n.get('type', '').endswith('DTYPE') and 'addr' in n:
            dt[n['addr']] = n
        for v in n.values():
            if isinstance(v, (list, dict)):
                collect_dtypes(v)
    elif isinstance(n, list):
        for v in n:
            collect_dtypes(v)
collect_dtypes(t['miscsp'])
collect_dtypes(t['modulesp'])

KW_W = {'integer': 32, 'int': 32, 'byte': 8, 'shortint': 16, 'longint': 64,
        'real': 64, 'logic': 1, 'bit': 1, 'reg': 1, 'time': 64}

def const_val(c):
    s = c['name']
    m = re.match(r"(\d+)?'s?([hdbo])([0-9a-fA-F_xz]+)", s)
    if not m:
        return int(s)
    base = {'h': 16, 'd': 10, 'b': 2, 'o': 8}[m.group(2)]
    return int(m.group(3).replace('_', ''), base)

def dshape(addr):
    """returns (unpacked dims list, element packed width, kind)"""
    d = dt[addr]
    ty = d['type']
    if ty == 'BASICDTYPE':
        kw = d.get('keyword')
        if kw == 'string':
            return [], 0, 'string'
        r = d.get('range')
        if r:
            a, b = (int(x) for x in r.split(':'))
            return [], abs(a - b) + 1, kw
        return [], KW_W.get(kw, 1), kw
    if ty == 'UNPACKARRAYDTYPE':
        rg = d['rangep'][0]
        lo = const_val(rg['leftp'][0]); hi = const_val(rg['rightp'][0])
        n = abs(hi - lo) + 1
        sub = d.get('refDTypep') or d.get('childDTypep')
        dims, w, kw = dshape(sub if isinstance(sub, str) else sub[0]['addr'])
        return [n] + dims, w, kw
    if ty == 'VOIDDTYPE':
        return [], 0, 'void'
    raise ValueError(ty)

# ---------------- modules ----------------
mods = {m['addr']: m for m in t['modulesp']}
top = [m for m in t['modulesp'] if m.get('level') == 1 or m['name'] == 'rv_allonchip_top_all_v1']

EDGE = {'POS', 'NEG', 'BOTH', 'EDGE'}

def sentree_clocked(al):
    for st in al.get('sentreep', []) or []:
        for si in st.get('sensesp', []) or []:
            if si.get('edgeType') in EDGE:
                return True
    return False

class ModInfo:
    def __init__(self, m):
        self.m = m
        self.vars = {}       # addr -> dict
        self.cells = []      # (path, modp)
        self.writes = collections.defaultdict(set)   # var addr -> set(contexts)
        self.readmem = collections.defaultdict(list)
        self.reads = collections.Counter()
        self.case_luts = []
        self.cur_func = None
        self.func_names = []
        self.funcrefs = collections.Counter()

def analyze_module(m):
    mi = ModInfo(m)

    def walk(n, gpath, ctx, in_lhs, in_dly):
        if isinstance(n, list):
            for v in n:
                walk(v, gpath, ctx, in_lhs, in_dly)
            return
        if not isinstance(n, dict):
            return
        ty = n.get('type')
        if ty == 'GENBLOCK':
            nm = n.get('name') or ''
            gp = gpath + (nm + '.' if nm else '')
            for k in ('genforp', 'itemsp', 'stmtsp'):
                if k in n:
                    walk(n[k], gp, ctx, False, False)
            return
        if ty == 'VAR':
            if ctx in ('func',):
                return
            dims, w, kw = dshape(n['dtypep'])
            mi.vars[n['addr']] = dict(name=gpath + n['name'], varType=n.get('varType'),
                                      lifetime=n.get('lifetime'), direction=n.get('direction'),
                                      dims=dims, width=w, kw=kw, loc=n.get('loc'),
                                      has_value=bool(n.get('valuep')))
            return
        if ty == 'CELL':
            mi.cells.append((gpath + n['name'], n['modp']))
            walk(n.get('pinsp', []), gpath, 'cellpin', True, False)
            return
        if ty == 'CASE':
            items = n.get('itemsp', [])
            const_items = 0; lhs_w = collections.Counter(); 
            n_default = 0
            for it in items:
                if not it.get('condsp'):
                    n_default += 1
                    continue
                st = it.get('stmtsp', [])
                if len(st) == 1 and st[0].get('type') in ('ASSIGN', 'ASSIGNDLY') and st[0]['rhsp'][0].get('type') == 'CONST':
                    const_items += 1
                    lhs = st[0]['lhsp'][0]
                    _, w, _ = dshape(lhs['dtypep'])
                    lhs_w[(lhs.get('name'), w)] += 1
            if const_items >= 16 and lhs_w:
                (lname, w), cnt_ = lhs_w.most_common(1)[0]
                mi.case_luts.append(dict(where=gpath + (mi.cur_func or ''), target=lname, rows=cnt_, width=w,
                                         bits=cnt_ * w, total_items=len(items), default_items=n_default, loc=n.get('loc'), ctx=ctx))
        if ty in ('FUNC', 'TASK'):
            mi.cur_func = n.get('name')
            mi.func_names.append(n.get('name'))
            walk(n.get('stmtsp', []), gpath, 'func', False, False)
            mi.cur_func = None
            return
        if ty == 'FUNCREF':
            mi.funcrefs[n.get('name')] += 1
        if ty == 'ALWAYS':
            c = 'clocked' if sentree_clocked(n) else ('cont' if n.get('keyword') == 'cont_assign' else 'comb')
            walk(n.get('stmtsp', []), gpath, c, False, False)
            return
        if ty in ('INITIAL', 'INITIALSTATIC', 'INITIALAUTOMATIC', 'FINAL'):
            walk(n.get('stmtsp', []), gpath, 'initial', False, False)
            return
        if ty == 'ASSIGNW':
            walk(n.get('rhsp', []), gpath, 'cont', False, False)
            walk(n.get('lhsp', []), gpath, 'cont', True, False)
            return
        if ty in ('ASSIGN', 'ASSIGNDLY'):
            walk(n.get('rhsp', []), gpath, ctx, False, False)
            walk(n.get('lhsp', []), gpath, ctx, True, ty == 'ASSIGNDLY')
            return
        if ty == 'READMEM':
            for mp in n.get('memp', []):
                if mp.get('type') == 'VARREF':
                    mi.readmem[mp['varp']].append(n.get('loc'))
                    mi.writes[mp['varp']].add('initial:readmem')
            for k in ('filenamep', 'lsbp', 'msbp'):
                walk(n.get(k, []), gpath, ctx, False, False)
            return
        if ty == 'VARREF':
            acc = n.get('access')
            if acc in ('WR', 'RW') and in_lhs:
                tag = ctx + (':nba' if in_dly else ':blk')
                mi.writes[n['varp']].add(tag)
            elif acc in ('WR', 'RW'):
                mi.writes[n['varp']].add(ctx + ':other')
            else:
                mi.reads[n['varp']] += 1
            return
        if ty in ('ARRAYSEL', 'SEL'):
            # base is first operand (fromp), index exprs are reads
            walk(n.get('fromp', []), gpath, ctx, in_lhs, in_dly)
            for k, v in n.items():
                if k != 'fromp' and isinstance(v, list):
                    walk(v, gpath, ctx, False, False)
            return
        for k, v in n.items():
            if isinstance(v, (list, dict)) and k not in ('dtypep',):
                walk(v, gpath, ctx, in_lhs, in_dly)

    walk(m.get('stmtsp', []), '', 'module', False, False)
    return mi

infos = {a: analyze_module(m) for a, m in mods.items()}

# ---------------- hierarchy ----------------
inst_paths = collections.defaultdict(list)
inst_count = collections.Counter()
def descend(maddr, path, depth=0):
    inst_count[maddr] += 1
    if len(inst_paths[maddr]) < 8:
        inst_paths[maddr].append(path)
    for cpath, cmod in infos[maddr].cells:
        descend(cmod, path + '.' + cpath, depth + 1)
topm = [m for m in t['modulesp'] if m['name'] == 'rv_allonchip_top_all_v1']
assert len(topm) == 1, [m['name'] for m in top]
descend(topm[0]['addr'], 'rv_allonchip_top_all_v1')

# ---------------- classify ----------------
def classify(v, wr, rm):
    ctxs = {w.split(':')[0] for w in wr}
    kinds = set(wr)
    if v['varType'] in ('LPARAM', 'GPARAM', 'GENVAR'):
        return 'param'
    if v['lifetime'] in ('VAUTOM', 'VAUTOMI'):
        return 'automatic'
    if 'clocked' in ctxs:
        if 'initial' in ctxs:
            return 'mutable_initialised'
        if any(k.endswith(':nba') for k in kinds if k.startswith('clocked')):
            return 'flop'
        return 'clocked_blocking_only'
    if ctxs & {'comb', 'cont', 'module', 'cellpin'}:
        return 'combinational'
    if 'initial' in ctxs:
        if rm:
            return 'rom_readmem'
        return 'rom_initial' if v['dims'] else 'constant_net'
    if v['has_value']:
        return 'rom_const_init'
    if v['direction'] == 'INPUT':
        return 'input_port'
    if 'func' in ctxs:
        return 'func_written'
    return 'undriven_or_child_driven'

rows = []
for maddr, n in inst_count.items():
    mi = infos[maddr]
    for vaddr, v in mi.vars.items():
        cls = classify(v, mi.writes.get(vaddr, set()), mi.readmem.get(vaddr))
        elems = 1
        for d in v['dims']:
            elems *= d
        bits = elems * v['width']
        rows.append(dict(module=mi.m['name'], module_orig=mi.m.get('origName'),
                         var=v['name'], dims=v['dims'], elem_width=v['width'],
                         elements=elems, bits_per_instance=bits, instances=n,
                         total_bits=bits * n, cls=cls, is_array=bool(v['dims']),
                         writes=sorted(mi.writes.get(vaddr, set())),
                         readmem=bool(mi.readmem.get(vaddr)),
                         reads=mi.reads.get(vaddr, 0),
                         src=(files.get(v['loc'].split(',')[0], '?') + ':' + v['loc'].split(',')[1].split(':')[0]) if v.get('loc') else '?',
                         example_paths=[p + '.' + v['name'] for p in inst_paths[maddr][:4]]))

luts = []
for maddr, n in inst_count.items():
    mi = infos[maddr]
    for c in mi.case_luts:
        fn = c['where'].split('.')[-1] if c['where'] else ''
        luts.append(dict(c, module=mi.m['name'], module_orig=mi.m.get('origName'), instances=n,
                         total_bits=c['bits'] * n, call_sites=mi.funcrefs.get(fn, None),
                         src=files.get(c['loc'].split(',')[0], '?') + ':' + c['loc'].split(',')[1].split(':')[0],
                         example_paths=inst_paths[maddr][:4]))
json.dump(dict(rows=rows, case_luts=luts, n_modules_elaborated=len(mods), n_modules_used=len(inst_count),
               total_instances=sum(inst_count.values())), open(out_path, 'w'))
print('modules', len(mods), 'used', len(inst_count), 'instances', sum(inst_count.values()), 'rows', len(rows))
