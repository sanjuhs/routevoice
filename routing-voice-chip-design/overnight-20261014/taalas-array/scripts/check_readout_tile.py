from pathlib import Path
import os,json,subprocess,shutil,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parents[1];R=W.parents[1];O=W/'integrated';PDK=R/'pdks/gf180mcuD'
assert shutil.disk_usage(W).free>=22*2**30
kl=str(next(Path('/nix/store').glob('*klayout*/bin/klayout')))
opts={'input':O/'readout-tile0.gds','report':O/'readout-tile0.lyrdb','topcell':'RV_K64_READOUT_TILE_00','feol':'true','beol':'true','conn_drc':'true','offgrid':'true','metal_top':'11K','metal_level':'5LM','mim_option':'B','run_mode':'deep','thr':'2'}
cmd=[kl,'-b','-r',str(R/'experiments/taalas-access/main.drc')]
for k,v in opts.items():cmd+=['-rd',f'{k}={v}']
(O/'drc-command.json').write_text(json.dumps(cmd,indent=2)+'\n')
with (O/'drc.log').open('w') as f:subprocess.run(['nice','-n','10']+cmd,cwd=O,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=1800)
n=len(ET.parse(O/'readout-tile0.lyrdb').getroot().findall('./items/item'))
(O/'drc-result.json').write_text(json.dumps({'drc_markers':n,'scope':'GF180 FEOL BEOL connectivity offgrid; antenna and density excluded','top':'RV_K64_READOUT_TILE_00'},indent=2)+'\n')
print('W5-STATUS: actual joined readout tile DRC markers',n)
