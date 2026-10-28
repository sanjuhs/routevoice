from pathlib import Path
import os,json,subprocess,hashlib,xml.etree.ElementTree as ET
W=Path(__file__).resolve().parent;R=W.parents[2]
PDK=R/'pdks/gf180mcuD'
os.environ['PDK_ROOT']=str(R/'pdks')
def run(args,log):
 assert __import__('shutil').disk_usage('/').free>=22*1024**3
 with (W/log).open('w') as f:subprocess.run(['nice','-n','10',*args],cwd=W,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=300)
cmd=['klayout','-b','-r',str(R/'experiments/taalas-access/main.drc')]
for k,v in dict(input=W/'index-array.gds',report=W/'index-array.lyrdb',topcell='TAALAS_MASK_INDEX_R64_C32',feol='true',beol='true',conn_drc='true',offgrid='true',metal_top='11K',metal_level='5LM',mim_option='B',run_mode='flat',thr=1).items():cmd+=['-rd',f'{k}={v}']
(W/'drc-command.json').write_text(json.dumps(cmd,indent=2));run(cmd,'drc.log')
markers=len(ET.parse(W/'index-array.lyrdb').getroot().findall('./items/item'))
(W/'extract.tcl').write_text('gds readonly true\ngds read index-array.gds\nload TAALAS_MASK_INDEX_R64_C32\nextract all\next2spice lvs\next2spice -o index-array.spice\next2spice cthresh 0\next2spice -o index-array-cap.spice\nquit -noprompt\n')
run(['magic','-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'],'extract.log')
image=json.loads((W/'indices.json').read_text());expected=[]
for row in range(64):
 for col in range(32):
  for bit in range(4):
   drain=f'IDX{col}_{bit}' if image[row][col]>>bit&1 else f'OPEN_R{row}_C{col}_B{bit}'
   expected.append((drain,f'WL{row}','VSS','VSS','nfet_03v3'))
actual=[]
for line in (W/'index-array.spice').read_text().splitlines():
 if line.startswith('X'):
  f=line.split();actual.append(tuple(f[1:6]));assert 'w=0.36u' in f and 'l=0.28u' in f
assert sorted(actual)==sorted(expected)
result={'drc_markers':markers,'drc_scope':'FEOL BEOL connectivity offgrid; excludes antenna/density','extracted_bit_tuples_matched':8192,'physical_lvs':'Exact extracted device and frozen-bit connectivity graph comparison, not independent LVS'}
(W/'checks.json').write_text(json.dumps(result,indent=2));print(result)
