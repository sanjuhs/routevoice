#!/usr/bin/env python3
"""Record one corner's original and explicit macro-only multicycle STA reports."""
import hashlib,json,os,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent

def digest(path):
 h=hashlib.sha256()
 with open(path,'rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
 return h.hexdigest()

def main():
 required=['W8_LIB_LIST','W8_MACRO_LIB','W8_NETLIST','W8_TOP','W8_SDC','W8_SPEF','W8_OUT_DIR','W8_CORNER']
 missing=[k for k in required if not os.environ.get(k)]
 if missing:raise ValueError('Missing '+', '.join(missing))
 env=dict(os.environ);out=Path(env['W8_OUT_DIR']).resolve();out.mkdir(parents=True,exist_ok=False);env['W8_OUT_DIR']=str(out)
 files=[Path(p.strip()).resolve() for p in env['W8_LIB_LIST'].splitlines() if p.strip()]
 files += [Path(env[k]).resolve() for k in ['W8_MACRO_LIB','W8_NETLIST','W8_SDC','W8_SPEF']]
 provenance={'inputs_sha256':{str(p):digest(p) for p in files},'script_sha256':digest(HERE/'postroute_timing.tcl'),'corner':env['W8_CORNER'],'macro_output_pattern':env.get('W8_MACRO_OUTPUT_PATTERN','bank/OUT*')}
 (out/'provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
 with (out/'sta.log').open('w') as log:
  cp=subprocess.run([env.get('W8_STA','sta'),'-no_splash','-exit',str(HERE/'postroute_timing.tcl')],env=env,stdout=log,stderr=subprocess.STDOUT,check=False)
 log=(out/'sta.log').read_text()
 if cp.returncode or re.search(r'^Error:',log,re.M):
  (out/'failure.json').write_text(json.dumps({'exit_code':cp.returncode,'log':'sta.log'},indent=2)+'\n');raise RuntimeError('Timing analysis failed; raw reports preserved')
 result={'corner':env['W8_CORNER'],'provenance':provenance,'scenarios':{},'full_bank_timing_qualified':False,'limitations':['PC-to-output44ns engineering proxy, not full-bank corner characterization.','Independent WL-to-output timing arcs absent.','3setup/2hold scenario relies on actual protocol timing; does not prove it.','Original scenario preserves input SDC; a single-cycle label requires verifying that SDC.'],'multicycle_scope':(out/'multicycle-scope.txt').read_text(),'parasitic_annotation':(out/'parasitic-annotation.rpt').read_text()}
 for name in ['original','macro-multicycle-3-2']:
  text=(out/(name+'-summary.rpt')).read_text()
  slack=re.findall(r'worst slack(?:\s+(?:min|max))?\s+([-+\d.eE]+)',text)
  result['scenarios'][name]={'raw_summary':text,'setup_worst_slack_report_units':float(slack[0]) if len(slack)>0 else None,'hold_worst_slack_report_units':float(slack[1]) if len(slack)>1 else None,'units_report':'units.rpt','setup_report':name+'-setup.rpt','hold_report':name+'-hold.rpt'}
 (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print('W8-TIMING: both bounded scenarios reported; complete-bank timing remains unqualified')
if __name__=='__main__':main()
