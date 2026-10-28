from pathlib import Path
import json,subprocess,sys
W=Path(__file__).resolve().parent
R=W.parents[1]
RUN=Path.home()/'.local/state/routevoice-internal-runs/20261014/onchip-enc'
c=json.loads((W/'commands.json').read_text())
verilator=c['generate-full'][0]
for kind,name in enumerate(['head','O','memory']):
 top='rv_onchip_encoder_'+name+'_v1';obj=RUN/('test-'+name)
 c['test-'+name+'-build']=[verilator,'--cc','--exe','--build','-j','6','-Wno-fatal','--top-module',top,'--Mdir',str(obj),'-CFLAGS',f'-DKIND={kind} -O2',str(W/(top+'.sv')),str(W/'responder_test.cpp')]
 c['test-'+name]=[str(obj/('V'+top)),str(Path.home()/'.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3/encoder/inputs.txt')]
(W/'commands.json').write_text(json.dumps(c,indent=2)+'\n')
for name in ['head','O','memory']:
 for stage in ['test-'+name+'-build','test-'+name]:subprocess.run([sys.executable,str(W/'run_stage.py'),stage],check=True)
