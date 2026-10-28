#!/usr/bin/env python3
"""Parameterized abstract whole-chip floorplan. All lengths in microns, power W."""
import argparse,json,math,re,hashlib
from pathlib import Path
from area_models import configure,block_area
W=Path(__file__).resolve().parent

def tile_blocks(cfg,scenario,partition='whole'):
 s=cfg['scenarios'][scenario]; tiles=[]; areas=[]
 for b in cfg['blocks']:
  group='encoder' if b['name'].startswith(('frontend','encoder','producer','KV')) else 'decoder'
  if partition!='whole' and 'source_hashes' not in cfg and group!=partition: continue
  breakdown=block_area(cfg,b,scenario);area=breakdown['total_mm2']
  n=math.ceil(area/cfg['maximum_tile_area_mm2']); side=math.ceil(math.sqrt(area/n)*1000/5)*5
  areas.append(dict(name=b['name'],area_mm2=area,tiles=n,area_breakdown=breakdown,power_w=b['power_w']))
  for i in range(n):tiles.append(dict(name=f"{b['name']}_{i}",block=b['name'],w=side,h=side,power=b['power_w']/n,modeled_area_mm2=area/n,replicate=b.get('replicate_per_die',False)))
 if partition!='whole' and 'source_hashes' in cfg:
  bins=[[],[]];loads=[0.,0.]
  for t in sorted(tiles,key=lambda t:t['w']*t['h'],reverse=True):
   if t['replicate']:
    for j in range(2):bins[j].append(t.copy());loads[j]+=t['modeled_area_mm2']
   else:
    j=min(range(2),key=lambda j:loads[j]);bins[j].append(t);loads[j]+=t['modeled_area_mm2']
  tiles=bins[0 if partition=='encoder' else 1];areas=[]
  for b in cfg['blocks']:
   bt=[t for t in tiles if t['block']==b['name']]
   if bt:areas.append(dict(name=b['name'],area_mm2=sum(t['modeled_area_mm2'] for t in bt),tiles=len(bt),power_w=sum(t['power'] for t in bt)))
 if partition!='whole':
  tiles.append(dict(name='die_link_interface',block='die_link_interface',w=2000,h=2000,power=.04))
  areas.append(dict(name='die_link_interface',area_mm2=4,tiles=1,power_w=.04))
 return tiles,areas

