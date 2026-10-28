from pathlib import Path
import os,json,shutil,subprocess,hashlib,sys,xml.etree.ElementTree as ET
BASE=Path(__file__).resolve().parent;R=BASE.parents[2];W=BASE/sys.argv[1];W.mkdir(exist_ok=True)
PDK=R/'pdks/gf180mcuD';os.environ['PDK_ROOT']=str(R/'pdks')
source=BASE.parent/'integrated/joined-bank0.gds';shutil.copyfile(source,W/'input.gds')
def run(args,log):
 assert shutil.disk_usage('/').free>=22*1024**3
 with (W/log).open('w') as f:subprocess.run(['nice','-n','10',*args],cwd=W,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=300)
cmd=['klayout','-b','-r',str(R/'experiments/taalas-access/main.drc')]
for k,v in dict(input=W/'input.gds',report=W/'drc.lyrdb',topcell='RV_JOINED_BANK_00_0',feol='true',beol='true',conn_drc='true',offgrid='true',metal_top='11K',metal_level='5LM',mim_option='B',run_mode='flat',thr=1).items():cmd+=['-rd',f'{k}={v}']
(W/'drc-command.json').write_text(json.dumps(cmd,indent=2));run(cmd,'drc.log')
xml=ET.parse(W/'drc.lyrdb').getroot();markers=xml.findall('./items/item');cats={}
for item in markers:
 c=item.findtext('category');cats[c]=cats.get(c,0)+1
result={'input_source':str(source.relative_to(R)),'input_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'drc_markers':len(markers),'categories':cats,'drc_scope':'FEOL BEOL connectivity offgrid; excludes antenna/density'}
(W/'checks.json').write_text(json.dumps(result,indent=2));print(result,flush=True)
if markers:raise SystemExit(2)
(W/'extract.tcl').write_text('gds readonly true\ngds read input.gds\nload RV_JOINED_BANK_00_0\nflatten RV_JOINED_FLAT\nload RV_JOINED_FLAT\nextract all\next2spice lvs\next2spice -o joined.spice\next2spice cthresh 0\next2spice -o joined-cap.spice\nquit -noprompt\n')
run(['magic','-dnull','-noconsole','-rcfile',str(PDK/'libs.tech/magic/gf180mcuD.magicrc'),'extract.tcl'],'extract.log')
assert (W/'joined-cap.spice').is_file()
print('Joined bank extracted',flush=True)
