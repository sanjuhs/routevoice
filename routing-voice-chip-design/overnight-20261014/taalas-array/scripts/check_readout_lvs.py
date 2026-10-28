from pathlib import Path
import os,sys,json,subprocess,shutil,re
from collections import Counter
sys.dont_write_bytecode=True
import numpy as np
W=Path(__file__).resolve().parents[1];R=W.parents[1];O=W/'integrated';PDK=R/'pdks/gf180mcuD'
assert shutil.disk_usage(W).free>=22*2**30
magic=str(next(Path('/nix/store').glob('*magic*/bin/magic')));netgen=str(next(Path('/nix/store').glob('*netgen*/bin/netgen')))
def run(cmd,log):
    with (O/'lvs-commands.jsonl').open('a') as f:f.write(json.dumps(cmd)+'\n')
    with (O/log).open('w') as f:subprocess.run(['nice','-n','10']+cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,PDK_ROOT=str(PDK.resolve().parent),TMPDIR=str(W/'tmp')),check=True,timeout=1800)
(O/'extract.tcl').write_text('''gds readonly true
gds read readout-tile0.gds
load RV_K64_READOUT_TILE_00
flatten W5_READOUT_TILE_FLAT
load W5_READOUT_TILE_FLAT
extract all
ext2spice lvs
ext2spice -o readout-tile0-extracted.spice
quit -noprompt
''')
run([magic,'-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'],'extract.log')
idx=np.load(W/'indices.npy');ports=['VDD','VSS','PC']+[f'WL{r}' for r in range(64)]+[f'OUT{i}' for i in range(1280)]
lines=['* Independent schematic admitted real image plus receiver design','.subckt W5_READOUT_TILE_FLAT '+' '.join(ports)]
for r in range(64):
 for c in range(320):
  for b in range(4):
   drain=f'IDX{c}_{b}' if (int(idx[r,c])>>b)&1 else f'OPEN_R{r}_C{c}_B{b}'
   lines.append(f'Xa{r}_{c}_{b} {drain} WL{r} VSS VSS nfet_03v3 w=0.36u l=0.28u')
for i in range(1280):
 c,b=divmod(i,4);bl=f'IDX{c}_{b}';out=f'OUT{i}'
 for name,d,g,s,body,kind,w in [('n',out,bl,'VSS','VSS','nfet_03v3',.36),('p',out,bl,'VDD','VDD','pfet_03v3',.72),('k',bl,out,'VDD','VDD','pfet_03v3',.36),('pc',bl,'PC','VDD','VDD','pfet_03v3',1.44)]:
  lines.append(f'X{name}{i} {d} {g} {s} {body} {kind} w={w}u l=0.28u')
lines.append('.ends W5_READOUT_TILE_FLAT');ref='\n'.join(lines)+'\n';(O/'readout-tile0-reference.spice').write_text(ref)
raw=(O/'readout-tile0-extracted.spice').read_text();rows=[x.split() for x in raw.splitlines() if x.startswith('X')];mapping={}
for f in rows:
 for n in f[1:5]:
  short=n.rsplit('.',1)[-1]
  assert short not in mapping or mapping[short]==n,('not one-to-one',short)
  mapping[short]=n
for p in ports:assert p in mapping,p
canonical=[]
for line in raw.splitlines():
 f=line.split()
 if line.startswith('X'):line=' '.join([f[0]]+[n.rsplit('.',1)[-1] for n in f[1:5]]+f[5:])
 elif line.startswith('.subckt'):line='.subckt W5_READOUT_TILE_FLAT '+' '.join(ports)
 canonical.append(line)
def tup(line):
 f=line.split();v=dict(t.split('=') for t in f[6:]);return (tuple(sorted([f[1],f[3]])),f[2],f[4],f[5],float(v['w'].removesuffix('u')),float(v['l'].removesuffix('u')))
a=Counter(tup(x) for x in canonical if x.startswith('X'));b=Counter(tup(x) for x in lines if x.startswith('X'));match=a==b
report={'expected_devices':87040,'extracted_devices':sum(a.values()),'exact_device_tuples_and_dimensions_match':match,'bijection_nodes':len(mapping),'scope':'full64x320 array plus1280 physical readouts and actual join/common rail metal; excludes decoder/phase control/bank mux','independent_netgen_lvs':None}
(O/'lvs-result.json').write_text(json.dumps(report,indent=2)+'\n');assert match,(list((a-b).items())[:2],list((b-a).items())[:2])
(O/'readout-tile0-canonical.spice').write_text('\n'.join(canonical)+'\n')
run([netgen,'-batch','lvs','readout-tile0-canonical.spice W5_READOUT_TILE_FLAT','readout-tile0-reference.spice W5_READOUT_TILE_FLAT',str(PDK/'libs.tech/netgen/gf180mcuD_setup.tcl'),'readout-tile0-netgen.log'],'netgen-console.log')
txt=(O/'readout-tile0-netgen.log').read_text();report['independent_netgen_lvs']={'unique_match':'Circuits match uniquely.' in txt,'property_errors':'Property errors' in txt,'qualification':'bijective hierarchical label prefix normalization plus existing-node port declarations; no node merging or device changes'}
(O/'lvs-result.json').write_text(json.dumps(report,indent=2)+'\n');print('W5-STATUS: readout tile LVS',json.dumps(report),flush=True)
