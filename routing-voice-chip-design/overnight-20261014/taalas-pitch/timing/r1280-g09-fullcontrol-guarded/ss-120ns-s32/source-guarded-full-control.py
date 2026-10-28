"""Measured-control-delay guarded protocol; physical circuit unchanged."""
from pathlib import Path
import argparse,json,hashlib,shutil
import global_control_sensitivity as g
s=g.s;W=Path(__file__).resolve().parent;BASE=s.build
FAILED=W/'r1280-g09-fullcontrol/ss-60ns-s32'
def protocol(period):
 assert period==120
 return {'period_ns':period,'pc_off_ns':30.,'wl_start_ns':55.,'wl_fall_start_ns':105.8,'wl_fall_end_ns':106.,'pc_on_start_ns':119.8,'sample_ns':[102.,119.5],'edge_ns':.2,'phase_family':'Conservative120ns full-control sensitivity:30ns precharge,25ns PC-off guard,13.8ns WL-release guard; selected after preserved60ns failure, not minimum-period search.'}
def physical(lines):
 return '\n'.join(l for l in lines if l.startswith(('X','R','C','.include ','.lib ','.temp ','.param ','.options ','Vrdd ','Vwdd ','Vpdd ','Vcolumn')))+'\n'
def build(*args):
 lines,names,meta,image=BASE(*args);old=physical((FAILED/'test.cir').read_text().splitlines());new=physical(lines);assert old==new,'Physical circuit changed'
 meta['transient_timeout_seconds']=1200
 meta['guarded_protocol_followup']={'failed_case':str(FAILED/'result.json'),'failed_case_sha256':hashlib.sha256((FAILED/'result.json').read_bytes()).hexdigest(),'control_diagnostic':str(FAILED/'control-delay-diagnostic.json'),'control_diagnostic_sha256':hashlib.sha256((FAILED/'control-delay-diagnostic.json').read_bytes()).hexdigest(),'physical_circuit_lines_byte_identical':True,'physical_circuit_sha256':hashlib.sha256(new.encode()).hexdigest(),'definition':'Every MOS/R/C, supply value, model inclusion, PVT and solver option unchanged byte-for-byte; only commanded phase/read/sample times and transient duration differ. Not a minimum timing search or placed-control implementation.'}
 return lines,names,meta,image
s.protocol=protocol;s.build=build
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',required=True);a=p.parse_args();D=W/a.directory/'ss-120ns-s32'
 try:s.run(W/a.directory,'ss',120,32)
 finally:
  if D.exists():
   shutil.copyfile(Path(__file__),D/'source-guarded-full-control.py');shutil.copyfile(W/'global_control_sensitivity.py',D/'source-global-control-sensitivity.py')
