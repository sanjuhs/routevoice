from pathlib import Path
import json,re,shutil
P=Path(__file__).resolve().parent
out=P/'handoff-v2';out.mkdir(exist_ok=True)
for tag,name in [('decoderb-v1','w5_row_decoder'),('mux128b-v1','w5_bank_mux128'),('bankdec-v1','w5_bank_decoder')]:
 f=P/'runs'/tag/'final'
 if not f.exists():continue
 pins={}
 text=(f/'lef'/f'{name}.lef').read_text()
 for m in re.finditer(r'^  PIN (\S+)\n(.*?)^  END \1$',text,re.M|re.S):
  body=m[2];rects=[]
  for layer,x0,y0,x1,y1 in re.findall(r'LAYER (\S+)\s*;\s*RECT ([\d.-]+) ([\d.-]+) ([\d.-]+) ([\d.-]+)',body):rects.append(dict(layer=layer,rect_um=list(map(float,[x0,y0,x1,y1]))))
  pins[m[1]]=rects
 (out/f'{name}-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
 for ext in ['lef','gds','def','nl','spice']:
  for file in (f/ext).glob('*'):shutil.copy2(file,out/file.name)
 j=json.loads((f/'metrics.json').read_text())
 if name=='w5_bank_mux128':j.update(json.loads((P/'runs/mux128b-poststa/final/metrics.json').read_text()))
 keep={k:v for k,v in j.items() if any(s in k for s in ['design__die__area','design__core__area','design__instance__area__stdcell','drc_error','lvs_','max_slew_violation','max_cap_violation','timing__setup__ws'])}
 (out/f'{name}-metrics.json').write_text(json.dumps(keep,indent=2)+'\n')
 print(name,'pins',len(pins))
