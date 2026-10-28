"""Independent full extraction, source-derived schematic, and disjoint LVS.

Run one stage at a time; preserve each run directory. All outputs local here.
"""
from pathlib import Path
from collections import Counter,defaultdict
import argparse,hashlib,json,os,re,shutil,subprocess,time
import numpy as np
P=Path(__file__).resolve().parent;W=P.parents[1];R=W.parents[1]
PDK=R/'pdks/gf180mcuD'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def image():
 candidate=R/'models/candidates/codebook-4bit-optimal-rectangular-k64'
 manifest=json.loads((candidate/'candidate.json').read_text())
 rec=next(x for x in manifest['changed_tensor_records'] if x['file']=='encoder.ort' and x['tensor']=='val_89_quantized')
 packed=(candidate/'packed'/rec['packed_file']).read_bytes();assert hashlib.sha256(packed).hexdigest()==rec['packed_sha256']
 idx=np.full((1280,320),255,np.uint8);used=set()
 for b in rec['blocks']:
  r0,r1=b['rows'];c0,c1=b['columns'];offset=b['index_offset'];size=b['index_bytes']
  assert (r1-r0,c1-c0,size,b['value_count'])==(64,1,32,64)
  assert not used.intersection(range(offset,offset+size));used.update(range(offset,offset+size))
  assert (idx[r0:r1,c0]==255).all()
  for i in range(64):idx[r0+i,c0]=(packed[offset+i//2]>>(4*(i%2)))&15
 assert len(used)==len(packed) and (idx<16).all()
 rtl=R/'overnight-20261014/fabric-k64/rtl/index_fabric.sv'
 rows=re.findall(r"frozen_rows\[(\d+)\]=1280'h([0-9a-f]+);",rtl.read_text());assert len(rows)==1280
 for r,h in rows:
  word=int(h,16);assert all(int(idx[int(r),c])==((word>>(4*c))&15) for c in range(320))
 assert np.array_equal(idx,np.load(W/'indices.npy'))
 return idx,dict(packed_sha256=hashlib.sha256(packed).hexdigest(),unpacked_sha256=hashlib.sha256(idx.tobytes()).hexdigest(),w2b_rtl_sha256=sha(rtl),all409600_indices_match=True)
def tool(name):
 q=shutil.which(name)
 if q:return q
 choices=list(Path('/nix/store').glob(f'*{name}*/bin/{name}'));assert choices,name
 return str(choices[0])
def run(cmd,o,stem,timeout):
 assert shutil.disk_usage(P).free>=22*2**30
 cmd=['nice','-n','10']+cmd
 (o/(stem+'-command.json')).write_text(json.dumps(cmd,indent=2)+'\n')
 start=time.monotonic();rc=None;status='finished'
 with (o/(stem+'-console.log')).open('w') as f:
  try:rc=subprocess.run(cmd,cwd=o,stdout=f,stderr=subprocess.STDOUT,timeout=timeout,env=dict(os.environ,TMPDIR=str(o),PDK_ROOT=str(PDK.parent),OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1')).returncode
  except subprocess.TimeoutExpired:status='timeout'
 report=dict(returncode=rc,status=status,elapsed_seconds=time.monotonic()-start)
 (o/(stem+'-process.json')).write_text(json.dumps(report,indent=2)+'\n');return report

def main():
 a=argparse.ArgumentParser();a.add_argument('stage',choices=['extract','compare','partitions']);a.add_argument('--gds',required=True);a.add_argument('--top',required=True);a.add_argument('--bank',type=int,required=True);a.add_argument('--run',required=True);args=a.parse_args()
 assert 0<=args.bank<4 and re.fullmatch('[A-Za-z0-9_-]+',args.run)
 o=P/args.run;o.mkdir(exist_ok=True);gds=Path(args.gds).resolve();assert gds.exists()
 meta=dict(gds=str(gds.relative_to(R)),gds_sha256=sha(gds),top=args.top,bank=args.bank,row_mapping='logical_row=bank+4*local_row')
 if (o/'input.json').exists():assert json.loads((o/'input.json').read_text())==meta,'Input changed; use a new run name'
 else:(o/'input.json').write_text(json.dumps(meta,indent=2)+'\n')
 ports=['VDD','VSS','PC']+[f'WL{r}' for r in range(320)]+[f'OUT{i}' for i in range(1280)]
 top='W5_TALL_BANK_FLAT'
 if args.stage=='extract':
  assert not (o/'extracted.spice').exists(),'Preserve existing extraction; use fresh run'
  (o/'extract.tcl').write_text(f'gds readonly true\ngds read {{{gds}}}\nload {args.top}\nflatten {top}\nload {top}\nextract all\next2spice lvs\next2spice -o extracted.spice\next2spice cthresh 0\next2spice -o extracted-cap.spice\nquit -noprompt\n')
  result=run([tool('magic'),'-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'],o,'extract',1800);print(result,flush=True);return
 if args.stage=='compare':
  idx,identity=image();(o/'identity.json').write_text(json.dumps(identity,indent=2)+'\n')
  lines=['* Independently decoded packed tensor; strengthened receiver circuit',f'.subckt {top} '+' '.join(ports)]
  for row in range(320):
   for col in range(320):
    for bit in range(4):
     drain=f'IDX{col}_{bit}' if (int(idx[args.bank+4*row,col])>>bit)&1 else f'OPEN_R{row}_C{col}_B{bit}'
     lines.append(f'Xa{row}_{col}_{bit} {drain} WL{row} VSS VSS nfet_03v3 w=0.36u l=0.28u')
  for i in range(1280):
   col,bit=divmod(i,4);bl=f'IDX{col}_{bit}';out=f'OUT{i}'
   for name,d,g,s,b,model,width in [('n',out,bl,'VSS','VSS','nfet_03v3',.36),('p',out,bl,'VDD','VDD','pfet_03v3',.72),('k',bl,out,'VDD','VDD','pfet_03v3',.36),('pc',bl,'PC','VDD','VDD','pfet_03v3',2.88)]:lines.append(f'X{name}{i} {d} {g} {s} {b} {model} w={width}u l=0.28u')
  lines.append(f'.ends {top}');(o/'reference.spice').write_text('\n'.join(lines)+'\n')
  raw=(o/'extracted.spice').read_text();forward={};back={};can=[]
  for line in raw.splitlines():
   f=line.split()
   if line.startswith('X'):
    assert len(f)>=8 and f[5] in ('nfet_03v3','pfet_03v3'),line
    nodes=[]
    for n in f[1:5]:
     short=n.rsplit('.',1)[-1]
     assert short not in back or back[short]==n,('non-bijective name normalization',short,n,back.get(short))
     forward[n]=short;back[short]=n;nodes.append(short)
    line=' '.join([f[0]]+nodes+f[5:])
   elif line.startswith('.subckt'):line=f'.subckt {top} '+' '.join(ports)
   can.append(line)
  assert all(x in back for x in ports),('Missing actual physical port nets',[x for x in ports if x not in back])
  def tup(line):
   f=line.split();v={k.lower():v for k,v in (t.split('=',1) for t in f[6:])};return tuple(sorted((f[1],f[3]))),f[2],f[4],f[5],float(v['w'].removesuffix('u')),float(v['l'].removesuffix('u'))
  x=Counter(tup(l) for l in can if l.startswith('X'));y=Counter(tup(l) for l in lines if l.startswith('X'))
  report=dict(extracted_devices=sum(x.values()),reference_devices=sum(y.values()),exact_device_tuples_and_dimensions_match=x==y,bijection_nodes=len(back),extra_device_examples=[str(k) for k in list((x-y))[:5]],missing_device_examples=[str(k) for k in list((y-x))[:5]],qualification='Bijective hierarchical prefix removal only; no device/net merges. All320 physical WL,PC,VDD,VSS and1280 outputs required present.')
  (o/'connectivity.json').write_text(json.dumps(report,indent=2)+'\n');assert x==y and sum(x.values())==414720,report
  (o/'canonical.spice').write_text('\n'.join(can)+'\n');print('W5-STATUS: full tall bank exact graph/W/L PASS',report,flush=True);return
 # Partition the ACTUAL full-bank extraction, without altering any node.
 shared=set(['VDD','VSS','PC']+[f'WL{r}' for r in range(320)]);seen=defaultdict(set);parts={s:[[] for _ in range(10)] for s in ['canonical','reference']}
 for source in parts:
  for line in (o/(source+'.spice')).read_text().splitlines():
   if not line.startswith('X'):continue
   f=line.split();gs=set()
   for n in f[1:5]:
    if n in shared:continue
    if m:=re.fullmatch(r'IDX(\d+)_\d',n):group=int(m[1])//32
    elif m:=re.fullmatch(r'OPEN_R\d+_C(\d+)_B\d',n):group=int(m[1])//32
    elif m:=re.fullmatch(r'OUT(\d+)',n):group=int(m[1])//128
    else:raise AssertionError(('unexpected local node',n))
    gs.add(group)
   assert len(gs)==1,line
   g=gs.pop();assert 0<=g<10;parts[source][g].append(line)
   if source=='canonical':
    for n in f[1:5]:seen[n].add(g)
 audit=dict(devices_per_partition=[len(v) for v in parts['canonical']],shared_nets_actual={n:sorted(v) for n,v in seen.items() if len(v)>1},unexpected_shared_nets=sorted(n for n,v in seen.items() if len(v)>1 and n not in shared),global_nets_not_seen_in_all10=sorted(n for n in shared if seen[n]!=set(range(10))))
 (o/'partition-audit.json').write_text(json.dumps(audit,indent=2)+'\n');assert audit['devices_per_partition']==[41472]*10 and not audit['unexpected_shared_nets'] and not audit['global_nets_not_seen_in_all10']
 results=[]
 for g in range(10):
  gp=['VDD','VSS','PC']+[f'WL{r}' for r in range(320)]+[f'OUT{i}' for i in range(g*128,(g+1)*128)]
  for s in parts:(o/f'g{g}-{s}.spice').write_text('.subckt W5_TALL_PART '+' '.join(gp)+'\n'+'\n'.join(parts[s][g])+'\n.ends W5_TALL_PART\n')
  proc=run([tool('netgen'),'-batch','lvs',f'g{g}-canonical.spice W5_TALL_PART',f'g{g}-reference.spice W5_TALL_PART',str(PDK/'libs.tech/netgen/gf180mcuD_setup.tcl'),f'g{g}-netgen.log'],o,f'g{g}-netgen',600)
  t=(o/f'g{g}-netgen.log').read_text() if (o/f'g{g}-netgen.log').exists() else ''
  res=dict(group=g,**proc,unique_match='Circuits match uniquely.' in t,property_errors='Property errors' in t);results.append(res)
  (o/'partition-results.json').write_text(json.dumps(results,indent=2)+'\n');print('W5-STATUS: tall bank partition LVS',res,flush=True)
  assert res['returncode']==0 and res['unique_match'] and not res['property_errors'],res
 (o/'lvs-result.json').write_text(json.dumps(dict(pass_all10=True,full_extraction_devices=414720,scope='Ten disjoint Netgen comparisons of actual full-bank extraction plus exact full graph/W/L equality and shared-net audit. Not a monolithic Netgen comparison.',partitions=results,input=meta),indent=2)+'\n')
if __name__=='__main__':main()
