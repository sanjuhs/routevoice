from pathlib import Path
import sys,json
sys.dont_write_bytecode=True
from verify import P,PDK,tool,run
O=P/'bank3-v1'
for stem,left,right,top,timeout in [('full-bank-netgen','canonical.spice','reference.spice','W5_TALL_BANK_FLAT',120),('negative-width-netgen','g0-canonical.spice','g0-reference-wrong-width.spice','W5_TALL_PART',30)]:
 if stem=='negative-width-netgen':
  ref=(O/'g0-reference.spice').read_text();assert ref.count('Xpc0 ')==1
  old=next(l for l in ref.splitlines() if l.startswith('Xpc0 '));new=old.replace('w=2.88u','w=5.76u');assert old!=new
  (O/right).write_text(ref.replace(old,new))
 result=run([tool('netgen'),'-batch','lvs',f'{left} {top}',f'{right} {top}',str(PDK/'libs.tech/netgen/gf180mcuD_setup.tcl'),stem+'.log'],O,stem,timeout)
 text=(O/(stem+'.log')).read_text() if (O/(stem+'.log')).exists() else ''
 result.update(unique_match='Circuits match uniquely.' in text,property_errors='Property errors' in text)
 result['pass']=result['returncode']==0 and result['unique_match'] and not result['property_errors']
 (O/(stem+'-result.json')).write_text(json.dumps(result,indent=2)+'\n');print('W5-STATUS:',stem,result,flush=True)
 if stem=='negative-width-netgen':assert result['property_errors'] and not result['pass'],result
