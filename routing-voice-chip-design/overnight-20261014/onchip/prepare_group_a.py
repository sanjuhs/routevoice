"""Reproducibly prepare W1 group (a); never edit the retained design or fixture."""
from pathlib import Path
import hashlib
import json
import re
import shutil

WORK = Path(__file__).resolve().parent
ROOT = WORK.parents[1]
SRC = ROOT / 'experiments/chip-integration-20261012-frontend-learned-norm-connected-source-v3'
RUN = Path.home() / '.local/state/routevoice-internal-runs/20261014/onchip'
FIX = Path.home() / '.local/state/routevoice-internal-runs/20261012/voice-e2e-onboard-numerical-fixture-v3'
OLD = 'rv_pcm_encoder_greedy_frontend_history_producer_metadata_KV_tables_onboard_v1'
NEW = 'rv_allonchip_top_v1'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def replace_once(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new)

def main():
    RUN.mkdir(parents=True, exist_ok=True)
    romdir = WORK / 'rom'
    romdir.mkdir(exist_ok=True)
    images = {
        'cross_coeff': ('cross/coefficients.bin', 1228800),
        'cross_meta': ('cross/metadata.bin', 30720),
        'ff_up_coeff': ('ff/up-weights.bin', 4915200),
        'ff_down_coeff': ('ff/down-weights.bin', 2457600),
        'ff_up_meta': ('ff/up-metadata.bin', 245760),
        'ff_down_meta': ('ff/down-metadata.bin', 30720),
        'self_coeff': ('self/coefficients.bin', 2457600),
        'self_meta': ('self/metadata.bin', 61440),
    }
    manifest = []
    for name, (relative, size) in images.items():
        source = FIX / relative
        data = source.read_bytes()
        assert len(data) == size and size % 32 == 0
        target = romdir / (name + '.hex')
        # Lane zero occupies bits [31:0]; binary input is little endian.
        target.write_text(''.join(data[i:i+32][::-1].hex() + '\n' for i in range(0, size, 32)))
        # Independent round trip of the emitted hex, before any simulator uses it.
        restored = b''.join(int(line, 16).to_bytes(32, 'little') for line in target.read_text().splitlines())
        assert restored == data
        manifest.append(dict(name=name, input=str(source), input_bytes=size,
                             input_sha256=digest(source), output=str(target),
                             output_sha256=digest(target), width_bits=256, words=size//32,
                             roundtrip_pass=True))
    (WORK / 'rom-manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')

    for kind in ('decoder_body', 'decoder_self'):
        body = kind == 'decoder_body'
        names = list(images)[:6] if body else list(images)[6:]
        params = ',\n'.join(f'  parameter {n.upper()}_FILE = "{romdir / (n + ".hex")}"' for n in names)
        rw, ww = (3, 14) if body else (2, 12)
        tile_ports = '  input wire [2:0] req_tile,\n  output logic [2:0] rsp_tile,\n' if body else ''
        declarations = '\n'.join(f'  logic [255:0] {n} [0:{images[n][1]//32-1}];\n  initial $readmemh({n.upper()}_FILE, {n});' for n in names)
        if body:
            address = '''    legal = req_layer < 6 && req_role >= 4 &&
      ((req_role < 6 && req_tile == 0 && req_word < (req_region ? 80 : 3200)) ||
       (req_role == 6 && req_word < (req_region ? 160 : 3200)) ||
       (req_role == 7 && req_tile == 0 && req_word < (req_region ? 160 : 12800)));
    case (req_role)
      4,5: begin
        if (req_region) begin
          address = (32'(req_layer)*2 + 32'(req_role)-4)*80 + 32'(req_word);
          if (legal) selected = cross_meta[address];
        end else begin
          address = (32'(req_layer)*2 + 32'(req_role)-4)*3200 + 32'(req_word);
          if (legal) selected = cross_coeff[address];
        end
      end
      6: begin
        if (req_region) begin
          address = 32'(req_layer)*1280 + 32'(req_tile)*160 + 32'(req_word);
          if (legal) selected = ff_up_meta[address];
        end else begin
          address = (32'(req_layer)*320 + 32'(req_word)/10)*80 + 32'(req_tile)*10 + 32'(req_word)%10;
          if (legal) selected = ff_up_coeff[address];
        end
      end
      7: begin
        if (req_region) begin
          address = 32'(req_layer)*160 + 32'(req_word);
          if (legal) selected = ff_down_meta[address];
        end else begin
          address = 32'(req_layer)*12800 + 32'(req_word);
          if (legal) selected = ff_down_coeff[address];
        end
      end
      default: ;
    endcase'''
        else:
            address = '''    legal = req_layer < 6 && req_word < (req_region ? 80 : 3200);
    if (req_region) begin
      address = (32'(req_layer)*4 + 32'(req_role))*80 + 32'(req_word);
      if (legal) selected = self_meta[address];
    end else begin
      address = (32'(req_layer)*4 + 32'(req_role))*3200 + 32'(req_word);
      if (legal) selected = self_coeff[address];
    end'''
        rtl = f'''// W1 functional immutable ROM backend. No runtime write port.
// Accepted edge N -> held response at PRE N+1, matching mode0 host.
// POR clears the queue; warm reset fences acceptance/ACK and retains its payload.
// Native UINT8/metadata payloads are unchanged. This is not a custom macro PPA proof.
module rv_onchip_{kind}_v1 #(
{params}
)(
  input wire clk, por_reset, warm_reset,
  input wire req_valid,
  output wire req_ready,
  input wire [31:0] req_tag,
  input wire [2:0] req_layer,
  input wire [{rw-1}:0] req_role,
  input wire req_region,
  input wire [{ww-1}:0] req_word,
{tile_ports}  output wire idle,
  output logic fault,
  output logic rsp_valid,
  input wire rsp_ready,
  output logic [31:0] rsp_tag,
  output logic [2:0] rsp_layer,
  output logic [{rw-1}:0] rsp_role,
  output logic rsp_region,
  output logic [{ww-1}:0] rsp_word,
  output logic [255:0] rsp_data
);
{declarations}
  wire available = !rsp_valid;
  assign req_ready = available;
  assign idle = available;
  logic legal;
  logic [255:0] selected;
  integer unsigned address;
  always_comb begin
    selected = '0;
    address = 0;
{address}
  end
  always_ff @(posedge clk) begin
    if (por_reset) begin
      rsp_valid <= 0; fault <= 0;
      rsp_tag <= 0; rsp_layer <= 0; rsp_role <= 0;
      rsp_region <= 0; rsp_word <= 0; rsp_data <= 0;
{('      rsp_tile <= 0;' if body else '')}
    end else if (!warm_reset) begin
      if (rsp_valid && rsp_ready) rsp_valid <= 0;
      if (req_valid && req_ready) begin
        rsp_valid <= 1;
        rsp_tag <= req_tag; rsp_layer <= req_layer; rsp_role <= req_role;
        rsp_region <= req_region; rsp_word <= req_word; rsp_data <= selected;
{('        rsp_tile <= req_tile;' if body else '')}
        if (!legal) fault <= 1;
      end
    end
  end
endmodule
'''
        (WORK / f'rv_onchip_{kind}_v1.sv').write_text(rtl)

    moved = set('memory_idle req_ready rsp_valid rsp_tag rsp_layer rsp_role rsp_tile rsp_region rsp_word rsp_data'.split())
    moved |= set('compact_fixed_idle compact_fixed_req_ready compact_fixed_rsp_valid compact_fixed_rsp_tag compact_fixed_rsp_layer compact_fixed_rsp_role compact_fixed_rsp_region compact_fixed_rsp_word compact_fixed_rsp_data'.split())
    oldrtl = (SRC / (OLD+'.sv')).read_text()
    header = oldrtl[oldrtl.index('(\n')+2:oldrtl.index('\n);')]
    # Resolve every ANSI declaration, including comma-grouped names, independently.
    ports = []
    for line in header.splitlines():
        line = line.split('//')[0].strip().rstrip(',')
        if not line:
            continue
        m = re.fullmatch(r'(input|output) wire\s*(\[[^]]+\])?\s*(.*)', line)
        assert m, line
        direction, width, names = m.groups()
        for name in names.split(','):
            name = name.strip()
            assert re.fullmatch(r'\w+', name), name
            ports.append((direction, width or '', name))
    assert moved <= {n for d,w,n in ports}
    header = ',\n'.join(f'  {"output" if n in moved else d} wire {w} {n}' for d,w,n in ports)
    wrapper = '// Group (a): original top is instantiated unchanged; all moved service buses are observable outputs.\n'
    wrapper += f'module {NEW}(\n{header},\n  output wire onchip_body_fault, onchip_self_fault\n);\n'
    wrapper += f'  {OLD} original (\n'+',\n'.join(f'    .{n}({n})' for d,w,n in ports)+'\n  );\n'
    for kind, prefix, idle, fault in [('decoder_body', '', 'memory_idle', 'onchip_body_fault'),
                                      ('decoder_self', 'compact_fixed_', 'compact_fixed_idle', 'onchip_self_fault')]:
        connections = dict(clk='clk', por_reset='table_por_reset', warm_reset='reset', idle=idle, fault=fault)
        for n in 'req_valid req_ready req_tag req_layer req_role req_region req_word rsp_valid rsp_ready rsp_tag rsp_layer rsp_role rsp_region rsp_word rsp_data'.split():
            connections[n] = prefix+n
        if kind == 'decoder_body':
            connections.update(req_tile='req_tile', rsp_tile='rsp_tile')
        wrapper += f'  rv_onchip_{kind}_v1 {kind} (\n'+',\n'.join(f'    .{a}({b})' for a,b in connections.items())+'\n  );\n'
    wrapper += 'endmodule\n'
    (WORK / (NEW+'.sv')).write_text(wrapper)
    for source in SRC.glob('*.hpp'):
        shutil.copyfile(source, WORK / source.name)
    host = (SRC / 'four_stage.cpp').read_text().replace(OLD, NEW)
    # Remove initialization writes as well as runtime response drivers.
    for name in moved:
        host = re.sub(r'(?:for\(unsigned i=0;i<8;i\+\+\))?t\.'+name+r'(?:\[i\])?=[01];', '', host)
    (WORK / 'four_stage.cpp').write_text(host)

    p = (WORK / 'producer_services.hpp').read_text()
    p = replace_once(p, 't.req_ready=!mem.active&&!extra_mem.active&&(!mode||(r&12));', '')
    start = p.index('  const auto& response=extra_mem.active?extra_mem:mem;')
    end = p.index('  producer.drive();', start)
    p = p[:start]+p[end:]
    marker = '  if(observation_hook)observation_hook();learned_observe();'
    observe = '''
  check(mode==0&&fault==0&&!extra_mem.active,"onchip body qualified nominal mode only");
  check(!t.onchip_body_fault,"onchip body ROM address fault");
  check(bool(t.req_ready)==!mem.active&&bool(t.memory_idle)==!mem.active,"onchip body queue ready/idle");
  check(bool(t.rsp_valid)==mem.active,"onchip body exact PRE N+1 schedule");
  if(t.rsp_valid){
   check(t.rsp_tag==mem.tag&&t.rsp_layer==mem.layer&&t.rsp_role==mem.role&&t.rsp_tile==mem.tile&&t.rsp_region==mem.region&&t.rsp_word==mem.word,"onchip body held reply identity");
   for(unsigned j=0;j<8;j++)equal(t.rsp_data[j],mem.data[j],"onchip body ROM payload mismatch");
  }
'''
    p = replace_once(p, marker, marker+observe)
    marker = ' void finish_observed(){'
    p = replace_once(p, marker, marker+'''
  check(requests==1392000&&replies==1392000&&compact.fixed_requests==787200&&compact.fixed_responses==787200,"onchip F64 group a exact coverage");
  std::cout<<"ONCHIP service=decoder_body rtl_replies="<<replies<<" host_replies=0 mismatches=0"<<std::endl;
  std::cout<<"ONCHIP service=decoder_self rtl_replies="<<compact.fixed_responses<<" host_replies=0 mismatches=0"<<std::endl;
''')
    (WORK / 'producer_services.hpp').write_text(p)
    p = (WORK / 'taalas_decoder_token_compact_services.hpp').read_text()
    start = p.index(' void drive(){')
    end = p.index(' uint32_t expected_record_word', start)
    p = p[:start]+''' void drive(){} // Both fixed ROM and mutable history are now RTL-owned.
 void observe_fixed(){
  auto&t=h.t;
  h.check(h.mode==0&&!fixed_extra.active,"onchip compact qualified nominal mode only");
  h.check(!t.onchip_self_fault,"onchip compact ROM address fault");
  h.check(bool(t.compact_fixed_req_ready)==!fixed.active&&bool(t.compact_fixed_idle)==!fixed.active,"onchip compact queue ready/idle");
  h.check(bool(t.compact_fixed_rsp_valid)==fixed.active,"onchip compact exact PRE N+1 schedule");
  if(t.compact_fixed_rsp_valid){
   h.check(t.compact_fixed_rsp_tag==fixed.tag&&t.compact_fixed_rsp_layer==fixed.layer&&t.compact_fixed_rsp_role==fixed.role&&t.compact_fixed_rsp_region==fixed.region&&t.compact_fixed_rsp_word==fixed.word,"onchip compact held reply identity");
   for(unsigned j=0;j<8;j++)h.equal(t.compact_fixed_rsp_data[j],fixed.data[j],"onchip compact ROM payload mismatch");
  }
 }
'''+p[end:]
    p = replace_once(p, 'auto&t=h.t;observe_memory();', 'auto&t=h.t;observe_fixed();observe_memory();')
    (WORK / 'taalas_decoder_token_compact_services.hpp').write_text(p)
    # Fail preparation if any copied host code still writes a moved output.
    for path in [WORK/'four_stage.cpp', *WORK.glob('*.hpp')]:
        for name in moved:
            assert not re.search(r'\bt\.'+name+r'(?:\[[^]]+\])?\s*=(?!=)',path.read_text()), (path, name)

    c = json.loads((ROOT/'experiments/chip-integration-20261012-Q8-learned-fulltables-lint-generation-control-v2/commands.json').read_text())
    for key, args in c.items():
        args[args.index('--top-module')+1] = NEW
        args[args.index('--Mdir')+1] = str(RUN / ('obj-a' if key=='generate-full' else 'lint-a'))
        args.extend(str(WORK / f) for f in [NEW+'.sv', 'rv_onchip_decoder_body_v1.sv', 'rv_onchip_decoder_self_v1.sv'])
        if key=='generate-full':
            args[args.index(str(SRC/'four_stage.cpp'))] = str(WORK/'four_stage.cpp')
            i=args.index('-CFLAGS')+1
            args[i] = args[i].replace(str(SRC), str(WORK))
    (WORK/'no-pch.mk').write_text((ROOT/'experiments/chip-integration-20261012-Q8-learned-fulltables-compile-v3/no-pch.mk').read_text().replace(OLD, NEW))
    c['compile'] = ['/usr/bin/make', '-C', str(RUN/'obj-a'), '-f', str(WORK/'no-pch.mk'), '-j8', 'OPT_FAST=-O3', 'OPT_SLOW=-O3', 'CXX=/usr/bin/c++', 'LINK=/usr/bin/c++', 'VM_PARALLEL_BUILDS=1']
    numeric = json.loads((ROOT/'experiments/chip-integration-20261012-Q8-learned-fulltables-numerical-run-v2/commands.json').read_text())
    oldrun = str(Path.home()/'.local/state/routevoice-internal-runs/20261012/Q8-learned-fulltables-numerical-run-v2/actual')
    for key in ['fixture','positive','render']:
        args = numeric[key]
        if key!='render':
            args[0] = str(RUN/'obj-a'/('V'+NEW))
        c[key] = [a.replace(oldrun,str(RUN/'actual-a')) for a in args]
    for service in ['body','self']:
        module = f'rv_onchip_decoder_{service}_v1'
        obj = RUN/f'unit-{service}'
        c[f'unit-{service}-build'] = [c['generate-full'][0], '--cc', '--exe', '--build', '-j', '2', '-Wno-fatal', '--top-module', module, '--Mdir', str(obj), str(WORK/(module+'.sv')), str(WORK/'responder_test.cpp'), '-CFLAGS', '-std=c++17 -O2'+(' -DTEST_SELF' if service=='self' else '')]
        c[f'unit-{service}-run'] = [str(obj/('V'+module)), str(FIX)]
    c['compare'] = [str(ROOT/'.venv/bin/python'), '-B', str(WORK/'compare_outputs.py')]
    (WORK/'commands-a.json').write_text(json.dumps(c,indent=2)+'\n')
    (WORK/'source-provenance.json').write_text(json.dumps({str(p):digest(p) for p in [SRC/(OLD+'.sv'), SRC/'four_stage.cpp', *SRC.glob('*.hpp')]},indent=2)+'\n')
    print('W1-STATUS: group a source and ROM generation complete; native ROM bytes=11427840; all eight hex round trips pass')

if __name__ == '__main__':
    main()
