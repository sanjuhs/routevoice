from pathlib import Path
import os,sys,json,subprocess,shutil,time,xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
import numpy as np
W=Path(__file__).resolve().parents[1];R=W.parents[1];O=W/'base'
PDK=R/'pdks/gf180mcuD'; PDROOT=PDK.resolve().parent
def tool(name,pattern):
    return shutil.which(name) or str(next(Path('/nix/store').glob(pattern)))
klayout=tool('klayout','*klayout*/bin/klayout');magic=tool('magic','*magic*/bin/magic');netgen=tool('netgen','*netgen*/bin/netgen')
def run(cmd,log):
    assert shutil.disk_usage(W).free>=22*2**30
    with (O/'commands.jsonl').open('a') as f:f.write(json.dumps(cmd)+'\n')
    t=time.time()
    with (O/log).open('w') as f:r=subprocess.run(['nice','-n','10']+cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PDK_ROOT=str(PDROOT),TMPDIR=str(W/'tmp')),timeout=1800)
    print(log,r.returncode,round(time.time()-t,2),flush=True)
    assert r.returncode==0,(log,r.returncode)
report={}
for name,top,mode in [('tile0','RV_K64_CELL_TILE_00','flat'),('array-core','RV_K64_CELL_ARRAY_CORE','deep')]:
    options={'input':O/f'{name}.gds','report':O/f'{name}.lyrdb','topcell':top,'feol':'true','beol':'true','conn_drc':'true','offgrid':'true','metal_top':'11K','metal_level':'5LM','mim_option':'B','run_mode':mode,'thr':'2'}
    cmd=[klayout,'-b','-r',str(R/'experiments/taalas-access/main.drc')]
    for k,v in options.items():cmd+=['-rd',f'{k}={v}']
    run(cmd,f'{name}-drc.log')
    n=len(ET.parse(O/f'{name}.lyrdb').getroot().findall('./items/item'))
    report[name]={'drc_markers':n,'scope':'GF180 FEOL BEOL connectivity offgrid; density and antenna excluded','hierarchical_input':name=='array-core'}
    (O/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
    print('W5-STATUS:',name,'DRC markers',n,flush=True)
top='RV_K64_CELL_TILE_00'
(O/'extract.tcl').write_text(f'''gds readonly true
gds read tile0.gds
load {top}
flatten W5_TILE0_FLAT
load W5_TILE0_FLAT
extract all
ext2spice lvs
ext2spice -o tile0-extracted.spice
quit -noprompt
''')
run([magic,'-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'],'tile0-magic.log')
indices=np.load(W/'indices.npy')
ports=['VSS']+[f'WL{r}' for r in range(64)]+[f'IDX{c}_{b}' for c in range(320) for b in range(4)]
lines=['* independent schematic from admitted K64 indices','.subckt W5_TILE0_FLAT '+' '.join(ports)]
expected=[]
for r in range(64):
    for c in range(320):
        for b in range(4):
            d=f'IDX{c}_{b}' if (int(indices[r,c])>>b)&1 else f'OPEN_R{r}_C{c}_B{b}'
            lines.append(f'Xr{r}c{c}b{b} {d} WL{r} VSS VSS nfet_03v3 w=0.36u l=0.28u')
            expected.append((d,f'WL{r}','VSS','VSS','nfet_03v3'))
lines.append('.ends W5_TILE0_FLAT');(O/'tile0-reference.spice').write_text('\n'.join(lines)+'\n')
observed=[]
for line in (O/'tile0-extracted.spice').read_text().splitlines():
    if line.startswith('X'):
        f=line.split();observed.append(tuple(f[1:6]));assert 'w=0.36u' in f and 'l=0.28u' in f
report['tile0']['exact_device_tuples']={'expected':len(expected),'extracted':len(observed),'match':sorted(expected)==sorted(observed)}
(O/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
run([netgen,'-batch','lvs','tile0-extracted.spice W5_TILE0_FLAT','tile0-reference.spice W5_TILE0_FLAT',str(PDK/'libs.tech/netgen/gf180mcuD_setup.tcl'),'tile0-netgen.log'],'tile0-netgen-console.log')
txt=(O/'tile0-netgen.log').read_text()
report['tile0']['netgen_lvs']={'unique_match':'Circuits match uniquely.' in txt,'property_errors': 'Property errors' in txt,'log':'tile0-netgen.log'}
(O/'verification.json').write_text(json.dumps(report,indent=2)+'\n')
print('W5-STATUS: tile0 extracted topology/LVS',json.dumps(report['tile0']),flush=True)
