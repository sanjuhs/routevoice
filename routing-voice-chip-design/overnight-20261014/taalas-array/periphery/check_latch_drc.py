from pathlib import Path
import subprocess,json,xml.etree.ElementTree as ET,os,hashlib
P=Path(__file__).resolve().parent;R=P.parents[2]
PDK=R/'pdks/gf180mcuD';rules=PDK/'libs.tech/klayout/tech/drc/rule_decks'
files=[rules/'main.drc']+sorted(p for p in rules.glob('*.drc') if not any(s in p.name for s in ['antenna','density','main','layers_def','tail']))+[rules/'tail.drc']
(P/'main.drc').write_text('\n'.join(p.read_text() for p in files));(P/'layers_def.drc').write_bytes((rules/'layers_def.drc').read_bytes())
T='/nix/store/yczxlrrywxp7q2aavm4b3zrj3lpmq18a-devshell-dir/bin/klayout'
result={}
for gds in (P/'handoff-latch128').glob('*.gds'):
 top=gds.stem;report=P/(top+'.lyrdb');opt=dict(input=str(gds),report=str(report),topcell=top,feol='true',beol='true',conn_drc='true',offgrid='true',metal_top='11K',metal_level='5LM',mim_option='B',run_mode='deep',thr='1')
 cmd=['nice','-n','10',T,'-b','-r',str(P/'main.drc')]
 for k,v in opt.items():cmd+=['-rd',f'{k}={v}']
 with (P/(top+'-drc.log')).open('w') as f:subprocess.run(cmd,cwd=P,stdout=f,stderr=subprocess.STDOUT,check=True,timeout=900,env=dict(os.environ,QT_QPA_PLATFORM='offscreen',TMPDIR=str(P/'tmp')))
 xml=ET.parse(report).getroot();items=xml.findall('./items/item');cats={}
 for x in items:cats[x.findtext('category')]=cats.get(x.findtext('category'),0)+1
 result[top]=dict(markers=len(items),categories=cats,command=cmd,scope='GF180 FEOL BEOL connectivity offgrid; density and antenna excluded',gds_sha256=hashlib.sha256(gds.read_bytes()).hexdigest())
 print(top,len(items),cats,flush=True)
(P/'latch-drc.json').write_text(json.dumps(result,indent=2)+'\n')
