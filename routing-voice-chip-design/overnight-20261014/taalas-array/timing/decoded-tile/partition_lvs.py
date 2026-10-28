from pathlib import Path
import re,json,subprocess,time,sys
W=Path(__file__).resolve().parent;O=W/'v1';R=W.parents[3]
G=int(sys.argv[1]) if len(sys.argv)>1 else 0
ports=['VDD','VSS','PC','EVAL']+[f'ROW{i}' for i in range(6)]+[f'OUT{i}' for i in range(G*128,(G+1)*128)]
can=['.subckt W5_DECODED_BANK '+' '.join(ports)];ref=can.copy();counts=[0]*10
# Each decoder device has one or more local terminals. Identify the bank from
# preserved hierarchical label, renamed WL, or Magic generated coordinate.
# Magic extracted coordinate scale is 0.005um, verified against WL labels.
def group(n):
 if (m:=re.match(r'RV_DECODED_BANK_00_(\d+)_0/',n)):return int(m[1])
 if (m:=re.match(r'WL_G(\d+)_',n)):return int(m[1])
 if (m:=re.match(r'a_(-?\d+)_',n)):return int(m[1])//93600
 return None
for l in (O/'canonical.spice').read_text().splitlines():
 if not l.startswith('X'):continue
 f=l.split()
 if '05v0' in f[5]:
  gs={group(n) for n in f[1:5]}-{None};assert len(gs)==1,(l,gs)
  g=gs.pop();assert 0<=g<10;counts[g]+=1
 else:
  gs={int(m[1]) for n in f[1:5] if (m:=re.match(r'WL_G(\d+)_',n))}
  if not gs:gs={int(m[1])//128 for n in f[1:5] if (m:=re.match(r'OUT(\d+)$',n))}
  if not gs:gs={int(m[1])//32 for n in f[1:5] if (m:=re.match(r'IDX(\d+)_',n))}
  assert len(gs)==1,l;g=gs.pop()
 if g==G:can.append(l)
for l in (O/'reference.spice').read_text().splitlines():
 if not l.startswith('X'):continue
 f=l.split();name=f[0]
 if name.startswith('XD'):keep=name.startswith(f'XD{G}_')
 elif name.startswith('Xa'):keep=int(name.split('_')[1])//32==G
 else:keep=int(re.search(r'(\d+)$',name)[1])//128==G
 if keep:ref.append(l)
assert counts==[2442]*10,counts
for name,lines in [(f'bank{G}-canonical.spice',can),(f'bank{G}-reference.spice',ref)]:
 assert len(lines)==11147,len(lines);lines.append('.ends W5_DECODED_BANK');(O/name).write_text('\n'.join(lines)+'\n')
cmd=['nice','-n','10','netgen','-batch','lvs',f'bank{G}-canonical.spice W5_DECODED_BANK',f'bank{G}-reference.spice W5_DECODED_BANK',str(R/'pdks/gf180mcuD/libs.tech/netgen/gf180mcuD_setup.tcl'),f'bank{G}-netgen.log'];(O/f'bank{G}-lvs-command.json').write_text(json.dumps(cmd,indent=2));start=time.monotonic()
with (O/f'bank{G}-netgen-console.log').open('w') as f:p=subprocess.run(cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,timeout=200)
t=(O/f'bank{G}-netgen.log').read_text();res={'bank':G,'returncode':p.returncode,'seconds':time.monotonic()-start,'devices':11146,'decoder_devices_per_bank':counts,'unique_match':'Circuits match uniquely.' in t,'property_errors':'Property errors' in t,'scope':'Single bank component selected from fulltile actual flat extraction by physical local node labels/coordinates; global VDD/VSS/ROW/EVAL/PC already unified by actual top wires. No new GDS, no circuit changes.'};(O/f'bank{G}-lvs-result.json').write_text(json.dumps(res,indent=2));print(res,flush=True)
