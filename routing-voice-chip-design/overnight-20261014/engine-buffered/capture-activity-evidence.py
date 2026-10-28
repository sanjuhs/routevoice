from pathlib import Path
import hashlib,json,re,datetime
W=Path(__file__).resolve().parent
log=W/'logs/lead-gate-activity.log';txt=log.read_text();assert 'PASS gate_activity vectors=1 outputs=320' in txt and '$finish' in txt
assert (W/'evidence/gate-full.status').exists()
saif=W/'evidence/array_port-mapped-speech-w9-frozen.saif'
with saif.open() as f:header=f.read(16384)
duration=int(re.search(r'\(DURATION\s+(\d+)\)',header).group(1));unit=re.search(r'\(TIMESCALE\s+([^)]*)\)',header).group(1).strip();assert re.fullmatch(r'1\s*ps',unit) and duration==83320000,(unit,duration)
files=[saif,log,W/'tb/activity_array_port.sv',W/'runs/buf-v4/01-yosys-synthesis/rv_k64_array_port.nl.v',W/'vectors/inputs.hex',W/'vectors/activation-scales.hex',W/'vectors/expected.hex',W/'evidence/gate-activity-inputs.sha256']
artifacts={}
for p in files:
 with p.open('rb') as f:h=hashlib.file_digest(f,'sha256').hexdigest()
 artifacts[str(p.relative_to(W))]={'bytes':p.stat().st_size,'sha256':h}
values=[int(x,16) for x in (W/'vectors/inputs.hex').read_text().split()[:1280]];values=[v-512 if v>=256 else v for v in values]
serial=W/'logs/gate-full-simulation.log';serialpass=serial.exists() and 'PASS gate vectors=54 outputs=17280' in serial.read_text()
r={'updated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'variant':'array_port_buf_v4','status':'all_54_gate_vectors_passed_and_one_vector_trace_complete','vectors':1,'fp32_outputs':320,'cycles_excluding_start':4163,'clock_period_ns':20,'trace_duration_ps':duration,'trace_duration_us':duration/1e6,'initial_reset_included':True,'activity_scope':'tb/dut','trace_provenance':'Completed lead-labelled repeat of the same W9 activity executable; original W9 pass and hash preserved separately; frozen-activity-provenance.json records replacement','gate_verification':'original serial 54-vector pass' if serialpass else 'eight shards, all 54 vectors, exact original per-vector stall cycles; see gate-sharded-results.json','activity':'Zero-delay mapped standard cells, saved real activation vector0; no SDF glitch timing, not long-stream/idle/peak characterization.','activation_statistics':{'samples':len(values),'min':min(values),'max':max(values),'zero_count':values.count(0),'mean_absolute':sum(abs(v) for v in values)/len(values)},'artifacts':artifacts,'annotation_coverage_pending':True,'power_computed':False}
probe=W/'evidence/placed-saif-annotation.rpt'
if probe.exists():
 counts={k:int(v) for k,v in re.findall(r'^(saif|unannotated)\s+(\d+)',probe.read_text(),re.M)}
 if set(counts)=={'saif','unannotated'}:
  r['placed_annotation']={'annotated_pins':counts['saif'],'unannotated_pins':counts['unannotated'],'coverage_fraction':counts['saif']/sum(counts.values()),'stage':'buf-v4/23-openroad-globalplacement','routed':False,'report':str(probe)}
(W/'evidence/array_port-mapped-activity.json').write_text(json.dumps(r,indent=2)+'\n');print('W9-STATUS: new mapped activity receipt saved',duration,'ps',saif.stat().st_size,'bytes')
