from pathlib import Path
import re,json,subprocess,time,os
from collections import Counter
W=Path(__file__).resolve().parent;R=W.parents[3];O=W/'v1';raw=(O/'decoded-tile-extracted.spice').read_text();ref=(O/'reference.spice').read_text();ports=next(l.split()[2:] for l in ref.splitlines() if l.startswith('.subckt'))
back={};forward={}
def norm(n):
 if n in forward:return forward[n]
 short=n.rsplit('.',1)[-1]
 if re.fullmatch(r'(?:IDX\d+_\d|OPEN_R\d+_C\d+_B\d|OUT\d+|PC)',short):new=short
 elif (m:=re.search(r'RV_DECODED_BANK_00_(\d+)_0/w5_row_decoder_0.wordline\[(\d+)\]$',n)):new=f'WL_G{m[1]}_R{m[2]}'
 else:new=n
 assert new not in back or back[new]==n,('nonbijective',new,n,back.get(new))
 back[new]=n;forward[n]=new;return new
can=[]
for l in raw.splitlines():
 f=l.split()
 if l.startswith('X'):l=' '.join([f[0]]+[norm(n) for n in f[1:5]]+f[5:])
 elif l.startswith('.subckt'):l='.subckt W5_DECODED_TILE_FLAT '+' '.join(ports)
 can.append(l)
assert all(p in back for p in ports),[p for p in ports if p not in back]
def tup(l):
 f=l.split();d={x.lower().split('=')[0]:x.split('=')[1] for x in f[6:]};return (tuple(sorted([f[1],f[3]])),f[2],f[4],f[5],float(d['w'].removesuffix('u')),float(d['l'].removesuffix('u')))
a=Counter(tup(l) for l in can if l.startswith('X') and 'fet_03v3 ' in l);b=Counter(tup(l) for l in ref.splitlines() if l.startswith('X') and 'fet_03v3 ' in l)
report={'extracted_total_devices':sum(l.startswith('X') for l in can),'reference_total_devices':sum(l.startswith('X') for l in ref.splitlines()),'analog_exact_device_graph_and_dimensions_match':a==b,'analog_devices':sum(a.values()),'bijection_nodes':len(back),'independent_wordline_nets':len([n for n in back if n.startswith('WL_G')]),'qualification':'Bijective normalization of unique external/analog nodes and bank-specific WL nodes; remaining decoder internal node names untouched. No net merging or circuit changes.'}
(O/'connectivity.json').write_text(json.dumps(report,indent=2));assert a==b,(list((a-b).items())[:2],list((b-a).items())[:2]);assert report['independent_wordline_nets']==640
(O/'canonical.spice').write_text('\n'.join(can)+'\n')
cmd=['nice','-n','10','netgen','-batch','lvs','canonical.spice W5_DECODED_TILE_FLAT','reference.spice W5_DECODED_TILE_FLAT',str(R/'pdks/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl'),'netgen.log'];(O/'lvs-command.json').write_text(json.dumps(cmd,indent=2));t=time.monotonic()
with (O/'netgen-console.log').open('w') as f:p=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,env=dict(os.environ,TMPDIR=str(O)))
txt=(O/'netgen.log').read_text();report.update({'netgen_returncode':p.returncode,'netgen_seconds':time.monotonic()-t,'unique_match':'Circuits match uniquely.' in txt,'property_errors':'Property errors' in txt});(O/'lvs-result.json').write_text(json.dumps(report,indent=2));print(report,flush=True)
