"""Flatten DUT declaration names to Yosys dot-separated net names.
Only hierarchy declarations change; timestamped value-change bytes are preserved.
"""
from pathlib import Path
import hashlib,json,sys
W=Path(__file__).resolve().parent;v=sys.argv[1] if len(sys.argv)>1 else 'array_port'
src=W/'evidence'/f'{v}-speech.vcd';dst=W/'evidence'/f'{v}-speech-flat.vcd'
stack=[];renamed=0;tail_hash=hashlib.sha256()
with src.open('rb') as f,dst.open('wb') as g:
 for line in f:
  tokens=line.split();emit=line
  if tokens and tokens[0]==b'$scope':
   stack.append(tokens[2].decode())
   if stack[:2]==['tb','dut'] and len(stack)>2:continue
  elif tokens and tokens[0]==b'$upscope':
   skip=stack[:2]==['tb','dut'] and len(stack)>2
   stack.pop()
   if skip:continue
  elif tokens and tokens[0]==b'$var' and stack[:2]==['tb','dut'] and len(stack)>2:
   tokens[4]=('.'.join(stack[2:])+'.').encode()+tokens[4]
   emit=b' '.join(tokens)+b'\n';renamed+=1
  g.write(emit)
  if tokens and tokens[0]==b'$enddefinitions':break
 for block in iter(lambda:f.read(1024*1024),b''):
  tail_hash.update(block);g.write(block)
check=hashlib.sha256()
with dst.open('rb') as f:
 for line in f:
  if line.strip().startswith(b'$enddefinitions'):break
 for block in iter(lambda:f.read(1024*1024),b''):check.update(block)
assert check.digest()==tail_hash.digest()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r={'source':str(src.relative_to(W)),'source_sha256':sha(src),'output':str(dst.relative_to(W)),'output_sha256':sha(dst),'renamed_declarations':renamed,'value_change_tail_sha256':tail_hash.hexdigest(),'value_changes_verified_identical':True,'scope':'tb/dut','reason':'Map RTL child hierarchy to Yosys flattened dot-separated net names; retain actual activity, not synthetic transitions.'}
(W/'evidence'/f'{v}-flat-vcd-provenance.json').write_text(json.dumps(r,indent=2)+'\n');print(r)