def pack(tiles,die,margin=700,halo=30,height=None):
 height=die if height is None else height
 # Descending-height shelves, deterministic, no overlaps; not a minimum packing proof.
 shelves=[]
 for t in sorted(tiles,key=lambda t:t['h'],reverse=True):
  tw,th=t['w']+2*halo,t['h']+2*halo
  found=next((s for s in shelves if s['h']>=th and s['x']+tw<=die-margin),None)
  if found is None:
   y=margin+sum(s['h'] for s in shelves)
   if y+th>height-margin:return False
   found=dict(y=y,h=th,x=margin);shelves.append(found)
  t.update(x=found['x']+halo,y=found['y']+halo); found['x']+=tw
 return True

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--memory',default='sram_open_macro');ap.add_argument('--levers',choices=['off','on','books','lossless'],default='off');ap.add_argument('--state',choices=['baseline','conservative'],default='baseline');ap.add_argument('--blocks',default=str(W/'blocks.json'));ap.add_argument('--scenario',required=True);ap.add_argument('--die-mm',type=float,required=True);ap.add_argument('--height-mm',type=float);ap.add_argument('--pdn-width-um',type=int,default=20);ap.add_argument('--supply-pad-pairs',type=int);ap.add_argument('--partition',default='whole',choices=['whole','encoder','decoder']);a=ap.parse_args()
 cfg=configure(json.loads(Path(a.blocks).read_text()),a.memory,a.levers,a.state);die=round(a.die_mm*1000);height=round((a.height_mm or a.die_mm)*1000);tiles,areas=tile_blocks(cfg,a.scenario,a.partition)
 out=W/'runs'/f'{a.scenario}_{a.memory}_{a.levers}_{a.state}_{a.partition}_{a.die_mm:g}{('x'+format(a.height_mm,'g')) if a.height_mm else ''}mm{('_pdn'+str(a.pdn_width_um)) if a.pdn_width_um!=20 else ''}{('_pads'+str(a.supply_pad_pairs)) if a.supply_pad_pairs else ''}';out.mkdir(parents=True,exist_ok=True)
 (out/'blocks_snapshot.json').write_text(json.dumps(cfg,indent=2)+'\n')
 power=sum(t['power'] for t in tiles);pairs=max(8,4*math.ceil(power/cfg['vdd']*cfg['pad_current_margin']/cfg['pad_current_budget_a']/4))
 minimum_pairs=pairs
 if a.supply_pad_pairs is not None:
  if a.supply_pad_pairs<pairs or a.supply_pad_pairs%4:ap.error('supply pad pairs must be a multiple of4 and at least current-derived count')
  pairs=a.supply_pad_pairs
 fit=pack(tiles,die,halo=cfg['macro_halo_um'],height=height)
 result=dict(memory=a.memory,levers=a.levers,state=a.state,scenario=a.scenario,partition=a.partition,die_mm=a.die_mm,die_width_mm=a.die_mm,die_height_mm=height/1000,block_area_mm2=sum(x['area_mm2'] for x in areas),abstract_rect_area_mm2=sum(t['w']*t['h']/1e6 for t in tiles),core_area_mm2=(a.die_mm-1.4)*(height/1000-1.4),placement_pass=fit,pdn_pass=False,worst_ir_drop_v=None,power_assumed_w=power,supply_pad_pairs=pairs,signal_pad_count=16,pad_count=pairs*2+16,areas=areas,tiles=tiles,macro_scope='ABSTRACTS, not routed internals',run_dir=str(out.relative_to(W)),vdd=cfg['vdd'])
 result['minimum_current_derived_pad_pairs']=minimum_pairs
 result['pdn_strap_width_um']=a.pdn_width_um
 result['blocks_sha256']=hashlib.sha256((out/'blocks_snapshot.json').read_bytes()).hexdigest()
 result['placement_utilization']=result['abstract_rect_area_mm2']/result['core_area_mm2']
 (out/'manifest.json').write_text(json.dumps(result,indent=2))
 if not fit:
  print(f'W3-STATUS: {out.name}: placement FAIL, blocks={result["block_area_mm2"]:.2f}mm2 core={result["core_area_mm2"]:.2f}mm2');return
 lef=['VERSION 5.8 ;','BUSBITCHARS "[]" ;','DIVIDERCHAR "/" ;']
 for t in tiles:
  n=t['name'];w=t['w'];h=t['h'];lef +=[f'MACRO M_{n}',' CLASS BLOCK ;',' ORIGIN 0 0 ;',f' SIZE {w} BY {h} ;',' SYMMETRY X Y ;']
  # Alternating vertical power-pin rails across whole macro allow distributed load access.
  for net,shift,use in [('VDD',0,'POWER'),('VSS',200,'GROUND')]:
   lef +=[f' PIN {net}',' DIRECTION INOUT ;',f' USE {use} ;',' PORT',' LAYER Metal4 ;']
   for x in range(100+shift,w-20,400):lef +=[f' RECT {x} 10 {x+20} {h-10} ;']
   lef +=[' END',f' END {net}']
  lef +=[' OBS']
  for layer in ['Metal1','Metal2','Metal3']:lef +=[f' LAYER {layer} ;',f' RECT 0 0 {w} {h} ;']
  lef+=[' END',f'END M_{n}']
 lef+=['END LIBRARY'];(out/'macros.lef').write_text('\n'.join(lef)+'\n')
 # Instance creation uses OpenDB so LEF-only macro abstracts need no invented timing model.
 tcl=['set_thread_count 4',f'read_lef {{{W}/pdk/gf180mcu_fd_sc_mcu7t5v0__nom.tlef}}',f'read_lef {{{W}/pdk/gf180mcu_fd_sc_mcu7t5v0.lef}}',f'read_liberty {{{W}/pdk/gf180mcu_fd_sc_mcu7t5v0__tt_025C_3v30.lib}}']
 for p in sorted((W/'pdk').glob('*fd_io*.lef')):tcl.append(f'read_lef {{{p}}}')
 tcl +=[f'read_lef {{{out}/macros.lef}}',f'read_verilog {{{out}/top.v}}','link_design routevoice',f'initialize_floorplan -site GF018hv5v_mcu_sc7 -die_area {{0 0 {die} {height}}} -core_area {{700 700 {die-700} {height-700}}}', 'make_tracks', 'set db [ord::get_db]','set block [ord::get_db_block]', '''proc inst {name master x y orient} {
 global db block
 set i [odb::dbInst_create $block [$db findMaster $master] $name]
 $i setOrient $orient
 $i setLocation [expr {int($x*2000)}] [expr {int($y*2000)}]
 $i setPlacementStatus FIRM
}''']
 (out/'top.v').write_text('module routevoice(input clk); endmodule\n')
 for t in tiles:tcl.append(f'inst {t["name"]} M_{t["name"]} {t["x"]} {t["y"]} R0')
 # Abutted GF180 pads, actual corner/filler masters. R0 has bond opening toward south.
 corners=[(0,0,'R0'),(die-355,0,'R90'),(die-355,height-355,'R180'),(0,height-355,'R270')]
 for i,(x,y,o) in enumerate(corners):tcl.append(f'inst corner_{i} gf180mcu_fd_io__cor {x} {y} {o}')
 signals=['pcm_data','pcm_bclk','pcm_lrclk','token_data','token_valid','token_ready','clock','reset_n','spi_sck','spi_mosi','spi_miso','spi_cs_n','uart_rx','uart_tx','test_en','status']
 pads=[]
 for side in range(4):
  cells=[]
  for k in range(pairs//4):cells.extend([(f'vdd_{side}_{k}','dvdd'),(f'vss_{side}_{k}','dvss')])
  cells.extend([(signals[side*4+k],'bi_t') for k in range(4)])
  side_length=die if side%2==0 else height
  available=side_length-710; gap=(available-len(cells)*75)//len(cells); pos=355;fi=0
  def place(name,master,width):
   nonlocal pos
   if side==0:x,y,o=pos,0,'R0'
   elif side==1:x,y,o=die-350,pos,'R90'
   elif side==2:x,y,o=die-pos-width,height-350,'R180'
   else:x,y,o=0,height-pos-width,'R270'
   tcl.append(f'inst {name} gf180mcu_fd_io__{master} {x} {y} {o}')
   if master in ('dvdd','dvss','bi_t'):pads.append(dict(name=name,master=master,x=x,y=y,orientation=o))
   pos+=width
  def fill(length):
   nonlocal fi
   for width in [10,5,1]:
    for _ in range(length//width):place(f'fill_{side}_{fi}',f'fill{width}',width);fi+=1
    length%=width
  for name,master in cells:place(name,master,75);fill(gap)
  fill(side_length-355-pos)
 result['pads']=pads
 tcl +=['add_global_connection -net VDD -pin_pattern {^(VDD|DVDD)$} -power','add_global_connection -net VSS -pin_pattern {^(VSS|DVSS)$} -ground','global_connect','connect_by_abutment',f'write_def {{{out}/placed.def}}','set_voltage_domain -name CORE -power VDD -ground VSS','define_pdn_grid -name core -voltage_domains CORE -pins {Metal5} -obstructions {Metal1 Metal2 Metal3}', 'add_pdn_ring -grid core -layers {Metal4 Metal5} -widths 40 -spacings 20 -core_offsets 80 -connect_to_pads -connect_to_pad_layers {Metal2}', f'add_pdn_stripe -grid core -layer Metal4 -width {a.pdn_width_um} -pitch 400 -offset 100 -extend_to_core_ring',f'add_pdn_stripe -grid core -layer Metal5 -width {a.pdn_width_um} -pitch 400 -offset 100 -extend_to_core_ring','add_pdn_connect -grid core -layers {Metal2 Metal4} -cut_pitch 20 -max_rows 2 -max_columns 2', 'add_pdn_connect -grid core -layers {Metal2 Metal5} -cut_pitch 20 -max_rows 2 -max_columns 2', 'add_pdn_connect -grid core -layers {Metal4 Metal5} -cut_pitch 20 -max_rows 2 -max_columns 2', 'define_pdn_grid -macro -name macros -cells {M_.*} -grid_over_boundary -halo 0 -obstructions {Metal1 Metal2 Metal3}', 'add_pdn_connect -grid macros -layers {Metal4 Metal5} -cut_pitch 20 -max_rows 2 -max_columns 2',f'pdngen -failed_via_report {{{out}/failed_vias.rpt}}',f'write_def {{{out}/floorplan.def}}',f'write_db {{{out}/floorplan.odb}}',f'catch {{save_image -width 1600 {{{out}/floorplan.png}}}} imgerr','puts "IMAGE: $imgerr"', 'set_pdnsim_net_voltage -net VDD -voltage 3.3','set_pdnsim_net_voltage -net VSS -voltage 0']
 for t in tiles:tcl.append(f'set_pdnsim_inst_power -inst {t["name"]} -power {t["power"]:.12f}')
 for net in ['VDD','VSS']:
  sources=[]
  for pad in pads:
   if pad['master']!=('dvdd' if net=='VDD' else 'dvss'):continue
   # Bond/feed pin largest Metal5 rectangle; use actual transformed pin center.
   txt=(W/'pdk'/f"gf180mcu_fd_io__{pad['master']}.lef").read_text()
   sec=txt.split('  PIN D'+net+'\n')[1].split('  END D'+net)[0]
   rects=[]
   for port in sec.split('LAYER Metal5 ;')[1:]:
    m=re.search(r'RECT ([\d.]+) ([\d.]+) ([\d.]+) ([\d.]+)',port)
    if m:rects.append(tuple(map(float,m.groups())))
   r=max(rects,key=lambda r:(r[2]-r[0])*(r[3]-r[1]));u=(r[0]+r[2])/2;v=(r[1]+r[3])/2
   if pad['orientation']=='R0':x,y=u,v
   elif pad['orientation']=='R90':x,y=350-v,u
   elif pad['orientation']=='R180':x,y=75-u,350-v
   else:x,y=v,75-u
   sources.append(f"{pad['x']+x},{pad['y']+y},20,{cfg['vdd'] if net=='VDD' else 0}")
  (out/f'{net}_sources.csv').write_text('\n'.join(sources)+'\n')
  tcl +=[f'if {{[catch {{check_power_grid -net {net} -error_file {{{out}/{net}_connectivity.rpt}}}} err]}} {{puts "W3_CONNECTIVITY_{net}_FAIL: $err"}} else {{puts "W3_CONNECTIVITY_{net}_PASS"}}',f'if {{[catch {{analyze_power_grid -net {net} -voltage_file {{{out}/{net}_voltage.rpt}} -error_file {{{out}/{net}_ir_errors.rpt}} -vsrc {{{out}/{net}_sources.csv}}}} err]}} {{puts "W3_IR_{net}_FAIL: $err"}} else {{puts "W3_IR_{net}_PASS"}}']
 tcl+=['exit']; (out/'floorplan.tcl').write_text('\n'.join(tcl)+'\n');(out/'manifest.json').write_text(json.dumps(result,indent=2))
 print(f'W3-STATUS: {out.name}: placement PASS {len(tiles)} macros, {result["block_area_mm2"]:.2f}mm2; power={power:.3f}W assumed; {pairs} supply pairs')
if __name__=='__main__':main()
